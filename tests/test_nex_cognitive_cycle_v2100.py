from __future__ import annotations

import unittest
from pathlib import Path

from nexus_gate.nex_core.build import build_inner_context, damped_diffusion
from nexus_gate.nex_core.chat import answer_nex_core


ROOT = Path(__file__).resolve().parents[1]


class NexCognitiveCycleV2100Tests(unittest.TestCase):
    def test_damped_diffusion_converges_and_parallel_paths_split(self) -> None:
        result = damped_diffusion(
            ["s", "a", "b", "z"],
            [("s", "a", 1.0), ("s", "b", 1.0), ("a", "z", 1.0), ("b", "z", 1.0)],
            {"s": 1.0},
            maximum_iterations=20,
        )
        self.assertLessEqual(result["iterations"], 20)
        self.assertAlmostEqual(result["activations"]["a"], result["activations"]["b"], places=6)
        self.assertAlmostEqual(result["contraction_error_bound_after_20"], 0.82**20, places=5)

    def test_contradiction_and_uncertainty_lower_final_score(self) -> None:
        base = damped_diffusion(["s", "x"], [("s", "x", 1.0)], {"s": 1.0})
        reduced = damped_diffusion(["s", "x"], [("s", "x", 1.0)], {"s": 1.0}, contradiction={"x": 0.2}, uncertainty={"x": 0.1})
        self.assertLess(reduced["activations"]["x"], base["activations"]["x"])

    def test_answer_closes_cycle_and_preserves_authority(self) -> None:
        packet = answer_nex_core(ROOT, "What is NEXUS permitted to learn?")
        self.assertEqual(packet["schema"], "NEXUS_NEX_CORE_RESPONSE.v2.10.0")
        self.assertEqual(packet["mode"], "NEX_CORE")
        self.assertFalse(packet["authority_boundary"]["may_execute"])
        self.assertGreaterEqual(packet["inner_trace"]["message_count"], 1)


if __name__ == "__main__":
    unittest.main()
