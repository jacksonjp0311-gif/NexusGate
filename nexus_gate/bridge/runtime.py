from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.bridge.session import BridgeSessionReport, BridgeSessionRunner


@dataclass(frozen=True)
class BoundedRuntimeReport:
    system: str
    version: str
    runtime_id: str
    generated_at_utc: str
    status: str
    max_events: int
    input_count: int
    processed_count: int
    truncated_count: int
    summary_counts: dict[str, int]
    session_reports: list[dict[str, Any]]
    claim_boundary: str = "BoundedRuntimeReport is local runtime evidence only. Not production interoperability."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BoundedBridgeRuntime:
    """Bounded local bridge runtime.

    This runtime deliberately avoids autonomous external I/O. It executes a finite
    list of raw local events through the compiled bridge session runner.
    """

    def __init__(self, max_events: int = 10, runner: BridgeSessionRunner | None = None) -> None:
        if max_events <= 0:
            raise ValueError("max_events must be positive")
        self.max_events = max_events
        self.runner = runner or BridgeSessionRunner()

    def run_batch(self, raw_events: list[dict[str, Any]], runtime_id: str = "local-demo-runtime") -> BoundedRuntimeReport:
        limited = raw_events[: self.max_events]
        session_reports: list[BridgeSessionReport] = [self.runner.run(event) for event in limited]

        counts: dict[str, int] = {
            "engage": 0,
            "shadow": 0,
            "reject": 0,
            "abstain": 0,
            "defer": 0,
        }
        for report in session_reports:
            counts[report.final_mode] = counts.get(report.final_mode, 0) + 1

        truncated = max(0, len(raw_events) - len(limited))
        status = "pass"
        if truncated:
            status = "bounded"

        return BoundedRuntimeReport(
            system="NEXUS GATE",
            version="0.2.0-bounded-bridge-runtime",
            runtime_id=runtime_id,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            status=status,
            max_events=self.max_events,
            input_count=len(raw_events),
            processed_count=len(limited),
            truncated_count=truncated,
            summary_counts=counts,
            session_reports=[report.to_dict() for report in session_reports],
        )

    def write_report(self, report: BoundedRuntimeReport, reports_dir: str | Path = "reports") -> Path:
        reports = Path(reports_dir)
        reports.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = reports / f"nexus_bounded_runtime_report_{stamp}.json"
        latest = reports / "nexus_bounded_runtime_report_latest.json"
        encoded = json.dumps(report.to_dict(), indent=2)
        path.write_text(encoded, encoding="utf-8")
        latest.write_text(encoded, encoding="utf-8")
        return path


def demo_events() -> list[dict[str, Any]]:
    return [
        {
            "session_id": "runtime-readonly",
            "packet_id": "runtime-readonly-packet",
            "event_type": "demo.message",
            "message": "bounded runtime readonly",
            "requested_action": "read_only_signal",
        },
        {
            "session_id": "runtime-tool-shadow",
            "packet_id": "runtime-tool-packet",
            "event_type": "demo.tool_request",
            "requested_action": "tool_call",
            "authority_scope": [],
        },
        {
            "session_id": "runtime-bad-schema",
            "packet_id": "runtime-bad-schema-packet",
            "event_type": "demo.message",
            "schema_id": "UNKNOWN_SCHEMA",
            "requested_action": "read_only_signal",
        },
    ]
