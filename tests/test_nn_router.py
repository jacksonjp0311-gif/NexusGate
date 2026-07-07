import json
import tempfile
import unittest
from pathlib import Path

from nexus_gate.nn_router.contract import SAFETY_CONTRACT, build_policy_manifest, choose_model
from nexus_gate.nn_router.detect import assign_roles, detect_ollama_inventory
from nexus_gate.nn_router.compile import build_distribution


class TestNexusNNRouter(unittest.TestCase):
    def _write_manifest(self, root: Path, model: str, tag: str) -> None:
        manifest = root / "manifests" / "registry.ollama.ai" / "library" / model / tag
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({
            "schemaVersion": 2,
            "config": {"digest": "sha256:" + ("a" * 64)},
            "layers": [{"digest": "sha256:" + ("b" * 64)}],
        }), encoding="utf-8")

    def test_safety_contract_blocks_authority(self):
        self.assertTrue(SAFETY_CONTRACT["recommendation_only"])
        self.assertFalse(SAFETY_CONTRACT["model_grants_authority"])
        self.assertFalse(SAFETY_CONTRACT["model_output_executes_tools"])
        self.assertFalse(SAFETY_CONTRACT["model_output_mutates_files"])
        self.assertFalse(SAFETY_CONTRACT["arbitrary_shell_allowed"])
        self.assertFalse(SAFETY_CONTRACT["secrets_access_allowed"])
        self.assertFalse(SAFETY_CONTRACT["external_api_writes_allowed"])
        self.assertTrue(SAFETY_CONTRACT["role_targeting_required_for_deep_calls"])

    def test_choose_model_prefers_phi4_for_fast(self):
        inventory = {"tnn-phi4-mini:latest": {"name": "tnn-phi4-mini:latest"}}
        assignment = choose_model(inventory, "FAST")
        self.assertTrue(assignment.available)
        self.assertEqual(assignment.model, "tnn-phi4-mini:latest")

    def test_detect_fake_ollama_manifests_and_assign_roles(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_manifest(root, "tnn-phi4-mini", "latest")
            self._write_manifest(root, "mistral", "latest")
            inventory = detect_ollama_inventory(root)
            self.assertIn("tnn-phi4-mini:latest", inventory["models"])
            self.assertIn("mistral:latest", inventory["models"])
            roles = assign_roles(inventory)
            self.assertEqual(roles["FAST"]["model"], "tnn-phi4-mini:latest")
            self.assertEqual(roles["BALANCED"]["model"], "tnn-phi4-mini:latest")
            self.assertEqual(roles["DEEP"]["model"], "mistral:latest")
            self.assertTrue(roles["HANDOFF"]["available"])
            self.assertIsNone(roles["HANDOFF"]["model"])

    def test_build_distribution_does_not_require_local_model_call(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report = build_distribution(
                root=root,
                intent="What should we do next?",
                models_root=root / "missing-models",
                call_model=False,
            )
            self.assertEqual(report["version"], "0.6.4")
            self.assertEqual(report["intent"], "What should we do next?")
            self.assertEqual(report["model_responses"], [])
            self.assertEqual(report["authority_boundary"]["models"], "recommendation_only")
            self.assertEqual(report["target_role"], "ALL")

    def test_policy_manifest_contains_core_rules(self):
        policy = build_policy_manifest()
        self.assertIn("No authority, no mutation.", policy["router_law"])
        self.assertIn("No model output may directly execute tools or mutate files.", policy["router_law"])
        self.assertIn("DEEP", policy["valid_target_roles"])


if __name__ == "__main__":
    unittest.main()

