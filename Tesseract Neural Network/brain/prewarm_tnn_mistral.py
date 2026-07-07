"""Bounded TNN Mistral prewarm command.

v0.2.0R:
- never dumps raw traceback for slow/cold Ollama
- writes reports/tnn_warm_latest.json
- exits cleanly for operator use
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict


BRAIN_DIR = Path(__file__).resolve().parent
TNN_ROOT = BRAIN_DIR.parents[0]
REPO_ROOT = TNN_ROOT.parent
REPORT_PATH = REPO_ROOT / "reports" / "tnn_warm_latest.json"

OLLAMA_URL = os.environ.get("TNN_OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("TNN_MODEL", "tnn-phi4-mini:latest")


def post_generate(model: str, timeout: float) -> Dict[str, Any]:
    payload = {
        "model": model,
        "prompt": "TNN READY",
        "system": "You are TNN. Reply with exactly: TNN READY",
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.0,
            "num_ctx": 256,
            "num_predict": 4,
        },
    }
    request = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
        return json.loads(raw)


def write_report(packet: Dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")


def classify_error(error: BaseException) -> str:
    text = str(error).lower()
    if isinstance(error, KeyboardInterrupt):
        return "interrupted"
    if isinstance(error, (TimeoutError, socket.timeout)):
        return "timeout"
    if isinstance(error, urllib.error.URLError):
        return "ollama_unavailable"
    if "timed out" in text or "timeout" in text:
        return "timeout"
    if "connection refused" in text:
        return "ollama_unavailable"
    return "error"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TNN_WARM_TIMEOUT_SECONDS", "18")))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when warm fails.")
    args = parser.parse_args()

    start = time.perf_counter()
    packet: Dict[str, Any]

    try:
        result = post_generate(args.model, args.timeout)
        response = (result.get("response") or "").strip()
        ok = bool(response)
        packet = {
            "ok": ok,
            "state": "warm" if ok else "empty_response",
            "model": args.model,
            "response": response,
            "latency_ms": int((time.perf_counter() - start) * 1000),
            "timeout_seconds": args.timeout,
            "report": str(REPORT_PATH),
            "next": "Run .\\scripts\\nexus.ps1 tnn-health, then tnn-chat.",
        }
    except KeyboardInterrupt as error:
        packet = {
            "ok": False,
            "state": "interrupted",
            "model": args.model,
            "error": "operator interrupted prewarm",
            "latency_ms": int((time.perf_counter() - start) * 1000),
            "timeout_seconds": args.timeout,
            "report": str(REPORT_PATH),
            "next": "Use tnn-chat scaffold now, or retry tnn-warm later.",
        }
    except BaseException as error:
        state = classify_error(error)
        packet = {
            "ok": False,
            "state": state,
            "model": args.model,
            "error": str(error),
            "latency_ms": int((time.perf_counter() - start) * 1000),
            "timeout_seconds": args.timeout,
            "report": str(REPORT_PATH),
            "next": (
                "Use tnn-chat scaffold now. If local Mistral is needed, restart Ollama, "
                "verify `ollama list`, then retry tnn-warm or use tnn-deep."
            ),
        }

    write_report(packet)

    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        if packet["ok"]:
            print("TNN WARM // READY")
        else:
            print("TNN WARM // NOT READY")
        print(f"state: {packet['state']}")
        print(f"model: {packet['model']}")
        print(f"latency_ms: {packet['latency_ms']}")
        if packet.get("error"):
            print(f"reason: {packet['error']}")
        print(f"report: {packet['report']}")
        print(f"next: {packet['next']}")

    if args.strict and not packet["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


