import json
import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
class TestLoopCardsPortalV091B(unittest.TestCase):
    def test_loop_cards_match_registry(self):
        registry=json.loads((ROOT/"loops/nexus_loop_registry.v0.1.json").read_text(encoding="utf-8")); packet=json.loads((ROOT/"state/loops/nexus_loop_cards_latest.json").read_text(encoding="utf-8")); self.assertEqual({c["loop_id"] for c in packet["cards"]}, set(registry["loops"].keys())); self.assertIn(packet["schema"], {"NEXUS_LOOP_CARD_SET.v0.9.1B","NEXUS_LOOP_CARD_SET.v0.9.2","NEXUS_LOOP_CARD_SET.v0.9.3"}); self.assertEqual(packet["card_count"], len(registry["loops"]))
    def test_each_loop_card_is_hud_ready(self):
        packet=json.loads((ROOT/"state/loops/nexus_loop_cards_latest.json").read_text(encoding="utf-8"))
        for card in packet["cards"]:
            for key in ["schema","loop_id","title","description","function","operator_use","command_surface","authority_boundary","hud"]: self.assertIn(key, card)
            self.assertIn(card["schema"], {"NEXUS_LOOP_CARD.v0.9.1B","NEXUS_LOOP_CARD.v0.9.2","NEXUS_LOOP_CARD.v0.9.3"}); self.assertIn("python -m nexus_gate.loops.runner", card["command_surface"]); self.assertEqual(card["hud"]["card_kind"], "nexus_loop"); self.assertTrue(card["hud"]["human_card_ready"]); self.assertFalse(card["authority_boundary"]["autonomous_authority"]); self.assertFalse(card["authority_boundary"]["git_write_enabled"])
    def test_portal_exposes_loop_cards(self):
        portal=(ROOT/"scripts/desktop/open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig"); self.assertIn("Invoke-NexusLoopCardsConsole",portal); self.assertIn("Nexus Loops / Cards",portal); self.assertIn("state\\loops\\nexus_loop_cards_latest.json",portal); self.assertIn('$choice -eq "14"',portal)
    def test_readme_and_chatgpt_doctrine_expose_loop_cards(self):
        readme=(ROOT/"README.md").read_text(encoding="utf-8-sig"); doctrine=(ROOT/"chatgpt/scripts.md").read_text(encoding="utf-8-sig"); self.assertIn("Nexus Loops / Cards",readme); self.assertIn("NEXUS Loop Cards",readme); self.assertLess(len(readme.splitlines()),220); self.assertIn("Loop Cards and Portal Preservation",doctrine); self.assertIn("state/loops/nexus_loop_cards_latest.json",doctrine)
    def test_loop_cards_module_imports_and_builds(self):
        from nexus_gate.loops.cards import build_loop_cards
        packet=build_loop_cards(ROOT); self.assertGreaterEqual(packet["card_count"],5); self.assertIn("claim_boundary",packet)
if __name__ == "__main__": unittest.main()
