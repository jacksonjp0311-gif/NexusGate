import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestRehydrationFailureUpdateCharts(unittest.TestCase):
    def test_readme_preserves_dual_shell_and_rehydration_rules(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Every new runtime loop must exist in both PowerShell and Bash.", text)
        self.assertIn("Every loop must run the gated compiler before it cycles, promotes, checkpoints, or claims a pass.", text)
        self.assertIn("No rehydration without failure chart visibility.", text)
        self.assertIn("No patch without update chart visibility.", text)

    def test_failure_and_update_charts_exist(self):
        failure = ROOT / "docs" / "failure_modes" / "FAILURE_MODE_CHART.md"
        update = ROOT / "docs" / "updates" / "UPDATE_CHART.md"
        self.assertTrue(failure.exists())
        self.assertTrue(update.exists())
        failure_text = failure.read_text(encoding="utf-8")
        update_text = update.read_text(encoding="utf-8")
        self.assertIn("compiler_failed", failure_text)
        self.assertIn("origin_dehydrated", failure_text)
        self.assertIn("v0.1.4b", update_text)

    def test_rehydration_manifest_requires_failure_and_update_visibility(self):
        manifest = json.loads((ROOT / "docs" / "context" / "rehydration_manifest.v0.1.4.json").read_text(encoding="utf-8"))
        required = manifest["agent_must_read_before_patch"]
        self.assertIn("docs/failure_modes/FAILURE_MODE_CHART.md", required)
        self.assertIn("docs/updates/UPDATE_CHART.md", required)
        self.assertIn("reports/nexus_compile_report_latest.json", required)

    def test_rehydration_scripts_exist(self):
        for rel in ["scripts/nexus_rehydrate.ps1", "scripts/nexus_rehydrate.sh"]:
            path = ROOT / rel
            self.assertTrue(path.exists(), rel)
            text = path.read_text(encoding="utf-8")
            self.assertIn("FAILURE_MODE_CHART", text)
            self.assertIn("UPDATE_CHART", text)


if __name__ == "__main__":
    unittest.main()
