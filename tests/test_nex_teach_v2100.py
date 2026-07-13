from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from nexus_gate.nex_core.teach import (
    begin_teaching_episode,
    bind_teaching_validation,
    compute_teaching_quality,
    seal_teaching_episode,
    verify_teaching_episode,
)


class NexTeachV2100Tests(unittest.TestCase):
    def test_teaching_stages_are_immutable_and_accepted_without_tests_has_zero_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            begin = begin_teaching_episode(root, "Teach acceptance versus validation")
            teaching_id = begin["teaching_id"]
            sealed = seal_teaching_episode(root, teaching_id, "accepted")
            self.assertEqual(sealed["status"], "pass")
            quality = sealed["seal"]["quality"]
            self.assertEqual(quality["human_acceptance"], 1.0)
            self.assertEqual(quality["validation_strength"], 0.0)
            again = seal_teaching_episode(root, teaching_id, "rejected")
            self.assertEqual(again["status"], "fail")
            self.assertEqual(again["reason"], "immutable_stage_mismatch")

    def test_tests_without_experience_do_not_produce_full_causal_quality(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            teaching_id = begin_teaching_episode(root, "Teach test attribution")["teaching_id"]
            bind_teaching_validation(root, teaching_id, "unit-test-bundle")
            sealed = seal_teaching_episode(root, teaching_id, "accepted")
            quality = sealed["seal"]["quality"]
            self.assertGreater(quality["validation_strength"], 0.0)
            self.assertLess(quality["causal_attribution"], 1.0)
            self.assertLess(quality["gate_quality"], 1.0)

    def test_rejected_teaching_becomes_negative_evidence_and_tamper_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            teaching_id = begin_teaching_episode(root, "Reject this lesson")["teaching_id"]
            sealed = seal_teaching_episode(root, teaching_id, "rejected")
            self.assertTrue(sealed["seal"]["negative_evidence"])
            seal_path = root / "state" / "nex_core" / "teaching" / teaching_id / "40_teaching_seal.json"
            packet = json.loads(seal_path.read_text(encoding="utf-8"))
            packet["human_disposition"] = "accepted"
            seal_path.write_text(json.dumps(packet), encoding="utf-8")
            self.assertEqual(verify_teaching_episode(root, teaching_id)["status"], "fail")


if __name__ == "__main__":
    unittest.main()
