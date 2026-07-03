import unittest

from nexus_gate.adapters.local_demo import LocalDemoAdapter
from nexus_gate.receptors.compatibility import evaluate_compatibility
from nexus_gate.receptors.compile import compile_receptor_registry
from nexus_gate.receptors.registry import ReceptorRegistry, load_receptor_manifests


class TestReceptorRegistry(unittest.TestCase):
    def test_receptor_manifests_register(self):
        registry = ReceptorRegistry()
        manifests = load_receptor_manifests("registry/receptors.local_demo.v0.1.8.json")
        entries = [registry.register(manifest) for manifest in manifests]
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].manifest.owner_adapter_id, "local.demo")

    def test_readonly_receptor_compatible(self):
        adapter = LocalDemoAdapter()
        packet = adapter.normalize_event({"packet_id": "r1", "requested_action": "read_only_signal"})
        receptor = load_receptor_manifests("registry/receptors.local_demo.v0.1.8.json")[0]
        decision = evaluate_compatibility(packet, receptor)
        self.assertEqual(decision.mode, "compatible")

    def test_tool_receptor_shadows_without_authority(self):
        adapter = LocalDemoAdapter()
        packet = adapter.normalize_event({"packet_id": "r2", "requested_action": "tool_call", "authority_scope": []})
        receptor = load_receptor_manifests("registry/receptors.local_demo.v0.1.8.json")[1]
        decision = evaluate_compatibility(packet, receptor)
        self.assertEqual(decision.mode, "shadow")
        self.assertEqual(decision.reason, "authority_required_missing")

    def test_receptor_compiler_passes(self):
        report = compile_receptor_registry(".")
        self.assertEqual(report.status, "pass")


if __name__ == "__main__":
    unittest.main()
