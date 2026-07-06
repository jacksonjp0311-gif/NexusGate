
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8-sig")


class TestNexusCellDoctrineV084(unittest.TestCase):
    def test_architecture_doctrine_markers(self):
        doc = read("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md")
        for marker in [
            "NexusCell is the execution containment organ of NexusGate.",
            "A sandbox contains code.",
            "NexusCell governs execution.",
            "No execution without containment.",
            "## 7. Capability, Risk, and Authority Equations",
            "## 8. Boundary Law",
            "## 9. Ledger Hashchain",
            "## 10. Receipt Model",
            "## 11. Return Seal Model",
            "## v0.8.4B Portal Access and Manifest Seal",
        ]:
            self.assertIn(marker, doc)

    def test_manifest_is_doctrine_only_and_ui_visible(self):
        manifest = json.loads(read("state/nexus_cell/cell_manifest.v0.8.4.json"))
        self.assertTrue(str(manifest["version"]).startswith("v0.8."))
        self.assertIn(manifest["status"], {"doctrine_manifest_ui_access_only", "read_only_planner_enabled_no_execution", "compiler_visible_planner_no_execution", "context_bridge_visible_no_execution", "operator_shell_visible_no_execution", "full_core_runtime_visible_controlled"})
        self.assertTrue(manifest["desktop_portal"]["enabled"])
        self.assertEqual(manifest["desktop_portal"]["menu_entry"], "[10] NexusCell / Containment")
        forbidden = set(manifest["desktop_portal"]["forbidden_surfaces"])
        self.assertIn("execute code", forbidden)
        self.assertIn("enable backend", forbidden)
        self.assertIn("claim rollback", forbidden)

    def test_desktop_portal_has_nexuscell_access(self):
        portal = read("scripts/desktop/open_nexus_gate_console.ps1")
        self.assertIn("function Invoke-NexusCellConsole", portal)
        self.assertIn("[10] NexusCell / Containment", portal)
        self.assertIn('elseif ($choice -eq "10")', portal)
        self.assertIn("No execution without containment.", portal)

    def test_entrypoints_and_readme_expose_nexuscell(self):
        entry = read("docs/ENTRYPOINTS.md")
        organ = read("NexusCell/README.md")
        self.assertIn("## NexusCell Execution Containment", entry)
        self.assertIn("[10] NexusCell / Containment", entry)
        self.assertIn("## Desktop Portal Access", organ)
        self.assertIn("No execution backend is defined here yet.", organ)

    def test_versioning_mentions_v084b(self):
        changelog = read("docs/versioning/NEXUS_CHANGELOG.md")
        versioning = read("docs/versioning/NEXUS_VERSIONING_REHYDRATION.md")
        self.assertIn("v0.8.4B - NexusCell Portal Access and Manifest Seal", changelog)
        self.assertIn("v0.8.4B NexusCell Portal Access and Manifest Seal", versioning)


if __name__ == "__main__":
    unittest.main()
