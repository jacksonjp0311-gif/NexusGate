from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nexus_gate.gitnexus.impact import build_impact_packet
from nexus_gate.state.snapshot import capture_repository_snapshot


VERSION = "2.5.0"
SCHEMA = "NEXUS_TRIADIC_GEOMETRIC_LATTICE.v2.5.0"
REPORT_LATEST = Path("reports") / "nexus_triadic_lattice_latest.json"
STATE_LATEST = Path("state") / "lattice" / "nexus_triadic_lattice_latest.json"

CLAIM_BOUNDARY = (
    "Triadic Geometric Lattice is recommendation-routing evidence only. It scores "
    "evidence, geometry, and authority alignment for candidate routes. It does not "
    "execute, mutate files, grant authority, prove correctness, or replace final evolve."
)

BLOCKED_ACTIONS = [
    "self_authorize",
    "execute_selected_action",
    "bypass_final_evolve",
    "git_write",
    "external_api_writes",
    "secret_access",
    "promote_geometry_to_authority",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(packet: Any) -> str:
    encoded = json.dumps(packet, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _evidence_axis(recommendation: dict[str, Any]) -> tuple[float, list[str]]:
    notes: list[str] = []
    freshness = recommendation.get("source_packet_freshness") or {}
    if recommendation.get("source") == "final-seal":
        notes.append("final seal has no upstream packet but remains mandatory")
        return 0.82, notes
    if freshness.get("fresh") is True:
        notes.append("source packet is snapshot-fresh")
        return 1.0, notes
    if freshness.get("fresh") is False:
        notes.append("source packet is stale against current snapshot")
        return 0.38, notes
    if recommendation.get("source_packet_hash"):
        notes.append("source packet hash is present but freshness is unknown")
        return 0.62, notes
    notes.append("source packet hash is missing")
    return 0.42, notes


def _geometry_axis(recommendation: dict[str, Any], impact: dict[str, Any]) -> tuple[float, list[str]]:
    notes: list[str] = []
    counts = impact.get("impact_counts") or {}
    impacted = int(counts.get("impacted") or 0)
    hot = int(counts.get("hot") or 0)
    source = str(recommendation.get("source") or "")
    if source in {"origin-seal", "coherence-field", "preflight"}:
        notes.append("route targets global orientation surfaces")
        base = 0.9
    elif source in {"git-scope", "predictive-evolve", "predictive-timing"}:
        notes.append("route targets bounded scope/runtime geometry")
        base = 0.84
    elif source in {"wound-compression", "certificate-resume"}:
        notes.append("route targets repair/resume geometry")
        base = 0.78
    elif source == "final-seal":
        notes.append("route spans full repository geometry")
        base = 0.58
    else:
        notes.append("route has neutral geometry alignment")
        base = 0.7
    if hot >= 80:
        base -= 0.12
        notes.append("high hot-file pressure increases blast-radius cost")
    elif hot <= 20 and impacted:
        base += 0.05
        notes.append("low hot-file pressure improves geometry alignment")
    if impacted >= 200 and source == "final-seal":
        base -= 0.08
        notes.append("full-repo impact makes final seal expensive before scoped lanes")
    return _clamp(base), notes


def _authority_axis(recommendation: dict[str, Any]) -> tuple[float, list[str]]:
    notes: list[str] = []
    blocked = recommendation.get("blocking_conditions") or []
    command = str(recommendation.get("command") or "")
    if "never_skip_before_commit" in blocked:
        notes.append("mandatory final guard is authority-safe but expensive")
        return 0.74, notes
    if "nexus.ps1" in command or command.startswith("python -m nexus_gate"):
        notes.append("route uses governed NEXUS command surface")
        base = 0.96
    else:
        notes.append("route command is not recognized as a governed NEXUS surface")
        base = 0.62
    if any("authorize" in str(item).lower() for item in blocked):
        base -= 0.15
        notes.append("blocking conditions include authorization language")
    return _clamp(base), notes


def align_recommendation(recommendation: dict[str, Any], impact: dict[str, Any]) -> dict[str, Any]:
    evidence, evidence_notes = _evidence_axis(recommendation)
    geometry, geometry_notes = _geometry_axis(recommendation, impact)
    authority, authority_notes = _authority_axis(recommendation)
    alignment = round((evidence * geometry * authority) ** (1 / 3), 4)
    adjustment = round((alignment - 0.65) * 18, 3)
    return {
        "source": recommendation.get("source"),
        "action": recommendation.get("action"),
        "axes": {
            "evidence": round(evidence, 4),
            "geometry": round(geometry, 4),
            "authority": round(authority, 4),
        },
        "alignment": alignment,
        "arbiter_adjustment": adjustment,
        "notes": evidence_notes + geometry_notes + authority_notes,
    }


def apply_lattice_alignment(
    recommendations: list[dict[str, Any]],
    lattice_packet: dict[str, Any],
) -> list[dict[str, Any]]:
    by_key = {
        (item.get("source"), item.get("action")): item
        for item in lattice_packet.get("route_alignments", [])
    }
    aligned: list[dict[str, Any]] = []
    for recommendation in recommendations:
        updated = dict(recommendation)
        lattice = by_key.get((recommendation.get("source"), recommendation.get("action")))
        if lattice:
            updated["triadic_lattice"] = lattice
        aligned.append(updated)
    return aligned


def build_triadic_lattice(
    root: str | Path,
    recommendations: list[dict[str, Any]] | None = None,
    repository_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    if recommendations is None:
        latest_decision = _read_json(root_path / "reports" / "nexus_decision_envelope_latest.json", {})
        recommendations = latest_decision.get("recommendations") or []
    repository_snapshot = repository_snapshot or capture_repository_snapshot(root_path, ["git status --short"])
    impact = build_impact_packet(root_path)
    route_alignments = [align_recommendation(item, impact) for item in recommendations]
    avg_alignment = round(
        sum(item["alignment"] for item in route_alignments) / len(route_alignments),
        4,
    ) if route_alignments else 0.0
    packet = {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "version": VERSION,
        "status": "pass" if impact.get("graph_source_present") else "warn",
        "generated_at_utc": _utc(),
        "mode": "triadic_geometric_route_alignment",
        "repository_snapshot": repository_snapshot,
        "triad": {
            "evidence": "packet freshness, source hashes, and generated report admissibility",
            "geometry": "GitNexus impact pressure, hot-file pressure, and route blast radius",
            "authority": "human-bound command surfaces and non-escalation boundaries",
        },
        "graph_source": impact.get("graph_source"),
        "impact_counts": impact.get("impact_counts"),
        "route_alignments": route_alignments,
        "average_alignment": avg_alignment,
        "selected_hint": max(route_alignments, key=lambda item: item["alignment"], default=None),
        "read_surfaces": [
            "state/gitnexus/gitnexus_graph_latest.json",
            "GITNEXUS/state/gitnexus_graph_latest.json",
            "reports/gitnexus_report_latest.json",
            "state/interconnect_graph.v0.2.2.json",
            "reports/nexus_decision_envelope_latest.json",
        ],
        "write_surfaces": [REPORT_LATEST.as_posix(), STATE_LATEST.as_posix()],
        "blocked_actions": BLOCKED_ACTIONS,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    packet["lattice_packet_hash"] = _sha(packet)
    return packet


def write_triadic_lattice(root: str | Path, packet: dict[str, Any]) -> None:
    root_path = Path(root).resolve()
    for rel in (REPORT_LATEST, STATE_LATEST):
        path = root_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile the NEXUS triadic geometric lattice.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = build_triadic_lattice(args.root)
    write_triadic_lattice(args.root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"NEXUS triadic lattice: {packet['status']} alignment={packet['average_alignment']}")
    return 0 if packet["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
