(() => {
  "use strict";

  const SEAL = "PETRI_005P2_ASCII_SAFE_HUD_REPAIR";

  function byId(id) {
    return document.getElementById(id);
  }

  function textClean(value) {
    return String(value || "")
      .replace(/\u00c2\u00b5g\/mL/g, "ug/mL")
      .replace(/\u00b5g\/mL/g, "ug/mL")
      .replace(/\u2697/g, "")
      .replace(/\u00d7/g, "X")
      .replace(/[\u2013\u2014]/g, "-")
      .replace(/\u03b2/g, "beta")
      .replace(/\s+/g, " ")
      .trim();
  }

  function important(el, prop, value) {
    if (el) el.style.setProperty(prop, value, "important");
  }

  function sanitizeText(root) {
    const scope = root || document;
    const btn = byId("petri-005o-drug-button");
    if (btn) {
      btn.textContent = "Drug Lab";
      btn.title = "Open Drug Lab";
      btn.dataset.seal005p2 = SEAL;
    }

    scope.querySelectorAll("*").forEach(node => {
      if (!node.childElementCount && node.textContent) {
        const next = textClean(node.textContent);
        if (next && next !== node.textContent) node.textContent = next;
      }
    });
  }

  function clamp(n, lo, hi) {
    return Math.max(lo, Math.min(hi, n));
  }

  function applyHudLayer() {
    const hud = byId("petri-005o-drug-hud");
    if (!hud) return;

    hud.dataset.seal005p2 = SEAL;
    hud.classList.add("petri-005p2-hud-layer");

    const width = Math.min(980, Math.max(760, Math.round(window.innerWidth * 0.58)));
    const height = Math.min(780, Math.max(560, Math.round(window.innerHeight * 0.78)));

    if (!hud.dataset.userMoved005p2) {
      const left = clamp(Math.round((window.innerWidth - width) / 2), 24, Math.max(24, window.innerWidth - width - 24));
      important(hud, "left", `${left}px`);
      important(hud, "top", "74px");
    }

    important(hud, "right", "auto");
    important(hud, "bottom", "auto");
    important(hud, "width", `${width}px`);
    important(hud, "height", `${height}px`);
    important(hud, "min-width", "720px");
    important(hud, "max-width", "calc(100vw - 36px)");
    important(hud, "max-height", "calc(100vh - 96px)");
    important(hud, "z-index", "2147483000");
    important(hud, "pointer-events", hud.classList.contains("open") ? "auto" : "none");

    const shell = hud.querySelector(".petri-005o-hud-shell");
    if (shell) {
      important(shell, "height", "100%");
      important(shell, "max-height", "100%");
      important(shell, "overflow", "hidden");
    }
  }

  function addHudTools() {
    const hud = byId("petri-005o-drug-hud");
    if (!hud) return;

    const head = hud.querySelector(".petri-005o-hud-head");
    if (!head || head.dataset.seal005p2) return;
    head.dataset.seal005p2 = SEAL;
    head.classList.add("petri-005p2-drag-handle");
    head.title = "Drag to move the HUD";

    const tools = document.createElement("div");
    tools.className = "petri-005p2-hud-tools";
    tools.innerHTML = [
      '<button type="button" data-action="center">Center</button>',
      '<button type="button" data-action="right">Dock Right</button>',
      '<button type="button" data-action="wide">Wide</button>'
    ].join("");

    const close = hud.querySelector("#petri-005o-hud-close");
    if (close && close.parentElement) close.parentElement.insertBefore(tools, close);
    else head.appendChild(tools);

    tools.querySelectorAll("button").forEach(btn => {
      btn.addEventListener("click", ev => {
        ev.stopPropagation();
        const action = btn.getAttribute("data-action");
        if (action === "center") {
          delete hud.dataset.userMoved005p2;
          applyHudLayer();
        }
        if (action === "right") {
          hud.dataset.userMoved005p2 = "true";
          important(hud, "left", `${Math.max(24, window.innerWidth - hud.getBoundingClientRect().width - 24)}px`);
          important(hud, "top", "74px");
        }
        if (action === "wide") {
          hud.dataset.userMoved005p2 = "true";
          important(hud, "left", "28px");
          important(hud, "top", "74px");
          important(hud, "width", "calc(100vw - 56px)");
          important(hud, "height", "calc(100vh - 108px)");
        }
      });
    });
  }

  function enableDrag() {
    const hud = byId("petri-005o-drug-hud");
    if (!hud || hud.dataset.drag005p2) return;
    hud.dataset.drag005p2 = "true";

    let dragging = false;
    let dx = 0;
    let dy = 0;

    function start(ev) {
      const head = ev.target.closest && ev.target.closest(".petri-005o-hud-head");
      if (!head) return;
      if (ev.target.closest("button,input,select")) return;
      const rect = hud.getBoundingClientRect();
      dragging = true;
      dx = ev.clientX - rect.left;
      dy = ev.clientY - rect.top;
      hud.dataset.userMoved005p2 = "true";
      document.body.classList.add("petri-005p2-dragging");
      ev.preventDefault();
    }

    function move(ev) {
      if (!dragging) return;
      const rect = hud.getBoundingClientRect();
      const left = clamp(ev.clientX - dx, 8, window.innerWidth - Math.min(rect.width, window.innerWidth - 16) - 8);
      const top = clamp(ev.clientY - dy, 8, window.innerHeight - 80);
      important(hud, "left", `${Math.round(left)}px`);
      important(hud, "top", `${Math.round(top)}px`);
      important(hud, "right", "auto");
      important(hud, "bottom", "auto");
    }

    function end() {
      dragging = false;
      document.body.classList.remove("petri-005p2-dragging");
    }

    document.addEventListener("mousedown", start, true);
    document.addEventListener("mousemove", move, true);
    document.addEventListener("mouseup", end, true);
  }

  function fixRegistryPanel() {
    const host = byId("petri-005o-registry-host");
    if (!host) return;

    host.dataset.seal005p2 = SEAL;
    host.classList.add("petri-005p2-registry-stable");

    document.querySelectorAll(".petri-005o-soft-hidden").forEach(el => {
      important(el, "display", "none");
      important(el, "visibility", "hidden");
      important(el, "pointer-events", "none");
    });

    important(host, "position", "relative");
    important(host, "width", "calc(100% - 18px)");
    important(host, "box-sizing", "border-box");
    important(host, "margin", "8px");
    important(host, "max-height", "calc(100vh - 132px)");
    important(host, "overflow-y", "auto");
    important(host, "overflow-x", "hidden");
    important(host, "z-index", "2");

    host.querySelectorAll(".petri-005o-org-card").forEach(card => {
      card.classList.add("petri-005p2-default-collapsed");
    });
  }

  function hookOpenButton() {
    const btn = byId("petri-005o-drug-button");
    if (!btn || btn.dataset.seal005p2Click) return;
    btn.dataset.seal005p2Click = "true";
    btn.addEventListener("click", () => {
      window.setTimeout(() => {
        applyHudLayer();
        addHudTools();
        enableDrag();
        sanitizeText();
      }, 30);
    }, true);
  }

  function repair() {
    sanitizeText();
    applyHudLayer();
    addHudTools();
    enableDrag();
    fixRegistryPanel();
    hookOpenButton();

    const hud = byId("petri-005o-drug-hud");
    if (hud && !hud.__petri005p2Observer) {
      const obs = new MutationObserver(() => {
        sanitizeText(hud);
        applyHudLayer();
      });
      obs.observe(hud, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ["class", "style"] });
      hud.__petri005p2Observer = obs;
    }

    window.PETRI_005P2_HUD_REPAIR = {
      seal: SEAL,
      center: () => {
        const hud = byId("petri-005o-drug-hud");
        if (hud) {
          delete hud.dataset.userMoved005p2;
          applyHudLayer();
        }
      },
      applyHudLayer,
      fixRegistryPanel,
      claim_boundary: "UI repair only; no medical or wet-lab guidance."
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", repair, { once: true });
  } else {
    repair();
  }

  let ticks = 0;
  const timer = window.setInterval(() => {
    ticks += 1;
    repair();
    if (ticks > 30) window.clearInterval(timer);
  }, 350);

  window.addEventListener("resize", () => window.setTimeout(repair, 80));
})();
