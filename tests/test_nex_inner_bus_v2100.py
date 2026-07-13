from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nexus_gate.nex_core.bus import publish_message, replay_message_bus
from nexus_gate.nex_core.messages import create_message, validate_message


class NexInnerBusV2100Tests(unittest.TestCase):
    def test_valid_messages_publish_and_replay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            msg = create_message(cycle_id="cycle_test", topic="breath.pressure", message_type="state_observation", source_organ="breath", target_organs=["language"], source_epoch_id="epoch", payload={"pressure": 12})
            self.assertTrue(validate_message(msg)["valid"])
            self.assertEqual(publish_message(tmp, msg)["status"], "pass")
            self.assertEqual(publish_message(tmp, msg)["status"], "verified_existing")
            replay = replay_message_bus(tmp)
            self.assertEqual(replay["status"], "pass")
            self.assertEqual(replay["message_count"], 1)

    def test_invalid_authority_and_self_reflection_fail(self) -> None:
        msg = create_message(cycle_id="cycle_test", topic="x", message_type="state", source_organ="language", target_organs=["self_model"], source_epoch_id="epoch", payload={})
        msg["authority_class"] = "root_authority"
        self.assertIn("invalid_authority_class", validate_message(msg)["errors"])
        msg = create_message(cycle_id="cycle_test", topic="x", message_type="state", source_organ="language", target_organs=["language"], source_epoch_id="epoch", payload={})
        self.assertIn("immediate_source_to_self_reflection", validate_message(msg)["errors"])

    def test_hop_limit_terminates_loops(self) -> None:
        msg = create_message(cycle_id="cycle_test", topic="x", message_type="state", source_organ="language", target_organs=["self_model"], source_epoch_id="epoch", payload={}, hop_count=9, hop_limit=8)
        self.assertIn("hop_limit_exceeded", validate_message(msg)["errors"])


if __name__ == "__main__":
    unittest.main()
