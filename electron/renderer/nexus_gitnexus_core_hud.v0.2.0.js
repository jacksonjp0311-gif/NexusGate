(() => {
  const VERSION = "v0.2.0";
  const REPORT_PATHS = [
    "../../reports/gitnexus_report_latest.json",
    "../../state/gitnexus/gitnexus_graph_latest.json",
    "../../GITNEXUS/reports/gitnexus_report_latest.json"
  ];

  let graphState = {
    nodes: [],
    edges: [],
    selected: null,
    query: "",
    showEdges: true,
    animation: true,
    raf: null,
    transform: { x: 0, y: 0, scale: 1 }
  };

  function make(tag, cls) {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    return el;
  }

  function text(value, fallback = "--") {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  function hash(str) {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function colorFor(path) {
    const p = String(path || "");
    if (p.includes("test")) return "#b46cff";
    if (p.endsWith(".py")) return "#55f7ff";
    if (p.endsWith(".js") || p.endsWith(".html") || p.endsWith(".css")) return "#ffaa00";
    if (p.includes("state") || p.includes("reports") || p.includes("ledger")) return "#7dff4d";
    if (p.includes("docs")) return "#5f7cff";
    return "#41f0d0";
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
      .filter((item) => item.rect.left >= -4 && item.rect.left < 80 && item.rect.width >= 230 && item.rect.width <= 390 && item.text.includes("PROCESS LANES"))
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
    const hit = Array.from(document.querySelectorAll("footer, section, div"))
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
    station.querySelector("[data-gitnexus-files]").textContent = text(data?.counts?.files);
    station.querySelector("[data-gitnexus-symbols]").textContent = text(data?.counts?.symbols);
    station.querySelector("[data-gitnexus-edges]").textContent = text(data?.counts?.edges);
    station.querySelector("[data-gitnexus-risk]").textContent = text(data?.impact?.risk, "scan");
  }

  function buildModel(report) {
    const files = Object.keys(report?.files || {});
    const top = (report?.top_imported_files || []).map((x) => x.file);
    const changed = (report?.impact?.changed_files || []).map((x) => String(x).replace(/^"|"$/g, ""));
    const edgeList = Array.isArray(report?.edges) ? report.edges : [];

    const ordered = [];
    const add = (name) => {
      if (!name || ordered.includes(name)) return;
      ordered.push(name);
    };

    top.forEach(add);
    changed.forEach(add);
    edgeList.forEach((e) => { add(e.source); add(e.target); });
    files.slice(0, 520).forEach(add);

    const nodes = ordered.slice(0, 620).map((id, index) => {
      const h = hash(id);
      const cluster = clusterFor(id);
      const ring = 70 + (cluster * 42) + ((h >>> 8) % 65);
      const angle = ((h % 3600) / 3600) * Math.PI * 2;
      const boost = top.includes(id) ? 1.75 : changed.includes(id) ? 1.45 : 1;
      return {
        id,
        label: id.split("/").slice(-2).join("/"),
        cluster,
        x: Math.cos(angle) * ring,
        y: Math.sin(angle) * ring,
        vx: 0,
        vy: 0,
        r: Math.max(2.2, Math.min(8, 2.2 * boost + Math.log2((report?.files?.[id]?.bytes || 1) + 1) * 0.08)),
        color: colorFor(id),
        hot: top.includes(id),
        changed: changed.includes(id)
      };
    });

    const index = new Map(nodes.map((n, i) => [n.id, i]));
    const edges = [];
    edgeList.forEach((e) => {
      const s = index.get(e.source);
      const t = index.get(e.target);
      if (s !== undefined && t !== undefined) edges.push({ s, t, kind: e.kind || "imports" });
    });

    return { nodes, edges };
  }

  function clusterFor(path) {
    const p = String(path || "");
    if (p.includes("nexus_cell")) return 1;
    if (p.includes("compiler")) return 2;
    if (p.includes("electron")) return 3;
    if (p.includes("tests")) return 4;
    if (p.includes("state") || p.includes("reports") || p.includes("ledger")) return 5;
    if (p.includes("docs")) return 6;
    return hash(p) % 7;
  }

  function relax(model) {
    const nodes = model.nodes;
    const edges = model.edges.slice(0, 1200);
    for (const e of edges) {
      const a = nodes[e.s];
      const b = nodes[e.t];
      if (!a || !b) continue;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) || 1;
      const desired = 52 + Math.abs(a.cluster - b.cluster) * 18;
      const force = (d - desired) * 0.0028;
      const fx = dx / d * force;
      const fy = dy / d * force;
      a.vx += fx; a.vy += fy;
      b.vx -= fx; b.vy -= fy;
    }

    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      for (let j = i + 1; j < Math.min(nodes.length, i + 90); j++) {
        const b = nodes[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const d2 = dx * dx + dy * dy + 0.01;
        if (d2 > 2500) continue;
        const d = Math.sqrt(d2);
        const force = Math.min(0.55, 40 / d2);
        const fx = dx / d * force;
        const fy = dy / d * force;
        a.vx -= fx; a.vy -= fy;
        b.vx += fx; b.vy += fy;
      }
    }

    for (const n of nodes) {
      const pull = 0.0009;
      n.vx += -n.x * pull;
      n.vy += -n.y * pull;
      n.x += n.vx;
      n.y += n.vy;
      n.vx *= 0.86;
      n.vy *= 0.86;
    }
  }

  function viewTransform(canvas, nodes) {
    if (!nodes.length) return { scale: 1, ox: canvas.width / 2, oy: canvas.height / 2 };
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const n of nodes) {
      minX = Math.min(minX, n.x); minY = Math.min(minY, n.y);
      maxX = Math.max(maxX, n.x); maxY = Math.max(maxY, n.y);
    }
    const w = Math.max(1, maxX - minX);
    const h = Math.max(1, maxY - minY);
    const scale = Math.min(canvas.width / (w + 160), canvas.height / (h + 160));
    return {
      scale,
      ox: canvas.width / 2 - ((minX + maxX) / 2) * scale,
      oy: canvas.height / 2 - ((minY + maxY) / 2) * scale
    };
  }

  function draw(canvas, model, report) {
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    if (canvas.width !== Math.floor(rect.width * dpr) || canvas.height !== Math.floor(rect.height * dpr)) {
      canvas.width = Math.floor(rect.width * dpr);
      canvas.height = Math.floor(rect.height * dpr);
    }

    if (graphState.animation) relax(model);

    const query = graphState.query.toLowerCase().trim();
    const matched = query ? new Set(model.nodes.filter((n) => n.id.toLowerCase().includes(query) || n.label.toLowerCase().includes(query)).map((n) => n.id)) : null;
    const t = viewTransform(canvas, model.nodes);
    graphState.transform = t;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.fillStyle = "#00040a";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const rad = Math.min(canvas.width, canvas.height) * .42;
    const g = ctx.createRadialGradient(cx, cy, 10, cx, cy, rad);
    g.addColorStop(0, "rgba(255,169,0,.14)");
    g.addColorStop(.25, "rgba(85,247,255,.10)");
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (graphState.showEdges) {
      ctx.lineWidth = Math.max(0.35, 0.75 * (window.devicePixelRatio || 1));
      for (const e of model.edges.slice(0, 2200)) {
        const a = model.nodes[e.s];
        const b = model.nodes[e.t];
        if (!a || !b) continue;
        const ax = a.x * t.scale + t.ox;
        const ay = a.y * t.scale + t.oy;
        const bx = b.x * t.scale + t.ox;
        const by = b.y * t.scale + t.oy;
        const hot = a.hot || b.hot || a.changed || b.changed;
        ctx.strokeStyle = hot ? "rgba(255,169,0,.34)" : "rgba(85,247,255,.13)";
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(bx, by);
        ctx.stroke();
      }
    }

    for (const n of model.nodes) {
      const x = n.x * t.scale + t.ox;
      const y = n.y * t.scale + t.oy;
      const active = !matched || matched.has(n.id);
      const r = (n.r * (active ? 1 : .55)) * (window.devicePixelRatio || 1);

      ctx.beginPath();
      ctx.arc(x, y, r + (n.hot ? 2 : 0), 0, Math.PI * 2);
      ctx.fillStyle = active ? n.color : "rgba(80,110,120,.35)";
      ctx.globalAlpha = active ? (n.changed ? .96 : .78) : .18;
      ctx.fill();

      if (n.hot || n.changed || matched?.has(n.id)) {
        ctx.globalAlpha = .88;
        ctx.lineWidth = 1.6;
        ctx.strokeStyle = n.changed ? "#7dff4d" : "#ffaa00";
        ctx.stroke();
      }
    }

    ctx.globalAlpha = 1;
    ctx.font = `${10 * (window.devicePixelRatio || 1)}px Consolas`;
    ctx.fillStyle = "rgba(223,251,255,.72)";
    const labels = model.nodes.filter((n) => n.hot || n.changed || matched?.has(n.id)).slice(0, 60);
    for (const n of labels) {
      const x = n.x * t.scale + t.ox;
      const y = n.y * t.scale + t.oy;
      ctx.fillText(n.label, x + 7, y - 7);
    }

    ctx.restore();
    graphState.raf = requestAnimationFrame(() => draw(canvas, model, report));
  }

  function rows(items, countKey) {
    if (!Array.isArray(items) || !items.length) return '<div class="gitnexus-row"><i></i><span>No entries.</span><b>--</b></div>';
    return items.slice(0, 18).map((item, index) => {
      const name = item.file || item.path || String(item);
      const count = item[countKey] ?? item.importer_count ?? item.index ?? "";
      return '<div class="gitnexus-row"><i class="gitnexus-dot" style="color:' + colorFor(name) + ';background:' + colorFor(name) + '"></i><span title="' + name.replace(/"/g, "&quot;") + '">' + name + '</span><b>' + count + '</b></div>';
    }).join("");
  }

  function createBigHud() {
    let hud = document.getElementById("gitnexus-big-hud");
    if (hud) return hud;

    hud = make("section", "gitnexus-big");
    hud.id = "gitnexus-big-hud";
    hud.hidden = true;
    hud.innerHTML =
      '<div class="gitnexus-big-top">' +
        '<div class="gitnexus-brand"><div class="gitnexus-logo-orb"></div><div><h1>GITNEXUS</h1><p>NexusGate Codegraph Intelligence</p></div></div>' +
        '<div class="gitnexus-search"><input data-gn-search placeholder="Search nodes, files, symbols..." /><button class="gitnexus-control-btn" data-gn-fit>Fit</button><button class="gitnexus-control-btn" data-gn-edges>Edges</button></div>' +
        '<div class="gitnexus-pill-row"><span class="gitnexus-pill" data-gn-risk>Risk</span><span class="gitnexus-pill">Evidence Only</span></div>' +
        '<button class="gitnexus-close" data-gn-close>Close</button>' +
      '</div>' +
      '<div class="gitnexus-big-body">' +
        '<aside class="gitnexus-big-panel gitnexus-sidebar"><h2>Explorer</h2><div class="gitnexus-stat-grid"><div class="gitnexus-stat">Files<b data-gn-files>--</b></div><div class="gitnexus-stat">Symbols<b data-gn-symbols>--</b></div><div class="gitnexus-stat">Edges<b data-gn-edge-count>--</b></div><div class="gitnexus-stat">Changed<b data-gn-changed>--</b></div></div><div class="gitnexus-filter-list" data-gn-filters></div><div class="gitnexus-file-list" data-gn-changed-list></div></aside>' +
        '<main class="gitnexus-big-panel gitnexus-graph-shell"><canvas id="gitnexus-big-canvas"></canvas><div class="gitnexus-canvas-hud"><span>Force Graph</span><span>Hot Nodes</span><span>Live Evidence</span></div><div class="gitnexus-selected" data-gn-selected>Click a node to inspect. Search highlights matching files.</div></main>' +
        '<aside class="gitnexus-big-panel gitnexus-right"><section><h2>Recommendation</h2><div class="gitnexus-recommendation" data-gn-rec>Run scripts/nexus_gitnexus.ps1 scan.</div></section><section><h2>Top Imported Files</h2><div class="gitnexus-detail-list" data-gn-top></div></section><section><h2>Selected Node</h2><div class="gitnexus-recommendation" data-gn-node>No node selected.</div></section></aside>' +
      '</div>' +
      '<footer class="gitnexus-big-bottom"><span>No autonomous authority.</span><span>No shell execution from model output.</span><span>No NexusCell policy change.</span></footer>';

    document.body.appendChild(hud);
    return hud;
  }

  function fillHud(hud, report) {
    hud.querySelector("[data-gn-files]").textContent = text(report?.counts?.files);
    hud.querySelector("[data-gn-symbols]").textContent = text(report?.counts?.symbols);
    hud.querySelector("[data-gn-edge-count]").textContent = text(report?.counts?.edges);
    hud.querySelector("[data-gn-changed]").textContent = text(report?.counts?.changed_files);
    hud.querySelector("[data-gn-risk]").textContent = "Risk " + text(report?.impact?.risk, "scan");
    hud.querySelector("[data-gn-rec]").textContent = text(report?.recommendation?.summary, "Run scripts/nexus_gitnexus.ps1 scan.");

    const changed = (report?.impact?.changed_files || []).map((file, i) => ({ file: String(file).replace(/^"|"$/g, ""), index: i + 1 }));
    hud.querySelector("[data-gn-changed-list]").innerHTML = rows(changed, "index");
    hud.querySelector("[data-gn-top]").innerHTML = rows(report?.top_imported_files || [], "importer_count");

    const filters = [
      ["Python", "#55f7ff"], ["Electron/UI", "#ffaa00"], ["Tests", "#b46cff"],
      ["State/Reports", "#7dff4d"], ["Docs", "#5f7cff"], ["Core", "#41f0d0"]
    ];
    hud.querySelector("[data-gn-filters]").innerHTML = filters.map(([name, color]) =>
      '<div class="gitnexus-filter-item"><i class="gitnexus-dot" style="color:' + color + ';background:' + color + '"></i><span>' + name + '</span><b>on</b></div>'
    ).join("");
  }

  function nearestNode(canvas, model, event) {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const mx = (event.clientX - rect.left) * dpr;
    const my = (event.clientY - rect.top) * dpr;
    let best = null;
    let bestD = 999999;
    const t = graphState.transform;
    for (const n of model.nodes) {
      const x = n.x * t.scale + t.ox;
      const y = n.y * t.scale + t.oy;
      const d = (x - mx) * (x - mx) + (y - my) * (y - my);
      if (d < bestD) { bestD = d; best = n; }
    }
    return bestD < 900 ? best : null;
  }

  async function openBigHud() {
    const report = await loadReport();
    const hud = createBigHud();
    fillHud(hud, report || {});
    hud.hidden = false;

    if (graphState.raf) cancelAnimationFrame(graphState.raf);
    const model = buildModel(report || {});
    graphState.nodes = model.nodes;
    graphState.edges = model.edges;
    graphState.query = "";
    graphState.animation = true;
    graphState.showEdges = true;

    const canvas = hud.querySelector("#gitnexus-big-canvas");
    const search = hud.querySelector("[data-gn-search]");
    const selected = hud.querySelector("[data-gn-selected]");
    const selectedPanel = hud.querySelector("[data-gn-node]");

    search.value = "";
    search.oninput = () => { graphState.query = search.value || ""; };
    hud.querySelector("[data-gn-edges]").onclick = () => { graphState.showEdges = !graphState.showEdges; };
    hud.querySelector("[data-gn-fit]").onclick = () => { graphState.animation = !graphState.animation; };
    hud.querySelector("[data-gn-close]").onclick = () => {
      hud.hidden = true;
      if (graphState.raf) cancelAnimationFrame(graphState.raf);
      graphState.raf = null;
    };

    canvas.onclick = (event) => {
      const n = nearestNode(canvas, model, event);
      graphState.selected = n;
      if (n) {
        selected.textContent = "Selected: " + n.id + " | cluster=" + n.cluster + " | changed=" + n.changed;
        selectedPanel.textContent = n.id + "\n\nType color: " + n.color + "\nChanged: " + n.changed + "\nHot/imported: " + n.hot;
        graphState.query = n.label;
        search.value = n.label;
      }
    };

    requestAnimationFrame(() => draw(canvas, model, report || {}));
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
        '<button type="button" class="gitnexus-core-button">Open Big Nexus HUD</button>' +
        '<div class="gitnexus-core-mini">' +
          '<span>Files<strong data-gitnexus-files>--</strong></span>' +
          '<span>Symbols<strong data-gitnexus-symbols>--</strong></span>' +
          '<span>Edges<strong data-gitnexus-edges>--</strong></span>' +
          '<span>Risk<strong data-gitnexus-risk>scan</strong></span>' +
        '</div>' +
        '<div class="gitnexus-core-note">Big graph explorer. Run scripts/nexus_gitnexus.ps1 scan.</div>' +
      '</section>';

    dock.querySelector("button")?.addEventListener("click", openBigHud);
    positionDock(dock);
    createBigHud();
    loadReport().then((data) => setMini(dock, data || {}));
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
})();
