from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus_gate.intelligence.common import read_json, sha_obj, utc, write_json


def root_path(root: str | Path) -> Path:
    return Path(root).resolve()


def ensure_dirs(root: str | Path) -> dict[str, Path]:
    base = root_path(root)
    paths = {
        "state": base / "state" / "nex_core",
        "messages": base / "state" / "nex_core" / "messages",
        "cycles": base / "state" / "nex_core" / "cycles",
        "teaching": base / "state" / "nex_core" / "teaching",
        "learning": base / "state" / "nex_core" / "learning",
        "reports": base / "reports",
        "ledger": base / "ledger",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def latest_epoch(root: str | Path) -> dict[str, Any]:
    base = root_path(root)
    pointer = read_json(base / "state" / "latest_epoch_pointer.json", {})
    return {
        "source_epoch_id": pointer.get("source_epoch_id") or pointer.get("epoch_id") or "unknown",
        "source_root": pointer.get("source_root") or pointer.get("working_tree_source_root") or "unknown",
        "epoch_state": pointer.get("epoch_state") or pointer.get("state") or "unknown",
        "durable_admissibility": pointer.get("durable_admissibility") or "unknown",
    }


def write_report(root: str | Path, name: str, payload: dict[str, Any]) -> dict[str, Any]:
    paths = ensure_dirs(root)
    write_json(paths["reports"] / name, payload)
    return payload


def content_hash(payload: Any) -> str:
    return sha_obj(payload)


def new_id(prefix: str, payload: Any) -> str:
    return f"{prefix}_{sha_obj({'prefix': prefix, 'payload': payload, 'created_at_utc': utc()})[:24]}"
