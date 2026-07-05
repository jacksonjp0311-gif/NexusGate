import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestNexCleanStartup(unittest.TestCase):
    def test_renderer_resets_to_one_greeting(self):
        js = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("resetChatToNexGreeting", js)
        self.assertIn("Hello. I am NEX", js)
        self.assertIn("bounded reflective intelligence surface", js)
        self.assertNotIn('pushConsole("WARN", "TUI surface missing. Hydrating from AI feedback context.")', js)

    def test_renderer_reflects_local_model_connection_refusal(self):
        js = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("reflectNexFailure", js)
        self.assertIn("WinError 10061", js)
        self.assertIn("Ollama is not running", js)
        self.assertIn("Next bounded test", js)

    def test_index_uses_ascii_nex_symbol(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn("Hello. I am NEX", html)
        self.assertNotIn("NÃŽÅ¾X", html)
        self.assertNotIn("NÎžX", html)


if __name__ == "__main__":
    unittest.main()
