/*
PETRI DISH PRO v0.6I
Drug dedupe + dashboard polish bridge.

Purpose:
- Deduplicate repeated drug select options/cards caused by multi-registry merges.
- Improve Metric Charts and Emergent Conditions readability without replacing the app.
- Preserve current event bus behavior and legacy UI handlers.

Boundary:
Educational simulation UI only. No clinical, diagnostic, dosing, treatment,
susceptibility, wet-lab, or biosafety claim is created.
*/
(function () {
  "use strict";

  const VERSION = "0.6I";
  const MARK = "data-petri-006i";
  const PANEL_MARK = "data-petri-006i-panel";
  const OPTION_MARK = "data-petri-006i-deduped";

  function norm(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .replace(/[^\w.+-]+/g, " ")
      .trim();
  }

  function optionKey(option) {
    const text = norm(option.textContent);
    const value = norm(option.value);
    const label = norm(option.getAttribute("label"));
    const key = value || label || text;
    return key || text;
  }

  function dedupeSelectOptions(select) {
    if (!select || !select.options) return 0;

    const seen = new Set();
    const remove = [];
    Array.from(select.options).forEach(function (option, index) {
      const text = norm(option.textContent);
      const value = norm(option.value);
      const isPlaceholder = index === 0 && (!value || /select|choose|card/.test(text));
      if (isPlaceholder) return;

      const key = optionKey(option);
      if (!key) return;

      if (seen.has(key)) {
        remove.push(option);
      } else {
        seen.add(key);
      }
    });

    remove.forEach(function (option) {
      option.remove();
    });

    if (remove.length > 0) {
      select.setAttribute(OPTION_MARK, "true");
      select.setAttribute("data-petri-006i-removed-options", String(remove.length));
    }

    return remove.length;
  }

  function dedupeArray(items) {
    const seen = new Set();
    const out = [];
    (items || []).forEach(function (item, index) {
      const id = item && typeof item === "object" ? item.id : null;
      const label = item && typeof item === "object" ? (item.label || item.name || item.title) : item;
      const key = norm(id || label || ("item_" + index));
      if (!key || seen.has(key)) return;
      seen.add(key);
      out.push(item);
    });
    return out;
  }

  function patchRegistryLoader() {
    const registry = window.PetriRegistrySelectors006G;
    if (!registry || registry.__petri006iPatched || typeof registry.loadRegistries !== "function") return false;

    const original = registry.loadRegistries;
    registry.loadRegistries = async function patchedLoadRegistries(paths) {
      const results = await original.call(registry, paths);
      const cleaned = Object.assign({}, results || {}, {
        organisms: dedupeArray((results && results.organisms) || []),
        drugs: dedupeArray((results && results.drugs) || []),
        presets: dedupeArray((results && results.presets) || [])
      });

      if (window.PetriEventBus) {
        window.PetriEventBus.emit("registry:loaded", cleaned, {
          source: "PetriDashboardPolish006I.dedupeRegistry",
          bridge: "006I",
          boundary: "educational registry normalization only"
        });
      }

      return cleaned;
    };

    try {
      Object.defineProperty(registry, "__petri006iPatched", { value: true });
    } catch (error) {
      registry.__petri006iPatched = true;
    }
    return true;
  }

  function selectLooksDrug(select) {
    const signature = norm([
      select.id,
      select.name,
      select.className,
      select.getAttribute("aria-label"),
      select.getAttribute("title"),
      select.closest("[class]") ? select.closest("[class]").className : "",
      Array.from(select.options || []).slice(0, 12).map(function (option) {
        return option.textContent;
      }).join(" ")
    ].join(" "));

    return /drug|compound|ampicillin|ciprofloxacin|gentamicin|vancomycin|tetracycline|fluconazole|anti lps/.test(signature);
  }

  function dedupeDrugSelects() {
    let removed = 0;
    document.querySelectorAll("select").forEach(function (select) {
      if (selectLooksDrug(select)) {
        removed += dedupeSelectOptions(select);
        select.setAttribute("data-petri-006i-drug-select", "true");
      }
    });
    return removed;
  }

  function smallestPanelContaining(label) {
    const target = norm(label);
    let best = null;

    document.querySelectorAll("section, aside, article, div").forEach(function (node) {
      const text = norm(node.textContent);
      if (!text || text.indexOf(target) < 0) return;

      const rect = node.getBoundingClientRect();
      if (!rect || rect.width < 80 || rect.height < 60) return;

      if (!best) {
        best = node;
        return;
      }

      const bestRect = best.getBoundingClientRect();
      if ((rect.width * rect.height) < (bestRect.width * bestRect.height)) {
        best = node;
      }
    });

    return best;
  }

  function labelCards(panel, kind) {
    if (!panel) return 0;

    panel.setAttribute(PANEL_MARK, kind);
    panel.classList.add("petri-006i-panel", "petri-006i-" + kind + "-panel");

    let count = 0;
    Array.from(panel.querySelectorAll("div, article, section")).forEach(function (node) {
      if (node === panel) return;
      const text = String(node.textContent || "").trim();
      if (!text || text.length < 3) return;
      if (/metric charts|emergent conditions/i.test(text) && text.length < 40) return;

      const rect = node.getBoundingClientRect();
      if (!rect || rect.width < 35 || rect.height < 35) return;
      if (node.children.length > 8) return;

      node.classList.add("petri-006i-card");
      if (!node.getAttribute("title")) node.setAttribute("title", text.replace(/\s+/g, " ").slice(0, 160));
      count += 1;
    });

    return count;
  }

  function addPanelEmptyState(panel, label, text) {
    if (!panel) return;
    if (panel.querySelector("[data-petri-006i-empty-state='" + label + "']")) return;

    const cards = panel.querySelectorAll(".petri-006i-card");
    if (cards.length > 0) return;

    const empty = document.createElement("div");
    empty.className = "petri-006i-empty-state";
    empty.setAttribute("data-petri-006i-empty-state", label);
    empty.textContent = text;
    panel.appendChild(empty);
  }

  function polishPanels() {
    const metrics = smallestPanelContaining("metric charts");
    const emergent = smallestPanelContaining("emergent conditions");

    const metricCards = labelCards(metrics, "metric");
    const emergentCards = labelCards(emergent, "emergent");

    addPanelEmptyState(metrics, "metric", "Metric trends appear after simulation data is available.");
    addPanelEmptyState(emergent, "emergent", "Emergent conditions will surface as readable event cards.");

    document.documentElement.setAttribute("data-petri-006i", "ready");
    document.documentElement.setAttribute("data-petri-006i-metric-cards", String(metricCards));
    document.documentElement.setAttribute("data-petri-006i-emergent-cards", String(emergentCards));

    return { metricCards: metricCards, emergentCards: emergentCards };
  }

  function emitRepairReceipt(removed, panels) {
    if (!window.PetriEventBus) return;
    window.PetriEventBus.emit("receipt:written", {
      id: "006i-dashboard-polish",
      label: "006I dashboard polish active",
      removedDuplicateDrugOptions: removed,
      metricCards: panels.metricCards,
      emergentCards: panels.emergentCards,
      boundary: "educational UI polish only"
    }, {
      source: "PetriDashboardPolish006I.boot",
      bridge: "006I"
    });
  }

  let scheduled = false;
  function scheduleRepair() {
    if (scheduled) return;
    scheduled = true;
    window.setTimeout(function () {
      scheduled = false;
      const removed = dedupeDrugSelects();
      patchRegistryLoader();
      const panels = polishPanels();
      if (removed || panels.metricCards || panels.emergentCards) {
        emitRepairReceipt(removed, panels);
      }
    }, 80);
  }

  function boot() {
    patchRegistryLoader();
    scheduleRepair();

    window.addEventListener("petri:registry:loaded", scheduleRepair);
    window.addEventListener("petri:drug:selected", scheduleRepair);
    window.addEventListener("petri:simulation:step", scheduleRepair);

    const observer = new MutationObserver(scheduleRepair);
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  window.PetriDashboardPolish006I = Object.freeze({
    version: VERSION,
    dedupeSelectOptions: dedupeSelectOptions,
    dedupeDrugSelects: dedupeDrugSelects,
    dedupeArray: dedupeArray,
    patchRegistryLoader: patchRegistryLoader,
    polishPanels: polishPanels,
    scheduleRepair: scheduleRepair
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
