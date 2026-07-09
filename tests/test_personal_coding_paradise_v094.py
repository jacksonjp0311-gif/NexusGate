import json
import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
PARADISE_LOOPS = {"idea-forge","architecture-sketch","patch-plan","test-strategy","debug-lens","refactor-map","ui-polish","performance-scout","docs-weaver","memory-anchor","command-palette","session-brief","commit-story","risk-register","paradise-index","code-garden-map","friction-detector","local-oracle","pair-programming-brief","continuity-seal","paradise-preflight","creative-build-chain","debug-recovery-chain","safe-ship-chain"}
class TestPersonalCodingParadiseV094(unittest.TestCase):
    def test_registry_contains_paradise_loops(self):
        registry=json.loads((ROOT/"loops/nexus_loop_registry.v0.1.json").read_text(encoding="utf-8")); self.assertIn(registry["generated_for"], {"NEXUS_GATE_v0.9.4", "NEXUS_GATE_v0.9.5", "NEXUS_GATE_v0.9.6", "NEXUS_GATE_v0.9.7", "NEXUS_GATE_v0.9.8"}); self.assertTrue(PARADISE_LOOPS.issubset(set(registry["loops"]))); self.assertFalse(registry["authority_boundary"]["autonomous_authority"]); self.assertFalse(registry["authority_boundary"]["git_write_enabled"])
        for loop_id in PARADISE_LOOPS:
            loop=registry["loops"][loop_id]; self.assertTrue(loop["ai_callable"]); self.assertFalse(loop["mutates"]); self.assertTrue(loop["function"]); self.assertTrue(loop["operator_use"])
    def test_toolkit_packets_build_for_paradise_tools(self):
        from nexus_gate.loops.toolkit import build_toolkit_packet
        for tool in ["idea-forge","patch-plan","debug-lens","command-palette","local-oracle","continuity-seal"]:
            packet=build_toolkit_packet(ROOT,tool,"unit"); self.assertEqual(packet["mode"],"nexus_ai_loop_toolkit"); self.assertIn(packet["version"], {"0.9.4", "0.9.5", "0.9.6", "0.9.7"}); self.assertEqual(packet["status"],"pass"); self.assertFalse(packet["boundary"]["git_push_enabled"]); self.assertFalse(packet["boundary"]["autonomous_authority"]); self.assertIn("data",packet)
    def test_loop_cards_include_paradise_cards(self):
        from nexus_gate.loops.cards import build_loop_cards
        packet=build_loop_cards(ROOT); self.assertIn(packet["schema"], {"NEXUS_LOOP_CARD_SET.v0.9.2", "NEXUS_LOOP_CARD_SET.v0.9.3", "NEXUS_LOOP_CARD_SET.v0.9.4", "NEXUS_LOOP_CARD_SET.v0.9.5", "NEXUS_LOOP_CARD_SET.v0.9.6", "NEXUS_LOOP_CARD_SET.v0.9.7"}); cards={card["loop_id"]:card for card in packet["cards"]}; self.assertTrue(PARADISE_LOOPS.issubset(cards))
        for loop_id in ["idea-forge","debug-recovery-chain","safe-ship-chain","continuity-seal"]:
            card=cards[loop_id]; self.assertIn(card["schema"], {"NEXUS_LOOP_CARD.v0.9.2", "NEXUS_LOOP_CARD.v0.9.3", "NEXUS_LOOP_CARD.v0.9.4", "NEXUS_LOOP_CARD.v0.9.5", "NEXUS_LOOP_CARD.v0.9.6", "NEXUS_LOOP_CARD.v0.9.7"}); self.assertTrue(card["hud"]["human_card_ready"]); self.assertTrue(card["hud"]["ai_toolkit_ready"]); self.assertIn("--execute --human-authorized",card["execute_surface"])
    def test_docs_readme_and_compiler_expose_paradise(self):
        readme=(ROOT/"README.md").read_text(encoding="utf-8-sig"); doc=(ROOT/"docs/runtime/NEXUS_PERSONAL_CODING_PARADISE.md").read_text(encoding="utf-8"); compiler=(ROOT/"nexus_gate/compiler/compiler.py").read_text(encoding="utf-8"); self.assertIn("v0.9.4 Personal Coding Paradise",readme); self.assertIn("Personal Coding Paradise",doc); self.assertIn("idea-forge",compiler); self.assertLess(len(readme.splitlines()),220)
if __name__=="__main__": unittest.main()
