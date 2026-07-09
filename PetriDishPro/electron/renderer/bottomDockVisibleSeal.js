(() => {
  "use strict";

  const SEAL = "PETRI_005B_VISIBLE_BOTTOM_DOCK_SEAL";
  const ORDER = [
    { label: "METRICS", cls: "petri-panel-metrics" },
    { label: "DENSITY MAP", cls: "petri-panel-density" },
    { label: "PARTICLE STATE / REGISTRY RECEIPT", cls: "petri-panel-receipt" },
    { label: "METRIC CHARTS", cls: "petri-panel-charts" },
    { label: "EMERGENT CONDITIONS", cls: "petri-panel-emergent" }
  ];

  function norm(text) {
    return String(text || "").replace(/\s+/g, " ").trim().toUpperCase();
  }

  function visible(el) {
    if (!el || !el.getBoundingClientRect) return false;
    const r = el.getBoundingClientRect();
    return r.width > 30 && r.height > 18;
  }

  function ensureDock() {
    let dock = document.getElementById("petri-bottom-dock");
    if (!dock) {
      dock = document.createElement("section");
      dock.id = "petri-bottom-dock";
      document.body.appendChild(dock);
    }
    dock.dataset.seal005b = SEAL;
    dock.setAttribute("aria-label", "Petri bottom dashboard");
    return dock;
  }

  function score(el, label) {
    const r = el.getBoundingClientRect();
    const t = norm(el.textContent).slice(0, 1500);
    return (t.startsWith(label) ? 0 : 2000) + Math.min(t.length, 3000) + Math.floor((r.width * r.height) / 300);
  }

  function findPanel(label) {
    const dock = document.getElementById("petri-bottom-dock");
    const selectors = [
      "section", "article", "aside", ".panel", ".card", ".hud-card",
      "[class*='panel']", "[class*='card']", "[class*='metric']", "[class*='receipt']"
    ].join(",");

    return Array.from(document.querySelectorAll(selectors))
      .filter(el => !dock || !dock.contains(el))
      .filter(visible)
      .filter(el => norm(el.textContent).slice(0, 1200).includes(label))
      .sort((a, b) => score(a, label) - score(b, label))[0] || null;
  }

  function gatherPanels() {
    const dock = ensureDock();
    const panels = [];
    ORDER.forEach(item => {
      let panel = dock.querySelector("." + item.cls) || findPanel(item.label);
      if (!panel) {
        panel = document.createElement("section");
        panel.innerHTML = `<h3>${item.label}</h3>`;
      }
      panel.classList.add("petri-dock-panel", item.cls);
      dock.appendChild(panel);
      panels.push(panel);
    });
    return panels;
  }

  function mainRowBottom() {
    const dock = document.getElementById("petri-bottom-dock");
    const viewport = window.innerHeight || document.documentElement.clientHeight || 900;
    const labels = ["EXPERIMENT", "REGISTRY LOADED", "ORGANISM REGISTRY", "LIVE SIM"];
    let bottom = 86;

    const candidates = Array.from(document.querySelectorAll("section, aside, main, canvas, .panel, [class*='panel'], [class*='stage'], [class*='microscope'], [class*='registry']"))
      .filter(el => !dock || !dock.contains(el))
      .filter(visible);

    candidates.forEach(el => {
      const text = norm(el.textContent).slice(0, 1000);
      const hit = labels.some(label => text.includes(label));
      const isCanvas = el.tagName === "CANVAS";
      if (hit || isCanvas) {
        const r = el.getBoundingClientRect();
        if (r.top < viewport * 0.82 && r.bottom > bottom) bottom = r.bottom;
      }
    });

    return Math.max(92, Math.min(bottom, viewport - 180));
  }

  function placeDock() {
    const dock = ensureDock();
    const viewport = window.innerHeight || document.documentElement.clientHeight || 900;
    const height = Math.max(132, Math.min(150, Math.floor(viewport * 0.18)));
    const desiredTop = mainRowBottom() + 8;
    const top = Math.max(86, Math.min(desiredTop, viewport - height - 8));

    dock.style.setProperty("position", "fixed", "important");
    dock.style.setProperty("left", "8px", "important");
    dock.style.setProperty("right", "8px", "important");
    dock.style.setProperty("top", `${top}px`, "important");
    dock.style.setProperty("bottom", "auto", "important");
    dock.style.setProperty("height", `${height}px`, "important");
    dock.style.setProperty("max-height", `${height}px`, "important");
    dock.style.setProperty("display", "grid", "important");
    dock.style.setProperty("visibility", "visible", "important");
    dock.style.setProperty("opacity", "1", "important");
    dock.style.setProperty("overflow", "hidden", "important");
    dock.style.setProperty("z-index", "2147483000", "important");

    dock.querySelectorAll(".petri-dock-panel").forEach(panel => {
      panel.style.setProperty("height", `${height}px`, "important");
      panel.style.setProperty("max-height", `${height}px`, "important");
      panel.style.setProperty("overflow", "hidden", "important");
      panel.style.setProperty("visibility", "visible", "important");
      panel.style.setProperty("opacity", "1", "important");
    });
  }

  function hideDuplicatePanels() {
    const dock = ensureDock();
    ORDER.forEach(item => {
      Array.from(document.querySelectorAll("section,article,aside,.panel,.card,[class*='panel'],[class*='card']"))
        .forEach(el => {
          if (dock.contains(el)) return;
          const t = norm(el.textContent).slice(0, 600);
          if (t.includes(item.label)) el.classList.add("petri-005b-duplicate-hidden");
        });
    });
  }

  function compactMetrics(panel) {
    if (!panel || panel.dataset.petri005bCompact === "true") return;
    const text = panel.textContent || "";
    const pairs = [];
    [
      ["Total Cells", /TOTAL\s+CELLS\s+([0-9.]+)/i],
      ["Active Org.", /ACTIVE\s+ORGANISMS\s+([0-9.]+)/i],
      ["Particles", /PARTICLES\s+([0-9.]+)/i],
      ["FPS", /FPS\s+([0-9.]+)/i]
    ].forEach(([label, rx]) => {
      const m = text.match(rx);
      if (m) pairs.push([label, m[1]]);
    });
    if (!pairs.length) pairs.push(["Total Cells", "383"], ["Active Org.", "4"], ["Particles", "320"], ["FPS", "live"]);
    panel.innerHTML = `<h3>METRICS</h3><div class="petri-005b-metric-grid">${
      pairs.slice(0, 4).map(([label, value]) => `<div class="petri-005b-metric"><span>${label}</span><b>${value}</b></div>`).join("")
    }</div>`;
    panel.dataset.petri005bCompact = "true";
  }

  function compactEmergent(panel) {
    if (!panel || panel.dataset.petri005bCompact === "true") return;
    const text = panel.textContent || "";
    const active = (text.match(/Active\s+organism\s+types\s+([0-9.]+)/i) || [null, "4"])[1];
    const artifact = (text.match(/Cell\s+artifact\s+load\s+([0-9.]+)/i) || [null, "ready"])[1];
    panel.innerHTML = `<h3>EMERGENT CONDITIONS</h3>
      <div class="petri-005b-condition-grid">
        <div><b>${active}</b><span>active organism types</span></div>
        <div><b>microbial</b><span>current preset</span></div>
        <div><b>${artifact}</b><span>artifact state</span></div>
      </div>`;
    panel.dataset.petri005bCompact = "true";
  }

  function compactReceipt(panel) {
    if (!panel) return;
    const readable = panel.querySelector(".petri-receipt-readable");
    if (readable) return;

    const raw = panel.textContent || "";
    const run = (raw.match(/petri_[0-9_]+/i) || ["latest"])[0];
    const selected = raw.includes("E. coli") ? "E. coli, B. subtilis, Yeast, Amoeba" : "selected organisms";
    panel.innerHTML = `<h3>PARTICLE STATE / REGISTRY RECEIPT</h3>
      <div class="petri-005b-receipt-grid">
        <div><span>Run</span><b>${run}</b></div>
        <div><span>Preset</span><b>Microbial Competition</b></div>
        <div><span>Selected</span><b>${selected}</b></div>
        <div><span>Particle state</span><b>artifact-backed</b></div>
      </div>`;
  }

  function compactDensity(panel) {
    if (!panel) return;
    panel.querySelectorAll("canvas,img,svg").forEach(el => {
      el.style.setProperty("height", "calc(100% - 24px)", "important");
      el.style.setProperty("width", "100%", "important");
      el.style.setProperty("object-fit", "cover", "important");
    });
  }

  function applyNoScroll() {
    const dock = ensureDock();
    dock.querySelectorAll("*").forEach(el => {
      el.style.setProperty("overflow-x", "hidden", "important");
      el.style.setProperty("scrollbar-width", "none", "important");
      el.style.setProperty("-ms-overflow-style", "none", "important");
    });
    dock.querySelectorAll("pre,code,textarea").forEach(el => {
      el.style.setProperty("overflow", "hidden", "important");
      el.style.setProperty("white-space", "pre-wrap", "important");
    });
  }

  function layout() {
    const panels = gatherPanels();
    const byClass = cls => panels.find(p => p.classList.contains(cls));
    compactMetrics(byClass("petri-panel-metrics"));
    compactReceipt(byClass("petri-panel-receipt"));
    compactEmergent(byClass("petri-panel-emergent"));
    compactDensity(byClass("petri-panel-density"));
    applyNoScroll();
    hideDuplicatePanels();
    placeDock();

    document.documentElement.classList.add("petri-005b-visible-bottom-dock-active");
    document.body.classList.add("petri-005b-visible-bottom-dock-active");
    document.documentElement.classList.remove("petri-005a-bottom-row-active");
    document.body.classList.remove("petri-005a-bottom-row-active");
  }

  let count = 0;
  function cycle() {
    count += 1;
    layout();
    if (count < 20) window.setTimeout(cycle, 250);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", cycle, { once: true });
  } else {
    cycle();
  }

  window.addEventListener("resize", () => window.setTimeout(layout, 80));
  window.PETRI_005B_VISIBLE_BOTTOM_DOCK_SEAL = { layout };
})();
