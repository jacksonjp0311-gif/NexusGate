import unittest

from nexus_gate.bridge.compile import compile_bridge_session
from nexus_gate.bridge.session import BridgeSessionRunner


class TestBridgeSessionRunner(unittest.TestCase):
    def test_readonly_bridge_engages(self):
        runner = BridgeSessionRunner()
        report = runner.run({
            "session_id": "test-readonly",
            "packet_id": "test-readonly-packet",
            "event_type": "demo.message",
            "requested_action": "read_only_signal",
        })
        self.assertEqual(report.route_mode, "engage")
        self.assertEqual(report.compatibility_mode, "compatible")
        self.assertEqual(report.final_mode, "engage")

    def test_tool_without_authority_shadows(self):
        runner = BridgeSessionRunner()
        report = runner.run({
            "session_id": "test-tool",
            "packet_id": "test-tool-packet",
            "event_type": "demo.tool_request",
            "requested_action": "tool_call",
            "authority_scope": [],
        })
        self.assertEqual(report.final_mode, "shadow")

    def test_unsupported_schema_rejects(self):
        runner = BridgeSessionRunner()
        report = runner.run({
            "session_id": "test-schema",
            "packet_id": "test-schema-packet",
            "event_type": "demo.message",
            "schema_id": "UNKNOWN_SCHEMA",
            "requested_action": "read_only_signal",
        })
        self.assertEqual(report.final_mode, "reject")

    def test_bridge_compiler_passes(self):
        report = compile_bridge_session(".")
        self.assertEqual(report.status, "pass")


if __name__ == "__main__":
    unittest.main()
