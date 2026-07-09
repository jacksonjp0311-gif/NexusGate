(() => {
  "use strict";

  const SEAL = "PETRI_005G_SAFE_BOTTOM_FILL_OVERRIDE";

  function visible(el) {
    if (!el || !el.getBoundingClientRect) return false;
    const r = el.getBoundingClientRect();
    return r.width > 80 && r.height > 50;
  }

  function upper(el) {
    return String(el?.innerText || el?.textContent || "").replace(/\s+/g, " ").trim().toUpperCase();
  }

  function overlay() {
    return document.getElementById("petri-005d-bottom-overlay");
  }

  function microscopeBottom() {
    const o = overlay();
    const viewport = window.innerHeight || document.documentElement.clientHeight || 900;
    const width = window.innerWidth || document.documentElement.clientWidth || 1600;
    let bottom = 92;

    const candidates = Array.from(document.querySelectorAll(
      "section,main,article,aside,.panel,[class*='panel'],[class*='stage'],[class*='microscope']"
    ));

    for (const el of candidates) {
      if (!visible(el)) continue;
      if (o && o.contains(el)) continue;
      if (el.id === "petri-bottom-dock" || el.id === "petri-005c-bottom-overlay") continue;
      if (el.classList.contains("petri-005d-hard-hidden")) continue;

      const r = el.getBoundingClientRect();
      if (r.top > viewport * 0.80) continue;
      if (r.left < 250) continue;
      if (r.right > width - 250) continue;
      if (r.width < 520) continue;

      const t = upper(el).slice(0, 1200);
      const isMicroscope =
        t.includes("REGISTRY LOADED") ||
        t.includes("TOGGLE ORGANISM") ||
        t.includes("2 UM") ||
        t.includes("MAG") ||
        t.includes("LIVE SIM");

      if (isMicroscope) bottom = Math.max(bottom, r.bottom);
    }

    if (bottom < 180) bottom = Math.floor(viewport * 0.70);
    return Math.min(bottom, viewport - 168);
  }

  function fillBottom() {
    const o = overlay();
    if (!o) return;

    const viewport = window.innerHeight || document.documentElement.clientHeight || 900;
    const top = Math.max(80, Math.min(microscopeBottom() + 8, viewport - 168));

    o.dataset.seal005g = SEAL;
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

    o.querySelectorAll(".petri-005d-panel").forEach(panel => {
      panel.style.setProperty("height", "100%", "important");
      panel.style.setProperty("min-height", "0", "important");
      panel.style.setProperty("overflow", "hidden", "important");
    });

    o.querySelectorAll(".metric-grid,.receipt-grid,.chart-grid,.condition-grid,#petri-005d-density-canvas").forEach(child => {
      child.style.setProperty("height", "calc(100% - 22px)", "important");
      child.style.setProperty("max-height", "none", "important");
      child.style.setProperty("overflow", "hidden", "important");
    });

    ["petri-bottom-dock", "petri-005c-bottom-overlay"].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.style.setProperty("display", "none", "important");
        el.style.setProperty("visibility", "hidden", "important");
        el.style.setProperty("opacity", "0", "important");
        el.style.setProperty("pointer-events", "none", "important");
      }
    });

    document.documentElement.classList.add("petri-005g-bottom-fill-active");
    document.body.classList.add("petri-005g-bottom-fill-active");
  }

  let ticks = 0;
  function loop() {
    ticks += 1;
    fillBottom();
    window.setTimeout(loop, ticks < 30 ? 150 : 600);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loop, { once: true });
  } else {
    loop();
  }

  window.addEventListener("resize", () => window.setTimeout(fillBottom, 80));
  window.PETRI_005G_SAFE_BOTTOM_FILL_OVERRIDE = { fillBottom };
})();
