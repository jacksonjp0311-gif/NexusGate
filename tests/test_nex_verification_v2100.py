from __future__ import annotations

import unittest
from pathlib import Path

from nexus_gate.nex_core.verify import run_before_after_benchmark, verify_all, verify_authority_invariants, verify_learning_proposal, verify_model_replay, verify_retention


ROOT = Path(__file__).resolve().parents[1]


class NexVerificationV2100Tests(unittest.TestCase):
    def test_authority_invariants_hold_across_field_conditions(self) -> None:
        packet = verify_authority_invariants(ROOT)
        self.assertEqual(packet["status"], "pass")
        for check in packet["checks"]:
            self.assertTrue(check["requires_human_authorization"])
            self.assertFalse(check["may_execute"])
            self.assertFalse(check["may_authorize"])

    def test_replay_missing_seal_warns_but_does_not_self_pass_seal(self) -> None:
        packet = verify_model_replay(ROOT)
        self.assertIn(packet["stored_seal_status"], {"warn", "pass"})
        if packet["stored_seal_status"] == "warn":
            self.assertEqual(packet["reason"], "stored_seal_missing")

    def test_benchmark_and_retention_are_measured(self) -> None:
        benchmark = run_before_after_benchmark(ROOT)
        self.assertIn("paired_comparison", benchmark)
        self.assertIn(benchmark["conclusion"], {"insufficient_evidence", "candidate_improvement"})
        retention = verify_retention(ROOT)
        self.assertIn("old_task_retention", retention)

    def test_successful_verification_still_does_not_authorize_application(self) -> None:
        packet = verify_learning_proposal(ROOT)
        self.assertIn("eligible_for_authorization", packet)
        self.assertNotIn("authorized", packet.get("reason", ""))
        all_packet = verify_all(ROOT)
        self.assertIn(all_packet["status"], {"pass", "warn"})


if __name__ == "__main__":
    unittest.main()
