(() => {
  const VERSION = "v0.3.8";
  const STATE_KEY = "__gitnexusScopeHygieneV038";

  const state = window[STATE_KEY] || (window[STATE_KEY] = {
    categoryPassDone: false,
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
    /nexus_gitnexus_(core_hud|geometric_mini|exact_mini_mirror)\.v0\.(1|2|3\.[0-6])/i,
    /nexus_conversation_output_bridge\.v0\.2\.1[a-e]\.js/i,
    /tests[\\\/]test_nexus_conversation_output_bridge_v021[a-e]\.py/i,
    /tests[\\\/]test_gitnexus/i,
    /electron[\\\/]renderer[\\\/]nexus_gitnexus_/i,
    /electron[\\\/]renderer[\\\/]nexus_conversation_output_bridge/i
  ];

  const CATEGORY_OFF = [
    /State\s*\/\s*Reports/i,
    /Tests/i,
    /Docs/i,
    /Electron\s*\/\s*UI/i
  ];

  function q(sel, root = document) { return root.querySelector(sel); }
  function qa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  function textOf(node) {
    return String(node && node.textContent || "").replace(/\s+/g, " ").trim();
  }

  function shouldHideText(text) {
    return DENY_TEXT.some((rx) => rx.test(text));
  }

  function addScopePill() {
    const big = document.getElementById("gitnexus-big-hud") ||
      q("[data-gitnexus-big-hud]") ||
      q(".gitnexus-big-hud");

    if (!big) return;

    if (q(".gitnexus-scope-hygiene-pill", big)) return;

    const pill = document.createElement("div");
    pill.className = "gitnexus-scope-hygiene-pill";
    pill.textContent = "CORE SCOPE";
    pill.title = "Generated artifacts hidden: reports/state/ledger/tests/backups/old renderer/self graph noise.";

    const top =
      q(".gitnexus-topbar", big) ||
      q(".gitnexus-header", big) ||
      q("header", big) ||
      big.firstElementChild;

    if (top) top.appendChild(pill);
  }

  function hideNoisyRows() {
    const roots = [
      document.getElementById("gitnexus-big-hud"),
      q("[data-gitnexus-big-hud]"),
      q(".gitnexus-big-hud")
    ].filter(Boolean);

    roots.forEach((root) => {
      qa("li, tr, .gitnexus-row, .gitnexus-list-row, .gitnexus-file-row, .gitnexus-symbol-row, .gitnexus-node-row, [data-node-id], [data-file-path]", root).forEach((node) => {
        const txt = textOf(node);
        if (!txt) return;

        if (shouldHideText(txt)) {
          node.classList.add("gitnexus-scope-hidden");
          node.setAttribute("data-gitnexus-scope-hidden", "true");
        }
      });

      qa("span, div, label", root).forEach((node) => {
        if (node.children.length > 0) return;
        const txt = textOf(node);
        if (!txt || txt.length > 180) return;

        if (shouldHideText(txt)) {
          const row = node.closest("li, tr, .gitnexus-row, .gitnexus-list-row, .gitnexus-file-row, .gitnexus-symbol-row, .gitnexus-node-row, [data-node-id], [data-file-path]");
          if (row) {
            row.classList.add("gitnexus-scope-hidden");
            row.setAttribute("data-gitnexus-scope-hidden", "true");
          }
        }
      });
    });
  }

  function clickOffNoisyCategories() {
    if (state.categoryPassDone) return;

    const big = document.getElementById("gitnexus-big-hud") ||
      q("[data-gitnexus-big-hud]") ||
      q(".gitnexus-big-hud");

    if (!big) return;

    let changed = false;
    qa("button, [role='button'], .gitnexus-filter, .gitnexus-category, .gitnexus-toggle, .gitnexus-list-row", big).forEach((node) => {
      const txt = textOf(node);
      if (!txt) return;

      const isNoisyCategory = CATEGORY_OFF.some((rx) => rx.test(txt));
      if (!isNoisyCategory) return;

      const looksOn = /tracked|on|enabled|active/i.test(txt) || node.className.toString().match(/active|on|tracked/i);
      const looksOff = /off|hidden|disabled|untracked/i.test(txt) || node.className.toString().match(/off|disabled|hidden/i);

      if (looksOn && !looksOff) {
        try {
          node.click();
          changed = true;
        } catch (_) {}
      }
    });

    state.categoryPassDone = true;

    if (changed) {
      setTimeout(() => {
        hideNoisyRows();
        addScopePill();
        const fit = q("[data-gn-fit], [data-gitnexus-fit], button[title*='fit' i]", big);
        if (fit) {
          try { fit.click(); } catch (_) {}
        }
      }, 180);
    }
  }

  function sanitizeToolbarLabels() {
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

  function boot() {
    sanitizeToolbarLabels();
    clickOffNoisyCategories();
    hideNoisyRows();
    addScopePill();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener("load", boot);
  window.addEventListener("gitnexus:open-big-hud", () => setTimeout(boot, 120));
  window.addEventListener("gitnexus:scope-hygiene", boot);
  window.gitnexusScopeHygiene = boot;

  if (!state.timer) {
    state.timer = window.setInterval(boot, 2500);
  }
})();