
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

NEW_LOOPS = {
    "repo-radar",
    "scope-hygiene",
    "claim-boundary-audit",
    "surface-map",
    "stale-surface-scan",
    "next-action-router",
    "handoff-pack",
    "dependency-preflight",
    "alignment-score",
    "boundary-scan",
    "release-brief",
    "evolution-radar",
}

class TestAILoopToolkitV093(unittest.TestCase):
    def test_registry_contains_toolkit_loops_and_commands(self):
        registry = json.loads((ROOT / "loops" / "nexus_loop_registry.v0.1.json").read_text(encoding="utf-8"))
        self.assertIn(registry["generated_for"], {"NEXUS_GATE_v0.9.3", "NEXUS_GATE_v0.9.4", "NEXUS_GATE_v0.9.5", "NEXUS_GATE_v0.9.6", "NEXUS_GATE_v0.9.7", "NEXUS_GATE_v0.9.8"})
        self.assertTrue(NEW_LOOPS.issubset(set(registry["loops"])))
        for loop_id in NEW_LOOPS:
            loop = registry["loops"][loop_id]
            self.assertTrue(loop["ai_callable"])
            self.assertFalse(loop["mutates"])
            self.assertTrue(loop["function"])
            self.assertTrue(loop["operator_use"])
        for command in ["toolkit_repo_radar", "toolkit_scope_hygiene", "toolkit_next_action", "toolkit_evolution_radar"]:
            self.assertIn(command, registry["allowed_commands"])
            self.assertFalse(registry["allowed_commands"][command]["mutates"])
        self.assertFalse(registry["authority_boundary"]["autonomous_authority"])
        self.assertFalse(registry["authority_boundary"]["git_write_enabled"])

    def test_toolkit_packets_build_without_authority(self):
        from nexus_gate.loops.toolkit import build_toolkit_packet
        for tool in ["repo-radar", "scope-hygiene", "next-action-router", "boundary-scan", "evolution-radar"]:
            packet = build_toolkit_packet(ROOT, tool, "unit")
            self.assertEqual(packet["mode"], "nexus_ai_loop_toolkit")
            self.assertEqual(packet["status"], "pass")
            self.assertFalse(packet["boundary"]["git_push_enabled"])
            self.assertFalse(packet["boundary"]["autonomous_authority"])
            self.assertIn("data", packet)

    def test_loop_cards_include_toolkit_cards(self):
        from nexus_gate.loops.cards import build_loop_cards
        packet = build_loop_cards(ROOT)
        self.assertIn(packet["schema"], {"NEXUS_LOOP_CARD_SET.v0.9.3", "NEXUS_LOOP_CARD_SET.v0.9.4","NEXUS_LOOP_CARD_SET.v0.9.5", "NEXUS_LOOP_CARD_SET.v0.9.6", "NEXUS_LOOP_CARD_SET.v0.9.7"})
        cards = {card["loop_id"]: card for card in packet["cards"]}
        self.assertTrue(NEW_LOOPS.issubset(cards))
        for loop_id in NEW_LOOPS:
            card = cards[loop_id]
            self.assertIn(card["schema"], {"NEXUS_LOOP_CARD.v0.9.3", "NEXUS_LOOP_CARD.v0.9.4","NEXUS_LOOP_CARD.v0.9.5", "NEXUS_LOOP_CARD.v0.9.6", "NEXUS_LOOP_CARD.v0.9.7"})
            self.assertTrue(card["hud"]["human_card_ready"])
            self.assertTrue(card["hud"]["ai_toolkit_ready"])
            self.assertIn("--execute --human-authorized", card["execute_surface"])

    def test_docs_readme_and_compiler_expose_toolkit(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        doc = (ROOT / "docs" / "runtime" / "NEXUS_AI_LOOP_TOOLKIT.md").read_text(encoding="utf-8")
        compiler = (ROOT / "nexus_gate" / "compiler" / "compiler.py").read_text(encoding="utf-8")
        self.assertIn("v0.9.3 AI Loop Toolkit Expansion", readme)
        self.assertIn("AI Loop Toolkit", doc)
        self.assertIn("repo-radar", compiler)
        self.assertLess(len(readme.splitlines()), 220)

if __name__ == "__main__":
    unittest.main()
