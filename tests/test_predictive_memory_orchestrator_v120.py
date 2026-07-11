from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.loops.predictive_memory_orchestrator import build_predictive_memory_orchestrator


ROOT = Path(__file__).resolve().parents[1]


class PredictiveMemoryOrchestratorTests(unittest.TestCase):
    def test_packet_fuses_cortex_cards_and_predictive_plan(self) -> None:
        packet = build_predictive_memory_orchestrator(ROOT, "test", max_runs=4)
        self.assertEqual(packet["schema"], "NEXUS_PREDICTIVE_MEMORY_ORCHESTRATOR.v1.2.0")
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertIn("cortex_memory", packet)
        self.assertIn("card_memory", packet)
        self.assertIn("predictive_evolve", packet)
        self.assertIn("recommendation", packet)
        self.assertTrue(packet["authority_boundary"]["recommendation_only"])
        self.assertFalse(packet["authority_boundary"]["execute_plan"])
        self.assertFalse(packet["authority_boundary"]["repo_mutation"])
        self.assertTrue(packet["authority_boundary"]["final_evolve_required_before_commit"])
        self.assertIn("self_authorize", packet["blocked_actions"])
        self.assertIn("autonomous_memory_promotion", packet["blocked_actions"])

    def test_cli_writes_report_state_and_trend_ledger(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "nexus_gate.loops.predictive_memory_orchestrator",
                "--root",
                ".",
                "--intent",
                "test",
                "--max-runs",
                "4",
                "--json",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=90,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertEqual(packet["schema"], "NEXUS_PREDICTIVE_MEMORY_ORCHESTRATOR.v1.2.0")
        self.assertTrue((ROOT / "reports" / "nexus_predictive_memory_orchestrator_latest.json").exists())
        self.assertTrue((ROOT / "state" / "loops" / "nexus_predictive_memory_orchestrator_latest.json").exists())
        self.assertTrue((ROOT / "ledger" / "cortex_benchmark_trends.jsonl").exists())

    def test_command_surfaces_and_evolve_chain_expose_predictive_memory(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn('"predictive-memory"', ps)
        self.assertIn("nexus_gate.loops.predictive_memory_orchestrator", ps)
        self.assertIn('"predictive-memory"', human)
        self.assertIn("16e_predictive_memory_orchestrator", human)
        self.assertIn("predictive-memory)", sh)
        self.assertIn("nexus_gate.loops.predictive_memory_orchestrator", sh)
        self.assertLess(human.index("16d_predictive_timing"), human.index("16e_predictive_memory_orchestrator"))

    def test_docs_cards_and_meta_orchestrator_reference_lane(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        algorithms = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8-sig")
        discoveries = (ROOT / "nexus_gate" / "discoveries" / "cards.py").read_text(encoding="utf-8-sig")
        meta = (ROOT / "nexus_gate" / "loops" / "meta_orchestrator_gate.py").read_text(encoding="utf-8-sig")
        self.assertIn("predictive-memory", readme)
        self.assertIn("Predictive Memory Orchestrator Algorithm", algorithms)
        self.assertIn("predictive-memory-orchestrator", discoveries)
        self.assertIn("reports/nexus_predictive_memory_orchestrator_latest.json", meta)
        self.assertIn("predictive_memory", meta)

    def test_constrained_cortex_recommends_refresh_lane(self) -> None:
        source = (ROOT / "nexus_gate" / "loops" / "predictive_memory_orchestrator.py").read_text(encoding="utf-8")
        self.assertIn("cortex-certificate-refresh", source)
        self.assertIn(r".\\scripts\\nexus.ps1 cortex-refresh", source)


if __name__ == "__main__":
    unittest.main()
