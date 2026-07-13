from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from nexus_gate.intelligence.common import read_json, sha_obj, utc, write_json
from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain

from .state import ensure_dirs, latest_epoch
from .teach import compute_teaching_quality


LEARN_LEDGER = Path("ledger") / "nex_learning_events.jsonl"
CONFIG = {
    "schema": "NEXUS_LEARNING_CONFIG.v2.10.0",
    "g_min": 0.01,
    "g_max": 10.0,
    "eta": 0.04,
    "mu": 0.02,
    "nu": 0.03,
    "lambda": 0.01,
    "delta_max": 0.05,
    "minimum_independent_verified_teachings": 3,
    "minimum_gate_quality": 0.75,
}
CONFIG_HASH = sha_obj(CONFIG)


def compute_learning_utility(delta_accuracy: float = 0.0, delta_retrieval: float = 0.0, delta_grounding: float = 0.0, delta_unsupported: float = 0.0, delta_compute: float = 0.0) -> float:
    value = 0.35 * delta_accuracy + 0.25 * delta_retrieval + 0.25 * delta_grounding - 0.45 * delta_unsupported - 0.1 * delta_compute
    return round(max(-1.0, min(1.0, value)), 6)


def log_conductance_update(
    *,
    current: float,
    prior: float,
    quality: float,
    utility: float,
    contradiction_pressure: float = 0.0,
    regression_pressure: float = 0.0,
) -> dict[str, float]:
    z = math.log(max(CONFIG["g_min"], current))
    z0 = math.log(max(CONFIG["g_min"], prior))
    raw_delta = (
        CONFIG["eta"] * quality * utility
        - CONFIG["mu"] * contradiction_pressure
        - CONFIG["nu"] * regression_pressure
        - CONFIG["lambda"] * (z - z0)
    )
    bounded_delta = max(-CONFIG["delta_max"], min(CONFIG["delta_max"], raw_delta))
    next_z = max(math.log(CONFIG["g_min"]), min(math.log(CONFIG["g_max"]), z + bounded_delta))
    return {
        "current_conductance": round(current, 8),
        "prior_conductance": round(prior, 8),
        "delta_z": round(bounded_delta, 8),
        "proposed_conductance": round(math.exp(next_z), 8),
        "relative_change": round(math.exp(next_z) / current - 1.0, 8) if current else 0.0,
    }


def _sealed_teachings(root: str | Path) -> list[dict[str, Any]]:
    teaching_root = ensure_dirs(root)["teaching"]
    out = []
    for path in teaching_root.glob("teach_*/40_teaching_seal.json"):
        packet = read_json(path, {})
        if packet:
            out.append(packet)
    return out


