import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestAlgorithmCardsV010(unittest.TestCase):
    def test_algorithm_card_packet_compiles(self):
        result = subprocess.run(
            [sys.executable, "-m", "nexus_gate.algorithms.cards", "--root", str(ROOT), "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = json.loads((ROOT / "state/algorithms/nexus_algorithm_cards_latest.json").read_text(encoding="utf-8"))
        self.assertEqual(packet["schema"], "NEXUS_ALGORITHM_CARD_SET.v0.3.0")
        self.assertGreaterEqual(packet["card_count"], 17)
        ids = {card["algorithm_id"] for card in packet["cards"]}
        self.assertIn("predictive-gate-timing-runtime-pressure-algorithm", ids)
        self.assertIn("runtime-pressure-model", ids)
        self.assertIn("adaptive-timeout-budgeting", ids)
        self.assertIn("gate-selection-policy", ids)
        self.assertIn("certificate-resume-policy", ids)
        self.assertIn("predictive-evolve-planner-algorithm", ids)
        self.assertIn("runtime-pressure-model", packet["discovered_algorithms"])
        self.assertIn("predictive-evolve-planner-algorithm", packet["discovered_algorithms"])
        self.assertEqual(set(packet["discovered_algorithms"]), ids)
        self.assertEqual(packet["discovery_source"], "derived_from_cards_algorithm_id")
        self.assertIn("origin-seal-algorithm", ids)
        self.assertIn("authority-monotonicity-algorithm", ids)
        self.assertIn("evidence-freshness-algorithm", ids)
        self.assertIn("gate-dependency-invalidation-algorithm", ids)
        self.assertIn("decision-envelope-arbitration-algorithm", ids)
        self.assertFalse(packet["authority_boundary"]["autonomous_authority"])
        self.assertFalse(packet["authority_boundary"]["arbitrary_command_execution"])
        self.assertIn("do not prove correctness", packet["claim_boundary"])

    def test_core_algorithm_doc_records_predictive_timing_discovery(self):
        text = (ROOT / "docs/algorithms/NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8-sig")
        self.assertIn("Predictive Gate Timing / Runtime Pressure Algorithm", text)
        self.assertIn("Predictive Evolve Planner Algorithm", text)
        self.assertIn("Origin Seal Algorithm", text)
        self.assertIn("Authority Monotonicity Algorithm", text)
        self.assertIn("Evidence Freshness Algorithm", text)
        self.assertIn("Gate Dependency Invalidation Algorithm", text)
        self.assertIn("duration history -> baseline -> drift -> anomaly", text)
        self.assertIn("prediction by feedback", text)

    def test_command_surfaces_expose_algorithm_cards(self):
        ps = (ROOT / "scripts/nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts/nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn("algorithm-cards", ps)
        self.assertIn("nexus_gate.algorithms.cards", ps)
        self.assertIn("algorithm-cards", sh)
        self.assertIn("nexus_gate.algorithms.cards", sh)

    def test_spiral_core_portal_exposes_algorithm_cards(self):
        portal = (ROOT / "scripts/desktop/open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("Invoke-NexusAlgorithmCardsConsole", portal)
        self.assertIn("[17] Algorithm Cards", portal)
        self.assertIn("state\\algorithms\\nexus_algorithm_cards_latest.json", portal)
        self.assertIn('$choice -eq "17"', portal)

    def test_readme_and_docs_map_algorithm_cards(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        docs = (ROOT / "docs/runtime/NEXUS_ALGORITHM_CARDS.md").read_text(encoding="utf-8-sig")
        self.assertIn("Algorithm Cards", readme)
        self.assertIn("docs/runtime/NEXUS_ALGORITHM_CARDS.md", readme)
        self.assertIn("Predictive Gate Timing / Runtime Pressure Model", docs)
        self.assertIn("Predictive Evolve Planner Algorithm", docs)
        self.assertIn("state/algorithms/nexus_algorithm_cards_latest.json", docs)


if __name__ == "__main__":
    unittest.main()
