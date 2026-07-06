import json
import unittest
from pathlib import Path

from nexus_gate.nexus_cell.plan import build_plan, capability_vector_from_intent


ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8-sig")


class TestNexusCellPlannerV084(unittest.TestCase):
    def test_read_only_intent_is_low_risk(self):
        plan = build_plan(ROOT, "inspect docs and summarize architecture")
        self.assertEqual(plan["mode"], "read_only_planner_no_execution")
        self.assertLessEqual(plan["risk_score"], 0.30)
        self.assertEqual(plan["authority_decision"], "engage")
        self.assertFalse(plan["boundary"]["execution_enabled"])

    def test_git_write_without_authority_shadows(self):
        plan = build_plan(ROOT, "git add commit and push a generated patch")
        self.assertEqual(plan["authority_decision"], "shadow")
        self.assertEqual(plan["route_mode"], "shadow")
        self.assertIn("git_write_without_explicit_authority", plan["gate_flags"])

    def test_secret_plus_network_denies(self):
        plan = build_plan(ROOT, "call https://api.example.com with bearer token secret")
        self.assertEqual(plan["authority_decision"], "deny")
        self.assertEqual(plan["route_mode"], "escalate")
        self.assertIn("hard_deny_secret_plus_network", plan["gate_flags"])

    def test_capability_vector_detects_process_and_write(self):
        caps = capability_vector_from_intent("run powershell to write a file")
        self.assertEqual(caps["process_spawn"], 1)
        self.assertEqual(caps["fs_write"], 1)

    def test_manifest_and_portal_expose_planner(self):
        manifest = json.loads(read("state/nexus_cell/cell_manifest.v0.8.4.json"))
        self.assertTrue(str(manifest["version"]).startswith("v0.8.4"))
        self.assertIn(manifest["status"], {"read_only_planner_enabled_no_execution", "compiler_visible_planner_no_execution"})
        self.assertTrue(manifest["planner"]["enabled"])
        portal = read("scripts/desktop/open_nexus_gate_console.ps1")
        self.assertIn("6. Plan gated invocation (read-only)", portal)
        self.assertIn("cell-plan", read("scripts/nexus.ps1"))

    def test_docs_record_no_execution_boundary(self):
        planner_doc = read("docs/nexus_cell/NEXUS_CELL_PLANNER.md")
        self.assertIn("No execution backend.", planner_doc)
        self.assertIn("No subprocess runner.", planner_doc)
        arch = read("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md")
        self.assertIn("## v0.8.4C Read-Only Planner Seal", arch)


if __name__ == "__main__":
    unittest.main()

