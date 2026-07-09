from __future__ import annotations
import argparse, datetime as _dt, json, subprocess
from pathlib import Path
from typing import Any

VERSION="0.9.7"
SCHEMA = "NEXUS_AI_TOOLBELT.v0.9.7"
MODE = "nexus_ai_toolbelt"
BOUNDARY = {
    "repo_mutation_enabled": False,
    "git_stage_enabled": False,
    "git_commit_enabled": False,
    "git_push_enabled": False,
    "network_enabled": False,
    "secrets_enabled": False,
    "autonomous_authority": False,
    "arbitrary_command_execution": False,
}
GROUPS = [
    {"group_id":"orient","title":"Orient","purpose":"Rehydrate, see status, and route next action.","loops":["repo-radar","toolbelt-index","toolbelt-console","toolbelt-cockpit","toolbelt-json","toolbelt-dashboard","toolbelt-next","next-action-router","local-oracle"],"chain":"repo-radar -> toolbelt-cockpit -> toolbelt-next"},
    {"group_id":"plan","title":"Plan","purpose":"Turn intent into architecture, patch plan, and tests.","loops":["idea-forge","architecture-sketch","patch-plan","test-strategy","creative-build-chain","pair-programming-brief"],"chain":"idea-forge -> architecture-sketch -> patch-plan -> test-strategy"},
    {"group_id":"debug","title":"Debug","purpose":"Narrow failures into wounds.","loops":["debug-lens","wound-indexed-resume","compiler-wound-focus","debug-recovery-chain","failure-intelligence","friction-detector"],"chain":"debug-lens -> wound-indexed-resume -> compiler-wound-focus"},
    {"group_id":"hygiene","title":"Hygiene","purpose":"Keep scope, claims, stale surfaces, and authority clean.","loops":["scope-hygiene","claim-boundary-audit","boundary-scan","stale-surface-scan","risk-register","dependency-preflight"],"chain":"scope-hygiene -> boundary-scan -> claim-boundary-audit"},
    {"group_id":"ship","title":"Ship","purpose":"Validate, summarize, seal, and prepare human-authorized mutation.","loops":["bounded-validation","release-brief","toolbelt-ship","toolbelt-ship-console","release-seal","commit-story","continuity-seal"],"chain":"bounded-validation -> release-brief -> release-seal -> commit-story"},
    {"group_id":"memory","title":"Memory","purpose":"Preserve continuity.","loops":["handoff-pack","session-brief","memory-anchor","docs-weaver","continuity-seal","paradise-index"],"chain":"handoff-pack -> session-brief -> memory-anchor -> continuity-seal"},
    {"group_id":"ui","title":"UI / HUD","purpose":"Support cards, command palette, UI polish, and code garden maps.","loops":["hud-loop-sync","command-palette","ui-polish","code-garden-map","surface-map"],"chain":"hud-loop-sync -> command-palette -> ui-polish"},
]
VIEWS = {"index":"toolbelt-index","start":"repo-radar","dashboard":"toolbelt-cockpit","next":"next-action-router","ship":"release-brief"}

def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()

def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default
    except Exception:
        return default

