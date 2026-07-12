from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain


VERSION = "2.6.2"
EPOCH_SUBSYSTEM_VERSION = "2.6.1a"
SCHEMA = "NEXUS_SOURCE_EPOCH.v2.6.2"
OBSERVATION_SCHEMA = "NEXUS_EPOCH_OBSERVATION.v2.6.2"
RUNTIME_CONTRACT_VERSION = "epoch-integrity-hardening.v2.6.1a"
SCHEMA_COMPATIBILITY_HASH = "source-epoch-observation-v1"
REPORT_LATEST = Path("reports") / "nexus_epoch_integrity_seal_latest.json"
LATEST_POINTER = Path("state") / "latest_epoch_pointer.json"
LATEST_OBSERVATION_POINTER = Path("state") / "latest_observation_pointer.json"
EPOCH_ROOT = Path("state") / "epochs"
LEDGER = Path("ledger") / "epoch_chain.jsonl"
OBSERVATION_LEDGER = Path("ledger") / "epoch_observations.jsonl"

CANONICAL_SOURCE_PREFIXES = (
    "nexus_gate/",
    "scripts/",
    "tests/",
    "docs/",
    "policy/",
    "chatgpt/",
    "schemas/",
    "registry/",
    "rcc/",
    "electron/",
    ".github/",
)
CANONICAL_SOURCE_FILES = (
    "README.md",
    "AGENTS.md",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
)
GENERATED_PREFIXES = ("reports/", "state/", "ledger/", "dist/")
IGNORED_RUNTIME_PREFIXES = (
    ".git/",
    ".venv/",
    "venv/",
    "node_modules/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
)
IGNORED_FILE_SUFFIXES = (
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
    ".tar.gz",
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".exe",
    ".dll",
)

REQUIRED_SURFACES = [
    "README.md",
    "AGENTS.md",
    "docs/updates/UPDATE_CHART.md",
    "docs/versioning/NEXUS_CHANGELOG.md",
    "docs/algorithms/NEXUS_CORE_ALGORITHMS.md",
    "nexus_gate/origin/seal.py",
    "nexus_gate/distillation/graph.py",
]

GATE_REPORTS = {
    "origin-seal": "reports/nexus_origin_seal_latest.json",
    "triadic-lattice": "reports/nexus_triadic_lattice_latest.json",
    "decision-envelope": "reports/nexus_decision_envelope_latest.json",
    "coherence-field": "reports/nexus_coherence_field_latest.json",
    "outcome-learn": "reports/nexus_recommendation_outcome_latest.json",
    "distill": "reports/nexus_evidence_distillation_report_latest.json",
    "runtime-hygiene": "reports/nexus_runtime_hygiene_latest.json",
    "compile": "reports/nexus_compile_report_latest.json",
}

