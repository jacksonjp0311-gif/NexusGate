import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronModelResponseErrorHud(unittest.TestCase):
    def test_model_response_error_triggers_system_hud(self):
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("NEX_MODEL_RESPONSE_STAGE_MARKER", renderer)
        self.assertIn('stage: "nex_model_response"', renderer)
        self.assertIn("const modelError = modelResponses.find", renderer)
        self.assertIn("showSystemErrorHud(systemReport)", renderer)
        self.assertIn("system-error", renderer)
        self.assertIn("append-only", renderer)
        self.assertNotIn('writeOutput(visible, { preTranslated: true });', renderer)


if __name__ == "__main__":
    unittest.main()
