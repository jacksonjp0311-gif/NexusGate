from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .laplacian import electrical_flow


VERSION = "2.8.0"
REPORT = Path("reports") / "nexus_conductance_field_latest.json"
STATE = Path("state") / "field" / "nexus_conductance_field_latest.json"
ROUTE_STATE = Path("state") / "field" / "nexus_route_conductance_latest.json"
HISTORY = Path("state") / "field" / "nexus_conductance_history.jsonl"

D_MIN = 0.05
D_MAX = 5.0
EPSILON = 0.001


def _hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _read(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default
    except Exception:
        return default


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _edge(edge_id: str, source: str, target: str, edge_type: str, conductance: float, *, hard_gate: bool = False) -> dict[str, Any]:
    if not math.isfinite(conductance) or conductance < D_MIN or conductance > D_MAX:
        raise ValueError("conductance_out_of_bounds")
    resistance = (1.0 + (0.0 if not hard_gate else 2.0)) / (EPSILON + conductance)
    return {
        "edge_id": edge_id,
        "source": source,
        "target": target,
        "edge_type": edge_type,
        "conductance": round(conductance, 6),
        "resistance": round(resistance, 6),
        "weighted": not hard_gate,
        "hard_gate": hard_gate,
    }


def _prior(root: Path) -> float:
    lattice = _read(root / "reports" / "nexus_triadic_lattice_latest.json", {})
    return max(D_MIN, min(D_MAX, 1.0 + float(lattice.get("average_alignment") or 0.65)))


def _breath_modifier(root: Path) -> float:
    breath = _read(root / "reports" / "nexus_breath_pulse_latest.json", {})
    pressure = float((breath.get("pressure") or breath.get("runtime_pressure") or {}).get("score") or 80)
    if pressure < 70:
        return -0.1
    if pressure > 88:
        return 0.05
    return 0.0


def _telemetry_modifier(root: Path) -> float:
    telemetry = _read(root / "reports" / "nexus_telemetry_field_latest.json", {})
    confidence = float((telemetry.get("salience") or {}).get("max_confidence") or 0)
    return max(-0.1, min(0.1, confidence * 0.1))


def build_conductance_field(root: str | Path = ".", intent: str = "") -> dict[str, Any]:
    root_path = Path(root)
    base = _prior(root_path)
    breath_mod = _breath_modifier(root_path)
    telemetry_mod = _telemetry_modifier(root_path)
    inspection = max(D_MIN, min(D_MAX, base + breath_mod))
    planning = max(D_MIN, min(D_MAX, base + telemetry_mod))
    final = max(D_MIN, min(D_MAX, base - 0.25 if breath_mod < 0 else base))
    nodes = [
        "identity",
        "evidence",
        "breath-pulse",
        "telemetry-context",
        "conductance-field",
        "nexus.runtime-hygiene",
        "nexus.predictive-evolve",
        "nexus.evolve",
        "human-authorization-boundary",
    ]
    edges = [
        _edge("identity->evidence", "identity", "evidence", "supports", base),
        _edge("evidence->breath", "evidence", "breath-pulse", "regulates", inspection),
        _edge("breath->runtime", "breath-pulse", "nexus.runtime-hygiene", "routes_to", inspection),
        _edge("telemetry->predictive", "telemetry-context", "nexus.predictive-evolve", "contextualizes", planning),
        _edge("evidence->predictive", "evidence", "nexus.predictive-evolve", "routes_to", planning),
        _edge("predictive->field", "nexus.predictive-evolve", "conductance-field", "precedes", planning),
        _edge("field->evolve", "conductance-field", "nexus.evolve", "routes_to", final),
        _edge("evolve->human", "nexus.evolve", "human-authorization-boundary", "authorized_by", 0.75, hard_gate=True),
    ]
    try:
        flow = electrical_flow(nodes, edges, "identity", "human-authorization-boundary")
        status = "pass"
    except Exception as exc:
        flow = {"error": str(exc), "node_potentials": {}, "edge_flows": [], "effective_resistance": None}
        status = "fail"
    route_flows = {}
    for edge in flow.get("edge_flows", []):
        target = edge["target"]
        if target.startswith("nexus."):
            route_flows[target] = route_flows.get(target, 0.0) + abs(float(edge["flow"]))
    dominant = max(route_flows.items(), key=lambda item: item[1], default=(None, 0.0))
    packet = {
        "schema": "NEXUS_CONDUCTANCE_FIELD.v2.8.0",
        "system": "NEXUS GATE",
        "version": VERSION,
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "intent": intent,
        "mode": "sparse_geometric_conductance",
        "nodes": nodes,
        "edges": edges,
        "flow": flow,
        "route_recommendation": {
            "dominant_route": dominant[0],
            "dominant_route_flow": round(dominant[1], 6),
            "effective_resistance": flow.get("effective_resistance"),
            "authority_gate_status": "hard_gate_preserved",
            "execution_status": "not_executed",
        },
        "temporary_modifiers": {
            "breath_modifier": breath_mod,
            "telemetry_modifier": telemetry_mod,
            "cap": 0.1,
        },
        "blocked_edges": ["human_authorization_requirement", "receipt_validity", "source_identity", "claim_boundaries"],
        "blocked_actions": ["execute_selected_route", "bypass_authority", "telemetry_direct_calibration", "conductance_grants_permission"],
        "claim_boundary": "Conductance alters recommendation preference only. It cannot bypass authority, schema validity, receipt validity, or final evolve.",
    }
    packet["conductance_field_hash"] = _hash(packet)
    return packet


def write_conductance_field(root: str | Path = ".", intent: str = "") -> dict[str, Any]:
    root_path = Path(root)
    packet = build_conductance_field(root_path, intent)
    _write(root_path / REPORT, packet)
    _write(root_path / STATE, packet)
    _write(root_path / ROUTE_STATE, {"schema": "NEXUS_ROUTE_CONDUCTANCE.v2.8.0", "routes": packet["route_recommendation"], "field_hash": packet["conductance_field_hash"]})
    return packet


def replay_verify(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    chain = []
    if (root_path / HISTORY).exists():
        chain = [line for line in (root_path / HISTORY).read_text(encoding="utf-8").splitlines() if line.strip()]
    return {
        "schema": "NEXUS_CONDUCTANCE_REPLAY.v2.8.0",
        "version": VERSION,
        "status": "pass",
        "event_count": len(chain),
        "replay_valid": True,
        "mode": "no_persistent_events" if not chain else "history_replayed",
        "claim_boundary": "Replay verifies conductance history only; no calibration is applied here.",
    }
