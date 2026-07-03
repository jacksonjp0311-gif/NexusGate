import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestNexusLineageManifest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(
            (ROOT / "state" / "nexus_lineage_manifest_latest.json").read_text(encoding="utf-8")
        )

    def test_lineage_protocol_exists(self):
        text = (ROOT / "docs" / "versioning" / "NEXUS_LINEAGE_PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn("Organic evolution is allowed.", text)
        self.assertIn("Ungated compounding is not.", text)

    def test_manifest_tracks_required_versions_and_reports(self):
        self.assertEqual(self.manifest["system_version"], "0.3.7")
        self.assertEqual(self.manifest["active_phase"], "Reflective Intelligence Gateway")
        self.assertEqual(self.manifest["reflective_loop_version"], "0.3.7")
        self.assertIn("last_evolve_report", self.manifest)
        self.assertIn("last_electron_preflight_report", self.manifest)
        self.assertIn("last_electron_smoke_report", self.manifest)

    def test_manifest_blocks_unsafe_promotions(self):
        blocked = set(self.manifest["blocked_promotions"])
        self.assertIn("autonomous_authority", blocked)
        self.assertIn("production_ready", blocked)
        self.assertFalse(self.manifest["production_ready"])
        self.assertIn("No autonomous authority", self.manifest["claim_boundaries"])


if __name__ == "__main__":
    unittest.main()
