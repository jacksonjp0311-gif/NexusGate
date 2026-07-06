from __future__ import annotations

import datetime as _dt
import hashlib
import json
from typing import Dict

VERSION = "0.8.8"


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _sha256(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def build_receipt(run_packet: Dict[str, object]) -> Dict[str, object]:
    basis = {
        "lane": run_packet.get("lane"),
        "intent_hash": run_packet.get("intent_hash"),
        "authority": run_packet.get("authority"),
        "cell_contract_id": run_packet.get("cell_contract", {}).get("cell_contract_id"),
        "execute_requested": run_packet.get("execute_requested"),
        "executed": run_packet.get("execution", {}).get("executed", False),
    }
    return {
        "version": VERSION,
        "generated_utc": _utc_now(),
        "mode": "nexus_cell_shadow_receipt",
        "receipt_id": _sha256(basis),
        "basis": basis,
        "claim_boundary": "Receipt records a controlled NexusCell lane decision. It is not rollback, sandbox proof, security proof, or autonomous authority.",
    }
