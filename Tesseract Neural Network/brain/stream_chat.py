"""Streaming TNN chat lane for NexusGate.

v0.2.0W â€” Operator Compactness Guard:
- Phi-4-mini hot lane is fast and now compacted
- hot model text is buffered, normalized, capped, and de-dangled before print
- Mistral deep lane remains longer-form
"""

from __future__ import annotations

import argparse
import json
import os
import re
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
MODEL = os.environ.get("TNN_MODEL", "tnn-phi4-mini:latest")
TNN_ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PROMPT_PATH = TNN_ROOT / "brain" / "system_prompt.md"

ENGINE_VERSION = "tnn.stream_chat.v0.2.0W"
MIN_MEANINGFUL_PARTIAL_CHARS = 36
HOT_MAX_LINES = 5
HOT_MAX_CHARS = 520

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


def model_label(model: str) -> str:
    low = model.lower()
    if "phi4" in low or "phi-4" in low:
        return "Tesseract Neural Network/phi4-mini-hot-brain"
    if "mistral" in low:
        return "Tesseract Neural Network/mistral-deep-brain"
    return "Tesseract Neural Network/local-operator-brain"


def is_hot_model(model: str) -> bool:
    low = model.lower()
    return "phi4" in low or "phi-4" in low


def stream_heading(model: str) -> str:
    if is_hot_model(model):
        return "TNN // HOT MODEL STREAM"
    if "mistral" in model.lower():
        return "TNN // DEEP MODEL STREAM"
    return "TNN // MODEL STREAM"


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


def model_budget_hit_message(partial_chars: int, started: bool, model: str) -> str:
    label = "hot model" if is_hot_model(model) else "model"
    if started:
        return (
            "TNN // MODEL BUDGET HIT\n"
            f"The {label} started but did not complete a useful phrase inside fast budget.\n"
            "next: use the scaffold now, or rerun --deep for full Mistral.\n"
            f"partial_chars: {partial_chars}\n"
            "boundary: recommendation-only."
        )
    return (
        "TNN // MODEL BUDGET HIT\n"
        f"The {label} did not start streaming inside fast budget.\n"
        "next: use the scaffold now, or run tnn-warm/tnn-doctor then retry.\n"
        "boundary: recommendation-only."
    )


def meaningful_partial(text: str) -> bool:
    stripped = " ".join(text.split())
    if len(stripped) < MIN_MEANINGFUL_PARTIAL_CHARS:
        return False
    if any(stripped.endswith(mark) for mark in [".", "!", "?"]):
        return True
    return len(stripped.split()) >= 8


