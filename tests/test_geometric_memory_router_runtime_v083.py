import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestGeometricMemoryRouterRuntimeV083(unittest.TestCase):
    def test_build_geometry_packet_read_only(self):
        from nexus_gate.geometric_memory.router import build_geometry_packet

        packet = build_geometry_packet(
            root=ROOT,
            intent="Summarize the failing test and route a bounded repair.",
            evidence="tests/test_geometric_memory_router_runtime_v083.py",
            authority="read_only",
            context="README.md,docs/intelligence/NEXUS_GEOMETRIC_MEMORY_ROUTER.md",
        )

        self.assertEqual(packet["version"], "0.8.3C")
        self.assertEqual(packet["mode"], "read_only_runtime_stub")
        self.assertEqual(packet["axis_complete"], 1.0)
        self.assertFalse(packet["geometry_pass"])
        self.assertEqual(packet["reason"], "read_only_runtime_stub_no_repair_authority")
        self.assertIn("latency_plan", packet)
        self.assertIn("LFTE", packet["source_theory_stack"])

    def test_cli_writes_report_and_state(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "nexus_gate.geometric_memory.router",
                "--root",
                str(ROOT),
                "--intent",
                "speed packet test",
                "--evidence",
                "tests/test_geometric_memory_router_runtime_v083.py",
                "--context",
                "README.md,docs/ENTRYPOINTS.md",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        packet = json.loads(result.stdout)
        self.assertEqual(packet["version"], "0.8.3C")
        self.assertEqual(packet["axis_complete"], 1.0)
        self.assertFalse(packet["geometry_pass"])
        self.assertTrue((ROOT / "reports" / "nexus_geometric_memory_packet_latest.json").exists())
        self.assertTrue((ROOT / "state" / "nexus_geometric_memory_runtime_latest.json").exists())

    def test_shell_surfaces_include_geo_command(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8")
        self.assertIn('"geo"', ps)
        self.assertIn("Invoke-NexusGeo", ps)
        self.assertIn("nexus_gate.geometric_memory.router", ps)
        self.assertIn("geo)", sh)
        self.assertIn("nexus_gate.geometric_memory.router", sh)

    def test_docs_and_readme_reference_runtime_packet(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        entry = (ROOT / "docs" / "ENTRYPOINTS.md").read_text(encoding="utf-8")
        router = (ROOT / "docs" / "intelligence" / "NEXUS_GEOMETRIC_MEMORY_ROUTER.md").read_text(encoding="utf-8")
        self.assertLess(len(readme.splitlines()), 220)
        self.assertIn("v0.8.1 UI cleanup line", readme)
        self.assertIn("v0.8.3C geometric router runtime stub line", readme)
        self.assertIn("python -m nexus_gate.geometric_memory.router", readme)
        self.assertIn("Geometric Runtime Packet", entry)
        self.assertIn("Runtime Stub v0.8.3C", router)


if __name__ == "__main__":
    unittest.main()
