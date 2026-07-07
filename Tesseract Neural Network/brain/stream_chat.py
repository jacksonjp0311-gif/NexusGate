"""Streaming TNN chat lane for NexusGate.

Streams local Mistral tokens for operator chat while enforcing NexusGate's
safe-development domain. v0.2.0K adds an alignment guard against cyber-offense drift.
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
from typing import Any, Dict, List

BRAIN_DIR = Path(__file__).resolve().parent
if str(BRAIN_DIR) not in sys.path:
    sys.path.insert(0, str(BRAIN_DIR))

from context_builder import build_context
from memory_store import write_memory


OLLAMA_URL = os.environ.get("TNN_OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.environ.get("TNN_MODEL", "tnn-mistral:latest")
TNN_ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PROMPT_PATH = TNN_ROOT / "brain" / "system_prompt.md"

RISK_TERMS = [
    "attack strategy",
    "entry points",
    "exploit",
    "exploitation",
    "credential",
    "payload",
    "persistence",
    "evasion",
    "targets within",
    "vulnerabilities",
]


def read_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8-sig")


def violates_operator_boundary(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in RISK_TERMS)


def safe_fallback(intent: str) -> str:
    return (
        "TNN // OPERATOR ALIGNMENT\n"
        "next: harden the NexusGate chat lane: add tests, tune prompt, verify stream latency.\n"
        "then: commit only validated repo/product changes.\n"
        "focus: UX, memory, reliability, and safe automation.\n"
        "boundary: no offensive cyber planning."
    )


def stream_generate(intent: str, model: str, timeout: float) -> Dict[str, Any]:
    start = time.perf_counter()
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
                    chunks.append(piece)

                joined = "".join(chunks)
                if violates_operator_boundary(joined):
                    boundary_rewrite = True
                    break

                if piece:
                    print(piece, end="", flush=True)

                if item.get("done"):
                    break
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

    latency_ms = int((time.perf_counter() - start) * 1000)
    packet = {
        "ok": ok and bool(text),
        "engine_version": "tnn.stream_chat.v0.2.0K",
        "role": "TNN",
        "model": model,
        "intent": intent,
        "response": text,
        "latency_ms": latency_ms,
        "error": error,
        "boundary_rewrite": boundary_rewrite,
        "boundary": "recommendation-only; no offensive cyber guidance; no shell execution, mutation, live pulls, scraping, or autonomous authority",
    }
    write_memory(packet)

    print("")
    print(f"model: Tesseract Neural Network/mistral-chat-brain")
    print(f"backend: {model}")
    print(f"latency_ms: {latency_ms}")
    if error:
        print(f"note: {error}")
    print("mode: stream")
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
