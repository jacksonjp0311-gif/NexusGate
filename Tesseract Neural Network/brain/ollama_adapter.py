"""Fast local Ollama adapter for TNN Mistral chat brain.

v0.2.0H: no fallback on timeout by default. Fallback doubles latency, so it is
opt-in only through TNN_ALLOW_FALLBACK=1 and intended for missing-model cases.
"""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


OLLAMA_URL = os.environ.get("TNN_OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("TNN_MODEL", "tnn-mistral:latest")
FALLBACK_MODEL = os.environ.get("TNN_FALLBACK_MODEL", "mistral:latest")
DEFAULT_TIMEOUT = float(os.environ.get("TNN_TIMEOUT_SECONDS", "6"))
ALLOW_FALLBACK = os.environ.get("TNN_ALLOW_FALLBACK", "0").strip().lower() in {"1", "true", "yes"}


class OllamaError(RuntimeError):
    pass


def _post_json(url: str, payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise OllamaError(f"Ollama HTTP {error.code}: {body}") from error
    except (TimeoutError, socket.timeout) as error:
        raise OllamaError(f"Ollama timed out after {timeout}s: {error}") from error
    except urllib.error.URLError as error:
        raise OllamaError(f"Ollama unavailable: {error}") from error
    except json.JSONDecodeError as error:
        raise OllamaError(f"Ollama returned invalid JSON: {error}") from error
    except Exception as error:
        raise OllamaError(f"Ollama transport failure: {error}") from error


def _should_fallback(error: Exception) -> bool:
    if not ALLOW_FALLBACK:
        return False
    message = str(error).lower()
    if "timed out" in message or "timeout" in message:
        return False
    if "unavailable" in message or "transport failure" in message:
        return False
    return "not found" in message or "404" in message or "does not exist" in message


def generate(
    prompt: str,
    system: str,
    model: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
    num_predict: int = 80,
) -> Dict[str, Any]:
    chosen = model or DEFAULT_MODEL
    payload = {
        "model": chosen,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.2,
            "top_p": 0.88,
            "num_ctx": 768,
            "num_predict": num_predict,
            "repeat_penalty": 1.08,
        },
    }

    try:
        data = _post_json(f"{OLLAMA_URL}/api/generate", payload, timeout)
        data["model_requested"] = chosen
        data["fallback_used"] = False
        return data
    except OllamaError as first_error:
        if chosen != FALLBACK_MODEL and _should_fallback(first_error):
            fallback_payload = dict(payload)
            fallback_payload["model"] = FALLBACK_MODEL
            data = _post_json(f"{OLLAMA_URL}/api/generate", fallback_payload, timeout)
            data["model_requested"] = FALLBACK_MODEL
            data["fallback_used"] = True
            data["fallback_reason"] = str(first_error)
            return data
        raise
