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

    def tearDown(self):
        bundle_path = TNN_ROOT / "receipts" / "receipt_bundle_latest.json"
        state_path = TNN_ROOT / "state" / "tnn_state_latest.json"
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        bundle_path.write_text(json.dumps({
            "ok": True,
            "source": "nexusgate_local_seed",
            "root_found": True,
            "self_contained": True,
            "neuralforge_required": False,
            "receipts": {
                "source_intake": {
                    "ok": True,
                    "registry_allowed": True,
                    "live_pull_allowed": False,
                    "scraping_allowed": False,
                    "raw_collection_allowed": False,
                    "mutation_allowed": False,
                    "claim_boundary": "NexusGate-local TNN seed; no live network calls, scraping, raw collection, or mutation.",
                    "source_count": 0,
                    "source_intake_version": "tnn.local_seed.v0.1.1A"
                }
            },
            "missing_receipts": ["control_bundle", "approval", "sandbox_plan"],
            "blocked_reasons": [],
            "tnn_version": "nexus.tesseract_neural_network.v0.1.1AAA",
            "claim_boundary": "NexusGate-local seed bundle. No external source is required at runtime."
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        state_path.write_text(json.dumps({
            "ok": True,
            "role": "TNN",
            "model": "Tesseract Neural Network/self-contained-receipt-core",
            "tnn_version": "nexus.tesseract_neural_network.v0.1.1AAA",
            "self_contained": True,
            "neuralforge_required": False,
            "local_bundle": "receipts/receipt_bundle_latest.json",
            "source": "nexusgate_local_seed"
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

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
