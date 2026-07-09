import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class TestAIToolbeltCockpitV097(unittest.TestCase):
    def test_toolbelt_packet_contract_has_cockpit_fields(self):
        from nexus_gate.loops.toolbelt import build_toolbelt_packet
        packet = build_toolbelt_packet(ROOT, "unit cockpit", "dashboard")
        self.assertEqual(packet["schema"], "NEXUS_AI_TOOLBELT.v0.9.7")
        self.assertEqual(packet["version"], "0.9.7")
        for key in ["recommended_next_loop", "next_command", "recommended_next_command", "chains", "groups", "boundary"]:
            self.assertIn(key, packet)
        self.assertTrue(packet["chains"])
        self.assertIn(".\\scripts\\nexus.ps1", packet["next_command"])

    def test_render_or_human_output_surface_exists(self):
        import nexus_gate.loops.toolbelt as toolbelt
        self.assertTrue(hasattr(toolbelt, "build_toolbelt_packet"))

if __name__ == "__main__":
    unittest.main()
