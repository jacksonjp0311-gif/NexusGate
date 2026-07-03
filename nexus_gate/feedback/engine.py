"""NEXUS GATE feedback engine.

This module reads local compiler/runtime/evidence reports and emits a compact
feedback report for the CLI. It is intentionally local-only and non-mutating.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import hashlib
from typing import Any, Dict, List, Optional


CLAIM_BOUNDARY = (
    "Feedback report is local development evidence only. "
    "It is not a production validation, safety proof, security proof, or correctness proof."
)


@dataclass
class FeedbackSignal:
    name: str
    status: str
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeedbackReport:
    system: str
    version: str
    root: str
    status: str
    generated_at_utc: str
    signals: List[Dict[str, Any]]
    health_score: float
    next_actions: List[str]
    evidence_pressure: Dict[str, Any]
    interconnect: Dict[str, Any]
    claim_boundary: str = CLAIM_BOUNDARY


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive report path
        return {"status": "unreadable", "error": str(exc), "path": str(path)}


def _status_of(data: Optional[Dict[str, Any]]) -> str:
    if data is None:
        return "missing"
    return str(data.get("status") or "present")


def _signal(name: str, path: Path) -> FeedbackSignal:
    data = read_json(path)
    status = _status_of(data)
    evidence: Dict[str, Any] = {"path": str(path), "exists": data is not None}
    if data:
        for key in ("version", "status", "file_count", "total_bytes", "total_lines", "health_score"):
            if key in data:
                evidence[key] = data[key]
    return FeedbackSignal(name=name, status=status, evidence=evidence)


def scan_evidence_pressure(root: Path) -> Dict[str, Any]:
    targets = [root / "reports", root / "dist", root / "ledger"]
    file_count = 0
    total_bytes = 0
    newest: List[Dict[str, Any]] = []

    for target in targets:
        if not target.exists():
            continue
        for path in target.rglob("*"):
            if path.is_file():
                file_count += 1
                try:
                    size = path.stat().st_size
                    total_bytes += size
                    newest.append({
                        "path": str(path.relative_to(root)),
                        "size_bytes": size,
                        "mtime": path.stat().st_mtime,
                    })
                except OSError:
                    pass

    newest = sorted(newest, key=lambda x: x["mtime"], reverse=True)[:8]
    for item in newest:
        item.pop("mtime", None)

    if file_count >= 250 or total_bytes >= 1_000_000:
        level = "high"
    elif file_count >= 150 or total_bytes >= 350_000:
        level = "medium"
    else:
        level = "low"

    return {
        "file_count": file_count,
        "total_bytes": total_bytes,
        "pressure_level": level,
        "newest_files": newest,
    }


def compile_feedback(root: str | Path = ".") -> FeedbackReport:
    root = Path(root).resolve()
    report_paths = {
        "nexus_compiler": root / "reports" / "nexus_compile_report_latest.json",
        "adapter_compiler": root / "reports" / "nexus_adapter_compile_report_latest.json",
        "receptor_compiler": root / "reports" / "nexus_receptor_compile_report_latest.json",
        "bridge_compiler": root / "reports" / "nexus_bridge_compile_report_latest.json",
        "runtime_compiler": root / "reports" / "nexus_runtime_compile_report_latest.json",
        "bounded_runtime": root / "reports" / "nexus_bounded_runtime_report_latest.json",
        "evidence_compaction": root / "reports" / "nexus_evidence_compaction_report_latest.json",
        "interconnect": root / "reports" / "nexus_interconnect_report_latest.json",
        "pack_manifest": root / "dist" / "nexus_gate_pack_manifest_latest.json",
    }

    signals = [_signal(name, path) for name, path in report_paths.items()]
    strong = {"pass", "present", "bounded"}
    passed = sum(1 for s in signals if s.status in strong)
    health_score = round(passed / max(1, len(signals)), 4)

    pressure = scan_evidence_pressure(root)
    interconnect = read_json(report_paths["interconnect"]) or {"status": "missing"}

    next_actions: List[str] = []
    if pressure["pressure_level"] != "low":
        next_actions.append("Run .\\scripts\\nexus.ps1 compact before adding more runtime lanes.")
    if interconnect.get("status") != "pass":
        next_actions.append("Run .\\scripts\\nexus.ps1 interconnect to refresh the governed transfer graph.")
    if health_score < 1.0:
        next_actions.append("Run .\\scripts\\nexus.ps1 human and inspect reports/human_surface for the failing lane.")
    if not next_actions:
        next_actions.append("System is ready for the next bounded adapter/receptor lane.")

    status = "pass" if health_score >= 0.75 else "warn"

    return FeedbackReport(
        system="NEXUS GATE",
        version="0.2.2-feedback",
        root=str(root),
        status=status,
        generated_at_utc=_utc(),
        signals=[asdict(s) for s in signals],
        health_score=health_score,
        next_actions=next_actions,
        evidence_pressure=pressure,
        interconnect=interconnect if isinstance(interconnect, dict) else {},
    )


def write_feedback_report(report: FeedbackReport, root: str | Path = ".") -> Path:
    root = Path(root).resolve()
    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    data = asdict(report)
    data["report_hash"] = _sha256_text(json.dumps(data, sort_keys=True))
    path = out_dir / f"nexus_feedback_report_{stamp}.json"
    latest = out_dir / "nexus_feedback_report_latest.json"
    text = json.dumps(data, indent=2)
    path.write_text(text, encoding="utf-8")
    latest.write_text(text, encoding="utf-8")
    return latest
