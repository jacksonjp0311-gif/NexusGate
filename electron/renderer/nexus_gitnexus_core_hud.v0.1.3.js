(() => {
  const VERSION = "v0.1.3";
  const REPORT_PATHS = [
    "../../reports/gitnexus_report_latest.json",
    "../../state/gitnexus/gitnexus_graph_latest.json",
    "../../GITNEXUS/reports/gitnexus_report_latest.json"
  ];

  function make(tag, cls) {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    return el;
  }

  function text(value, fallback = "--") {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  function escapeXml(value) {
    return String(value ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  async function loadReport() {
    for (const path of REPORT_PATHS) {
      try {
        const response = await fetch(path + "?t=" + Date.now());
        if (response.ok) return await response.json();
      } catch (_) {}
    }
    return null;
  }

  function rectOk(rect) {
    return rect && rect.width > 180 && rect.height > 80;
  }

  function findLeftRail() {
    const direct = [".left-stack", ".left-panel", "#left-stack", "#left-panel"]
      .map((selector) => document.querySelector(selector))
      .find(Boolean);

    if (direct && rectOk(direct.getBoundingClientRect())) return direct;

    const nodes = Array.from(document.querySelectorAll("aside, section, article, div"));
    const scored = nodes
      .map((node) => ({ node, rect: node.getBoundingClientRect(), text: (node.textContent || "").toUpperCase() }))
      .filter((item) =>
        item.rect.left >= -4 &&
        item.rect.left < 80 &&
        item.rect.width >= 230 &&
        item.rect.width <= 390 &&
        item.text.includes("PROCESS LANES")
      )
      .sort((a, b) => (b.rect.height * b.rect.width) - (a.rect.height * a.rect.width));

    return scored[0]?.node || null;
  }

  function findNeuralActivityRect(leftRail) {
    const leftRect = leftRail?.getBoundingClientRect?.();

    const candidates = Array.from(document.querySelectorAll("section, article, div"))
      .map((node) => ({ node, rect: node.getBoundingClientRect(), text: (node.textContent || "").toUpperCase() }))
      .filter((item) => {
        if (!item.text.includes("NEURAL ACTIVITY")) return false;
        if (!rectOk(item.rect)) return false;
        if (leftRect && Math.abs(item.rect.left - leftRect.left) > 28) return false;
        return item.rect.width <= 420;
      })
      .sort((a, b) => {
        const aScore = (a.rect.width * a.rect.height) - Math.abs(a.rect.width - 300) * 20;
        const bScore = (b.rect.width * b.rect.height) - Math.abs(b.rect.width - 300) * 20;
        return bScore - aScore;
      });

    return candidates[0]?.rect || null;
  }

  function findFooterTop() {
    const nodes = Array.from(document.querySelectorAll("footer, section, div"));
    const hit = nodes
      .map((node) => ({ node, rect: node.getBoundingClientRect(), text: (node.textContent || "").toUpperCase() }))
      .filter((item) => item.text.includes("GOVERNANCE") && item.text.includes("SYSTEM BUS"))
      .sort((a, b) => b.rect.top - a.rect.top)[0];

    if (hit && hit.rect.top > window.innerHeight * 0.65) return hit.rect.top;
    return window.innerHeight - 52;
  }

  function dockGeometry() {
    const leftRail = findLeftRail();
    const leftRect = leftRail?.getBoundingClientRect?.();
    const neuralRect = leftRail ? findNeuralActivityRect(leftRail) : null;

    const left = leftRect ? Math.max(6, leftRect.left + 6) : 6;
    const width = leftRect ? Math.max(240, Math.min(340, leftRect.width - 12)) : 300;

    const topFromNeural = neuralRect ? neuralRect.bottom + 10 : Math.round(window.innerHeight * 0.60);
    const footerTop = findFooterTop();
    const top = Math.max(120, Math.min(topFromNeural, footerTop - 150));
    const height = Math.max(118, footerTop - top - 10);

    return { left, top, width, height };
  }

  function positionDock(dock) {
    const g = dockGeometry();
    dock.style.left = g.left + "px";
    dock.style.top = g.top + "px";
    dock.style.width = g.width + "px";
    dock.style.maxHeight = g.height + "px";
  }

  function setMini(station, data) {
    const files = station.querySelector("[data-gitnexus-files]");
    const symbols = station.querySelector("[data-gitnexus-symbols]");
    const edges = station.querySelector("[data-gitnexus-edges]");
    const risk = station.querySelector("[data-gitnexus-risk]");
    if (files) files.textContent = text(data?.counts?.files);
    if (symbols) symbols.textContent = text(data?.counts?.symbols);
    if (edges) edges.textContent = text(data?.counts?.edges);
    if (risk) risk.textContent = text(data?.impact?.risk, "scan");
  }

  function rows(items, countKey) {
    if (!Array.isArray(items) || items.length === 0) {
      return '<div class="gitnexus-list-row"><em>--</em><span>No entries yet. Run scripts/nexus_gitnexus.ps1 scan.</span><b>--</b></div>';
    }
    return items.slice(0, 18).map((item, index) => {
      const name = item.file || item.path || String(item);
      const count = item[countKey] ?? item.importer_count ?? "";
      return '<div class="gitnexus-list-row"><em>' + String(index + 1).padStart(2, "0") + '</em><span title="' + escapeXml(name) + '">' + escapeXml(name) + '</span><b>' + escapeXml(count) + '</b></div>';
    }).join("");
  }

  function buildGraphSvg(data) {
    const top = Array.isArray(data?.top_imported_files) ? data.top_imported_files.slice(0, 8) : [];
    const affected = Array.isArray(data?.impact?.affected_files) ? data.impact.affected_files.slice(0, 4) : [];
    const nodes = [
      { id: "core", label: "GITNEXUS", x: 50, y: 50, hot: true },
      ...top.map((item, i) => {
        const angle = (Math.PI * 2 * i) / Math.max(top.length, 1) - Math.PI / 2;
        return { id: "t" + i, label: (item.file || "").split("/").slice(-2).join("/"), x: 50 + Math.cos(angle) * 32, y: 50 + Math.sin(angle) * 29, hot: false };
      }),
      ...affected.map((item, i) => {
        const angle = (Math.PI * 2 * i) / Math.max(affected.length, 1) + Math.PI / 4;
        return { id: "a" + i, label: String(item).split("/").slice(-2).join("/"), x: 50 + Math.cos(angle) * 42, y: 50 + Math.sin(angle) * 38, hot: true };
      })
    ];

    const edges = nodes.filter((n) => n.id !== "core").map((n) =>
      '<path class="gitnexus-edge" d="M50 50 C ' + ((50 + n.x) / 2).toFixed(1) + ' ' + (n.y < 50 ? 30 : 70) + ', ' + ((50 + n.x) / 2).toFixed(1) + ' ' + n.y.toFixed(1) + ', ' + n.x.toFixed(1) + ' ' + n.y.toFixed(1) + '" />'
    ).join("");

    const nodeSvg = nodes.map((n) => {
      const label = escapeXml(n.label.length > 24 ? n.label.slice(0, 23) + "…" : n.label);
      return '<g><circle class="' + (n.hot ? "gitnexus-node gitnexus-node-hot" : "gitnexus-node") + '" cx="' + n.x.toFixed(1) + '" cy="' + n.y.toFixed(1) + '" r="' + (n.id === "core" ? 4.5 : 3.2) + '" /><text class="gitnexus-node-label" x="' + (n.x + 4).toFixed(1) + '" y="' + (n.y + 1).toFixed(1) + '">' + label + '</text></g>';
    }).join("");

    return '<svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">' + edges + nodeSvg + '</svg>';
  }

  function ensureProgram() {
    let program = document.getElementById("gitnexus-core-program");
    if (program) return program;

    program = make("section", "gitnexus-core-program");
    program.id = "gitnexus-core-program";
    program.hidden = true;

    const head = make("div", "gitnexus-core-program-head");
    const title = make("strong");
    title.textContent = "GITNEXUS CODEGRAPH PROGRAM HUD";
    const status = make("span");
    status.textContent = "EVIDENCE ONLY";
    const close = make("button");
    close.type = "button";
    close.textContent = "Close";
    close.addEventListener("click", () => { program.hidden = true; });
    head.append(title, status, close);

    const body = make("div", "gitnexus-core-program-body");
    body.innerHTML =
      '<article class="gitnexus-panel gitnexus-graph-panel"><h2>Repo Graph</h2><div class="gitnexus-graph-canvas" data-gitnexus-graph></div></article>' +
      '<article class="gitnexus-panel"><h2>Codegraph Status</h2><div class="gitnexus-side-grid"><div class="gitnexus-kv"><span>Files</span><b data-program-files>--</b><span>Symbols</span><b data-program-symbols>--</b><span>Edges</span><b data-program-edges>--</b><span>Changed</span><b data-program-changed>--</b><span>Risk</span><b data-program-risk>scan</b><span>Affected</span><b data-program-affected>--</b></div><div class="gitnexus-recommendation" data-program-recommendation>Run scripts/nexus_gitnexus.ps1 scan.</div></div></article>' +
      '<article class="gitnexus-panel"><h2>Top Imported Files</h2><div class="gitnexus-scroll" data-program-top></div></article>' +
      '<article class="gitnexus-panel"><h2>Changed Files</h2><div class="gitnexus-scroll" data-program-changed-list></div></article>' +
      '<div class="gitnexus-footer-line"><span>No autonomous authority.</span><span>No shell execution from model output.</span><span>No NexusCell policy change.</span></div>';

    program.append(head, body);
    document.body.appendChild(program);
    return program;
  }

  function fillProgram(program, data) {
    const q = (selector) => program.querySelector(selector);
    const set = (selector, value, fallback) => {
      const el = q(selector);
      if (el) el.textContent = text(value, fallback);
    };

    set("[data-program-files]", data?.counts?.files);
    set("[data-program-symbols]", data?.counts?.symbols);
    set("[data-program-edges]", data?.counts?.edges);
    set("[data-program-changed]", data?.counts?.changed_files);
    set("[data-program-risk]", data?.impact?.risk, "scan");
    set("[data-program-affected]", data?.impact?.affected_count);
    set("[data-program-recommendation]", data?.recommendation?.summary, "Run scripts/nexus_gitnexus.ps1 scan.");

    const graph = q("[data-gitnexus-graph]");
    if (graph) graph.innerHTML = buildGraphSvg(data);
    const top = q("[data-program-top]");
    if (top) top.innerHTML = rows(data?.top_imported_files || [], "importer_count");
    const changed = q("[data-program-changed-list]");
    const changedRows = (data?.impact?.changed_files || []).slice(0, 18).map((file, i) => ({ file, index: i + 1 }));
    if (changed) changed.innerHTML = rows(changedRows, "index");
  }

  async function openProgram() {
    const program = ensureProgram();
    const data = await loadReport();
    fillProgram(program, data || {});
    program.hidden = false;
  }

  function ensureDock() {
    document.querySelectorAll("#gitnexus-core-station").forEach((el) => el.remove());
    let dock = document.getElementById("gitnexus-core-left-dock");
    if (!dock) {
      dock = make("section");
      dock.id = "gitnexus-core-left-dock";
      dock.dataset.gitnexusPlacement = "floating-left-empty-slot";
      document.body.appendChild(dock);
    }

    dock.innerHTML =
      '<section id="gitnexus-core-station" class="gitnexus-core-station">' +
        '<div class="gitnexus-core-station-head"><div class="gitnexus-core-title">GITNEXUS</div><div class="gitnexus-core-badge">Evidence</div></div>' +
        '<button type="button" class="gitnexus-core-button">Open Codegraph HUD</button>' +
        '<div class="gitnexus-core-mini">' +
          '<span>Files<strong data-gitnexus-files>--</strong></span>' +
          '<span>Symbols<strong data-gitnexus-symbols>--</strong></span>' +
          '<span>Edges<strong data-gitnexus-edges>--</strong></span>' +
          '<span>Risk<strong data-gitnexus-risk>scan</strong></span>' +
        '</div>' +
        '<div class="gitnexus-core-note">Floating left dock. Run scripts/nexus_gitnexus.ps1 scan.</div>' +
      '</section>';

    dock.querySelector("button")?.addEventListener("click", openProgram);
    positionDock(dock);
    ensureProgram();
    loadReport().then((data) => setMini(dock, data));
    return dock;
  }

  function boot() {
    document.querySelectorAll("#gitnexus-core-overlay").forEach((el) => el.remove());
    document.querySelectorAll("#gitnexus-core-station").forEach((el) => el.remove());
    const dock = ensureDock();
    positionDock(dock);
    setTimeout(() => positionDock(dock), 250);
    setTimeout(() => positionDock(dock), 900);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener("load", boot);
  window.addEventListener("resize", () => {
    const dock = document.getElementById("gitnexus-core-left-dock");
    if (dock) positionDock(dock);
  });
  setInterval(() => {
    const dock = document.getElementById("gitnexus-core-left-dock");
    if (dock) positionDock(dock);
  }, 1500);
})();
