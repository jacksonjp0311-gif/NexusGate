from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from nexus_gate.actions.cli import (
    _read_json,
    _stage_path,
    _write_json,
    action_final_evolve,
    calibration_status,
    experience_chain_verify,
    experience_seal,
    recommend,
    semantic_verify,
)


ROOT = Path(__file__).resolve().parents[1]


class GovernedExperienceEngineV270Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init"], cwd=str(self.root), capture_output=True, text=True, check=False)
        (self.root / "registry").mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            ROOT / "registry" / "nexus_command_registry.v2.6.2.json",
            self.root / "registry" / "nexus_command_registry.v2.6.2.json",
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_semantic_verify_rejects_tampered_receipt(self) -> None:
        packet = recommend(self.root)
        path = _stage_path(self.root, packet["action_id"], "recommendation")
        receipt = _read_json(path, {})
        receipt["recommendation"]["reason"] = "tampered after receipt hash"
        _write_json(path, receipt)

        report = semantic_verify(self.root, packet["action_id"])

        self.assertEqual(report["status"], "fail")
        self.assertIn("recommendation_receipt_invalid", report["failures"])

    def test_experience_seal_blocks_until_full_causal_chain_exists(self) -> None:
        packet = recommend(self.root)

        report = experience_seal(self.root, packet["action_id"])

        self.assertEqual(report["status"], "blocked")
        self.assertIn("missing_authorization", report["blocking_reasons"])

    def test_action_final_evolve_requires_effect_receipt(self) -> None:
        packet = recommend(self.root)

        with self.assertRaises(ValueError):
            action_final_evolve(self.root, packet["action_id"])

    def test_experience_chain_verify_exists_before_experiences(self) -> None:
        report = experience_chain_verify(self.root)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["chain"]["chain_length"], 0)

    def test_calibration_status_is_blocked_without_verified_experience(self) -> None:
        report = calibration_status(self.root)

        self.assertEqual(report["status"], "blocked")
        self.assertIn("missing_verified_experience", report["blocking_reasons"])


if __name__ == "__main__":
    unittest.main()
