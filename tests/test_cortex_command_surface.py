from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestCortexCommandSurface(unittest.TestCase):
    def test_powershell_cortex_lane_has_default_intent(self):
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('"cortex"', ps)
        self.assertIn("$cortexIntent = $Tag", ps)
        self.assertIn('Run NEXUS Cortex gate.', ps)
        self.assertIn("nexus_gate.cortex.compile", ps)

    def test_bash_cortex_lane_exists(self):
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn("cortex)", sh)
        self.assertIn("nexus_gate.cortex.compile", sh)


if __name__ == "__main__":
    unittest.main()
