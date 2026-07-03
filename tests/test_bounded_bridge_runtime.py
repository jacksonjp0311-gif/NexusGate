import unittest

from nexus_gate.bridge.runtime import BoundedBridgeRuntime, demo_events
from nexus_gate.bridge.runtime_compiler import compile_bounded_runtime


class TestBoundedBridgeRuntime(unittest.TestCase):
    def test_runtime_counts_engage_shadow_reject(self):
        runtime = BoundedBridgeRuntime(max_events=3)
        report = runtime.run_batch(demo_events(), runtime_id="unit-runtime")
        self.assertEqual(report.summary_counts["engage"], 1)
        self.assertEqual(report.summary_counts["shadow"], 1)
        self.assertEqual(report.summary_counts["reject"], 1)
        self.assertEqual(report.status, "pass")

    def test_runtime_truncates_over_limit(self):
        runtime = BoundedBridgeRuntime(max_events=2)
        report = runtime.run_batch(demo_events(), runtime_id="unit-runtime-bounded")
        self.assertEqual(report.status, "bounded")
        self.assertEqual(report.processed_count, 2)
        self.assertEqual(report.truncated_count, 1)

    def test_runtime_compiler_passes(self):
        report = compile_bounded_runtime(".")
        self.assertEqual(report.status, "pass")


if __name__ == "__main__":
    unittest.main()
