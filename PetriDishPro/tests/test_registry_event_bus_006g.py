from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def test_event_bus_file_exists_and_exports_api():
    text = read("electron/renderer/petriEventBus006G.js")
    assert "window.PetriEventBus" in text
    assert "organism:selected" in text
    assert "drug:selected" in text
    assert "drug:injected" in text
    assert "preset:changed" in text
    assert "simulation:step" in text
    assert "receipt:written" in text
    assert "registry:loaded" in text
    assert "getState" in text
    assert "getReplay" in text

def test_registry_selector_bridge_exists_and_uses_registries():
    text = read("electron/renderer/registrySelectors006G.js")
    assert "window.PetriRegistrySelectors006G" in text
    assert "loadRegistries" in text
    assert "../../config/organisms.json" in text
    assert "../../config/drug_card_registry.json" in text
    assert "registry:loaded" in text
    assert "educational interaction proxy only" in text

def test_index_html_loads_006g_scripts_in_order():
    html = read("electron/renderer/index.html")
    event_bus = "petriEventBus006G.js"
    selectors = "registrySelectors006G.js"
    assert event_bus in html
    assert selectors in html
    assert html.index(event_bus) < html.index(selectors)

def test_006g_claim_boundary_documented():
    doc = read("docs/updates/PETRI_006G_REGISTRY_EVENT_BUS.md")
    assert "not a wet-lab protocol" in doc
    assert "006H" in doc
