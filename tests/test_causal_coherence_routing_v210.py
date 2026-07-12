from __future__ import annotations

import unittest
from pathlib import Path

from nexus_gate.decision.arbiter import arbitrate_recommendations
from nexus_gate.decision.envelope import build_decision_envelope


ROOT = Path(__file__).resolve().parents[1]


class CausalCoherenceRoutingV210Tests(unittest.TestCase):
    def test_arbiter_scores_and_selects_without_authority(self) -> None:
        recs = [
            {
                "source": "final-seal",
                "action": "run_final_evolve_before_commit",
                "command": ".\\scripts\\nexus.ps1 evolve",
                "why": "Final seal.",
                "severity": "required",
                "confidence": 1.0,
                "estimated_cost": "long",
                "blocking_conditions": ["never_skip_before_commit"],
                "source_packet_hash": None,
            },
            {
                "source": "coherence-field",
                "action": "restore_coherence_field",
                "command": ".\\scripts\\nexus.ps1 coherence-field",
                "why": "Low coherence.",
                "severity": "high",
                "confidence": 0.9,
                "estimated_cost": "short",
                "blocking_conditions": [],
                "source_packet_hash": "abc",
            },
        ]
        result = arbitrate_recommendations(recs, {"coherence": {"score": 55, "lineage_entropy": 9, "missing_surfaces": ["x"]}})
        self.assertEqual(result["schema"], "NEXUS_RECOMMENDATION_ARBITER.v2.1.0")
        self.assertEqual(result["selected"]["source"], "coherence-field")
        self.assertIn("may not execute", result["boundary"])

    def test_decision_envelope_contains_causal_arbiter(self) -> None:
        packet = build_decision_envelope(ROOT, intent="causal coherence test")
        self.assertEqual(packet["schema"], "NEXUS_DECISION_ENVELOPE.v2.1.0")
        self.assertEqual(packet["arbiter"]["schema"], "NEXUS_RECOMMENDATION_ARBITER.v2.1.0")
        self.assertIn("scored_recommendations", packet["arbiter"])
        self.assertIn("arbiter_score", packet["selected_action"])
        self.assertTrue(packet["selected_action"]["requires_human_authorization"])


if __name__ == "__main__":
    unittest.main()