CLAIM_BOUNDARY = (
    "Source Epoch and Observation packets provide local temporal identity evidence only. "
    "They separate content-addressed repository identity from repeatable observation runs. "
    "They do not prove correctness, safety, security, production readiness, model "
    "understanding, consciousness, or autonomous authority."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "treat_commit_sha_as_primary_epoch",
    "overwrite_epoch_history",
    "learn_from_working_tree_only_epoch",
    "prune_without_distillation_coverage",
    "bypass_final_evolve",
    "external_api_writes",
    "secret_access",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_obj(obj: Any) -> str:
    return _sha_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8"))


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def _atomic_write_json(path: Path, packet: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        Path(tmp_name).replace(path)
    finally:
        tmp = Path(tmp_name)
        if tmp.exists():
            tmp.unlink()


def _git(root: Path, args: list[str], timeout: int = 10) -> str:
    try:
        proc = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, timeout=timeout, check=False)
    except Exception:
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _normalize(rel: str) -> str:
    rel = rel.replace("\\", "/").strip()
    if len(rel) >= 2 and rel[0] == '"' and rel[-1] == '"':
        rel = rel[1:-1]
    return rel


def _is_source_surface(rel: str) -> bool:
    normalized = _normalize(rel)
    if normalized in CANONICAL_SOURCE_FILES or fnmatch.fnmatch(normalized, "requirements*.txt"):
        return True
    if any(normalized.startswith(prefix) for prefix in CANONICAL_SOURCE_PREFIXES):
        return not _is_generated_or_ignored(normalized)
    return False


def _is_generated_or_ignored(rel: str) -> bool:
    normalized = _normalize(rel)
    if normalized == "state/neural_activity/repo_neural_graph_latest.json":
        return True
    if normalized.startswith(GENERATED_PREFIXES):
        return True
    if any(part in normalized for part in ("/__pycache__/", "/node_modules/", "/.pytest_cache/")):
        return True
    if normalized.startswith(IGNORED_RUNTIME_PREFIXES):
        return True
    return normalized.endswith(IGNORED_FILE_SUFFIXES)


def _tracked_files(root: Path) -> list[str]:
    output = _git(root, ["ls-files"])
    files = [_normalize(line) for line in output.splitlines() if line.strip()]
    return sorted(rel for rel in files if _is_source_surface(rel))


def _untracked_files(root: Path) -> list[str]:
    output = _git(root, ["ls-files", "--others", "--exclude-standard"])
    files = [_normalize(line) for line in output.splitlines() if line.strip()]
    return sorted(rel for rel in files if _is_source_surface(rel))


def _git_state_map(root: Path) -> dict[str, str]:
    states: dict[str, str] = {rel: "tracked" for rel in _tracked_files(root)}
    for rel in _untracked_files(root):
        states[rel] = "untracked"
    for line in _git(root, ["status", "--short", "--untracked-files=all"]).splitlines():
        if not line.strip():
            continue
        rel = _normalize(line[3:])
        if " -> " in rel:
            rel = _normalize(rel.split(" -> ", 1)[1])
        if _is_source_surface(rel) and rel in states:
            states[rel] = "untracked" if line.startswith("??") else "modified"
    return states


def _merkle_root(leaves: list[str]) -> str:
    if not leaves:
        return _sha_bytes(b"")
    layer = sorted(leaves)
    while len(layer) > 1:
        next_layer: list[str] = []
        for index in range(0, len(layer), 2):
            left = layer[index]
            right = layer[index + 1] if index + 1 < len(layer) else left
            next_layer.append(_sha_bytes((left + right).encode("utf-8")))
        layer = next_layer
    return layer[0]


def _source_records(root: Path, include_untracked: bool) -> tuple[list[dict[str, Any]], str]:
    states = _git_state_map(root)
    records: list[dict[str, Any]] = []
    leaves: list[str] = []
    for rel in sorted(states):
        if states[rel] == "untracked" and not include_untracked:
            continue
        path = root / rel
        try:
            data = path.read_bytes()
        except Exception:
            continue
        digest = _sha_bytes(data)
        leaf = _sha_bytes((rel + "\0" + digest).encode("utf-8"))
        records.append({
            "path": rel,
            "git_state": states[rel],
            "included": True,
            "exclusion_reason": None,
            "bytes": len(data),
            "sha256": digest,
            "leaf_hash": leaf,
        })
        leaves.append(leaf)
    return records, _merkle_root(leaves)


def _surface_record(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    if not path.exists():
        return {"path": rel, "exists": False, "sha256": None, "bytes": 0}
    data = path.read_bytes()
    return {"path": rel, "exists": True, "sha256": _sha_bytes(data), "bytes": len(data)}


def _gate_index(root: Path) -> dict[str, Any]:
    gates: dict[str, Any] = {}
    for gate, rel in GATE_REPORTS.items():
        path = root / rel
        packet = _read_json(path, {})
        gates[gate] = {
            "path": rel,
            "exists": path.exists(),
            "status": packet.get("status") if isinstance(packet, dict) else None,
            "schema": packet.get("schema") if isinstance(packet, dict) else None,
            "version": (packet.get("version") or packet.get("product_version")) if isinstance(packet, dict) else None,
            "sha256": _sha_bytes(path.read_bytes()) if path.exists() else None,
        }
    return gates


def _epoch_state(required: list[dict[str, Any]], dirty_source_count: int) -> tuple[str, str, bool]:
    if not all(item["exists"] for item in required):
        return "dehydrated", "dehydrated", False
    if dirty_source_count:
        return "sealed_working_tree", "working_tree_only", False
    return "sealed_clean", "admissible", True


def _directory_integrity(root: Path, epoch_dir: Path, manifest: dict[str, Any], source_index: dict[str, Any], compatibility: dict[str, Any], origin: dict[str, Any]) -> dict[str, Any]:
    if not epoch_dir.exists():
        return {
            "directory_status": "created",
            "manifest_hash_valid": True,
            "source_index_hash_valid": True,
            "origin_packet_hash_valid": True,
            "compatibility_packet_hash_valid": True,
        }
    immutable_names = ["epoch_manifest.json", "source_index.json", "origin_packet.json", "compatibility_packet.json"]
    if not any((epoch_dir / name).exists() for name in immutable_names):
        return {
            "directory_status": "created",
            "manifest_hash_valid": True,
            "source_index_hash_valid": True,
            "origin_packet_hash_valid": True,
            "compatibility_packet_hash_valid": True,
        }
    existing_manifest = _read_json(epoch_dir / "epoch_manifest.json", {})
    existing_manifest_hash_valid = bool(existing_manifest) and existing_manifest.get("manifest_hash") == _sha_obj({
        key: value for key, value in existing_manifest.items()
        if key not in {"manifest_hash", "chain_event_hash", "observation_event_hash", "epoch_chain", "observation_chain", "epoch_directory_integrity"}
    })
    manifest_identity_valid = all(
        existing_manifest.get(key) == manifest.get(key)
        for key in (
            "schema",
            "source_epoch_id",
            "source_root",
            "tracked_source_root",
            "working_tree_source_root",
            "runtime_contract_version",
            "schema_compatibility_hash",
        )
    )
    validity: dict[str, bool] = {
        "epoch_manifest.json": bool(existing_manifest) and existing_manifest_hash_valid and manifest_identity_valid,
        "source_index.json": (epoch_dir / "source_index.json").exists() and _sha_obj(_read_json(epoch_dir / "source_index.json", {})) == _sha_obj(source_index),
        "origin_packet.json": (epoch_dir / "origin_packet.json").exists() and _sha_obj(_read_json(epoch_dir / "origin_packet.json", {})) == _sha_obj(origin),
        "compatibility_packet.json": (epoch_dir / "compatibility_packet.json").exists() and _sha_obj(_read_json(epoch_dir / "compatibility_packet.json", {})) == _sha_obj(compatibility),
    }
    valid = all(validity.values())
    return {
        "directory_status": "verified_existing" if valid else "invalid_collision",
        "manifest_hash_valid": validity["epoch_manifest.json"],
        "source_index_hash_valid": validity["source_index.json"],
        "origin_packet_hash_valid": validity["origin_packet.json"],
        "compatibility_packet_hash_valid": validity["compatibility_packet.json"],
    }


def build_epoch_integrity_seal(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    generated_at = _utc()
    tracked_records, tracked_source_root = _source_records(root_path, include_untracked=False)
    working_records, working_tree_source_root = _source_records(root_path, include_untracked=True)
    source_epoch_id = _sha_obj({
        "working_tree_source_root": working_tree_source_root,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "schema_compatibility_hash": SCHEMA_COMPATIBILITY_HASH,
    })
    observation_id = _sha_obj({
        "source_epoch_id": source_epoch_id,
        "generated_at_utc": generated_at,
        "gate_index": _gate_index(root_path),
    })
    required = [_surface_record(root_path, rel) for rel in REQUIRED_SURFACES]
    dirty_entries = [
        line for line in _git(root_path, ["status", "--short", "--untracked-files=all"]).splitlines()
        if line.strip() and _is_source_surface(_normalize(line[3:]))
    ]
    gates = _gate_index(root_path)
    state, durable_admissibility, eligible = _epoch_state(required, len(dirty_entries))
    commit = _git(root_path, ["rev-parse", "HEAD"]) or "unknown"
    branch = _git(root_path, ["branch", "--show-current"]) or "unknown"
    source_index = {
        "schema": "NEXUS_SOURCE_INDEX.v2.6.2",
        "source_epoch_id": source_epoch_id,
        "tracked_source_root": tracked_source_root,
        "working_tree_source_root": working_tree_source_root,
        "tracked_source_surface_count": len(tracked_records),
        "working_tree_source_surface_count": len(working_records),
        "canonical_source_prefixes": list(CANONICAL_SOURCE_PREFIXES),
        "canonical_source_files": list(CANONICAL_SOURCE_FILES),
        "generated_prefixes": list(GENERATED_PREFIXES),
        "ignored_runtime_prefixes": list(IGNORED_RUNTIME_PREFIXES),
        "ignored_file_suffixes": list(IGNORED_FILE_SUFFIXES),
        "records": working_records,
    }
    compatibility = {
        "schema": "NEXUS_EPOCH_COMPATIBILITY_PACKET.v2.6.2",
        "source_epoch_id": source_epoch_id,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "schema_compatibility_hash": SCHEMA_COMPATIBILITY_HASH,
        "minimum_product_version": "2.6.1",
        "maximum_product_version": None,
    }
    origin = {
        "schema": "NEXUS_EPOCH_ORIGIN_PACKET.v2.6.2",
        "source_epoch_id": source_epoch_id,
        "source_root": working_tree_source_root,
        "tracked_source_root": tracked_source_root,
        "working_tree_source_root": working_tree_source_root,
        "epoch_state": state,
        "durable_admissibility": durable_admissibility,
        "eligible_as_learning_parent": eligible,
        "product_version": VERSION,
        "epoch_subsystem_version": EPOCH_SUBSYSTEM_VERSION,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    manifest = {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "product_version": VERSION,
        "product_phase": "Causal Action Receipt Loop",
        "epoch_subsystem_version": EPOCH_SUBSYSTEM_VERSION,
        "status": "pass" if state in {"sealed_clean", "sealed_working_tree"} else "warn",
        "epoch_state": state,
        "durable_admissibility": durable_admissibility,
        "eligible_as_learning_parent": eligible,
        "source_epoch_id": source_epoch_id,
        "epoch_id": source_epoch_id,
        "source_root": working_tree_source_root,
        "tracked_source_root": tracked_source_root,
        "working_tree_source_root": working_tree_source_root,
        "primary_root_kind": "working_tree_source_root",
        "source_surface_count": len(working_records),
        "source_surface_index_hash": _sha_obj(working_records),
        "source_surface_sample": working_records[:80],
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "schema_compatibility_hash": SCHEMA_COMPATIBILITY_HASH,
        "generated_at_utc": generated_at,
        "repository_attestation": {
            "commit_sha": commit,
            "branch": branch,
            "role": "advisory_post_source_identity_binding",
            "note": "Commit SHA is not the primary epoch identity because source epoch identity is available before commit.",
        },
        "dirty_source_count": len(dirty_entries),
        "dirty_source_entries_sample": dirty_entries[:40],
        "required_surfaces": required,
        "gate_index": gates,
        "checks": {
            "required_surfaces_present": all(item["exists"] for item in required),
            "source_root_present": bool(working_tree_source_root),
            "source_epoch_excludes_parent_epoch": True,
            "untracked_source_included": any(item["git_state"] == "untracked" for item in working_records),
            "neural_runtime_graph_excluded": True,
            "latest_pointer_is_convenience_only": True,
            "commit_sha_not_primary_epoch": True,
            "human_authority_boundary_declared": True,
        },
        "blocked_actions": BLOCKED_ACTIONS,
        "authority_boundary": {
            "recommendation_only": True,
            "autonomous_authority": False,
            "human_authorization_required_for_mutation": True,
            "final_evolve_required_before_commit": True,
        },
        "claim_boundary": CLAIM_BOUNDARY,
        "read_surfaces": REQUIRED_SURFACES,
        "write_surfaces": [
            REPORT_LATEST.as_posix(),
            LATEST_POINTER.as_posix(),
            LATEST_OBSERVATION_POINTER.as_posix(),
            (EPOCH_ROOT / source_epoch_id / "epoch_manifest.json").as_posix(),
            (EPOCH_ROOT / source_epoch_id / "origin_packet.json").as_posix(),
            (EPOCH_ROOT / source_epoch_id / "source_index.json").as_posix(),
            (EPOCH_ROOT / source_epoch_id / "compatibility_packet.json").as_posix(),
            (EPOCH_ROOT / source_epoch_id / "observations" / f"{observation_id}.json").as_posix(),
            LEDGER.as_posix(),
            OBSERVATION_LEDGER.as_posix(),
        ],
    }
    manifest["manifest_hash"] = _sha_obj({key: value for key, value in manifest.items() if key != "manifest_hash"})
    return {
        "manifest": manifest,
        "source_index": source_index,
        "compatibility_packet": compatibility,
        "origin_packet": origin,
        "observation": {
            "schema": OBSERVATION_SCHEMA,
            "system": "NEXUS GATE",
            "product_version": VERSION,
            "source_epoch_id": source_epoch_id,
            "observation_id": observation_id,
            "generated_at_utc": generated_at,
            "gate_index_hash": _sha_obj(gates),
            "gate_index": gates,
            "dirty_source_count": len(dirty_entries),
            "epoch_state": state,
            "durable_admissibility": durable_admissibility,
            "producer_version": VERSION,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    }


def write_epoch_integrity_seal(root: str | Path, packet: dict[str, Any]) -> dict[str, Any]:
    root_path = Path(root).resolve()
    manifest = packet["manifest"]
    epoch_id = manifest["source_epoch_id"]
    observation = packet["observation"]
    epoch_dir = root_path / EPOCH_ROOT / epoch_id
    epoch_dir.mkdir(parents=True, exist_ok=True)
    observation_dir = epoch_dir / "observations"
    observation_dir.mkdir(parents=True, exist_ok=True)
    integrity = _directory_integrity(root_path, epoch_dir, manifest, packet["source_index"], packet["compatibility_packet"], packet["origin_packet"])
    manifest["epoch_directory_integrity"] = integrity
    if integrity["directory_status"] == "invalid_collision":
        manifest["status"] = "fail"
        manifest["epoch_state"] = "invalid_epoch_collision"
        manifest["durable_admissibility"] = "invalid"
        manifest["eligible_as_learning_parent"] = False
    else:
        for name, payload in {
            "epoch_manifest.json": manifest,
            "origin_packet.json": packet["origin_packet"],
            "source_index.json": packet["source_index"],
            "compatibility_packet.json": packet["compatibility_packet"],
        }.items():
            path = epoch_dir / name
            if not path.exists():
                _atomic_write_json(path, payload)
    observation_path = observation_dir / f"{observation['observation_id']}.json"
    if not observation_path.exists():
        _atomic_write_json(observation_path, observation)
    pointer = {
        "schema": "NEXUS_LATEST_EPOCH_POINTER.v2.6.2",
        "source_epoch_id": epoch_id,
        "epoch_id": epoch_id,
        "source_root": manifest["source_root"],
        "tracked_source_root": manifest["tracked_source_root"],
        "working_tree_source_root": manifest["working_tree_source_root"],
        "epoch_state": manifest["epoch_state"],
        "durable_admissibility": manifest["durable_admissibility"],
        "eligible_as_learning_parent": manifest["eligible_as_learning_parent"],
        "epoch_manifest": (EPOCH_ROOT / epoch_id / "epoch_manifest.json").as_posix(),
        "updated_at_utc": _utc(),
        "pointer_boundary": "Latest pointer is convenience only; epoch directories and ledgers are durable memory.",
    }
    observation_pointer = {
        "schema": "NEXUS_LATEST_OBSERVATION_POINTER.v2.6.2",
        "source_epoch_id": epoch_id,
        "observation_id": observation["observation_id"],
        "observation_path": (EPOCH_ROOT / epoch_id / "observations" / f"{observation['observation_id']}.json").as_posix(),
        "updated_at_utc": _utc(),
    }
    _atomic_write_json(root_path / LATEST_POINTER, pointer)
    _atomic_write_json(root_path / LATEST_OBSERVATION_POINTER, observation_pointer)
    _atomic_write_json(root_path / REPORT_LATEST, manifest)
    epoch_event = append_hash_chained_event(root_path / LEDGER, {
        "schema": "NEXUS_EPOCH_CHAIN_EVENT.v2.6.2",
        "event_type": "source_epoch",
        "epoch_id": epoch_id,
        "source_epoch_id": epoch_id,
        "source_root": manifest["source_root"],
        "epoch_state": manifest["epoch_state"],
        "durable_admissibility": manifest["durable_admissibility"],
        "generated_at_utc": manifest["generated_at_utc"],
        "producer_version": VERSION,
        "source_surface_count": manifest["source_surface_count"],
        "gate_count": len(manifest["gate_index"]),
        "manifest_hash": manifest["manifest_hash"],
    }, producer="epoch-seal")
    observation_event = append_hash_chained_event(root_path / OBSERVATION_LEDGER, {
        "schema": "NEXUS_EPOCH_OBSERVATION_EVENT.v2.6.2",
        "event_type": "epoch_observation",
        "epoch_id": epoch_id,
        "source_epoch_id": epoch_id,
        "observation_id": observation["observation_id"],
        "generated_at_utc": observation["generated_at_utc"],
        "producer_version": VERSION,
        "observation_hash": _sha_obj(observation),
    }, producer="epoch-observe")
    manifest["chain_event_hash"] = epoch_event["event_hash"]
    manifest["observation_event_hash"] = observation_event["event_hash"]
    manifest["epoch_chain"] = verify_hash_chain(root_path / LEDGER)
    manifest["observation_chain"] = verify_hash_chain(root_path / OBSERVATION_LEDGER)
    _atomic_write_json(root_path / REPORT_LATEST, manifest)
    return manifest


def verify_epoch_integrity(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    pointer = _read_json(root_path / LATEST_POINTER, {})
    observation_pointer = _read_json(root_path / LATEST_OBSERVATION_POINTER, {})
    epoch_id = pointer.get("source_epoch_id") or pointer.get("epoch_id")
    manifest_path = root_path / (pointer.get("epoch_manifest") or "")
    manifest = _read_json(manifest_path, {}) if epoch_id else {}
    current = build_epoch_integrity_seal(root_path)["manifest"]
    manifest_hash_valid = bool(manifest) and manifest.get("manifest_hash") == _sha_obj({key: value for key, value in manifest.items() if key not in {"manifest_hash", "chain_event_hash", "observation_event_hash", "epoch_chain", "observation_chain", "epoch_directory_integrity"}})
    source_root_match = bool(pointer) and pointer.get("source_root") == current["source_root"]
    epoch_chain = verify_hash_chain(root_path / LEDGER)
    observation_chain = verify_hash_chain(root_path / OBSERVATION_LEDGER)
    observation_path = root_path / (observation_pointer.get("observation_path") or "")
    observation_valid = bool(observation_pointer) and observation_path.exists() and observation_pointer.get("source_epoch_id") == epoch_id
    valid = bool(epoch_id) and source_root_match and epoch_chain["chain_valid"] and observation_chain["chain_valid"] and observation_valid
    packet = {
        "schema": "NEXUS_EPOCH_VERIFY_REPORT.v2.6.2",
        "system": "NEXUS GATE",
        "version": VERSION,
        "status": "pass" if valid else "fail",
        "generated_at_utc": _utc(),
        "source_epoch_id": epoch_id,
        "source_root_match": source_root_match,
        "manifest_hash_valid": manifest_hash_valid,
        "epoch_chain": epoch_chain,
        "observation_chain": observation_chain,
        "observation_valid": observation_valid,
        "durable_admissibility": pointer.get("durable_admissibility"),
        "eligible_as_learning_parent": pointer.get("eligible_as_learning_parent"),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _atomic_write_json(root_path / "reports" / "nexus_epoch_verify_latest.json", packet)
    return packet


def render(packet: dict[str, Any]) -> str:
    return "\n".join([
        "NEXUS SOURCE EPOCH / OBSERVATION SEAL",
        f"Version: v{packet.get('product_version')} / epoch {packet.get('epoch_subsystem_version')}",
        f"Status: {packet.get('status')} / {packet.get('epoch_state')}",
        f"Source epoch: {packet.get('source_epoch_id')}",
        f"Source root: {packet.get('source_root')}",
        f"Source surfaces: {packet.get('source_surface_count')}",
        f"Dirty source entries: {packet.get('dirty_source_count')}",
        f"Learning admissibility: {packet.get('durable_admissibility')}",
        "Boundary: source epoch identity only; receipts and human authority govern learning.",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile or verify the NEXUS Source Epoch Seal.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--chain-verify", action="store_true")
    args = parser.parse_args(argv)
    if args.chain_verify:
        root_path = Path(args.root).resolve()
        packet = {
            "schema": "NEXUS_EPOCH_CHAIN_VERIFY.v2.6.2",
            "status": "pass",
            "generated_at_utc": _utc(),
            "epoch_chain": verify_hash_chain(root_path / LEDGER),
            "observation_chain": verify_hash_chain(root_path / OBSERVATION_LEDGER),
        }
        packet["status"] = "pass" if packet["epoch_chain"]["chain_valid"] and packet["observation_chain"]["chain_valid"] else "fail"
    elif args.verify:
        packet = verify_epoch_integrity(args.root)
    else:
        packet = write_epoch_integrity_seal(args.root, build_epoch_integrity_seal(args.root))
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet) if "source_epoch_id" in packet else json.dumps(packet, indent=2, sort_keys=True))
    return 0 if packet.get("status") in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
