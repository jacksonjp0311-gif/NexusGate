"""Prewarm local TNN Mistral model so tnn-chat responds quickly."""

from __future__ import annotations

import argparse
import json
import time

from ollama_adapter import generate, OllamaError, DEFAULT_MODEL


SYSTEM = "You are TNN. Reply with exactly: TNN READY"
PROMPT = "Warm the model. Reply with exactly: TNN READY"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    start = time.perf_counter()
    try:
        result = generate(
            prompt=PROMPT,
            system=SYSTEM,
            model=args.model,
            timeout=args.timeout,
            num_predict=8,
        )
        packet = {
            "ok": True,
            "model": result.get("model_requested", args.model),
            "response": (result.get("response") or "").strip(),
            "latency_ms": int((time.perf_counter() - start) * 1000),
            "next": "Run .\\scripts\\nexus.ps1 tnn-chat -Tag \"...\" -CallModel",
        }
    except OllamaError as error:
        packet = {
            "ok": False,
            "model": args.model,
            "error": str(error),
            "latency_ms": int((time.perf_counter() - start) * 1000),
            "next": "Open/start Ollama, verify `ollama list`, then rerun prewarm.",
        }

    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        if packet["ok"]:
            print("TNN PREWARM // READY")
            print(f"model: {packet['model']}")
            print(f"latency_ms: {packet['latency_ms']}")
            print(packet["next"])
        else:
            print("TNN PREWARM // NOT READY")
            print(f"model: {packet['model']}")
            print(f"error: {packet['error']}")
            print(packet["next"])


if __name__ == "__main__":
    main()
