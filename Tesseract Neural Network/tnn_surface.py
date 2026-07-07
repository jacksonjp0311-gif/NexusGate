"""Self-contained Tesseract Neural Network surface for NexusGate.

TNN v0.2.0 is a local neural chat brain backed by Mistral/Ollama.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

TNN_VERSION = "nexus.tesseract_neural_network.v0.2.0L"
TNN_MODEL_NAME = "Tesseract Neural Network/mistral-chat-brain"

TNN_ROOT = Path(__file__).resolve().parent
RECEIPTS_DIR = TNN_ROOT / "receipts"
STATE_DIR = TNN_ROOT / "state"
LOCAL_BUNDLE_PATH = RECEIPTS_DIR / "receipt_bundle_latest.json"
LOCAL_STATE_PATH = STATE_DIR / "tnn_state_latest.json"


def _load_module(name: str, path: Path):
    module_dir = str(path.parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError) as error:
        return {"parse_error": str(error), "path": str(path)}


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_local_bundle() -> Dict[str, Any]:
    bundle = read_json(LOCAL_BUNDLE_PATH)
    if bundle is None:
        bundle = {
            "ok": True,
            "source": "nexusgate_local_seed",
            "self_contained": True,
            "neuralforge_required": False,
            "receipts": {},
            "missing_receipts": [],
            "blocked_reasons": [],
            "tnn_version": TNN_VERSION,
        }
        write_json(LOCAL_BUNDLE_PATH, bundle)
    bundle.setdefault("ok", True)
    bundle.setdefault("self_contained", True)
    bundle.setdefault("neuralforge_required", False)
    bundle.setdefault("receipts", {})
    bundle.setdefault("missing_receipts", [])
    bundle.setdefault("blocked_reasons", [])
    return bundle


def build_model_response(intent: str) -> Dict[str, Any]:
    bundle = load_local_bundle()
    chat_engine = _load_module("tnn_chat_engine", TNN_ROOT / "brain" / "chat_engine.py")
    chat = chat_engine.chat(intent)
    response = {
        "role": "TNN",
        "model": TNN_MODEL_NAME,
        "backend_model": chat.get("model"),
        "ok": bool(chat.get("ok")),
        "response": chat.get("response", ""),
        "chat_response": chat.get("response", ""),
        "chat_packet": chat,
        "tnn_version": TNN_VERSION,
        "self_contained": True,
        "neuralforge_required": False,
        "receipt_bundle": bundle,
    }
    write_json(LOCAL_STATE_PATH, {
        "ok": response["ok"],
        "role": response["role"],
        "model": response["model"],
        "backend_model": response["backend_model"],
        "tnn_version": TNN_VERSION,
        "self_contained": True,
        "neuralforge_required": False,
        "last_intent": intent,
        "last_latency_ms": chat.get("latency_ms"),
        "local_bundle": str(LOCAL_BUNDLE_PATH),
    })
    return response


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", default="Read Tesseract Neural Network state.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    response = build_model_response(args.intent)
    print(json.dumps(response, indent=2, sort_keys=True) if args.json else response["response"])


if __name__ == "__main__":
    main()



