import json, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
NEW={"toolbelt-console","toolbelt-next","toolbelt-process","toolbelt-ship-console"}
class TestAIToolbeltConsoleV096(unittest.TestCase):
 def test_registry_commands(self):
  r=json.loads((ROOT/"loops"/"nexus_loop_registry.v0.1.json").read_text(encoding="utf-8-sig")); self.assertIn(r["generated_for"], {"NEXUS_GATE_v0.9.6","NEXUS_GATE_v0.9.7"}); self.assertTrue(NEW.issubset(set(r["loops"])))
  for c in ["toolbelt_console","toolbelt_next","toolbelt_start","toolbelt_ship"]: self.assertIn(c,r["allowed_commands"]); self.assertFalse(r["allowed_commands"][c]["mutates"])
  for l in NEW: self.assertTrue(r["loops"][l]["ai_callable"]); self.assertFalse(r["loops"][l]["mutates"]); self.assertTrue(r["loops"][l]["local_only"])
 def test_packet(self):
  from nexus_gate.loops.toolbelt import build_toolbelt_packet
  p=build_toolbelt_packet(ROOT,"unit","dashboard"); self.assertIn(p["schema"], {"NEXUS_AI_TOOLBELT.v0.9.6","NEXUS_AI_TOOLBELT.v0.9.7"}); self.assertEqual(p["view"],"dashboard"); self.assertIn("recommended_next_loop",p); self.assertIn("process_chains",p); self.assertFalse(p["boundary"]["autonomous_authority"])
 def test_cards(self):
  from nexus_gate.loops.cards import build_loop_cards
  p=build_loop_cards(ROOT); self.assertIn(p["schema"], {"NEXUS_LOOP_CARD_SET.v0.9.6","NEXUS_LOOP_CARD_SET.v0.9.7"}); cards={c["loop_id"]:c for c in p["cards"]}; self.assertTrue(NEW.issubset(cards)); self.assertIn(cards["toolbelt-console"]["schema"], {"NEXUS_LOOP_CARD.v0.9.6","NEXUS_LOOP_CARD.v0.9.7"})
 def test_shells_and_docs(self):
  ps=(ROOT/"scripts"/"nexus.ps1").read_text(encoding="utf-8-sig"); sh=(ROOT/"scripts"/"nexus.sh").read_text(encoding="utf-8-sig"); readme=(ROOT/"README.md").read_text(encoding="utf-8-sig"); doc=(ROOT/"docs"/"runtime"/"NEXUS_TOOLBELT_CONSOLE.md").read_text(encoding="utf-8")
  self.assertIn('"toolbelt"',ps); self.assertIn("function Invoke-NexusToolbelt",ps); self.assertIn("toolbelt|toolbelt-dashboard",sh); self.assertIn("AI Toolbelt Console",readme); self.assertIn("Toolbelt Console",doc); self.assertLess(len(readme.splitlines()),220)
if __name__=="__main__": unittest.main()
