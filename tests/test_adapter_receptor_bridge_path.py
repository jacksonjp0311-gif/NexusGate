import unittest

from nexus_gate.adapters.local_demo import LocalDemoAdapter
from nexus_gate.receptors.compatibility import evaluate_compatibility
from nexus_gate.receptors.registry import load_receptor_manifests
from nexus_gate.runtime.router import NexusRouter


class TestAdapterReceptorBridgePath(unittest.TestCase):
    def test_adapter_to_receptor_bridge_path(self):
        adapter = LocalDemoAdapter()
        packet = adapter.normalize_event({"packet_id": "bridge-path-1", "event_type": "demo.message", "message": "bridge path", "requested_action": "read_only_signal"})
        route = NexusRouter().route(packet)
        receptor = load_receptor_manifests("registry/receptors.local_demo.v0.1.8.json")[0]
        compatibility = evaluate_compatibility(packet, receptor)
        self.assertEqual(route.mode, "engage")
        self.assertEqual(compatibility.mode, "compatible")
        self.assertEqual(compatibility.receptor_id, "local.demo.readonly")


if __name__ == "__main__":
    unittest.main()
