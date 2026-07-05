import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronHiddenOllamaBackend(unittest.TestCase):
    def test_main_starts_hidden_ollama_backend(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        self.assertIn("ensureOllamaBackend", main)
        self.assertIn("ollamaTagsReady", main)
        self.assertIn('spawn(binary, ["serve"]', main)
        self.assertIn("detached: true", main)
        self.assertIn('stdio: "ignore"', main)
        self.assertIn("windowsHide: true", main)
        self.assertIn("await ensureOllamaBackend();", main)
        self.assertIn('ipcMain.handle("nexus:ensureOllama"', main)
        self.assertNotIn("exec(", main)
        self.assertNotIn("execFile(", main)

    def test_hidden_backend_is_cpu_stable_and_local_only(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        client = (ROOT / "nexus_gate" / "nn_router" / "ollama_client.py").read_text(encoding="utf-8-sig")
        self.assertIn("CUDA_VISIBLE_DEVICES", main)
        self.assertIn("NEXUS_OLLAMA_NUM_GPU", main)
        self.assertIn("127.0.0.1:11434", main)
        self.assertIn('"num_gpu"', client)
        self.assertIn("NEXUS_OLLAMA_NUM_GPU", client)

    def test_preload_and_renderer_surface_backend_status(self):
        preload = (ROOT / "electron" / "preload.js").read_text(encoding="utf-8-sig")
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("ensureOllama", preload)
        self.assertIn('ipcRenderer.invoke("nexus:ensureOllama")', preload)
        self.assertIn("ensureLocalOllamaBackend", renderer)
        self.assertIn("window.nexus.ensureOllama", renderer)


if __name__ == "__main__":
    unittest.main()
