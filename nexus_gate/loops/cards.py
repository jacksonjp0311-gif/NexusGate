
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.9.3"
CARD_SCHEMA = "NEXUS_LOOP_CARD.v0.9.3"
SET_SCHEMA = "NEXUS_LOOP_CARD_SET.v0.9.3"

DEFAULT_FUNCTIONS = {
    "rhp-core": "Rehydrate repository origin before patching, compounding, or agent continuation.",
    "script-evolution": "Shape generated scripts through governed local intelligence instead of loose patches.",
    "reflective-validation": "Run compile/test/compiler gates and convert failures into wound intelligence.",
    "failure-intelligence": "Read failure surfaces for the next exact wound.",
    "validate-promote": "Validate before promotion without granting autonomous commit/push authority.",
    "ai-orchestrator-preflight": "Give AI local context before selecting a loop.",
    "wound-indexed-resume": "Emit active wound and resume recommendation.",
    "impact-map": "Map patch impact through GITNEXUS.",
    "bounded-validation": "Run compile, bounded tests, and compiler.",
    "compiler-wound-focus": "Focus exact compiler failed gates.",
    "docs-doctrine-preflight": "Read README, doctrine, and loop docs before coding.",
    "hud-loop-sync": "Regenerate loop cards for the portal/HUD.",
    "release-seal": "Final local evidence before commit/push.",
}


def _stage_summary(stages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for stage in stages:
        item = {"name": stage.get("name", "unnamed"), "type": stage.get("type", "unknown")}
        for key in ["command", "path", "loop"]:
            if key in stage:
                item[key] = stage.get(key)
        out.append(item)
    return out


def build_loop_cards(root: str | Path) -> dict[str, Any]:
    root = Path(root).resolve()
    registry_path = root / "loops" / "nexus_loop_registry.v0.1.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    loops = registry.get("loops", {})
    cards = []
    for index, loop_id in enumerate(sorted(loops), start=1):
        loop = loops[loop_id]
        title = loop.get("title") or loop_id.replace("-", " ").title()
        function = loop.get("function") or DEFAULT_FUNCTIONS.get(loop_id) or loop.get("description", "")
        display_group = loop.get("display_group") or "Meta Loops"
        operator_use = loop.get("operator_use") or "Use when this loop matches the active gate, wound, or validation need."
        cards.append({
            "schema": CARD_SCHEMA,
            "order": index,
            "loop_id": loop_id,
            "title": title,
            "description": loop.get("description", ""),
            "function": function,
            "operator_use": operator_use,
            "command_surface": f"python -m nexus_gate.loops.runner --root . --loop {loop_id} --intent \"<intent>\" --json",
            "execute_surface": f"python -m nexus_gate.loops.runner --root . --loop {loop_id} --intent \"<intent>\" --execute --human-authorized --json",
            "powershell_surface": f".\\scripts\\nexus.ps1 meta-loop -Loop {loop_id} -Tag \"<intent>\"",
            "ai_callable": bool(loop.get("ai_callable", True)),
            "local_only": bool(loop.get("local_only", True)),
            "mutates": bool(loop.get("mutates", False)),
            "requires_human_authorization": bool(loop.get("requires_human_authorization", False)),
            "stop_on_failure": bool(loop.get("stop_on_failure", False)),
            "authority_boundary": registry.get("authority_boundary", {}),
            "claim_boundary": registry.get("claim_boundary", ""),
            "stages": _stage_summary(loop.get("stages", [])),
            "stages_summary": [f"{s.get('name')}:{s.get('type')}" for s in loop.get("stages", [])],
            "hud": {
                "card_kind": "nexus_loop",
                "display_group": display_group,
                "primary_action": "inspect_or_run_through_governed_loop_runner",
                "human_card_ready": True,
                "ai_toolkit_ready": True,
            },
        })
    return {
        "schema": SET_SCHEMA,
        "version": VERSION,
        "system": "NEXUS_LOOP_CARDS",
        "generated_for": "NEXUS_GATE_v0.9.3",
        "source_registry": "loops/nexus_loop_registry.v0.1.json",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "card_count": len(cards),
        "cards": cards,
        "authority_boundary": registry.get("authority_boundary", {}),
        "claim_boundary": "Loop cards are HUD-readable surfaces for local named loops. They grant no autonomous authority, shell authority, git write authority, memory promotion, network access, secret access, safety proof, security proof, or correctness proof.",
    }


def write_loop_cards(root: str | Path) -> dict[str, Any]:
    root = Path(root).resolve()
    packet = build_loop_cards(root)
    state_dir = root / "state" / "loops"
    docs_dir = root / "docs" / "runtime"
    state_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    (state_dir / "nexus_loop_cards.v0.9.3.json").write_text(encoded, encoding="utf-8")
    (state_dir / "nexus_loop_cards_latest.json").write_text(encoded, encoding="utf-8")
    lines = [
        "# NEXUS Loop Cards",
        "",
        "NEXUS Loop Cards are HUD-ready JSON descriptions of the canonical local loop registry.",
        "v0.9.3 expands cards into an AI Loop Toolkit: local evidence loops the AI can recommend while NexusGate preserves authority boundaries.",
        "",
        "Boundary: loop cards describe governed local loops. They do not grant autonomous authority, execution authority, git write authority, memory promotion, safety proof, security proof, or correctness proof.",
        "",
        "## Card Surfaces",
        "",
        "- `state/loops/nexus_loop_cards.v0.9.3.json`",
        "- `state/loops/nexus_loop_cards_latest.json`",
        "- `python -m nexus_gate.loops.cards --root . --json`",
        "- Spiral Core Portal option `[14] Nexus Loops / Cards`",
        "",
        "## Cards",
        "",
    ]
    for card in packet["cards"]:
        lines.extend([
            f"### {card['title']}",
            "",
            f"- Loop: `{card['loop_id']}`",
            f"- Group: `{card['hud']['display_group']}`",
            f"- Function: {card['function']}",
            f"- Operator use: {card['operator_use']}",
            f"- Command: `{card['command_surface']}`",
            f"- Execute: `{card['execute_surface']}`",
            "",
        ])
    (docs_dir / "NEXUS_LOOP_CARDS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build NEXUS loop cards from the loop registry.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_loop_cards(Path(args.root))
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"wrote {packet['card_count']} NEXUS loop cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