def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def _run(root: Path, args: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(args, cwd=str(root), capture_output=True, text=True, timeout=20, check=False)
        return {"ok": proc.returncode == 0, "returncode": proc.returncode, "stdout": (proc.stdout or "")[-2000:], "stderr": (proc.stderr or "")[-1000:]}
    except Exception as exc:
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": str(exc)}

def _status(root: Path) -> dict[str, Any]:
    raw = _run(root, ["git", "status", "--short"]).get("stdout", "")
    lines = [line for line in raw.splitlines() if line.strip()]
    comp = _read_json(root / "reports" / "nexus_compile_report_latest.json", {})
    failed = [g.get("gate") for g in comp.get("gates", []) if isinstance(g, dict) and g.get("status") == "fail"]
    return {
        "head": _run(root, ["git", "rev-parse", "--short", "HEAD"]).get("stdout", "").strip(),
        "dirty": bool(lines),
        "changed_count": len(lines),
        "status_preview": lines[:40],
        "compiler_status": comp.get("status", "unknown"),
        "failed_gates": failed,
    }

def _cards(cards: Any) -> dict[str, Any]:
    return {c.get("loop_id"): c for c in cards.get("cards", []) if isinstance(c, dict) and c.get("loop_id")}

def _group_status(group: dict[str, Any], loops: dict[str, Any], cards: dict[str, Any]) -> dict[str, Any]:
    ids = list(group["loops"])
    available = [loop_id for loop_id in ids if loop_id in loops]
    missing = [loop_id for loop_id in ids if loop_id not in loops]
    missing_cards = [loop_id for loop_id in ids if loop_id not in cards]
    return {**group, "available_loops": available, "missing_loops": missing, "missing_cards": missing_cards, "ready": not missing and not missing_cards, "commands": [f'python -m nexus_gate.loops.runner --root . --loop {loop_id} --intent "<intent>" --json' for loop_id in available], "execute_commands": [f'python -m nexus_gate.loops.runner --root . --loop {loop_id} --intent "<intent>" --execute --human-authorized --json' for loop_id in available]}

def _recommend(status: dict[str, Any], view: str) -> tuple[str, str]:
    if status.get("failed_gates"):
        return "debug-recovery-chain", "compiler report contains failed gates"
    if status.get("dirty"):
        return "scope-hygiene", "working tree has local changes"
    if view == "ship":
        return "release-brief", "ship view requested"
    if view == "start":
        return "repo-radar", "start view requested"
    if view == "next":
        return "next-action-router", "next view requested"
    return "evolution-radar", "tree appears ready for next evolution planning"

def build_toolbelt_packet(root: str | Path, intent: str = "", view: str = "dashboard") -> dict[str, Any]:
    root = Path(root).resolve()
    view = view if view in VIEWS else "dashboard"
    registry = _read_json(root / "loops" / "nexus_loop_registry.v0.1.json", {})
    card_packet = _read_json(root / "state" / "loops" / "nexus_loop_cards_latest.json", {})
    loops = registry.get("loops", {})
    cards = _cards(card_packet)
    groups = [_group_status(group, loops, cards) for group in GROUPS]
    missing = sorted({item for group in groups for item in group["missing_loops"]})
    status = _status(root)
    recommended, reason = _recommend(status, view)
    next_command = f'.\\scripts\\nexus.ps1 meta-loop -Loop {recommended} -Tag "{intent or "<intent>"}"'
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "mode": MODE,
        "view": view,
        "generated_utc": _utc(),
        "intent": intent,
        "root": str(root),
        "status": "pass" if not missing else "review",
        "repo_status": status,
        "recommended_next_loop": recommended,
        "recommendation_reason": reason,
        "next_command": next_command,
        "recommended_next_command": next_command,
        "toolbelt_group_count": len(groups),
        "ready_group_count": sum(1 for group in groups if group["ready"]),
        "loop_count": len(loops),
        "card_count": len(cards),
        "groups": groups,
        "missing_loop_count": len(missing),
        "missing_loops": missing,
        "powershell_surface": '.\\scripts\\nexus.ps1 toolbelt -Tag "<intent>"',
        "powershell_json_surface": '.\\scripts\\nexus.ps1 toolbelt-json -Tag "<intent>"',
        "bash_surface": 'bash scripts/nexus.sh toolbelt "<intent>"',
        "process_chains": {
            "start": "toolbelt-start -> toolbelt-dashboard -> next-action-router",
            "build": "idea-forge -> architecture-sketch -> patch-plan -> test-strategy",
            "debug": "debug-lens -> wound-indexed-resume -> compiler-wound-focus",
            "ship": "scope-hygiene -> boundary-scan -> release-brief -> release-seal",
            "continuity": "handoff-pack -> session-brief -> memory-anchor -> continuity-seal",
        },
        "cockpit": {
            "title": "NEXUS AI TOOLBELT COCKPIT",
            "version": VERSION,
            "next_command": next_command,
            "json_command": '.\\scripts\\nexus.ps1 toolbelt-json -Tag "<intent>"',
        },
        "boundary": BOUNDARY,
        "claim_boundary": "The AI Toolbelt Cockpit is a local read-only operator cockpit. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.",
    }

def render_cockpit(packet: dict[str, Any]) -> str:
    status = packet.get("repo_status", {})
    chains = packet.get("process_chains", {})
    lines = [
        "NEXUS AI TOOLBELT COCKPIT",
        f"Version: v{packet.get('version')}",
        f"HEAD: {status.get('head', 'unknown')}",
        f"Dirty: {status.get('dirty')}",
        f"Changed: {status.get('changed_count')}",
        f"Compiler: {status.get('compiler_status')}",
        "",
        f"Recommended next loop: {packet.get('recommended_next_loop')}",
        f"Reason: {packet.get('recommendation_reason')}",
        f"Next command: {packet.get('next_command')}",
        "",
        "Core commands:",
        "  .\\scripts\\nexus.ps1 toolbelt",
        "  .\\scripts\\nexus.ps1 toolbelt-json -Tag \"<intent>\"",
        "  .\\scripts\\nexus.ps1 toolbelt-next -Tag \"<intent>\"",
        "",
        "Chains:",
    ]
    for key in ["start", "build", "debug", "ship", "continuity"]:
        if key in chains:
            lines.append(f"  {key.title()}: {chains[key]}")
    lines += ["", "Boundary: read-only cockpit; no autonomous authority; no git write authority."]
    return "\n".join(lines)

