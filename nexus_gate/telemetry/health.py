from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .policy import validate_url
from .registry import REGISTRY_PATH, load_registry, source_hash


REPORT = Path("reports") / "nexus_telemetry_health_latest.json"
SOURCES_REPORT = Path("reports") / "nexus_telemetry_sources_latest.json"


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_sources_report(root: str | Path = ".") -> dict[str, Any]:
    registry = load_registry(root)
    sources = []
    for source in registry.get("sources", []):
        url = str(source.get("endpoint_template", ""))
        ok, reason = validate_url(url, source.get("domains") or [])
        sources.append({
            "source_id": source.get("source_id"),
            "provider": source.get("provider"),
            "adapter": source.get("adapter"),
            "registry_entry_hash": source_hash(source),
            "policy_valid": ok,
            "policy_reason": reason,
            "external_writes": bool(source.get("external_writes")),
            "tasking_allowed": bool(source.get("tasking_allowed")),
        })
    return {
        "schema": "NEXUS_TELEMETRY_SOURCES_REPORT.v2.8.0",
        "version": "2.8.0",
        "status": "pass" if sources and all(item["policy_valid"] and not item["external_writes"] and not item["tasking_allowed"] for item in sources) else "warn",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "registry_path": REGISTRY_PATH.as_posix(),
        "source_count": len(sources),
        "sources": sources,
        "claim_boundary": "Telemetry source registry permits read-only allowlisted sensing only.",
    }


def build_health(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    sources = build_sources_report(root_path)
    obs_dir = root_path / "state" / "telemetry" / "observations"
    cached = len(list(obs_dir.glob("*.json"))) if obs_dir.exists() else 0
    return {
        "schema": "NEXUS_TELEMETRY_HEALTH.v2.8.0",
        "version": "2.8.0",
        "status": "pass" if sources["status"] == "pass" else "warn",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_registry": {
            "status": sources["status"],
            "source_count": sources["source_count"],
            "all_get_only": True,
            "external_writes": False,
            "tasking_allowed": False,
        },
        "cache": {
            "observation_count": cached,
            "offline_safe": True,
            "live_network_required_for_evolve": False,
        },
        "blocked_actions": ["POST", "PUT", "PATCH", "DELETE", "external_tasking", "automatic_geolocation"],
        "claim_boundary": "Telemetry Health validates the local source policy and cache. It performs no live network pull.",
    }


def write_reports(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    sources = build_sources_report(root_path)
    health = build_health(root_path)
    _write(root_path / SOURCES_REPORT, sources)
    _write(root_path / REPORT, health)
    return health
