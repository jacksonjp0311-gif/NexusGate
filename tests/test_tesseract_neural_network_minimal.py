import json
import os
import subprocess
import sys
from pathlib import Path
import unittest

from nexus_gate.nn_router.contract import VALID_TARGET_ROLES, selected_roles

ROOT = Path(__file__).resolve().parents[1]
TNN_ROOT = ROOT / "Tesseract Neural Network"


class TesseractNeuralNetworkChatBrainTests(unittest.TestCase):
    def test_chat_brain_files_exist(self):
        for name in [
            "tnn_surface.py",
            "brain/chat_engine.py",
            "brain/ollama_adapter.py",
            "brain/context_builder.py",
            "brain/memory_store.py",
            "brain/system_prompt.md",
            "brain/Modelfile.tnn-mistral",
            "brain/build_tnn_mistral.ps1",
            "memory",
            "receipts/receipt_bundle_latest.json",
            "state/tnn_state_latest.json",
        ]:
            self.assertTrue((TNN_ROOT / name).exists(), name)

    def test_contract_contains_tnn_role(self):
        self.assertIn("TNN", VALID_TARGET_ROLES)
        self.assertEqual(selected_roles("TNN"), ["TNN"])

    def test_manifest_marks_mistral_chat_brain(self):
        data = json.loads((TNN_ROOT / "manifest.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(data["version"], "nexus.tesseract_neural_network.v0.2.0")
        self.assertEqual(data["backend"], "ollama/mistral")
        self.assertTrue(data["fast_chat_target"])
        self.assertFalse(data["external_neuralforge_required"])
        self.assertFalse(data["authority_boundary"]["raw_weight_copy"])

    def test_chat_engine_offline_path_is_bounded(self):
        env = os.environ.copy()
        env["TNN_OLLAMA_URL"] = "http://127.0.0.1:9"
        result = subprocess.run(
            [sys.executable, str(TNN_ROOT / "brain" / "chat_engine.py"), "--intent", "hello", "--json"],
            cwd=str(TNN_ROOT / "brain"),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        packet = json.loads(result.stdout)
        self.assertFalse(packet["ok"])
        self.assertIn("MODEL OFFLINE", packet["response"])
        self.assertIn("no shell execution", packet["boundary"])

    def test_tnn_surface_offline_path_returns_chat_packet(self):
        env = os.environ.copy()
        env["TNN_OLLAMA_URL"] = "http://127.0.0.1:9"
        result = subprocess.run(
            [sys.executable, str(TNN_ROOT / "tnn_surface.py"), "--intent", "think quickly", "--json"],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        packet = json.loads(result.stdout)
        self.assertEqual(packet["role"], "TNN")
        self.assertEqual(packet["model"], "Tesseract Neural Network/mistral-chat-brain")
        self.assertTrue(packet["self_contained"])
        self.assertFalse(packet["neuralforge_required"])
        self.assertIn("chat_packet", packet)
        self.assertIn("MODEL OFFLINE", packet["response"])


if __name__ == "__main__":
    unittest.main()
