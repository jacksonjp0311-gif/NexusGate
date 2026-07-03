import unittest

from nexus_gate.core.packets import StatePacket
from nexus_gate.runtime.router import NexusRouter


class TestNexusGateRuntime(unittest.TestCase):
    def test_missing_schema_rejects(self):
        packet = StatePacket(
            packet_id="p1",
            source_framework="test",
            source_surface="unit",
            schema_id="",
            schema_version="0.1.0",
            requested_action="read_only_signal",
            payload={},
        )
        decision = NexusRouter().route(packet)
        self.assertEqual(decision.mode, "reject")

    def test_unverified_tool_call_shadows(self):
        packet = StatePacket(
            packet_id="p2",
            source_framework="test",
            source_surface="unit",
            schema_id="NEXUS_STATE_PACKET",
            schema_version="0.1.0",
            requested_action="tool_call",
            payload={},
            authority_scope=[],
        )
        decision = NexusRouter().route(packet)
        self.assertEqual(decision.mode, "shadow")

    def test_read_only_engages_in_minimal_scaffold(self):
        packet = StatePacket(
            packet_id="p3",
            source_framework="test",
            source_surface="unit",
            schema_id="NEXUS_STATE_PACKET",
            schema_version="0.1.0",
            requested_action="read_only_signal",
            payload={},
            authority_scope=[],
        )
        decision = NexusRouter().route(packet)
        self.assertEqual(decision.mode, "engage")


if __name__ == "__main__":
    unittest.main()