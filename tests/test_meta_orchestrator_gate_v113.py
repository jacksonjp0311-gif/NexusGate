from __future__ import annotations

import json
import unittest
from pathlib import Path

from nexus_gate.loops.meta_orchestrator_gate import build_meta_orchestrator_packet


ROOT = Path(__file__).resolve().parents[1]


class MetaOrchestratorGateTests(unittest.TestCase):
    def test_packet_is_recommendation_only(self) -> None:
        packet = build_meta_orchestrator_packet(ROOT, "test")
        self.assertEqual(packet["schema"], "NEXUS_META_ORCHESTRATOR_GATE.v1.1.3")
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertFalse(packet["authority_boundary"]["autonomous_authority"])
        self.assertTrue(packet["authority_boundary"]["recommendation_only"])
        self.assertIn("self_authorize", packet["blocked_actions"])
        self.assertIn("arbitrary_shell_commands", packet["blocked_actions"])
        self.assertIn("reports/nexus_meta_orchestrator_gate_latest.json", packet["write_surfaces"])
        panel_ids = {panel["panel_id"] for panel in packet["panels"]}
        self.assertIn("predictive_evolve", panel_ids)
        self.assertIn("certificate_resume", panel_ids)
        self.assertIn("production readiness", packet["claim_boundary"])

    def test_command_surfaces_expose_meta_orchestrator(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('"meta-orchestrator"', ps)
        self.assertIn("Invoke-NexusMetaOrchestratorGate", ps)
        self.assertIn("meta-orchestrator)", sh)
        self.assertIn('"meta-orchestrator"', human)
        self.assertIn("meta_orchestrator_gate", human)

    def test_electron_reads_report_without_new_command_authority(self) -> None:
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        js = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        css = (ROOT / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8-sig")
        self.assertIn("reports/nexus_meta_orchestrator_gate_latest.json", main)
        self.assertIn("reports/nexus_predictive_evolve_plan_latest.json", main)
        self.assertIn("state/algorithms/nexus_algorithm_cards_latest.json", main)
        self.assertIn("state/discoveries/nexus_discovery_cards_latest.json", main)
        self.assertIn('id="meta-orchestrator-hud"', html)
        self.assertIn('id="algorithm-cards-hud"', html)
        self.assertIn('id="discovery-cards-hud"', html)
        self.assertIn('id="meta-orchestrator-popout"', html)
        self.assertIn("renderMetaOrchestratorPanels", js)
        self.assertIn("toggleCardsHud", js)
        self.assertIn("ALGORITHM_CARDS_SURFACE", js)
        self.assertIn("META_ORCHESTRATOR_SURFACE", js)
        self.assertIn(".meta-orchestrator-panels", css)
        self.assertIn(".nexus-cards-hud", css)
        allowlist_block = main.split("const ALLOWLISTED_COMMANDS", 1)[1].split("]);", 1)[0]
        self.assertNotIn('"meta-orchestrator"', allowlist_block)

    def test_state_index_is_valid_after_compile_when_present(self) -> None:
        path = ROOT / "state" / "loops" / "nexus_meta_orchestrator_gate.v1.1.3.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            self.assertEqual(data["schema"], "NEXUS_META_ORCHESTRATOR_GATE.v1.1.3")


if __name__ == "__main__":
    unittest.main()
