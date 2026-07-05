import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestGeometricMemoryRouterV083(unittest.TestCase):
    def test_main_readme_rehydrates_geometry_layer(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertLess(len(readme.splitlines()), 220)
        self.assertIn("v0.8.1 UI cleanup line", readme)
        self.assertIn("Geometric Memory Router", readme)
        self.assertIn("Intent -> Evidence -> Authority -> Context", readme)
        self.assertIn("LFTE depth typing + EIMT drift gate + RCMA latent remap + TRAT attractor score", readme)
        self.assertIn("NEXUS_GEOMETRIC_MEMORY_ROUTER.md", readme)
        self.assertIn("nexus_geometric_memory_manifest.v0.8.3.json", readme)

    def test_geometry_docs_exist_and_preserve_boundaries(self):
        router = (ROOT / "docs" / "intelligence" / "NEXUS_GEOMETRIC_MEMORY_ROUTER.md").read_text(encoding="utf-8")
        kernel = (ROOT / "docs" / "algorithms" / "NEXUS_TESSERACT_ALIGNMENT_KERNEL.md").read_text(encoding="utf-8")
        memory = (ROOT / "docs" / "memory" / "EIMT_RUNTIME_MEMORY_CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn("LFTE", router)
        self.assertIn("EIMT", router)
        self.assertIn("RCMA", router)
        self.assertIn("TRAT", router)
        self.assertIn("It does not train Mistral", router)
        self.assertIn("K = Intent x Evidence x Authority x Context", kernel)
        self.assertIn("geometry_pass", kernel)
        self.assertIn("DriftGate", memory)
        self.assertIn("SourceFallback", memory)

    def test_manifest_contract(self):
        manifest = json.loads((ROOT / "state" / "nexus_geometric_memory_manifest.v0.8.3.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.8.3A")
        self.assertEqual(manifest["status"], "contract_first_not_runtime_autonomy")
        self.assertEqual([axis["name"] for axis in manifest["axes"]], ["Intent", "Evidence", "Authority", "Context"])
        self.assertEqual(manifest["gates"]["model_output"], "recommendation_only")
        self.assertEqual(manifest["gates"]["repo_mutation"], "human_authorized_only")
        self.assertEqual(manifest["gates"]["model_weight_change"], "blocked_until_separate_tuning_protocol")

    def test_entrypoints_and_algorithms_reference_geometry(self):
        entry = (ROOT / "docs" / "ENTRYPOINTS.md").read_text(encoding="utf-8")
        alg = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8")
        self.assertIn("Geometric Memory Router", entry)
        self.assertIn("NEXUS_GEOMETRIC_MEMORY_ROUTER.md", entry)
        self.assertIn("Geometric Memory Router Algorithm", alg)
        self.assertIn("Models recommend. Memory orients. Geometry constrains. Evidence gates. Humans authorize compounding.", alg)


if __name__ == "__main__":
    unittest.main()
