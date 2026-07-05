"""Local-only Ollama client for NEXUS NN router.

This module is intentionally narrow:
- It only talks to loopback localhost Ollama.
- It does not execute shell commands.
- It does not read secrets.
- It does not write external APIs.
- It returns text as recommendation context only.

v0.7.1 adds a CPU-bounded inference profile so local Phi-3/Mistral calls do not
overrun the operator machine under high RAM/CPU pressure.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Dict


LOCAL_OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"


ROLE_LIMITS = {
    "FAST": {"num_ctx": 1024, "num_predict": 96, "timeout": 150},
    "BALANCED": {"num_ctx": 1536, "num_predict": 140, "timeout": 180},
    "DEEP": {"num_ctx": 2048, "num_predict": 180, "timeout": 240},
    "HANDOFF": {"num_ctx": 1024, "num_predict": 64, "timeout": 90},
}


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        return default


def _role_limits(role: str) -> Dict[str, int]:
    return ROLE_LIMITS.get(str(role or "FAST").upper(), ROLE_LIMITS["FAST"]).copy()


def build_nexus_prompt(intent: str, role: str) -> str:
    cleaned_intent = " ".join(str(intent or "").split())
    return (
        "NEXUS GATE local reasoning node.\n"
        "Rules: recommendation-only; no tool execution; no file mutation; no secrets; no authority claims.\n"
        "Keep the answer short because this is CPU-local inference.\n"
        "Use exactly four compact sections: Observation, Recommendation, Risk, Human Authorization.\n\n"
        f"ROLE: {role}\n"
        f"INTENT: {cleaned_intent}\n"
    )


def call_local_ollama(
    model: str,
    intent: str,
    role: str,
    timeout_seconds: int = 60,
) -> Dict[str, object]:
    limits = _role_limits(role)
    timeout = _env_int("NEXUS_OLLAMA_TIMEOUT_SECONDS", limits["timeout"])
    if timeout_seconds and timeout_seconds > timeout:
        timeout = timeout_seconds

    options = {
        "temperature": 0.1,
        "num_ctx": _env_int("NEXUS_OLLAMA_NUM_CTX", limits["num_ctx"]),
        "num_predict": _env_int("NEXUS_OLLAMA_NUM_PREDICT", limits["num_predict"]),
        "num_gpu": _env_int("NEXUS_OLLAMA_NUM_GPU", 0),
    }

    num_thread = _env_int("NEXUS_OLLAMA_NUM_THREAD", 0)
    if num_thread > 0:
        options["num_thread"] = num_thread

    payload = {
        "model": model,
        "prompt": build_nexus_prompt(intent=intent, role=role),
        "stream": False,
        "keep_alive": os.environ.get("NEXUS_OLLAMA_KEEP_ALIVE", "10m"),
        "options": options,
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        LOCAL_OLLAMA_GENERATE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(body)
            return {
                "ok": True,
                "model": model,
                "role": role,
                "endpoint": LOCAL_OLLAMA_GENERATE_URL,
                "response": parsed.get("response", ""),
                "raw_keys": sorted(parsed.keys()),
                "runtime_options": {
                    "timeout_seconds": timeout,
                    "num_ctx": options.get("num_ctx"),
                    "num_predict": options.get("num_predict"),
                    "num_gpu": options.get("num_gpu"),
                    "num_thread": options.get("num_thread"),
                    "keep_alive": payload.get("keep_alive"),
                },
            }
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "model": model,
            "role": role,
            "endpoint": LOCAL_OLLAMA_GENERATE_URL,
            "error": str(exc),
            "runtime_options": {
                "timeout_seconds": timeout,
                "num_ctx": options.get("num_ctx"),
                "num_predict": options.get("num_predict"),
                "num_gpu": options.get("num_gpu"),
                "num_thread": options.get("num_thread"),
                "keep_alive": payload.get("keep_alive"),
            },
        }
    except Exception as exc:
        return {
            "ok": False,
            "model": model,
            "role": role,
            "endpoint": LOCAL_OLLAMA_GENERATE_URL,
            "error": str(exc),
            "runtime_options": {
                "timeout_seconds": timeout,
                "num_ctx": options.get("num_ctx"),
                "num_predict": options.get("num_predict"),
                "num_gpu": options.get("num_gpu"),
                "num_thread": options.get("num_thread"),
                "keep_alive": payload.get("keep_alive"),
            },
        }
