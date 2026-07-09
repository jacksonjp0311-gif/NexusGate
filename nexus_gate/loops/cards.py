from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.9.7"
SCHEMA = "NEXUS_LOOP_CARD.v0.9.7"

def _stage_summary(stages):
    out = []
    for stage in stages:
        item = {"name": stage.get("name", "unnamed"), "type": stage.get("type", "unknown")}
        for key in ["command", "path", "loop"]:
            if key in stage:
                item[key] = stage[key]
        out.append(item)
    return out

def build_loop_cards(root):
    root = Path(root).resolve()
    registry = json.loads((root / "loops/nexus_loop_registry.v0.1.json").read_text(encoding="utf-8-sig"))
    cards = []
    for order, loop_id in enumerate(sorted(registry.get("loops", {})), 1):
        loop = registry["loops"][loop_id]
        cards.append({
            "schema": SCHEMA,
            "order": order,
            "loop_id": loop_id,
            "title": loop.get("title") or loop_id.replace("-", " ").title(),
            "description": loop.get("description", ""),
            "function": loop.get("function") or loop.get("description", ""),
            "operator_use": loop.get("operator_use", "Use when this loop matches the active gate, wound, or validation need."),
            "command_surface": f'python -m nexus_gate.loops.runner --root . --loop {loop_id} --intent "<intent>" --json',
            "execute_surface": f'python -m nexus_gate.loops.runner --root . --loop {loop_id} --intent "<intent>" --execute --human-authorized --json',
            "powershell_surface": f'.\\scripts\\nexus.ps1 meta-loop -Loop {loop_id} -Tag "<intent>"',
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
                "display_group": loop.get("display_group", "Meta Loops"),
                "primary_action": "inspect_or_run_through_governed_loop_runner",
                "human_card_ready": True,
                "ai_toolkit_ready": bool(loop.get("ai_callable", True)),
                "coding_paradise_ready": loop.get("display_group") in {"Coding Paradise", "Creative", "Design", "Debug", "Continuity", "Operator Tools"},
            },
        })
    return {
        "schema": "NEXUS_LOOP_CARD_SET.v0.9.7",
        "version": VERSION,
        "system": "NEXUS_LOOP_CARDS",
        "generated_for": "NEXUS_GATE_v0.9.7",
        "source_registry": "loops/nexus_loop_registry.v0.1.json",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "card_count": len(cards),
        "cards": cards,
        "authority_boundary": registry.get("authority_boundary", {}),
        "claim_boundary": "Loop cards are HUD-readable surfaces. They grant no authority.",
    }

def write_loop_cards(root):
    root = Path(root).resolve()
    packet = build_loop_cards(root)
    (root / "state/loops").mkdir(parents=True, exist_ok=True)
    (root / "docs/runtime").mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    (root / "state/loops/nexus_loop_cards.v0.9.7.json").write_text(encoded, encoding="utf-8")
    (root / "state/loops/nexus_loop_cards_latest.json").write_text(encoded, encoding="utf-8")
    lines = ["# NEXUS Loop Cards", "", "NEXUS Loop Cards are HUD-ready JSON descriptions of the canonical local loop registry.", "v0.9.7 includes Toolbelt Cockpit and Toolbelt JSON Packet cards.", "", "Boundary: cards describe governed local loops. They do not grant autonomous authority, execution authority, git write authority, memory promotion, safety proof, security proof, or correctness proof.", "", "## Card Surfaces", "", "- `state/loops/nexus_loop_cards.v0.9.7.json`", "- `state/loops/nexus_loop_cards_latest.json`", "- `python -m nexus_gate.loops.cards --root . --json`", "", "## Cards", ""]
    for card in packet["cards"]:
        lines += [f"### {card['title']}", "", f"- Loop: `{card['loop_id']}`", f"- Group: `{card['hud']['display_group']}`", f"- Function: {card['function']}", f"- Command: `{card['command_surface']}`", ""]
    (root / "docs/runtime/NEXUS_LOOP_CARDS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return packet

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_loop_cards(Path(args.root))
    print(json.dumps(packet, indent=2, sort_keys=True) if args.json else f"wrote {packet['card_count']} NEXUS loop cards")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
