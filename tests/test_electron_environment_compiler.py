import json
import unittest
from pathlib import Path

from nexus_gate.ui.electron_environment import (
    compile_electron_environment,
    write_electron_environment_report,
)


ROOT = Path(__file__).resolve().parents[1]


class TestElectronEnvironmentCompiler(unittest.TestCase):
    def test_environment_compiler_reports_non_mutating_readiness(self):
        report = compile_electron_environment(ROOT)
        self.assertEqual(report.status, "pass")
        self.assertIn(report.readiness, {"ready", "not_ready"})
        checks = {item["check"]: item["status"] for item in report.checks}
        self.assertEqual(checks["electron_package_present"], "pass")
        self.assertEqual(checks["electron_dependency_declared"], "pass")
        self.assertIn(checks["node_available"], {"pass", "warn"})
        self.assertIn(checks["npm_available"], {"pass", "warn"})
        self.assertIn(checks["electron_node_module_present"], {"pass", "warn"})
        self.assertIn("does not install", report.claim_boundary)

    def test_environment_report_is_written(self):
        report = compile_electron_environment(ROOT)
        path = write_electron_environment_report(report, ROOT)
        self.assertEqual(path.name, "nexus_electron_environment_report_latest.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "0.3.5-electron-environment")
        self.assertFalse(
            next(
                item for item in data["checks"] if item["check"] == "electron_node_module_present"
            )["evidence"]["mutation_performed"]
        )

    def test_environment_docs_and_index_exist(self):
        self.assertTrue((ROOT / "docs" / "ui" / "ELECTRON_ENVIRONMENT_GATE.md").exists())
        index = json.loads(
            (ROOT / "state" / "electron_environment_gate_index.v0.3.5.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(index["module"], "nexus_gate.ui.electron_environment_compile")
        self.assertEqual(index["report"], "reports/nexus_electron_environment_report_latest.json")
        self.assertIn("install_dependencies", index["blocked_actions"])

    def test_cli_surface_is_registered(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn('"electron-env"', ps)
        self.assertIn("nexus_gate.ui.electron_environment_compile", human)
        self.assertIn("electron-env)", sh)


if __name__ == "__main__":
    unittest.main()
