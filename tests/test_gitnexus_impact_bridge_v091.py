
from __future__ import annotations
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestGitNexusImpactBridgeV091(unittest.TestCase):
    def test_docs_and_manifest_visible(self):
        self.assertTrue((ROOT / "docs/gitnexus/NEXUS_GITNEXUS_IMPACT_BRIDGE.md").exists())
        data = json.loads((ROOT / "state/gitnexus/gitnexus_impact_manifest.v0.9.1.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(data["version"], "v0.9.1")
        self.assertTrue(data["no_execution"])
        self.assertTrue(data["no_mutation"])
        self.assertTrue(data["no_git_write_authority"])

    def test_impact_packet_is_read_only(self):
        from nexus_gate.gitnexus.impact import build_impact_packet
        packet = build_impact_packet(ROOT)
        self.assertEqual(packet["mode"], "gitnexus_impact_bridge_read_only")
        self.assertEqual(packet["nexuscell_lane"], "gitnexus-impact")
        self.assertFalse(packet["boundary"]["execution_enabled"])
        self.assertFalse(packet["boundary"]["repo_mutation_enabled"])
        self.assertFalse(packet["boundary"]["git_write_enabled"])
        self.assertIn("impact_packet_id", packet)

    def test_cli_emits_outputs(self):
        proc = subprocess.run([sys.executable, "-m", "nexus_gate.gitnexus.impact", "--root", str(ROOT), "--json"], cwd=str(ROOT), text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((ROOT / "state/gitnexus/gitnexus_impact_packet_latest.json").exists())
        self.assertTrue((ROOT / "reports/gitnexus_impact_report_latest.json").exists())
        self.assertTrue((ROOT / "reports/gitnexus_impact_report_latest.md").exists())

    def test_nexuscell_lane_registered_read_only(self):
        from nexus_gate.nexus_cell.policy import CONTROLLED_LANES, lane_policy
        self.assertIn("gitnexus-impact", CONTROLLED_LANES)
        meta = lane_policy("gitnexus-impact")
        self.assertTrue(meta["allowed"])
        self.assertFalse(meta["mutates"])

if __name__ == "__main__":
    unittest.main()
