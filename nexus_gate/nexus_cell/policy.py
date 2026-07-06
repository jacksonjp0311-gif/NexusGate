from __future__ import annotations

from typing import Dict, List

VERSION = "0.8.8"

CONTROLLED_LANES: Dict[str, Dict[str, object]] = {
    "status": {
        "argv": ["python", "-m", "nexus_gate.nexus_shell.shell", "--root", ".", "--command", "status", "--intent", "NexusCell controlled status lane", "--json"],
        "mutates": False,
        "description": "Build NexusShell status packet.",
    },
    "compile": {
        "argv": ["python", "-m", "nexus_gate.compiler", "--root", ".", "--json"],
        "mutates": False,
        "description": "Run the gated compiler.",
    },
    "tests": {
        "argv": ["python", "-m", "unittest", "discover", "-s", "tests"],
        "mutates": False,
        "description": "Run unit tests.",
    },
    "cell-plan": {
        "argv": ["python", "-m", "nexus_gate.nexus_cell.plan", "--root", ".", "--intent", "NexusCell controlled planner lane", "--json"],
        "mutates": False,
        "description": "Build NexusCell planner packet.",
    },
    "cell-context": {
        "argv": ["python", "-m", "nexus_gate.nexus_cell.context_bridge", "--root", ".", "--intent", "NexusCell controlled context lane", "--json"],
        "mutates": False,
        "description": "Build NexusCell context bridge packet.",
    },
    "cell-bridge": {
        "argv": ["python", "-m", "nexus_gate.nexus_cell.bridge", "--root", ".", "--intent", "NexusCell controlled bridge lane", "--json"],
        "mutates": False,
        "description": "Build NexusCell core bridge packet.",
    },
}

FORBIDDEN_CAPABILITIES = [
    "network",
    "secrets",
    "service_install",
    "registry",
    "host_mount",
    "git_write",
]

BOUNDARY = {
    "arbitrary_command_execution": False,
    "network_enabled": False,
    "secrets_enabled": False,
    "host_mount_enabled": False,
    "git_write_enabled": False,
    "rollback_claim_enabled": False,
    "self_authorization_enabled": False,
}


def list_lanes() -> List[str]:
    return sorted(CONTROLLED_LANES)


def lane_policy(lane: str) -> Dict[str, object]:
    if lane not in CONTROLLED_LANES:
        return {
            "lane": lane,
            "known": False,
            "allowed": False,
            "reason": "unknown_lane",
            "boundary": BOUNDARY,
        }
    policy = dict(CONTROLLED_LANES[lane])
    policy.update({
        "lane": lane,
        "known": True,
        "allowed": True,
        "reason": "controlled_internal_lane",
        "boundary": BOUNDARY,
    })
    return policy


def capability_policy(capability_vector: Dict[str, object]) -> Dict[str, object]:
    active = sorted([key for key, value in capability_vector.items() if bool(value)])
    forbidden_active = sorted([key for key in active if key in FORBIDDEN_CAPABILITIES])
    return {
        "active_capabilities": active,
        "forbidden_active": forbidden_active,
        "allowed": len(forbidden_active) == 0,
        "required_response": "deny_or_shadow" if forbidden_active else "read_only_lane_ok",
    }
