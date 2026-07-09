from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def test_006i_js_exports_runtime_surface_and_dedupe():
    text = read("electron/renderer/registryDedupeDashboard006I.js")
    assert "window.PetriDashboardPolish006I" in text
    assert "dedupeSelectOptions" in text
    assert "dedupeDrugSelects" in text
    assert "dedupeArray" in text
    assert "patchRegistryLoader" in text

def test_006i_js_targets_dashboard_panels():
    text = read("electron/renderer/registryDedupeDashboard006I.js")
    assert "metric charts" in text
    assert "emergent conditions" in text
    assert "petri-006i-metric-panel" in text
    assert "petri-006i-emergent-panel" in text

def test_006i_css_improves_cards():
    text = read("electron/renderer/dashboardPolish006I.css")
    assert ".petri-006i-metric-panel" in text
    assert ".petri-006i-emergent-panel" in text
    assert "min-width: 112px" in text
    assert "text-overflow: ellipsis" in text

def test_index_loads_006i_after_006h():
    html = read("electron/renderer/index.html")
    assert "petriEventBus006G.js" in html
    assert "registrySelectors006G.js" in html
    assert "eventBusWiring006H.js" in html
    assert "registryDedupeDashboard006I.js" in html
    assert "dashboardPolish006I.css" in html
    assert html.index("eventBusWiring006H.js") < html.index("registryDedupeDashboard006I.js")

def test_006i_doc_boundary_and_next_gate():
    doc = read("docs/updates/PETRI_006I_DRUG_DEDUPE_DASHBOARD_POLISH.md")
    assert "Duplicate drug card options" in doc
    assert "not a wet-lab protocol" in doc
    assert "006J" in doc
