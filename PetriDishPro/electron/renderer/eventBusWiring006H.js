/*
PETRI DISH PRO v0.6H
Event Bus UI Wiring

Non-destructive bridge:
- does not remove existing handlers
- does not rebuild DOM
- emits canonical events when existing controls change/click
- keeps current UI behavior intact

Boundary:
Educational simulation UI state only. No clinical, diagnostic, dosing,
treatment, susceptibility, wet-lab, or biosafety claims.
*/
(function () {
  "use strict";

  const VERSION = "0.6H";
  const BOUND = "data-petri-006h-bound";
  const KNOWN_EVENTS = Object.freeze([
    "organism:selected",
    "drug:selected",
    "drug:injected",
    "preset:changed",
    "simulation:step",
    "receipt:written"
  ]);

  function eventBus() {
    return window.PetriEventBus || null;
  }

  function textOf(node) {
    if (!node) return "";
    return String(
      node.getAttribute("aria-label") ||
      node.getAttribute("title") ||
      node.getAttribute("data-role") ||
      node.getAttribute("data-kind") ||
      node.getAttribute("data-action") ||
      node.id ||
      node.name ||
      node.className ||
      node.textContent ||
      ""
    ).toLowerCase();
  }

  function selectedPayload(node) {
    const option = node && node.options ? node.options[node.selectedIndex] : null;
    const value = String((node && node.value) || "");
    const label = String((option && option.textContent) || value || "unselected").trim();
    return {
      id: value || label,
      label: label,
      value: value,
      sourceElement: {
        tag: node ? node.tagName : null,
        id: node ? node.id || null : null,
        name: node ? node.name || null : null,
        className: node ? String(node.className || "") : ""
      }
    };
  }

  function buttonPayload(node) {
    return {
      id: node ? (node.id || node.getAttribute("data-action") || textOf(node) || "button") : "button",
      label: node ? String(node.textContent || node.getAttribute("aria-label") || node.id || "button").trim() : "button",
      sourceElement: {
        tag: node ? node.tagName : null,
        id: node ? node.id || null : null,
        className: node ? String(node.className || "") : ""
      }
    };
  }

  function inferSelectEvent(node) {
    const signature = textOf(node);
    if (signature.indexOf("drug") >= 0 || signature.indexOf("compound") >= 0 || signature.indexOf("antimicrobial") >= 0) {
      return { event: "drug:selected", collection: "drugs" };
    }
    if (signature.indexOf("preset") >= 0 || signature.indexOf("scenario") >= 0 || signature.indexOf("mode") >= 0) {
      return { event: "preset:changed", collection: "presets" };
    }
    if (signature.indexOf("organism") >= 0 || signature.indexOf("species") >= 0 || signature.indexOf("microbe") >= 0 || signature.indexOf("cell") >= 0) {
      return { event: "organism:selected", collection: "organisms" };
    }

    const optionText = Array.from(node.options || []).slice(0, 6).map(function (opt) {
      return String(opt.textContent || opt.value || "").toLowerCase();
    }).join(" ");

    if (optionText.indexOf("drug") >= 0 || optionText.indexOf("compound") >= 0) {
      return { event: "drug:selected", collection: "drugs" };
    }
    if (optionText.indexOf("preset") >= 0 || optionText.indexOf("scenario") >= 0) {
      return { event: "preset:changed", collection: "presets" };
    }

    return { event: "organism:selected", collection: "organisms" };
  }

  function inferButtonEvent(node) {
    const signature = textOf(node);
    if (signature.indexOf("inject") >= 0 || signature.indexOf("dose") >= 0 || signature.indexOf("apply drug") >= 0 || signature.indexOf("drug") >= 0) {
      return "drug:injected";
    }
    if (signature.indexOf("run") >= 0 || signature.indexOf("step") >= 0 || signature.indexOf("simulate") >= 0 || signature.indexOf("start") >= 0) {
      return "simulation:step";
    }
    if (signature.indexOf("receipt") >= 0 || signature.indexOf("export") >= 0 || signature.indexOf("save") >= 0) {
      return "receipt:written";
    }
    return null;
  }

  function emit(eventName, payload, source) {
    const bus = eventBus();
    if (!bus) return null;
    return bus.emit(eventName, payload, {
      source: source || "PetriEventBusWiring006H",
      bridge: "006H",
      boundary: "educational UI event only"
    });
  }

  function bindSelect(node) {
    if (!node || node.getAttribute(BOUND) === "true") return false;
    const inferred = inferSelectEvent(node);
    node.setAttribute(BOUND, "true");
    node.setAttribute("data-petri-006h-event", inferred.event);

    node.addEventListener("change", function () {
      const payload = selectedPayload(node);
      payload.collection = inferred.collection;
      emit(inferred.event, payload, "PetriEventBusWiring006H.select");
    });

    if (node.value) {
      const payload = selectedPayload(node);
      payload.collection = inferred.collection;
      payload.initial = true;
      emit(inferred.event, payload, "PetriEventBusWiring006H.initialSelect");
    }

    return true;
  }

  function bindButton(node) {
    if (!node || node.getAttribute(BOUND) === "true") return false;
    const eventName = inferButtonEvent(node);
    if (!eventName) return false;

    node.setAttribute(BOUND, "true");
    node.setAttribute("data-petri-006h-event", eventName);

    node.addEventListener("click", function () {
      const payload = buttonPayload(node);
      if (eventName === "drug:injected") {
        const state = eventBus() ? eventBus().getState() : {};
        payload.selectedDrug = state.selectedDrug || null;
        payload.boundary = "educational interaction proxy only";
      }
      emit(eventName, payload, "PetriEventBusWiring006H.button");
    });

    return true;
  }

  function bindInputs() {
    let bound = 0;
    document.querySelectorAll("select").forEach(function (node) {
      if (bindSelect(node)) bound += 1;
    });

    document.querySelectorAll("button, [role='button'], input[type='button'], input[type='submit']").forEach(function (node) {
      if (bindButton(node)) bound += 1;
    });

    return bound;
  }

  function writeDebugFlag(boundCount) {
    document.documentElement.setAttribute("data-petri-006h", "ready");
    document.documentElement.setAttribute("data-petri-006h-bound-count", String(boundCount));
  }

  function boot() {
    const boundCount = bindInputs();
    writeDebugFlag(boundCount);
    emit("receipt:written", {
      id: "006h-ui-wiring-ready",
      label: "006H UI wiring ready",
      boundCount: boundCount,
      events: KNOWN_EVENTS.slice()
    }, "PetriEventBusWiring006H.boot");

    const observer = new MutationObserver(function () {
      const count = bindInputs();
      writeDebugFlag(count);
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  window.PetriEventBusWiring006H = Object.freeze({
    version: VERSION,
    events: KNOWN_EVENTS,
    bindInputs: bindInputs,
    inferSelectEvent: inferSelectEvent,
    inferButtonEvent: inferButtonEvent
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
