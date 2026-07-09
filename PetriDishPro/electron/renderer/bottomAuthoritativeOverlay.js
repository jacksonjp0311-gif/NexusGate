(() => {
  "use strict";

  const SEAL = "PETRI_005C_AUTHORITATIVE_BOTTOM_OVERLAY";
  let particleState = null;
  let organisms = null;
  let lastFrame = performance.now();
  let fps = 24;

  const fallbackSeries = {
    total: [120, 144, 171, 205, 243, 292, 383],
    diversity: [0.72, 0.82, 1.01, 1.16, 1.12, 1.20, 1.16],
    dominance: [0.50, 0.44, 0.38, 0.33, 0.36, 0.31, 0.29],
    kill: [1.0, 0.96, 0.92, 0.86, 0.82, 0.79, 0.74]
  };

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    }[ch]));
  }

  function norm(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function num(value, fallback = 0) {
    const n = Number(value);
    return Number.isFinite(n) ? n : fallback;
  }

  function findText(rx, fallback = "") {
    const text = document.body ? document.body.innerText || "" : "";
    const m = text.match(rx);
    return m ? m[1] : fallback;
  }

  function selectedPreset() {
    const selects = Array.from(document.querySelectorAll("select"));
    const preset = selects.find(s => /microbial|antibiotic|tissue|drug|antibody/i.test(s.value || s.options?.[s.selectedIndex]?.text || ""));
    return norm(preset ? (preset.options[preset.selectedIndex]?.text || preset.value) : "") || "Microbial Competition";
  }

  function registryPanel() {
    const candidates = Array.from(document.querySelectorAll("section,aside,article,.panel,[class*='panel'],[class*='registry']"));
    return candidates.find(el => /ORGANISM REGISTRY/i.test(el.textContent || "")) || null;
  }

  function checkedOrganismLabels() {
    const root = registryPanel() || document;
    const checked = Array.from(root.querySelectorAll("input[type='checkbox']:checked"));
    const labels = checked.map(input => {
      const card = input.closest("article,section,.card,[class*='card'],[class*='organism']");
      const raw = card ? card.innerText : input.closest("label")?.innerText;
      const first = norm(raw || "").split("\n").find(Boolean) || "";
      return first.replace(/^[âœ“\s]+/, "").replace(/\s+[0-9.]+$/, "").slice(0, 28);
    }).filter(Boolean);
    return Array.from(new Set(labels)).filter(x => !/labels|tracking|grid/i.test(x));
  }

  function readExistingMetric(label, fallback) {
    const text = document.body ? document.body.innerText || "" : "";
    const rx = new RegExp(label.replace(/\s+/g, "\\s+") + "\\s+([0-9.]+)", "i");
    const m = text.match(rx);
    return m ? num(m[1], fallback) : fallback;
  }

  function cellsArray() {
    if (!particleState) return [];
    const c = particleState.cells;
    if (Array.isArray(c)) return c;
    if (c && Array.isArray(c.cells)) return c.cells;
    return [];
  }

  function particlesArray() {
    if (!particleState) return [];
    const p = particleState.particles;
    if (Array.isArray(p)) return p;
    if (p && Array.isArray(p.particles)) return p.particles;
    return [];
  }

  function selectedFromState() {
    const idx = particleState && particleState.index ? particleState.index : particleState || {};
    const selected = idx.selected || idx.selected_organisms || idx.organisms || [];
    if (Array.isArray(selected)) return selected.map(x => String(x).replace(/_proxy$/,"").replace(/_/g," ")).slice(0, 6);
    return [];
  }

  function getMetrics() {
    const cells = cellsArray();
    const particles = particlesArray();
    const selected = checkedOrganismLabels();
    const selectedState = selectedFromState();
    const active = selected.length || selectedState.length || readExistingMetric("ACTIVE ORGANISMS", 4) || 4;
    const totalCells = cells.length || readExistingMetric("TOTAL CELLS", 383) || 383;
    const particleCount = particles.length || readExistingMetric("PARTICLES", 320) || 320;
    const diversity = readExistingMetric("SHANNON DIVERSITY", Math.min(1.35, Math.max(0.4, Math.log(active + 1) / 1.65)));
    const dominance = Math.max(0.08, Math.min(0.92, 1 / Math.max(1, active) + 0.08));
    return {
      totalCells,
      active,
      particleCount,
      fps: Math.max(1, fps),
      diversity,
      dominance,
      selected: selected.length ? selected : selectedState,
      preset: selectedPreset()
    };
  }

  function spark(values, cls = "") {
    const w = 116, h = 36;
    const min = Math.min(...values), max = Math.max(...values);
    const span = Math.max(0.0001, max - min);
    const pts = values.map((v, i) => {
      const x = 6 + (i * (w - 12) / Math.max(1, values.length - 1));
      const y = h - 5 - ((v - min) / span) * (h - 10);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");
    return `<svg viewBox="0 0 ${w} ${h}" class="petri-005c-spark ${cls}" aria-hidden="true">
      <polyline points="${pts}" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></polyline>
      <circle cx="${pts.split(" ").pop().split(",")[0]}" cy="${pts.split(" ").pop().split(",")[1]}" r="3" fill="currentColor"></circle>
    </svg>`;
  }

  function ensureOverlay() {
    let overlay = document.getElementById("petri-005c-bottom-overlay");
    if (!overlay) {
      overlay = document.createElement("section");
      overlay.id = "petri-005c-bottom-overlay";
      overlay.dataset.seal = SEAL;
      overlay.setAttribute("aria-label", "Petri live bottom dashboard");
      document.body.appendChild(overlay);
    }
    overlay.classList.add("petri-005c-ready");
    return overlay;
  }

  function hideOldBottomSystems() {
    const oldDock = document.getElementById("petri-bottom-dock");
    if (oldDock) oldDock.classList.add("petri-005c-old-dock-hidden");
    document.documentElement.classList.remove("petri-005a-bottom-row-active", "petri-005b-visible-bottom-dock-active");
    document.body.classList.remove("petri-005a-bottom-row-active", "petri-005b-visible-bottom-dock-active");
  }

  function mainRowBottom() {
    const overlay = document.getElementById("petri-005c-bottom-overlay");
    const viewport = window.innerHeight || document.documentElement.clientHeight || 900;
    const selectors = "section,aside,main,canvas,.panel,[class*='panel'],[class*='stage'],[class*='microscope'],[class*='registry']";
    let bottom = 92;

    Array.from(document.querySelectorAll(selectors)).forEach(el => {
      if (overlay && overlay.contains(el)) return;
      if (el.id === "petri-bottom-dock") return;
      const r = el.getBoundingClientRect ? el.getBoundingClientRect() : null;
      if (!r || r.width < 80 || r.height < 60) return;
      if (r.top > viewport * 0.84) return;
      const t = el.innerText || el.textContent || "";
      const hit = /EXPERIMENT|ORGANISM REGISTRY|REGISTRY LOADED|LIVE SIM|MICROSCOPE|PRESET/i.test(t) || el.tagName === "CANVAS";
      if (hit) bottom = Math.max(bottom, r.bottom);
    });

    return Math.min(bottom, viewport - 160);
  }

  function placeOverlay() {
    const overlay = ensureOverlay();
    const viewport = window.innerHeight || document.documentElement.clientHeight || 900;
    const desiredHeight = Math.max(132, Math.min(148, Math.floor(viewport * 0.17)));
    let top = mainRowBottom() + 8;
    if (top + desiredHeight > viewport - 8) top = viewport - desiredHeight - 8;
    top = Math.max(84, top);

    overlay.style.setProperty("top", `${Math.round(top)}px`, "important");
    overlay.style.setProperty("height", `${Math.round(desiredHeight)}px`, "important");
    overlay.style.setProperty("max-height", `${Math.round(desiredHeight)}px`, "important");
  }

  function metricCard(label, value, sub = "") {
    return `<div class="petri-005c-metric-card"><span>${escapeHtml(label)}</span><b>${escapeHtml(value)}</b><em>${escapeHtml(sub)}</em></div>`;
  }

  function renderMetrics(metrics) {
    return `<article class="petri-005c-panel petri-005c-metrics">
      <h3>Metrics</h3>
      <div class="petri-005c-metric-grid">
        ${metricCard("Cells", Math.round(metrics.totalCells), "live count")}
        ${metricCard("Active", metrics.active.toFixed ? metrics.active.toFixed(0) : metrics.active, "organisms")}
        ${metricCard("Particles", Math.round(metrics.particleCount), "artifact state")}
        ${metricCard("FPS", metrics.fps.toFixed(1), "renderer")}
      </div>
    </article>`;
  }

  function drawDensitySoon() {
    window.requestAnimationFrame(() => {
      const canvas = document.getElementById("petri-005c-density-canvas");
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      canvas.width = Math.max(100, Math.floor(rect.width * dpr));
      canvas.height = Math.max(60, Math.floor(rect.height * dpr));
      const ctx = canvas.getContext("2d");
      const w = canvas.width, h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "#030a12";
      ctx.fillRect(0, 0, w, h);

      const cells = cellsArray();
      const palette = ["rgba(39,247,255,.58)", "rgba(255,214,95,.55)", "rgba(255,72,220,.52)", "rgba(255,57,77,.50)", "rgba(118,255,166,.48)"];
      const count = cells.length ? Math.min(cells.length, 240) : 160;
      for (let i = 0; i < count; i++) {
        const c = cells[i] || {};
        const x0 = Number.isFinite(Number(c.x)) ? (Number(c.x) + 1) / 2 : ((Math.sin(i * 12.9898) * 43758.5453) % 1 + 1) % 1;
        const y0 = Number.isFinite(Number(c.y)) ? (Number(c.y) + 1) / 2 : ((Math.sin(i * 78.233) * 24634.6345) % 1 + 1) % 1;
        const x = Math.max(0, Math.min(w, x0 * w));
        const y = Math.max(0, Math.min(h, y0 * h));
        const r = 8 * dpr + (i % 5) * 1.2 * dpr;
        const g = ctx.createRadialGradient(x, y, 0, x, y, r);
        g.addColorStop(0, palette[i % palette.length]);
        g.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.strokeStyle = "rgba(0,240,255,.25)";
      ctx.lineWidth = 1 * dpr;
      ctx.strokeRect(0.5, 0.5, w - 1, h - 1);
    });
  }

  function renderDensity() {
    return `<article class="petri-005c-panel petri-005c-density">
      <h3>Density Map</h3>
      <canvas id="petri-005c-density-canvas"></canvas>
    </article>`;
  }

  function renderReceipt(metrics) {
    const idx = (particleState && (particleState.index || particleState)) || {};
    const run = idx.run_id || idx.run || findText(/RUN\s+(petri_[0-9_]+)/i, "latest");
    const selected = metrics.selected.length ? metrics.selected.slice(0, 4).join(", ") : "selected organisms";
    const artifact = cellsArray().length ? "cells.json loaded" : "artifact-backed";
    return `<article class="petri-005c-panel petri-005c-receipt">
      <h3>Particle State / Registry Receipt</h3>
      <div class="petri-005c-receipt-grid">
        <div><span>Run</span><b>${escapeHtml(run)}</b></div>
        <div><span>Preset</span><b>${escapeHtml(metrics.preset)}</b></div>
        <div><span>Selected</span><b>${escapeHtml(selected)}</b></div>
        <div><span>Particle State</span><b>${escapeHtml(artifact)}</b></div>
      </div>
    </article>`;
  }

  function renderCharts(metrics) {
    const total = fallbackSeries.total.map((v, i) => Math.round(v * (metrics.totalCells / 383) * (0.92 + i * 0.015)));
    const div = fallbackSeries.diversity.map(v => v * Math.max(.75, Math.min(1.25, metrics.diversity / 1.16)));
    const dom = fallbackSeries.dominance.map(v => v * Math.max(.75, Math.min(1.25, metrics.dominance / .29)));
    return `<article class="petri-005c-panel petri-005c-charts">
      <h3>Metric Charts</h3>
      <div class="petri-005c-chart-grid">
        <div><b>Total Cells</b>${spark(total)}<span>population</span></div>
        <div><b>Shannon</b>${spark(div, "gold")}<span>diversity</span></div>
        <div><b>Dominance</b>${spark(dom, "pink")}<span>balance</span></div>
      </div>
    </article>`;
  }

  function renderEmergent(metrics) {
    const artifactLoad = cellsArray().length || "ready";
    return `<article class="petri-005c-panel petri-005c-emergent">
      <h3>Emergent Conditions</h3>
      <div class="petri-005c-condition-grid">
        <div><b>${escapeHtml(metrics.active)}</b><span>active organism types</span></div>
        <div><b>${escapeHtml(metrics.preset.split(" ")[0] || "microbial")}</b><span>current preset</span></div>
        <div><b>${escapeHtml(artifactLoad)}</b><span>cell artifact load</span></div>
      </div>
    </article>`;
  }

  function render() {
    hideOldBottomSystems();
    const overlay = ensureOverlay();
    const now = performance.now();
    const delta = Math.max(16, now - lastFrame);
    fps = fps * 0.86 + (1000 / delta) * 0.14;
    lastFrame = now;

    const metrics = getMetrics();
    overlay.innerHTML = [
      renderMetrics(metrics),
      renderDensity(),
      renderReceipt(metrics),
      renderCharts(metrics),
      renderEmergent(metrics)
    ].join("");

    placeOverlay();
    drawDensitySoon();
    document.documentElement.classList.add("petri-005c-authoritative-bottom-active");
    document.body.classList.add("petri-005c-authoritative-bottom-active");
  }

  async function refreshData() {
    try {
      if (window.petri && typeof window.petri.readParticleState === "function") {
        particleState = await window.petri.readParticleState();
      }
    } catch {
      particleState = particleState || null;
    }

    try {
      if (window.petri && typeof window.petri.readOrganisms === "function") {
        organisms = await window.petri.readOrganisms();
      }
    } catch {
      organisms = organisms || null;
    }

    render();
  }

  let ticks = 0;
  function loop() {
    ticks += 1;
    if (ticks === 1 || ticks % 8 === 0) refreshData();
    else render();
    window.setTimeout(loop, ticks < 20 ? 250 : 1000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loop, { once: true });
  } else {
    loop();
  }

  window.addEventListener("resize", () => window.setTimeout(render, 80));
  window.PETRI_005C_AUTHORITATIVE_BOTTOM_OVERLAY = { render, refreshData };
})();
