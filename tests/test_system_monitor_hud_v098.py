import json
import unittest
from pathlib import Path

from nexus_gate.loops.toolkit import build_toolkit_packet


ROOT = Path(__file__).resolve().parents[1]


class TestSystemMonitorHudV098(unittest.TestCase):
    def test_system_monitor_loop_is_registered(self):
        registry = json.loads((ROOT / "loops" / "nexus_loop_registry.v0.1.json").read_text(encoding="utf-8-sig"))
        self.assertIn("toolkit_system_monitor_scout", registry["allowed_commands"])
        self.assertIn("system-monitor-scout", registry["loops"])
        loop = registry["loops"]["system-monitor-scout"]
        self.assertFalse(loop["mutates"])
        self.assertTrue(loop["ai_callable"])
        self.assertIn("System Monitor", loop["title"])

    def test_system_monitor_toolkit_packet_is_read_only(self):
        packet = build_toolkit_packet(ROOT, "system-monitor-scout", "unit")
        self.assertEqual(packet["status"], "pass")
        self.assertFalse(packet["boundary"]["repo_mutation_enabled"])
        self.assertFalse(packet["boundary"]["arbitrary_command_execution"])
        contract = packet["data"]["telemetry_contract"]
        self.assertTrue(contract["read_only"])
        self.assertFalse(contract["raw_code_box"])
        self.assertIn("cyber_security_tempest", contract["tabs"])
        self.assertEqual(contract["tempest_status"], "reserved_empty_hook")

    def test_loop_cards_include_system_monitor_scout(self):
        cards = json.loads((ROOT / "state" / "loops" / "nexus_loop_cards_latest.json").read_text(encoding="utf-8-sig"))
        ids = {card["loop_id"] for card in cards["cards"]}
        self.assertIn("system-monitor-scout", ids)
        self.assertEqual(cards["card_count"], len(ids))

    def test_tempest_tab_is_placeholder_only(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        self.assertIn("Reserved hook. Empty until governed integration.", html)
        self.assertIn("Reserved empty hook", main)
        self.assertIn("No TEMPEST telemetry", main)


if __name__ == "__main__":
    unittest.main()
