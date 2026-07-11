from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.loops.predictive_evolve import build_predictive_evolve_plan


VERSION = "1.2.0"
SCHEMA = "NEXUS_PREDICTIVE_MEMORY_ORCHESTRATOR.v1.2.0"
REPORT_LATEST = Path("reports") / "nexus_predictive_memory_orchestrator_latest.json"
STATE_LATEST = Path("state") / "loops" / "nexus_predictive_memory_orchestrator_latest.json"
CORTEX_TREND_LEDGER = Path("ledger") / "cortex_benchmark_trends.jsonl"

CLAIM_BOUNDARY = (
    "Predictive Memory Orchestration is local development evidence only. It fuses "
    "Cortex memory health, vector benchmark evidence, discovery/algorithm cards, "
    "and predictive gate planning into a recommendation. It does not execute the "
    "plan, mutate the repository, prove retrieval correctness, prove safety or "
    "security, or grant autonomous authority."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "execute_plan",
    "bypass_final_evolve",
    "autonomous_memory_promotion",
    "arbitrary_shell_commands",
    "git_write",
    "external_api_writes",
    "secret_access",
    "hide_failures",
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


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def _git_scope(root: Path) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except Exception as exc:
        return {"status": "warn", "dirty_count": 0, "changed_files": [], "error": str(exc)}
    files = [line[3:].strip().replace("\\", "/") for line in proc.stdout.splitlines() if line.strip()]
    return {
        "status": "pass" if proc.returncode == 0 else "warn",
        "dirty_count": len(files),
        "changed_files": files[:80],
        "truncated": len(files) > 80,
    }


def _cortex_status(cortex_gate: dict[str, Any], benchmark: dict[str, Any], sync: dict[str, Any]) -> dict[str, Any]:
    checks = cortex_gate.get("checks") or {}
    doctor = cortex_gate.get("doctor") or {}
    governor = doctor.get("governor") or {}
    components = governor.get("components") or {}
    legacy = benchmark.get("legacy") or {}
    blob = benchmark.get("versioned_blob") or {}
    query_delta_ms = None
    if legacy.get("mean_query_ms") is not None and blob.get("mean_query_ms") is not None:
        query_delta_ms = round(float(legacy["mean_query_ms"]) - float(blob["mean_query_ms"]), 3)
    return {
        "gate_status": cortex_gate.get("status", "unknown"),
        "database_integrity": bool(checks.get("database_integrity")),
        "certificate_verified": bool(checks.get("certificate_verified")),
        "vector_storage_current": bool(checks.get("vector_storage_current")),
        "read_only_authority": bool(checks.get("read_only_authority")),
        "governor_mode": governor.get("mode", "unknown"),
        "retrieval_confidence": components.get("retrieval_confidence"),
        "source_commit": sync.get("source_commit"),
        "vector_payload_reduction_percent": benchmark.get("vector_payload_reduction_percent"),
        "query_delta_ms": query_delta_ms,
        "vectors_sampled": benchmark.get("vectors"),
    }


def _card_status(algorithms: dict[str, Any], discoveries: dict[str, Any]) -> dict[str, Any]:
    algorithm_ids = set(algorithms.get("discovered_algorithms") or [])
    discovery_ids = {card.get("discovery_id") for card in discoveries.get("cards") or []}
    required_algorithms = {
        "predictive-evolve-planner-algorithm",
        "cortex-sync-protocol-algorithm",
        "versioned-vector-blob-storage-algorithm",
    }
    required_discoveries = {
        "predictive-gate-timing-runtime-pressure",
        "predictive-evolve-dry-run-planner",
        "cortex-versioned-vector-memory",
    }
    return {
        "algorithm_count": algorithms.get("card_count", 0),
        "discovery_count": discoveries.get("card_count", 0),
        "required_algorithms_present": sorted(required_algorithms.intersection(algorithm_ids)),
        "missing_algorithms": sorted(required_algorithms.difference(algorithm_ids)),
        "required_discoveries_present": sorted(required_discoveries.intersection(discovery_ids)),
        "missing_discoveries": sorted(required_discoveries.difference(discovery_ids)),
    }


def _recommend(cortex: dict[str, Any], predictive: dict[str, Any], cards: dict[str, Any], git_scope: dict[str, Any]) -> dict[str, Any]:
    if cards.get("missing_algorithms") or cards.get("missing_discoveries"):
        return {
            "recommended_next_loop": "card-refresh",
            "recommended_next_command": ".\\scripts\\nexus.ps1 algorithm-cards; .\\scripts\\nexus.ps1 discovery-cards",
            "why": "Required memory/orchestration cards are missing; refresh cards before planning from them.",
        }
    if not cortex.get("database_integrity") or not cortex.get("read_only_authority"):
        return {
            "recommended_next_loop": "cortex-gate",
            "recommended_next_command": ".\\scripts\\nexus.ps1 cortex",
            "why": "Cortex gate evidence is missing or not bounded read-only; refresh Cortex before memory-aware planning.",
        }
    if not cortex.get("vector_storage_current"):
        return {
            "recommended_next_loop": "cortex-vector-migration",
            "recommended_next_command": "cd Cortex; python -m cortex --home ..\\state\\cortex_memory migrate-vectors --repo nexus-gate --json",
            "why": "Cortex vector storage is not current; migrate vectors before trusting memory health trend data.",
        }
    if cortex.get("gate_status") == "constrained":
        return {
            "recommended_next_loop": "cortex-certificate-refresh",
            "recommended_next_command": ".\\scripts\\nexus.ps1 cortex-refresh",
            "why": "Cortex is bounded read-only but constrained; refresh its certificate, graph, telemetry, vectors, and NEXUS packet before memory-aware planning.",
        }
    plan = predictive.get("recommended_plan") or []
    next_step = next((step for step in plan if not step.get("required_before_commit")), None)
    if next_step:
        return {
            "recommended_next_loop": next_step.get("step_id", "predictive-evolve"),
            "recommended_next_command": next_step.get("command", ".\\scripts\\nexus.ps1 predictive-evolve"),
            "why": "Predictive Evolve has the cheapest current validation step, with Cortex memory evidence available as context.",
        }
    if git_scope.get("dirty_count", 0):
        return {
            "recommended_next_loop": "scope-hygiene",
            "recommended_next_command": '.\\scripts\\nexus.ps1 preflight-json -Tag "predictive memory dirty scope"',
            "why": "Working tree has dirty entries; inspect scope before compounding memory-aware changes.",
        }
    return {
        "recommended_next_loop": "final-evolve-seal",
        "recommended_next_command": ".\\scripts\\nexus.ps1 evolve",
        "why": "Memory, cards, and predictive plan are aligned; final evolve remains the local seal before commit.",
    }


def build_predictive_memory_orchestrator(root: str | Path, intent: str = "", max_runs: int = 12) -> dict[str, Any]:
    root_path = Path(root).resolve()
    cortex_gate = _read_json(root_path / "reports" / "nexus_cortex_gate_latest.json", {})
    cortex_benchmark = _read_json(root_path / "reports" / "nexus_cortex_vector_benchmark_latest.json", {})
    cortex_sync = _read_json(root_path / "reports" / "nexus_cortex_sync_report_latest.json", {})
    algorithms = _read_json(root_path / "state" / "algorithms" / "nexus_algorithm_cards_latest.json", {})
    discoveries = _read_json(root_path / "state" / "discoveries" / "nexus_discovery_cards_latest.json", {})
    predictive = build_predictive_evolve_plan(root_path, max_runs=max_runs)
    git_scope = _git_scope(root_path)
    cortex = _cortex_status(cortex_gate, cortex_benchmark, cortex_sync)
    cards = _card_status(algorithms, discoveries)
    recommendation = _recommend(cortex, predictive, cards, git_scope)
    warnings = []
    if cortex.get("gate_status") == "constrained":
        warnings.append("cortex_constrained_read_only")
    if cards.get("missing_algorithms") or cards.get("missing_discoveries"):
        warnings.append("card_gap")
    if predictive.get("status") == "warn":
        warnings.append("runtime_pressure")
    status = "warn" if warnings else "pass"
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "system": "NEXUS GATE",
        "mode": "predictive_memory_orchestrator",
        "status": status,
        "generated_utc": _utc(),
        "intent": intent,
        "read_surfaces": [
            "reports/nexus_cortex_gate_latest.json",
            "reports/nexus_cortex_sync_report_latest.json",
            "reports/nexus_cortex_vector_benchmark_latest.json",
            "state/algorithms/nexus_algorithm_cards_latest.json",
            "state/discoveries/nexus_discovery_cards_latest.json",
            "reports/nexus_predictive_evolve_plan_latest.json",
            "git status --porcelain",
        ],
        "write_surfaces": [
            REPORT_LATEST.as_posix(),
            STATE_LATEST.as_posix(),
            CORTEX_TREND_LEDGER.as_posix(),
        ],
        "cortex_memory": cortex,
        "card_memory": cards,
        "predictive_evolve": {
            "status": predictive.get("status"),
            "git_scope": predictive.get("git_scope"),
            "gate_selection_policy": predictive.get("gate_selection_policy"),
            "recommended_plan": predictive.get("recommended_plan"),
            "final_evolve_required_before_commit": predictive.get("final_evolve_required_before_commit"),
        },
        "git_scope": git_scope,
        "warnings": warnings,
        "recommendation": recommendation,
        "blocked_actions": BLOCKED_ACTIONS,
        "authority_boundary": {
            "recommendation_only": True,
            "execute_plan": False,
            "repo_mutation": False,
            "git_write": False,
            "autonomous_memory_promotion": False,
            "arbitrary_shell_execution": False,
            "final_evolve_required_before_commit": True,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_outputs(root: str | Path, packet: dict[str, Any]) -> None:
    root_path = Path(root).resolve()
    _write_json(root_path / REPORT_LATEST, packet)
    _write_json(
        root_path / STATE_LATEST,
        {
            "schema": packet["schema"],
            "version": packet["version"],
            "status": packet["status"],
            "generated_utc": packet["generated_utc"],
            "cortex_memory": packet["cortex_memory"],
            "card_memory": packet["card_memory"],
            "recommendation": packet["recommendation"],
            "warnings": packet["warnings"],
            "blocked_actions": packet["blocked_actions"],
            "claim_boundary": packet["claim_boundary"],
        },
    )
    cortex = packet.get("cortex_memory") or {}
    if cortex.get("vectors_sampled") is not None or cortex.get("vector_payload_reduction_percent") is not None:
        _append_jsonl(
            root_path / CORTEX_TREND_LEDGER,
            {
                "timestamp": packet["generated_utc"],
                "status": packet["status"],
                "gate_status": cortex.get("gate_status"),
                "database_integrity": cortex.get("database_integrity"),
                "certificate_verified": cortex.get("certificate_verified"),
                "vector_storage_current": cortex.get("vector_storage_current"),
                "governor_mode": cortex.get("governor_mode"),
                "source_commit": cortex.get("source_commit"),
                "vectors_sampled": cortex.get("vectors_sampled"),
                "vector_payload_reduction_percent": cortex.get("vector_payload_reduction_percent"),
                "query_delta_ms": cortex.get("query_delta_ms"),
                "recommended_next_loop": packet.get("recommendation", {}).get("recommended_next_loop"),
            },
        )


def render(packet: dict[str, Any]) -> str:
    cortex = packet.get("cortex_memory") or {}
    rec = packet.get("recommendation") or {}
    return "\n".join(
        [
            "NEXUS PREDICTIVE MEMORY ORCHESTRATOR",
            f"Version: v{packet.get('version')}",
            f"Status: {packet.get('status')}",
            f"Cortex: {cortex.get('gate_status')} / vectors current={cortex.get('vector_storage_current')}",
            f"Vector gain: {cortex.get('vector_payload_reduction_percent')}% payload / {cortex.get('query_delta_ms')} ms query delta",
            f"Next: {rec.get('recommended_next_command')}",
            f"Why: {rec.get('why')}",
            "Boundary: recommendation-only; final evolve remains required before commit.",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS predictive memory orchestrator.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="Fuse Cortex memory and predictive gate evidence.")
    parser.add_argument("--max-runs", type=int, default=12)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = build_predictive_memory_orchestrator(args.root, intent=args.intent, max_runs=args.max_runs)
    write_outputs(args.root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render(packet))
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
