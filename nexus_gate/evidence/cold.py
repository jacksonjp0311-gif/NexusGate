from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


FailureSeverity = Literal["info", "warning", "block", "critical"]
WoundStatus = Literal["open", "contained", "replayed", "demoted", "retired"]
RouteAction = Literal["reject", "shadow", "replay", "demote", "recalibrate", "retire"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ShadowReport:
    """Cold evidence report produced by a shadow route."""

    report_id: str
    packet_id: str
    route_mode: str
    observed_result: str
    expected_boundary: str
    passed: bool
    timestamp_utc: str = field(default_factory=utc_now)
    claim_boundary: str = "ShadowReport is local cold evidence, not a safety proof."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ShadowFailure:
    """Failure extracted from a ShadowReport."""

    failure_id: str
    report_id: str
    failure_mode: str
    severity: FailureSeverity
    trigger: str
    required_response: str
    timestamp_utc: str = field(default_factory=utc_now)
    claim_boundary: str = "ShadowFailure classification is local evidence only."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ShadowWound:
    """Persistent wound record created from a shadow failure."""

    wound_id: str
    failure_id: str
    affected_surface: str
    status: WoundStatus = "open"
    memory_promotion_allowed: bool = False
    timestamp_utc: str = field(default_factory=utc_now)
    claim_boundary: str = "ShadowWound blocks trust promotion until replay evidence exists."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WoundRoute:
    """Declared response path for a wound."""

    route_id: str
    wound_id: str
    action: RouteAction
    reason: str
    replay_required: bool = True
    timestamp_utc: str = field(default_factory=utc_now)
    claim_boundary: str = "WoundRoute is a local recovery route, not a safety proof."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReplayCertificate:
    """Evidence that a wounded route was replayed before retrust."""

    certificate_id: str
    wound_id: str
    replay_passed: bool
    replay_report_path: str
    memory_promotion_allowed: bool = False
    timestamp_utc: str = field(default_factory=utc_now)
    claim_boundary: str = "ReplayCertificate permits only local gate progression."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DemotionDecision:
    """Decision to demote or retire a failing specialist/route."""

    decision_id: str
    wound_id: str
    decision: Literal["demote", "retire", "recalibrate"]
    reason: str
    timestamp_utc: str = field(default_factory=utc_now)
    claim_boundary: str = "DemotionDecision is local governance evidence only."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ColdEvidenceEngine:
    """Minimal cold evidence engine.

    Runtime laws:
    - No shadow failure without wound route.
    - No re-engagement without replay certificate.
    - No memory promotion from failed shadow evidence.
    """

    def classify_shadow_report(self, report: ShadowReport) -> ShadowFailure | None:
        if report.passed:
            return None

        return ShadowFailure(
            failure_id=f"failure::{report.report_id}",
            report_id=report.report_id,
            failure_mode="shadow_failure_unrouted",
            severity="block",
            trigger=report.observed_result,
            required_response="create_wound_route_before_retrust",
        )

    def create_wound(self, failure: ShadowFailure, affected_surface: str) -> ShadowWound:
        return ShadowWound(
            wound_id=f"wound::{failure.failure_id}",
            failure_id=failure.failure_id,
            affected_surface=affected_surface,
            status="open",
            memory_promotion_allowed=False,
        )

    def route_wound(self, wound: ShadowWound, action: RouteAction = "replay") -> WoundRoute:
        return WoundRoute(
            route_id=f"route::{wound.wound_id}",
            wound_id=wound.wound_id,
            action=action,
            reason="wound_requires_replay_before_retrust",
            replay_required=True,
        )

    def certify_replay(self, wound: ShadowWound, replay_passed: bool, replay_report_path: str) -> ReplayCertificate:
        return ReplayCertificate(
            certificate_id=f"replay::{wound.wound_id}",
            wound_id=wound.wound_id,
            replay_passed=replay_passed,
            replay_report_path=replay_report_path,
            memory_promotion_allowed=bool(replay_passed),
        )
