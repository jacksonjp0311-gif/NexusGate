import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestPhiMicrodoseLoopV110(unittest.TestCase):
    def test_packet_boundary_and_autonomy(self):
        from nexus_gate.loops.phi_microdose_loop import build_phi_microdose_packet
        packet = build_phi_microdose_packet(ROOT, "unit", run_gates=False, call_model=False)
        self.assertEqual(packet["schema"], "NEXUS_PHI_MICRODOSE_LOOP.v1.1.0")
        self.assertEqual(packet["version"], "1.1.0")
        self.assertIn(packet["status"], {"pass", "warn", "wound"})
        self.assertTrue(packet["boundary"]["allowlisted_readonly_gate_execution"])
        self.assertTrue(packet["boundary"]["localhost_model_call_enabled"])
        self.assertFalse(packet["boundary"]["repo_mutation_enabled"])
        self.assertFalse(packet["boundary"]["git_push_enabled"])
        self.assertFalse(packet["boundary"]["patch_apply_enabled"])
        self.assertIn("call_local_phi_adapter", packet["autonomy_policy"]["grants"])
        self.assertIn("repo_file_mutation", packet["autonomy_policy"]["blocked"])
        self.assertFalse(packet["patch_plan"]["may_apply_without_human"])
        self.assertIn("recommended_next_gate", packet)

    def test_command_surfaces_and_registry(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn("phi-loop", ps)
        self.assertIn("phi-loop-auto", ps)
        self.assertIn("nexus_gate.loops.phi_microdose_loop", ps)
        self.assertIn("phi-loop", sh)
        self.assertIn("phi-loop-auto", sh)
        registry = json.loads((ROOT / "loops" / "nexus_loop_registry.v0.1.json").read_text(encoding="utf-8"))
        self.assertIn("phi_microdose_loop", registry["allowed_commands"])
        self.assertFalse(registry["allowed_commands"]["phi_microdose_loop"]["mutates"])
        self.assertIn("phi-microdose-loop", registry["loops"])
        self.assertFalse(registry["loops"]["phi-microdose-loop"]["mutates"])

    def test_docs_and_readme_compact(self):
        doc = (ROOT / "docs" / "runtime" / "NEXUS_PHI_MICRODOSE_LOOP.md").read_text(encoding="utf-8")
        self.assertIn("Phi Microdose Loop", doc)
        self.assertIn("no git push", doc)
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("v1.1.0 Phi Microdose Loop", readme)
        self.assertIn("Phi Wound Advisor", readme)
        self.assertIn("Ollama", readme)
        self.assertLess(len(readme.splitlines()), 220)


if __name__ == "__main__":
    unittest.main()
