(() => {
  const VERSION = "v0.3.9";
  const STATE_KEY = "__gitnexusScopeSwitchV039";

  const state = window[STATE_KEY] || (window[STATE_KEY] = {
    mode: "all",
    timer: 0
  });

  const DENY_TEXT = [
    /(^|[\\\/])reports([\\\/]|$)/i,
    /(^|[\\\/])state([\\\/]|$)/i,
    /(^|[\\\/])ledger([\\\/]|$)/i,
    /(^|[\\\/])electron[\\\/]reports([\\\/]|$)/i,
    /compact_compile_logs/i,
    /nexus_compile_report_\d+\.json/i,
    /nexus_self_healing_report_\d+\.json/i,
    /_latest\.json/i,
    /\.jsonl\b/i,
    /\.bak/i,
    /Tesseract Neural Network[\\\/](memory|state)/i,
    /GITNEXUS[\\\/](reports|state|ledger)/i,
    /nexus_gitnexus_(core_hud|geometric_mini|exact_mini_mirror|scope_hygiene|scope_switch)\.v0\.(1|2|3\.[0-8])/i,
    /nexus_conversation_output_bridge\.v0\.2\.1[a-e]\.js/i,
    /tests[\\\/]test_nexus_conversation_output_bridge_v021[a-e]\.py/i
  ];

  function q(sel, root = document) { return root.querySelector(sel); }
  function qa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  function textOf(node) {
    return String(node && node.textContent || "").replace(/\s+/g, " ").trim();
  }

  function shouldCoreHide(text) {
    return DENY_TEXT.some((rx) => rx.test(text));
  }

  function getBigHud() {
    return document.getElementById("gitnexus-big-hud") ||
      q("[data-gitnexus-big-hud]") ||
      q(".gitnexus-big-hud");
  }

  function removeOldLockoutState() {
    document.documentElement.removeAttribute("data-gitnexus-scope-locked");
    document.body?.removeAttribute("data-gitnexus-scope-locked");

    qa(".gitnexus-scope-hidden, [data-gitnexus-scope-hidden='true']").forEach((node) => {
      node.classList.remove("gitnexus-scope-hidden");
      node.removeAttribute("data-gitnexus-scope-hidden");
      node.removeAttribute("hidden");
      if (node.style && node.style.display === "none") {
        node.style.display = "";
      }
    });
  }

  function setMode(mode) {
    state.mode = mode === "core" ? "core" : "all";
    document.documentElement.dataset.gitnexusScopeMode = state.mode;
    if (document.body) document.body.dataset.gitnexusScopeMode = state.mode;
    applyMode();
  }

  function makeSwitch(root) {
    if (!root) return;
    let switcher = q(".gitnexus-scope-switch-v039", root);
    if (switcher) return switcher;

    switcher = document.createElement("div");
    switcher.className = "gitnexus-scope-switch-v039";
    switcher.innerHTML = `
      <span class="gitnexus-scope-label">SCOPE</span>
      <button type="button" data-gitnexus-scope-all>ALL</button>
      <button type="button" data-gitnexus-scope-core>CORE</button>
    `;

    const top =
      q(".gitnexus-topbar", root) ||
      q(".gitnexus-header", root) ||
      q("header", root) ||
      root.firstElementChild ||
      root;

    top.appendChild(switcher);

    q("[data-gitnexus-scope-all]", switcher)?.addEventListener("click", () => setMode("all"));
    q("[data-gitnexus-scope-core]", switcher)?.addEventListener("click", () => setMode("core"));

    return switcher;
  }

  function tagRows(root) {
    if (!root) return;

    qa("li, tr, .gitnexus-row, .gitnexus-list-row, .gitnexus-file-row, .gitnexus-symbol-row, .gitnexus-node-row, [data-node-id], [data-file-path]", root).forEach((node) => {
      const txt = textOf(node);
      if (!txt) return;

      if (shouldCoreHide(txt)) {
        node.setAttribute("data-gitnexus-core-hidden", "true");
      }
    });

    qa("span, div, label", root).forEach((node) => {
      if (node.children.length > 0) return;
      const txt = textOf(node);
      if (!txt || txt.length > 180) return;

      if (shouldCoreHide(txt)) {
        const row = node.closest("li, tr, .gitnexus-row, .gitnexus-list-row, .gitnexus-file-row, .gitnexus-symbol-row, .gitnexus-node-row, [data-node-id], [data-file-path]");
        if (row) row.setAttribute("data-gitnexus-core-hidden", "true");
      }
    });
  }

  function updateSwitch(root) {
    const switcher = q(".gitnexus-scope-switch-v039", root || document);
    if (!switcher) return;

    const all = q("[data-gitnexus-scope-all]", switcher);
    const core = q("[data-gitnexus-scope-core]", switcher);

    if (all) all.dataset.active = state.mode === "all" ? "true" : "false";
    if (core) core.dataset.active = state.mode === "core" ? "true" : "false";
  }

  function sanitizeToolbarLabels(root = document) {
    const fixes = [
      [/FIT/i, "FIT"],
      [/TURN|ROT/i, "TURN"],
      [/EDGE/i, "EDGES"],
      [/LABEL/i, "LABELS"],
      [/CLOSE/i, "CLOSE"],
      [/RISK/i, "RISK HIGH"],
      [/EVIDENCE/i, "EVIDENCE ONLY"]
    ];

    qa("button, [role='button'], .gitnexus-control-btn, .gitnexus-pill").forEach((node) => {
      const raw = textOf(node);
      if (!raw) return;
      const ascii = raw.replace(/[^\x20-\x7E]/g, "").trim();
      if (ascii !== raw || /Ãƒ|Ã‚|ï¿½|Aï¿½/.test(raw)) {
        const hit = fixes.find(([rx]) => rx.test(raw) || rx.test(ascii));
        if (hit) node.textContent = hit[1];
      }
    });
  }

  function applyMode() {
    const big = getBigHud();
    removeOldLockoutState();
    sanitizeToolbarLabels();

    if (big) {
      makeSwitch(big);
      tagRows(big);
      updateSwitch(big);
    }

    document.documentElement.dataset.gitnexusScopeMode = state.mode;
    if (document.body) document.body.dataset.gitnexusScopeMode = state.mode;
  }

  function boot() {
    // Default is ALL. No lockout.
    if (!state.mode) state.mode = "all";
    applyMode();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener("load", boot);
  window.addEventListener("gitnexus:open-big-hud", () => setTimeout(boot, 100));
  window.gitnexusScopeAll = () => setMode("all");
  window.gitnexusScopeCore = () => setMode("core");
  window.gitnexusScopeSwitch = boot;

  if (!state.timer) {
    state.timer = window.setInterval(boot, 2500);
  }
})();