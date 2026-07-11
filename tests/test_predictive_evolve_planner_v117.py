from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.loops.predictive_evolve import build_predictive_evolve_plan


ROOT = Path(__file__).resolve().parents[1]


class PredictiveEvolvePlannerTests(unittest.TestCase):
    def test_plan_is_dry_run_and_requires_final_evolve(self) -> None:
        packet = build_predictive_evolve_plan(ROOT, max_runs=4)
        self.assertEqual(packet["schema"], "NEXUS_PREDICTIVE_EVOLVE_PLAN.v1.1.7")
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertTrue(packet["dry_run"])
        self.assertTrue(packet["final_evolve_required_before_commit"])
        commands = [step["command"] for step in packet["recommended_plan"]]
        self.assertIn(".\\scripts\\nexus.ps1 predictive-timing", commands)
        self.assertEqual(commands[-1], ".\\scripts\\nexus.ps1 evolve")
        self.assertEqual(len(commands), len(set(commands)))
        self.assertIn("self_authorize", packet["blocked_actions"])
        self.assertIn("skip_final_evolve_before_commit", packet["blocked_actions"])
        self.assertFalse(packet["authority_boundary"]["execute_plan"])
        self.assertFalse(packet["authority_boundary"]["repo_mutation"])
        self.assertIn("dry-run planning surface only", packet["claim_boundary"])

    def test_cli_writes_report_and_state(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "nexus_gate.loops.predictive_evolve",
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
        self.assertEqual(packet["schema"], "NEXUS_PREDICTIVE_EVOLVE_PLAN.v1.1.7")
        self.assertTrue((ROOT / "reports" / "nexus_predictive_evolve_plan_latest.json").exists())
        self.assertTrue((ROOT / "state" / "loops" / "nexus_predictive_evolve_plan_latest.json").exists())

    def test_command_surfaces_expose_predictive_evolve(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn('"predictive-evolve"', ps)
        self.assertIn("nexus_gate.loops.predictive_evolve", ps)
        self.assertIn("predictive-evolve)", sh)
        self.assertIn("nexus_gate.loops.predictive_evolve", sh)

    def test_docs_and_cards_record_predictive_evolve(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        algorithm_doc = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8-sig")
        runtime_doc = (ROOT / "docs" / "runtime" / "NEXUS_PREDICTIVE_EVOLVE.md").read_text(encoding="utf-8-sig")
        codex_doc = (ROOT / "docs" / "codex" / "CODEX_ORCHESTRATION_PROTOCOL.md").read_text(encoding="utf-8-sig")
        self.assertIn("predictive-evolve", readme)
        self.assertIn("Predictive Evolve Planner Algorithm", algorithm_doc)
        self.assertIn("final evolve seal required", runtime_doc)
        self.assertIn(".\\scripts\\nexus.ps1 predictive-evolve", codex_doc)


if __name__ == "__main__":
    unittest.main()
