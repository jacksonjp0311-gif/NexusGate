/*
PETRI DISH PRO v0.6G
Registry-driven selector bridge.

This is a non-destructive bridge. It does not remove existing UI behavior.
It gives the app one canonical event surface for organism/drug/preset choices.
*/
(function () {
  "use strict";

  const VERSION = "0.6G";
  const DEFAULT_REGISTRY_PATHS = Object.freeze({
    organisms: "../../config/organisms.json",
    organismCards: "../../config/bio/organism_card_registry.json",
    drugs: "../../config/drug_card_registry.json",
    drugCards: "../../config/bio/drug_interaction_card_registry.json",
    presets: "../../config/preset_cards.json"
  });

  function bus() {
    if (!window.PetriEventBus) {
      console.warn("[PetriRegistrySelectors006G] PetriEventBus missing.");
      return null;
    }
    return window.PetriEventBus;
  }

  function asArray(value) {
    if (Array.isArray(value)) return value;
    if (value && Array.isArray(value.items)) return value.items;
    if (value && Array.isArray(value.organisms)) return value.organisms;
    if (value && Array.isArray(value.drugs)) return value.drugs;
    if (value && Array.isArray(value.presets)) return value.presets;
    if (value && typeof value === "object") {
      return Object.keys(value).map(function (key) {
        const item = value[key];
        if (item && typeof item === "object" && !item.id) {
          return Object.assign({ id: key }, item);
        }
        return item;
      }).filter(Boolean);
    }
    return [];
  }

  function normalizeCard(item, fallbackPrefix, index) {
    if (!item || typeof item !== "object") {
      return { id: fallbackPrefix + "_" + index, label: String(item || fallbackPrefix + "_" + index), raw: item };
    }

    const id = String(item.id || item.key || item.name || item.slug || fallbackPrefix + "_" + index);
    const label = String(item.label || item.display_name || item.displayName || item.name || item.title || id);
    return Object.assign({}, item, { id: id, label: label });
  }

  async function loadJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error("Failed to load " + path + " (" + response.status + ")");
    return response.json();
  }

  async function loadRegistries(paths) {
    const resolved = Object.assign({}, DEFAULT_REGISTRY_PATHS, paths || {});
    const results = {
      organisms: [],
      drugs: [],
      presets: [],
      errors: []
    };

    async function tryLoad(kind, path, prefix) {
      try {
        const raw = await loadJson(path);
        const cards = asArray(raw).map(function (item, index) {
          return normalizeCard(item, prefix, index);
        });
        results[kind] = results[kind].concat(cards);
      } catch (error) {
        results.errors.push({ kind: kind, path: path, error: String(error.message || error) });
      }
    }

    await Promise.all([
      tryLoad("organisms", resolved.organisms, "organism"),
      tryLoad("organisms", resolved.organismCards, "organism_card"),
      tryLoad("drugs", resolved.drugs, "drug"),
      tryLoad("drugs", resolved.drugCards, "drug_card"),
      tryLoad("presets", resolved.presets, "preset")
    ]);

    const eventBus = bus();
    if (eventBus) {
      eventBus.emit("registry:loaded", {
        organisms: results.organisms,
        drugs: results.drugs,
        presets: results.presets,
        errors: results.errors
      }, { source: "PetriRegistrySelectors006G.loadRegistries" });
    }

    return results;
  }

  function bindSelect(selector, eventName, collectionName) {
    const node = typeof selector === "string" ? document.querySelector(selector) : selector;
    if (!node) return false;

    node.addEventListener("change", function () {
      const selectedId = String(node.value || "");
      const eventBus = bus();
      const state = eventBus ? eventBus.getState() : { registries: {} };
      const collection = (state.registries && state.registries[collectionName]) || [];
      const selected = collection.find(function (item) { return String(item.id) === selectedId; }) || { id: selectedId, label: selectedId };
      if (eventBus) {
        eventBus.emit(eventName, selected, { source: "PetriRegistrySelectors006G.bindSelect", selector: selector });
      }
    });

    return true;
  }

  function emitOrganismSelected(organism) {
    const eventBus = bus();
    if (eventBus) return eventBus.emit("organism:selected", organism, { source: "PetriRegistrySelectors006G.api" });
    return null;
  }

  function emitDrugSelected(drug) {
    const eventBus = bus();
    if (eventBus) return eventBus.emit("drug:selected", drug, { source: "PetriRegistrySelectors006G.api" });
    return null;
  }

  function emitDrugInjected(drug, doseProxy) {
    const eventBus = bus();
    if (eventBus) {
      return eventBus.emit("drug:injected", {
        drug: drug,
        doseProxy: doseProxy || null,
        boundary: "educational interaction proxy only"
      }, { source: "PetriRegistrySelectors006G.api" });
    }
    return null;
  }

  window.PetriRegistrySelectors006G = Object.freeze({
    version: VERSION,
    paths: DEFAULT_REGISTRY_PATHS,
    loadRegistries: loadRegistries,
    bindSelect: bindSelect,
    emitOrganismSelected: emitOrganismSelected,
    emitDrugSelected: emitDrugSelected,
    emitDrugInjected: emitDrugInjected
  });

  window.addEventListener("DOMContentLoaded", function () {
    loadRegistries().catch(function (error) {
      console.warn("[PetriRegistrySelectors006G] registry load failed", error);
    });
  });
})();
