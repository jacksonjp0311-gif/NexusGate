import json
import unittest
from pathlib import Path

from nexus_gate.nexus_shell.shell import NEXUS_SHELL_COMMANDS, build_shell_packet
from nexus_gate.compiler.compiler import NexusCompiler, REQUIRED_PATHS


ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8-sig")


class TestNexusShellOperatorV086(unittest.TestCase):
    def test_shell_packet_is_no_execution_operator(self):
        packet = build_shell_packet(ROOT, "inspect docs only", command="status", context_limit=6)
        self.assertEqual(packet["version"], "0.8.6")
        self.assertEqual(packet["mode"], "nexus_shell_operator_no_execution")
        self.assertFalse(packet["boundary"]["execution_enabled"])
        self.assertFalse(packet["boundary"]["shell_mutation_enabled"])
        self.assertLessEqual(packet["context_bridge"]["context_ref_count"], 6)

    def test_shell_commands_cover_full_scope(self):
        for command in ["status", "rehydrate", "compile", "doctor", "cell-plan", "cell-context", "handoff", "help"]:
            self.assertIn(command, NEXUS_SHELL_COMMANDS)

    def test_manifest_and_surfaces_expose_shell(self):
        manifest = json.loads(read("state/nexus_shell/shell_manifest.v0.8.6.json"))
        self.assertEqual(manifest["version"], "v0.8.6")
        self.assertEqual(manifest["status"], "operator_shell_visible_no_execution")
        self.assertTrue(manifest["nexus_shell"]["enabled"])
        self.assertIn("shell", read("scripts/nexus.ps1"))
        self.assertIn("[11] NexusShell / Operator", read("scripts/desktop/open_nexus_gate_console.ps1"))

    def test_required_paths_and_compiler_gate(self):
        for rel in [
            "NexusShell/README.md",
            "docs/nexus_shell/NEXUS_SHELL_OPERATOR.md",
            "state/nexus_shell/shell_manifest.v0.8.6.json",
            "nexus_gate/nexus_shell/shell.py",
        ]:
            self.assertIn(rel, REQUIRED_PATHS)
        compiler = NexusCompiler(ROOT)
        compiler.gate_nexus_shell_operator_visibility()
        self.assertEqual(compiler.gates[0].status, "pass")

    def test_docs_record_shell_boundary(self):
        doc = read("docs/nexus_shell/NEXUS_SHELL_OPERATOR.md")
        self.assertIn("It does not execute arbitrary commands.", doc)
        arch = read("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md")
        self.assertIn("## v0.8.6 NexusShell Operator Seal", arch)


if __name__ == "__main__":
    unittest.main()
