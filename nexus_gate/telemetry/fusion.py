from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .registry import stable_hash


FIELD_REPORT = Path("reports") / "nexus_telemetry_field_latest.json"
FUSION_STATE = Path("state") / "telemetry" / "fusion" / "nexus_telemetry_field_latest.json"


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_observations(root: Path) -> list[dict[str, Any]]:
    obs_dir = root / "state" / "telemetry" / "observations"
    if not obs_dir.exists():
        return []
    observations = []
    for path in sorted(obs_dir.glob("*.json")):
        try:
            observations.append(json.loads(path.read_text(encoding="utf-8-sig")))
        except Exception:
            continue
    return observations


def _weighted_median(values: list[tuple[float, float]]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    total = sum(weight for _, weight in ordered)
    seen = 0.0
    for value, weight in ordered:
        seen += weight
        if seen >= total / 2:
            return value
    return ordered[-1][0]


def fuse_observations(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    observations = _read_observations(root_path)
    by_phenomenon: dict[str, list[dict[str, Any]]] = {}
    for item in observations:
        by_phenomenon.setdefault(str(item.get("phenomenon")), []).append(item)
    fused = []
    for phenomenon, items in sorted(by_phenomenon.items()):
        scalar = []
        for item in items:
            value = item.get("measurement", {}).get("value")
            confidence = float(item.get("quality", {}).get("combined_confidence") or 0)
            if isinstance(value, (int, float)):
                scalar.append((float(value), confidence))
        median = _weighted_median(scalar)
        mad = None
        rejected = []
        if median is not None:
            deviations = [abs(value - median) for value, _ in scalar]
            mad = statistics.median(deviations) if deviations else 0.0
            for item in items:
                value = item.get("measurement", {}).get("value")
                if isinstance(value, (int, float)) and mad and abs(float(value) - median) / (1.4826 * mad + 0.001) > 4:
                    rejected.append(item.get("observation_id"))
        fused.append({
            "phenomenon": phenomenon,
            "supporting_observations": [item.get("observation_id") for item in items],
            "rejected_observations": rejected,
            "weighted_median": median,
            "median_absolute_deviation": mad,
            "agreement_score": 1.0 if not rejected else max(0.0, 1.0 - len(rejected) / max(1, len(items))),
            "fused_confidence": round(sum(float(item.get("quality", {}).get("combined_confidence") or 0) for item in items) / max(1, len(items)), 6),
        })
    packet = {
        "schema": "NEXUS_TELEMETRY_FIELD.v2.8.0",
        "system": "NEXUS GATE",
        "version": "2.8.0",
        "status": "pass" if observations else "warn",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "observation_count": len(observations),
        "fused": fused,
        "salience": {
            "max_confidence": max([item["fused_confidence"] for item in fused], default=0.0),
            "active_phenomena": [item["phenomenon"] for item in fused],
        },
        "blocked_actions": ["external_tasking", "telemetry_authorizes_action", "telemetry_direct_calibration"],
        "claim_boundary": "Telemetry fusion is observational context only. It cannot command NEXUS, authorize action, or create durable plasticity.",
    }
    packet["telemetry_field_hash"] = stable_hash(packet)
    return packet


def write_fusion(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    packet = fuse_observations(root_path)
    _write(root_path / FIELD_REPORT, packet)
    _write(root_path / FUSION_STATE, packet)
    return packet
