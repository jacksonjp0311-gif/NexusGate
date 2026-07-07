import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from nexus_gate.nn_router.contract import VALID_TARGET_ROLES, selected_roles
from nexus_gate.nn_router.tesseract_neural_network import build_tesseract_neural_network_response

ROOT = Path(__file__).resolve().parents[1]


class TesseractNeuralNetworkMinimalTests(unittest.TestCase):
    def test_folder_exists_and_has_minimal_payload(self):
        folder = ROOT / "Tesseract Neural Network"
        self.assertTrue(folder.exists())
        self.assertTrue((folder / "tnn_surface.py").exists())
        self.assertTrue((folder / "manifest.json").exists())
        data = json.loads((folder / "manifest.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(data["name"], "Tesseract Neural Network")
        self.assertFalse(data["vendored_neuralforge"])
        self.assertFalse(data["authority_boundary"]["patch_application"])

    def test_tnn_role_is_in_nn_router_contract(self):
        self.assertIn("TNN", VALID_TARGET_ROLES)
        self.assertEqual(selected_roles("TNN"), ["TNN"])

    def test_tnn_surface_reads_fixture_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifacts = root / "artifacts" / "tpn"
            artifacts.mkdir(parents=True)
            (artifacts / "control_bundle_report_v1_13_latest.json").write_text(json.dumps({
                "ok": True,
                "ready_for_human_review": True,
                "mutation_allowed": False,
                "patch_proposal_receipts": [{}, {}, {}],
            }), encoding="utf-8")
            result = subprocess.run([
                sys.executable,
                str(ROOT / "Tesseract Neural Network" / "tnn_surface.py"),
                "--intent", "fixture",
                "--neuralforge-root", str(root),
                "--json",
            ], cwd=str(ROOT), capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            packet = json.loads(result.stdout)
            self.assertEqual(packet["role"], "TNN")
            self.assertIn("TESSERACT NEURAL NETWORK", packet["response"])
            self.assertIn("mutation_allowed: False", packet["response"])

    def test_nn_router_can_build_tnn_response(self):
        response = build_tesseract_neural_network_response("status")
        self.assertEqual(response["role"], "TNN")
        self.assertEqual(response["model"], "Tesseract Neural Network/minimal-receipt-surface")

    def test_portal_and_selector_markers(self):
        nexus = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('"tnn"', nexus)
        self.assertIn('Role "TNN"', nexus)
        tui = (ROOT / "scripts" / "nexus_tui.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("Tesseract Neural Network", tui)
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn("Tesseract Neural Network", html)


if __name__ == "__main__":
    unittest.main()
