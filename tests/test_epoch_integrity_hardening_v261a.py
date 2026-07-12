from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nexus_gate.epochs.seal import build_epoch_integrity_seal, _is_source_surface


ROOT = Path(__file__).resolve().parents[1]


class EpochIntegrityHardeningV261aTests(unittest.TestCase):
    def test_same_source_reuses_source_epoch_identity(self) -> None:
        first = build_epoch_integrity_seal(ROOT)["manifest"]
        second = build_epoch_integrity_seal(ROOT)["manifest"]
        self.assertEqual(first["source_epoch_id"], second["source_epoch_id"])
        self.assertTrue(first["checks"]["source_epoch_excludes_parent_epoch"])

    def test_neural_runtime_graph_excluded_from_source(self) -> None:
        self.assertFalse(_is_source_surface("state/neural_activity/repo_neural_graph_latest.json"))
        self.assertTrue(_is_source_surface("nexus_gate/epochs/seal.py"))

    def test_relevant_untracked_source_is_included_in_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nexus_gate").mkdir()
            (root / "nexus_gate" / "__init__.py").write_text("", encoding="utf-8")
            (root / "nexus_gate" / "new_module.py").write_text("x = 1\n", encoding="utf-8")
            # Without git metadata the direct surface classifier still proves the inclusion boundary.
            self.assertTrue(_is_source_surface("nexus_gate/new_module.py"))


if __name__ == "__main__":
    unittest.main()
