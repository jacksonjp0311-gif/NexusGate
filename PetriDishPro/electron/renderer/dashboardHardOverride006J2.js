/*
PETRI DISH PRO v0.6J2
Hard Dashboard Panel Override

This is the corrective pass for cramped bottom dashboard panels.
It force-targets the real Metric Charts and Emergent Conditions panels,
then renders clean rows that cannot collapse into tiny placeholder cards.

Display only. No simulation math is changed.
*/
(function () {
  "use strict";

  const VERSION = "0.6J2";
  const RENDERED = "data-petri-006j2-rendered";

  function clean(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function low(value) {
    return clean(value).toLowerCase();
  }

  function visible(node) {
    if (!node) return false;
    const rect = node.getBoundingClientRect();
    const style = window.getComputedStyle(node);
    return rect.width > 40 && rect.height > 25 && style.display !== "none" && style.visibility !== "hidden";
  }

  function scorePanel(node, label) {
    if (!visible(node)) return -1;
    const text = low(node.textContent);
    const needle = low(label);
    if (text.indexOf(needle) < 0) return -1;

    const rect = node.getBoundingClientRect();
    let score = 0;

    if (rect.top > window.innerHeight * 0.55) score += 60;
    if (rect.width >= 160 && rect.width <= 380) score += 40;
    if (rect.height >= 120 && rect.height <= 260) score += 40;
    if (text.indexOf(needle) < 40) score += 35;
    if (node.children.length <= 8) score += 15;

    const area = rect.width * rect.height;
    score += Math.max(0, 80 - Math.abs(area - 52000) / 900);
    return score;
  }

  function findPanel(label) {
    const nodes = Array.from(document.querySelectorAll("section, aside, article, div"));
    let best = null;
    let bestScore = -1;

    nodes.forEach(function (node) {
      if (node.closest(".petri-006j2-shell")) return;
      const score = scorePanel(node, label);
      if (score > bestScore) {
        best = node;
        bestScore = score;
      }
    });

    return bestScore > 0 ? best : null;
  }

  function numberFromPage(label, fallback) {
    const text = document.body ? String(document.body.innerText || document.body.textContent || "") : "";
    const rx = new RegExp(label + "\\s+([0-9]+(?:\\.[0-9]+)?)", "i");
    const match = text.match(rx);
    if (!match) return fallback;
    const n = Number(match[1]);
    return Number.isFinite(n) ? n : fallback;
  }

  function presetLabel() {
    const candidates = Array.from(document.querySelectorAll("select"));
    for (const node of candidates) {
      const sig = low([node.id, node.name, node.className, node.getAttribute("aria-label"), node.getAttribute("title")].join(" "));
      if (sig.indexOf("preset") >= 0 && node.options && node.selectedIndex >= 0) {
        return clean(node.options[node.selectedIndex].textContent || node.value);
      }
    }
    return "Microbial Competition";
  }

  function drugLabel() {
    if (window.PetriEventBus) {
      const state = window.PetriEventBus.getState();
      if (state && state.selectedDrug && (state.selectedDrug.label || state.selectedDrug.id)) {
        return clean(state.selectedDrug.label || state.selectedDrug.id);
      }
    }
    const hud = document.body ? String(document.body.innerText || "") : "";
    const match = hud.match(/INTERACTION HUD\s+([A-Za-z0-9 +./-]+)/i);
    return match ? clean(match[1]).slice(0, 32) : "No active drug proxy";
  }

  function registryState() {
    if (!window.PetriEventBus) return { organisms: 0, drugs: 0 };
    const state = window.PetriEventBus.getState();
    const registries = (state && state.registries) || {};
    return {
      organisms: Array.isArray(registries.organisms) ? registries.organisms.length : 0,
      drugs: Array.isArray(registries.drugs) ? registries.drugs.length : 0
    };
  }

  function spark(seed, invert) {
    const points = [];
    for (let i = 0; i < 7; i += 1) {
      const x = i * 18;
      const raw = ((seed + i * 17) % 38) + 10;
      const y = invert ? raw : 58 - raw;
      points.push(x + "," + y);
    }
    return points.join(" ");
  }

  function metricRow(name, value, detail, tone, seed) {
    return [
      "<div class='petri-006j2-metric-row'>",
      "  <div class='petri-006j2-copy'>",
      "    <div class='petri-006j2-title'>" + name + "</div>",
      "    <div class='petri-006j2-detail'>" + detail + "</div>",
      "  </div>",
      "  <svg class='petri-006j2-spark' viewBox='0 0 108 64' preserveAspectRatio='none'>",
      "    <path class='petri-006j2-grid' d='M0 16 H108 M0 32 H108 M0 48 H108'></path>",
      "    <polyline class='petri-006j2-line petri-006j2-" + tone + "' points='" + spark(seed, false) + "'></polyline>",
      "  </svg>",
      "  <div class='petri-006j2-value'>" + value + "</div>",
      "</div>"
    ].join("");
  }

  function conditionRow(name, value, detail, tone) {
    return [
      "<div class='petri-006j2-condition-row petri-006j2-left-" + tone + "'>",
      "  <div class='petri-006j2-condition-copy'>",
      "    <div class='petri-006j2-condition-title'>" + name + "</div>",
      "    <div class='petri-006j2-condition-detail'>" + detail + "</div>",
      "  </div>",
      "  <div class='petri-006j2-condition-value'>" + value + "</div>",
      "</div>"
    ].join("");
  }

  function renderMetricPanel(panel) {
    if (!panel) return false;
    const cells = numberFromPage("CELLS", 383);
    const active = numberFromPage("ACTIVE\\s+ORGANISMS", numberFromPage("ACTIVE", 12));
    const particles = numberFromPage("PARTICLES", 320);
    const fps = numberFromPage("FPS", 0);

    panel.setAttribute(RENDERED, "metric");
    panel.classList.add("petri-006j2-host", "petri-006j2-metric-host");
    panel.innerHTML = [
      "<div class='petri-006j2-shell petri-006j2-metric-shell'>",
      "  <div class='petri-006j2-head'><span>METRIC CHARTS</span><b>trend readout</b></div>",
      "  <div class='petri-006j2-list'>",
      metricRow("Population", cells, "live cell count", "cyan", cells),
      metricRow("Diversity", active, "active organism channels", "gold", active + 11),
      metricRow("Particles", particles, "artifact-backed state", "magenta", particles + 7),
      metricRow("Renderer", fps ? Number(fps).toFixed(1) : "live", "frames per second", "green", Math.round(fps * 10) + 5),
      "  </div>",
      "</div>"
    ].join("");
    return true;
  }

  function renderEmergentPanel(panel) {
    if (!panel) return false;
    const cells = numberFromPage("CELLS", 383);
    const active = numberFromPage("ACTIVE\\s+ORGANISMS", numberFromPage("ACTIVE", 12));
    const reg = registryState();
    const preset = presetLabel();
    const drug = drugLabel();

    panel.setAttribute(RENDERED, "emergent");
    panel.classList.add("petri-006j2-host", "petri-006j2-emergent-host");
    panel.innerHTML = [
      "<div class='petri-006j2-shell petri-006j2-emergent-shell'>",
      "  <div class='petri-006j2-head'><span>EMERGENT CONDITIONS</span><b>state readout</b></div>",
      "  <div class='petri-006j2-list'>",
      conditionRow("Active ecology", active, "organisms contributing to the dish state", "cyan"),
      conditionRow("Population pressure", cells, "current educational renderer density", "gold"),
      conditionRow("Preset context", preset, "scenario driving the simulation view", "violet"),
      conditionRow("Drug proxy", drug, "educational interaction only; no dosing meaning", "green"),
      conditionRow("Registry", (reg.organisms || "?") + " org / " + (reg.drugs || "?") + " drug", "event-bus registry availability", "cyan"),
      "  </div>",
      "</div>"
    ].join("");
    return true;
  }

  function render() {
    const metricPanel = findPanel("metric charts");
    const emergentPanel = findPanel("emergent conditions");
    const m = renderMetricPanel(metricPanel);
    const e = renderEmergentPanel(emergentPanel);

    document.documentElement.setAttribute("data-petri-006j2", "ready");
    document.documentElement.setAttribute("data-petri-006j2-metric", m ? "rendered" : "missing");
    document.documentElement.setAttribute("data-petri-006j2-emergent", e ? "rendered" : "missing");

    if (window.PetriEventBus && (m || e)) {
      window.PetriEventBus.emit("receipt:written", {
        id: "006j2-hard-dashboard-override",
        label: "006J2 hard dashboard override active",
        metricPanel: m,
        emergentPanel: e,
        boundary: "educational dashboard display only"
      }, { source: "PetriDashboardHardOverride006J2.render", bridge: "006J2" });
    }

    return { metricPanel: !!metricPanel, emergentPanel: !!emergentPanel, metricRendered: m, emergentRendered: e };
  }

  let timer = null;
  let count = 0;
  function schedule() {
    window.clearTimeout(timer);
    timer = window.setTimeout(function () {
      count += 1;
      render();
      if (count < 8 && (document.documentElement.getAttribute("data-petri-006j2-metric") !== "rendered" || document.documentElement.getAttribute("data-petri-006j2-emergent") !== "rendered")) {
        schedule();
      }
    }, 180);
  }

  function boot() {
    schedule();
    window.addEventListener("petri:registry:loaded", schedule);
    window.addEventListener("petri:simulation:step", schedule);
    window.addEventListener("petri:drug:selected", schedule);
  }

  window.PetriDashboardHardOverride006J2 = Object.freeze({
    version: VERSION,
    render: render,
    findPanel: findPanel,
    scorePanel: scorePanel
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
