(() => {
  const VERSION = "v0.5.3";
  const MINI_ID = "gitnexus-core-left-dock";
  const HUD_ID = "gitnexus-local-hud";
  const STORE_KEY = "__nexusGitNexusLocalHudV053";

  const state = window[STORE_KEY] || (window[STORE_KEY] = {
    miniRaf: 0,
    fullRaf: 0,
    resizeTimer: 0,
    graph: null,
    graphLoaded: false,
    fullOpen: false,
    paused: false,
    layoutMode: "force", speedMode: "fast", filterMode: "all",
    compareSource: "",
    drag: null,
    hover: null,
    selected: null, analyzer: null, analyzerT: 0,
    search: "",
    lastT: 0,
    fps: 0,
    frameCount: 0,
    showEdges: true,
    showLabels: true,
    coreOnly: false,
    activeCategories: { core: true, ui: true, test: true, state: true, doc: true },
    miniRot: 0,
    camera: { x: 0, y: 0, zoom: 1, rot: 0 },
    target: { x: 0, y: 0, zoom: 1, rot: 0 },
    velocity: { x: 0, y: 0, zoom: 0, rot: 0 }
  });

  const COLORS = {
    bg: "#020712",
    cyan: "#55f7ff",
    cyan2: "#00eaff",
    green: "#7dff4d",
    amber: "#ffaa00",
    violet: "#a855f7",
    blue: "#5b7cff",
    red: "#ff5f7f",
    changed: "#ffb6c6",
    dim: "rgba(85,247,255,0.18)",
    text: "#dffcff",
    smoke: "rgba(160, 190, 200, 0.72)"
  };

  const TYPE_COLOR = {
    py: COLORS.cyan,
    js: COLORS.amber,
    ts: COLORS.amber,
    tsx: COLORS.amber,
    jsx: COLORS.amber,
    test: COLORS.violet,
    state: COLORS.green,
    report: COLORS.green,
    doc: COLORS.blue,
    core: COLORS.cyan,
    other: COLORS.smoke
  };
  const COMPARE_TYPE_COLOR = {
    py: "#ff5fcb",
    js: "#ffd166",
    ts: "#ffd166",
    tsx: "#ffd166",
    jsx: "#ffd166",
    test: "#c084fc",
    state: "#f97316",
    report: "#f97316",
    doc: "#38bdf8",
    core: "#ff5fcb",
    other: "#f5d0fe"
  };

  const CORE_TYPES = new Set(["core", "py", "js", "test"]);
  const CATEGORY_DEFS = [
    { id: "core", label: "Python/Core", kinds: ["core", "py"], color: COLORS.cyan },
    { id: "ui", label: "Electron/UI", kinds: ["js", "ts", "tsx", "jsx"], color: COLORS.amber },
    { id: "test", label: "Tests", kinds: ["test"], color: COLORS.violet },
    { id: "state", label: "State/Reports", kinds: ["state", "report"], color: COLORS.green },
    { id: "doc", label: "Docs", kinds: ["doc"], color: COLORS.blue }
  ];
  const KIND_CATEGORY = new Map(CATEGORY_DEFS.flatMap((category) => category.kinds.map((kind) => [kind, category.id])));
  CATEGORY_DEFS.forEach((category) => {
    if (!Object.prototype.hasOwnProperty.call(state.activeCategories, category.id)) state.activeCategories[category.id] = true;
  });
  const SPEED_PROFILES = {
    fast: { label: "FAST", fps: 28, physics: 0.58, ease: 0.095 },
    medium: { label: "MEDIUM", fps: 18, physics: 0.32, ease: 0.065 },
    slow: { label: "SLOW", fps: 10, physics: 0.12, ease: 0.035 }
  };
  const SPEED_ORDER = ["slow", "medium", "fast"];

  const FILTER_LABELS = {
    all: "MODE ALL",
    hot: "MODE HOT",
    changed: "MODE CHANGED",
    core: "MODE CORE"
  };
  const LAYOUT_LABELS = {
    force: "FORCE",
    orbit: "ORBIT",
    circle: "CIRCLE",
    organism: "ATTRACT",
    poles: "POLES"
  };
  const LAYOUT_ORDER = ["force", "orbit", "circle", "organism", "poles"];

  function q(sel, root = document) { return root.querySelector(sel); }
  function qa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  function safeText(value, fallback = "") {
    if (value == null) return fallback;
    return String(value).replace(/[^\x20-\x7E]/g, "").slice(0, 260);
  }

  function hashText(s) {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function classify(path) {
    const p = String(path || "").toLowerCase();
    if (p.includes("/tests/") || p.includes("\\tests\\") || p.startsWith("tests/") || p.includes("test_")) return "test";
    if (p.includes("/state/") || p.includes("\\state\\") || p.startsWith("state/")) return "state";
    if (p.includes("/reports/") || p.includes("\\reports\\") || p.startsWith("reports/")) return "report";
    if (p.includes("/docs/") || p.includes("\\docs\\") || p.endsWith(".md")) return "doc";
    if (p.includes("nexus_gate/") || p.includes("nexus_gate\\")) return "core";
    if (p.endsWith(".py")) return "py";
    if (p.endsWith(".js")) return "js";
    if (p.endsWith(".ts")) return "ts";
    if (p.endsWith(".tsx")) return "tsx";
    if (p.endsWith(".jsx")) return "jsx";
    return "other";
  }

  function findFooterTop() {
    const footer = qa("footer, section, div")
      .map((node) => ({ rect: node.getBoundingClientRect(), text: String(node.textContent || "").toUpperCase() }))
      .filter((item) => item.text.includes("GOVERNANCE") && item.text.includes("SYSTEM BUS"))
      .sort((a, b) => b.rect.top - a.rect.top)[0]?.rect;
    return footer && footer.top > window.innerHeight * 0.5 ? footer.top : window.innerHeight - 48;
  }

  function findLeftRailRect() {
    const neural = qa("aside, section, article, div")
      .map((node) => ({ rect: node.getBoundingClientRect(), text: String(node.textContent || "").toUpperCase() }))
      .filter((item) =>
        item.rect.width >= 220 &&
        item.rect.width <= 430 &&
        item.rect.left >= -20 &&
        item.rect.left < 140 &&
        item.text.includes("NEURAL ACTIVITY")
      )
      .sort((a, b) => (b.rect.width * b.rect.height) - (a.rect.width * a.rect.height))[0]?.rect;

    if (neural) return neural;
    return { left: 8, right: 310, top: Math.round(window.innerHeight * 0.2), bottom: Math.round(window.innerHeight * 0.58), width: 302, height: 300 };
  }

  function dockGeometry() {
    const rail = findLeftRailRect();
    const footerTop = findFooterTop();
    const petri = document.querySelector(".petri-dish-mini")?.getBoundingClientRect();
    const left = Math.max(4, rail.left);
    const width = Math.max(260, Math.min(405, rail.width || (rail.right - rail.left)));
    const petriAligned = petri && petri.top > window.innerHeight * 0.38 && petri.height > 180;
    const top = petriAligned ? petri.top : Math.min((rail.bottom || 360) + 10, footerTop - 235);
    const height = petriAligned ? petri.height : Math.max(215, footerTop - top - 10);
    return {
      left: Math.round(left),
      top: Math.round(top),
      width: Math.round(width),
      height: Math.round(height)
    };
  }

  function ensureMiniDock() {
    qa("#" + MINI_ID).slice(1).forEach((node) => node.remove());

    let dock = document.getElementById(MINI_ID);
    if (!dock) {
      dock = document.createElement("section");
      dock.id = MINI_ID;
      document.body.appendChild(dock);
    }

    const geo = dockGeometry();
    dock.className = "gnx-local-mini-dock gnx-polished";
    dock.dataset.version = VERSION;
    dock.style.left = geo.left + "px";
    dock.style.top = geo.top + "px";
    dock.style.width = geo.width + "px";
    dock.style.height = geo.height + "px";

    if (!dock.querySelector(".gnx-local-mini")) {
      dock.innerHTML = `
        <section class="gnx-local-mini">
          <div class="gnx-local-mini-head">
            <div class="gnx-local-mini-brand">
              <span class="gnx-local-orb"></span>
              <div>
                <div class="gnx-local-title">GITNEXUS</div>
                <div class="gnx-local-sub">LOCAL CODEGRAPH</div>
              </div>
            </div>
            <button class="gnx-local-open" type="button">OPEN</button>
          </div>
          <button class="gnx-local-mini-body" type="button" title="Open local GITNEXUS HUD">
            <canvas id="gnx-local-mini-canvas"></canvas>
            <span class="gnx-local-caption">LIVE LOCAL CODEGRAPH</span>
          </button>
        </section>
      `;
      q(".gnx-local-open", dock)?.addEventListener("click", openHud);
      q(".gnx-local-mini-body", dock)?.addEventListener("click", openHud);
    }

    return dock;
  }

  function fitCanvas(canvas) {
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    const w = Math.max(1, Math.floor(rect.width));
    const h = Math.max(1, Math.floor(rect.height));
    const tw = Math.floor(w * dpr);
    const th = Math.floor(h * dpr);
    if (canvas.width !== tw || canvas.height !== th) {
      canvas.width = tw;
      canvas.height = th;
    }
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx, w, h };
  }

  function extractCandidateFiles(json) {
    const files = [];
    const seen = new Set();

    function add(path, weight = 1, changed = false) {
      const p = safeText(path).replace(/\\/g, "/");
      if (!p || p.length < 2) return;
      if (p.includes(".bak_") || p.endsWith(".bak") || p.includes("__pycache__")) return;
      if (seen.has(p)) { const existing = files.find((x) => x.path === p); if (existing && changed) existing.changed = true; return; }
      seen.add(p);
      files.push({ path: p, weight: Math.max(1, Number(weight) || 1), changed: Boolean(changed) });
    }

    function walk(x, depth = 0, changedContext = false) {
      if (!x || depth > 5) return;
      if (Array.isArray(x)) {
        for (const item of x.slice(0, 1800)) walk(item, depth + 1, changedContext);
        return;
      }
      if (typeof x !== "object") return;

      const pathKeys = ["path", "file", "filePath", "name", "id", "source", "target"];
      for (const key of pathKeys) {
        const v = x[key];
        if (typeof v === "string" && /[\/\\.]|nexus_gate|electron|reports|state|ledger|docs|tests|GITNEXUS/i.test(v)) {
          add(v, x.weight || x.count || x.imports || x.score || (changedContext ? 6 : 1), changedContext || x.changed === true);
        }
      }

      const arrays = ["nodes", "files", "changed_files", "top_imported_files", "relationships", "edges", "affected_files"];
      for (const key of arrays) {
        if (Array.isArray(x[key])) walk(x[key], depth + 1);
      }

      if (depth < 2) {
        for (const k of Object.keys(x).slice(0, 50)) walk(x[k], depth + 1);
      }
    }

    walk(json, 0);
    return files;
  }

  function buildFallbackFiles() {
    const roots = [
      "docs/context/rcc_nexus_index.json",
      "nexus_gate/__init__.py",
      "nexus_gate/core/packets.py",
      "nexus_gate/runtime/router.py",
      "nexus_gate/compiler/compiler.py",
      "nexus_gate/compiler/gates.py",
      "nexus_gate/geometric_memory/score.py",
      "nexus_gate/adapters/local_demo.py",
      "nexus_gate/adapters/registry.py",
      "nexus_gate/nexus_cell/plan.py",
      "nexus_gate/nexus_cell/policy.py",
      "nexus_gate/receptors/registry.py",
      "nexus_gate/receptors/compatibility.py",
      "nexus_gate/nexus_cell/context_bridge.py",
      "nexus_gate/nn_router/contract.py",
      "nexus_gate/bridge/runtime.py",
      "nexus_gate/bridge/session.py",
      "nexus_gate/self_healing/engine.py",
      "electron/renderer/index.html",
      "electron/main.js",
      "electron/preload.js",
      "reports/nexus_compile_report_latest.json",
      "reports/nexus_electron_smoke_report_latest.json",
      "state/interconnect_graph.v0.2.2.json",
      "ledger/nexus_gate_ledger.v0.1.0.jsonl",
      "docs/runtime/NEXUS_METRICS_HUD.md",
      "docs/gitnexus/NEXUS_GITNEXUS_LOCAL_HUD.md",
      "tests/test_gitnexus_hud_assets.py",
      "tests/test_nn_router.py"
    ];
    const files = [];
    for (let round = 0; round < 10; round++) {
      roots.forEach((p, i) => files.push({ path: p.replace(/(\.[a-z0-9]+)$/i, "_" + round + "$1"), weight: 1 + ((i + round) % 13) }));
    }
    return files;
  }

  function buildGraphFromFiles(files) {
    if (!files || files.length < 12) files = buildFallbackFiles();

    const nodes = [];
    const edges = [];
    const byPath = new Map();

    function addNode(id, path, kind, weight, folder = false, changed = false) {
      if (byPath.has(id)) { const existing = byPath.get(id); if (changed) existing.changed = true; return existing; }
      const h = hashText(id);
      const clusterMap = { py: 0, core: 0, js: 1, ts: 1, tsx: 1, jsx: 1, test: 2, state: 3, report: 3, doc: 4, other: 5 };
      const cluster = clusterMap[kind] ?? 5;
      const golden = Math.PI * (3 - Math.sqrt(5));
      const idx = nodes.length + 1;
      const baseR = folder ? 95 + cluster * 55 : 150 + cluster * 46 + Math.sqrt(idx) * 11;
      const angle = idx * golden + cluster * 0.78 + (h % 360) * Math.PI / 1800;
      const tx = Math.cos(angle) * baseR + ((h & 255) - 128) * 0.18;
      const ty = Math.sin(angle) * baseR + (((h >> 8) & 255) - 128) * 0.18;
      const node = {
        id,
        path,
        name: path.split("/").filter(Boolean).pop() || path,
        kind,
        cluster,
        folder, changed: Boolean(changed),
        weight: Math.max(1, Number(weight) || 1),
        x: tx + (((h >> 16) & 127) - 64),
        y: ty + (((h >> 23) & 127) - 64),
        tx,
        ty,
        vx: 0,
        vy: 0,
        hot: false,
        degree: 0,
        phase: (h % 628) / 100
      };
      nodes.push(node);
      byPath.set(id, node);
      return node;
    }

    const root = addNode("nexus-gate", "nexus-gate", "core", 30, true, false);
    files.slice(0, 1000).forEach((f) => {
      const path = safeText(f.path || f, "unknown");
      const kind = classify(path);
      const n = addNode(path, path, kind, f.weight || 1, false);
      const parts = path.split("/").filter(Boolean);
      const folder = parts.length > 1 ? parts[0] + "/" : "root/";
      const folderNode = addNode("folder:" + folder, folder, classify(folder), 10, true, false);
      edges.push({ a: root.id, b: folderNode.id, type: "contains", weight: 0.7 });
      edges.push({ a: folderNode.id, b: n.id, type: f.changed ? "changed" : "contains", weight: f.changed ? 0.8 : 0.45 });
    });

    const top = nodes.filter((n) => !n.id.startsWith("folder:") && n.id !== root.id);
    top.forEach((n, i) => {
      const h = hashText(n.id);
      const j = h % Math.max(1, top.length);
      if (top[j] && top[j] !== n && (i % 2 === 0 || n.kind === top[j].kind)) {
        edges.push({ a: n.id, b: top[j].id, type: n.kind === top[j].kind ? "same-kind" : "trace", weight: n.kind === top[j].kind ? 0.30 : 0.15 });
      }
      if (i % 9 === 0 && top[i + 5]) edges.push({ a: n.id, b: top[i + 5].id, type: "pulse", weight: 0.11 });
    });

    edges.forEach((e) => {
      const a = byPath.get(e.a), b = byPath.get(e.b);
      if (a) a.degree += 1;
      if (b) b.degree += 1;
    });

    nodes.sort((a, b) => (b.degree + b.weight) - (a.degree + a.weight));
    nodes.slice(0, Math.max(12, Math.floor(nodes.length * 0.09))).forEach((n) => { n.hot = true; });

    return { nodes, edges, byId: byPath, counts: { files: files.length, symbols: nodes.length, edges: edges.length } };
  }

  function setAllCategories(enabled = true) {
    CATEGORY_DEFS.forEach((category) => {
      state.activeCategories[category.id] = Boolean(enabled);
    });
    updateCategoryPanel();
  }

  function mergeCompareGraph(base, compare, sourceLabel = "compare") {
    if (!base || !compare?.nodes?.length) return base;
    const cleanLabel = safeText(sourceLabel || "compare", "compare").replace(/\\/g, "/").split("/").filter(Boolean).slice(-2).join("/") || "compare";
    const existingNodes = (base.nodes || []).filter((node) => !node.compare);
    const existingEdges = (base.edges || []).filter((edge) => !edge.compare);
    existingNodes.forEach((node) => {
      node.repoIndex = 0;
      if (!node.repoOffsetApplied) {
        node.x -= 260;
        node.tx -= 260;
        node.repoOffsetApplied = true;
      }
    });
    const offsetX = 620;
    const prefix = "compare:";
    const copiedNodes = (compare.nodes || []).slice(0, 1000).map((node) => {
      const id = prefix + node.id;
      const copied = {
        ...node,
        id,
        path: `${cleanLabel}/${safeText(node.path || node.name || node.id)}`,
        name: safeText(node.name || node.path || node.id),
        x: (Number(node.x) || 0) + offsetX,
        tx: (Number(node.tx) || 0) + offsetX,
        compare: true,
        repoIndex: 1,
        repoOffsetApplied: true,
        vx: 0,
        vy: 0
      };
      return copied;
    });
    const copiedIds = new Set(copiedNodes.map((node) => node.id));
    const copiedEdges = (compare.edges || []).slice(0, 1400).map((edge) => ({
      ...edge,
      a: prefix + edge.a,
      b: prefix + edge.b,
      compare: true,
      weight: Math.max(0.08, Number(edge.weight) || 0.18)
    })).filter((edge) => copiedIds.has(edge.a) && copiedIds.has(edge.b));

    const nodes = existingNodes.concat(copiedNodes);
    const edges = existingEdges.concat(copiedEdges);
    const byId = new Map(nodes.map((node) => [node.id, node]));
    nodes.forEach((node) => { node.degree = 0; });
    edges.forEach((edge) => {
      const a = byId.get(edge.a);
      const b = byId.get(edge.b);
      if (a) a.degree += 1;
      if (b) b.degree += 1;
    });
    const baseFiles = base.counts?.files || existingNodes.filter((node) => !node.folder).length;
    const compareFiles = compare.counts?.files || copiedNodes.filter((node) => !node.folder).length;
    return {
      ...base,
      nodes,
      edges,
      byId,
      source: `${base.source || "local"} + ${cleanLabel}`,
      counts: {
        files: baseFiles + compareFiles,
        symbols: nodes.length,
        edges: edges.length
      }
    };
  }

  async function tryReadJson(path) {
    try {
      const res = await fetch(path + "?t=" + Date.now(), { cache: "no-store" });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  }

  async function loadGraph(force = false) {
    if (state.graphLoaded && state.graph && !force) return state.graph;

    const paths = [
      "../../GITNEXUS/state/gitnexus_graph_latest.json",
      "../../state/gitnexus/gitnexus_graph_latest.json",
      "../../GITNEXUS/reports/gitnexus_report_latest.json",
      "../../reports/gitnexus_report_latest.json",
      "../../reports/nexus_compile_report_latest.json",
      "../../state/interconnect_graph.v0.2.2.json"
    ];

    let files = [];
    let source = "fallback";
    for (const path of paths) {
      const json = await tryReadJson(path);
      if (!json) continue;
      const extracted = extractCandidateFiles(json);
      if (extracted.length > files.length) {
        files = extracted;
        source = path.replace("../../", "");
      }
    }

    if (files.length < 12) files = buildFallbackFiles();
    state.graph = buildGraphFromFiles(files);
    state.graph.source = source;
    state.graphLoaded = true; state.analyzer = analyzeGeometry(state.graph);
    updateHudStats();
    updateTopFiles();
    updateAnalyzerPanel();
    return state.graph;
  }

  async function loadCompareGraph(localPath) {
    const hud = q(`#${HUD_ID}`);
    const status = q("[data-status]", hud);
    if (!window.nexus?.scanGitNexusExternal) {
      if (status) status.textContent = "External repo compare bridge is unavailable.";
      return;
    }
    if (status) status.textContent = "Scanning external repo read-only...";
    try {
      await loadGraph(false);
      const packet = await window.nexus.scanGitNexusExternal(localPath);
      const files = extractCandidateFiles(packet);
      if (files.length < 3) throw new Error("No candidate files found in external repo.");
      const compare = buildGraphFromFiles(files);
      compare.source = packet.root || localPath;
      state.compareSource = compare.source;
      state.graph = mergeCompareGraph(state.graph, compare, compare.source);
      state.analyzer = analyzeGeometry(state.graph);
      updateHudStats();
      updateTopFiles();
      updateAnalyzerPanel();
      fitFull();
      if (status) status.textContent = `Compared read-only repo: ${safeText(compare.source).slice(0, 120)}`;
    } catch (error) {
      if (status) status.textContent = `Compare blocked: ${error.message}`;
    }
  }

  function visibleNode(n) {
    if (!n) return false;
    if (!n.folder) {
      const category = KIND_CATEGORY.get(n.kind) || "other";
      if (Object.prototype.hasOwnProperty.call(state.activeCategories, category) && state.activeCategories[category] === false) return false;
    }
    if (state.filterMode === "hot" && !n.hot) return false;
    if (state.filterMode === "changed" && !n.changed) return false;
    if (state.filterMode === "core" && !CORE_TYPES.has(n.kind)) return false;
    if (state.coreOnly && !CORE_TYPES.has(n.kind)) return false;
    const s = String(state.search || "").toLowerCase().trim();
    if (s && !String(n.path).toLowerCase().includes(s) && !String(n.name).toLowerCase().includes(s)) return false;
    return true;
  }

  function visibleNodes(graph = state.graph) {
    return (graph?.nodes || []).filter(visibleNode);
  }

  function visibleFileNodes(graph = state.graph) {
    return visibleNodes(graph).filter((n) => !n.folder && n.id !== "nexus-gate");
  }

  function countVisibleForMode(mode) {
    const previous = state.filterMode;
    const previousCore = state.coreOnly;
    state.filterMode = mode;
    state.coreOnly = mode === "core";
    const count = visibleFileNodes().length;
    state.filterMode = previous;
    state.coreOnly = previousCore;
    return count;
  }

  function setFilterMode(mode, button) {
    const nextMode = FILTER_LABELS[mode] ? mode : "all";
    if (nextMode === "all") setAllCategories(true);
    state.filterMode = countVisibleForMode(nextMode) > 0 ? nextMode : "all";
    state.coreOnly = state.filterMode === "core";
    if (button) button.textContent = FILTER_LABELS[state.filterMode];
    updateTopFiles();
    updateAnalyzerPanel();
    fitFull();
  }

  // selected-node focus path highlighting + geometry analyzer
  function analyzeGeometry(graph) {
    const nodes = visibleFileNodes(graph);
    const visibleIds = new Set(visibleNodes(graph).map((n) => n.id));
    const edges = (graph?.edges || []).filter((edge) => visibleIds.has(edge.a) && visibleIds.has(edge.b));
    const count = Math.max(1, nodes.length);
    const edgeCount = edges.length;
    const degrees = nodes.map((n) => n.degree || 0);
    const mean = degrees.reduce((a, b) => a + b, 0) / count;
    const variance = degrees.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / count;
    const std = Math.sqrt(variance);
    const hubs = nodes.filter((n) => (n.degree || 0) >= mean + Math.max(2, std * 1.35)).length;
    const changed = nodes.filter((n) => n.changed).length;
    const hot = nodes.filter((n) => n.hot).length;
    const density = count > 1 ? (2 * edgeCount) / (count * (count - 1)) : 0;

    let cx = 0, cy = 0;
    nodes.forEach((n) => { cx += n.x; cy += n.y; });
    cx /= count; cy /= count;

    let sx = 0, sy = 0, sxy = 0, radius = 0;
    nodes.forEach((n) => {
      const dx = n.x - cx;
      const dy = n.y - cy;
      sx += dx * dx;
      sy += dy * dy;
      sxy += dx * dy;
      radius += Math.hypot(dx, dy);
    });
    sx /= count; sy /= count; sxy /= count; radius /= count;

    const trace = sx + sy;
    const det = sx * sy - sxy * sxy;
    const root = Math.sqrt(Math.max(0, trace * trace / 4 - det));
    const l1 = trace / 2 + root;
    const l2 = Math.max(0.0001, trace / 2 - root);
    const anisotropy = Math.sqrt(l1 / l2);

    const clusters = {};
    nodes.forEach((n) => { clusters[n.kind] = (clusters[n.kind] || 0) + 1; });
    const parts = Object.values(clusters);
    const entropy = -parts.reduce((acc, c) => {
      const p = c / count;
      return acc + p * Math.log2(p);
    }, 0);
    const entropyMax = Math.log2(Math.max(2, parts.length));
    const balance = entropyMax ? entropy / entropyMax : 0; // category entropy

    const byId = graph.byId || new Map((graph.nodes || []).map((n) => [n.id, n]));
    let cross = 0;
    edges.forEach((edge) => {
      const a = byId.get(edge.a);
      const b = byId.get(edge.b);
      if (a && b && a.kind !== b.kind) cross += 1;
    });
    const bridgePressure = edgeCount ? cross / edgeCount : 0;

    let pattern = "balanced mesh";
    if (hubs >= 3 && bridgePressure > 0.55) pattern = "multi-hub bridge mesh";
    if (hubs <= 1 && density < 0.015) pattern = "sparse radial field";
    if (anisotropy > 2.2) pattern = "stretched corridor";
    if (changed / count > 0.18) pattern = "change-pressure bloom";
    if (balance < 0.45) pattern = "single-domain dominance";

    let recommendation = "Geometry is balanced. Use MODE HOT for strongest pressure routes.";
    if (pattern === "multi-hub bridge mesh") recommendation = "Multiple hubs are bridging domains. Select a hub to inspect pressure paths.";
    if (pattern === "sparse radial field") recommendation = "Graph is sparse and radial. Use MODE CORE to inspect root route authority.";
    if (pattern === "stretched corridor") recommendation = "Geometry is elongated. Rotate and fit before interpreting clusters.";
    if (pattern === "change-pressure bloom") recommendation = "Changed files are distributed. Use MODE CHANGED before commit.";
    if (pattern === "single-domain dominance") recommendation = "One category dominates. Toggle labels and MODE HOT/CORE to reduce bias.";

    const diagnostics = buildDiagnostics(graph, nodes, edges);
    const summary = buildGeometrySummary({ pattern, nodeCount: count, edgeCount, density, hubs, changed, hot, radius, anisotropy, bridgePressure, balance }, diagnostics);

    return { pattern, recommendation, summary, diagnostics, nodeCount: count, edgeCount, density, hubs, changed, hot, radius, anisotropy, bridgePressure, balance };
  }

  function scoreNode(n) {
    return Math.round((n.degree || 0) * 1.8 + (n.weight || 1) + (n.hot ? 8 : 0) + (n.changed ? 10 : 0));
  }

  function buildDiagnostics(graph, nodes, edges) {
    const visibleIds = new Set(nodes.map((n) => n.id));
    const adjacency = new Map(nodes.map((n) => [n.id, new Set()]));
    const inbound = new Map(nodes.map((n) => [n.id, 0]));
    const outbound = new Map(nodes.map((n) => [n.id, 0]));
    edges.forEach((edge) => {
      if (!visibleIds.has(edge.a) || !visibleIds.has(edge.b)) return;
      adjacency.get(edge.a)?.add(edge.b);
      adjacency.get(edge.b)?.add(edge.a);
      outbound.set(edge.a, (outbound.get(edge.a) || 0) + 1);
      inbound.set(edge.b, (inbound.get(edge.b) || 0) + 1);
    });

    const centrality = nodes
      .map((n) => ({ node: n, score: scoreNode(n), inbound: inbound.get(n.id) || 0, outbound: outbound.get(n.id) || 0 }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 20);
    const deadIslands = nodes
      .filter((n) => (inbound.get(n.id) || 0) + (outbound.get(n.id) || 0) <= 1)
      .sort((a, b) => scoreNode(a) - scoreNode(b))
      .slice(0, 12)
      .map((node) => ({ node, score: scoreNode(node) }));
    const bridgeRisk = centrality
      .filter((item) => item.inbound > 0 && item.outbound > 0)
      .map((item) => ({ ...item, score: item.score + Math.min(item.inbound, item.outbound) * 3 }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 12);
    const changePriority = nodes
      .filter((n) => n.changed || n.hot || (n.degree || 0) >= 5)
      .map((node) => ({ node, score: scoreNode(node) + (node.changed ? 20 : 0) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 12);
    const blastRadius = (state.selected && graph?.byId?.get(state.selected))
      ? [...(adjacency.get(state.selected) || [])].map((id) => graph.byId.get(id)).filter(Boolean).slice(0, 12)
      : centrality.slice(0, 8).map((item) => item.node);

    return { centrality, deadIslands, bridgeRisk, changePriority, blastRadius };
  }

  function buildGeometrySummary(a, diagnostics) {
    const lead = `${a.nodeCount} visible files are forming a ${a.pattern} with ${a.hubs} load-bearing hubs and ${Math.round(a.bridgePressure * 100)}% cross-domain bridge pressure.`;
    const central = diagnostics.centrality[0]?.node?.path || "no central file";
    const change = diagnostics.changePriority[0]?.node?.path || "no changed or hot file";
    const islandCount = diagnostics.deadIslands.length;
    const compareCount = visibleFileNodes().filter((node) => node.repoIndex === 1).length;
    const repoFrame = compareCount
      ? `External compare lobe active with ${compareCount} visible files; colors are shifted to separate local architecture from the compared repository.`
      : "Single-repository lobe active.";
    const spatial = `Spatial read: density ${(a.density).toFixed(3)}, anisotropy ${a.anisotropy.toFixed(2)}, balance ${Math.round(a.balance * 100)}%. High anisotropy means corridor-like coupling; high bridge pressure means cross-domain risk.`;
    return `${lead} ${repoFrame} ${spatial} Highest centrality: ${central}. Highest patch priority: ${change}. Dead-island candidates: ${islandCount}. Use category toggles and diagnostic HUDs to isolate domains before mutation.`;
  }

  function updateAnalyzerPanel() {
    const a = state.analyzer;
    if (!a) return;
    const set = (key, value) => {
      qa(`[data-geo='${key}']`).forEach((node) => { node.textContent = String(value); });
    };
    set("pattern", a.pattern);
    set("density", a.density.toFixed(3));
    set("hubs", a.hubs);
    set("bridge", Math.round(a.bridgePressure * 100) + "%");
    set("balance", Math.round(a.balance * 100) + "%");
    set("anisotropy", a.anisotropy.toFixed(2));
    set("recommendation", a.recommendation);
    set("summary", a.summary || a.recommendation);
    updateDiagnosticPanel(a.diagnostics);
    qa("[data-mini-caption]").forEach((n) => { n.textContent = a.pattern.toUpperCase().slice(0, 28); });
  }

  function diagnosticRow(item, i) {
    const node = item?.node || item;
    if (!node) return "";
    const score = item?.score ?? scoreNode(node);
    return `<li data-node-id="${encodeURIComponent(node.id)}"><span>${String(i + 1).padStart(2, "0")}</span><b>${safeText(node.path).slice(0, 48)}</b><em>${Math.round(score)}</em></li>`;
  }

  function updateDiagnosticPanel(diagnostics) {
    const panel = q("[data-diagnostics]");
    if (!panel || !diagnostics) return;
    const sections = [
      ["Centrality", diagnostics.centrality, "top 20 load-bearing files"],
      ["Blast Radius", diagnostics.blastRadius, "selected or central neighbors"],
      ["Dead Islands", diagnostics.deadIslands, "low-link refactor candidates"],
      ["Bridge Risk", diagnostics.bridgeRisk, "files linking clusters"],
      ["Change Priority", diagnostics.changePriority, "patch-risk ranking"]
    ];
    panel.innerHTML = sections.map(([title, rows, note]) => `
      <section>
        <h4>${title}<span>${note}</span></h4>
        <ol>${(rows || []).slice(0, title === "Centrality" ? 20 : 10).map(diagnosticRow).join("") || "<li><span>--</span><b>No evidence in current filter.</b><em>0</em></li>"}</ol>
      </section>
    `).join("");
    qa("li[data-node-id]", panel).forEach((li) => {
      li.addEventListener("click", () => {
        const id = decodeURIComponent(li.getAttribute("data-node-id") || "");
        const node = state.graph?.byId?.get(id);
        if (node) focusNode(node, true);
      });
    });
  }

  function labelAllowed(box, placed) {
    for (const b of placed) {
      if (!(box.x2 < b.x1 || box.x1 > b.x2 || box.y2 < b.y1 || box.y1 > b.y2)) return false;
    }
    placed.push(box);
    return true;
  }

  function setLayoutMode(mode) {
    state.layoutMode = LAYOUT_LABELS[mode] ? mode : "force";
    state.velocity.x = 0;
    state.velocity.y = 0;
    updateControlStates();
  }

  function togglePause(force) {
    state.paused = typeof force === "boolean" ? force : !state.paused;
    updateControlStates();
  }

  function turnGraph(amount = Math.PI / 7) {
    state.target.rot += amount;
    state.camera.rot += amount * 0.22;
    state.velocity.rot = amount * 0.01;
  }

  function updateControlStates() {
    const hud = q(`#${HUD_ID}`);
    if (!hud) return;
    const layoutButton = q("[data-layout]", hud);
    if (layoutButton) layoutButton.textContent = "FORCE";
    qa("[data-layout], [data-attractor], [data-poles]", hud).forEach((button) => button.classList.remove("is-on"));
    if (state.layoutMode === "force") q("[data-layout]", hud)?.classList.add("is-on");
    if (state.layoutMode === "organism") q("[data-attractor]", hud)?.classList.add("is-on");
    if (state.layoutMode === "poles") q("[data-poles]", hud)?.classList.add("is-on");
    const pause = q("[data-pause]", hud);
    if (pause) {
      pause.textContent = state.paused ? "RESUME" : "PAUSE";
      pause.classList.toggle("is-on", state.paused);
    }
    const speed = q("[data-speed]", hud);
    if (speed) speed.textContent = SPEED_PROFILES[state.speedMode]?.label || "SPEED";
  }

  async function snapScreenshotToClipboard() {
    const hud = q(`#${HUD_ID}`);
    const canvas = q("#gnx-local-full-canvas", hud);
    const status = q("[data-status]", hud);
    if (!canvas) return;
    try {
      const dataUrl = canvas.toDataURL("image/png");
      if (window.nexus?.copyPngToClipboard) {
        await window.nexus.copyPngToClipboard(dataUrl);
        if (status) status.textContent = "GitNexus screenshot copied to clipboard.";
        return;
      }
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(dataUrl);
        if (status) status.textContent = "GitNexus screenshot data URL copied to clipboard.";
        return;
      }
      throw new Error("clipboard bridge unavailable");
    } catch (error) {
      if (status) status.textContent = `Screenshot blocked: ${error.message}`;
    }
  }

  function openDataHud(kind) {
    const hud = q(`#${HUD_ID}`);
    const target = q(`[data-popout='${kind}']`, hud);
    if (!target) return;
    qa("[data-popout]", hud).forEach((panel) => panel.classList.add("is-hidden"));
    target.classList.remove("is-hidden");
  }

  function closeDataHud(button) {
    button?.closest?.("[data-popout]")?.classList.add("is-hidden");
  }

  function tickPhysics(dt) {
    const graph = state.graph;
    if (!graph || state.paused) return;

    const nodes = graph.nodes;
    const edges = graph.edges;
    const byId = graph.byId || new Map(nodes.map((n) => [n.id, n]));
    const simNodes = nodes.slice(0, Math.min(520, nodes.length));
    const mode = state.layoutMode;

    const pull = mode === "force" ? 0.014 : mode === "orbit" ? 0.020 : mode === "organism" ? 0.024 : 0.026;
    const repel = mode === "force" ? 2600 : mode === "orbit" ? 1500 : mode === "poles" ? 2300 : 2100;
    const damping = mode === "force" ? 0.88 : mode === "organism" ? 0.91 : 0.90;

    for (const n of simNodes) {
      if (!visibleNode(n)) continue;
      let tx = n.tx;
      let ty = n.ty;

      if (mode === "orbit") {
        const angle = Math.atan2(n.ty, n.tx) + 0.0022 * dt * (1 + n.cluster * 0.08);
        const r = Math.hypot(n.tx, n.ty);
        tx = Math.cos(angle) * r;
        ty = Math.sin(angle) * r;
      } else if (mode === "circle") {
        const ring = 105 + n.cluster * 88;
        const angle = (hashText(n.id) % 6283) / 1000 + state.lastT * 0.00004;
        tx = Math.cos(angle) * ring;
        ty = Math.sin(angle) * ring;
      } else if (mode === "organism") {
        const h = hashText(n.id);
        const ring = (n.folder ? 92 : 180) + n.cluster * 62 + ((h >> 7) % 70);
        const angle = n.cluster * 1.08 + (h % 6283) / 1000 + Math.sin(state.lastT * 0.00034 + n.phase) * 0.22;
        const strand = Math.sin(state.lastT * 0.00058 + (h % 99)) * (n.folder ? 24 : 56);
        tx = Math.cos(angle) * ring + Math.cos(angle + Math.PI / 2) * strand;
        ty = Math.sin(angle) * ring + Math.sin(angle + Math.PI / 2) * strand;
      } else if (mode === "poles") {
        const h = hashText(n.id);
        const polarity = n.cluster % 2 === 0 ? -1 : 1;
        const poleX = polarity * (180 + n.cluster * 28);
        const laneY = (n.cluster - 2) * 74;
        tx = poleX + Math.sin(state.lastT * 0.00046 + n.phase) * (70 + (h % 35));
        ty = laneY + Math.cos(state.lastT * 0.00036 + (h % 51)) * 92;
      }

      n.vx += (tx - n.x) * pull * dt;
      n.vy += (ty - n.y) * pull * dt;
    }

    for (let i = 0; i < simNodes.length; i++) {
      const a = simNodes[i];
      if (!visibleNode(a)) continue;
      for (let j = i + 1; j < simNodes.length; j++) {
        const b = simNodes[j];
        if (!visibleNode(b)) continue;
        if ((a.repoIndex || 0) !== (b.repoIndex || 0)) continue;
        let dx = a.x - b.x;
        let dy = a.y - b.y;
        let d2 = dx * dx + dy * dy + 0.01;
        if (d2 > 20000) continue;
        const d = Math.sqrt(d2);
        const min = (a.folder || b.folder) ? 22 : 16;
        const f = (repel / d2) * dt;
        dx /= d;
        dy /= d;
        const extra = d < min ? (min - d) * 0.08 * dt : 0;
        a.vx += dx * (f + extra);
        a.vy += dy * (f + extra);
        b.vx -= dx * (f + extra);
        b.vy -= dy * (f + extra);
      }
    }

    for (const e of edges.slice(0, 1400)) {
      const a = byId.get(e.a), b = byId.get(e.b);
      if (!a || !b || !visibleNode(a) || !visibleNode(b)) continue;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) + 0.01;
      const rest = e.type === "contains" ? (a.folder || b.folder ? 80 : 56) : 150;
      const k = (e.weight || 0.2) * 0.012 * dt;
      const f = (d - rest) * k;
      const fx = (dx / d) * f;
      const fy = (dy / d) * f;
      a.vx += fx;
      a.vy += fy;
      b.vx -= fx;
      b.vy -= fy;
    }

    for (const n of simNodes) {
      n.vx *= damping;
      n.vy *= damping;
      n.x += clamp(n.vx, -12, 12) * dt;
      n.y += clamp(n.vy, -12, 12) * dt;
    }
  }

  function updateCamera(dt, profile = SPEED_PROFILES.medium) {
    const ease = profile.ease || 0.08;
    state.target.zoom = clamp(state.target.zoom, 0.08, 9);
    state.camera.x = lerp(state.camera.x, state.target.x, ease);
    state.camera.y = lerp(state.camera.y, state.target.y, ease);
    state.camera.zoom = lerp(state.camera.zoom, state.target.zoom, ease);
    state.camera.rot = lerp(state.camera.rot, state.target.rot, ease);

    state.target.x += state.velocity.x * dt;
    state.target.y += state.velocity.y * dt;
    state.target.rot += state.velocity.rot * dt;
    state.target.zoom += state.velocity.zoom * dt;

    state.velocity.x *= 0.90;
    state.velocity.y *= 0.90;
    state.velocity.rot *= 0.90;
    state.velocity.zoom *= 0.88;

    if (Math.abs(state.velocity.x) < 0.01) state.velocity.x = 0;
    if (Math.abs(state.velocity.y) < 0.01) state.velocity.y = 0;
    if (Math.abs(state.velocity.rot) < 0.00001) state.velocity.rot = 0;
    if (Math.abs(state.velocity.zoom) < 0.00001) state.velocity.zoom = 0;
  }

  function worldProject(n, fit, mini = false) {
    const cam = mini
      ? { x: 0, y: 0, zoom: Math.min(fit.w, fit.h) / 720, rot: state.miniRot }
      : state.camera;

    const ca = Math.cos(cam.rot), sa = Math.sin(cam.rot);
    const x = n.x * ca - n.y * sa;
    const y = n.x * sa + n.y * ca;
    return {
      x: fit.w / 2 + (x + cam.x) * cam.zoom,
      y: fit.h / 2 + (y + cam.y) * cam.zoom
    };
  }

  function edgeEnergy(e, t) {
    return 0.35 + 0.35 * Math.sin(t * 0.004 + (hashText(e.a + e.b) % 628) / 100);
  }

  function nodeColor(n) {
    if (n.compare || n.repoIndex === 1) return COMPARE_TYPE_COLOR[n.kind] || COMPARE_TYPE_COLOR.other;
    return TYPE_COLOR[n.kind] || TYPE_COLOR.other;
  }

  function drawGraph(ctx, w, h, opts = {}) {
    const graph = state.graph || buildGraphFromFiles(buildFallbackFiles());
    const nodes = graph.nodes || [];
    const edges = graph.edges || [];
    const mini = Boolean(opts.mini);
    const t = performance.now();

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, w, h);

    const bg = ctx.createRadialGradient(w * 0.50, h * 0.50, 0, w * 0.50, h * 0.50, Math.max(w, h) * 0.52);
    bg.addColorStop(0, "rgba(0,240,255,0.11)");
    bg.addColorStop(0.28, "rgba(255,170,0,0.055)");
    bg.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);

    const byId = graph.byId || new Map(nodes.map((n) => [n.id, n]));
    const fit = { w, h };

    const hover = state.hover;
    const selected = state.selected;
    const focusId = selected || hover;
    const neighbors = new Set();
    if (focusId) {
      for (const e of edges) {
        if (e.a === focusId) neighbors.add(e.b);
        if (e.b === focusId) neighbors.add(e.a);
      }
    }

    if (state.showEdges) {
      ctx.lineCap = "round";
      for (const e of edges.slice(0, mini ? 1100 : 1800)) {
        const a = byId.get(e.a), b = byId.get(e.b);
        if (!a || !b || !visibleNode(a) || !visibleNode(b)) continue;
        const pa = worldProject(a, fit, mini), pb = worldProject(b, fit, mini);
        const onPath = focusId && (e.a === focusId || e.b === focusId);
        const energy = edgeEnergy(e, t);
        const alpha = onPath ? 0.62 : mini ? 0.12 : 0.14 + energy * 0.07;
        const isTrace = e.type === "trace" || e.type === "pulse";
        const compareEdge = a.compare || b.compare || a.repoIndex === 1 || b.repoIndex === 1;
        ctx.strokeStyle = compareEdge
          ? `rgba(255,95,203,${Math.min(0.50, alpha + 0.04)})`
          : isTrace
          ? `rgba(255,170,0,${alpha})`
          : `rgba(0,240,255,${alpha})`;
        ctx.lineWidth = onPath ? (mini ? 1.2 : 1.8) : (mini ? 0.42 : Math.max(0.48, (e.weight || 0.2) * 1.15));
        ctx.beginPath();
        ctx.moveTo(pa.x, pa.y);
        const mx = (pa.x + pb.x) / 2;
        const my = (pa.y + pb.y) / 2;
        const bend = Math.sin((hashText(e.a + e.b) % 628) / 100) * (mini ? 7 : 18);
        ctx.quadraticCurveTo(mx + bend, my - bend, pb.x, pb.y);
        ctx.stroke();
      }
    }

    const ordered = nodes.filter(visibleNode).slice().sort((a, b) => (a.hot === b.hot ? 0 : a.hot ? 1 : -1));
    for (const n of ordered) {
      const p = worldProject(n, fit, mini);
      if (p.x < -80 || p.y < -80 || p.x > w + 80 || p.y > h + 80) continue;
      const color = n.changed ? COLORS.changed : nodeColor(n);
      const pulse = 1 + Math.sin(t * 0.003 + n.phase) * 0.10;
      const hotBoost = n.hot ? 1.45 : 1;
      const focusBoost = n.id === selected ? 2.05 : n.id === hover ? 1.75 : neighbors.has(n.id) ? 1.30 : 1;
      const base = mini ? 1.8 : 2.35;
      const r = clamp((base + Math.sqrt(n.weight || 1) * (mini ? 0.72 : 0.92)) * pulse * hotBoost * focusBoost, mini ? 1.7 : 2.1, mini ? 8.5 : 16);

      if (!mini && focusId && n.id !== focusId && !neighbors.has(n.id)) {
        ctx.globalAlpha = 0.52;
      } else {
        ctx.globalAlpha = 1;
      }

      ctx.shadowBlur = n.hot || neighbors.has(n.id) || n.id === selected ? (mini ? 18 : 28) : (mini ? 8 : 12);
      ctx.shadowColor = n.id === selected ? COLORS.text : n.changed ? COLORS.changed : n.hot ? "rgba(255,170,0,0.82)" : color;
      ctx.fillStyle = n.changed ? COLORS.changed : (n.hot && !n.compare ? COLORS.amber : color);
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.fill();

      if (n.id === hover || n.id === selected) {
        ctx.shadowBlur = 0;
        ctx.strokeStyle = n.id === selected ? COLORS.text : COLORS.green;
        ctx.lineWidth = mini ? 1 : 2;
        ctx.beginPath();
        ctx.arc(p.x, p.y, r + (mini ? 4 : 7), 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }

    ctx.shadowBlur = 0;

    if (!mini && state.showLabels) {
      ctx.font = "10px Consolas, monospace";
      ctx.textBaseline = "middle";
      const placed = [];
      const labels = ordered
        .filter((n) => n.hot || n.id === selected || n.id === hover || neighbors.has(n.id) || (state.camera.zoom > 1.05 && (n.kind === "core" || n.kind === "py")))
        .slice(0, 120);
      for (const n of labels) {
        const p = worldProject(n, fit, false);
        if (p.x < 0 || p.y < 0 || p.x > w || p.y > h) continue;
        const labelAlpha = clamp((state.camera.zoom - 0.32) / 1.15, 0.12, 1); ctx.globalAlpha = n.id === selected ? 1 : labelAlpha; ctx.fillStyle = n.id === selected ? COLORS.text : neighbors.has(n.id) ? COLORS.green : "rgba(220,250,255,0.78)";
        const labelText = safeText(n.name, "node").slice(0, 44); const labelBox = { x1: p.x + 8, y1: p.y - 13, x2: p.x + 12 + ctx.measureText(labelText).width, y2: p.y + 7 }; if (n.id === selected || n.id === hover || labelAllowed(labelBox, placed || [])) ctx.fillText(labelText, p.x + 10, p.y - 4); ctx.globalAlpha = 1;
      }
    }

    if (mini) {
      ctx.fillStyle = "rgba(220,250,255,0.72)";
      ctx.font = "9px Consolas, monospace";
      ctx.fillText("LOCAL / " + String(state.layoutMode).toUpperCase(), 8, 14);
    }
  }

  function startMini() {
    if (state.miniRaf) cancelAnimationFrame(state.miniRaf);
    const loop = (t) => {
      const canvas = document.getElementById("gnx-local-mini-canvas");
      const fit = fitCanvas(canvas);
      if (fit) {
        const dt = state.lastT ? clamp((t - state.lastT) / 16.67, 0.25, 2.5) : 1;
        state.miniRot += 0.0028 * dt;
        if (!state.fullOpen) {
          const profile = SPEED_PROFILES[state.speedMode] || SPEED_PROFILES.medium;
          tickPhysics(dt * 0.20 * profile.physics);
        }
        drawGraph(fit.ctx, fit.w, fit.h, { mini: true });
      }
      state.miniRaf = requestAnimationFrame(loop);
    };
    state.miniRaf = requestAnimationFrame(loop);
  }

  function ensureHud() {
    let hud = document.getElementById(HUD_ID);
    if (hud) return hud;

    hud = document.createElement("section");
    hud.id = HUD_ID;
    hud.className = "gnx-local-hud is-hidden";
    hud.innerHTML = `
      <div class="gnx-local-top">
        <div class="gnx-local-brand">
          <span class="gnx-local-orb"></span>
          <div>
            <div class="gnx-local-hud-title">GITNEXUS</div>
            <div class="gnx-local-hud-sub">LOCAL GEOMETRY ANALYZER</div>
          </div>
        </div>
        <div class="gnx-local-search-strip">
          <input class="gnx-local-search" type="search" placeholder="Search nodes, files, symbols... Ctrl+K" />
          <input class="gnx-compare-path" type="text" data-compare-path placeholder="Compare local repo path..." />
          <button class="gnx-local-btn" data-compare-load>LOAD</button>
        </div>
        <div class="gnx-local-controls">
        <button class="gnx-local-btn" data-fit>FIT</button>
        <button class="gnx-local-btn" data-zoom-in>+</button>
        <button class="gnx-local-btn" data-zoom-out>-</button>
        <button class="gnx-local-btn" data-turn>TURN</button>
        <button class="gnx-local-btn" data-pause>PAUSE</button>
        <button class="gnx-local-btn is-on" data-edges>EDGES</button>
        <button class="gnx-local-btn is-on" data-labels>LABELS</button>
        <button class="gnx-local-btn" data-filter-mode>MODE ALL</button>
        <button class="gnx-local-btn is-on" data-layout>FORCE</button>
        <button class="gnx-local-btn" data-attractor>ATTRACT</button>
        <button class="gnx-local-btn" data-poles>POLES</button>
        <button class="gnx-local-btn is-on" data-speed>FAST</button>
        <button class="gnx-local-btn" data-snapshot>SNAP</button>
        <button class="gnx-local-btn" data-refresh>REFRESH</button>
        <button class="gnx-local-btn gnx-local-close" data-close>CLOSE</button>
        </div>
      </div>
      <main class="gnx-local-main">
        <aside class="gnx-local-left">
          <h3>EXPLORER</h3>
          <div class="gnx-local-count-grid">
            <div><span>FILES</span><b data-gnx-count="files">--</b></div>
            <div><span>SYMBOLS</span><b data-gnx-count="symbols">--</b></div>
            <div><span>EDGES</span><b data-gnx-count="edges">--</b></div>
            <div><span>SOURCE</span><b data-gnx-source>local</b></div>
          </div>
          <div class="gnx-local-legend" data-category-filters>
            ${CATEGORY_DEFS.map((category) => `
              <button type="button" class="gnx-category-filter is-on" data-category="${category.id}">
                <i style="background:${category.color}"></i><span>${category.label}</span><b data-category-count="${category.id}">--</b>
              </button>
            `).join("")}
          </div>
          <div class="gnx-category-files" data-category-files></div>
          <ol class="gnx-local-top-files" data-top-files></ol>
        </aside>
        <section class="gnx-local-canvas-shell">
          <div class="gnx-local-hints">DRAG = PAN &nbsp;&nbsp; WHEEL = ZOOM &nbsp;&nbsp; ALT-DRAG / SHIFT-WHEEL = ROTATE &nbsp;&nbsp; SPACE = PAUSE</div>
          <canvas id="gnx-local-full-canvas"></canvas>
          <div class="gnx-local-status" data-status>No node selected.</div>
        </section>
        <aside class="gnx-local-right">
          <h3>GEOMETRY ANALYZER</h3>
          <div class="gnx-geometry-panel" data-geometry-panel><div><span>PATTERN</span><b data-geo="pattern">--</b></div><div><span>DENSITY</span><b data-geo="density">--</b></div><div><span>HUBS</span><b data-geo="hubs">--</b></div><div><span>BRIDGE</span><b data-geo="bridge">--</b></div><div><span>BALANCE</span><b data-geo="balance">--</b></div><div><span>ANISOTROPY</span><b data-geo="anisotropy">--</b></div></div>
          <div class="gnx-local-recommend" data-geo="recommendation">Reading local geometry.</div>
          <div class="gnx-geometry-summary" data-geo="summary">Waiting for geometry summary.</div>
          <div class="gnx-side-actions">
            <button class="gnx-local-btn" data-open-top-files>OPEN TOP FILES</button>
            <button class="gnx-local-btn" data-open-diagnostics>OPEN DIAGNOSTICS</button>
            <button class="gnx-local-btn" data-snapshot-side>SNAP SCREENSHOT</button>
          </div>
          <h3>SELECTED NODE</h3>
          <div class="gnx-local-selected" data-selected>No node selected.</div>
        </aside>
        <section class="gnx-popout is-hidden" data-popout="top-files">
          <div class="gnx-popout-head"><strong>TOP FILES</strong><button class="gnx-local-btn" data-popout-close>CLOSE</button></div>
          <ol class="gnx-local-top-files" data-top-files-right></ol>
        </section>
        <section class="gnx-popout is-hidden" data-popout="diagnostics">
          <div class="gnx-popout-head"><strong>DIAGNOSTIC REPORTS</strong><button class="gnx-local-btn" data-popout-close>CLOSE</button></div>
          <div class="gnx-diagnostics" data-diagnostics></div>
        </section>
      </main>
      <footer class="gnx-local-foot">
        <span>Evidence only.</span>
        <span data-fps>FPS --</span>
        <span>No NexusCell policy change.</span>
        <span>No shell execution from model output.</span>
      </footer>
    `;
    document.body.appendChild(hud);

    q("[data-close]", hud).addEventListener("click", closeHud);
    q("[data-fit]", hud).addEventListener("click", fitFull);
    q("[data-zoom-in]", hud).addEventListener("click", () => { zoomAroundCenter(1.18); });
    q("[data-zoom-out]", hud).addEventListener("click", () => { zoomAroundCenter(1 / 1.18); });
    q("[data-turn]", hud).addEventListener("click", () => { turnGraph(); });
    q("[data-pause]", hud).addEventListener("click", () => { togglePause(); });
    q("[data-snapshot]", hud).addEventListener("click", snapScreenshotToClipboard);
    q("[data-snapshot-side]", hud).addEventListener("click", snapScreenshotToClipboard);
    q("[data-open-top-files]", hud).addEventListener("click", () => openDataHud("top-files"));
    q("[data-open-diagnostics]", hud).addEventListener("click", () => openDataHud("diagnostics"));
    qa("[data-popout-close]", hud).forEach((button) => button.addEventListener("click", () => closeDataHud(button)));
    q("[data-refresh]", hud).addEventListener("click", async () => {
      await loadGraph(true);
      fitFull();
    });
    q("[data-edges]", hud).addEventListener("click", (e) => {
      state.showEdges = !state.showEdges;
      e.currentTarget.classList.toggle("is-on", state.showEdges);
    });
    q("[data-labels]", hud).addEventListener("click", (e) => {
      state.showLabels = !state.showLabels;
      e.currentTarget.classList.toggle("is-on", state.showLabels);
    });
    q("[data-filter-mode]", hud).addEventListener("click", (e) => {
      const order = ["all", "hot", "changed", "core"];
      const start = order.indexOf(state.filterMode);
      for (let offset = 1; offset <= order.length; offset++) {
        const candidate = order[(start + offset + order.length) % order.length];
        if (candidate === "all" || countVisibleForMode(candidate) > 0) {
          setFilterMode(candidate, e.currentTarget);
          return;
        }
      }
      setFilterMode("all", e.currentTarget);
    });
    qa("[data-category]", hud).forEach((button) => {
      button.addEventListener("click", () => {
        const category = button.getAttribute("data-category");
        if (!category) return;
        const currentlyOn = state.activeCategories[category] !== false;
        const onCount = Object.values(state.activeCategories).filter(Boolean).length;
        if (currentlyOn && onCount <= 1) return;
        state.activeCategories[category] = !currentlyOn;
        button.classList.toggle("is-on", state.activeCategories[category] !== false);
        if (countVisibleForMode(state.filterMode) === 0) setFilterMode("all", q("[data-filter-mode]", hud));
        updateCategoryPanel();
        updateTopFiles();
        state.analyzer = analyzeGeometry(state.graph);
        updateAnalyzerPanel();
        fitFull();
      });
    });
    q("[data-layout]", hud).addEventListener("click", (e) => {
      setLayoutMode("force");
    });
    q("[data-attractor]", hud).addEventListener("click", () => {
      setLayoutMode("organism");
    });
    q("[data-poles]", hud).addEventListener("click", () => {
      setLayoutMode("poles");
    });
    q("[data-speed]", hud).addEventListener("click", (e) => {
      const index = SPEED_ORDER.indexOf(state.speedMode);
      state.speedMode = SPEED_ORDER[(index + 1 + SPEED_ORDER.length) % SPEED_ORDER.length];
      updateControlStates();
    });
    q(".gnx-local-search", hud).addEventListener("input", (e) => {
      state.search = e.currentTarget.value || "";
      const hit = firstSearchHit();
      if (hit) focusNode(hit, false);
    });
    q("[data-compare-load]", hud).addEventListener("click", async () => {
      const input = q("[data-compare-path]", hud);
      const localPath = input?.value?.trim();
      if (!localPath) {
        const status = q("[data-status]", hud);
        if (status) status.textContent = "Enter a local repository path to compare.";
        return;
      }
      await loadCompareGraph(localPath);
    });

    const canvas = q("#gnx-local-full-canvas", hud);
    canvas.addEventListener("pointerdown", (ev) => {
      canvas.setPointerCapture(ev.pointerId);
      state.drag = { x: ev.clientX, y: ev.clientY, mode: ev.altKey ? "rotate" : "pan", moved: false };
      state.velocity.x = 0;
      state.velocity.y = 0;
      state.velocity.rot = 0;
      ev.preventDefault();
    });
    canvas.addEventListener("pointermove", (ev) => {
      if (!state.drag) {
        pickNode(ev, true);
        return;
      }
      const dx = ev.clientX - state.drag.x;
      const dy = ev.clientY - state.drag.y;
      state.drag.x = ev.clientX;
      state.drag.y = ev.clientY;
      if (Math.abs(dx) + Math.abs(dy) > 2) state.drag.moved = true;
      if (state.drag.mode === "rotate" || ev.altKey) {
        const delta = dx * 0.008;
        state.target.rot += delta;
        state.velocity.rot = delta * 0.08;
      } else {
        const deltaX = dx / Math.max(0.1, state.target.zoom);
        const deltaY = dy / Math.max(0.1, state.target.zoom);
        state.target.x += deltaX;
        state.target.y += deltaY;
        state.velocity.x = deltaX * 0.10;
        state.velocity.y = deltaY * 0.10;
      }
      ev.preventDefault();
    });
    canvas.addEventListener("pointerup", (ev) => {
      const moved = state.drag?.moved;
      state.drag = null;
      try { canvas.releasePointerCapture(ev.pointerId); } catch {}
      if (!moved) pickNode(ev, false);
    });
    canvas.addEventListener("pointerleave", () => { state.drag = null; });
    canvas.addEventListener("wheel", (ev) => {
      if (ev.shiftKey) {
        const delta = ev.deltaY * -0.002;
        state.target.rot += delta;
        state.velocity.rot = delta * 0.08;
      } else {
        const factor = Math.exp(-ev.deltaY * 0.001);
        zoomAtEvent(ev, factor);
      }
      ev.preventDefault();
    }, { passive: false });
    canvas.addEventListener("dblclick", (ev) => {
      const n = pickNode(ev, false);
      if (n) focusNode(n, true);
      if (!n) fitFull();
    });

    return hud;
  }

  function updateHudStats() {
    const g = state.graph;
    const files = g?.counts?.files ?? 0;
    const symbols = g?.counts?.symbols ?? 0;
    const edges = g?.counts?.edges ?? 0;
    qa("[data-gnx-count='files']").forEach((n) => { n.textContent = String(files); });
    qa("[data-gnx-count='symbols']").forEach((n) => { n.textContent = String(symbols); });
    qa("[data-gnx-count='edges']").forEach((n) => { n.textContent = String(edges); });
    qa("[data-gnx-source]").forEach((n) => { n.textContent = safeText(g?.source || "local").slice(0, 14); });
  }

  function updateTopFiles() {
    const graph = state.graph;
    if (!graph) return;
    const files = visibleFileNodes(graph)
      .sort((a, b) => (b.degree + b.weight) - (a.degree + a.weight))
      .slice(0, 28);

    function fill(sel) {
      qa(sel).forEach((list) => {
        list.innerHTML = files.map((n, i) =>
          `<li data-node-id="${encodeURIComponent(n.id)}"><span>${String(i + 1).padStart(2, "0")}</span><b>${safeText(n.path).slice(0, 52)}</b><em>${Math.round((n.degree || 0) + (n.weight || 1))}</em></li>`
        ).join("");
        qa("li", list).forEach((li) => {
          li.addEventListener("click", () => {
            const id = decodeURIComponent(li.getAttribute("data-node-id") || "");
            const node = state.graph?.byId?.get(id);
            if (node) focusNode(node, true);
          });
        });
      });
    }
    fill("[data-top-files]");
    fill("[data-top-files-right]");
    updateCategoryPanel();
  }

  function updateCategoryPanel() {
    const graph = state.graph;
    if (!graph) return;
    const allFiles = (graph.nodes || []).filter((n) => !n.folder && n.id !== "nexus-gate");
    CATEGORY_DEFS.forEach((category) => {
      const count = allFiles.filter((n) => KIND_CATEGORY.get(n.kind) === category.id).length;
      qa(`[data-category-count='${category.id}']`).forEach((node) => { node.textContent = String(count); });
      qa(`[data-category='${category.id}']`).forEach((button) => {
        button.classList.toggle("is-on", state.activeCategories[category.id] !== false);
      });
    });
    const panel = q("[data-category-files]");
    if (!panel) return;
    panel.innerHTML = CATEGORY_DEFS.map((category) => {
      const files = allFiles
        .filter((n) => KIND_CATEGORY.get(n.kind) === category.id)
        .sort((a, b) => scoreNode(b) - scoreNode(a))
        .slice(0, 18);
      return `
        <section data-category-file-section="${category.id}" class="${state.activeCategories[category.id] === false ? "is-off" : ""}">
          <h4><i style="background:${category.color}"></i>${category.label}<span>${files.length}</span></h4>
          <ol>${files.map((node, i) => diagnosticRow({ node, score: scoreNode(node) }, i)).join("")}</ol>
        </section>
      `;
    }).join("");
    qa("li[data-node-id]", panel).forEach((li) => {
      li.addEventListener("click", () => {
        const id = decodeURIComponent(li.getAttribute("data-node-id") || "");
        const node = state.graph?.byId?.get(id);
        if (node) focusNode(node, true);
      });
    });
  }

  function fitFull() {
    const graph = state.graph;
    if (!graph || !graph.nodes.length) return;
    const canvas = document.getElementById("gnx-local-full-canvas");
    const fit = fitCanvas(canvas);
    if (!fit) return;

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    const nodes = visibleNodes(graph);
    if (!nodes.length) {
      state.search = "";
      const search = q(".gnx-local-search");
      if (search) search.value = "";
      state.filterMode = "all";
      state.coreOnly = false;
      setAllCategories(true);
      const filterButton = q("[data-filter-mode]");
      if (filterButton) filterButton.textContent = FILTER_LABELS.all;
      graph.nodes.forEach((n) => {
        minX = Math.min(minX, n.x);
        maxX = Math.max(maxX, n.x);
        minY = Math.min(minY, n.y);
        maxY = Math.max(maxY, n.y);
      });
    } else {
      nodes.forEach((n) => {
      minX = Math.min(minX, n.x);
      maxX = Math.max(maxX, n.x);
      minY = Math.min(minY, n.y);
      maxY = Math.max(maxY, n.y);
      });
    }
    if (!Number.isFinite(minX) || !Number.isFinite(maxX) || !Number.isFinite(minY) || !Number.isFinite(maxY)) {
      minX = -220; maxX = 220; minY = -180; maxY = 180;
    }
    const bw = Math.max(1, maxX - minX);
    const bh = Math.max(1, maxY - minY);
    state.target.zoom = clamp(Math.min(fit.w / bw, fit.h / bh) * 0.78, 0.08, 4);
    state.target.x = -(minX + maxX) / 2;
    state.target.y = -(minY + maxY) / 2;
    state.target.rot = 0;
  }

  function zoomAroundCenter(factor) {
    state.target.zoom = clamp(state.target.zoom * factor, 0.08, 9);
    state.velocity.zoom = (factor - 1) * 0.012;
  }

  function zoomAtEvent(ev, factor) {
    const oldZoom = state.target.zoom;
    const newZoom = clamp(oldZoom * factor, 0.08, 9);
    state.target.zoom = newZoom;
    state.velocity.zoom = (factor - 1) * 0.012;
  }

  function screenToNearestNode(ev) {
    const graph = state.graph;
    if (!graph) return null;
    const canvas = document.getElementById("gnx-local-full-canvas");
    const fit = fitCanvas(canvas);
    if (!fit) return null;
    const rect = canvas.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const my = ev.clientY - rect.top;

    let best = null;
    let bestD = 999999;
    for (const n of graph.nodes) {
      if (!visibleNode(n)) continue;
      const p = worldProject(n, fit, false);
      const d = Math.hypot(p.x - mx, p.y - my);
      if (d < bestD) {
        bestD = d;
        best = n;
      }
    }
    if (best && bestD < 24) return best;
    return null;
  }

  function pickNode(ev, hoverOnly) {
    const node = screenToNearestNode(ev);
    if (hoverOnly) {
      state.hover = node ? node.id : null;
      return node;
    }
    if (node) {
      state.selected = node.id;
      const text = `${node.path} | kind=${node.kind} | degree=${node.degree} | weight=${Math.round(node.weight || 1)}`;
      const sel = q("[data-selected]");
      const status = q("[data-status]");
      if (sel) sel.textContent = text;
      if (status) status.textContent = "Selected: " + text;
      state.analyzer = analyzeGeometry(state.graph);
      updateAnalyzerPanel();
    } else {
      state.selected = null;
      const sel = q("[data-selected]");
      const status = q("[data-status]");
      if (sel) sel.textContent = "No node selected.";
      if (status) status.textContent = "No node selected.";
      state.analyzer = analyzeGeometry(state.graph);
      updateAnalyzerPanel();
    }
    return node;
  }

  function focusNode(node, tight) {
    state.selected = node.id;
    state.target.x = -node.x;
    state.target.y = -node.y;
    if (tight) state.target.zoom = clamp(state.target.zoom * 1.5, 0.45, 3.4);
    const text = `${node.path} | kind=${node.kind} | degree=${node.degree} | weight=${Math.round(node.weight || 1)}`;
    const sel = q("[data-selected]");
    const status = q("[data-status]");
    if (sel) sel.textContent = text;
    if (status) status.textContent = "Focused: " + text;
    state.analyzer = analyzeGeometry(state.graph);
    updateAnalyzerPanel();
  }

  function firstSearchHit() {
    const graph = state.graph;
    if (!graph) return null;
    const s = String(state.search || "").toLowerCase().trim();
    if (!s) return null;
    return graph.nodes.find((n) => String(n.path).toLowerCase().includes(s) || String(n.name).toLowerCase().includes(s)) || null;
  }

  function startFull() {
    if (state.fullRaf) cancelAnimationFrame(state.fullRaf);
    state.lastT = performance.now();
    const loop = (t) => {
      if (!state.fullOpen) {
        state.fullRaf = 0;
        return;
      }

      const profile = SPEED_PROFILES[state.speedMode] || SPEED_PROFILES.fast; const frameMs = 1000 / profile.fps; if (t - (state.lastDrawT || 0) < frameMs) { state.fullRaf = requestAnimationFrame(loop); return; } state.lastDrawT = t; const dt = clamp((t - state.lastT) / 16.67, 0.25, 2.5);
      state.lastT = t;
      state.frameCount += 1;
      if (state.frameCount % 24 === 0) {
        state.fps = Math.round(60 / dt);
        const fps = q("[data-fps]");
        if (fps) fps.textContent = `FPS ${state.fps}`;
      }

      tickPhysics(dt * profile.physics); if (performance.now() - (state.analyzerT || 0) > 900) { state.analyzer = analyzeGeometry(state.graph); state.analyzerT = performance.now(); updateAnalyzerPanel(); }
      updateCamera(dt, profile);

      const canvas = document.getElementById("gnx-local-full-canvas");
      const fit = fitCanvas(canvas);
      if (fit) drawGraph(fit.ctx, fit.w, fit.h, { mini: false });
      state.fullRaf = requestAnimationFrame(loop);
    };
    state.fullRaf = requestAnimationFrame(loop);
  }

  function openHud() {
    ensureHud();
    const hud = document.getElementById(HUD_ID);
    hud.classList.remove("is-hidden");
    state.fullOpen = true;
    updateControlStates();
    if (!state.graphLoaded) {
      loadGraph().then(() => { updateHudStats(); updateTopFiles(); fitFull(); });
    } else {
      updateHudStats();
      updateTopFiles();
      fitFull();
    }
    startFull();
  }

  function closeHud() {
    const hud = document.getElementById(HUD_ID);
    if (hud) hud.classList.add("is-hidden");
    state.fullOpen = false;
    if (state.fullRaf) {
      cancelAnimationFrame(state.fullRaf);
      state.fullRaf = 0;
    }
  }

  function scheduleDock() {
    if (state.resizeTimer) clearTimeout(state.resizeTimer);
    state.resizeTimer = setTimeout(() => ensureMiniDock(), 100);
  }

  function bindKeys() {
    if (window.__gitnexusLocalHudKeysV053) return;
    window.__gitnexusLocalHudKeysV053 = true;

    window.addEventListener("keydown", (ev) => {
      const hud = document.getElementById(HUD_ID);
      const open = hud && !hud.classList.contains("is-hidden");
      if (ev.ctrlKey && String(ev.key).toLowerCase() === "k") {
        if (open) {
          q(".gnx-local-search", hud)?.focus();
          ev.preventDefault();
        }
        return;
      }
      if (!open) return;

      const key = String(ev.key).toLowerCase();
      const pan = 34 / Math.max(0.1, state.target.zoom);

      if (key === "escape") { closeHud(); ev.preventDefault(); }
      if (key === " ") { togglePause(); ev.preventDefault(); }
      if (key === "f") { const n = state.selected && state.graph?.byId?.get(state.selected); if (n) focusNode(n, true); ev.preventDefault(); }
      if (key === "r") { fitFull(); ev.preventDefault(); }
      if (key === "m") { const btn = q("[data-filter-mode]"); if (btn) btn.click(); ev.preventDefault(); }
      if (key === "g") { const btn = q("[data-speed]"); if (btn) btn.click(); ev.preventDefault(); }
      if (key === "[" ) { state.target.rot -= 0.14; ev.preventDefault(); }
      if (key === "]" ) { state.target.rot += 0.14; ev.preventDefault(); }
      if (key === "+" || key === "=") { zoomAroundCenter(1.12); ev.preventDefault(); }
      if (key === "-" || key === "_") { zoomAroundCenter(1 / 1.12); ev.preventDefault(); }
      if (key === "arrowleft" || key === "a") { state.target.x += pan; ev.preventDefault(); }
      if (key === "arrowright" || key === "d") { state.target.x -= pan; ev.preventDefault(); }
      if (key === "arrowup" || key === "w") { state.target.y += pan; ev.preventDefault(); }
      if (key === "arrowdown" || key === "s") { state.target.y -= pan; ev.preventDefault(); }
    });
  }

  function boot() {
    ensureMiniDock();
    ensureHud();
    if (!state.graphLoaded) loadGraph().then(() => { updateHudStats(); updateTopFiles(); });
    startMini();
    bindKeys();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener("load", boot);
  window.addEventListener("resize", scheduleDock);
  window.nexusOpenGitNexus = openHud;
  window.nexusCloseGitNexus = closeHud;
  window.nexusGitNexusRefresh = () => loadGraph(true);
})();
