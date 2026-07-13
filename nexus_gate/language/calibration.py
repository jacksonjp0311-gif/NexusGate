from __future__ import annotations

from pathlib import Path

from nexus_gate.ledger.append_only import verify_hash_chain


LEDGER = Path("ledger") / "language_training_events.jsonl"


def status(root: str | Path) -> dict:
    chain = verify_hash_chain(Path(root) / LEDGER)
    return {"schema": "NEXUS_LANGUAGE_CALIBRATION_STATUS.v2.9.0", "status": "pass" if chain["chain_valid"] else "fail", "automatic_apply": False, "persistent_conductance_applied": False, "ledger_chain": chain}


def propose(root: str | Path) -> dict:
    return {"schema": "NEXUS_LANGUAGE_CONDUCTANCE_PROPOSAL.v2.9.0", "status": "blocked", "blocking_reasons": ["minimum_three_verified_experiences_required", "explicit_human_authorization_required"], "automatic_apply": False}


def replay_verify(root: str | Path) -> dict:
    return status(root) | {"schema": "NEXUS_LANGUAGE_CALIBRATION_REPLAY.v2.9.0"}
