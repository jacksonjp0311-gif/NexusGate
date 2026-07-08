
from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
from typing import Any

VERSION = "0.9.5"
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

TOOLBELT_GROUPS = [
    {
        "group_id": "orient",
        "title": "Orient",
        "purpose": "Rehydrate from repo truth, see status, and select the next local loop.",
        "loops": ["repo-radar", "ai-orchestrator-preflight", "toolbelt-index", "toolbelt-dashboard", "next-action-router", "local-oracle"],
        "chain": "repo-radar -> toolbelt-index -> next-action-router",
    },
    {
        "group_id": "plan",
        "title": "Plan",
        "purpose": "Turn intent into architecture, patch plan, test plan, and bounded build chain.",
        "loops": ["idea-forge", "architecture-sketch", "patch-plan", "test-strategy", "creative-build-chain", "pair-programming-brief"],
        "chain": "idea-forge -> architecture-sketch -> patch-plan -> test-strategy",
    },
    {
        "group_id": "debug",
        "title": "Debug",
        "purpose": "Narrow failures into wounds and select the smallest healing surface.",
        "loops": ["debug-lens", "wound-indexed-resume", "compiler-wound-focus", "debug-recovery-chain", "failure-intelligence", "friction-detector"],
        "chain": "debug-lens -> wound-indexed-resume -> compiler-wound-focus",
    },
    {
        "group_id": "hygiene",
        "title": "Hygiene",
        "purpose": "Keep scope clean, claims bounded, stale surfaces visible, and authority intact.",
        "loops": ["scope-hygiene", "claim-boundary-audit", "boundary-scan", "stale-surface-scan", "risk-register", "dependency-preflight"],
        "chain": "scope-hygiene -> boundary-scan -> claim-boundary-audit",
    },
    {
        "group_id": "ship",
        "title": "Ship",
        "purpose": "Validate, summarize, seal, and prepare human-authorized durable mutation.",
        "loops": ["bounded-validation", "release-brief", "toolbelt-ship", "release-seal", "commit-story", "continuity-seal"],
        "chain": "bounded-validation -> release-brief -> release-seal -> commit-story",
    },
    {
        "group_id": "memory",
        "title": "Memory",
        "purpose": "Preserve continuity through handoff packs, session briefs, docs weaving, and memory anchors.",
        "loops": ["handoff-pack", "session-brief", "memory-anchor", "docs-weaver", "continuity-seal", "paradise-index"],
        "chain": "handoff-pack -> session-brief -> memory-anchor -> continuity-seal",
    },
    {
        "group_id": "ui",
        "title": "UI / HUD",
        "purpose": "Support the operator surface: loop cards, command palette, UI polish, and code garden maps.",
        "loops": ["hud-loop-sync", "command-palette", "ui-polish", "code-garden-map", "surface-map"],
        "chain": "hud-loop-sync -> command-palette -> ui-polish",
    },
]

def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()

def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default

def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def _loop_lookup(registry: dict[str, Any]) -> dict[str, Any]:
    return registry.get("loops", {}) if isinstance(registry, dict) else {}

