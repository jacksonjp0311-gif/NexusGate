from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Dict, List

from nexus_gate.nexus_cell.plan import build_plan

VERSION = "0.8.5"

DEFAULT_REFS = [
    ("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md", "NexusCell doctrine and claim boundaries"),
    ("docs/nexus_cell/NEXUS_CELL_PLANNER.md", "planner contract and no-execution boundary"),
    ("docs/nexus_cell/NEXUS_CELL_COMPILER_VISIBILITY.md", "compiler visibility boundary"),
    ("state/nexus_cell/cell_manifest.v0.8.4.json", "NexusCell manifest and forbidden surfaces"),
    ("docs/failure_modes/NEXUS_FAILURE_MODE_DOCTOR.md", "Doctor wound routing and repair boundary"),
    ("docs/failure_modes/FAILURE_MODE_CHART.md", "global failure-mode visibility"),
]

CAPABILITY_REFS = {
    "fs_write": [
        ("docs/versioning/NEXUS_CHANGELOG.md", "versioning surface for durable documentation changes"),
        ("docs/versioning/NEXUS_VERSIONING_REHYDRATION.md", "rehydration/versioning continuity"),
    ],
    "git_write": [
        ("scripts/nexus.ps1", "compact command surface and human-run command boundary"),
        ("docs/failure_modes/NEXUS_FAILURE_MODE_DOCTOR.md", "human authorization before durable mutation"),
    ],
    "network": [
        ("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md", "Boundary Seal and network-deny doctrine"),
        ("state/nexus_cell/cell_manifest.v0.8.4.json", "network forbidden surface"),
    ],
    "secrets": [
        ("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md", "Secret Veil doctrine"),
        ("state/nexus_cell/cell_manifest.v0.8.4.json", "secret forbidden surface"),
    ],
    "process_spawn": [
        ("docs/nexus_cell/NEXUS_CELL_PLANNER.md", "no subprocess runner boundary"),
        ("scripts/desktop/open_nexus_gate_console.ps1", "portal read-only operator surface"),
    ],
    "service_install": [
        ("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md", "hard deny future backend boundary"),
        ("docs/failure_modes/FAILURE_MODE_CHART.md", "failure chart visibility before escalation"),
    ],
    "host_mount": [
        ("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md", "host mount / blast-radius boundary"),
        ("state/nexus_cell/cell_manifest.v0.8.4.json", "host resource forbidden surface"),
    ],
}


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _file_digest(root: Path, rel: str) -> Dict[str, object]:
    path = root / rel
    if not path.exists() or not path.is_file():
        return {"path": rel, "exists": False, "sha256": None, "size_bytes": 0}
    data = path.read_bytes()
    return {"path": rel, "exists": True, "sha256": _sha256_bytes(data), "size_bytes": len(data)}


def _dedupe_refs(refs: List[tuple[str, str]], limit: int) -> List[tuple[str, str]]:
    seen = set()
    out: List[tuple[str, str]] = []
    for path, reason in refs:
        if path in seen:
            continue
        seen.add(path)
        out.append((path, reason))
        if len(out) >= limit:
            break
    return out


def select_context_refs(plan: Dict[str, object], limit: int = 12) -> List[Dict[str, str]]:
    refs: List[tuple[str, str]] = list(DEFAULT_REFS)
    caps = plan.get("capability_vector", {})
    if isinstance(caps, dict):
        for capability, enabled in caps.items():
            if enabled and capability in CAPABILITY_REFS:
                refs.extend(CAPABILITY_REFS[capability])

    decision = str(plan.get("authority_decision", ""))
    if decision in {"deny", "reject", "shadow", "review"}:
        refs.extend([
            ("docs/failure_modes/NEXUS_FAILURE_MODE_DOCTOR.md", "review or denial requires Doctor boundary visibility"),
            ("docs/failure_modes/FAILURE_MODE_CHART.md", "repeated wounds must be chart-visible"),
        ])

    return [{"path": path, "reason": reason} for path, reason in _dedupe_refs(refs, max(1, limit))]


def build_context_bridge(root: Path, intent: str, limit: int = 12) -> Dict[str, object]:
    plan = build_plan(root=root, intent=intent)
    refs = select_context_refs(plan, limit=limit)
    evidence = []
    for ref in refs:
        digest = _file_digest(root, ref["path"])
        digest["reason"] = ref["reason"]
        evidence.append(digest)

    bridge_seed = json.dumps(
        {
            "intent_hash": plan.get("intent_hash"),
            "risk_score": plan.get("risk_score"),
            "authority_decision": plan.get("authority_decision"),
            "refs": evidence,
        },
        sort_keys=True,
    )

    return {
        "version": VERSION,
        "generated_utc": _utc_now(),
        "mode": "read_only_context_bridge_no_execution",
        "intent": intent,
        "planner": {
            "version": plan.get("version"),
            "mode": plan.get("mode"),
            "risk_score": plan.get("risk_score"),
            "authority_decision": plan.get("authority_decision"),
            "route_mode": plan.get("route_mode"),
            "gate_flags": plan.get("gate_flags"),
            "claim_boundary": plan.get("claim_boundary"),
        },
        "context_refs": evidence,
        "context_ref_count": len(evidence),
        "context_bridge_hash": _sha256_bytes(bridge_seed.encode("utf-8")),
        "boundary": {
            "execution_enabled": False,
            "backend_enabled": False,
            "network_enabled": False,
            "secrets_enabled": False,
            "git_write_enabled": False,
            "rollback_claim_enabled": False,
            "file_contents_embedded": False,
        },
        "outputs": {
            "report": "reports/nexus_cell_context_bridge_latest.json",
            "state": "state/nexus_cell/context_bridge_state_latest.json",
        },
        "claim_boundary": "Context bridge selects bounded evidence references for review; it does not execute, sandbox, read secrets, use network, mutate git, or claim rollback.",
    }


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_outputs(root: Path, packet: Dict[str, object]) -> None:
    _write_json(root / "reports" / "nexus_cell_context_bridge_latest.json", packet)
    _write_json(root / "state" / "nexus_cell" / "context_bridge_state_latest.json", {
        "version": VERSION,
        "generated_utc": packet.get("generated_utc"),
        "mode": packet.get("mode"),
        "context_bridge_hash": packet.get("context_bridge_hash"),
        "context_ref_count": packet.get("context_ref_count"),
        "authority_decision": packet.get("planner", {}).get("authority_decision"),
        "risk_score": packet.get("planner", {}).get("risk_score"),
        "claim_boundary": packet.get("claim_boundary"),
    })


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a read-only NexusCell context bridge packet.")
    parser.add_argument("--root", default=".", help="Repo root.")
    parser.add_argument("--intent", default="", help="Requested action intent.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum context refs.")
    parser.add_argument("--json", action="store_true", help="Print full JSON packet.")
    parser.add_argument("--no-write", action="store_true", help="Do not write report/state files.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    packet = build_context_bridge(root=root, intent=args.intent, limit=args.limit)
    if not args.no_write:
        write_outputs(root, packet)

    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(json.dumps({
            "ok": True,
            "version": VERSION,
            "mode": packet["mode"],
            "context_ref_count": packet["context_ref_count"],
            "authority_decision": packet["planner"]["authority_decision"],
            "risk_score": packet["planner"]["risk_score"],
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
