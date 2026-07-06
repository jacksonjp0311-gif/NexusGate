
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8-sig")


class TestNexusCellFailureModesV084(unittest.TestCase):
    def test_nexuscell_wounds_saved_in_doctor(self):
        doctor = read("docs/failure_modes/NEXUS_FAILURE_MODE_DOCTOR.md")
        for marker in [
            "FM-128 stale_manifest_version_pin",
            "FM-129 stale_planner_manifest_version_pin",
            "FM-130 compiler_visibility_not_authority",
            "FM-131 planner_visibility_not_backend_enablement",
            "FM-132 doctor_trap_without_self_authority",
        ]:
            self.assertIn(marker, doctor)

    def test_nexuscell_wounds_saved_in_chart(self):
        chart = read("docs/failure_modes/FAILURE_MODE_CHART.md")
        for marker in [
            "`stale_manifest_version_pin`",
            "`stale_planner_manifest_version_pin`",
            "`compiler_visibility_not_authority`",
            "`planner_visibility_not_backend_enablement`",
            "`doctor_trap_without_self_authority`",
        ]:
            self.assertIn(marker, chart)
        self.assertIn("No repeated failure without chart update", chart)

    def test_manifest_links_failure_visibility(self):
        manifest = json.loads(read("state/nexus_cell/cell_manifest.v0.8.4.json"))
        self.assertEqual(manifest["version"], "v0.8.4E")
        self.assertEqual(manifest["status"], "compiler_visible_planner_no_execution")
        self.assertTrue(manifest["failure_mode_visibility"]["enabled"])
        self.assertIn("stale_manifest_version_pin", manifest["failure_mode_visibility"]["modes"])
        self.assertIn("does not self-authorize", manifest["failure_mode_visibility"]["boundary"])

    def test_architecture_and_versioning_record_ledger(self):
        arch = read("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md")
        changelog = read("docs/versioning/NEXUS_CHANGELOG.md")
        versioning = read("docs/versioning/NEXUS_VERSIONING_REHYDRATION.md")
        self.assertIn("## v0.8.4E Failure-Mode Ledger Seal", arch)
        self.assertIn("v0.8.4E - NexusCell Failure-Mode Ledger", changelog)
        self.assertIn("v0.8.4E NexusCell Failure-Mode Ledger", versioning)


if __name__ == "__main__":
    unittest.main()
