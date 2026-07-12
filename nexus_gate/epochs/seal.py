from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "2.6.1"
SCHEMA = "NEXUS_EPOCH_INTEGRITY_SEAL.v2.6.1"
RUNTIME_CONTRACT_VERSION = "epoch-integrity-seal.v2.6.1"
REPORT_LATEST = Path("reports") / "nexus_epoch_integrity_seal_latest.json"
LATEST_POINTER = Path("state") / "latest_epoch_pointer.json"
EPOCH_ROOT = Path("state") / "epochs"
LEDGER = Path("ledger") / "epoch_chain.jsonl"

SOURCE_PREFIXES = (
    "README.md",
    "AGENTS.md",
    "pyproject.toml",
    "nexus_gate/",
    "scripts/",
    "tests/",
    "docs/",
    "policy/",
    "chatgpt/",
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
    "Epoch Integrity Seal is local development identity evidence only. It creates a "
    "source-root epoch and append-only chain for later graph, memory, and routing "
    "comparisons. It does not prove correctness, safety, security, production "
    "readiness, model understanding, or autonomous authority."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "treat_commit_sha_as_primary_epoch",
    "overwrite_epoch_history",
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
        proc = subprocess.run(
            ["git", *args],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except Exception:
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _tracked_files(root: Path) -> list[str]:
    output = _git(root, ["ls-files"])
    files = [line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()]
    return sorted(rel for rel in files if _is_source_surface(rel))


def _is_source_surface(rel: str) -> bool:
    normalized = rel.replace("\\", "/")
    return any(normalized == prefix or normalized.startswith(prefix) for prefix in SOURCE_PREFIXES)


def _dirty_source_entries(root: Path) -> list[str]:
    entries = []
    for line in _git(root, ["status", "--short"]).splitlines():
        if not line.strip():
            continue
        rel = line[3:].strip().replace("\\", "/")
        if rel.startswith('"') and rel.endswith('"'):
            rel = rel.strip('"')
        if _is_source_surface(rel):
            entries.append(line)
    return entries


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


def _source_records(root: Path) -> tuple[list[dict[str, Any]], str]:
    records: list[dict[str, Any]] = []
    leaves: list[str] = []
    for rel in _tracked_files(root):
        path = root / rel
        try:
            data = path.read_bytes()
        except Exception:
            continue
        digest = _sha_bytes(data)
        leaf = _sha_bytes((rel + "\0" + digest).encode("utf-8"))
        records.append({"path": rel, "bytes": len(data), "sha256": digest, "leaf_hash": leaf})
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


def _last_chain_hash(root: Path) -> str:
    path = root / LEDGER
    if not path.exists():
        return "genesis"
    for line in reversed(path.read_text(encoding="utf-8-sig").splitlines()):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except Exception:
            continue
        return item.get("event_hash") or item.get("chain_hash") or "genesis"
    return "genesis"


def _append_chain_event(root: Path, event: dict[str, Any]) -> dict[str, Any]:
    ledger = root / LEDGER
    ledger.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = _last_chain_hash(root)
    body = dict(event)
    body["previous_event_hash"] = previous_hash
    body["event_id"] = _sha_obj({"epoch_id": body.get("epoch_id"), "previous_event_hash": previous_hash, "generated_at_utc": body.get("generated_at_utc")})
    body["event_hash"] = _sha_obj(body)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(body, sort_keys=True) + "\n")
        handle.flush()
    return body


def _epoch_state(required: list[dict[str, Any]], dirty_source_count: int) -> str:
    if not all(item["exists"] for item in required):
        return "dehydrated"
    if dirty_source_count:
        return "sealed_working_tree"
    return "sealed_clean"


def build_epoch_integrity_seal(root: str | Path) -> dict[str, Any]:
    root_path = Path(root).resolve()
    generated_at = _utc()
    source_records, source_root = _source_records(root_path)
    previous_pointer = _read_json(root_path / LATEST_POINTER, {})
    parent_epoch_id = previous_pointer.get("epoch_id") or "genesis"
    epoch_id = _sha_obj({
        "source_root": source_root,
        "parent_epoch_id": parent_epoch_id,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
    })
    required = [_surface_record(root_path, rel) for rel in REQUIRED_SURFACES]
    dirty_entries = _dirty_source_entries(root_path)
    gates = _gate_index(root_path)
    state = _epoch_state(required, len(dirty_entries))
    commit = _git(root_path, ["rev-parse", "HEAD"]) or "unknown"
    branch = _git(root_path, ["branch", "--show-current"]) or "unknown"

    manifest = {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "product_version": VERSION,
        "product_phase": "Epoch Integrity Seal",
        "status": "pass" if state in {"sealed_clean", "sealed_working_tree"} else "warn",
        "epoch_state": state,
        "epoch_id": epoch_id,
        "parent_epoch_id": parent_epoch_id,
        "source_root": source_root,
        "source_surface_count": len(source_records),
        "source_surface_index_hash": _sha_obj(source_records),
        "source_surface_sample": source_records[:80],
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "generated_at_utc": generated_at,
        "repository_attestation": {
            "commit_sha": commit,
            "branch": branch,
            "role": "advisory_post_source_identity_binding",
            "note": "Commit SHA is not the primary epoch identity because generated evidence can be committed after source-root capture.",
        },
        "dirty_source_count": len(dirty_entries),
        "dirty_source_entries_sample": dirty_entries[:40],
        "required_surfaces": required,
        "gate_index": gates,
        "checks": {
            "required_surfaces_present": all(item["exists"] for item in required),
            "source_root_present": bool(source_root),
            "latest_pointer_is_convenience_only": True,
            "append_only_chain_declared": True,
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
            (EPOCH_ROOT / epoch_id / "epoch_manifest.json").as_posix(),
            (EPOCH_ROOT / epoch_id / "origin_packet.json").as_posix(),
            (EPOCH_ROOT / epoch_id / "gate_index.json").as_posix(),
            LEDGER.as_posix(),
        ],
    }
    manifest["manifest_hash"] = _sha_obj({key: value for key, value in manifest.items() if key != "manifest_hash"})
    return manifest


def write_epoch_integrity_seal(root: str | Path, packet: dict[str, Any]) -> dict[str, Any]:
    root_path = Path(root).resolve()
    epoch_id = packet["epoch_id"]
    epoch_dir = root_path / EPOCH_ROOT / epoch_id
    epoch_dir.mkdir(parents=True, exist_ok=True)

    immutable_files = {
        epoch_dir / "epoch_manifest.json": packet,
        epoch_dir / "origin_packet.json": {
            "schema": "NEXUS_EPOCH_ORIGIN_PACKET.v2.6.1",
            "epoch_id": epoch_id,
            "source_root": packet["source_root"],
            "epoch_state": packet["epoch_state"],
            "product_version": VERSION,
            "origin_manifest_hash": packet["manifest_hash"],
            "claim_boundary": CLAIM_BOUNDARY,
        },
        epoch_dir / "gate_index.json": {
            "schema": "NEXUS_EPOCH_GATE_INDEX.v2.6.1",
            "epoch_id": epoch_id,
            "source_root": packet["source_root"],
            "gates": packet["gate_index"],
            "claim_boundary": "Gate index records report presence and hashes only; it is not proof of final correctness.",
        },
    }
    for path, payload in immutable_files.items():
        if not path.exists():
            _atomic_write_json(path, payload)

    pointer = {
        "schema": "NEXUS_LATEST_EPOCH_POINTER.v2.6.1",
        "epoch_id": epoch_id,
        "source_root": packet["source_root"],
        "epoch_state": packet["epoch_state"],
        "epoch_manifest": (EPOCH_ROOT / epoch_id / "epoch_manifest.json").as_posix(),
        "updated_at_utc": _utc(),
        "pointer_boundary": "Latest pointer is convenience only; epoch directories and ledger are the durable memory.",
    }
    _atomic_write_json(root_path / LATEST_POINTER, pointer)
    _atomic_write_json(root_path / REPORT_LATEST, packet)

    event = _append_chain_event(root_path, {
        "schema": "NEXUS_EPOCH_CHAIN_EVENT.v2.6.1",
        "epoch_id": epoch_id,
        "source_root": packet["source_root"],
        "epoch_state": packet["epoch_state"],
        "generated_at_utc": packet["generated_at_utc"],
        "producer_version": VERSION,
        "source_surface_count": packet["source_surface_count"],
        "gate_count": len(packet["gate_index"]),
        "manifest_hash": packet["manifest_hash"],
    })
    packet["chain_event_hash"] = event["event_hash"]
    _atomic_write_json(root_path / REPORT_LATEST, packet)
    return packet


def render(packet: dict[str, Any]) -> str:
    return "\n".join([
        "NEXUS EPOCH INTEGRITY SEAL",
        f"Version: v{packet.get('product_version')} {packet.get('product_phase')}",
        f"Status: {packet.get('status')} / {packet.get('epoch_state')}",
        f"Epoch: {packet.get('epoch_id')}",
        f"Source root: {packet.get('source_root')}",
        f"Source surfaces: {packet.get('source_surface_count')}",
        f"Dirty source entries: {packet.get('dirty_source_count')}",
        "Boundary: source-root identity only; human authority and final evolve still control durable mutation.",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile the NEXUS Epoch Integrity Seal.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_epoch_integrity_seal(args.root, build_epoch_integrity_seal(args.root))
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