def normalize_hot_response(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(Sure[,!\s]+|Okay[,!\s]+|Here('?s| is)\s+)", "", text, flags=re.I).strip()
    if not text:
        return "next: wire the TNN hot lane into Electron and show the model-health badge."

    parts = re.split(r"(?<=[.!?])\s+", text)
    clean_parts: List[str] = []
    for part in parts:
        item = part.strip(" -\t\r\n")
        if not item:
            continue
        if len(item.split()) < 3 and not item.endswith((".", "!", "?")):
            continue
        clean_parts.append(item)
        if len(clean_parts) >= HOT_MAX_LINES:
            break

    if not clean_parts:
        clean_parts = [text]

    joined = "\n".join(clean_parts)
    if len(joined) > HOT_MAX_CHARS:
        cut = joined[:HOT_MAX_CHARS].rsplit(" ", 1)[0].strip()
        if cut and not cut.endswith((".", "!", "?")):
            cut += "."
        joined = cut

    lines = [line.strip() for line in joined.splitlines() if line.strip()]
    if lines:
        last = lines[-1]
        last_words = last.split()
        dangling_starts = {"using", "with", "by", "for", "to", "and", "or", "in", "on", "via", "through"}
        if (not last.endswith((".", "!", "?"))) and (len(last_words) < 7 or last_words[-1].lower() in dangling_starts):
            lines = lines[:-1]
    if not lines:
        return "next: wire the TNN hot lane into Electron and show the model-health badge."
    return "\n".join(lines[:HOT_MAX_LINES])


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
    hot = is_hot_model(model) and not deep

    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": True,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.10 if hot else 0.12,
            "top_p": 0.75 if hot else 0.8,
            "num_ctx": 512,
            "num_predict": 40 if hot else 120,
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
    model_budget_hit = False
    stream_completed = False
    scaffold_text = ""

    print("")
    print("TNN CHAT")
    print("--------", flush=True)

    if scaffold:
        scaffold_text = fast_scaffold(intent)
        scaffold_at = time.perf_counter()
        print(scaffold_text, flush=True)
        print("", flush=True)
        print(stream_heading(model), flush=True)

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

                joined = "".join(chunks)
                if violates_operator_boundary(joined):
                    boundary_rewrite = True
                    break

                if item.get("done"):
                    stream_completed = True
                    break
    except (TimeoutError, socket.timeout) as exc:
        ok = False
        error = f"Ollama timed out after {timeout}s: {exc}"
        model_budget_hit = True
    except urllib.error.URLError as exc:
        ok = False
        error = f"Ollama unavailable: {exc}"
        model_budget_hit = True
    except Exception as exc:
        ok = False
        error = f"Ollama stream failure: {exc}"
        model_budget_hit = True

    raw_model_text = "".join(chunks).strip()
    partial_chars = len(raw_model_text)

    if boundary_rewrite:
        ok = True
        error = "operator boundary rewrite applied"
        model_text = safe_fallback(intent)
    elif model_budget_hit:
        if raw_model_text and meaningful_partial(raw_model_text):
            model_text = "TNN // MODEL PARTIAL\n" + (normalize_hot_response(raw_model_text) if hot else raw_model_text)
        else:
            model_text = model_budget_hit_message(partial_chars=partial_chars, started=bool(raw_model_text), model=model)
    elif raw_model_text:
        model_text = normalize_hot_response(raw_model_text) if hot else raw_model_text
    else:
        model_budget_hit = True
        model_text = model_budget_hit_message(partial_chars=0, started=False, model=model)

    print(model_text, flush=True)

    total_latency_ms = int((time.perf_counter() - start) * 1000)
    scaffold_ms = None if scaffold_at is None else int((scaffold_at - start) * 1000)
    ttft_ms = None if first_token_at is None else int((first_token_at - start) * 1000)

    final_response = model_text
    if scaffold_text and (model_budget_hit or not stream_completed):
        final_response = scaffold_text + "\n\n" + model_text

    packet = {
        "ok": bool(final_response),
        "engine_version": ENGINE_VERSION,
        "role": "TNN",
        "model": model,
        "model_label": model_label(model),
        "intent": intent,
        "response": final_response,
        "model_response": model_text,
        "raw_partial_response": raw_model_text,
        "partial_chars": partial_chars,
        "model_budget_hit": model_budget_hit,
        "stream_completed": stream_completed,
        "scaffold_ms": scaffold_ms,
        "time_to_first_token_ms": ttft_ms,
        "latency_ms": total_latency_ms,
        "total_latency_ms": total_latency_ms,
        "error": error,
        "boundary_rewrite": boundary_rewrite,
        "deep": deep,
        "hot_compacted": hot,
        "boundary": "recommendation-only; no offensive cyber guidance; no shell execution, mutation, live pulls, scraping, or autonomous authority",
    }
    write_memory(packet)

    print("")
    print(f"model: {model_label(model)}")
    print(f"backend: {model}")
    if scaffold_ms is not None:
        print(f"scaffold_ms: {scaffold_ms}")
    if ttft_ms is not None:
        print(f"ttft_ms: {ttft_ms}")
    print(f"total_ms: {total_latency_ms}")
    if model_budget_hit:
        print("model_budget_hit: true")
    if error:
        print(f"note: {error}")
    print("mode: hot_compact_guard_v6" if hot else "mode: deep_stream_guard_v6")
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
