from __future__ import annotations

import hashlib
import json
import os
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOCK_STALE_SECONDS = 120
LOCK_RETRY_SECONDS = 5


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha_obj(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def _event_hash(event: dict[str, Any]) -> str:
    body = {key: value for key, value in event.items() if key != "event_hash"}
    return _sha_obj(body)


def _lock_payload(producer: str) -> str:
    return json.dumps(
        {
            "pid": os.getpid(),
            "created_at_utc": _utc(),
            "created_at_epoch": time.time(),
            "hostname": socket.gethostname(),
            "producer": producer,
        },
        sort_keys=True,
    )


class _LedgerLock:
    def __init__(self, path: Path, producer: str):
        self.path = path.with_suffix(path.suffix + ".lock")
        self.producer = producer

    def __enter__(self) -> "_LedgerLock":
        deadline = time.time() + LOCK_RETRY_SECONDS
        while True:
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(_lock_payload(self.producer))
                    handle.flush()
                    os.fsync(handle.fileno())
                return self
            except FileExistsError:
                stale = False
                try:
                    data = json.loads(self.path.read_text(encoding="utf-8"))
                    stale = (time.time() - float(data.get("created_at_epoch", 0))) > LOCK_STALE_SECONDS
                except Exception:
                    stale = True
                if stale:
                    try:
                        self.path.unlink()
                        continue
                    except FileNotFoundError:
                        continue
                    except Exception:
                        pass
                if time.time() >= deadline:
                    raise TimeoutError(f"Timed out waiting for ledger lock: {self.path}")
                time.sleep(0.05)

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def _read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        events.append(json.loads(line))
    return events


def verify_hash_chain(path: str | Path) -> dict[str, Any]:
    ledger = Path(path)
    previous = "genesis"
    seen_event_ids: set[str] = set()
    seen_previous: set[str] = set()
    malformed = 0
    mismatches = 0
    duplicate_ids = 0
    fork_detected = False
    tail_hash = "genesis"
    length = 0
    if not ledger.exists():
        return {
            "chain_valid": True,
            "chain_length": 0,
            "tail_hash": tail_hash,
            "fork_detected": False,
            "malformed_rows": 0,
            "hash_mismatches": 0,
            "duplicate_event_ids": 0,
        }
    for line in ledger.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except Exception:
            malformed += 1
            continue
        length += 1
        event_id = str(event.get("event_id") or "")
        if event_id in seen_event_ids:
            duplicate_ids += 1
        seen_event_ids.add(event_id)
        actual_previous = event.get("previous_event_hash")
        if actual_previous != previous:
            mismatches += 1
        if actual_previous in seen_previous and actual_previous != "genesis":
            fork_detected = True
        seen_previous.add(str(actual_previous))
        expected_hash = _event_hash(event)
        if event.get("event_hash") != expected_hash:
            mismatches += 1
        previous = str(event.get("event_hash") or expected_hash)
        tail_hash = previous
    valid = malformed == 0 and mismatches == 0 and duplicate_ids == 0 and not fork_detected
    return {
        "chain_valid": valid,
        "chain_length": length,
        "tail_hash": tail_hash,
        "fork_detected": fork_detected,
        "malformed_rows": malformed,
        "hash_mismatches": mismatches,
        "duplicate_event_ids": duplicate_ids,
    }


def read_chain_tail(path: str | Path) -> dict[str, Any]:
    events = _read_events(Path(path))
    if not events:
        return {"tail_hash": "genesis", "tail_event": None, "chain_length": 0}
    tail = events[-1]
    return {"tail_hash": tail.get("event_hash") or "genesis", "tail_event": tail, "chain_length": len(events)}


def append_hash_chained_event(path: str | Path, event: dict[str, Any], producer: str = "nexus-ledger") -> dict[str, Any]:
    ledger = Path(path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with _LedgerLock(ledger, producer):
        before = verify_hash_chain(ledger)
        if not before["chain_valid"]:
            raise ValueError(f"Cannot append to invalid ledger chain: {ledger}")
        body = dict(event)
        body.setdefault("generated_at_utc", _utc())
        body.setdefault("producer", producer)
        body["previous_event_hash"] = before["tail_hash"]
        body["event_id"] = body.get("event_id") or _sha_obj(
            {
                "event_type": body.get("event_type"),
                "action_id": body.get("action_id"),
                "epoch_id": body.get("epoch_id"),
                "observation_id": body.get("observation_id"),
                "previous_event_hash": body["previous_event_hash"],
                "generated_at_utc": body.get("generated_at_utc"),
            }
        )
        body["event_hash"] = _event_hash(body)
        with ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(body, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        after = read_chain_tail(ledger)
        if after["tail_hash"] != body["event_hash"]:
            raise ValueError(f"Ledger append verification failed: {ledger}")
        return body
