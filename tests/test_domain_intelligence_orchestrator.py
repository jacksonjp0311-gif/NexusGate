import json
import unittest
from pathlib import Path

from nexus_gate.domain.domain_intelligence import compile_domain_intelligence, write_domain_intelligence_report


ROOT = Path(__file__).resolve().parents[1]


class TestDomainIntelligenceOrchestrator(unittest.TestCase):
    def test_domain_docs_dirs_schemas_and_state_exist(self):
        self.assertTrue((ROOT / "docs/intelligence/DOMAIN_INTELLIGENCE_ORCHESTRATOR.md").exists())
        self.assertTrue((ROOT / "domains/README.md").exists())
        for domain in ["biology", "technology", "code", "math", "physics", "systems", "human_ai", "governance"]:
            self.assertTrue((ROOT / "domains" / domain / "README.md").exists(), domain)
        for schema in [
            "source_card.schema.json",
            "concept_card.schema.json",
            "claim_card.schema.json",
            "equation_card.schema.json",
            "simulation_card.schema.json",
            "code_pattern_card.schema.json",
            "orchestration_card.schema.json",
        ]:
            self.assertTrue((ROOT / "domains" / "_schemas" / schema).exists(), schema)
        data = json.loads((ROOT / "state/domain_intelligence_index.v0.4.0.json").read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "0.4.0")

    def test_domain_compiler_passes(self):
        report = compile_domain_intelligence(ROOT)
        self.assertEqual(report.status, "pass")
        self.assertIn("biology", report.domains)
        self.assertIn("unsupported_cross_domain_fact", report.blocked_claims)
        path = write_domain_intelligence_report(report, ROOT)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "pass")
        self.assertIn("scientific truth", data["claim_boundary"])

    def test_domain_command_lane_and_evolve_integration(self):
        ps = (ROOT / "scripts/nexus.ps1").read_text(encoding="utf-8")
        human = (ROOT / "scripts/nexus_human.ps1").read_text(encoding="utf-8")
        sh = (ROOT / "scripts/nexus.sh").read_text(encoding="utf-8")
        self.assertIn('"domain"', ps)
        self.assertIn("nexus_gate.domain.compile", human)
        self.assertIn("nexus_gate.domain.compile", sh)
        self.assertLess(human.index("nexus_gate.reflection.compile"), human.index("nexus_gate.domain.compile"))
        self.assertLess(human.index("nexus_gate.domain.compile"), human.index("nexus_gate.build.packer"))

    def test_domain_boundaries_exist(self):
        biology = (ROOT / "domains/biology/README.md").read_text(encoding="utf-8")
        math = (ROOT / "domains/math/README.md").read_text(encoding="utf-8")
        physics = (ROOT / "domains/physics/README.md").read_text(encoding="utf-8")
        code = (ROOT / "domains/code/README.md").read_text(encoding="utf-8")
        self.assertIn("not medical authority", biology)
        self.assertIn("unsafe wet-lab", biology)
        self.assertIn("conjecture", math)
        self.assertIn("theorem", math)
        self.assertIn("dimensional", physics)
        self.assertIn("simulation", physics)
        self.assertIn("tests", code)
        self.assertIn("production readiness", code)


if __name__ == "__main__":
    unittest.main()
