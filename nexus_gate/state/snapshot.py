from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "NEXUS_REPOSITORY_SNAPSHOT.v2.4.0"


def _run_git(root: Path, args: list[str], timeout: int = 10) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _tracked_source_status(root: Path) -> list[str]:
    proc = _run_git(root, ["status", "--short"])
    rows = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip().strip('"').replace("\\", "/")
        if path.startswith(("reports/", "dist/", "ledger/", "state/")):
            continue
        rows.append(line)
    return sorted(rows)


def capture_repository_snapshot(root: str | Path, input_surfaces: list[str] | None = None) -> dict[str, Any]:
    root_path = Path(root).resolve()
    commit_proc = _run_git(root_path, ["rev-parse", "HEAD"])
    branch_proc = _run_git(root_path, ["branch", "--show-current"])
    source_rows = _tracked_source_status(root_path)
    surfaces: list[dict[str, Any]] = []
    for rel in input_surfaces or []:
        if rel.startswith("git "):
            continue
        path = root_path / rel
        if path.exists() and path.is_file():
            try:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
            except Exception:
                digest = None
            surfaces.append({"path": rel, "exists": True, "sha256": digest})
        else:
            surfaces.append({"path": rel, "exists": False, "sha256": None})
    payload = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_commit": commit_proc.stdout.strip() if commit_proc.returncode == 0 else None,
        "branch": branch_proc.stdout.strip() if branch_proc.returncode == 0 else None,
        "source_status_hash": _hash_text("\n".join(source_rows)),
        "source_status_count": len(source_rows),
        "input_surfaces": surfaces,
    }
    payload["input_snapshot_hash"] = _hash_text(json.dumps(payload["input_surfaces"], sort_keys=True))
    payload["epoch_id"] = _hash_text(json.dumps({
        "commit": payload["repository_commit"],
        "source_status_hash": payload["source_status_hash"],
        "input_snapshot_hash": payload["input_snapshot_hash"],
    }, sort_keys=True))[:24]
    return payload


def packet_is_fresh(packet: dict[str, Any], snapshot: dict[str, Any]) -> bool:
    packet_snapshot = packet.get("repository_snapshot") or {}
    if not packet_snapshot:
        return False
    return (
        packet_snapshot.get("repository_commit") == snapshot.get("repository_commit")
        and packet_snapshot.get("source_status_hash") == snapshot.get("source_status_hash")
        and packet_snapshot.get("input_snapshot_hash") == snapshot.get("input_snapshot_hash")
    )
