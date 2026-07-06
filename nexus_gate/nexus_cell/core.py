from __future__ import annotations

import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Dict, List

from nexus_gate.nexus_cell.context_bridge import build_context_bridge
from nexus_gate.nexus_cell.plan import build_plan

VERSION = "0.8.7"

READ_ONLY_STATUS = "core_bridge_visible_no_execution"

BLOCKED_BY_CAPABILITY = {
    "fs_write": "filesystem_write",
    "network": "network_access",
    "secrets": "secret_access",
    "registry": "registry_mutation",
    "process_spawn": "process_spawn",
    "service_install": "service_install",
    "git_write": "git_mutation",
    "host_mount": "host_mount",
    "clipboard": "clipboard_access",
}

SAFE_ALLOWED_BASE = [
    "read doctrine",
    "inspect manifest",
    "build planner report",
    "build context bridge packet",
    "build NexusCell bridge contract",
    "request human authorization for any future mutation",
]


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _active_capabilities(plan: Dict[str, object]) -> List[str]:
    caps = plan.get("capability_vector", {})
    if not isinstance(caps, dict):
        return []
    return [key for key, value in caps.items() if bool(value)]


def _blocked_operations(plan: Dict[str, object]) -> List[str]:
    active = _active_capabilities(plan)
    blocked = [BLOCKED_BY_CAPABILITY[key] for key in active if key in BLOCKED_BY_CAPABILITY]
    if str(plan.get("authority_decision")) in {"deny", "reject"}:
        blocked.append("all_execution")
    return sorted(set(blocked))


def _required_authority(plan: Dict[str, object]) -> List[str]:
    decision = str(plan.get("authority_decision", ""))
    active = set(_active_capabilities(plan))
    required = []
    if decision in {"shadow", "review", "deny", "reject"}:
        required.append("human_decision")
    if {"fs_write", "git_write", "registry", "host_mount", "clipboard"} & active:
        required.append("human_mutation_authority")
    if {"network", "secrets", "service_install"} & active:
        required.append("future_backend_authority")
    if not required:
        required.append("read_only_operator_authority")
    return sorted(set(required))


def _cell_phase(plan: Dict[str, object]) -> str:
    decision = str(plan.get("authority_decision", ""))
    if decision in {"deny", "reject"}:
        return "blocked"
    if decision in {"shadow", "review"}:
        return "shadow_review"
    return "read_only_ready"


def build_cell_contract(root: Path, intent: str, context_limit: int = 12) -> Dict[str, object]:
    plan = build_plan(root=root, intent=intent)
    context_packet = build_context_bridge(root=root, intent=intent, limit=context_limit)

    seed = json.dumps(
        {
            "intent_hash": plan.get("intent_hash"),
            "authority_decision": plan.get("authority_decision"),
            "risk_score": plan.get("risk_score"),
            "context_bridge_hash": context_packet.get("context_bridge_hash"),
            "active_capabilities": _active_capabilities(plan),
        },
        sort_keys=True,
    )

    blocked = _blocked_operations(plan)
    required = _required_authority(plan)

    return {
        "version": VERSION,
        "generated_utc": _utc_now(),
        "mode": "nexus_cell_core_contract_no_execution",
        "intent": intent,
        "intent_hash": plan.get("intent_hash"),
        "cell_contract_id": _sha256_text(seed),
        "cell_phase": _cell_phase(plan),
        "planner": {
            "version": plan.get("version"),
            "mode": plan.get("mode"),
            "risk_score": plan.get("risk_score"),
            "authority_decision": plan.get("authority_decision"),
            "route_mode": plan.get("route_mode"),
            "gate_flags": plan.get("gate_flags"),
            "capability_vector": plan.get("capability_vector"),
        },
        "context_bridge": {
            "version": context_packet.get("version"),
            "mode": context_packet.get("mode"),
            "context_bridge_hash": context_packet.get("context_bridge_hash"),
            "context_ref_count": context_packet.get("context_ref_count"),
        },
        "active_capabilities": _active_capabilities(plan),
        "blocked_operations": blocked,
        "required_authority": required,
        "human_authorization_required": "human_decision" in required or "human_mutation_authority" in required or "future_backend_authority" in required,
        "allowed_operations": SAFE_ALLOWED_BASE,
        "boundary": {
            "execution_enabled": False,
            "backend_enabled": False,
            "network_enabled": False,
            "secrets_enabled": False,
            "git_write_enabled": False,
            "rollback_claim_enabled": False,
            "shell_mutation_enabled": False,
            "host_mount_enabled": False,
        },
        "claim_boundary": "NexusCell core contract is a read-only execution-governance contract; it does not execute, sandbox, expose secrets, use network, mutate git, mount host paths, claim rollback, or self-authorize.",
    }
