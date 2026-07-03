import tempfile
import unittest
from pathlib import Path

from nexus_gate.compiler.compiler import NexusCompiler
from nexus_gate.compiler.gates import GateResult


class TestNexusGateCompilerContracts(unittest.TestCase):
    def test_gate_result_flags(self):
        passed = GateResult(gate="demo", status="pass", message="ok")
        failed = GateResult(gate="demo", status="fail", message="bad")
        self.assertTrue(passed.passed)
        self.assertFalse(passed.failed)
        self.assertTrue(failed.failed)

    def test_compiler_constructs(self):
        compiler = NexusCompiler(Path.cwd())
        self.assertIsNotNone(compiler.root)


if __name__ == "__main__":
    unittest.main()