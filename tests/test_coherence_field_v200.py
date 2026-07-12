from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.coherence.field import build_coherence_field


ROOT = Path(__file__).resolve().parents[1]


class CoherenceFieldV200Tests(unittest.TestCase):
    def test_coherence_field_declares_v2_protocol_and_boundary(self) -> None:
        packet = build_coherence_field(ROOT, intent="test coherence")
        self.assertEqual(packet["schema"], "NEXUS_COHERENCE_CONTINUITY_FIELD.v2.4.0")
        self.assertEqual(packet["version"], "2.4.0")
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertIn("coherence", packet)
        self.assertIn("score", packet["coherence"])
        self.assertIn("policy_kernel", packet)
        self.assertIn("evidence_dependency_graph", packet)
        self.assertIn("wound_intelligence", packet)
        self.assertIn("benchmark_manifest", packet)
        self.assertIn("continuity_protocol", packet)
        self.assertIn("outcome_learning", packet)
        self.assertIn("repository_snapshot", packet)
        self.assertIn("state", packet["coherence"])
        self.assertTrue(packet["selected_next_action"]["recommendation_only"])
        self.assertTrue(packet["selected_next_action"]["requires_human_authorization"])
        self.assertIn("convert_coherence_to_authority", packet["blocked_actions"])
        self.assertIn("coherence may not grant authority", packet["claim_boundary"])

    def test_coherence_field_cli_writes_report_and_state(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "nexus_gate.coherence.field", "--root", ".", "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertEqual(packet["schema"], "NEXUS_COHERENCE_CONTINUITY_FIELD.v2.4.0")
        self.assertTrue((ROOT / "reports" / "nexus_coherence_field_latest.json").exists())
        self.assertTrue((ROOT / "state" / "coherence" / "nexus_coherence_field_latest.json").exists())

    def test_command_surfaces_expose_coherence_field(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        self.assertIn('"coherence-field"', ps)
        self.assertIn("nexus_gate.coherence.field", ps)
        self.assertIn("coherence-field)", sh)
        self.assertIn("nexus_gate.coherence.field", sh)
        self.assertIn('"coherence-field"', human)
        self.assertIn("16h_coherence_field", human)
        self.assertIn("v2.4.0 Causal Loop Hardening", readme)
        self.assertIn("reports/nexus_coherence_field_latest.json", agents)

    def test_v2_docs_and_policy_kernel_exist(self) -> None:
        required = [
            "docs/runtime/NEXUS_COHERENCE_FIELD_PROTOCOL.md",
            "docs/design/CAUSAL_COHERENCE_ROUTING_DESIGN.md",
            "docs/protocols/CAUSAL_COHERENCE_ROUTING_PROTOCOL.md",
            "docs/design/OUTCOME_AWARE_ARBITER_DESIGN.md",
            "docs/protocols/OUTCOME_AWARE_ARBITER_PROTOCOL.md",
            "docs/protocols/GOVERNED_AGENT_CONTINUITY_PROTOCOL.md",
            "policy/authority_laws.json",
            "policy/risk_profiles.json",
            "policy/capabilities.json",
            "policy/claim_boundaries.json",
            "state/protocols/nexus_continuity_protocol.v2.0.json",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).exists(), rel)
        algorithms = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8-sig")
        discoveries = (ROOT / "nexus_gate" / "discoveries" / "cards.py").read_text(encoding="utf-8-sig")
        self.assertIn("Coherence Field Algorithm", algorithms)
        self.assertIn("Governed Agent Continuity Algorithm", algorithms)
        self.assertIn("Causal Coherence Routing Algorithm", algorithms)
        self.assertIn("Outcome Feedback Algorithm", algorithms)
        self.assertIn("coherence-continuity-threshold", discoveries)
        self.assertIn("causal-coherence-routing", discoveries)
        self.assertIn("recommendation-outcome-learning", discoveries)


if __name__ == "__main__":
    unittest.main()
