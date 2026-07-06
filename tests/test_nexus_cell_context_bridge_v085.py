import json
import unittest
from pathlib import Path

from nexus_gate.nexus_cell.context_bridge import build_context_bridge, select_context_refs
from nexus_gate.nexus_cell.plan import build_plan


ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8-sig")


class TestNexusCellContextBridgeV085(unittest.TestCase):
    def test_context_bridge_is_read_only_and_bounded(self):
        packet = build_context_bridge(ROOT, "inspect docs only", limit=8)
        self.assertEqual(packet["version"], "0.8.5")
        self.assertEqual(packet["mode"], "read_only_context_bridge_no_execution")
        self.assertLessEqual(packet["context_ref_count"], 8)
        self.assertFalse(packet["boundary"]["execution_enabled"])
        self.assertFalse(packet["boundary"]["file_contents_embedded"])

    def test_mutating_intent_includes_failure_visibility(self):
        packet = build_context_bridge(ROOT, "git add commit and push a generated patch", limit=12)
        paths = {ref["path"] for ref in packet["context_refs"]}
        self.assertIn("docs/failure_modes/NEXUS_FAILURE_MODE_DOCTOR.md", paths)
        self.assertIn("docs/failure_modes/FAILURE_MODE_CHART.md", paths)
        self.assertEqual(packet["planner"]["authority_decision"], "shadow")

    def test_select_context_refs_dedupes_and_limits(self):
        plan = build_plan(ROOT, "download api secret then git push")
        refs = select_context_refs(plan, limit=5)
        self.assertEqual(len(refs), 5)
        self.assertEqual(len({item["path"] for item in refs}), 5)

    def test_manifest_and_commands_expose_context_bridge(self):
        manifest = json.loads(read("state/nexus_cell/cell_manifest.v0.8.4.json"))
        self.assertTrue(str(manifest["version"]).startswith("v0.8."))
        self.assertEqual(manifest["status"], "context_bridge_visible_no_execution")
        self.assertTrue(manifest["context_bridge"]["enabled"])
        self.assertIn("cell-context", read("scripts/nexus.ps1"))
        self.assertIn("Build context bridge packet", read("scripts/desktop/open_nexus_gate_console.ps1"))

    def test_docs_record_context_bridge(self):
        self.assertIn("NexusCell Context Bridge", read("docs/nexus_cell/NEXUS_CELL_CONTEXT_BRIDGE.md"))
        self.assertIn("## v0.8.5 Context Bridge Seal", read("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md"))


if __name__ == "__main__":
    unittest.main()