def propose_conductance_updates(teaching_packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    accepted = [item for item in teaching_packets if item.get("human_disposition") in {"accepted", "accepted_with_modification"} and not item.get("negative_evidence")]
    support = len({item.get("teaching_id") for item in accepted})
    quality_values = [float((item.get("quality") or compute_teaching_quality(item)).get("gate_quality", 0.0)) for item in accepted]
    gate_quality = min(quality_values) if quality_values else 0.0
    eligible = support >= CONFIG["minimum_independent_verified_teachings"] and gate_quality >= CONFIG["minimum_gate_quality"]
    utility = compute_learning_utility(delta_accuracy=0.02 if eligible else 0.0, delta_retrieval=0.02 if eligible else 0.0, delta_grounding=0.02 if eligible else 0.0)
    update = log_conductance_update(current=1.0, prior=1.0, quality=gate_quality, utility=utility)
    return [
        {
            "edge_id": "language.intent->procedure.retrieval",
            "eligible": eligible,
            "support_count": support,
            "minimum_required": CONFIG["minimum_independent_verified_teachings"],
            "utility": utility,
            "math": update,
        }
    ]


def propose(root: str | Path) -> dict[str, Any]:
    paths = ensure_dirs(root)
    epoch = latest_epoch(root)
    teachings = _sealed_teachings(root)
    quality_components = {
        "provenance_integrity": min([float(item.get("quality", {}).get("provenance_integrity", 0)) for item in teachings], default=0.0),
        "validation_strength": min([float(item.get("quality", {}).get("validation_strength", 0)) for item in teachings], default=0.0),
        "causal_attribution": min([float(item.get("quality", {}).get("causal_attribution", 0)) for item in teachings], default=0.0),
        "later_stability": min([float(item.get("quality", {}).get("later_stability", 0)) for item in teachings], default=0.0),
        "human_acceptance": min([float(item.get("quality", {}).get("human_acceptance", 0)) for item in teachings], default=0.0),
        "independent_repetition": min(1.0, len({item.get("teaching_id") for item in teachings if item.get("human_disposition") in {"accepted", "accepted_with_modification"}}) / 3.0),
    }
    values = list(quality_components.values())
    product = 1.0
    for value in values:
        product *= value
    quality_components["gate_quality"] = round(min(values) if values else 0.0, 6)
    quality_components["ranking_quality"] = round(product ** (1.0 / 6.0), 6) if values else 0.0
    proposal_id = "learn_" + sha_obj({"teachings": [item.get("teaching_id") for item in teachings], "epoch": epoch, "created_at_utc": utc()})[:24]
    packet = {
        "schema": "NEXUS_GEOMETRIC_LEARNING_PROPOSAL.v2.10.0",
        "proposal_id": proposal_id,
        "teaching_ids": [item.get("teaching_id") for item in teachings],
        "experience_ids": [],
        "candidate_ids": [],
        "edge_updates": propose_conductance_updates(teachings),
        "motif_updates": [],
        "alias_updates": [],
        "procedure_updates": [],
        "negative_evidence_updates": [item.get("teaching_id") for item in teachings if item.get("negative_evidence")],
        "quality": quality_components,
        "learning_config": CONFIG,
        "learning_config_hash": CONFIG_HASH,
        "predicted_effect": {"persistent_weight_change": False, "requires_human_authorization": True},
        "verification_requirements": ["replay_exact", "paired_improvement", "retention", "authority_invariants"],
        "status": "pending_verification" if quality_components["gate_quality"] else "blocked_insufficient_verified_teaching",
        "automatic_apply": False,
        "source_epoch_id": epoch["source_epoch_id"],
        "authority_boundary": {"human_authorization_required": True, "may_apply_itself": False},
    }
    packet["proposal_hash"] = sha_obj({k: v for k, v in packet.items() if k != "proposal_hash"})
    write_json(paths["learning"] / f"{proposal_id}.json", packet)
    append_hash_chained_event(Path(root) / LEARN_LEDGER, {"schema": "NEXUS_LEARNING_EVENT.v2.10.0", "event_type": "proposal_created", "proposal_id": proposal_id, "proposal_hash": packet["proposal_hash"], "source_epoch_id": epoch["source_epoch_id"]}, producer="nex-learn")
    return packet


def authorize_learning_proposal(root: str | Path, proposal_id: str, expires_minutes: int = 30) -> dict[str, Any]:
    proposal = read_json(ensure_dirs(root)["learning"] / f"{proposal_id}.json", {})
    if not proposal:
        return {"schema": "NEXUS_LEARNING_AUTHORIZATION.v2.10.0", "status": "fail", "reason": "missing_proposal"}
    payload = {
        "schema": "NEXUS_LEARNING_AUTHORIZATION.v2.10.0",
        "authorization_id": "learn_auth_" + sha_obj({"proposal": proposal_id, "created_at_utc": utc()})[:24],
        "proposal_id": proposal_id,
        "proposal_hash": proposal.get("proposal_hash"),
        "source_epoch_id": proposal.get("source_epoch_id"),
        "learning_config_hash": proposal.get("learning_config_hash"),
        "created_at_utc": utc(),
        "expires_minutes": expires_minutes,
        "human_authorization_required": True,
        "authority_boundary": {"single_proposal_only": True, "reusable": False, "may_create_authority": False},
    }
    payload["authorization_hash"] = sha_obj({k: v for k, v in payload.items() if k != "authorization_hash"})
    write_json(ensure_dirs(root)["learning"] / f"{proposal_id}.authorization.json", payload)
    append_hash_chained_event(Path(root) / LEARN_LEDGER, {"schema": "NEXUS_LEARNING_EVENT.v2.10.0", "event_type": "proposal_authorized", "proposal_id": proposal_id, "authorization_hash": payload["authorization_hash"]}, producer="nex-learn")
    return payload | {"status": "pass"}


def apply_learning_event(root: str | Path, proposal_id: str) -> dict[str, Any]:
    proposal = read_json(ensure_dirs(root)["learning"] / f"{proposal_id}.json", {})
    authorization = read_json(ensure_dirs(root)["learning"] / f"{proposal_id}.authorization.json", {})
    if not proposal:
        return {"schema": "NEXUS_LEARNING_APPLY.v2.10.0", "status": "fail", "reason": "missing_proposal"}
    if not authorization:
        return {"schema": "NEXUS_LEARNING_APPLY.v2.10.0", "status": "blocked", "reason": "missing_human_authorization", "persistent_learning_applied": False}
    if proposal.get("quality", {}).get("gate_quality", 0.0) < CONFIG["minimum_gate_quality"]:
        return {"schema": "NEXUS_LEARNING_APPLY.v2.10.0", "status": "blocked", "reason": "gate_quality_below_threshold", "persistent_learning_applied": False}
    applied_path = ensure_dirs(root)["learning"] / f"{proposal_id}.applied.json"
    if applied_path.exists():
        return {"schema": "NEXUS_LEARNING_APPLY.v2.10.0", "status": "verified_existing", "reason": "duplicate_apply_rejected", "persistent_learning_applied": False}
    payload = {
        "schema": "NEXUS_LEARNING_EVENT_APPLIED.v2.10.0",
        "proposal_id": proposal_id,
        "proposal_hash": proposal.get("proposal_hash"),
        "authorization_hash": authorization.get("authorization_hash"),
        "created_at_utc": utc(),
        "edge_updates": proposal.get("edge_updates", []),
        "persistent_learning_applied": True,
        "authority_boundary": {"may_execute": False, "may_authorize": False, "may_mutate_source": False},
    }
    payload["learning_event_hash"] = sha_obj({k: v for k, v in payload.items() if k != "learning_event_hash"})
    write_json(applied_path, payload)
    append_hash_chained_event(Path(root) / LEARN_LEDGER, {"schema": "NEXUS_LEARNING_EVENT.v2.10.0", "event_type": "proposal_applied", "proposal_id": proposal_id, "learning_event_hash": payload["learning_event_hash"]}, producer="nex-learn")
    return payload | {"status": "pass"}


def status(root: str | Path) -> dict[str, Any]:
    paths = ensure_dirs(root)
    proposals = sorted(path.stem for path in paths["learning"].glob("learn_*.json"))
    chain = verify_hash_chain(Path(root) / LEARN_LEDGER)
    return {"schema": "NEX_LEARN_STATUS.v2.10.0", "status": "pass" if chain["chain_valid"] else "fail", "proposal_count": len(proposals), "persistent_learning_applied": any((paths["learning"]).glob("*.applied.json")), "chain": chain}


def replay_verify(root: str | Path) -> dict[str, Any]:
    chain = verify_hash_chain(Path(root) / LEARN_LEDGER)
    errors: list[str] = []
    applied: set[str] = set()
    ledger = Path(root) / LEARN_LEDGER
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("event_type") == "proposal_applied":
                proposal_id = str(event.get("proposal_id"))
                if proposal_id in applied:
                    errors.append(f"duplicate_apply:{proposal_id}")
                applied.add(proposal_id)
    return {"schema": "NEX_LEARNING_REPLAY.v2.10.0", "status": "pass" if chain["chain_valid"] and not errors else "fail", "chain": chain, "errors": errors, "applied_count": len(applied)}
