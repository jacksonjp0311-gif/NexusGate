from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestCortexCommandSurface(unittest.TestCase):
    def test_powershell_cortex_lane_has_default_intent(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('"cortex"', ps)
        self.assertIn('"sync-cortex"', ps)
        self.assertIn("$cortexIntent = $Tag", ps)
        self.assertIn('Run NEXUS Cortex gate.', ps)
        self.assertIn("nexus_gate.cortex.compile", ps)
        self.assertIn("sync_cortex.ps1", ps)

    def test_bash_cortex_lane_exists(self):
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn("cortex)", sh)
        self.assertIn("sync-cortex)", sh)
        self.assertIn("nexus_gate.cortex.compile", sh)
        self.assertIn("sync_cortex.sh", sh)

    def test_sync_script_excludes_runtime_and_secret_surfaces(self):
        ps = (ROOT / "scripts" / "sync_cortex.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('".git"', ps)
        self.assertIn('".cortex"', ps)
        self.assertIn('"__pycache__"', ps)
        self.assertIn('"*.pyc"', ps)
        self.assertIn("authority_boundary", ps)
        self.assertIn("nexus_cortex_sync_report_latest.json", ps)

    def test_cortex_gate_checks_vector_storage(self):
        compiler = (ROOT / "nexus_gate" / "cortex" / "compile.py").read_text(encoding="utf-8")
        self.assertIn("vector_storage_current", compiler)
        self.assertIn("legacy_or_invalid", compiler)

    def test_cortex_discovery_and_algorithm_cards_exist(self):
        algorithms = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8")
        discoveries = (ROOT / "nexus_gate" / "discoveries" / "cards.py").read_text(encoding="utf-8")
        self.assertIn("Cortex Sync Protocol Algorithm", algorithms)
        self.assertIn("Versioned Vector Blob Storage Algorithm", algorithms)
        self.assertIn("cortex-versioned-vector-memory", discoveries)
        self.assertIn("observed_reduction", discoveries)


if __name__ == "__main__":
    unittest.main()
