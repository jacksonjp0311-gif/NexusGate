from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from nexus_gate.gitnexus_bridge.engine import compile_graph


class TestGitNexusBridge(unittest.TestCase):
    def test_compile_graph_extracts_python_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text(
                "import b\n\n"
                "def alpha():\n"
                "    return b.beta()\n",
                encoding="utf-8",
            )
            (root / "b.py").write_text(
                "def beta():\n"
                "    return 1\n",
                encoding="utf-8",
            )
            packet = compile_graph(root)
            self.assertTrue(packet["boundary"]["evidence_only"])
            self.assertFalse(packet["boundary"]["autonomous_authority"])
            self.assertGreaterEqual(packet["counts"]["files"], 2)
            self.assertGreaterEqual(packet["counts"]["symbols"], 2)
            self.assertGreaterEqual(packet["counts"]["edges"], 1)

    def test_packet_is_json_serializable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "x.js").write_text(
                "import './y.js';\n"
                "function run() {}\n",
                encoding="utf-8",
            )
            (root / "y.js").write_text(
                "export function y() { return 1 }\n",
                encoding="utf-8",
            )
            packet = compile_graph(root)
            blob = json.dumps(packet)
            self.assertIn("nexus.gitnexus_bridge", blob)


if __name__ == "__main__":
    unittest.main()
