import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from nexus_gate.nn_router.contract import VALID_TARGET_ROLES, selected_roles
from nexus_gate.nn_router.tesseract_neural_network import build_tesseract_neural_network_response

ROOT = Path(__file__).resolve().parents[1]
TNN_ROOT = ROOT / "Tesseract Neural Network"


class TesseractNeuralNetworkSelfContainedTests(unittest.TestCase):
    def test_folder_exists_and_has_self_contained_payload(self):
        folder = TNN_ROOT
        self.assertTrue(folder.exists())
        for name in [
            "tnn_surface.py",
            "refresh_from_neuralforge.py",
            "manifest.json",
            "receipt_paths.json",
            "portal_entry.json",
            "receipts/receipt_bundle_latest.json",
            "state/tnn_state_latest.json",
            "schemas/receipt_bundle.schema.json",
        ]:
            self.assertTrue((folder / name).exists(), name)
        data = json.loads((folder / "manifest.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(data["name"], "Tesseract Neural Network")
        self.assertTrue(data["self_contained_runtime"])
        self.assertFalse(data["external_neuralforge_required"])
        self.assertFalse(data["authority_boundary"]["patch_application"])

    def test_tnn_role_is_in_nn_router_contract(self):
        self.assertIn("TNN", VALID_TARGET_ROLES)
        self.assertEqual(selected_roles("TNN"), ["TNN"])

    def test_tnn_surface_runs_without_neuralforge_dependency(self):
        env = os.environ.copy()
        env.pop("NEURALFORGE_ROOT", None)
        result = subprocess.run(
            [sys.executable, str(TNN_ROOT / "tnn_surface.py"), "--intent", "self-contained", "--json"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        packet = json.loads(result.stdout)
        self.assertEqual(packet["role"], "TNN")
        self.assertTrue(packet["self_contained"])
        self.assertFalse(packet["neuralforge_required"])
        self.assertIn("Runtime: NexusGate-local self-contained core", packet["response"])

    def test_refresh_from_neuralforge_is_explicit_optional(self):
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
            result = subprocess.run(
                [
                    sys.executable,
                    str(TNN_ROOT / "refresh_from_neuralforge.py"),
                    "--neuralforge-root",
                    str(root),
                    "--json",
                ],
                cwd=str(TNN_ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            packet = json.loads(result.stdout)
            self.assertTrue(packet["refreshed"])
            bundle = json.loads((TNN_ROOT / "receipts" / "receipt_bundle_latest.json").read_text(encoding="utf-8-sig"))
            self.assertTrue(bundle["self_contained"])
            self.assertFalse(bundle["neuralforge_required"])
            self.assertIn("control_bundle", bundle["receipts"])

    def test_nn_router_can_build_tnn_response(self):
        response = build_tesseract_neural_network_response("status")
        self.assertEqual(response["role"], "TNN")
        self.assertEqual(response["model"], "Tesseract Neural Network/self-contained-receipt-core")
        self.assertTrue(response["self_contained"])
        self.assertFalse(response["neuralforge_required"])


if __name__ == "__main__":
    unittest.main()
