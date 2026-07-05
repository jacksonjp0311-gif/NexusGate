import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestGeoPreflightCleanupV083(unittest.TestCase):
    def test_python_m_router_has_no_runpy_warning(self):
        result = subprocess.run(
            [
                sys.executable,
                "-W",
                "error",
                "-m",
                "nexus_gate.geometric_memory.router",
                "--root",
                str(ROOT),
                "--intent",
                "warning seal test",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        packet = json.loads(result.stdout)
        self.assertEqual(packet["version"], "0.8.3C")

    def test_package_init_uses_importlib_lazy_access(self):
        init_text = (ROOT / "nexus_gate" / "geometric_memory" / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("import_module", init_text)
        self.assertNotIn("from .router import", init_text)

    def test_cleanup_removes_generated_untracked_residue(self):
        report = ROOT / "reports" / "nexus_geometric_memory_packet_latest.json"
        state = ROOT / "state" / "nexus_geometric_memory_runtime_latest.json"
        timed = ROOT / "reports" / "nexus_compile_report_20990101_010101.json"
        report.parent.mkdir(parents=True, exist_ok=True)
        state.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("{}", encoding="utf-8")
        state.write_text("{}", encoding="utf-8")
        timed.write_text("{}", encoding="utf-8")

        from nexus_gate.geometric_memory.cleanup import cleanup_generated

        cleaned = cleanup_generated(ROOT)
        self.assertIn("reports/nexus_geometric_memory_packet_latest.json", cleaned["removed"])
        self.assertIn("state/nexus_geometric_memory_runtime_latest.json", cleaned["removed"])
        self.assertIn("reports/nexus_compile_report_20990101_010101.json", cleaned["removed"])
        self.assertFalse(report.exists())
        self.assertFalse(state.exists())
        self.assertFalse(timed.exists())

    def test_entrypoints_deduplicated(self):
        entry = (ROOT / "docs" / "ENTRYPOINTS.md").read_text(encoding="utf-8")
        self.assertEqual(entry.count("## GitHub Repository"), 1)
        self.assertIn("Geometric Cleanup", entry)
        self.assertIn("geo-clean", entry)

    def test_shell_surfaces_include_geo_clean(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn('"geo-clean"', ps)
        self.assertIn("Invoke-NexusGeoClean", ps)
        self.assertIn("geo-clean)", sh)
        self.assertIn("nexus_gate.geometric_memory.cleanup", sh)


if __name__ == "__main__":
    unittest.main()

