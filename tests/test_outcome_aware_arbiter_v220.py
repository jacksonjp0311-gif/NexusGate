from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.outcomes.learn import build_outcome_report


ROOT = Path(__file__).resolve().parents[1]


class OutcomeAwareArbiterV220Tests(unittest.TestCase):
    def test_outcome_report_compiles_without_authority(self) -> None:
        packet = build_outcome_report(ROOT, intent="test outcome", record=False)
        self.assertIn(packet["schema"], {"NEXUS_RECOMMENDATION_OUTCOME_LEARNER.v2.2.0", "NEXUS_RECOMMENDATION_OUTCOME_LEARNER.v2.6.3"})
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertIn("latest_outcome", packet)
        self.assertIn("calibration", packet)
        self.assertIn("pressure_memory", packet)
        self.assertIn("route_fitness", packet["latest_outcome"])
        self.assertIn("execute_recommendation", packet["blocked_actions"])
        self.assertIn("does not prove", packet["claim_boundary"])

    def test_outcome_cli_writes_report_and_state(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "nexus_gate.outcomes.learn", "--root", ".", "--json", "--no-record"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertIn(packet["schema"], {"NEXUS_RECOMMENDATION_OUTCOME_LEARNER.v2.2.0", "NEXUS_RECOMMENDATION_OUTCOME_LEARNER.v2.6.3"})
        self.assertTrue((ROOT / "reports" / "nexus_recommendation_outcome_latest.json").exists())
        self.assertTrue((ROOT / "state" / "coherence" / "arbiter_calibration_latest.json").exists())
        self.assertTrue((ROOT / "state" / "coherence" / "pressure_memory_latest.json").exists())

    def test_command_surfaces_expose_outcome_learn(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn('"outcome-learn"', ps)
        self.assertIn("nexus_gate.outcomes.learn", ps)
        self.assertIn("outcome-learn)", sh)
        self.assertIn("nexus_gate.outcomes.learn", sh)
        self.assertIn('"outcome-learn"', human)
        self.assertIn("16i_outcome_learner", human)
        self.assertIn("outcome-learn", readme)
        self.assertIn("runtime-hygiene", readme)


if __name__ == "__main__":
    unittest.main()
