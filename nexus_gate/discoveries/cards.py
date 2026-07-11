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
