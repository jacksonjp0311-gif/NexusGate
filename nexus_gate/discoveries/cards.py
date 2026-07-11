from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SYSTEM = "NEXUS_DISCOVERY_CARDS"
VERSION = "0.2.0"
SCHEMA = "NEXUS_DISCOVERY_CARD_SET.v0.2.0"
LATEST_PATH = Path("state/discoveries/nexus_discovery_cards_latest.json")
VERSIONED_PATH = Path("state/discoveries/nexus_discovery_cards.v0.2.0.json")

CLAIM_BOUNDARY = (
    "Discovery cards preserve local engineering discoveries as reproducible cards. "
    "They do not prove correctness, safety, security, production readiness, scientific truth, "
    "mathematical proof, or autonomous authority."
)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_discovery_cards(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    cards = [
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.1.0",
            "discovery_id": "predictive-gate-timing-runtime-pressure",
            "version": "0.1.0",
            "title": "Predictive Gate Timing / Runtime Pressure Model",
            "status": "active",
            "summary": "Timeouts and slow gates are not just failures; they are runtime pressure signals that can guide cheaper next gates.",
            "math": {
                "baseline": "median_duration = median(durations)",
                "p90": "p90_duration = percentile(durations, 0.90)",
                "drift": "drift_ratio = latest_duration / median_duration",
                "adaptive_timeout": "timeout = max(min_timeout, min(max_timeout, p90 * 1.5))",
                "control_loop": "observe -> estimate -> compare -> classify -> recommend -> record",
            },
            "code_references": [
                "nexus_gate/loops/predictive_timing.py::build_predictive_timing_packet",
                "nexus_gate/loops/predictive_timing.py::_analyze_steps",
                "nexus_gate/loops/predictive_timing.py::_gate_selection_policy",
                "nexus_gate/loops/predictive_timing.py::write_outputs",
            ],
            "algorithm_card_refs": [
                "runtime-pressure-model",
                "adaptive-timeout-budgeting",
                "gate-selection-policy",
                "certificate-resume-policy",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 predictive-timing",
                "Inspect reports/nexus_predictive_gate_timing_latest.json",
                "Inspect ledger/runtime_gate_timings.jsonl",
                "Use the recommendation before repeating full evolve",
            ],
            "evidence_surfaces": [
                "reports/nexus_predictive_gate_timing_latest.json",
                "state/loops/nexus_predictive_gate_timing_latest.json",
                "ledger/runtime_gate_timings.jsonl",
                "state/algorithms/nexus_algorithm_cards_latest.json",
            ],
            "next_versions": [
                "v0.2: add confidence intervals and per-gate trend windows",
                "v0.3: add predictive-evolve dry-run planner",
                "v0.4: surface timing pressure in Electron/System Monitor HUD",
            ],
            "boundary": "Recommendation-only. It may guide gate choice; it may not skip required final evolve before commit.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "predictive-evolve-dry-run-planner",
            "version": "0.2.0",
            "title": "Predictive Evolve Dry-Run Planner",
            "status": "active",
            "summary": "Predictive timing becomes more useful when wrapped in a dry-run plan that orders the next cheapest gate while preserving the final evolve seal.",
            "math": {
                "scope_policy": "scope = classify(changed_files)",
                "pressure_policy": "pressure = max_level(runtime_pressure)",
                "plan_rule": "plan = [predictive-timing, targeted_gate(scope, pressure), final_evolve_seal]",
                "authority_rule": "commit_allowed = final_evolve_passed and human_authorized",
                "control_loop": "estimate -> classify -> plan -> require seal -> record",
            },
            "code_references": [
                "nexus_gate/loops/predictive_evolve.py::build_predictive_evolve_plan",
                "nexus_gate/loops/predictive_evolve.py::_plan_steps",
                "nexus_gate/loops/predictive_timing.py::build_predictive_timing_packet",
            ],
            "algorithm_card_refs": [
                "predictive-evolve-planner-algorithm",
                "gate-selection-policy",
                "runtime-pressure-model",
                "certificate-resume-policy",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 predictive-evolve",
                "Inspect reports/nexus_predictive_evolve_plan_latest.json",
                "Run any recommended targeted gate manually",
                "Run .\\scripts\\nexus.ps1 evolve before commit",
            ],
            "evidence_surfaces": [
                "reports/nexus_predictive_evolve_plan_latest.json",
                "state/loops/nexus_predictive_evolve_plan_latest.json",
                "reports/nexus_predictive_gate_timing_latest.json",
                "state/algorithms/nexus_algorithm_cards_latest.json",
            ],
            "next_versions": [
                "v0.3: add HUD runtime pressure visibility",
                "v0.4: add confidence windows and EWMA pressure smoothing",
                "v0.5: add certificate resume planning",
            ],
            "boundary": "Dry-run and recommendation-only. It may recommend targeted gates; it may not execute them or skip full evolve before commit.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "certificate-resume-gate-fingerprint",
            "version": "0.2.0",
            "title": "Certificate Resume Gate Fingerprint",
            "status": "active",
            "summary": "Passed gates can become local resume evidence when their logs and current git scope are hashed, but certificates never replace the final evolve seal.",
            "math": {
                "evidence_hash": "evidence_sha256 = sha256(gate_log_bytes)",
                "input_fingerprint": "input_fingerprint = sha256(gate_id + git_scope_hash + gate_log_bytes)",
                "resume_rule": "resume_gate = first(status in {fail, timeout})",
                "commit_rule": "commit_allowed = final_evolve_passed and human_authorized",
                "control_loop": "gate -> hash -> certify -> fail point -> recommend resume -> require seal",
            },
            "code_references": [
                "nexus_gate/loops/certificate_resume.py::build_certificate_resume_packet",
                "nexus_gate/loops/certificate_resume.py::_certificate_for",
                "nexus_gate/loops/certificate_resume.py::_latest_human_surface",
            ],
            "algorithm_card_refs": [
                "certificate-resume-policy",
                "predictive-evolve-planner-algorithm",
                "compiler-gate-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 certificate-resume",
                "Inspect reports/nexus_certificate_resume_report_latest.json",
                "Fix the active wound if a resume gate is present",
                "Run .\\scripts\\nexus.ps1 evolve before commit",
            ],
            "evidence_surfaces": [
                "reports/nexus_certificate_resume_report_latest.json",
                "state/loops/nexus_certificate_resume_latest.json",
                "reports/human_surface/*",
            ],
            "next_versions": [
                "v0.2: compare certificate fingerprints across changed inputs",
                "v0.3: recommend exact targeted rerun command per gate",
                "v0.4: show certificate status in System Monitor HUD",
            ],
            "boundary": "Recommendation-only. Certificates may recommend resume points; they may not claim correctness or skip final evolve before commit.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "cortex-versioned-vector-memory",
            "version": "0.1.0",
            "title": "Cortex Versioned Vector Memory",
            "status": "active",
            "summary": "Cortex memory can become cheaper and more governable when semantic vectors are stored as versioned float32 blobs instead of legacy JSON strings.",
            "math": {
                "payload_reduction": "reduction = 1 - blob_payload_bytes / legacy_payload_bytes",
                "observed_reduction": "1 - 1545000 / 2366490 = 0.3471",
                "query_delta": "delta_ms = legacy_mean_query_ms - blob_mean_query_ms",
                "observed_query_delta": "242.630 ms - 183.011 ms = 59.619 ms",
                "format_rule": "current = vector_bytes startswith CTXV1",
            },
            "code_references": [
                "Cortex/cortex/embeddings.py::vector_to_bytes",
                "Cortex/cortex/embeddings.py::deserialize_vector",
                "Cortex/cortex/store.py::migrate_vectors",
                "Cortex/cortex/store.py::vector_format_status",
                "nexus_gate/cortex/compile.py::compile_gate",
            ],
            "algorithm_card_refs": [
                "versioned-vector-blob-storage-algorithm",
                "cortex-sync-protocol-algorithm",
                "compiler-gate-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 sync-cortex -Tag \"C:\\Users\\jacks\\OneDrive\\Desktop\\Cortex\"",
                "cd Cortex",
                "python -m cortex --home ..\\state\\cortex_memory migrate-vectors --repo nexus-gate --json",
                "python -m Cortex.benchmarks.vector_migration_benchmark",
                ".\\scripts\\nexus.ps1 cortex",
            ],
            "evidence_surfaces": [
                "reports/nexus_cortex_gate_latest.json",
                "reports/nexus_cortex_sync_report_latest.json",
                "reports/nexus_cortex_vector_benchmark_latest.json",
                "docs/runtime/NEXUS_CORTEX.md",
            ],
            "next_versions": [
                "v0.2: add benchmark trend ledger for vector payload/query measurements",
                "v0.3: expose Cortex vector health in Meta-Orchestrator/System Monitor HUD",
                "v0.4: add safe bootstrap refresh lane after source sync",
            ],
            "boundary": "Local memory optimization only. It does not prove retrieval correctness, model understanding, safety, security, or mutation authority.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "predictive-memory-orchestrator",
            "version": "0.1.0",
            "title": "Predictive Memory Orchestrator",
            "status": "active",
            "summary": "NEXUS can reduce wasted validation cycles when Cortex memory health, vector benchmark trends, algorithm cards, discovery cards, and predictive evolve plans are fused into one recommendation-only packet.",
            "math": {
                "memory_gain": "gain = vector_payload_reduction_percent + max(query_delta_ms, 0)",
                "card_readiness": "ready = missing_algorithms == 0 and missing_discoveries == 0",
                "gate_rule": "next = cortex_repair if memory_unhealthy else predictive_evolve_next_step",
                "authority_rule": "commit_allowed = final_evolve_passed and human_authorized",
                "control_loop": "memory -> cards -> timing -> recommend -> record -> require seal",
            },
            "code_references": [
                "nexus_gate/loops/predictive_memory_orchestrator.py::build_predictive_memory_orchestrator",
                "nexus_gate/loops/predictive_memory_orchestrator.py::_cortex_status",
                "nexus_gate/loops/predictive_memory_orchestrator.py::_recommend",
                "nexus_gate/loops/predictive_evolve.py::build_predictive_evolve_plan",
            ],
            "algorithm_card_refs": [
                "predictive-memory-orchestrator-algorithm",
                "predictive-evolve-planner-algorithm",
                "versioned-vector-blob-storage-algorithm",
                "cortex-sync-protocol-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 cortex",
                ".\\scripts\\nexus.ps1 predictive-evolve",
                ".\\scripts\\nexus.ps1 predictive-memory",
                "Inspect reports/nexus_predictive_memory_orchestrator_latest.json",
                "Run .\\scripts\\nexus.ps1 evolve before commit",
            ],
            "evidence_surfaces": [
                "reports/nexus_predictive_memory_orchestrator_latest.json",
                "state/loops/nexus_predictive_memory_orchestrator_latest.json",
                "ledger/cortex_benchmark_trends.jsonl",
                "reports/nexus_cortex_gate_latest.json",
                "reports/nexus_predictive_evolve_plan_latest.json",
            ],
            "next_versions": [
                "v0.2: add Cortex certificate refresh lane",
                "v0.3: expose predictive memory state in Electron System Monitor HUD",
                "v0.4: add retrieval confidence trend rows after Cortex query runs",
            ],
            "boundary": "Recommendation-only. It may choose the next evidence lane; it may not execute the plan, mutate memory, or skip final evolve before commit.",
        }
    ]
    return {
        "schema": SCHEMA,
        "system": SYSTEM,
        "version": VERSION,
        "generated_at_utc": _utc(),
        "card_count": len(cards),
        "cards": cards,
        "portal_entry": "[18] Discoveries",
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_discovery_cards(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    packet = build_discovery_cards(root)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    for rel in (LATEST_PATH, VERSIONED_PATH):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS discovery cards.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_discovery_cards(args.root)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"wrote {packet['card_count']} NEXUS discovery cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
