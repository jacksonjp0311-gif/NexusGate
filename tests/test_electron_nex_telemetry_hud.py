import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronNexTelemetryHud(unittest.TestCase):
    def test_index_has_stop_and_telemetry_hud(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        self.assertIn('id="nex-stop-button"', html)
        self.assertIn("Stop<br>Transmission", html)
        self.assertIn('id="telemetry-popout"', html)
        self.assertIn('id="telemetry-hud"', html)
        self.assertIn("System Monitor Station", html)
        self.assertIn("Cyber Security - TEMPEST", html)
        self.assertIn('data-telemetry-tab="tempest"', html)
        self.assertNotIn('id="hud-telemetry-raw"', html)

    def test_preload_exposes_bounded_telemetry_and_stop(self):
        preload = (ROOT / "electron" / "preload.js").read_text(encoding="utf-8-sig")
        self.assertIn("stopNex", preload)
        self.assertIn("getTelemetry", preload)
        self.assertIn("terminateProcess", preload)
        self.assertIn('ipcRenderer.invoke("nexus:stopNex")', preload)
        self.assertIn('ipcRenderer.invoke("nexus:getTelemetry")', preload)
        self.assertIn('ipcRenderer.invoke("nexus:terminateProcess"', preload)

    def test_main_has_read_only_telemetry_and_cpu_fallback(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        self.assertIn('ipcMain.handle("nexus:getTelemetry"', main)
        self.assertIn('ipcMain.handle("nexus:terminateProcess"', main)
        self.assertIn('ipcMain.handle("nexus:stopNex"', main)
        self.assertIn("activeNexChild", main)
        self.assertIn("CUDA_VISIBLE_DEVICES", main)
        self.assertIn("NEXUS_OLLAMA_NUM_GPU", main)
        self.assertIn("Read-only local telemetry", main)
        self.assertIn("top_cpu_processes", main)
        self.assertIn("network_adapters", main)
        self.assertIn("buildTelemetryAnalysis", main)
        self.assertIn("terminateFixedProcess", main)
        self.assertIn("PROTECTED_PROCESS_NAMES", main)
        self.assertIn("task_manager_processes", main)
        self.assertIn("cyber_security_tempest", main)
        self.assertNotIn("exec(", main)
        self.assertNotIn("execFile(", main)

    def test_renderer_has_stable_chat_and_telemetry_handlers(self):
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        self.assertIn("refreshTelemetry", renderer)
        self.assertIn("toggleTelemetryHud", renderer)
        self.assertIn("Transmission stop requested", renderer)
        self.assertIn("window.nexus.stopNex", renderer)
        self.assertIn("window.nexus.getTelemetry", renderer)
        self.assertIn("activateTelemetryTab", renderer)
        self.assertIn("renderTelemetryRows", renderer)
        self.assertIn("renderProcessManagerRows", renderer)
        self.assertIn("requestTerminateProcess", renderer)
        self.assertIn("data-terminate-pid", renderer)
        self.assertNotIn("hud-telemetry-raw", renderer)

    def test_styles_have_cyberpunk_controls(self):
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn(".stop-transmission", css)
        self.assertIn(".telemetry-hud", css)
        self.assertIn("NEXUS v0.9.8: expanded System Monitor HUD", css)
        self.assertIn(".telemetry-tabs", css)
        self.assertIn(".process-manager-row", css)
        self.assertIn("max-height: calc(100vh - 350px)", css)
        self.assertIn("max-height: calc(100vh - 372px)", css)
        self.assertIn("position: sticky", css)
        self.assertIn(".terminate-process-button", css)
        self.assertIn(".tempest-panel", css)
        self.assertIn(".transmission-actions", css)
        self.assertIn("max-height: 230px", css)
        self.assertIn("rgba(250, 204, 21", css)
        self.assertNotIn("#hud-telemetry-raw", css)

    def test_ollama_client_defaults_to_cpu_gpu_zero(self):
        client = (ROOT / "nexus_gate" / "nn_router" / "ollama_client.py").read_text(encoding="utf-8-sig")
        self.assertIn('"num_gpu"', client)
        self.assertIn("NEXUS_OLLAMA_NUM_GPU", client)


if __name__ == "__main__":
    unittest.main()
