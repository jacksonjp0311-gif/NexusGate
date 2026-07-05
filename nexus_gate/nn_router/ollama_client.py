"""Local-only Ollama client for NEXUS NN router v0.6.2.

This module is intentionally narrow:
- It only talks to loopback localhost Ollama.
- It does not execute shell commands.
- It does not read secrets.
- It does not write external APIs.
- It returns text as recommendation context only.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Dict, Optional


LOCAL_OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"


def build_nexus_prompt(intent: str, role: str) -> str:
    return (
        "NEXUS GATE bounded local model router.\n"
        "You are a recommendation-only local reasoning voice.\n"
        "Do not claim authority. Do not execute tools. Do not mutate files.\n"
        "Do not request secrets. Do not write external APIs.\n"
        "Return concise recommendations that a human may accept, reject, or edit.\n\n"
        f"ROLE: {role}\n"
        f"INTENT: {intent}\n\n"
        "Return sections: Observation, Recommendation, Risks, Human Authorization Needed."
    )


def call_local_ollama(
    model: str,
    intent: str,
    role: str,
    timeout_seconds: int = 60,
) -> Dict[str, object]:
    payload = {
        "model": model,
        "prompt": build_nexus_prompt(intent=intent, role=role),
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 4096,
        },
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        LOCAL_OLLAMA_GENERATE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(body)
            return {
                "ok": True,
                "model": model,
                "role": role,
                "endpoint": LOCAL_OLLAMA_GENERATE_URL,
                "response": parsed.get("response", ""),
                "raw_keys": sorted(parsed.keys()),
            }
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "model": model,
            "role": role,
            "endpoint": LOCAL_OLLAMA_GENERATE_URL,
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "model": model,
            "role": role,
            "endpoint": LOCAL_OLLAMA_GENERATE_URL,
            "error": str(exc),
        }