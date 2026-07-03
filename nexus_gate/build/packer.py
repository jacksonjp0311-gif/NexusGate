from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
import tarfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "dist",
}

INCLUDE_PATTERNS = [
    "*.py",
    "*.ps1",
    "*.sh",
    "*.md",
    "*.json",
    "*.toml",
    "*.yml",
    "*.yaml",
    ".gitattributes",
    ".gitignore",
]

CRITICAL_GOAL_LANES = [
    "adapter",
    "schema",
    "codec",
    "authority",
    "hot_route",
    "cold_evidence",
    "wound_route",
    "replay",
    "disengagement",
    "ledger",
    "compiler",
]


@dataclass(frozen=True)
class FileEntry:
    path: str
    size_bytes: int
    line_count: int
    sha256: str


@dataclass(frozen=True)
class PackReport:
    system: str
    version: str
    generated_at_utc: str
    root: str
    status: str
    file_count: int
    total_bytes: int
    total_lines: int
    bundle_path: str
    manifest_path: str
    largest_files: list[FileEntry]
    commands: list[dict]
    goal_lanes: list[str]
    claim_boundary: str = "Pack report is local engineering evidence only. Not production validation."


def display_path(path: Path, root: Path) -> str:
    """Return repo-relative path when possible, absolute path otherwise.

    This lets tests pack into a temporary directory outside the repo while normal
    runtime packing still reports dist-relative paths.
    """

    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def should_include(path: Path) -> bool:
    return any(fnmatch.fnmatch(path.name, pattern) for pattern in INCLUDE_PATTERNS)


def iter_source_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.relative_to(root).parts)
        if parts & EXCLUDE_DIRS:
            continue
        if should_include(path):
            yield path


def file_entry(root: Path, path: Path) -> FileEntry:
    data = path.read_bytes()
    text = data.decode("utf-8", errors="ignore")
    return FileEntry(
        path=str(path.relative_to(root)).replace("\\", "/"),
        size_bytes=len(data),
        line_count=text.count("\n") + (1 if text else 0),
        sha256=sha256_bytes(data),
    )


def run_command(root: Path, cmd: list[str]) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }


def build_bundle(root: Path, output_dir: Path, run_checks: bool = True) -> PackReport:
    root = root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    commands: list[dict] = []
    status = "pass"

    if run_checks:
        checks = [
            [sys.executable, "-m", "compileall", "nexus_gate", "tests"],
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            [sys.executable, "-m", "nexus_gate.compiler", "--root", ".", "--json"],
        ]
        for cmd in checks:
            result = run_command(root, cmd)
            commands.append(result)
            if result["returncode"] != 0:
                status = "fail"

    entries = [file_entry(root, path) for path in iter_source_files(root)]
    entries_sorted = sorted(entries, key=lambda item: item.path)
    largest = sorted(entries, key=lambda item: item.size_bytes, reverse=True)[:15]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    bundle_path = output_dir / f"nexus_gate_source_bundle_{stamp}.tar.gz"
    latest_bundle = output_dir / "nexus_gate_source_bundle_latest.tar.gz"
    manifest_path = output_dir / f"nexus_gate_pack_manifest_{stamp}.json"
    latest_manifest = output_dir / "nexus_gate_pack_manifest_latest.json"

    with tarfile.open(bundle_path, "w:gz") as tar:
        for entry in entries_sorted:
            tar.add(root / entry.path, arcname=entry.path)

    latest_bundle.write_bytes(bundle_path.read_bytes())

    report = PackReport(
        system="NEXUS GATE",
        version="0.1.6b-pack-compiler",
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        root=str(root),
        status=status,
        file_count=len(entries_sorted),
        total_bytes=sum(item.size_bytes for item in entries_sorted),
        total_lines=sum(item.line_count for item in entries_sorted),
        bundle_path=display_path(bundle_path, root),
        manifest_path=display_path(manifest_path, root),
        largest_files=largest,
        commands=commands,
        goal_lanes=CRITICAL_GOAL_LANES,
    )

    encoded = json.dumps(asdict(report), indent=2)
    manifest_path.write_text(encoded, encoding="utf-8")
    latest_manifest.write_text(encoded, encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="NEXUS GATE pack/compiler")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out", default="dist", help="Output directory")
    parser.add_argument("--no-checks", action="store_true", help="Only pack; do not run compile/tests/compiler")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = build_bundle(root=root, output_dir=root / args.out, run_checks=not args.no_checks)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE pack status: {report.status}")
        print(f"Bundle: {report.bundle_path}")
        print(f"Manifest: {report.manifest_path}")

    if report.status != "pass":
        sys.exit(1)


if __name__ == "__main__":
    main()
