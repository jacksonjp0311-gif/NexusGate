from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.loops.orchestrator import build_orchestration_packet


ROOT = Path(__file__).resolve().parents[1]


class LoopOrchestratorV114Tests(unittest.TestCase):
    def test_orchestrator_selects_registered_loop_without_authority(self) -> None:
        packet = build_orchestration_packet(ROOT, "unit orchestration")
        self.assertEqual(packet["schema"], "NEXUS_LOOP_ORCHESTRATOR.v1.1.4")
        self.assertIn(packet["status"], {"pass", "warn", "blocked"})
        self.assertIn(packet["selected_loop"], packet["available_loops"])
        self.assertFalse(packet["authority_boundary"]["autonomous_authority"])
        self.assertFalse(packet["authority_boundary"]["arbitrary_shell_execution"])
        self.assertFalse(packet["authority_boundary"]["mutating_loop_execution"])
        self.assertIn("self_authorize", packet["blocked_actions"])
        self.assertIn("arbitrary_shell_commands", packet["blocked_actions"])

    def test_cli_writes_report_and_state(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "nexus_gate.loops.orchestrator",
                "--root",
                ".",
                "--intent",
                "unit cli orchestration",
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
        self.assertEqual(packet["schema"], "NEXUS_LOOP_ORCHESTRATOR.v1.1.4")
        self.assertTrue((ROOT / "reports" / "nexus_loop_orchestration_report_latest.json").exists())
        self.assertTrue((ROOT / "state" / "loops" / "nexus_loop_orchestration_latest.json").exists())

    def test_command_surfaces_expose_orchestrate_without_electron_authority(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        self.assertIn('"orchestrate"', ps)
        self.assertIn("Invoke-NexusLoopOrchestrator", ps)
        self.assertIn("orchestrate)", sh)
        self.assertIn('"orchestrate"', human)
        self.assertIn("nexus_gate.loops.orchestrator", human)
        self.assertIn("reports/nexus_loop_orchestration_report_latest.json", main)
        allowlist_block = main.split("const ALLOWLISTED_COMMANDS", 1)[1].split("]);", 1)[0]
        self.assertNotIn('"orchestrate"', allowlist_block)


if __name__ == "__main__":
    unittest.main()
