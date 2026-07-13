from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REGISTRY_PATH = Path("registry") / "nexus_telemetry_sources.v2.8.0.json"


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def load_registry(root: str | Path = ".") -> dict[str, Any]:
    path = Path(root) / REGISTRY_PATH
    if not path.exists():
        return {"schema": "NEXUS_TELEMETRY_SOURCES.v2.8.0", "sources": []}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def source_hash(source: dict[str, Any]) -> str:
    return stable_hash({k: v for k, v in source.items() if k != "registry_entry_hash"})


def indexed_sources(root: str | Path = ".") -> dict[str, dict[str, Any]]:
    registry = load_registry(root)
    return {item["source_id"]: item for item in registry.get("sources", [])}
