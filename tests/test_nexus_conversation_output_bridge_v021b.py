from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "electron" / "renderer" / "index.html"
BRIDGE = ROOT / "electron" / "renderer" / "nexus_conversation_output_bridge.v0.2.1b.js"


class TestNexusConversationOutputBridgeV021B(unittest.TestCase):
    def test_bridge_is_linked(self):
        html = HTML.read_text(encoding="utf-8-sig")
        self.assertIn("nexus_conversation_output_bridge.v0.2.1b.js", html)

    def test_bridge_catches_partial_audit_cards(self):
        js = BRIDGE.read_text(encoding="utf-8-sig")
        self.assertIn("hasObservation && hasRecommendation", js)
        self.assertIn("hasRecommendation && hasRisk", js)

    def test_bridge_recognizes_you_there_as_chat(self):
        js = BRIDGE.read_text(encoding="utf-8-sig")
        self.assertIn("you there", js)
        self.assertIn("Yeah - I'm here.", js)

    def test_bridge_suppresses_stale_engineering_move(self):
        js = BRIDGE.read_text(encoding="utf-8-sig")
        self.assertIn("next safe engineering move", js)
        self.assertIn("NexusGate product development", js)
        self.assertIn("looksLikeStaleEngineeringMove", js)

    def test_bridge_keeps_operator_split(self):
        js = BRIDGE.read_text(encoding="utf-8-sig")
        self.assertIn("isOperatorCommand", js)
        self.assertIn("repo mutation", js)


if __name__ == "__main__":
    unittest.main()