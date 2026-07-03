import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestInterfaceAdapterContract(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(
            (ROOT / "state" / "interface_adapter_contract_index.v0.3.7.json").read_text(encoding="utf-8")
        )

    def test_contract_docs_and_json_exist(self):
        self.assertTrue((ROOT / "docs" / "interfaces" / "INTERFACE_ADAPTER_CONTRACT.md").exists())
        self.assertEqual(self.contract["version"], "0.3.7")

    def test_required_interfaces_declared(self):
        ids = {item["interface_id"] for item in self.contract["interfaces"]}
        for interface_id in [
            "powershell_cli",
            "powershell_tui",
            "electron_hud",
            "chatgpt_handoff",
            "codex_handoff",
            "future_browser_dashboard",
            "future_local_agent",
        ]:
            self.assertIn(interface_id, ids)

    def test_no_autonomous_authority_granted(self):
        for item in self.contract["interfaces"]:
            self.assertNotIn("autonomous", item["authority_level"].lower())
            self.assertIn("self_authorize", item["blocked_actions"])
            self.assertIn("bypass_evolve", item["blocked_actions"])

    def test_tui_and_electron_reflective_surfaces_declared(self):
        by_id = {item["interface_id"]: item for item in self.contract["interfaces"]}
        self.assertIn("reports/nexus_reflective_loop_report_latest.json", by_id["powershell_tui"]["read_surfaces"])
        self.assertIn("state/nexus_lineage_manifest_latest.json", by_id["electron_hud"]["read_surfaces"])
        self.assertEqual(by_id["electron_hud"]["surface_type"], "reflection_surface")


if __name__ == "__main__":
    unittest.main()
