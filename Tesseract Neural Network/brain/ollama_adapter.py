"""Fast local Ollama adapter for TNN Mistral chat brain."""

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


def generate(
    prompt: str,
    system: str,
    model: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
    num_predict: int = 120,
) -> Dict[str, Any]:
    chosen = model or DEFAULT_MODEL
    payload = {
        "model": chosen,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "keep_alive": "20m",
        "options": {
            "temperature": 0.25,
            "top_p": 0.9,
            "num_ctx": 1024,
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
        if chosen == FALLBACK_MODEL:
            raise
        fallback_payload = dict(payload)
        fallback_payload["model"] = FALLBACK_MODEL
        data = _post_json(f"{OLLAMA_URL}/api/generate", fallback_payload, timeout)
        data["model_requested"] = FALLBACK_MODEL
        data["fallback_used"] = True
        data["fallback_reason"] = str(first_error)
        return data
