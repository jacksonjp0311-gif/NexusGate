import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

class DashboardHardOverride006J2Tests(unittest.TestCase):
    def test_runtime_surface_exists(self):
        text = read("electron/renderer/dashboardHardOverride006J2.js")
        self.assertIn("window.PetriDashboardHardOverride006J2", text)
        self.assertIn("findPanel", text)
        self.assertIn("scorePanel", text)
        self.assertIn("renderMetricPanel", text)
        self.assertIn("renderEmergentPanel", text)

    def test_metric_and_emergent_are_hard_replaced(self):
        text = read("electron/renderer/dashboardHardOverride006J2.js")
        self.assertIn("petri-006j2-metric-row", text)
        self.assertIn("petri-006j2-condition-row", text)
        self.assertIn("METRIC CHARTS", text)
        self.assertIn("EMERGENT CONDITIONS", text)
        self.assertIn("panel.innerHTML", text)

    def test_css_has_real_row_layouts(self):
        text = read("electron/renderer/dashboardHardOverride006J2.css")
        self.assertIn(".petri-006j2-metric-row", text)
        self.assertIn("grid-template-columns: minmax(72px, 0.82fr)", text)
        self.assertIn(".petri-006j2-condition-row", text)
        self.assertIn("-webkit-line-clamp: 2", text)

    def test_index_loads_006j2_after_006j_or_006i(self):
        html = read("electron/renderer/index.html")
        self.assertIn("dashboardHardOverride006J2.css", html)
        self.assertIn("dashboardHardOverride006J2.js", html)
        if "dashboardReadability006J.js" in html:
            self.assertLess(html.index("dashboardReadability006J.js"), html.index("dashboardHardOverride006J2.js"))
        elif "registryDedupeDashboard006I.js" in html:
            self.assertLess(html.index("registryDedupeDashboard006I.js"), html.index("dashboardHardOverride006J2.js"))

    def test_doc_boundary_and_next_gate(self):
        doc = read("docs/updates/PETRI_006J2_HARD_DASHBOARD_PANEL_OVERRIDE.md")
        self.assertIn("not a wet-lab protocol", doc)
        self.assertIn("006K", doc)

if __name__ == "__main__":
    unittest.main()
