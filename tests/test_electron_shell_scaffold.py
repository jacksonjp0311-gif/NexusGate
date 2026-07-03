import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronShellScaffold(unittest.TestCase):
    def test_scaffold_files_exist(self):
        for path in [
            "electron/README.md",
            "electron/package.json",
            "electron/main.js",
            "electron/preload.js",
            "electron/renderer/index.html",
            "electron/renderer/renderer.js",
            "electron/renderer/styles.css",
            "docs/ui/ELECTRON_SHELL_SCAFFOLD.md",
            "state/electron_shell_scaffold_index.v0.3.3.json",
        ]:
            self.assertTrue((ROOT / path).exists(), path)

    def test_main_process_uses_electron_security_controls(self):
        text = (ROOT / "electron" / "main.js").read_text(encoding="utf-8")
        for marker in [
            "contextIsolation: true",
            "nodeIntegration: false",
            "sandbox: true",
            "shell: false",
            "ALLOWLISTED_COMMANDS",
            "READ_SURFACES",
            "scripts\", \"nexus.ps1",
        ]:
            self.assertIn(marker, text)
        self.assertNotIn("exec(", text)
        self.assertNotIn("execFile(", text)
        self.assertNotIn("shell: true", text)

    def test_preload_exposes_only_nexus_api(self):
        text = (ROOT / "electron" / "preload.js").read_text(encoding="utf-8")
        self.assertIn('contextBridge.exposeInMainWorld("nexus"', text)
        self.assertIn("readSurface", text)
        self.assertIn("surfaceExists", text)
        self.assertIn("runLane", text)
        self.assertIn("getContract", text)
        self.assertNotIn("require(\"fs\")", text)
        self.assertNotIn("child_process", text)

    def test_package_is_private_scaffold(self):
        data = json.loads((ROOT / "electron" / "package.json").read_text(encoding="utf-8"))
        self.assertTrue(data["private"])
        self.assertEqual(data["main"], "main.js")
        self.assertIn("electron", data["devDependencies"])
        self.assertIn("smoke", data["scripts"])

    def test_scaffold_index_matches_read_contract_allowlist(self):
        scaffold = json.loads(
            (ROOT / "state" / "electron_shell_scaffold_index.v0.3.3.json").read_text(
                encoding="utf-8"
            )
        )
        contract = json.loads(
            (ROOT / "state" / "electron_read_contract_index.v0.3.2.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            set(scaffold["allowlisted_commands"]),
            set(contract["allowlisted_commands"]),
        )
        self.assertIn("spawn_shell_false", scaffold["security_controls"])
        self.assertIn("no_exec", scaffold["security_controls"])
        self.assertIn("local runtime", scaffold["claim_boundary"])
        self.assertIn("not packaged", scaffold["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
