import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestCrossDomainSynthesisProtocol(unittest.TestCase):
    def test_cross_domain_synthesis_boundaries(self):
        text = (ROOT / "docs/intelligence/CROSS_DOMAIN_SYNTHESIS_PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn("No metaphor becomes fact without evidence.", text)
        self.assertIn("No simulation becomes real-world proof.", text)
        self.assertIn("No code demo becomes production validation.", text)
        self.assertIn("No biological pattern becomes medical advice.", text)
        self.assertIn("No mathematical conjecture becomes theorem without proof.", text)
        self.assertIn("No physics analogy becomes physical law without dimensional and empirical support.", text)


if __name__ == "__main__":
    unittest.main()
