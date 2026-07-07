"""Streaming TNN chat lane for NexusGate.

v0.2.0L â€” Stream Guard v2:
- streams local Mistral tokens through a short safety buffer
- allows defensive engineering language such as repo hardening and vulnerability audits
- rewrites before unsafe buffered phrases are printed
- records time-to-first-token and total latency
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
from typing import Any, Dict, List, Tuple

BRAIN_DIR = Path(__file__).resolve().parent
if str(BRAIN_DIR) not in sys.path:
    sys.path.insert(0, str(BRAIN_DIR))

from context_builder import build_context
from memory_store import write_memory


OLLAMA_URL = os.environ.get("TNN_OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.environ.get("TNN_MODEL", "tnn-mistral:latest")
TNN_ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PROMPT_PATH = TNN_ROOT / "brain" / "system_prompt.md"

ENGINE_VERSION = "tnn.stream_chat.v0.2.0L"

DEFENSIVE_ALLOWLIST = [
    "harden against vulnerabilities",
    "harden vulnerabilities",
    "vulnerability audit",
    "safe vulnerability review",
    "dependency audit",
    "security tests",
    "security test",
    "repo hardening",
    "defensive hardening",
    "input validation",
    "safe review",
    "defensive review",
    "threat model",
    "secure coding",
    "patch verification",
    "test coverage",
    "latency benchmark",
    "ux",
    "memory",
    "reliability",
    "governance",
]

OFFENSIVE_BLOCKLIST = [
    "attack strategy",
    "entry points",
    "exploit targets",
    "targets within",
    "credential access",
    "steal credentials",
    "persistence mechanism",
    "evasion technique",
    "payload delivery",
    "exploit chain",
    "lateral movement",
    "privilege escalation",
    "malware",
    "phishing",
    "exfiltration",
    "backdoor",
]


def read_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8-sig")


def allowed_defensive_context(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in DEFENSIVE_ALLOWLIST)


def violates_operator_boundary(text: str) -> bool:
    low = text.lower()
    if allowed_defensive_context(low):
        return False
    return any(term in low for term in OFFENSIVE_BLOCKLIST)


def safe_fallback(intent: str) -> str:
    return (
        "TNN // OPERATOR ALIGNMENT\n"
        "next: harden the NexusGate chat lane: add stream-guard tests and latency metrics.\n"
        "then: wire the clean stream into the Electron chat panel.\n"
        "focus: UX, memory, reliability, safe automation, and repo governance.\n"
        "boundary: no offensive cyber planning."
    )


def should_flush(buffer: str) -> bool:
    if not buffer:
        return False
    if len(buffer) >= 72:
        return True
    return any(buffer.endswith(mark) for mark in [".", "!", "?", "\n", ":", ";"])


def safe_flush(buffer: str, printed_any: bool) -> Tuple[str, bool]:
    if not buffer:
        return "", printed_any
    print(buffer, end="", flush=True)
    return "", True


def stream_generate(intent: str, model: str, timeout: float) -> Dict[str, Any]:
    start = time.perf_counter()
    first_token_at: float | None = None
    prompt = build_context(intent)
    system = read_system_prompt()

    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": True,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.12,
            "top_p": 0.8,
            "num_ctx": 512,
            "num_predict": 48,
            "repeat_penalty": 1.12,
        },
    }

    request = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    chunks: List[str] = []
    buffer = ""
    printed_any = False
    ok = True
    error = ""
    boundary_rewrite = False

    print("")
    print("TNN CHAT")
    print("--------", flush=True)

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw_line in response:
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue

                piece = item.get("response") or ""
                if piece:
                    if first_token_at is None:
                        first_token_at = time.perf_counter()
                    chunks.append(piece)
                    buffer += piece

                joined = "".join(chunks)
                if violates_operator_boundary(joined):
                    boundary_rewrite = True
                    buffer = ""
                    break

                if should_flush(buffer):
                    buffer, printed_any = safe_flush(buffer, printed_any)

                if item.get("done"):
                    break

        if buffer and not boundary_rewrite:
            buffer, printed_any = safe_flush(buffer, printed_any)

        if printed_any:
            print("", flush=True)
    except (TimeoutError, socket.timeout) as exc:
        ok = False
        error = f"Ollama timed out after {timeout}s: {exc}"
    except urllib.error.URLError as exc:
        ok = False
        error = f"Ollama unavailable: {exc}"
    except Exception as exc:
        ok = False
        error = f"Ollama stream failure: {exc}"

    text = "".join(chunks).strip()

    if boundary_rewrite:
        ok = True
        error = "operator boundary rewrite applied"
        text = safe_fallback(intent)
        if printed_any:
            print("")
        print(text, flush=True)

    if not ok or not text:
        if not text:
            text = (
                "TNN // MODEL WARMING\n"
                "Mistral did not stream a response yet.\n"
                "next: run prewarm, then retry once.\n"
                "safe: NexusGate did not crash.\n"
                "boundary: recommendation-only."
            )
        print(text, flush=True)

    total_latency_ms = int((time.perf_counter() - start) * 1000)
    ttft_ms = None if first_token_at is None else int((first_token_at - start) * 1000)

    packet = {
        "ok": ok and bool(text),
        "engine_version": ENGINE_VERSION,
        "role": "TNN",
        "model": model,
        "intent": intent,
        "response": text,
        "time_to_first_token_ms": ttft_ms,
        "latency_ms": total_latency_ms,
        "total_latency_ms": total_latency_ms,
        "error": error,
        "boundary_rewrite": boundary_rewrite,
        "boundary": "recommendation-only; no offensive cyber guidance; no shell execution, mutation, live pulls, scraping, or autonomous authority",
    }
    write_memory(packet)

    print("")
    print("model: Tesseract Neural Network/mistral-chat-brain")
    print(f"backend: {model}")
    if ttft_ms is not None:
        print(f"ttft_ms: {ttft_ms}")
    print(f"total_ms: {total_latency_ms}")
    if error:
        print(f"note: {error}")
    print("mode: stream_guard_v2")
    return packet


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", required=True)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TNN_STREAM_TIMEOUT_SECONDS", "45")))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    packet = stream_generate(args.intent, model=args.model, timeout=args.timeout)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
