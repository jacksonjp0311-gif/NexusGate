import os
import unittest
from unittest.mock import patch
from urllib.error import URLError

from nexus_gate.nn_router import ollama_client


class TestAdaptiveCpuOllama(unittest.TestCase):
    def test_role_limits_are_cpu_bounded(self):
        self.assertEqual(ollama_client._role_limits("FAST")["num_ctx"], 1024)
        self.assertEqual(ollama_client._role_limits("FAST")["num_predict"], 96)
        self.assertGreaterEqual(ollama_client._role_limits("DEEP")["timeout"], 240)

    def test_bad_env_int_falls_back(self):
        with patch.dict(os.environ, {"NEXUS_OLLAMA_NUM_GPU": ""}, clear=False):
            self.assertEqual(ollama_client._env_int("NEXUS_OLLAMA_NUM_GPU", 0), 0)

    def test_timeout_response_contains_runtime_options(self):
        with patch("urllib.request.urlopen", side_effect=URLError("timed out")):
            result = ollama_client.call_local_ollama(
                model="phi3:mini",
                intent="hello",
                role="FAST",
            )
        self.assertFalse(result["ok"])
        self.assertIn("timed out", result["error"])
        self.assertEqual(result["runtime_options"]["num_gpu"], 0)
        self.assertLessEqual(result["runtime_options"]["num_ctx"], 1024)
        self.assertLessEqual(result["runtime_options"]["num_predict"], 96)


if __name__ == "__main__":
    unittest.main()
