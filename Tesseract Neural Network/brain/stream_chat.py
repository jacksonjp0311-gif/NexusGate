"""Streaming TNN chat lane for NexusGate.

v0.2.0M â€” Fast Scaffold Lane:
- prints an immediate safe operator scaffold
- gives Mistral a short fast budget by default
- keeps deep Mistral available with --deep
- preserves Stream Guard v2 boundary logic
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

ENGINE_VERSION = "tnn.stream_chat.v0.2.0M"

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


def fast_scaffold(intent: str) -> str:
    return (
        "TNN // FAST SCAFFOLD\n"
        "next: wire the streaming TNN lane into the Electron chat panel.\n"
        "then: add a latency benchmark and model-health badge.\n"
        "verify: run tests, commit, push.\n"
        "boundary: recommendation-only."
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


def stream_generate(
    intent: str,
    model: str,
    timeout: float,
    scaffold: bool = True,
    deep: bool = False,
) -> Dict[str, Any]:
    start = time.perf_counter()
    first_token_at: float | None = None
    scaffold_at: float | None = None
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
            "num_predict": 48 if not deep else 120,
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
    scaffold_text = ""

    print("")
    print("TNN CHAT")
    print("--------", flush=True)

    if scaffold:
        scaffold_text = fast_scaffold(intent)
        scaffold_at = time.perf_counter()
        print(scaffold_text, flush=True)
        print("", flush=True)
        print("TNN // MISTRAL STREAM", flush=True)

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

    model_text = "".join(chunks).strip()

    if boundary_rewrite:
        ok = True
        error = "operator boundary rewrite applied"
        model_text = safe_fallback(intent)
        if printed_any:
            print("")
        print(model_text, flush=True)

    if not ok or not model_text:
        if not model_text:
            model_text = (
                "TNN // MODEL BUDGET HIT\n"
                "Mistral did not stream inside the fast budget.\n"
                "next: use the scaffold now, or rerun with --deep for full Mistral.\n"
                "safe: NexusGate did not crash.\n"
                "boundary: recommendation-only."
            )
        print(model_text, flush=True)

    total_latency_ms = int((time.perf_counter() - start) * 1000)
    scaffold_ms = None if scaffold_at is None else int((scaffold_at - start) * 1000)
    ttft_ms = None if first_token_at is None else int((first_token_at - start) * 1000)

    final_response = model_text
    if scaffold_text and (not ok or not "".join(chunks).strip()):
        final_response = scaffold_text + "\n\n" + model_text

    packet = {
        "ok": bool(final_response),
        "engine_version": ENGINE_VERSION,
        "role": "TNN",
        "model": model,
        "intent": intent,
        "response": final_response,
        "scaffold_ms": scaffold_ms,
        "time_to_first_token_ms": ttft_ms,
        "latency_ms": total_latency_ms,
        "total_latency_ms": total_latency_ms,
        "error": error,
        "boundary_rewrite": boundary_rewrite,
        "deep": deep,
        "boundary": "recommendation-only; no offensive cyber guidance; no shell execution, mutation, live pulls, scraping, or autonomous authority",
    }
    write_memory(packet)

    print("")
    print("model: Tesseract Neural Network/mistral-chat-brain")
    print(f"backend: {model}")
    if scaffold_ms is not None:
        print(f"scaffold_ms: {scaffold_ms}")
    if ttft_ms is not None:
        print(f"ttft_ms: {ttft_ms}")
    print(f"total_ms: {total_latency_ms}")
    if error:
        print(f"note: {error}")
    print("mode: fast_scaffold_stream_guard_v3" if not deep else "mode: deep_stream_guard_v3")
    return packet


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", required=True)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--timeout", type=float, default=None)
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--no-scaffold", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    timeout = args.timeout
    if timeout is None:
        timeout = float(os.environ.get("TNN_STREAM_TIMEOUT_SECONDS", "8" if not args.deep else "45"))

    packet = stream_generate(
        args.intent,
        model=args.model,
        timeout=timeout,
        scaffold=not args.no_scaffold,
        deep=args.deep,
    )
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
