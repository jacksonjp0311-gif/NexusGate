import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestCodexOrchestrationProtocol(unittest.TestCase):
    def test_codex_protocol_mentions_required_behavior(self):
        text = (ROOT / "docs/codex/CODEX_ORCHESTRATION_PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn("Rehydrate before patching.", text)
        self.assertIn(".\\scripts\\nexus.ps1 domain", text)
        self.assertIn(".\\scripts\\nexus.ps1 reflect", text)
        self.assertIn(".\\scripts\\nexus.ps1 evolve", text)
        self.assertIn("cannot self-authorize", text)

    def test_codex_index_blocks_self_authorization(self):
        data = json.loads((ROOT / "state/codex_orchestration_index.v0.4.0.json").read_text(encoding="utf-8"))
        self.assertIn("self_authorize", data["blocked_actions"])
        self.assertIn("README.md", data["required_read_order"])
        self.assertIn("reports/nexus_domain_intelligence_report_latest.json", data["required_read_order"])


if __name__ == "__main__":
    unittest.main()
