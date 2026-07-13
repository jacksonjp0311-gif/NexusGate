from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from nexus_gate.nex_core.learn import CONFIG, apply_learning_event, authorize_learning_proposal, compute_learning_utility, log_conductance_update, propose
from nexus_gate.nex_core.teach import begin_teaching_episode, bind_teaching_validation, seal_teaching_episode


class NexLearningMathV2100Tests(unittest.TestCase):
    def test_log_space_update_is_bounded_and_positive(self) -> None:
        update = log_conductance_update(current=1.0, prior=1.0, quality=0.48, utility=0.6)
        self.assertGreater(update["proposed_conductance"], 1.0)
        self.assertAlmostEqual(update["relative_change"], math.exp(0.04 * 0.48 * 0.6) - 1.0, places=6)
        severe = log_conductance_update(current=1.0, prior=1.0, quality=0.9, utility=0.9, contradiction_pressure=10.0)
        self.assertLess(severe["proposed_conductance"], 1.0)
        self.assertGreater(severe["proposed_conductance"], 0.0)
        self.assertLessEqual(abs(severe["delta_z"]), CONFIG["delta_max"])

    def test_one_or_two_teachings_cannot_apply_persistent_learning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for idx in range(2):
                tid = begin_teaching_episode(root, f"lesson {idx}")["teaching_id"]
                bind_teaching_validation(root, tid, f"tests-{idx}")
                seal_teaching_episode(root, tid, "accepted")
            proposal = propose(root)
            self.assertFalse(proposal["edge_updates"][0]["eligible"])
            self.assertEqual(apply_learning_event(root, proposal["proposal_id"])["status"], "blocked")

    def test_authorization_without_quality_still_blocks_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proposal = propose(root)
            auth = authorize_learning_proposal(root, proposal["proposal_id"])
            self.assertEqual(auth["status"], "pass")
            applied = apply_learning_event(root, proposal["proposal_id"])
            self.assertEqual(applied["status"], "blocked")
            self.assertFalse(applied["persistent_learning_applied"])


if __name__ == "__main__":
    unittest.main()
