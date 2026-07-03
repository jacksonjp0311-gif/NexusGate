import unittest

from nexus_gate.adapters.compile import compile_adapter_registry
from nexus_gate.adapters.local_demo import LocalDemoAdapter
from nexus_gate.adapters.registry import AdapterRegistry
from nexus_gate.runtime.router import NexusRouter


class TestAdapterRegistry(unittest.TestCase):
    def test_local_demo_manifest_registers(self):
        adapter = LocalDemoAdapter()
        registry = AdapterRegistry()
        entry = registry.register(adapter.manifest())
        self.assertEqual(entry.manifest.adapter_id, "local.demo")

    def test_local_demo_normalizes_and_routes_readonly(self):
        adapter = LocalDemoAdapter()
        packet = adapter.normalize_event({
            "packet_id": "demo-1",
            "message": "hello",
            "requested_action": "read_only_signal",
        })
        decision = NexusRouter().route(packet)
        self.assertEqual(packet.source_framework, "LocalDemo")
        self.assertEqual(decision.mode, "engage")

    def test_local_demo_tool_call_shadows_without_authority(self):
        adapter = LocalDemoAdapter()
        packet = adapter.normalize_event({
            "packet_id": "demo-2",
            "requested_action": "tool_call",
            "authority_scope": [],
        })
        decision = NexusRouter().route(packet)
        self.assertEqual(decision.mode, "shadow")

    def test_adapter_compiler_passes(self):
        report = compile_adapter_registry(".")
        self.assertEqual(report.status, "pass")


if __name__ == "__main__":
    unittest.main()
