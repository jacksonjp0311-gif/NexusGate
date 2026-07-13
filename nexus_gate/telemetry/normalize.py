from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from .registry import source_hash, stable_hash


SCHEMA = "NEXUS_TELEMETRY_OBSERVATION.v2.8.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def freshness(age_seconds: float, half_life_seconds: float) -> float:
    if half_life_seconds <= 0:
        return 0.0
    return round(math.exp(-math.log(2) * max(0.0, age_seconds) / half_life_seconds), 6)


def observation(
    source: dict[str, Any],
    phenomenon: str,
    value: Any,
    unit: str,
    *,
    observed_at_utc: str | None = None,
    quality_flag: str = "cached_fixture",
    location: dict[str, Any] | None = None,
    original: dict[str, Any] | None = None,
) -> dict[str, Any]:
    retrieved = utc_now()
    observed = observed_at_utc or retrieved
    body = original or {"value": value, "unit": unit}
    source_prior = float(source.get("trust_prior", 0.5))
    fresh = freshness(0, float(source.get("freshness_half_life_seconds", 900)))
    confidence = round(source_prior * fresh, 6)
    location_packet = location or {
        "reference_frame": "earth" if not phenomenon.startswith("orbital") else "solar_system",
        "latitude": None,
        "longitude": None,
        "precision": "global",
    }
    packet = {
        "schema": SCHEMA,
        "source_id": source["source_id"],
        "provider": source["provider"],
        "phenomenon": phenomenon,
        "observed_at_utc": observed,
        "retrieved_at_utc": retrieved,
        "location": location_packet,
        "measurement": {
            "value": value,
            "unit": unit,
            "quality_flag": quality_flag,
            "original": body,
        },
        "provenance": {
            "registry_entry_hash": source_hash(source),
            "endpoint_template_hash": stable_hash(source.get("endpoint_template")),
            "request_parameters_hash": stable_hash({}),
            "response_body_hash": stable_hash(body),
            "content_type": (source.get("content_types") or ["application/json"])[0],
        },
        "quality": {
            "schema_valid": True,
            "source_trust": source_prior,
            "freshness": fresh,
            "agreement": None,
            "combined_confidence": confidence,
        },
        "authority_boundary": {
            "observational_only": True,
            "may_execute": False,
            "may_authorize": False,
            "may_calibrate_directly": False,
        },
    }
    packet["observation_id"] = stable_hash(packet)
    return packet
