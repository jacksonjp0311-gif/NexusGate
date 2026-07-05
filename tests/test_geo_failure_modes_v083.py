import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestGeoFailureModesV083(unittest.TestCase):
    def test_geometric_wounds_saved_in_failure_doctor(self):
        doctor = (ROOT / "docs" / "failure_modes" / "NEXUS_FAILURE_MODE_DOCTOR.md").read_text(encoding="utf-8-sig")
        for marker in [
            "FM-120 readme_anchor_drift",
            "FM-121 untracked_cleanup_git_restore_pathspec",
            "FM-122 runpy_eager_package_import",
            "FM-123 lazy_import_readback_false_positive",
            "FM-124 readme_line_budget_boundary",
            "FM-125 powershell_child_command_expansion",
            "FM-126 tracked_report_cleanup_hazard",
            "FM-127 powershell_backtick_string_parse_wound",
        ]:
            self.assertIn(marker, doctor)

    def test_geometric_wounds_saved_in_failure_chart(self):
        chart = (ROOT / "docs" / "failure_modes" / "FAILURE_MODE_CHART.md").read_text(encoding="utf-8-sig")
        for marker in [
            "`readme_anchor_drift`",
            "`untracked_cleanup_git_restore_pathspec`",
            "`runpy_eager_package_import`",
            "`lazy_import_readback_false_positive`",
            "`readme_line_budget_boundary`",
            "`powershell_child_command_expansion`",
            "`tracked_report_cleanup_hazard`",
            "`powershell_backtick_string_parse_wound`",
        ]:
            self.assertIn(marker, chart)
        self.assertIn("No repeated failure without chart update", chart)

    def test_versioning_mentions_geometric_failure_ledger(self):
        changelog = (ROOT / "docs" / "versioning" / "NEXUS_CHANGELOG.md").read_text(encoding="utf-8-sig")
        versioning = (ROOT / "docs" / "versioning" / "NEXUS_VERSIONING_REHYDRATION.md").read_text(encoding="utf-8-sig")
        self.assertIn("v0.8.3J - Geometric Failure Mode Ledger Close", changelog)
        self.assertIn("v0.8.3J Geometric Failure Mode Ledger Close", versioning)

if __name__ == "__main__":
    unittest.main()
