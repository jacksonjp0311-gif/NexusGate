from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "2.0.0"
SCHEMA = "NEXUS_COHERENCE_CONTINUITY_FIELD.v2.0.0"
REPORT_LATEST = Path("reports") / "nexus_coherence_field_latest.json"
STATE_LATEST = Path("state") / "coherence" / "nexus_coherence_field_latest.json"

CLAIM_BOUNDARY = (
    "The NEXUS Coherence Field is local development evidence only. It scores "
    "orientation, memory, evidence freshness, runtime pressure, wounds, policy, "
    "and continuity surfaces to recommend routing. It does not prove correctness, "
    "safety, security, production readiness, scientific truth, model understanding, "
    "or autonomous authority; coherence may not grant authority."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "convert_coherence_to_authority",
    "execute_selected_action",
    "skip_final_evolve",
    "reuse_stale_certificate",
    "promote_memory_without_receipt",
    "git_write",
    "arbitrary_shell_commands",
    "external_api_writes",
    "secret_access",
]

REQUIRED_SURFACES = [
    "reports/nexus_decision_envelope_latest.json",
    "reports/nexus_origin_seal_latest.json",
    "state/nexus_origin_manifest_latest.json",
    "state/algorithms/nexus_algorithm_cards_latest.json",
    "state/discoveries/nexus_discovery_cards_latest.json",
    "policy/authority_laws.json",
    "policy/risk_profiles.json",
    "policy/capabilities.json",
    "policy/claim_boundaries.json",
    "docs/protocols/GOVERNED_AGENT_CONTINUITY_PROTOCOL.md",
    "docs/runtime/NEXUS_COHERENCE_FIELD_PROTOCOL.md",
    "state/protocols/nexus_continuity_protocol.v2.0.json",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_scope(root: Path) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        return {"status": "warn", "dirty_count": None, "entries": [], "error": str(exc)}
    entries = [line for line in proc.stdout.splitlines() if line.strip()]
    return {
        "status": "pass" if proc.returncode == 0 else "warn",
        "dirty_count": len(entries),
        "entries": entries[:80],
        "truncated": len(entries) > 80,
    }


def _surface_status(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    return {
        "path": rel,
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }


def _lineage_entropy(origin: dict[str, Any], missing: list[str], git_scope: dict[str, Any]) -> int:
    lineage = origin.get("legacy_version_lineage") or {}
    identities = {
        str(value)
        for key, value in lineage.items()
        if "version" in key or key in {"product_version", "lineage_manifest_system_version"}
    }
    dirty_penalty = 1 if (git_scope.get("dirty_count") or 0) else 0
    return len(identities) + len(missing) + dirty_penalty


def _coherence_score(
    origin: dict[str, Any],
    decision: dict[str, Any],
    missing: list[str],
    git_scope: dict[str, Any],
    algorithms: dict[str, Any],
    discoveries: dict[str, Any],
) -> int:
    score = 100
    if origin.get("status") not in {"pass", "warn"}:
        score -= 20
    if decision.get("status") not in {"pass", "warn"}:
        score -= 20
    score -= min(25, len(missing) * 4)
    score -= min(20, int((git_scope.get("dirty_count") or 0) / 10))
    if algorithms.get("card_count", 0) < 1:
        score -= 10
    if discoveries.get("card_count", 0) < 1:
        score -= 10
    return max(0, min(100, score))


def _runtime_pressure(decision: dict[str, Any]) -> dict[str, Any]:
    risk = decision.get("risk") or {}
    pressure = risk.get("runtime_pressure") or "unknown"
    return {
        "level": pressure,
        "slowest_gate": risk.get("slowest_gate"),
        "timeout_budget": "adaptive_recommendation_only",
    }


def build_coherence_field(root: str | Path, intent: str = "") -> dict[str, Any]:
    root_path = Path(root).resolve()
    decision = _read_json(root_path / "reports" / "nexus_decision_envelope_latest.json", {})
    origin = _read_json(root_path / "reports" / "nexus_origin_seal_latest.json", {})
    algorithms = _read_json(root_path / "state" / "algorithms" / "nexus_algorithm_cards_latest.json", {})
    discoveries = _read_json(root_path / "state" / "discoveries" / "nexus_discovery_cards_latest.json", {})
    protocol = _read_json(root_path / "state" / "protocols" / "nexus_continuity_protocol.v2.0.json", {})
    git_scope = _git_scope(root_path)
    surfaces = [_surface_status(root_path, rel) for rel in REQUIRED_SURFACES]
    missing = [item["path"] for item in surfaces if not item["exists"]]
    score = _coherence_score(origin, decision, missing, git_scope, algorithms, discoveries)
    entropy = _lineage_entropy(origin, missing, git_scope)
    status = "pass" if score >= 85 and not missing else "warn"
    if score < 60:
        status = "fail"

    selected = decision.get("selected_action") or {}
    return {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "version": VERSION,
        "phase": "Coherence Continuity Protocol",
        "mode": "coherence_field",
        "status": status,
        "generated_at_utc": _utc(),
        "intent": intent,
        "coherence": {
            "score": score,
            "threshold": 85,
            "lineage_entropy": entropy,
            "field_state": "coherent" if score >= 85 else "forming",
            "dirty_count": git_scope.get("dirty_count"),
            "missing_surfaces": missing,
        },
        "origin": {
            "status": origin.get("status", "unknown"),
            "product_version": origin.get("product_version"),
            "product_phase": origin.get("product_phase"),
            "origin_manifest_hash": origin.get("origin_manifest_hash"),
        },
        "decision_envelope": {
            "status": decision.get("status", "unknown"),
            "selected_action": selected,
            "recommendation_count": len(decision.get("recommendations") or []),
        },
        "runtime_pressure": _runtime_pressure(decision),
        "policy_kernel": {
            "status": "present" if not any(rel.startswith("policy/") for rel in missing) else "warn",
            "surfaces": [rel for rel in REQUIRED_SURFACES if rel.startswith("policy/")],
            "law": "governance is compiled into organs, not copied between organs",
        },
        "evidence_dependency_graph": {
            "status": "scaffolded",
            "tracked_inputs": [
                "command",
                "relevant_file_hashes",
                "toolchain_fingerprint",
                "producer_version",
                "output_hash",
                "duration",
                "status",
            ],
            "reuse_rule": "prior pass may be reused only when gate inputs, toolchain, and gate contract match",
        },
        "wound_intelligence": {
            "status": "scaffolded",
            "priority_formula": "severity * recurrence * affected_surface_centrality * blast_radius / max(closure_confidence, 0.1)",
        },
        "benchmark_manifest": {
            "status": "scaffolded",
            "families": [
                "interrupted_agent_recovery",
                "incremental_validation_efficiency",
                "authority_containment",
                "recommendation_agreement",
                "token_attention_cost",
            ],
        },
        "continuity_protocol": {
            "status": "present" if protocol else "missing",
            "schema": protocol.get("schema"),
            "loop": protocol.get("loop", []),
        },
        "selected_next_action": {
            "command": selected.get("command", ".\\scripts\\nexus.ps1 decision-envelope"),
            "why": selected.get("why", "Compile decision envelope before choosing a route."),
            "recommendation_only": True,
            "requires_human_authorization": True,
            "requires_final_evolve_before_commit": True,
        },
        "blocked_actions": BLOCKED_ACTIONS,
        "read_surfaces": REQUIRED_SURFACES + ["git status --short"],
        "write_surfaces": [REPORT_LATEST.as_posix(), STATE_LATEST.as_posix()],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_coherence_field(root: str | Path, intent: str = "") -> dict[str, Any]:
    root_path = Path(root).resolve()
    packet = build_coherence_field(root_path, intent=intent)
    for rel in (REPORT_LATEST, STATE_LATEST):
        _write_json(root_path / rel, packet)
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile the NEXUS coherence continuity field.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="Compile NEXUS coherence continuity field.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_coherence_field(args.root, intent=args.intent)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"NEXUS coherence field: {packet['status']} score={packet['coherence']['score']}")
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
