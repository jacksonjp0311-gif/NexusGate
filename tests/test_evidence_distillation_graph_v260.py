from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.distillation.graph import BLOCKED_ACTIONS, build_evidence_distillation_graph


ROOT = Path(__file__).resolve().parents[1]


class EvidenceDistillationGraphV260Tests(unittest.TestCase):
    def test_distillation_graph_declares_biological_efficiency_boundaries(self) -> None:
        packet = build_evidence_distillation_graph(ROOT)
        self.assertEqual(packet["schema"], "NEXUS_EVIDENCE_DISTILLATION_GRAPH.v2.6.0")
        self.assertEqual(packet["version"], "2.6.0")
        self.assertIn(packet["status"], {"pass", "warn"})
        principles = {item["principle_id"] for item in packet["biological_efficiency_principles"]}
        self.assertIn("efficient-coding", principles)
        self.assertIn("synaptic-pruning", principles)
        self.assertIn("small-world-efficiency", principles)
        self.assertIn("homeostatic-retention", principles)
        self.assertIn("does not prove", packet["claim_boundary"])

    def test_nodes_preserve_source_hash_and_claim_boundary(self) -> None:
        packet = build_evidence_distillation_graph(ROOT)
        self.assertGreaterEqual(packet["graph_metrics"]["node_count"], 6)
        for node in packet["nodes"]:
            self.assertIn("node_id", node)
            self.assertIn("source_hash", node)
            self.assertIn("claim_boundary", node)
            self.assertIn("retention_policy", node)
        self.assertIn("graph_hash", packet)

    def test_pruning_policy_is_recommendation_only_and_protects_source(self) -> None:
        packet = build_evidence_distillation_graph(ROOT)
        policy = packet["pruning_policy"]
        self.assertEqual(policy["mode"], "recommendation_only")
        self.assertTrue(policy["requires_human_authorization"])
        self.assertTrue(policy["requires_final_evolve"])
        blocked_text = json.dumps(policy["blocked_patterns"])
        self.assertIn("nexus_gate/", blocked_text)
        self.assertIn("tests/", blocked_text)
        self.assertIn("docs/", blocked_text)
        self.assertIn("delete_source_files", BLOCKED_ACTIONS)
        self.assertIn("prune_without_distillation_node", BLOCKED_ACTIONS)

    def test_cli_writes_report_state_and_ledger(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "nexus_gate.distillation.graph", "--root", ".", "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertEqual(packet["schema"], "NEXUS_EVIDENCE_DISTILLATION_GRAPH.v2.6.0")
        self.assertTrue((ROOT / "reports" / "nexus_evidence_distillation_report_latest.json").exists())
        self.assertTrue((ROOT / "state" / "distillation" / "nexus_evidence_graph_latest.json").exists())
        self.assertTrue((ROOT / "ledger" / "evidence_distillation.jsonl").exists())

    def test_command_surfaces_and_evolve_expose_distillation(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        self.assertIn('"distill"', ps)
        self.assertIn("nexus_gate.distillation.graph", ps)
        self.assertIn("distill)", sh)
        self.assertIn("nexus_gate.distillation.graph", human)
        self.assertIn("16i2_evidence_distillation", human)
        self.assertIn("v2.6.0 Evidence Distillation Graph", readme)
        self.assertIn("reports/nexus_evidence_distillation_report_latest.json", agents)

    def test_docs_and_algorithm_cards_record_distillation(self) -> None:
        algorithms = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8-sig")
        discoveries = (ROOT / "nexus_gate" / "discoveries" / "cards.py").read_text(encoding="utf-8-sig")
        self.assertIn("Evidence Distillation Algorithm", algorithms)
        self.assertIn("Provenance-Preserving Pruning Algorithm", algorithms)
        self.assertIn("Concept Graph Compression Algorithm", algorithms)
        self.assertIn("Emergence Detection Algorithm", algorithms)
        self.assertTrue((ROOT / "docs" / "design" / "EVIDENCE_DISTILLATION_GRAPH_DESIGN.md").exists())
        self.assertTrue((ROOT / "docs" / "protocols" / "EVIDENCE_DISTILLATION_GRAPH_PROTOCOL.md").exists())
        self.assertIn("evidence-distillation-graph", discoveries)


if __name__ == "__main__":
    unittest.main()
