"""NEXUS GATE evidence compaction compiler.

This creates a compaction manifest and pressure report. It does not delete
evidence by default. It gives the operator a bounded view before further growth.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, List


CLAIM_BOUNDARY = (
    "Evidence compaction report is local operator evidence only. "
    "It does not prove correctness, safety, security, or production readiness."
)


@dataclass
class EvidenceFile:
    path: str
    size_bytes: int
    sha256: str


@dataclass
class EvidenceCompactionReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    file_count: int
    total_bytes: int
    retained_latest: List[Dict[str, Any]]
    candidate_count: int
    pressure_level: str
    recommended_action: str
    archive_path: str | None = None
    claim_boundary: str = CLAIM_BOUNDARY


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _scan(root: Path) -> List[EvidenceFile]:
    files: List[EvidenceFile] = []
    for folder in ("reports", "dist", "ledger"):
        base = root / folder
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file():
                try:
                    files.append(EvidenceFile(
                        path=str(path.relative_to(root)),
                        size_bytes=path.stat().st_size,
                        sha256=_sha256(path),
                    ))
                except OSError:
                    pass
    return sorted(files, key=lambda item: item.path)


def _latest_by_prefix(files: List[EvidenceFile]) -> List[Dict[str, Any]]:
    latest: Dict[str, EvidenceFile] = {}
    prefixes = [
        "reports/nexus_compile_report",
        "reports/nexus_adapter_compile_report",
        "reports/nexus_receptor_compile_report",
        "reports/nexus_bridge_compile_report",
        "reports/nexus_runtime_compile_report",
        "reports/nexus_bounded_runtime_report",
        "reports/nexus_feedback_report",
        "reports/nexus_interconnect_report",
        "reports/nexus_evidence_compaction_report",
        "dist/nexus_gate_pack_manifest",
    ]
    for prefix in prefixes:
        candidates = [f for f in files if f.path.startswith(prefix)]
        if candidates:
            latest[prefix] = sorted(candidates, key=lambda f: f.path)[-1]
    return [asdict(v) for v in latest.values()]


def compile_evidence_compaction(root: str | Path = ".", archive: bool = False) -> EvidenceCompactionReport:
    root = Path(root).resolve()
    files = _scan(root)
    total_bytes = sum(f.size_bytes for f in files)
    retained = _latest_by_prefix(files)
    candidate_count = max(0, len(files) - len(retained))

    if len(files) >= 250 or total_bytes >= 1_000_000:
        pressure = "high"
    elif len(files) >= 150 or total_bytes >= 350_000:
        pressure = "medium"
    else:
        pressure = "low"

    archive_path = None
    recommended = "No archive needed yet. Keep latest reports and continue."
    if pressure in {"medium", "high"}:
        recommended = "Archive older timestamped reports before adding new adapter families."

    if archive and candidate_count > 0:
        archive_dir = root / "reports" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_file = archive_dir / f"nexus_evidence_archive_{stamp}.json.gz"
        payload = {"files": [asdict(f) for f in files], "retained_latest": retained}
        with gzip.open(archive_file, "wt", encoding="utf-8") as gz:
            json.dump(payload, gz, indent=2)
        archive_path = str(archive_file.relative_to(root))
        recommended = "Archive manifest written. No source evidence was deleted."

    status = "pass"
    return EvidenceCompactionReport(
        system="NEXUS GATE",
        version="0.2.2-evidence-compaction",
        root=str(root),
        status=status,
        generated_at_utc=_utc(),
        file_count=len(files),
        total_bytes=total_bytes,
        retained_latest=retained,
        candidate_count=candidate_count,
        pressure_level=pressure,
        recommended_action=recommended,
        archive_path=archive_path,
    )


def write_compaction_report(report: EvidenceCompactionReport, root: str | Path = ".") -> Path:
    root = Path(root).resolve()
    out = root / "reports"
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    data = asdict(report)
    path = out / f"nexus_evidence_compaction_report_{stamp}.json"
    latest = out / "nexus_evidence_compaction_report_latest.json"
    text = json.dumps(data, indent=2)
    path.write_text(text, encoding="utf-8")
    latest.write_text(text, encoding="utf-8")
    return latest


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexus-compact", description="Compile NEXUS GATE evidence compaction report")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--archive", action="store_true", help="Write gzip archive manifest; does not delete evidence")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    args = parser.parse_args()

    report = compile_evidence_compaction(args.root, archive=args.archive)
    write_compaction_report(report, args.root)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE evidence compaction status: {report.status}")
        print(f"pressure: {report.pressure_level}")
        print(f"files: {report.file_count}")
        print(f"bytes: {report.total_bytes}")

    if report.status != "pass":
        sys.exit(1)


if __name__ == "__main__":
    main()
