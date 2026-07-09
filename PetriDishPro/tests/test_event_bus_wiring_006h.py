from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def test_006h_wiring_file_exports_runtime_surface():
    text = read("electron/renderer/eventBusWiring006H.js")
    assert "window.PetriEventBusWiring006H" in text
    assert "bindInputs" in text
    assert "inferSelectEvent" in text
    assert "inferButtonEvent" in text

def test_006h_wires_canonical_events():
    text = read("electron/renderer/eventBusWiring006H.js")
    for event in [
        "organism:selected",
        "drug:selected",
        "drug:injected",
        "preset:changed",
        "simulation:step",
        "receipt:written",
    ]:
        assert event in text

def test_006h_is_non_destructive_and_boundary_limited():
    text = read("electron/renderer/eventBusWiring006H.js")
    assert "does not remove existing handlers" in text
    assert "educational UI event only" in text
    assert "educational interaction proxy only" in text
    assert "MutationObserver" in text

def test_index_html_loads_006h_after_006g():
    html = read("electron/renderer/index.html")
    assert "petriEventBus006G.js" in html
    assert "registrySelectors006G.js" in html
    assert "eventBusWiring006H.js" in html
    assert html.index("petriEventBus006G.js") < html.index("registrySelectors006G.js")
    assert html.index("registrySelectors006G.js") < html.index("eventBusWiring006H.js")

def test_006h_doc_has_next_gate_and_claim_boundary():
    doc = read("docs/updates/PETRI_006H_EVENT_BUS_UI_WIRING.md")
    assert "006I" in doc
    assert "not a wet-lab protocol" in doc
