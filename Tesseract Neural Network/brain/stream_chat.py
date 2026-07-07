"""Streaming TNN chat lane for NexusGate.

This bypasses the router envelope for live operator chat and streams tokens as
Ollama emits them. It preserves the governed TNN system prompt, compact context,
memory write, and recommendation-only boundary.
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


def read_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8-sig")


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
            "temperature": 0.18,
            "top_p": 0.85,
            "num_ctx": 512,
            "num_predict": 48,
            "repeat_penalty": 1.08,
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
        "ok": ok and bool("".join(chunks).strip()),
        "engine_version": "tnn.stream_chat.v0.2.0J",
        "role": "TNN",
        "model": model,
        "intent": intent,
        "response": text,
        "latency_ms": latency_ms,
        "error": error,
        "boundary": "recommendation-only; no shell execution, mutation, live pulls, scraping, or autonomous authority",
    }
    write_memory(packet)

    print("")
    print(f"model: Tesseract Neural Network/mistral-chat-brain")
    print(f"backend: {model}")
    print(f"latency_ms: {latency_ms}")
    if error:
        print(f"error: {error}")
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
