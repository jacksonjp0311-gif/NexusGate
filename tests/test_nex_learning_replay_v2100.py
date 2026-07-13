from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nexus_gate.nex_core.learn import propose, replay_verify


class NexLearningReplayV2100Tests(unittest.TestCase):
    def test_replay_starts_empty_and_detects_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(replay_verify(root)["status"], "pass")
            propose(root)
            replay = replay_verify(root)
            self.assertEqual(replay["status"], "pass")
            self.assertEqual(replay["applied_count"], 0)


if __name__ == "__main__":
    unittest.main()
