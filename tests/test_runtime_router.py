import unittest
from nexus_gate.core.packets import StatePacket
from nexus_gate.runtime.router import NexusRouter


class TestNexusGateRuntime(unittest.TestCase):
    def test_missing_schema_rejects(self):
        packet = StatePacket("p1", "test", "unit", "", "0.1.3", "read_only_signal", {})
        self.assertEqual(NexusRouter().route(packet).mode, "reject")

    def test_unverified_tool_call_shadows(self):
        packet = StatePacket("p2", "test", "unit", "NEXUS_STATE_PACKET", "0.1.3", "tool_call", {}, authority_scope=[])
        self.assertEqual(NexusRouter().route(packet).mode, "shadow")

    def test_read_only_engages(self):
        packet = StatePacket("p3", "test", "unit", "NEXUS_STATE_PACKET", "0.1.3", "read_only_signal", {})
        self.assertEqual(NexusRouter().route(packet).mode, "engage")


if __name__ == "__main__":
    unittest.main()
