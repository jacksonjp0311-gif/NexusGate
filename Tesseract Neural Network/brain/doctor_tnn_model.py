"""TNN local model doctor.

v0.2.0S:
- inspects Ollama availability
- lists installed/running models when possible
- probes tnn-mistral with a bounded stream request
- writes reports/tnn_model_doctor_latest.json and .md
- exits cleanly for operator use
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple


BRAIN_DIR = Path(__file__).resolve().parent
TNN_ROOT = BRAIN_DIR.parents[0]
REPO_ROOT = TNN_ROOT.parent
REPORT_JSON = REPO_ROOT / "reports" / "tnn_model_doctor_latest.json"
REPORT_MD = REPO_ROOT / "reports" / "tnn_model_doctor_latest.md"

OLLAMA_URL = os.environ.get("TNN_OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("TNN_MODEL", "tnn-mistral:latest")


def run_cmd(args: List[str], timeout: float = 8.0) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "latency_ms": int((time.perf_counter() - start) * 1000),
        }
    except FileNotFoundError as error:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(error),
            "latency_ms": int((time.perf_counter() - start) * 1000),
        }
    except subprocess.TimeoutExpired as error:
        return {
            "ok": False,
            "returncode": None,
            "stdout": (error.stdout or "").strip() if isinstance(error.stdout, str) else "",
            "stderr": "command timed out",
            "latency_ms": int((time.perf_counter() - start) * 1000),
        }


def http_json(path: str, timeout: float = 5.0) -> Dict[str, Any]:
    url = OLLAMA_URL.rstrip("/") + path
    request = urllib.request.Request(url, method="GET")
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return {
                "ok": True,
                "data": json.loads(raw),
                "error": "",
                "latency_ms": int((time.perf_counter() - start) * 1000),
            }
    except BaseException as error:
        return {
            "ok": False,
            "data": None,
            "error": str(error),
            "latency_ms": int((time.perf_counter() - start) * 1000),
        }


def probe_stream(model: str, timeout: float = 8.0) -> Dict[str, Any]:
    payload = {
        "model": model,
        "prompt": "Reply with exactly: TNN READY",
        "system": "You are TNN. Reply with exactly: TNN READY",
        "stream": True,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.0,
            "num_ctx": 256,
            "num_predict": 4,
        },
    }
    request = urllib.request.Request(
        OLLAMA_URL.rstrip("/") + "/api/generate",
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    first_token_ms = None
    chunks: List[str] = []
    done = False
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw_line in response:
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                item = json.loads(line)
                piece = item.get("response") or ""
                if piece:
                    if first_token_ms is None:
                        first_token_ms = int((time.perf_counter() - start) * 1000)
                    chunks.append(piece)
                if item.get("done"):
                    done = True
                    break
        total_ms = int((time.perf_counter() - start) * 1000)
        return {
            "ok": bool(chunks),
            "state": "ready" if bool(chunks) else "empty",
            "model": model,
            "first_token_ms": first_token_ms,
            "total_ms": total_ms,
            "done": done,
            "response": "".join(chunks).strip(),
            "error": "",
        }
    except (TimeoutError, socket.timeout) as error:
        return {
            "ok": False,
            "state": "timeout",
            "model": model,
            "first_token_ms": first_token_ms,
            "total_ms": int((time.perf_counter() - start) * 1000),
            "done": done,
            "response": "".join(chunks).strip(),
            "error": str(error),
        }
    except urllib.error.URLError as error:
        return {
            "ok": False,
            "state": "unavailable",
            "model": model,
            "first_token_ms": first_token_ms,
            "total_ms": int((time.perf_counter() - start) * 1000),
            "done": done,
            "response": "".join(chunks).strip(),
            "error": str(error),
        }
    except BaseException as error:
        return {
            "ok": False,
            "state": "error",
            "model": model,
            "first_token_ms": first_token_ms,
            "total_ms": int((time.perf_counter() - start) * 1000),
            "done": done,
            "response": "".join(chunks).strip(),
            "error": str(error),
        }


def extract_model_names(tags_payload: Dict[str, Any]) -> List[str]:
    data = tags_payload.get("data") or {}
    models = data.get("models") if isinstance(data, dict) else []
    names: List[str] = []
    if isinstance(models, list):
        for item in models:
            if isinstance(item, dict) and item.get("name"):
                names.append(str(item["name"]))
    return names


def classify(report: Dict[str, Any]) -> str:
    if not report["ollama_api"].get("ok"):
        return "ollama_unavailable"
    probe = report["probe"]
    if probe.get("ok") and (probe.get("first_token_ms") or 999999) <= 3000:
        return "ready_hot"
    if probe.get("ok"):
        return "ready_warm"
    if probe.get("state") == "timeout" and probe.get("first_token_ms") is not None:
        return "slow_partial"
    if probe.get("state") == "timeout":
        return "cold_or_slow"
    if DEFAULT_MODEL not in report.get("installed_models", []):
        return "model_missing"
    return "not_ready"


def recommended_next(state: str) -> str:
    if state in {"ready_hot", "ready_warm"}:
        return "Run .\\scripts\\nexus.ps1 tnn-chat or wire the TNN health badge into Electron."
    if state == "model_missing":
        return "Run .\\Tesseract Neural Network\\brain\\build_tnn_mistral.ps1 or verify `ollama list` contains tnn-mistral:latest."
    if state == "ollama_unavailable":
        return "Start or restart Ollama, then rerun .\\scripts\\nexus.ps1 tnn-doctor."
    if state in {"cold_or_slow", "slow_partial"}:
        return "Keep using scaffold fast lane; use tnn-deep for full model waits, or install/configure a smaller fast local model."
    return "Use tnn-chat scaffold now and inspect the doctor report."


def write_reports(report: Dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    md = [
        "# TNN Model Doctor",
        "",
        f"- state: {report['state']}",
        f"- model: {report['model']}",
        f"- ollama_url: {report['ollama_url']}",
        f"- ollama_cli_ok: {report['ollama_version'].get('ok')}",
        f"- ollama_api_ok: {report['ollama_api'].get('ok')}",
        f"- installed_models: {', '.join(report.get('installed_models') or []) if report.get('installed_models') else 'none detected'}",
        f"- probe_state: {report['probe'].get('state')}",
        f"- probe_first_token_ms: {report['probe'].get('first_token_ms')}",
        f"- probe_total_ms: {report['probe'].get('total_ms')}",
        f"- next: {report['next']}",
        "",
        "## Probe",
        "",
        "```json",
        json.dumps(report["probe"], indent=2, sort_keys=True),
        "```",
    ]
    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TNN_DOCTOR_TIMEOUT_SECONDS", "8")))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    version = run_cmd(["ollama", "--version"], timeout=8)
    list_cmd = run_cmd(["ollama", "list"], timeout=8)
    ps_cmd = run_cmd(["ollama", "ps"], timeout=8)
    tags = http_json("/api/tags", timeout=5)
    probe = probe_stream(args.model, timeout=args.timeout)

    report: Dict[str, Any] = {
        "ok": False,
        "model": args.model,
        "ollama_url": OLLAMA_URL,
        "ollama_version": version,
        "ollama_list": list_cmd,
        "ollama_ps": ps_cmd,
        "ollama_api": tags,
        "installed_models": extract_model_names(tags),
        "probe": probe,
        "report": str(REPORT_JSON),
    }
    report["state"] = classify(report)
    report["ok"] = report["state"] in {"ready_hot", "ready_warm", "slow_partial", "cold_or_slow"}
    report["next"] = recommended_next(report["state"])
    report["ui_badge"] = {
        "label": "TNN " + report["state"].upper(),
        "state": report["state"],
        "model": args.model,
    }

    write_reports(report)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    print("TNN MODEL DOCTOR")
    print("----------------")
    print(f"state: {report['state']}")
    print(f"model: {args.model}")
    print(f"ollama_api: {tags.get('ok')}")
    print(f"installed_models: {', '.join(report['installed_models']) if report['installed_models'] else 'none detected'}")
    print(f"probe_state: {probe.get('state')}")
    print(f"probe_first_token_ms: {probe.get('first_token_ms')}")
    print(f"probe_total_ms: {probe.get('total_ms')}")
    if probe.get("error"):
        print(f"probe_error: {probe.get('error')}")
    print(f"report: {REPORT_JSON}")
    print(f"badge: {report['ui_badge']['label']}")
    print(f"next: {report['next']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
