from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TestT3mp3stPortal(unittest.TestCase):
    def test_embedded_t3mp3st_root_exists(self):
        self.assertTrue((ROOT / "T3MP3ST" / "package.json").exists())
        self.assertTrue((ROOT / "T3MP3ST" / "README.md").exists())

    def test_electron_exposes_bounded_t3mp3st_hud(self):
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        preload = (ROOT / "electron" / "preload.js").read_text(encoding="utf-8-sig")
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")

        self.assertIn('id="tempest-popout"', html)
        self.assertIn('id="tempest-hud"', html)
        self.assertIn("T3MP3ST", html)
        self.assertIn(".tempest-button", css)
        self.assertIn(".tempest-hud", css)
        self.assertIn("bindMovableHud", renderer)
        self.assertIn("refreshTempestHud", renderer)
        self.assertIn("openTempestFullUi", preload)
        self.assertIn('ipcRenderer.invoke("nexus:openTempestFullUi")', preload)
        self.assertIn('ipcMain.handle("nexus:openTempestFullUi"', main)
        self.assertIn('path.join(repoRoot, "T3MP3ST")', main)
        self.assertIn("unauthorized_targeting", main)
        self.assertIn("arbitrary_shell_commands", main)
        self.assertNotIn("exec(", main)
        self.assertNotIn("execFile(", main)

    def test_spiral_core_portal_exposes_t3mp3st(self):
        portal = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("function Invoke-NexusT3mp3stPortal", portal)
        self.assertIn("[16] T3MP3ST", portal)
        self.assertIn('$choice -eq "16"', portal)
        self.assertIn('Join-Path $RepoRoot "T3MP3ST"', portal)
        self.assertIn("authorized security lab / War Room", portal)

    def test_docs_and_readme_name_t3mp3st(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        doc = (ROOT / "docs" / "runtime" / "NEXUS_T3MP3ST_PORTAL.md").read_text(encoding="utf-8-sig")
        self.assertIn("T3MP3ST", readme)
        self.assertIn("T3MP3ST is authorized-use-only", doc)
        self.assertIn("may not choose targets", doc)
        self.assertLess(len(readme.splitlines()), 220)


if __name__ == "__main__":
    unittest.main()
