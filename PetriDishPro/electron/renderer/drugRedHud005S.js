(() => {
  "use strict";

  const SEAL = "PETRI_005S_DRUG_RED_HUD";

  function upper(value) {
    return String(value || "").replace(/\s+/g, " ").trim().toUpperCase();
  }

  function isDrugPanel(el) {
    if (!el || !(el instanceof HTMLElement)) return false;
    const text = upper(el.textContent || "");
    if (!text.includes("DRUG")) return false;
    if (!(text.includes("LAB") || text.includes("INJECTION") || text.includes("DOSE") || text.includes("TARGET") || text.includes("LIBRARY"))) return false;
    const area = el.getBoundingClientRect();
    return area.width > 260 && area.height > 180;
  }

  function candidatePanels() {
    const pool = Array.from(document.querySelectorAll("[id*='drug'], [class*='drug'], [id*='Drug'], [class*='Drug'], [id*='injection'], [class*='injection'], [id*='hud'], [class*='hud']"));
    return pool.filter(isDrugPanel);
  }

  function makeDraggable(panel) {
    if (!panel || panel.dataset.dragSeal005s === SEAL) return;
    const handle = panel.querySelector(".petri-005s-drug-hud-title") || panel.firstElementChild || panel;
    let dragging = false;
    let startX = 0;
    let startY = 0;
    let baseLeft = 0;
    let baseTop = 0;

    handle.style.cursor = "move";

    const down = (ev) => {
      dragging = true;
      const rect = panel.getBoundingClientRect();
      baseLeft = rect.left;
      baseTop = rect.top;
      startX = ev.clientX;
      startY = ev.clientY;
      panel.style.left = rect.left + "px";
      panel.style.top = rect.top + "px";
      panel.style.right = "auto";
      panel.style.bottom = "auto";
      panel.style.position = "fixed";
      panel.style.margin = "0";
      ev.preventDefault();
    };

    const move = (ev) => {
      if (!dragging) return;
      const dx = ev.clientX - startX;
      const dy = ev.clientY - startY;
      panel.style.left = Math.max(12, baseLeft + dx) + "px";
      panel.style.top = Math.max(80, baseTop + dy) + "px";
    };

    const up = () => {
      dragging = false;
    };

    handle.addEventListener("pointerdown", down);
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    panel.dataset.dragSeal005s = SEAL;
  }

  function repairDrugHud() {
    const panels = candidatePanels();
    panels.forEach(panel => {
      panel.classList.add("petri-005s-drug-red-hud");
      panel.dataset.seal005s = SEAL;
      const title = panel.querySelector("h1, h2, h3, .title, .header, .hud-title, .panel-title") || panel.firstElementChild;
      if (title && !title.classList.contains("petri-005s-drug-hud-title")) {
        title.classList.add("petri-005s-drug-hud-title");
      }
      makeDraggable(panel);
    });

    window.PETRI_005S_DRUG_HUD = {
      seal: SEAL,
      count: panels.length,
      claim_boundary: "Drug HUD is a UI layer only."
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", repairDrugHud, { once: true });
  } else {
    repairDrugHud();
  }

  let tick = 0;
  const timer = setInterval(() => {
    tick += 1;
    repairDrugHud();
    if (tick > 30) clearInterval(timer);
  }, 350);
})();
