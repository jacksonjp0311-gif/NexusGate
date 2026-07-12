from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.decision.envelope import build_decision_envelope


ROOT = Path(__file__).resolve().parents[1]


class DecisionEnvelopeV130Tests(unittest.TestCase):
    def test_decision_envelope_is_self_bootstrap_and_recommendation_only(self) -> None:
        packet = build_decision_envelope(ROOT, intent="test self bootstrap")
        self.assertEqual(packet["schema"], "NEXUS_DECISION_ENVELOPE.v2.2.0")
        self.assertEqual(packet["version"], "2.2.0")
        self.assertEqual(packet["mode"], "outcome_aware_decision_envelope")
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertTrue(packet["authority"]["recommendation_only"])
        self.assertFalse(packet["authority"]["autonomous_authority"])
        self.assertFalse(packet["authority"]["execution_enabled"])
        self.assertTrue(packet["authority"]["final_evolve_required_before_commit"])
        self.assertIn("self_authorize", packet["blocked_actions"])
        self.assertIn("execute_selected_action", packet["blocked_actions"])
        self.assertIn("origin", packet)
        self.assertIn("memory", packet)
        self.assertIn("risk", packet)
        self.assertGreaterEqual(len(packet["recommendations"]), 1)
        self.assertIn("selected_action", packet)
        self.assertIn("arbiter", packet)
        self.assertIn("coherence_input", packet)
        self.assertIn("outcome_awareness", packet)
        self.assertTrue(packet["selected_action"]["recommendation_only"])

    def test_decision_envelope_cli_writes_report_and_state(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "nexus_gate.decision.envelope", "--root", ".", "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertEqual(packet["schema"], "NEXUS_DECISION_ENVELOPE.v2.2.0")
        self.assertTrue((ROOT / "reports" / "nexus_decision_envelope_latest.json").exists())
        self.assertTrue((ROOT / "state" / "decision" / "nexus_decision_envelope_latest.json").exists())

    def test_command_surfaces_expose_decision_envelope(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        self.assertIn('"decision-envelope"', ps)
        self.assertIn("nexus_gate.decision.envelope", ps)
        self.assertIn("decision-envelope)", sh)
        self.assertIn("nexus_gate.decision.envelope", sh)
        self.assertIn('"decision-envelope"', human)
        self.assertIn("16g_decision_envelope", human)
        self.assertIn("Causal Coherence Routing", readme)
        self.assertIn("reports/nexus_decision_envelope_latest.json", agents)

    def test_docs_cards_record_self_bootstrap_discovery(self) -> None:
        algorithms = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8-sig")
        discoveries = (ROOT / "nexus_gate" / "discoveries" / "cards.py").read_text(encoding="utf-8-sig")
        runtime_doc = (ROOT / "docs" / "runtime" / "NEXUS_DECISION_ENVELOPE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Self Bootstrap Decision Envelope Algorithm", algorithms)
        self.assertIn("Causal Coherence Routing Algorithm", algorithms)
        self.assertIn("self-bootstrap-decision-envelope", discoveries)
        self.assertIn("self-orientation, not self-authorization", runtime_doc)


if __name__ == "__main__":
    unittest.main()
