import unittest
from pathlib import Path

from nexus_gate.compiler.compiler import NexusCompiler, REQUIRED_PATHS


ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8-sig")


class TestNexusCellCompilerVisibilityV084(unittest.TestCase):
    def test_required_paths_include_nexuscell_surfaces(self):
        for rel in [
            "NexusCell/README.md",
            "docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md",
            "docs/nexus_cell/NEXUS_CELL_PLANNER.md",
            "state/nexus_cell/cell_manifest.v0.8.4.json",
            "nexus_gate/nexus_cell/plan.py",
        ]:
            self.assertIn(rel, REQUIRED_PATHS)

    def test_compiler_gate_passes_directly(self):
        compiler = NexusCompiler(ROOT)
        compiler.gate_nexus_cell_planner_visibility()
        self.assertEqual(len(compiler.gates), 1)
        gate = compiler.gates[0]
        self.assertEqual(gate.gate, "nexus_cell_planner_visibility")
        self.assertEqual(gate.status, "pass")
        self.assertIn(gate.evidence["status"], {"compiler_visible_planner_no_execution", "context_bridge_visible_no_execution", "operator_shell_visible_no_execution"})

    def test_docs_record_compiler_visibility_boundary(self):
        doc = read("docs/nexus_cell/NEXUS_CELL_COMPILER_VISIBILITY.md")
        self.assertIn("Compiler visibility is not execution authority.", doc)
        arch = read("docs/nexus_cell/NEXUS_CELL_ARCHITECTURE.md")
        self.assertIn("## v0.8.4D Compiler Visibility Seal", arch)


if __name__ == "__main__":
    unittest.main()

