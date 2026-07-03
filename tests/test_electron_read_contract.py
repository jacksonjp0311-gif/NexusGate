import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronReadContract(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(
            (ROOT / "state" / "electron_read_contract_index.v0.3.2.json").read_text(
                encoding="utf-8"
            )
        )

    def test_contract_docs_and_state_exist(self):
        self.assertTrue((ROOT / "docs" / "ui" / "ELECTRON_READ_CONTRACT.md").exists())
        self.assertEqual(self.contract["implementation_status"], "contract_only_no_electron_app")

    def test_read_surfaces_include_tui_pair(self):
        surfaces = self.contract["read_surfaces"]
        self.assertIn("reports/tui/nexus_tui_snapshot_latest.html", surfaces)
        self.assertIn("reports/tui/nexus_tui_surface_latest.json", surfaces)
        self.assertIn("state/ai_feedback_context_latest.json", surfaces)

    def test_snapshot_pair_is_required(self):
        pairs = self.contract["required_pairs"]
        snapshot_pair = next(pair for pair in pairs if pair["command"] == "/snapshot")
        self.assertIn("reports/tui/nexus_tui_snapshot_latest.html", snapshot_pair["outputs"])
        self.assertIn("reports/tui/nexus_tui_surface_latest.json", snapshot_pair["outputs"])

    def test_allowlist_is_governed_nexus_lanes_only(self):
        expected = {
            "evolve",
            "interface",
            "feedback",
            "heal",
            "status",
            "compact",
            "interconnect",
            "runtime",
            "pack",
        }
        self.assertEqual(set(self.contract["allowlisted_commands"]), expected)
        self.assertNotIn("powershell", self.contract["allowlisted_commands"])
        self.assertNotIn("cmd", self.contract["allowlisted_commands"])
        self.assertNotIn("bash", self.contract["allowlisted_commands"])

    def test_blocked_actions_and_boundary_are_explicit(self):
        blocked = self.contract["blocked_actions"]
        for action in [
            "arbitrary_shell_commands",
            "external_api_write",
            "secret_access",
            "self_authorize",
            "memory_promotion_without_evidence",
            "ungated_repo_mutation",
            "mutate_graph_state",
            "bypass_evolve",
        ]:
            self.assertIn(action, blocked)
        self.assertIn("does not build Electron", self.contract["claim_boundary"])
        self.assertIn("authorize autonomous action", self.contract["claim_boundary"])

    def test_existing_bridge_index_matches_contract_surfaces(self):
        bridge = json.loads(
            (ROOT / "state" / "tui_to_electron_bridge_index.v0.2.5.json").read_text(
                encoding="utf-8"
            )
        )
        for surface in self.contract["read_surfaces"]:
            self.assertIn(surface, bridge["electron_read_surfaces"])


if __name__ == "__main__":
    unittest.main()
