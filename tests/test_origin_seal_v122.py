from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.origin.seal import build_origin_seal


ROOT = Path(__file__).resolve().parents[1]


class OriginSealV122Tests(unittest.TestCase):
    def test_origin_seal_packet_declares_current_product_identity(self) -> None:
        packet = build_origin_seal(ROOT)
        self.assertEqual(packet["schema"], "NEXUS_ORIGIN_SEAL.v2.5.0")
        self.assertEqual(packet["product_version"], "2.5.0")
        self.assertEqual(packet["product_phase"], "Triadic Geometric Lattice")
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertIn("origin_manifest_hash", packet)
        self.assertIn("legacy_version_lineage", packet)
        self.assertIn("pyproject_distribution_version", packet["legacy_version_lineage"])
        self.assertIn("python_package_api_version", packet["legacy_version_lineage"])
        self.assertFalse(packet["authority_boundary"]["autonomous_authority"])
        self.assertTrue(packet["authority_boundary"]["final_evolve_required_before_commit"])
        self.assertIn("stale_evidence_as_truth", packet["blocked_actions"])

    def test_origin_seal_cli_writes_report_and_manifest(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "nexus_gate.origin.seal", "--root", ".", "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertEqual(packet["schema"], "NEXUS_ORIGIN_SEAL.v2.5.0")
        self.assertTrue((ROOT / "reports" / "nexus_origin_seal_latest.json").exists())
        self.assertTrue((ROOT / "state" / "nexus_origin_manifest_latest.json").exists())

    def test_command_surfaces_expose_origin_seal(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        self.assertIn('"origin-seal"', ps)
        self.assertIn("nexus_gate.origin.seal", ps)
        self.assertIn("origin-seal)", sh)
        self.assertIn("nexus_gate.origin.seal", sh)
        self.assertIn('"origin-seal"', human)
        self.assertIn("16f_origin_seal", human)
        self.assertIn("v2.5.0 Triadic Geometric Lattice", readme)
        self.assertIn("state/nexus_origin_manifest_latest.json", agents)


if __name__ == "__main__":
    unittest.main()
