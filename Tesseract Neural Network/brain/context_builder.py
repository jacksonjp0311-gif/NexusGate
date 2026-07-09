"""Build turbo compact local context for TNN chat."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List


TNN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TNN_ROOT.parent
INCLUDE_MEMORY = os.environ.get("TNN_INCLUDE_MEMORY", "0").strip().lower() in {"1", "true", "yes"}


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
        "self_contained": bundle.get("self_contained"),
        "neuralforge_required": bundle.get("neuralforge_required"),
        "missing_receipts": bundle.get("missing_receipts", []),
        "blocked_reasons": bundle.get("blocked_reasons", []),
    }


def recent_memory(limit: int = 2) -> List[Dict[str, Any]]:
    if not INCLUDE_MEMORY:
        return []
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
                    "intent": str(item.get("intent", ""))[:120],
                    "response": str(item.get("response", ""))[:180],
                })
        except json.JSONDecodeError:
            continue
    return items


def build_context(intent: str) -> str:
    bundle = compact_bundle()
    blocked = bundle.get("blocked_reasons") or []
    missing = bundle.get("missing_receipts") or []

    lines = [
        "TNN TURBO OPERATOR CHAT",
        f"intent: {intent}",
        "domain: NexusGate repo/product engineering, not cyber offense.",
        f"self_contained: {bundle.get('self_contained')}",
        f"neuralforge_required: {bundle.get('neuralforge_required')}",
        f"blocked: {', '.join(blocked) if blocked else 'none'}",
        f"missing_optional: {', '.join(missing) if missing else 'none'}",
        "boundary: recommendation-only; no shell, no mutation, no live pulls.",
        "forbidden: targets, attack strategy, exploitation, entry points, credential access, evasion, persistence.",
        "answer: max 6 short lines.",
        "line1: direct human answer.",
        "line2: Why: one sentence explaining the reasoning (no hidden chain-of-thought).",
        "then: next safe repo/build move.",
    ]

    memory = recent_memory()
    if memory:
        lines.append("memory: " + json.dumps(memory, separators=(",", ":"))[:500])

    return "\n".join(lines)
