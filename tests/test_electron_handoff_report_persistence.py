import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestElectronHandoffReportPersistence(unittest.TestCase):
    def test_main_persists_handoff_reports_defensively(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")

        self.assertIn("function persistHandoffReport", main)
        self.assertIn("fs.mkdirSync", main)
        self.assertIn("path.dirname", main)
        self.assertIn("recursive: true", main)
        self.assertIn("reports\", \"handoff_queue\", \"recovered", main)
        self.assertIn("report.original_report_path", main)
        self.assertIn("report.report_write_error", main)
        self.assertEqual(main.count("persistHandoffReport(reportPath, report);"), 2)

    def test_main_has_no_direct_handoff_report_writes_left(self):
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        self.assertNotIn(
            'fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), "utf8");',
            main,
        )

    def test_handoff_doc_records_wound_lesson(self):
        doc = (ROOT / "docs" / "ui" / "NEX_HANDOFF_ACTION_SHELL.md").read_text(encoding="utf-8-sig")
        self.assertIn("v0.7.5 Wound-Safe Report Persistence", doc)
        self.assertIn("cleanup scripts must not delete their own active execution/report directory", doc)


if __name__ == "__main__":
    unittest.main()
