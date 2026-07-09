/*
PETRI DISH PRO v0.6G
Registry Event Bus Foundation

Boundary:
Educational simulation UI state only. This module does not create clinical,
diagnostic, dosing, treatment, susceptibility, wet-lab, or biosafety claims.
*/
(function () {
  "use strict";

  const VERSION = "0.6G";
  const EVENT_NAMES = Object.freeze([
    "organism:selected",
    "drug:selected",
    "drug:injected",
    "preset:changed",
    "simulation:step",
    "receipt:written",
    "registry:loaded"
  ]);

  const listeners = new Map();
  const replay = [];
  const state = {
    selectedOrganism: null,
    selectedDrug: null,
    selectedPreset: null,
    lastReceipt: null,
    registries: Object.freeze({ organisms: [], drugs: [], presets: [] })
  };

  function safeClone(value) {
    if (value === undefined || value === null) return value;
    try {
      return JSON.parse(JSON.stringify(value));
    } catch (error) {
      return { value: String(value), cloneWarning: "non_json_payload" };
    }
  }

  function normalizeEventName(name) {
    if (typeof name !== "string" || !name.trim()) {
      throw new Error("PetriEventBus requires a non-empty event name.");
    }
    return name.trim();
  }

  function on(name, handler) {
    const eventName = normalizeEventName(name);
    if (typeof handler !== "function") {
      throw new Error("PetriEventBus handler must be a function.");
    }

    if (!listeners.has(eventName)) listeners.set(eventName, new Set());
    listeners.get(eventName).add(handler);

    return function unsubscribe() {
      const bucket = listeners.get(eventName);
      if (bucket) bucket.delete(handler);
    };
  }

  function emit(name, payload, meta) {
    const eventName = normalizeEventName(name);
    const packet = Object.freeze({
      event: eventName,
      payload: safeClone(payload || {}),
      meta: Object.freeze(Object.assign({
        version: VERSION,
        source: "PetriEventBus",
        emittedAt: new Date().toISOString()
      }, meta || {}))
    });

    replay.push(packet);
    if (replay.length > 200) replay.shift();

    if (eventName === "organism:selected") state.selectedOrganism = packet.payload;
    if (eventName === "drug:selected") state.selectedDrug = packet.payload;
    if (eventName === "preset:changed") state.selectedPreset = packet.payload;
    if (eventName === "receipt:written") state.lastReceipt = packet.payload;
    if (eventName === "registry:loaded") {
      state.registries = Object.freeze(Object.assign({}, state.registries, packet.payload || {}));
    }

    const bucket = listeners.get(eventName);
    if (bucket) {
      Array.from(bucket).forEach(function (handler) {
        try {
          handler(packet);
        } catch (error) {
          console.error("[PetriEventBus] handler failed", eventName, error);
        }
      });
    }

    window.dispatchEvent(new CustomEvent("petri:" + eventName, { detail: packet }));
    return packet;
  }

  function once(name, handler) {
    const unsubscribe = on(name, function (packet) {
      unsubscribe();
      handler(packet);
    });
    return unsubscribe;
  }

  function getState() {
    return safeClone(state);
  }

  function getReplay() {
    return replay.map(safeClone);
  }

  function resetReplay() {
    replay.splice(0, replay.length);
  }

  window.PetriEventBus = Object.freeze({
    version: VERSION,
    events: EVENT_NAMES,
    on: on,
    once: once,
    emit: emit,
    getState: getState,
    getReplay: getReplay,
    resetReplay: resetReplay
  });

  window.dispatchEvent(new CustomEvent("petri:event-bus-ready", {
    detail: { version: VERSION, events: EVENT_NAMES.slice() }
  }));
})();
