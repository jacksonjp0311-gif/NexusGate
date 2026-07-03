import json
import unittest
from pathlib import Path

from nexus_gate.ui.electron_preflight import (
    EXPECTED_ALLOWLIST,
    compile_electron_preflight,
    write_electron_preflight_report,
)


ROOT = Path(__file__).resolve().parents[1]


class TestElectronPreflightCompiler(unittest.TestCase):
    def test_preflight_compiler_passes(self):
        report = compile_electron_preflight(ROOT)
        self.assertEqual(report.status, "pass")
        self.assertEqual(set(report.allowlisted_commands), EXPECTED_ALLOWLIST)
        checks = {item["check"]: item["status"] for item in report.checks}
        for check in [
            "electron_required_paths",
            "electron_allowlist_matches_contract",
            "electron_blocked_actions_complete",
            "electron_required_surface_pair",
            "electron_main_security_markers",
            "electron_preload_api_limited",
            "electron_renderer_uses_preload_bridge",
            "electron_package_private",
            "electron_claim_boundary_present",
        ]:
            self.assertEqual(checks[check], "pass")

    def test_preflight_report_is_written(self):
        report = compile_electron_preflight(ROOT)
        path = write_electron_preflight_report(report, ROOT)
        self.assertEqual(path.name, "nexus_electron_preflight_report_latest.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "pass")
        self.assertIn("reports/tui/nexus_tui_surface_latest.json", data["read_surfaces"])

    def test_preflight_docs_and_index_exist(self):
        self.assertTrue((ROOT / "docs" / "ui" / "ELECTRON_PREFLIGHT_COMPILER.md").exists())
        index = json.loads(
            (ROOT / "state" / "electron_preflight_compiler_index.v0.3.4.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(index["module"], "nexus_gate.ui.electron_preflight_compile")
        self.assertEqual(index["report"], "reports/nexus_electron_preflight_report_latest.json")
        self.assertIn("launch_electron", index["blocked_actions"])

    def test_cli_surface_is_registered_in_scripts(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn('"electron-preflight"', ps)
        self.assertIn("nexus_gate.ui.electron_preflight_compile", human)
        self.assertIn("electron-preflight)", sh)


if __name__ == "__main__":
    unittest.main()
