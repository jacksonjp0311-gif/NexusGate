from __future__ import annotations

import unittest

from nexus_gate.hygiene.runtime_churn import GENERATED_RUNTIME_CACHE_PATTERNS, TRACKED_GENERATED_PATTERNS, _classify


class NeuralGraphRuntimeHygieneV262Tests(unittest.TestCase):
    def test_repo_neural_graph_is_generated_runtime_cache(self) -> None:
        path = "state/neural_activity/repo_neural_graph_latest.json"
        self.assertIn(path, TRACKED_GENERATED_PATTERNS)
        self.assertIn(path, GENERATED_RUNTIME_CACHE_PATTERNS)
        classified = _classify([{"status": " M", "path": path}])
        self.assertEqual(classified["tracked_generated"][0]["classification"], "generated_runtime_cache")


if __name__ == "__main__":
    unittest.main()
