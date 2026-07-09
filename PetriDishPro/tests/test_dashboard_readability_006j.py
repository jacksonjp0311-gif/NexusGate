import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

class DashboardReadability006JTests(unittest.TestCase):
    def test_006j_runtime_surface_exists(self):
        text = read("electron/renderer/dashboardReadability006J.js")
        self.assertIn("window.PetriDashboardReadability006J", text)
        self.assertIn("smallestPanelContaining", text)
        self.assertIn("renderMetrics", text)
        self.assertIn("renderEmergent", text)

    def test_006j_metric_and_emergent_replacements_exist(self):
        text = read("electron/renderer/dashboardReadability006J.js")
        self.assertIn("METRIC CHARTS", text)
        self.assertIn("EMERGENT CONDITIONS", text)
        self.assertIn("petri-006j-metric-row", text)
        self.assertIn("petri-006j-condition-row", text)
        self.assertIn("educational dashboard display only", text)

    def test_006j_css_has_readable_layout(self):
        text = read("electron/renderer/dashboardReadability006J.css")
        self.assertIn(".petri-006j-metric-row", text)
        self.assertIn("grid-template-columns: minmax(70px, 0.8fr)", text)
        self.assertIn(".petri-006j-condition-row", text)
        self.assertIn("-webkit-line-clamp: 2", text)

    def test_index_loads_006j_after_006i(self):
        html = read("electron/renderer/index.html")
        self.assertIn("dashboardReadability006J.css", html)
        self.assertIn("dashboardReadability006J.js", html)
        self.assertIn("registryDedupeDashboard006I.js", html)
        self.assertLess(html.index("registryDedupeDashboard006I.js"), html.index("dashboardReadability006J.js"))

    def test_006j_doc_boundary_and_next_gate(self):
        doc = read("docs/updates/PETRI_006J_DASHBOARD_READABILITY_UPGRADE.md")
        self.assertIn("not a wet-lab protocol", doc)
        self.assertIn("006K", doc)

if __name__ == "__main__":
    unittest.main()
