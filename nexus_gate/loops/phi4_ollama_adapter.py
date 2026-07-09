from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

VERSION = "1.0.1"
SCHEMA = "NEXUS_PHI4_OLLAMA_ADAPTER.v1.0.1"
DEFAULT_MODEL = "phi4-mini"
DEFAULT_URL = "http://localhost:11434/api/generate"
REQUIRED_KEYS = ["diagnosis", "repair_surface", "repair_type", "patch_intent", "rerun_gate", "confidence", "requires_human_authorization"]


def _read_prompt(prompt: str = "", prompt_file: str = "") -> str:
    if prompt_file:
        return Path(prompt_file).read_text(encoding="utf-8-sig")
    if prompt:
        return prompt
    data = sys.stdin.read()
    return data or ""


def _extract_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    first = text.find("{")
    last = text.rfind("}")
    if first < 0 or last <= first:
        return None
    try:
        data = json.loads(text[first:last + 1])
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _fallback_advice(raw: str) -> dict[str, Any]:
    preview = (raw or "").strip()[-900:]
    return {
        "diagnosis": preview or "Phi returned no parseable JSON. Treat this as an adapter formatting wound, not repair authority.",
        "repair_surface": "model_output_format_or_prompt_contract",
        "repair_type": "advisor_format_repair",
        "patch_intent": "Tighten the prompt or adapter until Phi returns the required compact JSON keys.",
        "rerun_gate": ".\\scripts\\nexus.ps1 phi-wound-gpu -Tag \"adapter live test\"",
        "confidence": 0.25,
        "requires_human_authorization": True,
    }


def _normalize_advice(data: dict[str, Any], raw: str = "") -> dict[str, Any]:
    if not isinstance(data, dict):
        data = {}
    if any(key not in data for key in REQUIRED_KEYS):
        fallback = _fallback_advice(raw)
        merged = {**fallback, **{k: v for k, v in data.items() if k in REQUIRED_KEYS}}
        data = merged
    try:
        data["confidence"] = float(data.get("confidence", 0.25))
    except Exception:
        data["confidence"] = 0.25
    data["requires_human_authorization"] = bool(data.get("requires_human_authorization", True))
    return {key: data[key] for key in REQUIRED_KEYS}


def _build_system() -> str:
    return (
        "You are Phi-4 Mini running locally as a NexusGate wound advisor. "
        "Return ONLY one compact JSON object with these exact keys: "
        + ", ".join(REQUIRED_KEYS)
        + ". You cannot run shell commands, change files, stage git, commit, push, access secrets, or self-authorize. "
        "Diagnose the wound, name the smallest repair surface, propose the next deterministic gate."
    )


def call_ollama(prompt: str, model: str, url: str, timeout: int) -> tuple[int, dict[str, Any]]:
    body = {
        "model": model,
        "system": _build_system(),
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 500},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        raw = str(payload.get("response", ""))
        parsed = _extract_json(raw)
        advice = _normalize_advice(parsed or {}, raw)
        return 0, advice
    except urllib.error.URLError as exc:
        err = {
            "diagnosis": f"Ollama adapter could not reach {url}: {exc}.",
            "repair_surface": "local_ollama_service",
            "repair_type": "start_or_install_model",
            "patch_intent": "Start Ollama and ensure phi4-mini is installed: ollama serve; ollama pull phi4-mini.",
            "rerun_gate": ".\\scripts\\nexus.ps1 phi-wound-gpu -Tag \"adapter live test\"",
            "confidence": 0.9,
            "requires_human_authorization": True,
        }
        return 2, err
    except Exception as exc:
        err = {
            "diagnosis": f"Ollama adapter error: {exc}.",
            "repair_surface": "nexus_gate/loops/phi4_ollama_adapter.py",
            "repair_type": "adapter_runtime_error",
            "patch_intent": "Inspect adapter response parsing and Ollama payload shape.",
            "rerun_gate": ".\\scripts\\nexus.ps1 phi-wound-gpu -Tag \"adapter live test\"",
            "confidence": 0.5,
            "requires_human_authorization": True,
        }
        return 2, err


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="")
    parser.add_argument("--prompt-file", default="")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--info", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.info:
        print(json.dumps({
            "schema": SCHEMA,
            "version": VERSION,
            "model": args.model,
            "url": args.url,
            "mode": "non_interactive_ollama_adapter",
            "stdout_contract": "single_json_object_only",
            "requires_network": False,
            "local_http_only": True,
        }, indent=2, sort_keys=True))
        return 0

    if args.self_test:
        print(json.dumps(_normalize_advice({"diagnosis": "self-test"}), indent=2, sort_keys=True))
        return 0

    prompt = _read_prompt(args.prompt, args.prompt_file)
    code, advice = call_ollama(prompt, args.model, args.url, args.timeout)
    print(json.dumps(advice, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
