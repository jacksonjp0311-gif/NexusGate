from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .laplacian import electrical_flow


VERSION = "2.9.0"
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


ROUTE_NODES = [
    "nexus.status",
    "nexus.runtime-hygiene",
    "nexus.predictive-evolve",
    "nexus.experience-readiness",
    "nexus.conductance-field",
]


def _route_scores(flow: dict[str, Any]) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    for route in ROUTE_NODES:
        incoming = 0.0
        outgoing = 0.0
        for edge in flow.get("edge_flows", []):
            if edge.get("target") == route:
                incoming += abs(float(edge.get("flow") or 0.0))
            if edge.get("source") == route:
                outgoing += abs(float(edge.get("flow") or 0.0))
        scores[route] = {
            "net_incoming_flow": round(incoming, 6),
            "net_outgoing_flow": round(outgoing, 6),
            "route_flow": round((incoming + outgoing) / 2.0, 6),
        }
    return scores


def _event_hash(event: dict[str, Any]) -> str:
    body = {key: value for key, value in event.items() if key != "event_hash"}
    return _hash(body)


def _read_history(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.exists():
        return events, errors
    previous = "genesis"
    seen: set[str] = set()
    for index, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except Exception:
            errors.append(f"malformed_row:{index}")
            continue
        if event.get("previous_event_hash") != previous:
            errors.append(f"previous_hash_mismatch:{index}")
        if event.get("event_id") in seen:
            errors.append(f"duplicate_event_id:{index}")
        seen.add(str(event.get("event_id")))
        if event.get("event_hash") != _event_hash(event):
            errors.append(f"event_hash_mismatch:{index}")
        previous = str(event.get("event_hash") or previous)
        events.append(event)
    return events, errors


def build_conductance_field(root: str | Path = ".", intent: str = "") -> dict[str, Any]:
    root_path = Path(root)
    base = _prior(root_path)
    breath_mod = _breath_modifier(root_path)
    telemetry_mod = _telemetry_modifier(root_path)
    inspection = max(D_MIN, min(D_MAX, base + breath_mod))
    planning = max(D_MIN, min(D_MAX, base + telemetry_mod))
    readiness = max(D_MIN, min(D_MAX, base + max(0.0, -breath_mod) + 0.05))
    field = max(D_MIN, min(D_MAX, base + 0.025))
    status = max(D_MIN, min(D_MAX, base + (0.08 if breath_mod < 0 else 0.0)))
    nodes = [
        "identity",
        "evidence",
        "breath-pulse",
        "telemetry-context",
        "recommendation-sink",
        "nexus.runtime-hygiene",
        "nexus.predictive-evolve",
        "nexus.experience-readiness",
        "nexus.conductance-field",
        "nexus.status",
    ]
    edges = [
        _edge("identity->evidence", "identity", "evidence", "supports", base),
        _edge("evidence->breath", "evidence", "breath-pulse", "regulates", inspection),
        _edge("evidence->status", "evidence", "nexus.status", "routes_to", status),
        _edge("status->sink", "nexus.status", "recommendation-sink", "routes_to", status),
        _edge("breath->runtime", "breath-pulse", "nexus.runtime-hygiene", "routes_to", inspection),
        _edge("runtime->sink", "nexus.runtime-hygiene", "recommendation-sink", "routes_to", inspection),
        _edge("telemetry->predictive", "telemetry-context", "nexus.predictive-evolve", "contextualizes", planning),
        _edge("evidence->predictive", "evidence", "nexus.predictive-evolve", "routes_to", planning),
        _edge("predictive->sink", "nexus.predictive-evolve", "recommendation-sink", "routes_to", planning),
        _edge("evidence->readiness", "evidence", "nexus.experience-readiness", "routes_to", readiness),
        _edge("readiness->sink", "nexus.experience-readiness", "recommendation-sink", "routes_to", readiness),
        _edge("evidence->field", "evidence", "nexus.conductance-field", "routes_to", field),
        _edge("field->sink", "nexus.conductance-field", "recommendation-sink", "routes_to", field),
    ]
    try:
        flow = electrical_flow(nodes, edges, "identity", "recommendation-sink")
        packet_status = "pass"
    except Exception as exc:
        flow = {"error": str(exc), "node_potentials": {}, "edge_flows": [], "effective_resistance": None}
        packet_status = "fail"
    route_scores = _route_scores(flow)
    dominant = max(((route, score["route_flow"]) for route, score in route_scores.items()), key=lambda item: item[1], default=(None, 0.0))
    packet = {
        "schema": "NEXUS_CONDUCTANCE_FIELD.v2.9.0",
        "system": "NEXUS GATE",
        "version": VERSION,
        "status": packet_status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "intent": intent,
        "mode": "sparse_geometric_conductance",
        "field_boundary": {
            "adaptive_recommendation_field": True,
            "recommendation_result": "bounded_preference_only",
            "non_adaptive_authorization_gate": "downstream_application_invariant",
            "authorization_is_learnable_weight": False,
        },
        "nodes": nodes,
        "edges": edges,
        "flow": flow,
        "route_scores": route_scores,
        "route_recommendation": {
            "dominant_route": dominant[0],
            "dominant_route_flow": round(dominant[1], 6),
            "effective_resistance": flow.get("effective_resistance"),
            "authority_gate_status": "outside_adaptive_field",
            "execution_status": "not_executed",
        },
        "temporary_modifiers": {
            "breath_modifier": breath_mod,
            "telemetry_modifier": telemetry_mod,
            "cap": 0.1,
        },
        "blocked_edges": ["human_authorization_requirement", "receipt_validity", "source_identity", "claim_boundaries", "telemetry_to_persistent_conductance"],
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
    _write(root_path / ROUTE_STATE, {"schema": "NEXUS_ROUTE_CONDUCTANCE.v2.9.0", "routes": packet["route_scores"], "field_hash": packet["conductance_field_hash"]})
    return packet


def replay_verify(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    events, errors = _read_history(root_path / HISTORY)
    state: dict[str, float] = {}
    for event in events:
        if event.get("event_type") != "conductance_weight_update":
            errors.append(f"unsupported_event_type:{event.get('event_type')}")
            continue
        if event.get("source") == "telemetry":
            errors.append("telemetry_direct_persistent_update")
        edge_id = str(event.get("edge_id") or "")
        after = event.get("conductance_after")
        try:
            parsed = float(after)
        except (TypeError, ValueError):
            errors.append(f"invalid_conductance:{edge_id}")
            continue
        if not math.isfinite(parsed) or parsed < D_MIN or parsed > D_MAX:
            errors.append(f"conductance_out_of_bounds:{edge_id}")
            continue
        state[edge_id] = round(parsed, 6)
    state_hash = _hash({"events": len(events), "state": state})
    return {
        "schema": "NEXUS_CONDUCTANCE_REPLAY.v2.9.0",
        "version": VERSION,
        "status": "pass" if not errors else "fail",
        "event_count": len(events),
        "replay_valid": not errors,
        "mode": "replayed_empty_history" if not events else "deterministic_event_replay",
        "errors": errors,
        "reconstructed_edge_count": len(state),
        "final_state_hash": state_hash,
        "claim_boundary": "Replay verifies conductance history only; no calibration is applied here.",
    }
