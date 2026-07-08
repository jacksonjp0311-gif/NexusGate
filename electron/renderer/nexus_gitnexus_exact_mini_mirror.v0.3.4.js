(() => {
  const VERSION = "v0.3.4";
  const BIG_HUD_ID_CANDIDATES = ["gitnexus-big-hud", "gitnexus-interactive-hud", "gitnexus-hud"];
  const MINI_DOCK_ID = "gitnexus-core-left-dock";
  const ASCII_FIXES = [
    ["FIT", "FIT"],
    ["TURN", "TURN"],
    ["EDGES", "EDGES"],
    ["LABELS", "LABELS"],
    ["CLOSE", "CLOSE"],
    ["RISK HIGH", "RISK HIGH"],
    ["EVIDENCE ONLY", "EVIDENCE ONLY"],
    ["ROT -", "ROT -"],
    ["ROT +", "ROT +"]
  ];

  function q(sel, root = document) { return root.querySelector(sel); }
  function qa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  function hasNonAscii(text) {
    return /[^\x00-\x7F]/.test(String(text || ""));
  }

  function normalizeTextNode(node) {
    if (!node) return;
    const raw = String(node.textContent || "").trim();

    if (!raw) return;
    if (hasNonAscii(raw) || /Aï¿½|Ã‚|Ãƒ|Ã„|Ã…|Ã†|Ã‡|Ã|Ã‘|Ã˜|Ã™|Ãš|Ã›|Ãœ|Ã|Ãž|ÃŸ|ï¿½/.test(raw)) {
      const up = raw.toUpperCase();
      if (up.includes("TURN")) node.textContent = "TURN";
      else if (up.includes("EDGE")) node.textContent = "EDGES";
      else if (up.includes("LABEL")) node.textContent = "LABELS";
      else if (up.includes("FIT")) node.textContent = "FIT";
      else if (up.includes("CLOSE")) node.textContent = "CLOSE";
      else if (up.includes("RISK")) node.textContent = "RISK HIGH";
      else if (up.includes("EVIDENCE")) node.textContent = "EVIDENCE ONLY";
      else node.textContent = raw.replace(/[^\x20-\x7E]/g, "").trim() || "TURN";
    }
  }

  function sanitizeToolbar(root = document) {
    const selectors = [
      "button", "[role='button']", ".gitnexus-mini-pill",
      ".gitnexus-toolbar button", ".gitnexus-topbar button",
      "[data-gn-rotate-left]", "[data-gn-rotate-right]"
    ];
    selectors.forEach((sel) => qa(sel, root).forEach(normalizeTextNode));

    qa("*", root).forEach((node) => {
      const txt = String(node.textContent || "").trim();
      if (!txt) return;
      if (txt.length > 32) return;
      if (hasNonAscii(txt)) normalizeTextNode(node);
    });
  }

  function getBigHud() {
    for (const id of BIG_HUD_ID_CANDIDATES) {
      const node = document.getElementById(id);
      if (node) return node;
    }
    return q("[data-gitnexus-big-hud]") || q(".gitnexus-big-hud");
  }

  function ensureBigHudReady() {
    let hud = getBigHud();
    if (hud) return hud;

    const openers = [
      "[data-gn-open-big-hud]",
      "[data-gn-open-big]",
      "[data-gn-open-hud]",
      "[data-gitnexus-open-big]",
      "#gitnexus-open-big-hud"
    ];

    for (const sel of openers) {
      const node = q(sel);
      if (node) {
        try { node.click(); } catch (_) {}
      }
    }

    window.dispatchEvent(new CustomEvent("gitnexus:open-big-hud"));
    return getBigHud();
  }

  function makeMiniWrapper(dock) {
    let shell = q(".gitnexus-exact-mini-shell", dock);
    if (shell) return shell;

    dock.innerHTML = `
      <div class="gitnexus-exact-mini-shell" data-gitnexus-mini-version="${VERSION}">
        <div class="gitnexus-exact-mini-frame">
          <div class="gitnexus-exact-mini-scale-wrap">
            <div class="gitnexus-exact-mini-clone"></div>
          </div>
        </div>
        <button type="button" class="gitnexus-exact-mini-open" data-gitnexus-open-full-exact>
          OPEN GITNEXUS HUD
        </button>
      </div>
    `;

    shell = q(".gitnexus-exact-mini-shell", dock);
    const openBtn = q("[data-gitnexus-open-full-exact]", shell);
    if (openBtn) {
      openBtn.addEventListener("click", () => {
        const hud = ensureBigHudReady();
        if (hud) {
          hud.classList.remove("is-hidden");
          hud.style.display = "grid";
          hud.style.visibility = "visible";
          hud.style.opacity = "1";
        }
      });
    }

    return shell;
  }

  function removeInteractiveNoise(root) {
    [
      ".gitnexus-close", "[data-gn-close]", "[data-gitnexus-close]",
      "#gitnexus-close", ".gitnexus-debug", "[data-gitnexus-debug]"
    ].forEach((sel) => qa(sel, root).forEach((n) => n.remove()));

    qa("script", root).forEach((n) => n.remove());

    const openers = qa("button, [role='button']", root).filter((n) =>
      /open gitnexus hud/i.test(String(n.textContent || ""))
    );
    if (openers.length > 1) {
      openers.slice(1).forEach((n) => n.remove());
    }
  }

  function scaleCloneToFit(cloneTarget, shell) {
    const scaleWrap = q(".gitnexus-exact-mini-scale-wrap", shell);
    const frame = q(".gitnexus-exact-mini-frame", shell);
    if (!scaleWrap || !frame || !cloneTarget) return;

    const baseW = 1720;
    const baseH = 900;
    const availableW = Math.max(320, frame.clientWidth - 2);
    const availableH = Math.max(180, frame.clientHeight - 2);
    const scale = Math.max(0.16, Math.min(0.42, Math.min(availableW / baseW, availableH / baseH)));

    cloneTarget.style.width = baseW + "px";
    cloneTarget.style.height = baseH + "px";
    cloneTarget.style.transform = `scale(${scale})`;
    cloneTarget.style.transformOrigin = "top left";

    scaleWrap.style.width = (baseW * scale) + "px";
    scaleWrap.style.height = (baseH * scale) + "px";
  }

  function mirrorBigHudIntoMini() {
    const dock = document.getElementById(MINI_DOCK_ID);
    if (!dock) return;

    const shell = makeMiniWrapper(dock);
    const frame = q(".gitnexus-exact-mini-frame", shell);
    const cloneRoot = q(".gitnexus-exact-mini-clone", shell);
    if (!frame || !cloneRoot) return;

    const big = ensureBigHudReady();
    if (!big) return;

    sanitizeToolbar(document);

    const clone = big.cloneNode(true);
    clone.removeAttribute("id");
    clone.classList.add("gitnexus-exact-mini-cloned-hud");

    removeInteractiveNoise(clone);
    sanitizeToolbar(clone);

    cloneRoot.innerHTML = "";
    cloneRoot.appendChild(clone);
    scaleCloneToFit(cloneRoot, shell);
  }

  function hookRotateShortcuts() {
    if (window.__gitnexusRotateShortcutsBound) return;
    window.__gitnexusRotateShortcutsBound = true;

    document.addEventListener("keydown", (ev) => {
      if (ev.key === "[" || ev.key === "{") {
        const btn = q("[data-gn-rotate-left]");
        if (btn) { ev.preventDefault(); btn.click(); }
      }
      if (ev.key === "]" || ev.key === "}") {
        const btn = q("[data-gn-rotate-right]");
        if (btn) { ev.preventDefault(); btn.click(); }
      }
    });

    document.addEventListener("wheel", (ev) => {
      if (!ev.shiftKey) return;
      const btn = ev.deltaY > 0 ? q("[data-gn-rotate-right]") : q("[data-gn-rotate-left]");
      if (btn) {
        ev.preventDefault();
        btn.click();
      }
    }, { passive: false });
  }

  function boot() {
    sanitizeToolbar(document);
    hookRotateShortcuts();
    mirrorBigHudIntoMini();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener("load", boot);
  window.addEventListener("resize", boot);
  window.setInterval(boot, 2200);
})();