from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


REGISTRY_FILENAMES = [
    Path("loops") / "nexus_loop_registry.v0.1.json",
    Path("state") / "loops" / "nexus_loop_registry.v0.1.json",
]


class LoopRegistryError(ValueError):
    pass


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_registry(root: str | Path) -> Dict[str, Any]:
    root_path = Path(root).resolve()
    last_error = None
    for rel in REGISTRY_FILENAMES:
        path = root_path / rel
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8-sig"))
            except Exception as exc:  # pragma: no cover - error text is diagnostic
                last_error = exc
                continue
            validate_registry(data)
            data["_registry_path"] = str(path.relative_to(root_path))
            data["_registry_hash"] = _sha256_text(json.dumps(data, sort_keys=True, default=str))
            return data
    if last_error is not None:
        raise LoopRegistryError(f"Loop registry exists but failed to parse: {last_error}")
    raise LoopRegistryError("No loop registry found in loops/ or state/loops/.")


def validate_registry(data: Dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise LoopRegistryError("Registry must be a JSON object.")
    if "loops" not in data or not isinstance(data["loops"], dict):
        raise LoopRegistryError("Registry missing loops object.")
    if "allowed_commands" not in data or not isinstance(data["allowed_commands"], dict):
        raise LoopRegistryError("Registry missing allowed_commands object.")
    for name, loop in data["loops"].items():
        if not isinstance(loop, dict):
            raise LoopRegistryError(f"Loop {name!r} must be an object.")
        stages = loop.get("stages")
        if not isinstance(stages, list) or not stages:
            raise LoopRegistryError(f"Loop {name!r} must define non-empty stages.")
        for stage in stages:
            if not isinstance(stage, dict):
                raise LoopRegistryError(f"Loop {name!r} contains a non-object stage.")
            if "name" not in stage or "type" not in stage:
                raise LoopRegistryError(f"Loop {name!r} contains a stage missing name/type.")


def list_loops(root: str | Path) -> List[str]:
    data = load_registry(root)
    return sorted(data["loops"].keys())


def get_loop(root: str | Path, loop_name: str) -> Dict[str, Any]:
    data = load_registry(root)
    loops = data["loops"]
    if loop_name not in loops:
        raise LoopRegistryError(f"Unknown loop {loop_name!r}. Known loops: {', '.join(sorted(loops))}")
    loop = dict(loops[loop_name])
    loop["_name"] = loop_name
    loop["_registry_path"] = data.get("_registry_path")
    loop["_registry_hash"] = data.get("_registry_hash")
    loop["_allowed_commands"] = data.get("allowed_commands", {})
    loop["_authority_boundary"] = data.get("authority_boundary", {})
    loop["_claim_boundary"] = data.get("claim_boundary", "")
    return loop


def file_digest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False, "sha256": None, "bytes": 0, "line_count": 0}
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    return {
        "exists": True,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "line_count": len(text.splitlines()),
    }