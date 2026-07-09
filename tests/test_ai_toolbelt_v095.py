
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLBELT_LOOPS = {"toolbelt-index", "toolbelt-start", "toolbelt-dashboard", "toolbelt-ship"}

class TestAIToolbeltV095(unittest.TestCase):
    def test_registry_contains_toolbelt_loops_and_command(self):
        registry = json.loads((ROOT / "loops" / "nexus_loop_registry.v0.1.json").read_text(encoding="utf-8"))
        self.assertIn(registry["generated_for"], {"NEXUS_GATE_v0.9.5", "NEXUS_GATE_v0.9.6", "NEXUS_GATE_v0.9.7"})
        self.assertTrue(TOOLBELT_LOOPS.issubset(set(registry["loops"])))
        self.assertIn("toolbelt_index", registry["allowed_commands"])
        self.assertFalse(registry["allowed_commands"]["toolbelt_index"]["mutates"])
        for loop_id in TOOLBELT_LOOPS:
            loop = registry["loops"][loop_id]
            self.assertTrue(loop["ai_callable"])
            self.assertFalse(loop["mutates"])
            self.assertTrue(loop["function"])
            self.assertTrue(loop["operator_use"])
        self.assertFalse(registry["authority_boundary"]["autonomous_authority"])
        self.assertFalse(registry["authority_boundary"]["git_write_enabled"])

    def test_toolbelt_packet_builds_and_writes_surfaces(self):
        from nexus_gate.loops.toolbelt import build_toolbelt_packet, write_toolbelt
        packet = build_toolbelt_packet(ROOT, "unit")
        self.assertIn(packet["schema"], {"NEXUS_AI_TOOLBELT.v0.9.5", "NEXUS_AI_TOOLBELT.v0.9.6", "NEXUS_AI_TOOLBELT.v0.9.7"})
        self.assertEqual(packet["mode"], "nexus_ai_toolbelt")
        self.assertFalse(packet["boundary"]["git_push_enabled"])
        self.assertFalse(packet["boundary"]["autonomous_authority"])
        self.assertGreaterEqual(packet["toolbelt_group_count"], 6)
        written = write_toolbelt(ROOT, "unit")
        self.assertIn(written["version"], {"0.9.5", "0.9.6", "0.9.7"})
        self.assertTrue((ROOT / "state" / "loops" / "nexus_toolbelt_latest.json").exists())
        self.assertTrue((ROOT / "docs" / "runtime" / "NEXUS_AI_TOOLBELT.md").exists())

    def test_loop_cards_include_toolbelt_cards(self):
        from nexus_gate.loops.cards import build_loop_cards
        packet = build_loop_cards(ROOT)
        self.assertIn(packet["schema"], {"NEXUS_LOOP_CARD_SET.v0.9.5", "NEXUS_LOOP_CARD_SET.v0.9.6", "NEXUS_LOOP_CARD_SET.v0.9.7"})
        cards = {card["loop_id"]: card for card in packet["cards"]}
        self.assertTrue(TOOLBELT_LOOPS.issubset(cards))
        for loop_id in TOOLBELT_LOOPS:
            card = cards[loop_id]
            self.assertIn(card["schema"], {"NEXUS_LOOP_CARD.v0.9.5", "NEXUS_LOOP_CARD.v0.9.6", "NEXUS_LOOP_CARD.v0.9.7"})
            self.assertTrue(card["hud"]["human_card_ready"])
            self.assertIn("--execute --human-authorized", card["execute_surface"])

    def test_readme_has_toolbelt_section(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("## AI Toolbelt", readme)
        self.assertIn("toolbelt-start", readme)
        self.assertIn("toolbelt-dashboard", readme)
        self.assertTrue(any(token in readme for token in ["v0.9.5 AI Toolbelt Surface", "v0.9.6 Toolbelt Console Integration", "AI Toolbelt Console", "Toolbelt Cockpit Output", "Toolbelt Cockpit Output"]))
        self.assertLess(len(readme.splitlines()), 220)

    def test_compiler_exposes_toolbelt_visibility(self):
        compiler = (ROOT / "nexus_gate" / "compiler" / "compiler.py").read_text(encoding="utf-8")
        self.assertTrue(any(token in compiler for token in ["v0.9.5", "v0.9.6", "v0.9.7"]))
        self.assertIn("NEXUS_AI_TOOLBELT.md", compiler)
        self.assertIn("toolbelt-index", compiler)

if __name__ == "__main__":
    unittest.main()
