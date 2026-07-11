import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestPredictiveTimingOperatingContractV116(unittest.TestCase):
    def test_agents_contract_requires_predictive_timing_before_expensive_gates(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        self.assertIn("Predictive Timing Preflight", text)
        self.assertIn(".\\scripts\\nexus.ps1 predictive-timing", text)
        self.assertIn("Before running full `evolve`", text)
        self.assertIn("reports/nexus_predictive_gate_timing_latest.json", text)
        self.assertIn("state/algorithms/nexus_algorithm_cards_latest.json", text)
        self.assertIn("It may not hide failures, bypass gates, self-authorize, or extend authority.", text)

    def test_chatgpt_script_doctrine_requires_predictive_timing_gate(self):
        text = (ROOT / "chatgpt/scripts.md").read_text(encoding="utf-8-sig")
        self.assertIn("Run `.\\scripts\\nexus.ps1 predictive-timing` before full evolve", text)
        self.assertIn("GATE 05: Run predictive timing before expensive gates", text)
        self.assertIn("Run predictive timing before expensive gates", text)

    def test_codex_orchestration_protocol_and_index_require_predictive_timing(self):
        doc = (ROOT / "docs/codex/CODEX_ORCHESTRATION_PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn(".\\scripts\\nexus.ps1 predictive-timing", doc)
        self.assertIn("Predictive Timing Rule", doc)
        self.assertIn("cannot authorize mutation", doc)

        data = json.loads((ROOT / "state/codex_orchestration_index.v0.4.0.json").read_text(encoding="utf-8"))
        self.assertIn(".\\scripts\\nexus.ps1 predictive-timing", data["required_commands"])
        self.assertIn("reports/nexus_predictive_gate_timing_latest.json", data["required_read_order"])
        self.assertIn("state/algorithms/nexus_algorithm_cards_latest.json", data["required_read_order"])

    def test_rehydrate_commands_emit_predictive_timing(self):
        ps = (ROOT / "scripts/nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts/nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn('"rehydrate" {', ps)
        self.assertIn("nexus_gate.loops.predictive_timing --root . --json", ps)
        self.assertIn("Predictive timing preflight failed.", ps)
        self.assertIn("rehydrate)", sh)
        self.assertIn("python -m nexus_gate.loops.predictive_timing --root . --json", sh)


if __name__ == "__main__":
    unittest.main()
