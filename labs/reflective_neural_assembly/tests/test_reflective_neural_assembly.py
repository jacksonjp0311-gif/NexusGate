from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT))

from assembly.neural.neural_optional import torch_status
from assembly.neural.pattern_engine import detect_pattern
from assembly.neural.smart_policy import decide
from assembly.distribution.chat_intelligence import (
    BLOCKED_ACTIONS as DISTRIBUTION_BLOCKED_ACTIONS,
    build_distribution_packet,
    write_distribution,
)
from assembly.runtime.realtime_evolution import RealtimeEvolutionEngine
from assembly.telemetry.neuralforge_event_codec import (
    BLOCKED_ADAPTER_ACTIONS,
    make_parent_emitter_packet,
    normalize_event,
    telemetry_adapter_contract,
)
from run_neural_assembly import build_report


class TestReflectiveNeuralAssembly(unittest.TestCase):
    def test_fallback_works_without_requiring_torch(self):
        status = torch_status()
        self.assertIn("available", status)
        self.assertIn(status["mode"], {"optional_local", "standard_library_fallback"})
        report = build_report("What should we do next?")
        self.assertEqual(report["status"], "pass")
        self.assertIn("recommendation", report)

    def test_telemetry_adapters_are_disabled_by_default(self):
        contract = telemetry_adapter_contract()
        self.assertTrue(contract["local_file"]["enabled"])
        self.assertFalse(contract["http_readonly"]["enabled"])
        self.assertFalse(contract["github_readonly"]["enabled"])
        self.assertFalse(contract["api_checkpoint"]["enabled"])
        for item in ["POST", "PUT", "PATCH", "DELETE", "secret_exfiltration"]:
            self.assertIn(item, BLOCKED_ADAPTER_ACTIONS)

    def test_event_normalization_handles_missing_fields(self):
        event = normalize_event({})
        self.assertEqual(event["workflow_name"], "unknown_workflow")
        self.assertEqual(event["tool_name"], "unknown_tool")
        self.assertFalse(event["success"])
        self.assertIn("timestamp", event)

    def test_memory_event_ledger_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            engine = RealtimeEvolutionEngine(event_log_path=path, load_existing=False)
            result = engine.ingest({"workflow_name": "evolve", "success": False, "duration_ms": 1200, "step_count": 3})
            self.assertTrue(path.exists())
            self.assertIn("recommendations", result)
            reloaded = RealtimeEvolutionEngine(event_log_path=path, load_existing=True)
            self.assertEqual(len(reloaded.events), 1)

    def test_parent_emitter_packet_validates(self):
        packet = make_parent_emitter_packet("Map the next NEXUS step", raw_text="Recommend only.")
        result = packet.validate()
        self.assertTrue(result["valid"])
        self.assertIn("not authority", result["claim_boundary"])

    def test_pattern_and_policy_recommend_only(self):
        pattern = detect_pattern([1, 2, 3, 4, 5])
        self.assertIn(pattern["pattern"], {"trend", "step", "unknown"})
        decision = decide("fix", history=[{"success": False, "duration_ms": 100, "step_count": 1}])
        self.assertEqual(decision["decision"], "recommend")
        self.assertIn("auto_apply_fix", decision["blocked_actions"])

    def test_runtime_report_is_generated(self):
        report = build_report("What should we do next?")
        reports_dir = LAB_ROOT / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        path = reports_dir / "neural_assembly_report_latest.json"
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "0.5.1")
        self.assertIn("recommendation-only", data["claim_boundary"])

    def test_chat_intelligence_distribution_declares_codex_and_chats(self):
        report = build_report("Distribute intelligence to Codex and chats")
        packet = build_distribution_packet(report)
        self.assertEqual(packet["version"], "0.5.1")
        for surface in ["codex", "chatgpt", "local_agent", "tui", "electron"]:
            self.assertIn(surface, packet["packets"])
        self.assertIn("self_authorize", packet["blocked_actions"])
        self.assertIn("parent_repo_mutation", packet["blocked_actions"])
        self.assertIn("Distributed intelligence", packet["packets"]["codex"]["claim_boundary"])

    def test_chat_intelligence_distribution_writes_lab_only_surfaces(self):
        report = build_report("Write handoff packets")
        packet = build_distribution_packet(report, surfaces=["codex", "chatgpt"])
        outputs = write_distribution(packet)
        self.assertTrue(Path(outputs["report"]).exists())
        self.assertTrue(Path(outputs["codex_json"]).exists())
        self.assertTrue(Path(outputs["chatgpt_markdown"]).exists())
        for output in outputs.values():
            self.assertIn("reflective_neural_assembly", output)
        for blocked in ["arbitrary_shell", "external_api_write", "memory_promotion_without_evidence"]:
            self.assertIn(blocked, DISTRIBUTION_BLOCKED_ACTIONS)

    def test_no_arbitrary_shell_or_external_api_writes(self):
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (LAB_ROOT / "assembly").rglob("*.py")
        ) + (LAB_ROOT / "run_neural_assembly.py").read_text(encoding="utf-8")
        forbidden = ["subprocess", "os.system", "Start-Process", "requests.post", "requests.put", "requests.patch", "requests.delete"]
        for marker in forbidden:
            self.assertNotIn(marker, source)
        self.assertIn("No external writes", telemetry_adapter_contract()["claim_boundary"])

    def test_recommendation_only_boundary_exists(self):
        mini = (LAB_ROOT / "MINI_README.md").read_text(encoding="utf-8")
        self.assertIn("recommendation-only", mini)
        self.assertIn("no self-authorization", mini)
        self.assertIn("no arbitrary shell", mini)
        self.assertIn("no parent repo mutation", mini)
        self.assertIn("Chat intelligence distribution", (LAB_ROOT / "CHAT_INTELLIGENCE_DISTRIBUTION.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
