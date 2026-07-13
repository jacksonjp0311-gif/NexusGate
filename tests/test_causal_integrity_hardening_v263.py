from __future__ import annotations

import unittest
import tempfile
import shutil
import subprocess
from pathlib import Path

from nexus_gate.actions.cli import (
    _compare_file_snapshots,
    _read_json,
    _stage_path,
    _write_json,
    authorize,
    execute,
    first_learning_readiness,
    recommend,
    validate,
)


ROOT = Path(__file__).resolve().parents[1]


class CausalIntegrityHardeningV263Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init"], cwd=str(self.root), capture_output=True, text=True, check=False)
        (self.root / "registry").mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "registry" / "nexus_command_registry.v2.6.2.json", self.root / "registry" / "nexus_command_registry.v2.6.2.json")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_recommendation_binds_registry_definition_hash(self) -> None:
        packet = recommend(self.root)
        self.assertEqual(packet["schema"], "NEXUS_ACTION_RECOMMENDATION_RECEIPT.v2.6.3")
        self.assertIn("command_registry_entry_hash", packet["recommendation"])
        self.assertTrue(packet["recommendation"]["command_registry_entry_hash"])

    def test_authorization_is_idempotent_when_receipt_matches(self) -> None:
        packet = recommend(self.root)
        first = authorize(self.root, packet["action_id"], note="test idempotent auth")
        second = authorize(self.root, packet["action_id"], note="test idempotent auth")
        self.assertEqual(first["receipt_hash"], second["receipt_hash"])

    def test_expired_authorization_blocks_execution(self) -> None:
        packet = recommend(self.root)
        authorize(self.root, packet["action_id"], note="expired auth test", expires_minutes=-1)
        with self.assertRaises(ValueError):
            execute(self.root, packet["action_id"])
        lifecycle = _read_json(_stage_path(self.root, packet["action_id"], "lifecycle"), {})
        self.assertEqual(lifecycle["state"], "EXPIRED")

    def test_validation_rejects_missing_effect_receipt(self) -> None:
        packet = recommend(self.root)
        action_id = packet["action_id"]
        fake_execution = {
            "schema": "NEXUS_ACTION_EXECUTION_RECEIPT.v2.6.3",
            "action_id": action_id,
            "recommendation_id": packet["recommendation_id"],
            "execution": {"exit_class": "success"},
            "pre_execution": packet["pre_epoch"],
            "post_execution_observation": packet["pre_epoch"],
            "receipt_hash": "fake",
        }
        _write_json(_stage_path(self.root, action_id, "execution"), fake_execution)
        with self.assertRaises(ValueError):
            validate(self.root, action_id)

    def test_snapshot_comparison_detects_already_dirty_file_changed_again(self) -> None:
        pre = {
            "working_tree_files": {
                "nexus_gate/example.py": {
                    "exists": True,
                    "hash": "before",
                    "size": 10,
                    "classification": "canonical_source",
                }
            }
        }
        post = {
            "working_tree_files": {
                "nexus_gate/example.py": {
                    "exists": True,
                    "hash": "after",
                    "size": 11,
                    "classification": "canonical_source",
                }
            }
        }
        comparison = _compare_file_snapshots(pre, post)
        self.assertIn("nexus_gate/example.py", comparison["actual_modified"])
        self.assertIn("nexus_gate/example.py", comparison["already_dirty_changed"])

    def test_first_learning_readiness_is_conservative(self) -> None:
        packet = first_learning_readiness(self.root)
        self.assertIn(packet["status"], {"ready", "blocked"})
        self.assertTrue(packet["authorization_integrity_ready"])
        self.assertTrue(packet["effect_capture_ready"])
        self.assertTrue(packet["final_evolve_enforced"])


if __name__ == "__main__":
    unittest.main()
