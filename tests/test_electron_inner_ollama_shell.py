import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestNexInnerOllamaShell(unittest.TestCase):
    def test_desktop_portal_starts_inner_ollama_before_electron(self):
        portal = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("function Start-OllamaInnerBackend", portal)
        self.assertIn("Test-OllamaEndpoint", portal)
        self.assertIn("CreateNoWindow", portal)
        self.assertIn("NEXUS_OLLAMA_NUM_GPU", portal)
        self.assertIn("CUDA_VISIBLE_DEVICES", portal)
        self.assertIn("Opening Electron UI with npm start", portal)
        self.assertLess(portal.index("Start-OllamaInnerBackend"), portal.index("Opening Electron UI with npm start"))

    def test_electron_single_instance_and_focus_guard(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        self.assertIn("requestSingleInstanceLock", main)
        self.assertIn("second-instance", main)
        self.assertIn("mainWindow", main)
        self.assertIn("mainWindow.focus()", main)
        self.assertIn("if (!gotSingleInstanceLock) return;", main)

    def test_nex_python_child_receives_cpu_env_and_models_path(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        self.assertIn("function runNexPython", main)
        self.assertIn("OLLAMA_MODELS", main)
        self.assertIn("resolveOllamaModels()", main)
        self.assertIn("CUDA_VISIBLE_DEVICES", main)
        self.assertIn("NEXUS_OLLAMA_NUM_GPU", main)
        self.assertIn("activeNexChild = child", main)

    def test_ollama_client_safe_num_gpu_parse(self):
        client = (ROOT / "nexus_gate" / "nn_router" / "ollama_client.py").read_text(encoding="utf-8-sig")
        self.assertIn("def _env_int", client)
        self.assertIn('_env_int("NEXUS_OLLAMA_NUM_GPU", 0)', client)
        self.assertNotIn('int(os.environ.get("NEXUS_OLLAMA_NUM_GPU", "0"))', client)


if __name__ == "__main__":
    unittest.main()
