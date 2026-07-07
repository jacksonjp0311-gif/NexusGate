from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "electron" / "renderer" / "index.html"
BRIDGE = ROOT / "electron" / "renderer" / "nexus_conversation_output_bridge.v0.2.1a.js"


class TestNexusConversationOutputBridgeV021A(unittest.TestCase):
    def test_bridge_is_linked(self):
        html = HTML.read_text(encoding="utf-8-sig")
        self.assertIn("nexus_conversation_output_bridge.v0.2.1a.js", html)

    def test_bridge_has_conversation_and_operator_split(self):
        js = BRIDGE.read_text(encoding="utf-8-sig")
        self.assertIn("isSimpleHumanChat", js)
        self.assertIn("isOperatorCommand", js)
        self.assertIn("conversationalizeAudit", js)

    def test_bridge_removes_robotic_audit_for_normal_chat(self):
        js = BRIDGE.read_text(encoding="utf-8-sig")
        self.assertIn("Observation", js)
        self.assertIn("Recommendation", js)
        self.assertIn("Human Authorization", js)
        self.assertIn("Hey - I'm here.", js)

    def test_bridge_suppresses_stale_fast_selector_event(self):
        js = BRIDGE.read_text(encoding="utf-8-sig")
        self.assertIn("suppressStaleSelectorEvents", js)
        self.assertIn("[NEXUS] FAST selected.", js)
        self.assertIn("Selector source=select", js)

    def test_bridge_preserves_governance_for_commands(self):
        js = BRIDGE.read_text(encoding="utf-8-sig")
        self.assertIn("commit", js)
        self.assertIn("run script", js)
        self.assertIn("operator", js)


if __name__ == "__main__":
    unittest.main()