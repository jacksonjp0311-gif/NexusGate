"""Build compact local context for TNN chat."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


TNN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TNN_ROOT.parent


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def compact_bundle() -> Dict[str, Any]:
    bundle = read_json(TNN_ROOT / "receipts" / "receipt_bundle_latest.json")
    return {
        "source": bundle.get("source"),
        "self_contained": bundle.get("self_contained"),
        "neuralforge_required": bundle.get("neuralforge_required"),
        "missing_receipts": bundle.get("missing_receipts", []),
        "blocked_reasons": bundle.get("blocked_reasons", []),
        "tnn_version": bundle.get("tnn_version"),
    }


def recent_memory(limit: int = 5) -> List[Dict[str, Any]]:
    path = TNN_ROOT / "memory" / "tnn_memory.jsonl"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8-sig").splitlines()[-limit:]
    items: List[Dict[str, Any]] = []
    for line in lines:
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                items.append({
                    "intent": item.get("intent", "")[:240],
                    "response": item.get("response", "")[:400],
                    "model": item.get("model"),
                })
        except json.JSONDecodeError:
            continue
    return items


def build_context(intent: str) -> str:
    bundle = compact_bundle()
    memory = recent_memory()
    parts = [
        "LOCAL TNN STATE:",
        json.dumps(bundle, indent=2, sort_keys=True),
    ]
    if memory:
        parts.extend([
            "",
            "RECENT TNN MEMORY:",
            json.dumps(memory, indent=2, sort_keys=True),
        ])
    parts.extend([
        "",
        "CURRENT INTENT:",
        intent,
        "",
        "RESPONSE RULES:",
        "- Be fast and concrete.",
        "- Answer like NexusGate operator intelligence.",
        "- Give the next safe move.",
        "- Stay within recommendation-only boundary.",
    ])
    return "\n".join(parts)
