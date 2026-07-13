from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .fusion import write_fusion
from .health import build_sources_report, write_reports
from .normalize import observation
from .registry import indexed_sources


PROFILE_SOURCES = {
    "local-weather": "nws.forecast",
    "space-weather": "noaa.swpc.planetary-k-index",
    "earth-events": "usgs.earthquake-significant",
    "planetary": "jpl.horizons.ephemeris",
}


def _write_observation(root: Path, packet: dict) -> None:
    path = root / "state" / "telemetry" / "observations" / f"{packet['observation_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pull_fixture(root: str | Path, profile: str, latitude: float | None = None, longitude: float | None = None) -> dict:
    root_path = Path(root)
    sources = indexed_sources(root_path)
    source_id = PROFILE_SOURCES.get(profile, profile)
    if source_id not in sources:
        return {"status": "fail", "error": "unknown_profile", "profile": profile}
    source = sources[source_id]
    if os.environ.get("NEXUS_TELEMETRY_LIVE") != "1":
        values = {
            "nws.forecast": ("temperature_c", 21.0, "C"),
            "noaa.swpc.planetary-k-index": ("geomagnetic_kp", 3.0, "Kp"),
            "usgs.earthquake-significant": ("earthquake_magnitude", 0.0, "Mw"),
            "jpl.horizons.ephemeris": ("orbital_distance", 1.0, "AU"),
        }
        phenomenon, value, unit = values[source_id]
        location = {
            "reference_frame": "earth",
            "latitude": latitude if source.get("location_required") else None,
            "longitude": longitude if source.get("location_required") else None,
            "precision": "coarse" if source.get("location_required") else "global",
        }
        packet = observation(source, phenomenon, value, unit, location=location)
        _write_observation(root_path, packet)
        return {
            "schema": "NEXUS_TELEMETRY_PULL.v2.8.0",
            "status": "pass",
            "mode": "offline_fixture",
            "observation": packet,
            "claim_boundary": "Offline fixture pull exercises the codec without live network dependency.",
        }
    return {
        "schema": "NEXUS_TELEMETRY_PULL.v2.8.0",
        "status": "warn",
        "mode": "live_not_implemented_in_core_release",
        "source_id": source_id,
        "claim_boundary": "Live telemetry is explicitly enabled but this core release keeps live adapters bounded for later smoke tests.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEXUS governed telemetry codec.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("sources", "health", "fuse", "status"):
        p = sub.add_parser(name)
        p.add_argument("--root", default=".")
        p.add_argument("--json", action="store_true")
    pull = sub.add_parser("pull")
    pull.add_argument("--root", default=".")
    pull.add_argument("--profile", default="space-weather")
    pull.add_argument("--latitude", type=float)
    pull.add_argument("--longitude", type=float)
    pull.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "sources":
        packet = build_sources_report(args.root)
    elif args.command in {"health", "status"}:
        packet = write_reports(args.root)
    elif args.command == "fuse":
        packet = write_fusion(args.root)
    else:
        packet = pull_fixture(args.root, args.profile, args.latitude, args.longitude)
    print(json.dumps(packet, indent=2, sort_keys=True) if getattr(args, "json", False) else packet.get("status", "unknown"))
    return 0 if packet.get("status") in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
