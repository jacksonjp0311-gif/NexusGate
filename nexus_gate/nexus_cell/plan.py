"""Read-only NexusCell planning surface.

This module scores requested capabilities and emits a plan report. It does not
execute commands, spawn processes for user actions, create sandboxes, expose
secrets, mutate git, or claim rollback.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

VERSION = "0.8.4C"

CAPABILITY_WEIGHTS: Dict[str, float] = {
    "fs_read": 0.05,
    "fs_write": 0.25,
    "network": 0.30,
    "secrets": 0.90,
    "registry": 0.70,
    "process_spawn": 0.25,
    "service_install": 0.95,
    "git_write": 0.80,
    "host_mount": 0.60,
    "clipboard": 0.20,
    "gpu": 0.10,
}

CAPABILITY_ORDER: List[str] = list(CAPABILITY_WEIGHTS.keys())


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _contains_any(text: str, needles: List[str]) -> bool:
    return any(item in text for item in needles)


def capability_vector_from_intent(intent: str) -> Dict[str, int]:
    text = " ".join(intent.lower().split())
    caps = {key: 0 for key in CAPABILITY_ORDER}

    if _contains_any(text, ["read", "open", "inspect", "show", "list", "cat ", "get-content", "view", "summarize"]):
        caps["fs_read"] = 1
    if _contains_any(text, ["write", "create", "patch", "edit", "update", "delete", "remove", "modify", "commit file"]):
        caps["fs_write"] = 1
    if _contains_any(text, ["http://", "https://", "api", "download", "upload", "internet", "web request", "curl", "wget"]):
        caps["network"] = 1
    if _contains_any(text, ["secret", "token", "api key", "password", "credential", "bearer"]):
        caps["secrets"] = 1
    if _contains_any(text, ["registry", "regedit", "hkey_", "hkcu", "hklm"]):
        caps["registry"] = 1
    if _contains_any(text, ["run", "execute", "start", "launch", "subprocess", "powershell", "python -m", "npm ", "cmd.exe"]):
        caps["process_spawn"] = 1
    if _contains_any(text, ["install service", "service install", "daemon", "driver", "scheduled task"]):
        caps["service_install"] = 1
    if _contains_any(text, ["git add", "git commit", "git push", "git tag", "rebase", "merge", "durable commit"]):
        caps["git_write"] = 1
    if _contains_any(text, ["host mount", "mount host", "c:\\", "users\\", "onedrive\\desktop", "system32"]):
        caps["host_mount"] = 1
    if _contains_any(text, ["clipboard", "copy to clipboard", "paste from clipboard"]):
        caps["clipboard"] = 1
    if _contains_any(text, ["gpu", "cuda", "vram"]):
        caps["gpu"] = 1

    if caps["fs_write"] or caps["git_write"]:
        caps["fs_read"] = 1
    return caps


def risk_terms(capabilities: Dict[str, int]) -> Dict[str, float]:
    blast = 0.0
    if capabilities.get("host_mount"):
        blast = 0.40
    elif capabilities.get("fs_write"):
        blast = 0.20

    git_penalty = 0.80 if capabilities.get("git_write") else 0.0
    network_penalty = 0.45 if capabilities.get("network") else 0.0
    secret_penalty = 1.00 if capabilities.get("secrets") else 0.0

    capability_sum = sum(CAPABILITY_WEIGHTS[key] * float(capabilities.get(key, 0)) for key in CAPABILITY_ORDER)

    return {
        "capability_sum": round(capability_sum, 4),
        "blast_radius": round(blast, 4),
        "git_mutation": round(git_penalty, 4),
        "network_openness": round(network_penalty, 4),
        "secret_exposure": round(secret_penalty, 4),
    }


def authority_decision(intent: str, capabilities: Dict[str, int], score: float) -> Tuple[str, str, List[str]]:
    text = intent.lower()
    flags: List[str] = []

    if not intent.strip():
        return "reject", "reject", ["schema_missing_intent"]

    if capabilities.get("secrets") and capabilities.get("network"):
        return "deny", "escalate", ["hard_deny_secret_plus_network"]
    if capabilities.get("service_install"):
        return "deny", "escalate", ["hard_deny_service_install_requires_future_backend"]
    if capabilities.get("git_write") and "authorize" not in text and "human" not in text:
        flags.append("git_write_without_explicit_authority")

    mutating = any(capabilities.get(k) for k in ["fs_write", "git_write", "registry", "host_mount", "clipboard"])
    if mutating and "authorize" not in text and "human" not in text:
        return "shadow", "shadow", flags or ["authority_missing_for_mutation"]

    if score > 0.65:
        return "deny", "escalate", flags or ["risk_above_deny_threshold"]
    if score > 0.30:
        return "review", "defer", flags or ["risk_requires_review"]
    return "engage", "engage", flags or ["planner_only_low_risk"]


def build_plan(root: Path, intent: str) -> Dict[str, object]:
    caps = capability_vector_from_intent(intent)
    terms = risk_terms(caps)
    score = round(sum(terms.values()), 4)
    decision, route_mode, flags = authority_decision(intent, caps, score)

    allowed_next_actions = [
        "read doctrine",
        "inspect manifest",
        "review risk report",
        "request human authorization before any future execution backend",
    ]

    if decision in {"deny", "reject"}:
        allowed_next_actions = ["do not execute", "review policy", "revise intent", "request human decision"]

    return {
        "version": VERSION,
        "generated_utc": _utc_now(),
        "mode": "read_only_planner_no_execution",
        "intent": intent,
        "intent_hash": _sha256_text(intent),
        "capability_vector": caps,
        "risk_terms": terms,
        "risk_score": score,
        "authority_decision": decision,
        "route_mode": route_mode,
        "gate_flags": flags,
        "boundary": {
            "execution_enabled": False,
            "backend_enabled": False,
            "network_enabled": False,
            "secrets_enabled": False,
            "git_write_enabled": False,
            "rollback_claim_enabled": False,
        },
        "allowed_next_actions": allowed_next_actions,
        "outputs": {
            "report": "reports/nexus_cell_plan_latest.json",
            "state": "state/nexus_cell/planner_state_latest.json",
        },
        "claim_boundary": "NexusCell planner scores intent and emits evidence only; it does not execute, sandbox, rollback, mutate git, expose secrets, or authorize itself.",
    }


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_outputs(root: Path, plan: Dict[str, object]) -> None:
    _write_json(root / "reports" / "nexus_cell_plan_latest.json", plan)
    _write_json(root / "state" / "nexus_cell" / "planner_state_latest.json", {
        "version": VERSION,
        "generated_utc": plan.get("generated_utc"),
        "mode": plan.get("mode"),
        "intent_hash": plan.get("intent_hash"),
        "risk_score": plan.get("risk_score"),
        "authority_decision": plan.get("authority_decision"),
        "route_mode": plan.get("route_mode"),
        "claim_boundary": plan.get("claim_boundary"),
    })


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan a NexusCell invocation without executing it.")
    parser.add_argument("--root", default=".", help="Repo root.")
    parser.add_argument("--intent", default="", help="Requested action intent.")
    parser.add_argument("--json", action="store_true", help="Print full JSON report.")
    parser.add_argument("--no-write", action="store_true", help="Do not write report/state files.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    plan = build_plan(root=root, intent=args.intent)
    if not args.no_write:
        write_outputs(root, plan)

    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True))
    else:
        print(json.dumps({
            "ok": True,
            "version": VERSION,
            "mode": plan["mode"],
            "risk_score": plan["risk_score"],
            "authority_decision": plan["authority_decision"],
            "route_mode": plan["route_mode"],
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
