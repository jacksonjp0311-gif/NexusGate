from __future__ import annotations

import unittest
from pathlib import Path

from nexus_gate.hygiene.runtime_churn import (
    BLOCKED_ACTIONS,
    TRACKED_GENERATED_PATTERNS,
    UNTRACKED_GENERATED_PATTERNS,
    _classify,
    build_runtime_hygiene_report,
)


ROOT = Path(__file__).resolve().parents[1]


class RuntimeChurnHygieneV230Tests(unittest.TestCase):
    def test_classifier_separates_generated_from_source(self) -> None:
        classified = _classify([
            {"status": " M", "path": "reports/nexus_compile_report_latest.json"},
            {"status": " M", "path": "\"Tesseract Neural Network/memory/tnn_memory.jsonl\""},
            {"status": " M", "path": "nexus_gate/core.py"},
            {"status": "??", "path": "dist/nexus_gate_source_bundle_20260712_112641.tar.gz"},
            {"status": "??", "path": "docs/new_design.md"},
        ])
        self.assertEqual(len(classified["tracked_generated"]), 2)
        self.assertEqual(len(classified["untracked_generated"]), 1)
        self.assertEqual(len(classified["source_dirty"]), 2)

    def test_boundaries_block_unbounded_cleaning(self) -> None:
        self.assertIn("git_reset_hard", BLOCKED_ACTIONS)
        self.assertIn("clean_unclassified_paths", BLOCKED_ACTIONS)
        self.assertIn("reports/nexus_*_latest.json", TRACKED_GENERATED_PATTERNS)
        self.assertIn("state/coherence/*.json", TRACKED_GENERATED_PATTERNS)
        self.assertIn("dist/nexus_gate_source_bundle_20*.tar.gz", UNTRACKED_GENERATED_PATTERNS)

    def test_runtime_hygiene_dry_run_writes_report(self) -> None:
        report = build_runtime_hygiene_report(ROOT, apply=False)
        self.assertEqual(report["schema"], "NEXUS_RUNTIME_CHURN_HYGIENE.v2.3.0")
        self.assertIn(report["status"], {"pass", "warn"})
        self.assertTrue((ROOT / "reports" / "nexus_runtime_hygiene_latest.json").exists())
        self.assertIn("does not prove", report["claim_boundary"])

    def test_command_surfaces_expose_hygiene_lanes(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn('"runtime-hygiene"', ps)
        self.assertIn('"clean-runtime"', ps)
        self.assertIn('"install-hooks"', ps)
        self.assertIn("nexus_gate.hygiene.runtime_churn", ps)
        self.assertIn("runtime-hygiene)", sh)
        self.assertIn("clean-runtime)", sh)
        self.assertIn("install-hooks)", sh)
        self.assertIn('"runtime-hygiene"', human)
        self.assertIn("runtime-hygiene", readme)
        self.assertIn("clean-runtime", readme)


if __name__ == "__main__":
    unittest.main()
