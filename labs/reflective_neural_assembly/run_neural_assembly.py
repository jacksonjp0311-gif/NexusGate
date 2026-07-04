from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

LAB_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB_ROOT))

from assembly.neural.neural_optional import torch_status
from assembly.neural.smart_policy import decide
from assembly.runtime.realtime_evolution import RealtimeEvolutionEngine
from assembly.telemetry.neuralforge_event_codec import (
    make_parent_emitter_packet,
    packet_to_dict,
    telemetry_adapter_contract,
)


def build_report(intent: str) -> dict:
    engine = RealtimeEvolutionEngine()
    if not engine.events:
        engine.ingest({"workflow_name": "bootstrap_observation", "tool_name": "neural_assembly", "success": True, "duration_ms": 0, "step_count": 1})
    memory = engine.report()
    decision = decide("analyze", context={"intent": intent}, history=engine.events)
    packet = make_parent_emitter_packet(intent=intent, raw_text=decision["recommendation"], source_model="local_fallback")
    return {
        "system": "NEXUS Reflective Neural Assembly",
        "version": "0.5.0",
        "status": "pass",
        "intent": intent,
        "reasoning_mode": decision["mode"],
        "recommendation": decision["recommendation"],
        "confidence": decision["confidence"],
        "why": decision["reasoning"],
        "uncertainty": ["standard-library fallback is heuristic", "no external telemetry adapters enabled"],
        "blocked_actions": decision["blocked_actions"],
        "telemetry_adapters": telemetry_adapter_contract(),
        "optional_neural": torch_status(),
        "parent_emitter_packet": packet_to_dict(packet),
        "raw_evidence_report": memory,
        "claim_boundary": "Reflective Neural Assembly is recommendation-only lab evidence. It does not execute shell, mutate the parent repo, write external APIs, access secrets, or self-authorize.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NEXUS Reflective Neural Assembly lab")
    parser.add_argument("--intent", required=True)
    args = parser.parse_args()
    report = build_report(args.intent)
    reports_dir = LAB_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / "neural_assembly_report_latest.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("NEXUS Reflective Neural Assembly")
    print(f"reasoning_mode: {report['reasoning_mode']}")
    print(f"recommendation: {report['recommendation']}")
    print(f"confidence: {report['confidence']}")
    print(f"uncertainty: {'; '.join(report['uncertainty'])}")
    print(f"blocked_actions: {', '.join(report['blocked_actions'])}")
    print(f"report: {path}")


if __name__ == "__main__":
    main()
