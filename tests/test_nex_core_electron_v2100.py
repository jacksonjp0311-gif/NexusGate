from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NexCoreElectronV2100Tests(unittest.TestCase):
    def test_selector_and_preload_expose_nex_core(self) -> None:
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        preload = (ROOT / "electron" / "preload.js").read_text(encoding="utf-8")
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")
        self.assertIn('value="NEX_CORE"', html)
        self.assertIn("askNexCore", preload)
        self.assertIn("window.nexus.askNexCore", renderer)
        self.assertIn("NEX CORE -> NGLM", renderer)

    def test_nex_core_bypasses_model_bridge_and_ollama_startup(self) -> None:
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8")
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")
        self.assertIn('ipcMain.handle("nexus:askNexCore"', main)
        self.assertIn('"nexus_gate.nex_core.cli"', main)
        self.assertIn('"nexus_gate.nn_router.compile"', main)
        ready_block = main.split("app.whenReady().then", 1)[1].split("app.on(\"window-all-closed\"", 1)[0]
        self.assertNotIn("ensureOllamaBackend", ready_block)
        nex_branch = renderer.split('if (role === "NEX_CORE")', 1)[1].split("// Offline graceful degradation", 1)[0]
        self.assertNotIn("ensureLocalOllamaBackend", nex_branch)
        self.assertNotIn("askNex({", nex_branch)

    def test_inner_trace_panel_has_no_hidden_reasoning_field(self) -> None:
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")
        self.assertIn("nex-core-status-panel", html)
        self.assertNotIn("chain-of-thought", html.lower())


if __name__ == "__main__":
    unittest.main()