def _card_lookup(cards: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for card in cards.get("cards", []) if isinstance(cards, dict) else []:
        if isinstance(card, dict) and card.get("loop_id"):
            out[card["loop_id"]] = card
    return out

def _group_status(group: dict[str, Any], loops: dict[str, Any], card_map: dict[str, Any]) -> dict[str, Any]:
    ids = list(group["loops"])
    missing_loops = [loop_id for loop_id in ids if loop_id not in loops]
    missing_cards = [loop_id for loop_id in ids if loop_id not in card_map]
    available = [loop_id for loop_id in ids if loop_id in loops]
    return {
        **group,
        "available_loops": available,
        "missing_loops": missing_loops,
        "missing_cards": missing_cards,
        "ready": not missing_loops and not missing_cards,
        "commands": [
            f'python -m nexus_gate.loops.runner --root . --loop {loop_id} --intent "<intent>" --json'
            for loop_id in available
        ],
        "execute_commands": [
            f'python -m nexus_gate.loops.runner --root . --loop {loop_id} --intent "<intent>" --execute --human-authorized --json'
            for loop_id in available
        ],
    }

def build_toolbelt_packet(root: str | Path, intent: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    registry = _read_json(root / "loops" / "nexus_loop_registry.v0.1.json", {})
    cards = _read_json(root / "state" / "loops" / "nexus_loop_cards_latest.json", {})
    loops = _loop_lookup(registry)
    card_map = _card_lookup(cards)
    groups = [_group_status(group, loops, card_map) for group in TOOLBELT_GROUPS]
    ready_groups = [g for g in groups if g["ready"]]
    missing = sorted({m for g in groups for m in g["missing_loops"]})
    return {
        "schema": "NEXUS_AI_TOOLBELT.v0.9.5",
        "version": VERSION,
        "mode": MODE,
        "generated_utc": _utc(),
        "intent": intent,
        "root": str(root),
        "status": "pass" if not missing else "review",
        "toolbelt_group_count": len(groups),
        "ready_group_count": len(ready_groups),
        "loop_count": len(loops),
        "card_count": len(card_map),
        "recommended_first": "toolbelt-start",
        "recommended_when_dirty": "scope-hygiene",
        "recommended_when_failed": "debug-recovery-chain",
        "recommended_when_ready": "toolbelt-ship",
        "groups": groups,
        "missing_loop_count": len(missing),
        "missing_loops": missing,
        "command_surface": "python -m nexus_gate.loops.toolbelt --root . --json",
        "loop_surface": 'python -m nexus_gate.loops.runner --root . --loop toolbelt-index --intent "<intent>" --execute --human-authorized --json',
        "boundary": BOUNDARY,
        "claim_boundary": "The AI Toolbelt is a local read-only operator index. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.",
    }

def write_toolbelt(root: str | Path, intent: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    packet = build_toolbelt_packet(root, intent=intent)
    _write_json(root / "state" / "loops" / "nexus_toolbelt.v0.9.5.json", packet)
    _write_json(root / "state" / "loops" / "nexus_toolbelt_latest.json", packet)
    _write_json(root / "reports" / "nexus_toolbelt_latest.json", packet)

    lines = [
        "# NEXUS AI Toolbelt",
        "",
        "The NEXUS AI Toolbelt is the operator-visible map of local, AI-callable loops.",
        "It lets ChatGPT/Codex recommend useful local loops without granting direct repo authority.",
        "",
        "Boundary: the toolbelt is an index and packet emitter only. It grants no autonomous authority, shell authority, network access, secret access, git write authority, safety proof, security proof, or correctness proof.",
        "",
        "## Fast Start",
        "",
        "```powershell",
        'python -m nexus_gate.loops.toolbelt --root . --json',
        'python -m nexus_gate.loops.runner --root . --loop toolbelt-start --intent "<intent>" --execute --human-authorized --json',
        'python -m nexus_gate.loops.runner --root . --loop toolbelt-dashboard --intent "<intent>" --execute --human-authorized --json',
        "```",
        "",
        "## Toolbelt Groups",
        "",
    ]
    for group in packet["groups"]:
        lines.extend([
            f"### {group['title']}",
            "",
            f"- Purpose: {group['purpose']}",
            f"- Chain: `{group['chain']}`",
            f"- Ready: `{str(group['ready']).lower()}`",
            f"- Loops: `{', '.join(group['loops'])}`",
            "",
        ])
    (root / "docs" / "runtime").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "runtime" / "NEXUS_AI_TOOLBELT.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return packet

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build NEXUS AI Toolbelt packet.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_toolbelt(args.root, intent=args.intent)
    print(json.dumps(packet, indent=2, sort_keys=True) if args.json else f"wrote NEXUS AI Toolbelt {packet['status']}")
    return 0 if packet["status"] in {"pass", "review"} else 1

if __name__ == "__main__":
    raise SystemExit(main())
