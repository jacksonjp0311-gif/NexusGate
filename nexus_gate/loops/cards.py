"""NEXUS loop card compiler.

Builds HUD-ready JSON cards from the canonical local loop registry.
Cards are read-only operator surfaces. They do not grant execution authority.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

VERSION = "0.9.1B"
SCHEMA = "NEXUS_LOOP_CARD.v0.9.1B"

FUNCTIONS = {
    "rhp-core": "Rehydrate repository origin before patching, compounding, or agent continuation.",
    "script-evolution": "Shape generated scripts so ChatGPT/Codex work through local governed intelligence instead of loose patches.",
    "reflective-validation": "Run compile/test/compiler gates and convert failures into compact wound intelligence.",
    "failure-intelligence": "Read failure surfaces so the next closer heals the active wound rather than drifting.",
    "validate-promote": "Validate a candidate patch and stop before durable mutation unless a human-authorized outer script promotes it.",
}

OPERATORS = {
    "rhp-core": "Use first when resuming from chat, memory, or a dirty session.",
    "script-evolution": "Use before generating a new All-One closer or code-changing script.",
    "reflective-validation": "Use after a patch when you need gate evidence and wound capture.",
    "failure-intelligence": "Use after a failed gate to identify the next exact repair target.",
    "validate-promote": "Use as the final local validation loop before commit/push authority.",
}

DISPLAY_GROUPS = {
    "rhp-core": "Origin",
    "script-evolution": "Script Governance",
    "reflective-validation": "Validation",
    "failure-intelligence": "Failure Intelligence",
    "validate-promote": "Promotion",
}


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _stage_summary(stages: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for stage in stages:
        item = {
            "name": stage.get("name", "unnamed_stage"),
            "type": stage.get("type", "unknown"),
        }
        if "command" in stage:
            item["command"] = stage.get("command")
        if "path" in stage:
            item["path"] = stage.get("path")
        if "loop" in stage:
            item["loop"] = stage.get("loop")
        out.append(item)
    return out


def build_loop_cards(root: Path) -> Dict[str, Any]:
    root = root.resolve()
    registry_path = root / "loops" / "nexus_loop_registry.v0.1.json"
    registry = _read_json(registry_path)
    loops = registry.get("loops", {})
    cards: List[Dict[str, Any]] = []

    for index, loop_id in enumerate(sorted(loops.keys()), start=1):
        loop = loops[loop_id]
        title = loop_id.replace("-", " ").title()
        cards.append({
            "schema": SCHEMA,
            "order": index,
            "loop_id": loop_id,
            "title": title,
            "description": loop.get("description", ""),
            "function": FUNCTIONS.get(loop_id, loop.get("description", "")),
            "operator_use": OPERATORS.get(loop_id, "Use when this named loop matches the active gate or wound."),
            "command_surface": f"python -m nexus_gate.loops.runner --root . --loop {loop_id} --intent \"<intent>\" --json",
            "powershell_surface": f".\\scripts\\nexus.ps1 meta-loop -Loop {loop_id} -Tag \"<intent>\"",
            "mutates": bool(loop.get("mutates", False)),
            "requires_human_authorization": bool(loop.get("requires_human_authorization", False)),
            "stop_on_failure": bool(loop.get("stop_on_failure", False)),
            "authority_boundary": registry.get("authority_boundary", {}),
            "claim_boundary": registry.get("claim_boundary", ""),
            "stages": _stage_summary(loop.get("stages", [])),
            "stages_summary": [f"{s.get('name')}:{s.get('type')}" for s in loop.get("stages", [])],
            "hud": {
                "card_kind": "nexus_loop",
                "display_group": DISPLAY_GROUPS.get(loop_id, "Meta Loops"),
                "primary_action": "inspect_or_run_through_governed_loop_runner",
                "human_card_ready": True,
            },
        })

    return {
        "schema": "NEXUS_LOOP_CARD_SET.v0.9.1B",
        "version": VERSION,
        "system": "NEXUS_LOOP_CARDS",
        "generated_for": "NEXUS_GATE_v0.9.1B",
        "source_registry": "loops/nexus_loop_registry.v0.1.json",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "card_count": len(cards),
        "cards": cards,
        "authority_boundary": registry.get("authority_boundary", {}),
        "claim_boundary": "Loop cards are human/HUD-readable surfaces for existing registry loops. They do not grant autonomous authority, shell authority, git write authority, memory promotion, network access, secret access, safety proof, security proof, or correctness proof.",
    }


def write_loop_cards(root: Path) -> Dict[str, Any]:
    packet = build_loop_cards(root)
    state_dir = root / "state" / "loops"
    docs_dir = root / "docs" / "runtime"
    state_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    versioned = state_dir / "nexus_loop_cards.v0.9.1B.json"
    latest = state_dir / "nexus_loop_cards_latest.json"
    versioned.write_text(json.dumps(packet, indent=2), encoding="utf-8", newline="\n")
    latest.write_text(json.dumps(packet, indent=2), encoding="utf-8", newline="\n")

    lines = [
        "# NEXUS Loop Cards",
        "",
        "NEXUS Loop Cards are HUD-ready JSON descriptions of the canonical local loop registry.",
        "They preserve the loop registry as data and present each loop as a human-readable card.",
        "",
        "Boundary: loop cards describe governed local loops. They do not grant autonomous authority, execution authority, git write authority, memory promotion, safety proof, security proof, or correctness proof.",
        "",
        "## Card Surfaces",
        "",
        "- `state/loops/nexus_loop_cards.v0.9.1B.json`",
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
            f"- Function: {card['function']}",
            f"- Operator use: {card['operator_use']}",
            f"- Command: `{card['command_surface']}`",
            f"- Human authorization required: `{str(card['requires_human_authorization']).lower()}`",
            "",
        ])
    (docs_dir / "NEXUS_LOOP_CARDS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return packet


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build NEXUS loop cards from the loop registry.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_loop_cards(Path(args.root))
    if args.json:
        print(json.dumps(packet, indent=2))
    else:
        print(f"wrote {packet['card_count']} NEXUS loop cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
