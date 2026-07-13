from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def sha_obj(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default
    except Exception:
        return default


def run_git(root: Path, args: list[str]) -> str:
    try:
        return subprocess.run(["git", *args], cwd=root, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False).stdout.strip()
    except Exception:
        return ""


def git_commit(root: Path) -> str:
    return run_git(root, ["rev-parse", "HEAD"]) or "unknown"


def git_status(root: Path) -> str:
    return run_git(root, ["status", "--short"])


def git_status_hash(root: Path) -> str:
    return sha_text(git_status(root))


def patch_hash(root: Path) -> str:
    return sha_text(run_git(root, ["diff", "--binary"]) + "\n--staged--\n" + run_git(root, ["diff", "--cached", "--binary"]))


def changed_files(root: Path) -> list[str]:
    files: set[str] = set()
    for line in git_status(root).splitlines():
        if len(line) > 3:
            files.add(line[3:].strip().replace("\\", "/"))
    for line in run_git(root, ["diff", "--name-only", "HEAD"]).splitlines():
        if line.strip():
            files.add(line.strip().replace("\\", "/"))
    return sorted(files)


def latest_epoch(root: Path) -> dict[str, Any]:
    pointer = read_json(root / "state" / "latest_epoch_pointer.json", {})
    return {
        "source_epoch_id": pointer.get("source_epoch_id") or pointer.get("epoch_id"),
        "source_root": pointer.get("source_root") or pointer.get("working_tree_source_root"),
    }


def receipt_hash(receipt: dict[str, Any]) -> str:
    body = {k: v for k, v in receipt.items() if k not in {"receipt_hash", "candidate_hash", "model_hash"}}
    return sha_obj(body)
