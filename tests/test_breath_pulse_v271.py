from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from nexus_gate.breath.pulse import build_breath_packet, write_breath_packet


class BreathPulseV271Tests(unittest.TestCase):
    def test_packet_contains_bounded_breath_contract(self) -> None:
        packet = build_breath_packet(Path.cwd())
        self.assertEqual(packet["schema"], "NEXUS_BREATH_PULSE.v2.8.0")
        self.assertIn(packet["breath"]["phase"], {"inhale", "hold", "exhale"})
        self.assertIn("recommended_next_command", packet["breath"])
        self.assertIn("treat_breath_as_evolve_pass", packet["blocked_actions"])
        self.assertIn("does not execute commands", packet["claim_boundary"])

    def test_write_breath_packet_creates_report_and_state_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet = write_breath_packet(root)
            report = root / "reports" / "nexus_breath_pulse_latest.json"
            state = root / "state" / "breath" / "nexus_breath_pulse_latest.json"
            self.assertTrue(report.exists())
            self.assertTrue(state.exists())
            self.assertEqual(json.loads(report.read_text(encoding="utf-8"))["schema"], packet["schema"])
            self.assertEqual(json.loads(state.read_text(encoding="utf-8"))["version"], "2.8.0")


if __name__ == "__main__":
    unittest.main()
