"""TNN runtime health + benchmark reporter.

Runs the streaming TNN lane, captures scaffold/model timing metrics, writes a
stable health report for operators and UI surfaces.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict

BRAIN_DIR = Path(__file__).resolve().parent
if str(BRAIN_DIR) not in sys.path:
    sys.path.insert(0, str(BRAIN_DIR))

import stream_chat


TNN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TNN_ROOT.parent
REPORT_PATH = REPO_ROOT / "reports" / "tnn_runtime_health_latest.json"
TEXT_REPORT_PATH = REPO_ROOT / "reports" / "tnn_runtime_health_latest.md"


def classify(packet: Dict[str, Any]) -> str:
    if not packet.get("ok"):
        return "offline"
    scaffold_ms = packet.get("scaffold_ms")
    ttft_ms = packet.get("time_to_first_token_ms")
    total_ms = packet.get("total_latency_ms") or packet.get("latency_ms")

    if ttft_ms is None:
        return "scaffold_only"
    if ttft_ms <= 3000 and total_ms <= 12000:
        return "hot"
    if ttft_ms <= 8000 and total_ms <= 20000:
        return "warm"
    return "slow"


def compact_output(text: str, limit: int = 1200) -> str:
    text = re.sub(r"\s+\n", "\n", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]"


def write_reports(packet: Dict[str, Any], captured: str, intent: str) -> Dict[str, Any]:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    state = classify(packet)
    report = {
        "ok": bool(packet.get("ok")),
        "state": state,
        "role": "TNN",
        "engine_version": packet.get("engine_version"),
        "model": packet.get("model"),
        "intent": intent,
        "scaffold_ms": packet.get("scaffold_ms"),
        "ttft_ms": packet.get("time_to_first_token_ms"),
        "total_ms": packet.get("total_latency_ms") or packet.get("latency_ms"),
        "boundary_rewrite": packet.get("boundary_rewrite"),
        "deep": packet.get("deep"),
        "error": packet.get("error") or "",
        "mode": "fast_scaffold_stream_guard_v3",
        "ui_badge": {
            "label": f"TNN {state.upper()}",
            "state": state,
            "model": packet.get("model"),
        },
        "captured_output": compact_output(captured),
        "next": (
            "Wire reports/tnn_runtime_health_latest.json into the Electron chat panel "
            "as a TNN model-health badge."
        ),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    md = [
        "# TNN Runtime Health",
        "",
        f"- state: {state}",
        f"- ok: {report['ok']}",
        f"- model: {report['model']}",
        f"- engine_version: {report['engine_version']}",
        f"- scaffold_ms: {report['scaffold_ms']}",
        f"- ttft_ms: {report['ttft_ms']}",
        f"- total_ms: {report['total_ms']}",
        f"- boundary_rewrite: {report['boundary_rewrite']}",
        f"- mode: {report['mode']}",
        "",
        "## Captured Output",
        "",
        "```text",
        report["captured_output"],
        "```",
        "",
        "## Next",
        "",
        report["next"],
    ]
    TEXT_REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", default="Give me the next NexusGate move, snappy AF.")
    parser.add_argument("--model", default=stream_chat.MODEL)
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TNN_STREAM_TIMEOUT_SECONDS", "8")))
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    start = time.perf_counter()
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        packet = stream_chat.stream_generate(
            args.intent,
            model=args.model,
            timeout=args.timeout if not args.deep else max(args.timeout, 45.0),
            scaffold=True,
            deep=args.deep,
        )
    captured = stdout.getvalue()
    report = write_reports(packet, captured, args.intent)
    report["benchmark_wall_ms"] = int((time.perf_counter() - start) * 1000)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return

    print("TNN RUNTIME HEALTH")
    print("------------------")
    print(f"state: {report['state']}")
    print(f"model: {report['model']}")
    print(f"scaffold_ms: {report['scaffold_ms']}")
    print(f"ttft_ms: {report['ttft_ms']}")
    print(f"total_ms: {report['total_ms']}")
    print(f"report: {REPORT_PATH}")
    print(f"badge: {report['ui_badge']['label']}")
    print("")
    print("captured:")
    print(report["captured_output"])


if __name__ == "__main__":
    main()
