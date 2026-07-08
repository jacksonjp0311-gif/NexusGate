from __future__ import annotations

import unittest
from pathlib import Path

from nexus_gate.loops.registry import get_loop, list_loops, load_registry
from nexus_gate.loops.runner import build_loop_packet


class NexusMetaLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]

    def test_registry_loads_canonical_loops(self) -> None:
        registry = load_registry(self.root)
        loops = set(registry["loops"])
        self.assertIn("rhp-core", loops)
        self.assertIn("script-evolution", loops)
        self.assertIn("reflective-validation", loops)
        self.assertIn("failure-intelligence", loops)
        self.assertIn("validate-promote", loops)

    def test_list_loops_sorted(self) -> None:
        loops = list_loops(self.root)
        self.assertEqual(loops, sorted(loops))
        self.assertIn("rhp-core", loops)

    def test_rhp_core_reads_root_readme(self) -> None:
        loop = get_loop(self.root, "rhp-core")
        paths = [stage.get("path") for stage in loop["stages"] if stage.get("type") == "read"]
        self.assertIn("README.md", paths)

    def test_packet_without_execute_plans_commands(self) -> None:
        packet = build_loop_packet(
            root=self.root,
            loop_name="validate-promote",
            intent="unit test",
            execute=False,
            human_authorized=False,
        )
        self.assertEqual(packet["status"], "pass")
        command_stages = [stage for stage in packet["stages"] if stage["type"] == "command"]
        self.assertTrue(command_stages)
        self.assertTrue(all(stage["status"] == "planned" for stage in command_stages))
        self.assertTrue(all(stage["execution"]["executed"] is False for stage in command_stages))


if __name__ == "__main__":
    unittest.main()