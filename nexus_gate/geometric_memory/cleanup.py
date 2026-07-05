"""Generated report cleanup for NEXUS geometric memory runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

VERSION = "0.8.3F"

EXACT_GENERATED = [
    "reports/nexus_geometric_memory_packet_latest.json",
    "state/nexus_geometric_memory_runtime_latest.json",
]

REPORT_PATTERNS = [
    "reports/nexus_*_report_20??????_??????.json",
]


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _tracked_paths(root: Path) -> set[str]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def candidate_paths(root: Path) -> List[Path]:
    paths: List[Path] = []
    for rel in EXACT_GENERATED:
        candidate = root / rel
        if candidate.exists() and candidate not in paths:
            paths.append(candidate)
    for pattern in REPORT_PATTERNS:
        for candidate in root.glob(pattern):
            if candidate.is_file() and candidate not in paths:
                paths.append(candidate)
    return sorted(paths, key=lambda item: item.as_posix())


def cleanup_generated(root: Path, dry_run: bool = False) -> Dict[str, Any]:
    root = root.resolve()
    tracked = _tracked_paths(root)
    removed: List[str] = []
    skipped_tracked: List[str] = []
    missing: List[str] = []

    for path in candidate_paths(root):
        rel = _rel(path, root)
        if rel in tracked:
            skipped_tracked.append(rel)
            continue
        if not path.exists():
            missing.append(rel)
            continue
        if not dry_run:
            path.unlink()
        removed.append(rel)

    return {
        "ok": True,
        "version": VERSION,
        "mode": "generated_report_cleanup",
        "dry_run": dry_run,
        "removed": removed,
        "skipped_tracked": skipped_tracked,
        "missing": missing,
        "removed_count": len(removed),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Clean generated NEXUS geometric/runtime report residue.")
    parser.add_argument("--root", default=".", help="Repo root.")
    parser.add_argument("--dry-run", action="store_true", help="Report candidates without deleting.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    args = parser.parse_args(argv)

    report = cleanup_generated(root=Path(args.root), dry_run=bool(args.dry_run))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps({"ok": report["ok"], "version": report["version"], "removed_count": report["removed_count"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

