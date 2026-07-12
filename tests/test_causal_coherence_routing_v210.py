from __future__ import annotations

import unittest
from pathlib import Path

from nexus_gate.decision.arbiter import arbitrate_recommendations
from nexus_gate.decision.envelope import build_decision_envelope
from nexus_gate.loops.wounds import has_active_wound


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
        self.assertEqual(result["schema"], "NEXUS_RECOMMENDATION_ARBITER.v2.4.0")
        self.assertEqual(result["selected"]["source"], "coherence-field")
        self.assertIn("may not execute", result["boundary"])

    def test_decision_envelope_contains_causal_arbiter(self) -> None:
        packet = build_decision_envelope(ROOT, intent="causal coherence test")
        self.assertEqual(packet["schema"], "NEXUS_DECISION_ENVELOPE.v2.4.0")
        self.assertEqual(packet["arbiter"]["schema"], "NEXUS_RECOMMENDATION_ARBITER.v2.4.0")
        self.assertIn("scored_recommendations", packet["arbiter"])
        self.assertIn("arbiter_score", packet["selected_action"])
        self.assertIn("repository_snapshot", packet)
        self.assertIn("epoch_id", packet["repository_snapshot"])
        self.assertTrue(packet["selected_action"]["requires_human_authorization"])
        self.assertIn("outcome_awareness", packet)

    def test_zero_coherence_and_confidence_clamping(self) -> None:
        recs = [
            {
                "source": "coherence-field",
                "action": "restore",
                "command": ".\\scripts\\nexus.ps1 coherence-field",
                "why": "zero coherence",
                "severity": "high",
                "confidence": 9.0,
                "estimated_cost": "short",
                "source_packet_hash": "abc",
            },
            {
                "source": "final-seal",
                "action": "final",
                "command": ".\\scripts\\nexus.ps1 evolve",
                "why": "final",
                "severity": "required",
                "confidence": 1.0,
                "estimated_cost": "long",
                "blocking_conditions": ["never_skip_before_commit"],
            },
        ]
        result = arbitrate_recommendations(recs, {"coherence": {"score": 0, "lineage_entropy": 0}})
        selected = result["selected"]
        self.assertEqual(selected["source"], "coherence-field")
        self.assertEqual(selected["arbiter_factors"]["confidence_weight"], 20.0)
        self.assertGreater(selected["arbiter_factors"]["coherence_adjustment"], 0)

    def test_wound_sentinel_normalization(self) -> None:
        self.assertFalse(has_active_wound({"status": "pass", "active_wound_key": "none"}))
        self.assertFalse(has_active_wound({"status": "pass", "active_wound_key": "clear"}))
        self.assertTrue(has_active_wound({"status": "pass", "active_wound_key": "compiler_failed"}))
        self.assertTrue(has_active_wound({"status": "fail", "active_wound_key": "none"}))


if __name__ == "__main__":
    unittest.main()
