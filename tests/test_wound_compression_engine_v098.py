
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestWoundCompressionEngineV098(unittest.TestCase):
    def test_packet_contract_is_read_only_and_file_truth_based(self):
        from nexus_gate.loops.wound_compression import build_wound_compression_packet
        packet = build_wound_compression_packet(ROOT, "unit")
        self.assertEqual(packet["schema"], "NEXUS_WOUND_COMPRESSION.v0.9.8")
        self.assertEqual(packet["version"], "0.9.8", "0.9.9")
        self.assertIn(packet["status"], {"pass", "wound"})
        self.assertIn("active_wound", packet)
        self.assertIn("active_wound_key", packet)
        self.assertIn("recommended_next_loop", packet)
        self.assertIn("recommended_next_command", packet)
        self.assertEqual(packet["truth_rule"]["stdout"], "smoke_only")
        self.assertEqual(packet["truth_rule"]["tail"], "never_truth")
        self.assertFalse(packet["boundary"]["autonomous_authority"])
        self.assertFalse(packet["boundary"]["git_push_enabled"])

    def test_registry_scripts_and_docs_expose_wound_compression(self):
        registry = json.loads((ROOT / "loops" / "nexus_loop_registry.v0.1.json").read_text(encoding="utf-8"))
        self.assertIn(registry["generated_for"], {"NEXUS_GATE_v0.9.8", "NEXUS_GATE_v0.9.9"})
        self.assertIn("wound_compress", registry["allowed_commands"])
        self.assertFalse(registry["allowed_commands"]["wound_compress"]["mutates"])
        self.assertIn("wound-compression-engine", registry["loops"])
        self.assertFalse(registry["loops"]["wound-compression-engine"]["mutates"])
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn("wound-compress", ps)
        self.assertIn("wound-compress", sh)
        self.assertIn("nexus_gate.loops.wound_compression", ps)
        self.assertIn("nexus_gate.loops.wound_compression", sh)

    def test_readme_and_doc_surface_v098(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        doc = (ROOT / "docs" / "runtime" / "NEXUS_WOUND_COMPRESSION_ENGINE.md").read_text(encoding="utf-8")
        self.assertIn("v0.9.8 Wound Compression Engine", readme)
        self.assertIn("Wound Compression Engine", doc)
        self.assertIn("stdout = smoke only", doc)
        self.assertIn("files = evidence", doc)
        self.assertLess(len(readme.splitlines()), 220)


if __name__ == "__main__":
    unittest.main()
