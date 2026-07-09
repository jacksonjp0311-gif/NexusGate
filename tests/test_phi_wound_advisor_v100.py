import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestPhiWoundAdvisorV100(unittest.TestCase):
    def test_packet_is_read_only_microdose_and_chat_separate(self):
        from nexus_gate.loops.phi_wound_advisor import build_phi_wound_advisor_packet
        packet = build_phi_wound_advisor_packet(ROOT, "unit", call_model=False)
        self.assertEqual(packet["schema"], "NEXUS_PHI_WOUND_ADVISOR.v1.0.0")
        self.assertEqual(packet["version"], "1.0.0")
        self.assertEqual(packet["mode"], "nexus_phi_wound_advisor")
        self.assertIn(packet["status"], {"advice", "model_unavailable"})
        self.assertTrue(packet["model_channel"]["separate_from_chat"])
        self.assertTrue(packet["model_channel"]["microdose"])
        self.assertEqual(packet["model_channel"]["model_status"], "not_requested")
        self.assertFalse(packet["boundary"]["autonomous_authority"])
        self.assertFalse(packet["boundary"]["git_push_enabled"])
        self.assertFalse(packet["boundary"]["patch_apply_enabled"])
        self.assertTrue(packet["self_heal_policy"]["human_authorization_required"])
        self.assertIn("advice", packet)
        self.assertIn("repair_surface", packet["advice"])

    def test_registry_scripts_and_docs_expose_phi_wound_advisor(self):
        registry = json.loads((ROOT / "loops" / "nexus_loop_registry.v0.1.json").read_text(encoding="utf-8"))
        self.assertIn("phi_wound_advisor", registry["allowed_commands"])
        self.assertIn("phi_wound_gpu", registry["allowed_commands"])
        self.assertFalse(registry["allowed_commands"]["phi_wound_advisor"]["mutates"])
        self.assertFalse(registry["allowed_commands"]["phi_wound_gpu"]["mutates"])
        self.assertIn("phi-wound-advisor", registry["loops"])
        self.assertFalse(registry["loops"]["phi-wound-advisor"]["mutates"])
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn("phi-wound", ps)
        self.assertIn("phi-wound-gpu", ps)
        self.assertIn("phi-wound", sh)
        self.assertIn("phi-wound-gpu", sh)
        self.assertIn("nexus_gate.loops.phi_wound_advisor", ps)
        self.assertIn("nexus_gate.loops.phi_wound_advisor", sh)
        doc = (ROOT / "docs" / "runtime" / "NEXUS_PHI_WOUND_ADVISOR.md").read_text(encoding="utf-8")
        self.assertIn("Phi Wound Advisor", doc)
        self.assertIn("Phi recommends. NexusGate verifies. Human authorizes durable mutation.", doc)

    def test_readme_exposes_v100_without_breaking_compactness(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("v1.0.0 Phi Wound Advisor", readme)
        self.assertIn("phi-wound", readme)
        self.assertLess(len(readme.splitlines()), 220)


if __name__ == "__main__":
    unittest.main()
