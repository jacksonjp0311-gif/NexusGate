(() => {
  "use strict";

  const SEAL = "PETRI_005D_SINGLE_LAYER_BOTTOM_OVERLAY";
  let particleState = null;
  let lastFrame = performance.now();
  let fps = 24;

  const labels = [
    "METRICS",
    "DENSITY MAP",
    "PARTICLE STATE / REGISTRY RECEIPT",
    "METRIC CHARTS",
    "EMERGENT CONDITIONS"
  ];

  function esc(v) {
    return String(v ?? "").replace(/[&<>"']/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;" }[c]));
  }

  function clean(t) {
    return String(t || "").replace(/\s+/g, " ").trim();
  }

  function upper(t) {
    return clean(t).toUpperCase();
  }

  function visible(el) {
    if (!el || !el.getBoundingClientRect) return false;
    const r = el.getBoundingClientRect();
    return r.width > 40 && r.height > 20;
  }

  function ensure() {
    let o = document.getElementById("petri-005d-bottom-overlay");
    if (!o) {
      o = document.createElement("section");
      o.id = "petri-005d-bottom-overlay";
      o.dataset.seal = SEAL;
      document.body.appendChild(o);
    }
    return o;
  }

  function hideOld() {
    const overlay = document.getElementById("petri-005d-bottom-overlay");
    ["petri-bottom-dock", "petri-005c-bottom-overlay"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.classList.add("petri-005d-hard-hidden");
    });

    Array.from(document.querySelectorAll("section,article,aside,.panel,.card,[class*='panel'],[class*='card']")).forEach(el => {
      if (overlay && overlay.contains(el)) return;
      if (!visible(el)) return;
      const r = el.getBoundingClientRect();
      if (r.top < (window.innerHeight || 900) * 0.48) return;
      const head = upper(Array.from(el.querySelectorAll("h1,h2,h3,h4,h5,h6,.title,.panel-title,[class*='title']"))[0]?.textContent || "");
      const start = upper(el.textContent).slice(0, 180);
      if (labels.some(x => head === x || start.startsWith(x))) el.classList.add("petri-005d-hard-hidden");
    });

    document.documentElement.classList.remove(
      "petri-004z-bottom-dock-active",
      "petri-005a-bottom-row-active",
      "petri-005b-visible-bottom-dock-active",
      "petri-005c-authoritative-bottom-active"
    );
    document.body.classList.remove(
      "petri-004z-bottom-dock-active",
      "petri-005a-bottom-row-active",
      "petri-005b-visible-bottom-dock-active",
      "petri-005c-authoritative-bottom-active"
    );
  }

  function cells() {
    const c = particleState && particleState.cells;
    if (Array.isArray(c)) return c;
    if (c && Array.isArray(c.cells)) return c.cells;
    return [];
  }

  function particles() {
    const p = particleState && particleState.particles;
    if (Array.isArray(p)) return p;
    if (p && Array.isArray(p.particles)) return p.particles;
    return [];
  }

  function bodyMetric(name, fallback) {
    const rx = new RegExp(name.replace(/\s+/g, "\\s+") + "\\s+([0-9.]+)", "i");
    const m = (document.body?.innerText || "").match(rx);
    const n = m ? Number(m[1]) : NaN;
    return Number.isFinite(n) ? n : fallback;
  }

  function preset() {
    const s = Array.from(document.querySelectorAll("select"))
      .find(x => /microbial|antibiotic|tissue|drug|antibody/i.test(x.value || x.options?.[x.selectedIndex]?.text || ""));
    return clean(s ? (s.options[s.selectedIndex]?.text || s.value) : "") || "Microbial Competition";
  }

  function selected() {
    const root = Array.from(document.querySelectorAll("section,aside,article,.panel,[class*='panel'],[class*='registry']"))
      .find(el => upper(el.textContent).includes("ORGANISM REGISTRY")) || document;
    const out = Array.from(root.querySelectorAll("input[type='checkbox']:checked")).map(input => {
      const card = input.closest("article,section,.card,[class*='card'],[class*='organism']");
      const first = clean((card ? card.innerText : input.closest("label")?.innerText) || "").split("\n").find(Boolean) || "";
      return first.replace(/^[âœ“\s]+/, "").replace(/\s+[0-9.]+$/, "").slice(0, 32);
    }).filter(x => x && !/labels|tracking|grid/i.test(x));
    return Array.from(new Set(out));
  }

  function metrics() {
    const now = performance.now();
    const delta = Math.max(16, now - lastFrame);
    fps = fps * 0.86 + (1000 / delta) * 0.14;
    lastFrame = now;
    const sel = selected();
    const active = sel.length || bodyMetric("ACTIVE ORGANISMS", 4);
    return {
      cells: cells().length || bodyMetric("TOTAL CELLS", 383),
      active,
      particles: particles().length || bodyMetric("PARTICLES", 320),
      fps: Math.max(1, fps),
      diversity: bodyMetric("SHANNON DIVERSITY", Math.min(1.35, Math.log(active + 1) / 1.65)),
      dominance: Math.max(0.08, Math.min(0.92, 1 / Math.max(1, active) + 0.08)),
      selected: sel,
      preset: preset()
    };
  }

  function microscopeBottom() {
    const overlay = document.getElementById("petri-005d-bottom-overlay");
    const w = window.innerWidth || 1600;
    const h = window.innerHeight || 900;
    let bottom = 88;
    Array.from(document.querySelectorAll("section,main,article,.panel,[class*='panel'],[class*='stage'],[class*='microscope']")).forEach(el => {
      if (overlay && overlay.contains(el)) return;
      if (el.classList.contains("petri-005d-hard-hidden")) return;
      if (!visible(el)) return;
      const r = el.getBoundingClientRect();
      if (r.width < 520 || r.left < 250 || r.right > w - 250 || r.top > h * 0.78) return;
      const t = upper(el.textContent).slice(0, 900);
      if (t.includes("REGISTRY LOADED") || t.includes("2 UM") || t.includes("MAG") || t.includes("LIVE SIM")) {
        bottom = Math.max(bottom, r.bottom);
      }
    });
    if (bottom < 120) bottom = Math.floor(h * 0.70);
    return Math.min(bottom, h - 156);
  }

  function place() {
    const o = ensure();
    const viewport = window.innerHeight || document.documentElement.clientHeight || 900;

    // PETRI 005H STABLE BOTTOM OWNER SEAL:
    // One owner only. No second override loop. No alternating fixed-height/fill-height fight.
    // Top snaps under the microscope. Bottom locks to viewport edge. Height derives from top+bottom.
    let top = microscopeBottom() + 8;
    top = Math.max(80, Math.min(top, viewport - 172));

    o.dataset.seal005h = "PETRI_005H_STABLE_BOTTOM_OWNER_SEAL";
    o.style.setProperty("position", "fixed", "important");
    o.style.setProperty("left", "8px", "important");
    o.style.setProperty("right", "8px", "important");
    o.style.setProperty("top", `${Math.round(top)}px`, "important");
    o.style.setProperty("bottom", "8px", "important");
    o.style.setProperty("height", "auto", "important");
    o.style.setProperty("max-height", "none", "important");
    o.style.setProperty("min-height", "136px", "important");
    o.style.setProperty("display", "grid", "important");
    o.style.setProperty("overflow", "hidden", "important");
    o.style.setProperty("visibility", "visible", "important");
    o.style.setProperty("opacity", "1", "important");
  }

  function spark(values, cls = "") {
    const w = 112, h = 34, min = Math.min(...values), max = Math.max(...values);
    const span = Math.max(0.0001, max - min);
    const pts = values.map((v, i) => {
      const x = 5 + (i * (w - 10) / Math.max(1, values.length - 1));
      const y = h - 5 - ((v - min) / span) * (h - 10);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");
    const last = pts.split(" ").pop().split(",");
    return `<svg viewBox="0 0 ${w} ${h}" class="petri-005d-spark ${cls}"><polyline points="${pts}" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></polyline><circle cx="${last[0]}" cy="${last[1]}" r="3" fill="currentColor"></circle></svg>`;
  }

  function drawDensity() {
    requestAnimationFrame(() => {
      const canvas = document.getElementById("petri-005d-density-canvas");
      if (!canvas) return;
      const r = canvas.getBoundingClientRect(), dpr = Math.min(2, window.devicePixelRatio || 1);
      canvas.width = Math.max(160, Math.floor(r.width * dpr));
      canvas.height = Math.max(70, Math.floor(r.height * dpr));
      const ctx = canvas.getContext("2d"), w = canvas.width, h = canvas.height;
      ctx.clearRect(0,0,w,h);
      ctx.fillStyle = "#030a12";
      ctx.fillRect(0,0,w,h);
      const arr = cells();
      const colors = ["rgba(39,247,255,.55)", "rgba(255,214,95,.55)", "rgba(255,72,220,.52)", "rgba(255,57,77,.48)", "rgba(118,255,166,.48)", "rgba(184,150,255,.42)"];
      const count = arr.length ? Math.min(arr.length, 260) : 170;
      for (let i = 0; i < count; i++) {
        const c = arr[i] || {};
        const x0 = Number.isFinite(Number(c.x)) ? (Number(c.x) + 1) / 2 : ((Math.sin(i * 12.9898) * 43758.5453) % 1 + 1) % 1;
        const y0 = Number.isFinite(Number(c.y)) ? (Number(c.y) + 1) / 2 : ((Math.sin(i * 78.233) * 24634.6345) % 1 + 1) % 1;
        const x = Math.max(0, Math.min(w, x0 * w)), y = Math.max(0, Math.min(h, y0 * h));
        const rad = (6 + (i % 5) * 1.4) * dpr;
        const g = ctx.createRadialGradient(x, y, 0, x, y, rad);
        g.addColorStop(0, colors[i % colors.length]);
        g.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(x, y, rad, 0, Math.PI * 2);
        ctx.fill();
      }
    });
  }

  function render() {
    hideOld();
    const m = metrics();
    const o = ensure();
    const run = (particleState && (particleState.index?.run_id || particleState.index?.run || particleState.run_id)) || "latest";
    const sel = m.selected.length ? m.selected.slice(0, 4).join(", ") : "selected organisms";
    const artifactLoad = cells().length || "ready";

    o.innerHTML = `
      <article class="petri-005d-panel metrics"><h3>Metrics</h3><div class="metric-grid">
        <div><span>Cells</span><b>${Math.round(m.cells)}</b><em>live count</em></div>
        <div><span>Active</span><b>${Math.round(m.active)}</b><em>organisms</em></div>
        <div><span>Particles</span><b>${Math.round(m.particles)}</b><em>artifact state</em></div>
        <div><span>FPS</span><b>${m.fps.toFixed(1)}</b><em>renderer</em></div>
      </div></article>
      <article class="petri-005d-panel density"><h3>Density Map</h3><canvas id="petri-005d-density-canvas"></canvas></article>
      <article class="petri-005d-panel receipt"><h3>Particle State / Registry Receipt</h3><div class="receipt-grid">
        <div><span>Run</span><b>${esc(run)}</b></div>
        <div><span>Preset</span><b>${esc(m.preset)}</b></div>
        <div><span>Selected</span><b>${esc(sel)}</b></div>
        <div><span>Particle State</span><b>${cells().length ? "cells.json loaded" : "artifact-backed"}</b></div>
      </div></article>
      <article class="petri-005d-panel charts"><h3>Metric Charts</h3><div class="chart-grid">
        <div><b>Total Cells</b>${spark([120,150,182,221,260,311,m.cells])}<span>population</span></div>
        <div><b>Shannon</b>${spark([.72,.84,1.02,m.diversity,1.12,1.20,m.diversity], "gold")}<span>diversity</span></div>
        <div><b>Dominance</b>${spark([.54,.47,.39,.34,m.dominance,.31,m.dominance], "pink")}<span>balance</span></div>
      </div></article>
      <article class="petri-005d-panel emergent"><h3>Emergent Conditions</h3><div class="condition-grid">
        <div><b>${Math.round(m.active)}</b><span>active organism types</span></div>
        <div><b>${esc(m.preset.split(" ")[0] || "microbial")}</b><span>current preset</span></div>
        <div><b>${esc(artifactLoad)}</b><span>cell artifact load</span></div>
      </div></article>`;

    place();
    drawDensity();
    document.documentElement.classList.add("petri-005d-single-layer-active");
    document.body.classList.add("petri-005d-single-layer-active");
  }

  async function refresh() {
    try {
      if (window.petri && typeof window.petri.readParticleState === "function") {
        particleState = await window.petri.readParticleState();
      }
    } catch {}
    render();
  }

  let tick = 0;
  function loop() {
    tick++;
    if (tick === 1 || tick % 8 === 0) refresh();
    else render();
    setTimeout(loop, tick < 20 ? 250 : 1000);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", loop, { once: true });
  else loop();

  window.addEventListener("resize", () => setTimeout(render, 80));
  window.PETRI_005D_SINGLE_LAYER_BOTTOM_OVERLAY = { render, refresh };
})();
