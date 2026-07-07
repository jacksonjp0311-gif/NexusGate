"""TNN v0.2.0 Mistral chat engine."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict

from ollama_adapter import generate, OllamaError, DEFAULT_MODEL, FALLBACK_MODEL
from context_builder import build_context
from memory_store import write_memory


BRAIN_DIR = Path(__file__).resolve().parent
if str(BRAIN_DIR) not in sys.path:
    sys.path.insert(0, str(BRAIN_DIR))

TNN_ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PROMPT_PATH = TNN_ROOT / "brain" / "system_prompt.md"
CHAT_ENGINE_VERSION = "tnn.chat_engine.v0.2.0"


def read_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8-sig")


def tighten(text: str, max_lines: int = 10) -> str:
    lines = [line.rstrip() for line in text.strip().splitlines()]
    lines = [line for line in lines if line.strip()]
    if not lines:
        return "TNN is online, but the local model returned an empty response."
    return "\n".join(lines[:max_lines])


def chat(intent: str, model: str | None = None, timeout: float = 6.0) -> Dict[str, Any]:
    start = time.perf_counter()
    system = read_system_prompt()
    prompt = build_context(intent)
    try:
        result = generate(prompt=prompt, system=system, model=model, timeout=timeout)
        raw = result.get("response", "")
        response = tighten(raw)
        ok = True
        error = ""
        model_used = result.get("model_requested", model or DEFAULT_MODEL)
        fallback_used = bool(result.get("fallback_used", False))
    except OllamaError as exc:
        response = (
            "TNN // MODEL WARMING\n"
            "Mistral/Ollama did not answer inside the fast gate.\n"
            "next: retry once; if cold, start Ollama or rebuild tnn-mistral.\n"
            "safe: NexusGate did not crash and no shell action was taken.\n"
            "boundary: recommendation-only; no mutation authority."
        )
        ok = False
        error = str(exc)
        model_used = model or DEFAULT_MODEL
        fallback_used = False

    latency_ms = int((time.perf_counter() - start) * 1000)
    packet = {
        "ok": ok,
        "engine_version": CHAT_ENGINE_VERSION,
        "role": "TNN",
        "model": model_used,
        "fallback_model": FALLBACK_MODEL,
        "fallback_used": fallback_used,
        "intent": intent,
        "response": response,
        "latency_ms": latency_ms,
        "error": error,
        "boundary": "recommendation-only; no shell execution, mutation, live pulls, scraping, or autonomous authority",
    }
    write_memory(packet)
    return packet


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", required=True)
    parser.add_argument("--model", default="")
    parser.add_argument("--timeout", type=float, default=6.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    packet = chat(args.intent, model=args.model or None, timeout=args.timeout)
    print(json.dumps(packet, indent=2, sort_keys=True) if args.json else packet["response"])


if __name__ == "__main__":
    main()
