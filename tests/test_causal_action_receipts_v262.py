from __future__ import annotations

import tempfile
import unittest
import shutil
import subprocess
from pathlib import Path

from nexus_gate.actions.cli import VALID_TRANSITIONS, chain_verify, execute, recommend


ROOT = Path(__file__).resolve().parents[1]


class CausalActionReceiptsV262Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init"], cwd=str(self.root), capture_output=True, text=True, check=False)
        (self.root / "registry").mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "registry" / "nexus_command_registry.v2.6.2.json", self.root / "registry" / "nexus_command_registry.v2.6.2.json")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_state_machine_blocks_proposed_to_executing(self) -> None:
        self.assertNotIn("EXECUTING", VALID_TRANSITIONS["PROPOSED"])
        self.assertIn("AUTHORIZED", VALID_TRANSITIONS["PROPOSED"])

    def test_recommendation_receipt_created_without_authorization(self) -> None:
        packet = recommend(self.root)
        self.assertIn(packet["schema"], {"NEXUS_ACTION_RECOMMENDATION_RECEIPT.v2.6.2", "NEXUS_ACTION_RECOMMENDATION_RECEIPT.v2.6.3"})
        self.assertTrue(packet["authority_boundary"]["recommendation_only"])
        self.assertFalse(packet["authority_boundary"]["autonomous_execution"])

    def test_execution_without_authorization_is_blocked(self) -> None:
        packet = recommend(self.root)
        with self.assertRaises(ValueError):
            execute(self.root, packet["action_id"])

    def test_action_chain_verify_passes_after_recommendation(self) -> None:
        recommend(self.root)
        packet = chain_verify(self.root)
        self.assertEqual(packet["status"], "pass")
        self.assertTrue(packet["chains"]["action_receipts"]["chain_valid"])


if __name__ == "__main__":
    unittest.main()
