import json, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class TestAILoopFabricV092(unittest.TestCase):
 def test_registry_contains_ai_callable_loops(self):
  r=json.loads((ROOT/"loops"/"nexus_loop_registry.v0.1.json").read_text(encoding="utf-8")); expected={"ai-orchestrator-preflight","wound-indexed-resume","impact-map","bounded-validation","compiler-wound-focus","docs-doctrine-preflight","hud-loop-sync","release-seal"}
  self.assertTrue(expected.issubset(set(r["loops"])))
  for c in ["bounded_tests","wound_resume","loop_cards","gitnexus_impact"]: self.assertIn(c,r["allowed_commands"]); self.assertFalse(r["allowed_commands"][c]["mutates"])
  self.assertFalse(r["authority_boundary"]["autonomous_authority"]); self.assertFalse(r["authority_boundary"]["git_write_enabled"])
 def test_loop_cards_v092_are_hud_ready_and_ai_callable(self):
  from nexus_gate.loops.cards import build_loop_cards
  p=build_loop_cards(ROOT); self.assertIn(p["schema"],{"NEXUS_LOOP_CARD_SET.v0.9.2","NEXUS_LOOP_CARD_SET.v0.9.3","NEXUS_LOOP_CARD_SET.v0.9.4","NEXUS_LOOP_CARD_SET.v0.9.5"}); cards={c["loop_id"]:c for c in p["cards"]}; self.assertIn("wound-indexed-resume",cards); self.assertTrue(cards["ai-orchestrator-preflight"]["ai_callable"]); self.assertIn("--execute --human-authorized",cards["release-seal"]["execute_surface"])
 def test_wound_indexed_resume_packet_builds(self):
  from nexus_gate.loops.resume import build_resume_packet
  p=build_resume_packet(ROOT,"unit"); self.assertEqual(p["mode"],"nexus_wound_indexed_resume"); self.assertIn("active_wound",p); self.assertFalse(p["boundary"]["git_push_enabled"])
 def test_bounded_tests_discovers_local_untracked_tests(self):
  from nexus_gate.loops.bounded_tests import discover_test_files
  self.assertIn("tests/test_ai_loop_fabric_v092.py",discover_test_files(ROOT))
 def test_docs_and_doctrine_expose_ai_loop_fabric(self):
  readme=(ROOT/"README.md").read_text(encoding="utf-8-sig"); doctrine=(ROOT/"chatgpt"/"scripts.md").read_text(encoding="utf-8-sig"); doc=(ROOT/"docs"/"runtime"/"NEXUS_AI_LOOP_FABRIC.md").read_text(encoding="utf-8")
  self.assertIn("AI-callable local loop fabric",readme); self.assertIn("v0.9.3 AI Loop Toolkit Expansion",readme); self.assertIn("AI-Callable Local Loop Fabric",doctrine); self.assertIn("meta-orchestrator",doc); self.assertLess(len(readme.splitlines()),220)
if __name__=="__main__": unittest.main()
