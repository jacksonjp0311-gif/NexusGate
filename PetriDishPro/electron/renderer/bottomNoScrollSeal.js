(() => {
  "use strict";

  const SEAL = "PETRI_005A_BOTTOM_ROW_NO_SCROLL_SEAL";

  function byId(id) { return document.getElementById(id); }

  function norm(text) {
    return String(text || "").replace(/\s+/g, " ").trim().toUpperCase();
  }

  function dock() {
    return byId("petri-bottom-dock");
  }

  function hardResetDockPosition() {
    const d = dock();
    if (!d) return false;

    d.dataset.seal005a = SEAL;
    d.style.setProperty("position", "relative", "important");
    d.style.setProperty("left", "auto", "important");
    d.style.setProperty("right", "auto", "important");
    d.style.setProperty("bottom", "auto", "important");
    d.style.setProperty("top", "auto", "important");
    d.style.setProperty("height", "154px", "important");
    d.style.setProperty("max-height", "154px", "important");
    d.style.setProperty("width", "calc(100vw - 18px)", "important");
    d.style.setProperty("margin", "8px 9px 0 9px", "important");
    d.style.setProperty("overflow", "hidden", "important");

    // Keep the dock in normal document flow directly after the main microscope row.
    // This removes the huge vertical dead-space created by the 004Z fixed-bottom dock.
    const rightPanel = Array.from(document.querySelectorAll("section,aside,.panel,[class*='panel'],[class*='registry']"))
      .find(el => norm(el.textContent).includes("ORGANISM REGISTRY"));
    const centralPanel = Array.from(document.querySelectorAll("section,main,.panel,[class*='panel'],[class*='stage'],[class*='microscope']"))
      .find(el => norm(el.textContent).includes("REGISTRY LOADED") || norm(el.textContent).includes("LIVE SIM"));
    const anchor = rightPanel || centralPanel;
    if (anchor && anchor.parentElement && d.previousElementSibling !== anchor.parentElement) {
      const parent = anchor.parentElement;
      if (parent && parent.parentElement && parent.parentElement !== d) {
        parent.parentElement.insertBefore(d, parent.nextSibling);
      }
    }

    return true;
  }

  function removeScrollbars() {
    const d = dock();
    if (!d) return;

    d.querySelectorAll("*").forEach(el => {
      el.style.setProperty("scrollbar-width", "none", "important");
      el.style.setProperty("-ms-overflow-style", "none", "important");
    });

    d.querySelectorAll(".petri-dock-panel").forEach(panel => {
      panel.style.setProperty("overflow", "hidden", "important");
      panel.style.setProperty("height", "154px", "important");
      panel.style.setProperty("max-height", "154px", "important");
      panel.style.setProperty("min-height", "0", "important");
    });
  }

  function compactMetrics() {
    const d = dock();
    if (!d) return;
    const panel = d.querySelector(".petri-panel-metrics");
    if (!panel || panel.dataset.petri005aCompact === "true") return;

    const text = panel.textContent || "";
    const pairs = [];
    const patterns = [
      ["Total Cells", /TOTAL\s+CELLS\s+([0-9.]+)/i],
      ["Active Organisms", /ACTIVE\s+ORGANISMS\s+([0-9.]+)/i],
      ["Particles", /PARTICLES\s+([0-9.]+)/i],
      ["FPS", /FPS\s+([0-9.]+)/i]
    ];
    patterns.forEach(([label, rx]) => {
      const m = text.match(rx);
      if (m) pairs.push([label, m[1]]);
    });

    if (!pairs.length) return;
    panel.innerHTML = `<h3>METRICS</h3><div class="petri-005a-metric-grid">${
      pairs.map(([label, value]) => `<div class="petri-005a-metric"><span>${label}</span><b>${value}</b></div>`).join("")
    }</div>`;
    panel.dataset.petri005aCompact = "true";
  }

  function compactEmergent() {
    const d = dock();
    if (!d) return;
    const panel = d.querySelector(".petri-panel-emergent");
    if (!panel || panel.dataset.petri005aCompact === "true") return;

    const text = panel.textContent || "";
    const cards = [];
    const active = text.match(/Active\s+organism\s+types\s+([0-9.]+)/i);
    const preset = text.match(/Preset\s+([A-Za-z ]+)/i);
    const artifact = text.match(/Cell\s+artifact\s+load\s+([0-9.]+)/i);

    cards.push(["Active organism types", active ? active[1] : "4"]);
    cards.push(["Preset", preset ? preset[1].trim().slice(0, 22) : "Microbial competition"]);
    cards.push(["Cell artifact load", artifact ? artifact[1] : "ready"]);

    panel.innerHTML = `<h3>EMERGENT CONDITIONS</h3><div class="petri-005a-condition-grid">${
      cards.map(([label, value]) => `<div class="petri-005a-condition"><b>${value}</b><span>${label}</span></div>`).join("")
    }</div>`;
    panel.dataset.petri005aCompact = "true";
  }

  function compactReceipt() {
    const d = dock();
    if (!d) return;
    const panel = d.querySelector(".petri-panel-receipt");
    if (!panel) return;

    // If 004Z already humanized it, this mostly just enforces sizing.
    const rows = panel.querySelector(".petri-receipt-readable");
    if (rows) {
      rows.style.setProperty("height", "112px", "important");
      rows.style.setProperty("overflow", "hidden", "important");
    }
    panel.querySelectorAll("pre,code,textarea").forEach(el => {
      el.style.setProperty("overflow", "hidden", "important");
      el.style.setProperty("max-height", "108px", "important");
    });
  }

  function layout() {
    const ok = hardResetDockPosition();
    if (!ok) return;
    document.documentElement.classList.add("petri-005a-bottom-row-active");
    document.body.classList.add("petri-005a-bottom-row-active");
    removeScrollbars();
    compactMetrics();
    compactReceipt();
    compactEmergent();
  }

  let tries = 0;
  function cycle() {
    tries += 1;
    layout();
    if (tries < 16) window.setTimeout(cycle, 250);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", cycle, { once: true });
  } else {
    cycle();
  }

  window.addEventListener("resize", () => window.setTimeout(layout, 60));
  window.PETRI_005A_BOTTOM_ROW_NO_SCROLL_SEAL = { layout };
})();
