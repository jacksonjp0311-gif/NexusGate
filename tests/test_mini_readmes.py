import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MINI_DIRS = [
    "nexus_gate",
    "nexus_gate/core",
    "nexus_gate/runtime",
    "nexus_gate/compiler",
    "nexus_gate/evidence",
    "docs",
    "docs/context",
    "docs/failure_modes",
    "rcc/nexus",
    "scripts",
    "tests",
    "state",
    "ledger",
    "reports",
    "logs",
]


class TestMiniReadmes(unittest.TestCase):
    def test_mini_readmes_have_echo_location(self):
        for rel in MINI_DIRS:
            path = ROOT / rel / "README.md"
            self.assertTrue(path.exists(), rel)
            self.assertIn("RCC Nexus Echo Location", path.read_text(encoding="utf-8"), rel)


if __name__ == "__main__":
    unittest.main()
