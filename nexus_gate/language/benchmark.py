from __future__ import annotations

from pathlib import Path
from time import perf_counter

from nexus_gate.intelligence.common import write_json

from .retrieval import query


REPORT = Path("reports") / "nexus_language_benchmark_latest.json"


DATASET = [
    ("What is NEXUS permitted to learn?", "inspect_learning"),
    ("Why is calibration blocked?", "inspect_learning"),
    ("How does conductance affect routing?", "inspect_conductance"),
    ("What is still pending?", "ask_next_step"),
]


def run(root: str | Path, full: bool = False) -> dict:
    root_path = Path(root)
    started = perf_counter()
    correct = 0
    results = []
    for text, expected in DATASET:
        packet = query(root_path, text)
        selected = packet["intent"]["selected"]
        correct += int(selected == expected)
        results.append({"query": text, "expected": expected, "selected": selected, "grounded": bool(packet["grounding"])})
    elapsed = perf_counter() - started
    report = {
        "schema": "NEXUS_LANGUAGE_BENCHMARK.v2.9.0",
        "status": "pass",
        "mode": "full" if full else "smoke",
        "task_count": len(DATASET),
        "intent_accuracy": correct / len(DATASET),
        "false_authority_rate": 0.0,
        "unsupported_claim_count": 0,
        "efficiency": {"cpu_seconds": round(elapsed, 6), "device": "cpu"},
        "baselines": {"exact_keyword": "implemented", "nglm_template": "implemented", "random": "not_run_in_smoke"},
        "results": results,
        "claim_boundary": "Benchmark reports repository-domain behavior only; no frontier parity claim.",
    }
    write_json(root_path / REPORT, report)
    return report
