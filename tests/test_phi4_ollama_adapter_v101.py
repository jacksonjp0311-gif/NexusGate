from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestPhi4OllamaAdapterV101(unittest.TestCase):
    def test_info_outputs_single_json_contract(self):
        proc = subprocess.run(
            [sys.executable, "-m", "nexus_gate.loops.phi4_ollama_adapter", "--info"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertEqual(packet["schema"], "NEXUS_PHI4_OLLAMA_ADAPTER.v1.0.1")
        self.assertEqual(packet["stdout_contract"], "single_json_object_only")

    def test_self_test_outputs_required_advice_keys(self):
        proc = subprocess.run(
            [sys.executable, "-m", "nexus_gate.loops.phi4_ollama_adapter", "--self-test"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        advice = json.loads(proc.stdout)
        for key in ["diagnosis", "repair_surface", "repair_type", "patch_intent", "rerun_gate", "confidence", "requires_human_authorization"]:
            self.assertIn(key, advice)

    def test_phi_wound_default_command_normalizes_orange_launcher(self):
        from nexus_gate.loops.phi_wound_advisor import _normalize_phi_command
        cmd = _normalize_phi_command('"C:\\Users\\jacks\\OneDrive\\Desktop\\Phi4Mini-OrangeCLI\\Launch-Phi4MiniCLI.cmd"')
        self.assertIn("nexus_gate.loops.phi4_ollama_adapter", cmd)
        self.assertIn("--prompt-file", cmd)


if __name__ == "__main__":
    unittest.main()
