(() => {
  "use strict";

  const SEAL = "PETRI_004Z_BOTTOM_DOCK_LAYOUT_SEAL";
  const PANEL_ORDER = [
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
    return r.width > 40 && r.height > 20;
  }

  function scorePanel(el, label) {
    const text = norm(el.textContent);
    const exactStart = text.startsWith(label) ? 0 : 2000;
    const lenPenalty = Math.min(text.length, 6000);
    const r = el.getBoundingClientRect ? el.getBoundingClientRect() : { width: 0, height: 0 };
    const area = Math.max(1, r.width * r.height);
    return exactStart + lenPenalty + Math.floor(area / 150);
  }

  function findPanel(label) {
    const selectors = [
      "section", "article", "aside",
      ".panel", ".card", ".hud-card", ".dashboard-card", ".metric-panel",
      "[class*='panel']", "[class*='card']", "[class*='metric']", "[class*='receipt']"
    ].join(",");
    const candidates = Array.from(document.querySelectorAll(selectors))
      .filter(el => !el.closest("#petri-bottom-dock"))
      .filter(visible)
      .filter(el => {
        const t = norm(el.textContent).slice(0, 900);
        return t.includes(label);
      })
      .sort((a, b) => scorePanel(a, label) - scorePanel(b, label));

    if (candidates.length) return candidates[0];

    const header = Array.from(document.querySelectorAll("h1,h2,h3,h4,h5,h6,.title,.panel-title,[class*='title'],[class*='header']"))
      .filter(visible)
      .find(el => norm(el.textContent).includes(label));

    if (!header) return null;
    let cur = header;
    for (let i = 0; i < 8 && cur && cur !== document.body; i += 1) {
      if (visible(cur) && norm(cur.textContent).includes(label)) {
        const r = cur.getBoundingClientRect();
        if (r.width > 120 && r.height > 40) return cur;
      }
      cur = cur.parentElement;
    }
    return header.parentElement || null;
  }

  function ensureDock() {
    let dock = document.getElementById("petri-bottom-dock");
    if (!dock) {
      dock = document.createElement("section");
      dock.id = "petri-bottom-dock";
      dock.setAttribute("aria-label", "Petri bottom dashboard");
      dock.dataset.seal = SEAL;
      document.body.appendChild(dock);
    }
    return dock;
  }

  function hideDuplicates(selectedPanels) {
    const selected = new Set(selectedPanels.filter(Boolean));
    PANEL_ORDER.forEach(item => {
      const label = item.label;
      const selectors = [
        "section", "article", "aside", ".panel", ".card", ".hud-card",
        "[class*='panel']", "[class*='card']"
      ].join(",");
      Array.from(document.querySelectorAll(selectors)).forEach(el => {
        if (selected.has(el)) return;
        if (el.closest("#petri-bottom-dock")) return;
        const t = norm(el.textContent).slice(0, 500);
        if (t.includes(label)) {
          el.classList.add("petri-004z-duplicate-hidden");
        }
      });
    });
  }

  function cleanPanel(panel, item) {
    if (!panel) return;
    panel.classList.add("petri-dock-panel", item.cls);
    panel.style.minWidth = "0";
    panel.style.minHeight = "0";
    panel.removeAttribute("style");
    panel.classList.add("petri-dock-panel", item.cls);
    const headers = Array.from(panel.querySelectorAll("h1,h2,h3,h4,h5,h6,.title,.panel-title,[class*='title']"));
    headers.slice(1).forEach(h => {
      if (norm(h.textContent) === item.label) h.classList.add("petri-004z-repeated-title");
    });
  }

  function extractJsonFromReceipt(panel) {
    if (!panel) return null;
    const rawTarget = panel.querySelector("pre, code, textarea");
    const raw = rawTarget ? rawTarget.textContent : panel.textContent;
    const first = raw.indexOf("{");
    const last = raw.lastIndexOf("}");
    if (first < 0 || last <= first) return null;
    try {
      return JSON.parse(raw.slice(first, last + 1));
    } catch {
      return null;
    }
  }

  function humanizeReceipt(panel) {
    if (!panel || panel.dataset.petri004zHumanized === "true") return;
    const data = extractJsonFromReceipt(panel);
    if (!data) return;

    const selected = Array.isArray(data.selected) ? data.selected
      : Array.isArray(data.selected_organisms) ? data.selected_organisms
      : [];
    const paths = [
      data.cells_path || data.cells,
      data.particles_path || data.particles,
      data.interactions_path || data.interactions,
      data.fields_path || data.fields
    ].filter(Boolean);

    const body = document.createElement("div");
    body.className = "petri-receipt-readable";
    body.innerHTML = `
      <div class="petri-receipt-row"><span>Run</span><b>${escapeHtml(data.run_id || data.run || "latest")}</b></div>
      <div class="petri-receipt-row"><span>Preset</span><b>${escapeHtml(data.preset || data.name || "Microbial Competition")}</b></div>
      <div class="petri-receipt-row"><span>Selected</span><b>${selected.length || data.selected_count || "n/a"} organism cards</b></div>
      <div class="petri-receipt-row"><span>Artifacts</span><b>${paths.length || "registry"} linked files</b></div>
      <div class="petri-receipt-row wide"><span>Gate</span><b>source-gated simulation proxy</b></div>
    `;

    const header = Array.from(panel.children).find(el => norm(el.textContent).includes("PARTICLE STATE") || norm(el.textContent).includes("REGISTRY RECEIPT"));
    panel.querySelectorAll("pre, code, textarea").forEach(el => el.remove());
    if (header) {
      while (header.nextSibling) header.nextSibling.remove();
      header.insertAdjacentElement("afterend", body);
    } else {
      panel.appendChild(body);
    }
    panel.dataset.petri004zHumanized = "true";
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    }[ch]));
  }

  function layout() {
    const dock = ensureDock();
    const panels = PANEL_ORDER.map(item => {
      const existing = dock.querySelector("." + item.cls);
      const panel = existing || findPanel(item.label);
      if (!panel) return null;
      cleanPanel(panel, item);
      if (panel.parentElement !== dock) dock.appendChild(panel);
      if (item.cls === "petri-panel-receipt") humanizeReceipt(panel);
      return panel;
    }).filter(Boolean);

    hideDuplicates(panels);
    document.documentElement.classList.add("petri-004z-bottom-dock-active");
    document.body.classList.add("petri-004z-bottom-dock-active");
  }

  let attempts = 0;
  function schedule() {
    attempts += 1;
    layout();
    if (attempts < 12) window.setTimeout(schedule, 350);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", schedule, { once: true });
  } else {
    schedule();
  }

  window.addEventListener("resize", () => window.setTimeout(layout, 80));
  window.PETRI_004Z_BOTTOM_DOCK_LAYOUT_SEAL = { layout };
})();
