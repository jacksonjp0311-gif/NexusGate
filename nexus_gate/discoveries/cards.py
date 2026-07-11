from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SYSTEM = "NEXUS_DISCOVERY_CARDS"
VERSION = "0.1.0"
SCHEMA = "NEXUS_DISCOVERY_CARD_SET.v0.1.0"
LATEST_PATH = Path("state/discoveries/nexus_discovery_cards_latest.json")
VERSIONED_PATH = Path("state/discoveries/nexus_discovery_cards.v0.1.0.json")

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
