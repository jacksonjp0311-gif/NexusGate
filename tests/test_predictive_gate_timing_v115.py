from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.loops.predictive_timing import build_predictive_timing_packet


ROOT = Path(__file__).resolve().parents[1]


class PredictiveGateTimingTests(unittest.TestCase):
    def test_packet_is_recommendation_only(self) -> None:
        packet = build_predictive_timing_packet(ROOT, max_runs=4)
        self.assertEqual(packet["schema"], "NEXUS_PREDICTIVE_GATE_TIMING.v1.1.5")
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertIn("step_analysis", packet)
        self.assertIn("runtime_pressure", packet)
        self.assertIn("recommendation", packet)
        self.assertTrue(packet["authority_boundary"]["recommendation_only"])
        self.assertFalse(packet["authority_boundary"]["autonomous_timeout_extension"])
        self.assertFalse(packet["authority_boundary"]["bypass_gates"])
        self.assertIn("self_authorize", packet["blocked_actions"])
        self.assertIn("bypass_gates", packet["blocked_actions"])
        self.assertIn("local development evidence only", packet["claim_boundary"])

    def test_cli_writes_report_and_state(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "nexus_gate.loops.predictive_timing",
                "--root",
                ".",
                "--max-runs",
                "4",
                "--json",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertEqual(packet["schema"], "NEXUS_PREDICTIVE_GATE_TIMING.v1.1.5")
        self.assertTrue((ROOT / "reports" / "nexus_predictive_gate_timing_latest.json").exists())
        self.assertTrue((ROOT / "state" / "loops" / "nexus_predictive_gate_timing_latest.json").exists())

    def test_command_surfaces_expose_predictive_timing(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('"predictive-timing"', ps)
        self.assertIn("nexus_gate.loops.predictive_timing", ps)
        self.assertIn("predictive-timing)", sh)
        self.assertIn('"predictive-timing"', human)
        self.assertIn("16d_predictive_timing.json", human)
        self.assertLess(human.index("16c_loop_orchestrator"), human.index("16d_predictive_timing"))
        self.assertLess(human.index("16d_predictive_timing"), human.index("17_pack_compiler"))

    def test_meta_orchestrator_reads_predictive_timing(self) -> None:
        meta = (ROOT / "nexus_gate" / "loops" / "meta_orchestrator_gate.py").read_text(encoding="utf-8-sig")
        self.assertIn("reports/nexus_predictive_gate_timing_latest.json", meta)
        self.assertIn("predictive_timing", meta)
        self.assertIn("Predictive Timing", meta)
        self.assertIn("predictive-gate-timing", meta)

    def test_readme_records_priority(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("Predictive Gate Timing / Runtime Pressure Model is a priority", text)
        self.assertIn("baseline -> drift -> anomaly -> recommended next timeout", text)


if __name__ == "__main__":
    unittest.main()