def write_toolbelt(root: str | Path, intent: str = "", view: str = "dashboard") -> dict[str, Any]:
    root = Path(root).resolve()
    packet = build_toolbelt_packet(root, intent, view)
    _write_json(root / "state" / "loops" / "nexus_toolbelt.v0.9.7.json", packet)
    _write_json(root / "state" / "loops" / "nexus_toolbelt_latest.json", packet)
    _write_json(root / "reports" / "nexus_toolbelt_latest.json", packet)
    lines = [
        "# NEXUS AI Toolbelt",
        "",
        "The NEXUS AI Toolbelt is the operator-visible map of local, AI-callable loops.",
        "v0.9.7 adds Toolbelt Cockpit Output: human cockpit by default, JSON packet on request.",
        "",
        "Boundary: read-only operator cockpit. No autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.",
        "",
        "## Commands",
        "",
        "```powershell",
        ".\\scripts\\nexus.ps1 toolbelt",
        ".\\scripts\\nexus.ps1 toolbelt-json -Tag \"<intent>\"",
        ".\\scripts\\nexus.ps1 toolbelt-next -Tag \"<intent>\"",
        ".\\scripts\\nexus.ps1 toolbelt-ship -Tag \"<intent>\"",
        "```",
        "",
        "## Default Process",
        "",
        "```text",
    ]
    for key, chain in packet["process_chains"].items():
        lines.append(f"{key.title()}: {chain}")
    lines += ["```", "", "## Current Recommendation", "", f"- Loop: `{packet['recommended_next_loop']}`", f"- Reason: {packet['recommendation_reason']}", f"- Next command: `{packet['next_command']}`", "", "## Groups", ""]
    for group in packet["groups"]:
        lines += [f"### {group['title']}", "", f"- Purpose: {group['purpose']}", f"- Chain: `{group['chain']}`", f"- Ready: `{str(group['ready']).lower()}`", ""]
    docs = root / "docs" / "runtime"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "NEXUS_AI_TOOLBELT.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return packet

def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="")
    parser.add_argument("--view", default="dashboard", choices=sorted(VIEWS))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_toolbelt(args.root, args.intent, args.view)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render_cockpit(packet))
    return 0

# NEXUS v0.9.7 cockpit contract shim BEGIN
def _nexus_v097_chain_map(packet):
    current = packet.get("chains")
    if isinstance(current, dict) and current:
        return current
    process = packet.get("process_chains")
    if isinstance(process, dict) and process:
        return process
    chains = {}
    for group in packet.get("groups", []):
        if isinstance(group, dict):
            key = group.get("title") or group.get("group_id") or f"group_{len(chains) + 1}"
            value = group.get("chain") or " -> ".join(group.get("loops", []))
            if value:
                chains[str(key)] = value
    if not chains:
        chains = {
            "Start": "toolbelt-start -> toolbelt-dashboard -> next-action-router",
            "Build": "idea-forge -> architecture-sketch -> patch-plan -> test-strategy",
            "Debug": "debug-lens -> wound-indexed-resume -> compiler-wound-focus",
            "Ship": "scope-hygiene -> boundary-scan -> release-brief -> release-seal",
            "Continuity": "handoff-pack -> session-brief -> memory-anchor -> continuity-seal",
        }
    return chains


def _nexus_v097_safe_intent(intent):
    s = str(intent or "operator").replace('"', "'").strip()
    return s or "operator"


def _nexus_v097_apply_contract(packet, intent=""):
    if not isinstance(packet, dict):
        raise TypeError("Toolbelt packet contract expected dict")
    packet["schema"] = "NEXUS_AI_TOOLBELT.v0.9.7"
    packet["version"] = "0.9.7"
    packet.setdefault("mode", "nexus_ai_toolbelt")
    rec = packet.get("recommended_next_loop") or packet.get("next_loop") or "next-action-router"
    packet["recommended_next_loop"] = rec
    packet.setdefault("recommendation_reason", "Toolbelt cockpit contract selected next local loop.")
    tag = _nexus_v097_safe_intent(packet.get("intent") or intent)
    command = f'.\\scripts\\nexus.ps1 meta-loop -Loop {rec} -Tag "{tag}" -Execute -HumanAuthorized'
    packet["next_command"] = packet.get("next_command") or command
    packet["recommended_next_command"] = packet.get("recommended_next_command") or packet["next_command"]
    packet["json_surface"] = packet.get("json_surface") or f'.\\scripts\\nexus.ps1 toolbelt-json -Tag "{tag}"'
    packet["chains"] = _nexus_v097_chain_map(packet)
    packet.setdefault("process_chains", packet["chains"])
    packet.setdefault("cockpit_title", "NEXUS AI TOOLBELT COCKPIT")
    packet.setdefault("evidence_rule", "stdout = smoke only; file packets = truth")
    return packet


_NEXUS_V097_ORIGINAL_BUILD_TOOLBELT_PACKET = build_toolbelt_packet


def build_toolbelt_packet(root, intent="", view="dashboard", *args, **kwargs):
    packet = _NEXUS_V097_ORIGINAL_BUILD_TOOLBELT_PACKET(root, intent, view, *args, **kwargs)
    return _nexus_v097_apply_contract(packet, intent)
# NEXUS v0.9.7 cockpit contract shim END

if __name__ == "__main__":
    raise SystemExit(main())
