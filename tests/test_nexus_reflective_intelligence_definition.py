import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestNexusReflectiveIntelligenceDefinition(unittest.TestCase):
    def test_readme_defines_nexus_as_reflective_intelligence(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("Reflective Intelligence Layer for AI Systems", readme)
        self.assertIn("local-first reflective intelligence layer for AI systems", readme)
        self.assertIn("The portal is only the doorway", readme)
        self.assertIn("observable, diagnosable, bounded", readme)

    def test_versioning_preserves_portal_as_gateway_not_whole_system(self):
        doc = (ROOT / "docs" / "versioning" / "NEXUS_VERSIONING_REHYDRATION.md").read_text(encoding="utf-8-sig")
        self.assertIn("Portal = gateway.", doc)
        self.assertIn("Nexus Gate = reflective intelligence layer for AI systems.", doc)
        self.assertIn("v0.8.1 UI cleanup", doc)

    def test_electron_package_description_uses_reflective_intelligence(self):
        package = json.loads((ROOT / "electron" / "package.json").read_text(encoding="utf-8"))
        self.assertIn("Reflective intelligence HUD", package["description"])


if __name__ == "__main__":
    unittest.main()
