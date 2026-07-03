import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestDualShellRuntime(unittest.TestCase):
    def test_powershell_and_bash_pairs_exist(self):
        names = [
            "nexus_compile",
            "nexus_once",
            "nexus_dev_loop",
            "nexus_watch",
            "nexus_status",
            "nexus_promote",
        ]
        for name in names:
            self.assertTrue((ROOT / "scripts" / f"{name}.ps1").exists(), name)
            self.assertTrue((ROOT / "scripts" / f"{name}.sh").exists(), name)

    def test_compile_loop_promote_scripts_call_compiler(self):
        required = [
            "nexus_compile.ps1",
            "nexus_once.ps1",
            "nexus_dev_loop.ps1",
            "nexus_promote.ps1",
            "nexus_compile.sh",
            "nexus_once.sh",
            "nexus_dev_loop.sh",
            "nexus_promote.sh",
        ]
        for filename in required:
            text = (ROOT / "scripts" / filename).read_text(encoding="utf-8")
            self.assertIn("nexus_gate.compiler", text, filename)

    def test_readme_contains_dual_shell_rule(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Every new runtime loop must exist in both PowerShell and Bash.", text)
        self.assertIn("Every loop must run the gated compiler before it cycles, promotes, checkpoints, or claims a pass.", text)


if __name__ == "__main__":
    unittest.main()