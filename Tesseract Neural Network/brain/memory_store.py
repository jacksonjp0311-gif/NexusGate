"""Small append-only memory store for TNN chat."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict


TNN_ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATH = TNN_ROOT / "memory" / "tnn_memory.jsonl"
LATEST_PATH = TNN_ROOT / "memory" / "conversation_latest.json"


def write_memory(record: Dict[str, Any]) -> None:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    item = dict(record)
    item.setdefault("created_at_unix", time.time())
    with MEMORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, sort_keys=True) + "\n")
    LATEST_PATH.write_text(json.dumps(item, indent=2, sort_keys=True) + "\n", encoding="utf-8")
