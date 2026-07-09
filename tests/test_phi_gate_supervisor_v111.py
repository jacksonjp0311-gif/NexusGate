from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nexus_gate.loops import phi_gate_supervisor as supervisor
from nexus_gate.loops import phi_gate_supervisor_compile as compiler


class TestPhiGateSupervisorV111(unittest.TestCase):
    def test_detects_readme_compactness_wound(self):
        wound = supervisor.detect_wound("AssertionError: 220 not less than 220")
        self.assertEqual(wound["wound_key"], "readme_compactness_regression")
        self.assertEqual(wound["repair_lane"], "compact_readme_without_removing_required_markers")

    def test_allowed_repairs_are_bounded(self):
        self.assertIn("loop_registry_card_packet_drift", supervisor.ALLOWED_REPAIR_LANES)
        self.assertIn("readme_compactness_regression", supervisor.ALLOWED_REPAIR_LANES)
        self.assertFalse(supervisor.AUTHORITY_BOUNDARY["git_push_enabled"])
        self.assertFalse(supervisor.AUTHORITY_BOUNDARY["secrets_enabled"])
        self.assertTrue(supervisor.AUTHORITY_BOUNDARY["deterministic_allowlisted_repairs_only"])

    def test_supervisor_compiler_passes_current_contract(self):
        packet = compiler.compile_report(Path("."))
        self.assertEqual(packet["status"], "pass")
        self.assertIn("allowed_repair_lanes", packet)
        self.assertIn("claim_boundary", packet)

    def test_command_surfaces_use_current_flags(self):
        for path in [
            Path("scripts/nexus.ps1"),
            Path("scripts/nexus.sh"),
            Path("loops/nexus_loop_registry.v0.1.json"),
            Path("state/loops/nexus_loop_registry.v0.1.json"),
        ]:
            text = path.read_text(encoding="utf-8-sig")
            self.assertNotIn("--self-heal", text)
            self.assertNotIn("--call-phi", text)
        self.assertIn("--auto-repair", Path("scripts/nexus.ps1").read_text(encoding="utf-8-sig"))
        self.assertIn("--call-model", Path("scripts/nexus.ps1").read_text(encoding="utf-8-sig"))

    def test_compact_readme_preserves_loop_card_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lines = ["# README", "", "Nexus Loops / Cards", "", "NEXUS Loop Cards"]
            while len(lines) < 221:
                lines.append("")
            (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            packet = supervisor.compact_readme(root)
            text = (root / "README.md").read_text(encoding="utf-8")
            self.assertLess(len(text.splitlines()), 220)
            self.assertIn("Nexus Loops / Cards", text)
            self.assertIn("NEXUS Loop Cards", text)
            self.assertGreaterEqual(packet["removed_blank_lines"], 1)


if __name__ == "__main__":
    unittest.main()
