from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus_gate.intelligence.common import write_json
from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain

from .messages import create_message, validate_message
from .state import ensure_dirs


MESSAGE_LEDGER = Path("ledger") / "nex_inner_messages.jsonl"
MAX_MESSAGES_PER_CYCLE = 96
MAX_MESSAGES_PER_TOPIC = 16


def _read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def publish_message(root: str | Path, message: dict[str, Any]) -> dict[str, Any]:
    paths = ensure_dirs(root)
    check = validate_message(message)
    if not check["valid"]:
        return {"schema": "NEXUS_INNER_MESSAGE_PUBLISH.v2.10.0", "status": "fail", "errors": check["errors"]}
    ledger = Path(root) / MESSAGE_LEDGER
    existing = _read_events(ledger)
    same_cycle = [item for item in existing if item.get("cycle_id") == message.get("cycle_id")]
    same_topic = [item for item in same_cycle if item.get("topic") == message.get("topic")]
    if len(same_cycle) >= MAX_MESSAGES_PER_CYCLE:
        return {"schema": "NEXUS_INNER_MESSAGE_PUBLISH.v2.10.0", "status": "bounded", "reason": "inner_message_budget_exhausted"}
    if len(same_topic) >= MAX_MESSAGES_PER_TOPIC:
        return {"schema": "NEXUS_INNER_MESSAGE_PUBLISH.v2.10.0", "status": "bounded", "reason": "topic_message_budget_exhausted"}
    for item in existing:
        if item.get("message_id") == message.get("message_id") or item.get("payload_hash") == message.get("payload_hash"):
            return {"schema": "NEXUS_INNER_MESSAGE_PUBLISH.v2.10.0", "status": "verified_existing", "message_id": message["message_id"]}
    event = {
        "schema": "NEXUS_INNER_MESSAGE_EVENT.v2.10.0",
        "event_type": "inner_message",
        "message_id": message["message_id"],
        "cycle_id": message["cycle_id"],
        "topic": message["topic"],
        "payload_hash": message["payload_hash"],
        "message_hash": message["message_hash"],
        "source_epoch_id": message["source_epoch_id"],
    }
    appended = append_hash_chained_event(ledger, event, producer="nex-inner-bus")
    write_json(paths["messages"] / f"{message['message_id']}.json", message)
    return {"schema": "NEXUS_INNER_MESSAGE_PUBLISH.v2.10.0", "status": "pass", "event_hash": appended["event_hash"], "message_id": message["message_id"]}


def read_topic(root: str | Path, topic: str) -> list[dict[str, Any]]:
    paths = ensure_dirs(root)
    out = []
    for path in paths["messages"].glob("msg_*.json"):
        try:
            message = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if message.get("topic") == topic:
            out.append(message)
    return sorted(out, key=lambda item: item.get("created_at_utc", ""))


def replay_message_bus(root: str | Path) -> dict[str, Any]:
    base = Path(root)
    ledger = base / MESSAGE_LEDGER
    chain = verify_hash_chain(ledger)
    errors: list[str] = []
    seen: set[str] = set()
    for event in _read_events(ledger):
        message_id = event.get("message_id")
        if message_id in seen:
            errors.append(f"duplicate_message:{message_id}")
        seen.add(str(message_id))
        path = base / "state" / "nex_core" / "messages" / f"{message_id}.json"
        if not path.exists():
            errors.append(f"missing_message_file:{message_id}")
            continue
        message = json.loads(path.read_text(encoding="utf-8-sig"))
        check = validate_message(message)
        if not check["valid"]:
            errors.extend([f"{message_id}:{err}" for err in check["errors"]])
        if event.get("message_hash") != message.get("message_hash"):
            errors.append(f"event_message_hash_mismatch:{message_id}")
    return {
        "schema": "NEXUS_INNER_MESSAGE_REPLAY.v2.10.0",
        "status": "pass" if chain["chain_valid"] and not errors else "fail",
        "message_count": len(seen),
        "chain": chain,
        "errors": errors,
        "claim_boundary": "Inner message replay reconstructs typed evidence traffic only; no authority is created.",
    }
