import json
import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "state" / "visual" / "nexus_spiral_gate_logo_manifest.v0.1.0.json"
DOC = REPO_ROOT / "docs" / "runtime" / "NEXUS_SPIRAL_GATE_LOGO.md"


class TestSpiralGateLogoV010(unittest.TestCase):
    def read_target(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        target = REPO_ROOT / data["target_file"]
        self.assertTrue(target.exists(), data["target_file"])
        return data, target.read_text(encoding="utf-8-sig")

    def test_manifest_records_close_h_corrections(self):
        data, text = self.read_target()
        self.assertEqual(data["version"], "v0.1.0-close-m")
        self.assertTrue(data["no_authority_change"])
        self.assertTrue(data["no_execution_change"])
        self.assertTrue(data["tnn_import_order_fixed"])
        self.assertIn("compact portal size", data["features"])
        self.assertIn("transparent logo backing", data["features"])
        self.assertIn("hidden original brand h1", data["features"])
        self.assertIn("no cross-buffer energy bar", data["features"])
        self.assertIn("local send pulse only", data["features"])
        self.assertIn("window.nexusGatePulse(reason)", data["public_hook"])

    def test_logo_is_compact_and_has_no_backing_box(self):
        data, text = self.read_target()
        self.assertIn("NEXUS_SPIRAL_GATE_LOGO_V010_STYLE_BEGIN", text)
        self.assertIn("NEXUS_SPIRAL_GATE_LOGO_V010_DOM_BEGIN", text)
        self.assertIn("NEXUS_SPIRAL_GATE_LOGO_V010_SCRIPT_BEGIN", text)
        self.assertIn('id="nexus-spgw-v010"', text)
        self.assertIn("width: 390px", text)
        self.assertIn("width: 80px", text)
        self.assertIn("background: transparent !important", text)
        self.assertIn("display: none !important", text)
        self.assertIn(".brand-block h1", text)
        self.assertIn("opacity: 0 !important", text)

    def test_cross_buffer_energy_bar_is_removed(self):
        data, text = self.read_target()
        self.assertNotIn('id="nexus-gate-energy-v010"', text)
        self.assertNotIn("nexus-gate-ether-stream", text)
        self.assertNotIn("nexusGateEtherFlowV010", text)
        self.assertNotIn("nexusGateHeaderBurstV010", text)
        self.assertIn("nexus-gate-local-pulse", text)
        self.assertIn("@keyframes nexusGateLocalBurstV010", text)

    def test_close_j_text_alignment_is_centered(self):
        data, text = self.read_target()
        self.assertTrue(data["text_alignment_fixed"])
        self.assertEqual(data["title_top_px"], 9)
        self.assertEqual(data["subtitle_top_px"], 48)
        self.assertIn("top: 9px", text)
        self.assertIn("top: 48px", text)
    def test_gear_vortex_and_send_hooks_remain(self):
        data, text = self.read_target()
        self.assertIn("@keyframes nexusGateVortexSpinV010", text)
        self.assertIn("@keyframes nexusGateFrameSpinV010", text)
        self.assertIn("@keyframes nexusGateGearSpinV010", text)
        self.assertIn("nexus-gate-micro-teeth", text)
        self.assertIn("nexus-gate-hole", text)
        self.assertIn("window.nexusGatePulse", text)
        self.assertIn("send-click", text)
        self.assertIn("send-enter", text)
        self.assertIn("send-submit", text)
        self.assertIn("nexus-message-sent", text)

    def test_tnn_import_order_wound_is_closed(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        self.assertTrue(data["tnn_import_order_fixed"])
        chat_engine = REPO_ROOT / "Tesseract Neural Network" / "brain" / "chat_engine.py"
        text = chat_engine.read_text(encoding="utf-8-sig")
        self.assertLess(text.index("BRAIN_DIR = Path(__file__).resolve().parent"), text.index("from ollama_adapter import"))
        self.assertLess(text.index("sys.path.insert(0, str(BRAIN_DIR))"), text.index("from ollama_adapter import"))

    def test_docs_lock_boundary(self):
        doc = DOC.read_text(encoding="utf-8-sig")
        self.assertIn("Close H visual correction", doc)
        self.assertIn("Close M text alignment", doc)
        self.assertIn("Close L text alignment", doc)
        self.assertIn("Close K text alignment", doc)
        self.assertIn("Close J text alignment", doc)
        self.assertIn("remove the long pulse/energy bar", doc)
        self.assertIn("hide the original brand-block h1", doc)
        self.assertIn("local halo burst", doc)
        self.assertIn("The gate animates. It does not gain authority.", doc)


if __name__ == "__main__":
    unittest.main()
