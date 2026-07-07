import json
import unittest
from pathlib import Path


class TestRehydrationProcessLineage(unittest.TestCase):
    def test_root_readme_records_current_process_without_bloat(self):
        text = Path("README.md").read_text(encoding="utf-8-sig")
        self.assertLess(len(text.splitlines()), 220)
        self.assertIn("Failure Intelligence Distributor", text)
        self.assertIn("Reflective Local Loop", text)
        self.assertIn("future systems can continue without chat context", text)
        self.assertIn("NEXUS_FUTURE_SYSTEM_REHYDRATION_HANDOFF.md", text)
        self.assertIn("No rehydration without failure chart visibility.", text)
        self.assertIn("PART III - AI Agent README", text)

    def test_future_system_handoff_is_self_contained(self):
        text = Path("docs/runtime/NEXUS_FUTURE_SYSTEM_REHYDRATION_HANDOFF.md").read_text(encoding="utf-8-sig")
        self.assertIn("No chat context required", text)
        self.assertIn("The repository is the origin", text)
        self.assertIn("commit only when authorized", text)
        self.assertIn("push only when authorized", text)
        self.assertIn("repository evidence wins", text)

    def test_process_manifest_declares_spine_and_authority_boundary(self):
        path = Path("state/process/nexus_process_rehydration_manifest.v0.1.5.json")
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        self.assertEqual(data["version"], "0.1.5")
        self.assertTrue(data["stability_lock_requires_clean_status"])
        self.assertIn("docs/runtime/NEXUS_FUTURE_SYSTEM_REHYDRATION_HANDOFF.md", data["read_first"])
        self.assertIn("commit only when authorized", data["process_spine"])
        self.assertIn("not autonomous authority", data["claim_boundary"])
        self.assertIn("tracked reports", data["tracked_report_rule"])
        self.assertIn("--untracked-files=all", data["untracked_directory_rule"])


if __name__ == "__main__":
    unittest.main()
