import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestDiscoveryCardsV010(unittest.TestCase):
    def test_discovery_card_packet_compiles(self):
        result = subprocess.run(
            [sys.executable, "-m", "nexus_gate.discoveries.cards", "--root", str(ROOT), "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = json.loads((ROOT / "state/discoveries/nexus_discovery_cards_latest.json").read_text(encoding="utf-8"))
        self.assertEqual(packet["schema"], "NEXUS_DISCOVERY_CARD_SET.v0.2.0")
        self.assertEqual(packet["portal_entry"], "[18] Discoveries")
        self.assertGreaterEqual(packet["card_count"], 2)
        card = packet["cards"][0]
        self.assertEqual(card["discovery_id"], "predictive-gate-timing-runtime-pressure")
        self.assertIn("drift_ratio", card["math"]["drift"])
        self.assertIn("p90 * 1.5", card["math"]["adaptive_timeout"])
        self.assertIn("nexus_gate/loops/predictive_timing.py::build_predictive_timing_packet", card["code_references"])
        self.assertIn("runtime-pressure-model", card["algorithm_card_refs"])
        self.assertIn("ledger/runtime_gate_timings.jsonl", card["evidence_surfaces"])
        self.assertIn("Recommendation-only", card["boundary"])
        ids = {item["discovery_id"] for item in packet["cards"]}
        self.assertIn("predictive-evolve-dry-run-planner", ids)

    def test_command_surfaces_expose_discovery_cards(self):
        ps = (ROOT / "scripts/nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts/nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn("discovery-cards", ps)
        self.assertIn("nexus_gate.discoveries.cards", ps)
        self.assertIn("discovery-cards", sh)
        self.assertIn("nexus_gate.discoveries.cards", sh)

    def test_spiral_core_portal_exposes_discoveries(self):
        portal = (ROOT / "scripts/desktop/open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("Invoke-NexusDiscoveryCardsConsole", portal)
        self.assertIn("[18] Discoveries", portal)
        self.assertIn("state\\discoveries\\nexus_discovery_cards_latest.json", portal)
        self.assertIn('$choice -eq "18"', portal)

    def test_docs_and_readme_map_discoveries(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        docs = (ROOT / "docs/runtime/NEXUS_DISCOVERY_CARDS.md").read_text(encoding="utf-8-sig")
        self.assertIn("Discovery Cards", readme)
        self.assertIn("docs/runtime/NEXUS_DISCOVERY_CARDS.md", readme)
        self.assertIn("math -> code function references -> algorithm card references", docs)
        self.assertIn("Predictive Gate Timing / Runtime Pressure Model", docs)
        self.assertIn("Predictive Evolve Dry-Run Planner", docs)


if __name__ == "__main__":
    unittest.main()
