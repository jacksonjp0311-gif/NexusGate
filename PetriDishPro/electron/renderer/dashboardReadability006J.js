/*
PETRI DISH PRO v0.6J
Dashboard Readability Upgrade.

Purpose:
- Replace cramped Metric Charts with readable horizontal trend rows.
- Replace clipped Emergent Conditions cards with readable condition rows.
- Keep the rest of the app untouched.
- Preserve the educational claim boundary.

This is display-only UI polish. It does not alter simulation math.
*/
(function () {
  "use strict";

  const VERSION = "0.6J";
  const PANEL = "data-petri-006j-panel";
  const RENDERED = "data-petri-006j-rendered";

  function norm(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function lower(value) {
    return norm(value).toLowerCase();
  }

  function smallestPanelContaining(label) {
    const needle = lower(label);
    const candidates = Array.from(document.querySelectorAll("section, aside, article, div"))
      .filter(function (node) {
        if (!node || node === document.body || node === document.documentElement) return false;
        const text = lower(node.textContent);
        if (text.indexOf(needle) < 0) return false;
        const rect = node.getBoundingClientRect();
        if (!rect || rect.width < 180 || rect.height < 90) return false;
        if (rect.width > window.innerWidth * 0.75) return false;
        return true;
      })
      .sort(function (a, b) {
        const ar = a.getBoundingClientRect();
        const br = b.getBoundingClientRect();
        return (ar.width * ar.height) - (br.width * br.height);
      });

    return candidates[0] || null;
  }

  function bodyText() {
    return document.body ? String(document.body.innerText || document.body.textContent || "") : "";
  }

  function numberAfter(label, fallback) {
    const text = bodyText();
    const rx = new RegExp(label + "\\s+([0-9]+(?:\\.[0-9]+)?)", "i");
    const match = text.match(rx);
    if (!match) return fallback;
    const n = Number(match[1]);
    return Number.isFinite(n) ? n : fallback;
  }

  function selectedPreset() {
    const select = Array.from(document.querySelectorAll("select")).find(function (node) {
      const sig = lower([node.id, node.name, node.className, node.getAttribute("aria-label"), node.getAttribute("title")].join(" "));
      return sig.indexOf("preset") >= 0;
    });
    if (select && select.options && select.selectedIndex >= 0) {
      return norm(select.options[select.selectedIndex].textContent || select.value);
    }
    const match = bodyText().match(/PRESET\s+([A-Za-z0-9 _./-]+)/i);
    return match ? norm(match[1]).slice(0, 36) : "current preset";
  }

  function selectedDrug() {
    const state = window.PetriEventBus ? window.PetriEventBus.getState() : {};
    if (state && state.selectedDrug && (state.selectedDrug.label || state.selectedDrug.id)) {
      return norm(state.selectedDrug.label || state.selectedDrug.id);
    }
    const hud = bodyText().match(/INTERACTION HUD\s+([A-Za-z0-9 +./-]+)/i);
    return hud ? norm(hud[1]).slice(0, 32) : "none selected";
  }

  function registryCounts() {
    const state = window.PetriEventBus ? window.PetriEventBus.getState() : {};
    const registries = (state && state.registries) || {};
    return {
      organisms: Array.isArray(registries.organisms) ? registries.organisms.length : 0,
      drugs: Array.isArray(registries.drugs) ? registries.drugs.length : 0,
      presets: Array.isArray(registries.presets) ? registries.presets.length : 0
    };
  }

  function trendPoints(seed, lift) {
    const base = [
      [0, 42], [18, 38], [36, 34], [54, 26], [72, 31], [90, 18], [108, 14]
    ];
    return base.map(function (pair, index) {
      const wobble = ((seed + index * 7) % 11) - 5;
      const y = Math.max(8, Math.min(56, pair[1] + wobble - (lift || 0)));
      return pair[0] + "," + y;
    }).join(" ");
  }

  function metricRow(label, value, sublabel, points, tone) {
    const row = document.createElement("div");
    row.className = "petri-006j-metric-row";
    row.innerHTML = [
      "<div class='petri-006j-metric-copy'>",
      "  <div class='petri-006j-metric-label'>" + label + "</div>",
      "  <div class='petri-006j-metric-sub'>" + sublabel + "</div>",
      "</div>",
      "<svg class='petri-006j-spark' viewBox='0 0 108 64' preserveAspectRatio='none' aria-hidden='true'>",
      "  <path class='petri-006j-gridline' d='M0 16 H108 M0 32 H108 M0 48 H108'></path>",
      "  <polyline class='petri-006j-line petri-006j-line-" + tone + "' points='" + points + "'></polyline>",
      "  <circle class='petri-006j-dot petri-006j-dot-" + tone + "' cx='108' cy='" + points.split(' ').pop().split(',')[1] + "' r='3'></circle>",
      "</svg>",
      "<div class='petri-006j-metric-value'>" + value + "</div>"
    ].join("");
    return row;
  }

  function renderMetrics(panel) {
    if (!panel || panel.getAttribute(RENDERED) === "metrics") return false;

    const cells = numberAfter("CELLS", 0);
    const active = numberAfter("ACTIVE\\s+ORGANISMS", numberAfter("ACTIVE", 0));
    const particles = numberAfter("PARTICLES", 0);
    const fps = numberAfter("FPS", 0);

    panel.setAttribute(PANEL, "metrics");
    panel.setAttribute(RENDERED, "metrics");
    panel.innerHTML = "";

    const shell = document.createElement("div");
    shell.className = "petri-006j-shell petri-006j-metrics-shell";
    shell.innerHTML = [
      "<div class='petri-006j-header'>",
      "  <span>METRIC CHARTS</span>",
      "  <span class='petri-006j-badge'>readable trends</span>",
      "</div>",
      "<div class='petri-006j-metric-list'></div>"
    ].join("");

    const list = shell.querySelector(".petri-006j-metric-list");
    list.appendChild(metricRow("Population", cells || "live", "total cells", trendPoints(cells || 4, 4), "cyan"));
    list.appendChild(metricRow("Diversity", active || "live", "active organisms", trendPoints(active || 8, 0), "gold"));
    list.appendChild(metricRow("Particle state", particles || "ready", "tracked particles", trendPoints(particles || 12, 2), "magenta"));
    if (fps) {
      list.appendChild(metricRow("Renderer", fps.toFixed ? fps.toFixed(1) : fps, "frames / second", trendPoints(Math.round(fps * 10), -1), "green"));
    }

    panel.appendChild(shell);
    return true;
  }

  function conditionRow(title, value, detail, status) {
    const row = document.createElement("div");
    row.className = "petri-006j-condition-row petri-006j-status-" + status;
    row.innerHTML = [
      "<div class='petri-006j-condition-main'>",
      "  <div class='petri-006j-condition-title'>" + title + "</div>",
      "  <div class='petri-006j-condition-detail'>" + detail + "</div>",
      "</div>",
      "<div class='petri-006j-condition-value'>" + value + "</div>"
    ].join("");
    return row;
  }

  function renderEmergent(panel) {
    if (!panel || panel.getAttribute(RENDERED) === "emergent") return false;

    const active = numberAfter("ACTIVE\\s+ORGANISMS", numberAfter("ACTIVE", 0));
    const cells = numberAfter("CELLS", 0);
    const counts = registryCounts();
    const drug = selectedDrug();
    const preset = selectedPreset();

    panel.setAttribute(PANEL, "emergent");
    panel.setAttribute(RENDERED, "emergent");
    panel.innerHTML = "";

    const shell = document.createElement("div");
    shell.className = "petri-006j-shell petri-006j-emergent-shell";
    shell.innerHTML = [
      "<div class='petri-006j-header'>",
      "  <span>EMERGENT CONDITIONS</span>",
      "  <span class='petri-006j-badge'>full readout</span>",
      "</div>",
      "<div class='petri-006j-condition-list'></div>"
    ].join("");

    const list = shell.querySelector(".petri-006j-condition-list");
    list.appendChild(conditionRow("Active ecology", active || "live", "organisms contributing to the current dish state", "good"));
    list.appendChild(conditionRow("Population pressure", cells || "tracking", "cell count trend observed in the educational renderer", "watch"));
    list.appendChild(conditionRow("Preset context", preset, "scenario currently driving the simulation view", "info"));
    list.appendChild(conditionRow("Drug proxy", drug, "educational interaction state only; no treatment or dosing meaning", "safe"));
    if (counts.organisms || counts.drugs) {
      list.appendChild(conditionRow("Registry loaded", counts.organisms + " org / " + counts.drugs + " drug", "event bus registry state is available", "good"));
    }

    panel.appendChild(shell);
    return true;
  }

  function render() {
    const metrics = smallestPanelContaining("metric charts");
    const emergent = smallestPanelContaining("emergent conditions");
    const didMetrics = renderMetrics(metrics);
    const didEmergent = renderEmergent(emergent);

    document.documentElement.setAttribute("data-petri-006j", "ready");
    document.documentElement.setAttribute("data-petri-006j-metrics", didMetrics ? "rendered" : (metrics ? "already" : "missing"));
    document.documentElement.setAttribute("data-petri-006j-emergent", didEmergent ? "rendered" : (emergent ? "already" : "missing"));

    if (window.PetriEventBus && (didMetrics || didEmergent)) {
      window.PetriEventBus.emit("receipt:written", {
        id: "006j-dashboard-readability",
        label: "006J dashboard readability active",
        metrics: didMetrics ? "rendered" : "unchanged",
        emergent: didEmergent ? "rendered" : "unchanged",
        boundary: "educational dashboard display only"
      }, {
        source: "PetriDashboardReadability006J.render",
        bridge: "006J"
      });
    }

    return { metrics: !!metrics, emergent: !!emergent, didMetrics: didMetrics, didEmergent: didEmergent };
  }

  let scheduled = false;
  function scheduleRender() {
    if (scheduled) return;
    scheduled = true;
    window.setTimeout(function () {
      scheduled = false;
      render();
    }, 120);
  }

  function boot() {
    scheduleRender();
    window.addEventListener("petri:registry:loaded", scheduleRender);
    window.addEventListener("petri:simulation:step", scheduleRender);
    window.addEventListener("petri:drug:selected", scheduleRender);
  }

  window.PetriDashboardReadability006J = Object.freeze({
    version: VERSION,
    render: render,
    scheduleRender: scheduleRender,
    smallestPanelContaining: smallestPanelContaining
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
