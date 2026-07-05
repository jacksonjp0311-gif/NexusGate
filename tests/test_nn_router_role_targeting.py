import json
import tempfile
import unittest
from pathlib import Path

from nexus_gate.nn_router.compile import build_distribution
from nexus_gate.nn_router.scorecard import build_scorecard, write_scorecard


class TestNexusRoleTargetingAndDrift(unittest.TestCase):
    def _write_manifest(self, root: Path, model: str, tag: str) -> None:
        manifest = root / "manifests" / "registry.ollama.ai" / "library" / model / tag
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({
            "schemaVersion": 2,
            "config": {"digest": "sha256:" + ("a" * 64)},
            "layers": [{"digest": "sha256:" + ("b" * 64)}],
        }), encoding="utf-8")

    def test_deep_role_targets_mistral_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_manifest(root, "phi3", "mini")
            self._write_manifest(root, "mistral", "latest")
            report = build_distribution(
                root=root,
                intent="Use DEEP reasoning.",
                models_root=root,
                call_model=False,
                target_role="DEEP",
            )
            self.assertEqual(report["version"], "0.6.4")
            self.assertEqual(report["target_role"], "DEEP")
            self.assertEqual(len(report["route_decisions"]), 1)
            decision = report["route_decisions"][0]
            self.assertEqual(decision["role"], "DEEP")
            self.assertEqual(decision["model"], "mistral:latest")
            self.assertFalse(decision["model_called"])
            self.assertTrue(decision["recommendation_only"])

    def test_public_report_sanitizes_local_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            repo_root = temp_root / "repo"
            models_root = temp_root / "models"
            repo_root.mkdir()
            models_root.mkdir()
            self._write_manifest(models_root, "mistral", "latest")

            report = build_distribution(
                root=repo_root,
                intent="sanitize",
                models_root=models_root,
                target_role="DEEP",
            )
            encoded = json.dumps(report)
            self.assertNotIn(str(repo_root), encoded)
            self.assertNotIn(str(models_root), encoded)
            self.assertIn("<repo-root>", encoded)
            self.assertTrue("<models-root>" in encoded or "%USERPROFILE%" in encoded)

    def test_scorecard_reports_review_without_live_model_call(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "reports").mkdir()
            report = build_distribution(root=root, intent="score", models_root=root, target_role="DEEP")
            (root / "reports" / "nexus_nn_router_report_latest.json").write_text(json.dumps(report), encoding="utf-8")
            (root / "reports" / "nexus_compile_report_latest.json").write_text(json.dumps({
                "status": "pass",
                "gates": [{"gate": "unit_tests", "status": "pass"}],
            }), encoding="utf-8")
            scorecard = build_scorecard(root)
            self.assertEqual(scorecard["version"], "0.6.4")
            self.assertIn("live_model_call_not_yet_observed", scorecard["drift_flags"])
            self.assertGreaterEqual(scorecard["scores"]["overall_score"], 0.8)
            write_scorecard(root, scorecard)
            self.assertTrue((root / "reports" / "nexus_drift_reduction_scorecard_latest.json").exists())


if __name__ == "__main__":
    unittest.main()

