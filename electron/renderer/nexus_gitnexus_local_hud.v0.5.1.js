(() => {
  const VERSION = "v0.5.1";
  const MINI_ID = "gitnexus-core-left-dock";
  const HUD_ID = "gitnexus-local-hud";
  const STORE_KEY = "__nexusGitNexusLocalHudV051";

  const state = window[STORE_KEY] || (window[STORE_KEY] = {
    miniRaf: 0,
    fullRaf: 0,
    resizeTimer: 0,
    graph: null,
    graphLoaded: false,
    fullOpen: false,
    drag: null,
    view: { x: 0, y: 0, zoom: 1, rot: 0 },
    miniRot: 0,
    showEdges: true,
    showLabels: true,
    coreOnly: false,
    selected: null,
    search: ""
  });

  const COLORS = {
    bg: "#020712",
    cyan: "#55f7ff",
    cyan2: "#00eaff",
    green: "#7dff4d",
    amber: "#ffaa00",
    violet: "#a855f7",
    blue: "#5b7cff",
    dim: "rgba(85,247,255,0.18)",
    text: "#dffcff"
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
    other: "#8aa0aa"
  };

  function q(sel, root = document) { return root.querySelector(sel); }
  function qa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

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
    const left = Math.max(4, rail.left);
    const width = Math.max(260, Math.min(405, rail.width || (rail.right - rail.left)));
    const top = Math.min((rail.bottom || 360) + 10, footerTop - 235);
    const height = Math.max(215, footerTop - top - 10);
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
    dock.className = "gnx-local-mini-dock";
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

    function add(path, weight = 1) {
      const p = safeText(path).replace(/\\/g, "/");
      if (!p || p.length < 2) return;
      if (p.includes(".bak_") || p.endsWith(".bak") || p.includes("__pycache__")) return;
      if (seen.has(p)) return;
      seen.add(p);
      files.push({ path: p, weight: Math.max(1, Number(weight) || 1) });
    }

    function walk(x, depth = 0) {
      if (!x || depth > 5) return;
      if (Array.isArray(x)) {
        for (const item of x.slice(0, 1200)) walk(item, depth + 1);
        return;
      }
      if (typeof x !== "object") return;

      const pathKeys = ["path", "file", "filePath", "name", "id", "source", "target"];
      for (const key of pathKeys) {
        const v = x[key];
        if (typeof v === "string" && /[\/\\.]|nexus_gate|electron|reports|state|ledger|docs|tests/.test(v)) {
          add(v, x.weight || x.count || x.imports || x.score || 1);
        }
      }

      const arrays = ["nodes", "files", "changed_files", "top_imported_files", "relationships", "edges", "affected_files"];
      for (const key of arrays) {
        if (Array.isArray(x[key])) walk(x[key], depth + 1);
      }

      if (depth < 2) {
        for (const k of Object.keys(x).slice(0, 40)) walk(x[k], depth + 1);
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
      "nexus_gate/geometric_memory/score.py",
      "nexus_gate/adapters/local_demo.py",
      "nexus_gate/nexus_cell/plan.py",
      "nexus_gate/receptors/registry.py",
      "nexus_gate/nexus_cell/context_bridge.py",
      "nexus_gate/nn_router/contract.py",
      "nexus_gate/bridge/runtime.py",
      "nexus_gate/self_healing/engine.py",
      "nexus_gate/nexus_cell/policy.py",
      "electron/renderer/index.html",
      "electron/renderer/renderer.js",
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
      roots.forEach((p, i) => files.push({ path: p.replace(/(\.[a-z0-9]+)$/i, "_" + round + "$1"), weight: 1 + ((i + round) % 9) }));
    }
    return files;
  }

  function buildGraphFromFiles(files) {
    if (!files || files.length < 12) files = buildFallbackFiles();

    const nodes = [];
    const edges = [];
    const byPath = new Map();

    function addNode(id, path, kind, weight) {
      if (byPath.has(id)) return byPath.get(id);
      const h = hashText(id);
      const clusterMap = { py: 0, core: 0, js: 1, ts: 1, tsx: 1, jsx: 1, test: 2, state: 3, report: 3, doc: 4, other: 5 };
      const cluster = clusterMap[kind] ?? 5;
      const golden = Math.PI * (3 - Math.sqrt(5));
      const idx = nodes.length + 1;
      const baseR = 85 + cluster * 52 + Math.sqrt(idx) * 12;
      const angle = idx * golden + cluster * 0.7 + (h % 360) * Math.PI / 1800;
      const node = {
        id,
        path,
        name: path.split("/").filter(Boolean).pop() || path,
        kind,
        cluster,
        weight: Math.max(1, Number(weight) || 1),
        x: Math.cos(angle) * baseR + ((h & 255) - 128) * 0.25,
        y: Math.sin(angle) * baseR + (((h >> 8) & 255) - 128) * 0.25,
        hot: false
      };
      nodes.push(node);
      byPath.set(id, node);
      return node;
    }

    const root = addNode("nexus-gate", "nexus-gate", "core", 24);
    files.slice(0, 900).forEach((f) => {
      const path = safeText(f.path || f, "unknown");
      const kind = classify(path);
      const n = addNode(path, path, kind, f.weight || 1);
      const parts = path.split("/").filter(Boolean);
      const folder = parts.length > 1 ? parts[0] + "/" : "root/";
      const folderNode = addNode("folder:" + folder, folder, classify(folder), 8);
      edges.push({ a: root.id, b: folderNode.id, type: "contains", weight: 0.4 });
      edges.push({ a: folderNode.id, b: n.id, type: "contains", weight: 0.65 });
    });

    const top = nodes.filter((n) => !n.id.startsWith("folder:") && n.id !== root.id);
    top.forEach((n, i) => {
      const h = hashText(n.id);
      const j = h % Math.max(1, top.length);
      if (top[j] && top[j] !== n && (i % 2 === 0 || n.kind === top[j].kind)) {
        edges.push({ a: n.id, b: top[j].id, type: n.kind === top[j].kind ? "same-kind" : "synthetic", weight: 0.18 });
      }
      if (i % 7 === 0 && top[i + 3]) edges.push({ a: n.id, b: top[i + 3].id, type: "trace", weight: 0.12 });
    });

    nodes.sort((a, b) => b.weight - a.weight);
    nodes.slice(0, Math.max(12, Math.floor(nodes.length * 0.08))).forEach((n) => { n.hot = true; });
    return { nodes, edges, counts: { files: files.length, symbols: nodes.length, edges: edges.length } };
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

  async function loadGraph() {
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
    state.graphLoaded = true;
    updateHudStats();
  }

  function updateHudStats() {
    const g = state.graph;
    const files = g?.counts?.files ?? 0;
    const symbols = g?.counts?.symbols ?? 0;
    const edges = g?.counts?.edges ?? 0;
    qa("[data-gnx-count='files']").forEach((n) => { n.textContent = String(files); });
    qa("[data-gnx-count='symbols']").forEach((n) => { n.textContent = String(symbols); });
    qa("[data-gnx-count='edges']").forEach((n) => { n.textContent = String(edges); });
    qa("[data-gnx-source]").forEach((n) => { n.textContent = safeText(g?.source || "local"); });
  }

  function drawGraph(ctx, w, h, opts) {
    const graph = state.graph || buildGraphFromFiles(buildFallbackFiles());
    const nodes = graph.nodes || [];
    const edges = graph.edges || [];
    const mini = opts?.mini;
    const t = performance.now() * 0.001;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, w, h);

    const bg = ctx.createRadialGradient(w * 0.50, h * 0.50, 0, w * 0.50, h * 0.50, Math.max(w, h) * 0.52);
    bg.addColorStop(0, "rgba(0,240,255,0.10)");
    bg.addColorStop(0.40, "rgba(255,170,0,0.05)");
    bg.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);

    const view = mini
      ? { x: 0, y: 0, zoom: Math.min(w, h) / 760, rot: state.miniRot }
      : state.view;

    const search = String(state.search || "").toLowerCase().trim();

    function visible(n) {
      if (state.coreOnly && !(n.kind === "core" || n.kind === "py")) return false;
      if (search && !String(n.path).toLowerCase().includes(search) && !String(n.name).toLowerCase().includes(search)) return false;
      return true;
    }

    function project(n) {
      const zr = view.zoom || 1;
      const a = (view.rot || 0);
      const ca = Math.cos(a), sa = Math.sin(a);
      const x = n.x * ca - n.y * sa;
      const y = n.x * sa + n.y * ca;
      return {
        x: w / 2 + (x + view.x) * zr,
        y: h / 2 + (y + view.y) * zr
      };
    }

    const visibleNodes = nodes.filter(visible);
    const byId = new Map(nodes.map((n) => [n.id, n]));

    if (state.showEdges) {
      ctx.lineCap = "round";
      edges.forEach((e) => {
        const a = byId.get(e.a), b = byId.get(e.b);
        if (!a || !b || !visible(a) || !visible(b)) return;
        const pa = project(a), pb = project(b);
        const color = e.type === "trace" ? "rgba(255,170,0,0.18)" : "rgba(0,240,255,0.11)";
        ctx.strokeStyle = color;
        ctx.lineWidth = mini ? 0.55 : Math.max(0.5, e.weight * 1.4);
        ctx.beginPath();
        ctx.moveTo(pa.x, pa.y);
        const mx = (pa.x + pb.x) / 2;
        const my = (pa.y + pb.y) / 2;
        const bend = Math.sin(hashText(e.a + e.b) % 628 / 100) * (mini ? 8 : 18);
        ctx.quadraticCurveTo(mx + bend, my - bend, pb.x, pb.y);
        ctx.stroke();
      });
    }

    visibleNodes.forEach((n) => {
      const p = project(n);
      if (p.x < -60 || p.y < -60 || p.x > w + 60 || p.y > h + 60) return;
      const base = mini ? 1.9 : 2.4;
      const r = clamp(base + Math.sqrt(n.weight || 1) * (mini ? 0.85 : 1.05), mini ? 1.8 : 2.2, mini ? 7 : 13);
      const color = TYPE_COLOR[n.kind] || TYPE_COLOR.other;
      ctx.shadowBlur = n.hot ? (mini ? 16 : 22) : (mini ? 8 : 11);
      ctx.shadowColor = n.hot ? "rgba(255,170,0,0.75)" : color;
      ctx.fillStyle = n.hot ? COLORS.amber : color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.fill();

      if (!mini && state.selected === n.id) {
        ctx.shadowBlur = 0;
        ctx.strokeStyle = COLORS.text;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(p.x, p.y, r + 6, 0, Math.PI * 2);
        ctx.stroke();
      }
    });

    ctx.shadowBlur = 0;

    if (!mini && state.showLabels) {
      ctx.font = "10px Consolas, monospace";
      ctx.textBaseline = "middle";
      ctx.fillStyle = "rgba(220,250,255,0.78)";
      visibleNodes
        .filter((n) => n.hot || (state.view.zoom > 0.9 && (n.kind === "core" || n.kind === "py")))
        .slice(0, 85)
        .forEach((n) => {
          const p = project(n);
          if (p.x < 0 || p.y < 0 || p.x > w || p.y > h) return;
          ctx.fillText(safeText(n.name, "node").slice(0, 42), p.x + 9, p.y - 3);
        });
    }

    if (mini) {
      ctx.fillStyle = "rgba(220,250,255,0.72)";
      ctx.font = "9px Consolas, monospace";
      ctx.fillText("LOCAL", 8, 14);
    }
  }

  function startMini() {
    if (state.miniRaf) cancelAnimationFrame(state.miniRaf);
    const loop = () => {
      const canvas = document.getElementById("gnx-local-mini-canvas");
      const fit = fitCanvas(canvas);
      if (fit) {
        state.miniRot += 0.0035;
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
            <div class="gnx-local-hud-sub">NEXUSGATE LOCAL CODEGRAPH</div>
          </div>
        </div>
        <input class="gnx-local-search" type="search" placeholder="Search nodes, files, symbols... Ctrl+K" />
        <button class="gnx-local-btn" data-fit>FIT</button>
        <button class="gnx-local-btn" data-zoom-in>+</button>
        <button class="gnx-local-btn" data-zoom-out>-</button>
        <button class="gnx-local-btn" data-turn>TURN</button>
        <button class="gnx-local-btn is-on" data-edges>EDGES</button>
        <button class="gnx-local-btn is-on" data-labels>LABELS</button>
        <button class="gnx-local-btn" data-core>CORE</button>
        <button class="gnx-local-btn gnx-local-close" data-close>CLOSE</button>
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
          <div class="gnx-local-legend">
            <span><i style="background:#55f7ff"></i>Python/Core</span>
            <span><i style="background:#ffaa00"></i>Electron/UI</span>
            <span><i style="background:#a855f7"></i>Tests</span>
            <span><i style="background:#7dff4d"></i>State/Reports</span>
            <span><i style="background:#5b7cff"></i>Docs</span>
          </div>
          <ol class="gnx-local-top-files" data-top-files></ol>
        </aside>
        <section class="gnx-local-canvas-shell">
          <div class="gnx-local-hints">DRAG = PAN &nbsp;&nbsp; WHEEL = ZOOM &nbsp;&nbsp; ALT-DRAG / SHIFT-WHEEL = ROTATE</div>
          <canvas id="gnx-local-full-canvas"></canvas>
          <div class="gnx-local-status" data-status>No node selected.</div>
        </section>
        <aside class="gnx-local-right">
          <h3>RECOMMENDATION</h3>
          <div class="gnx-local-recommend">Local visual codegraph. Inspect affected files before durable mutation.</div>
          <h3>TOP FILES</h3>
          <ol class="gnx-local-top-files" data-top-files-right></ol>
          <h3>SELECTED NODE</h3>
          <div class="gnx-local-selected" data-selected>No node selected.</div>
        </aside>
      </main>
      <footer class="gnx-local-foot">
        <span>Evidence only.</span>
        <span>No NexusCell policy change.</span>
        <span>No shell execution from model output.</span>
      </footer>
    `;
    document.body.appendChild(hud);

    q("[data-close]", hud).addEventListener("click", closeHud);
    q("[data-fit]", hud).addEventListener("click", fitFull);
    q("[data-zoom-in]", hud).addEventListener("click", () => { state.view.zoom *= 1.18; });
    q("[data-zoom-out]", hud).addEventListener("click", () => { state.view.zoom /= 1.18; });
    q("[data-turn]", hud).addEventListener("click", () => { state.view.rot += Math.PI / 10; });
    q("[data-edges]", hud).addEventListener("click", (e) => {
      state.showEdges = !state.showEdges;
      e.currentTarget.classList.toggle("is-on", state.showEdges);
    });
    q("[data-labels]", hud).addEventListener("click", (e) => {
      state.showLabels = !state.showLabels;
      e.currentTarget.classList.toggle("is-on", state.showLabels);
    });
    q("[data-core]", hud).addEventListener("click", (e) => {
      state.coreOnly = !state.coreOnly;
      e.currentTarget.classList.toggle("is-on", state.coreOnly);
    });
    q(".gnx-local-search", hud).addEventListener("input", (e) => { state.search = e.currentTarget.value || ""; });

    const canvas = q("#gnx-local-full-canvas", hud);
    canvas.addEventListener("pointerdown", (ev) => {
      canvas.setPointerCapture(ev.pointerId);
      state.drag = { x: ev.clientX, y: ev.clientY, mode: ev.altKey ? "rotate" : "pan" };
      ev.preventDefault();
    });
    canvas.addEventListener("pointermove", (ev) => {
      if (!state.drag) {
        pickNode(ev);
        return;
      }
      const dx = ev.clientX - state.drag.x;
      const dy = ev.clientY - state.drag.y;
      state.drag.x = ev.clientX;
      state.drag.y = ev.clientY;
      if (state.drag.mode === "rotate" || ev.altKey) {
        state.view.rot += dx * 0.008;
      } else {
        state.view.x += dx / Math.max(0.1, state.view.zoom);
        state.view.y += dy / Math.max(0.1, state.view.zoom);
      }
      ev.preventDefault();
    });
    canvas.addEventListener("pointerup", (ev) => {
      state.drag = null;
      try { canvas.releasePointerCapture(ev.pointerId); } catch {}
    });
    canvas.addEventListener("pointerleave", () => { state.drag = null; });
    canvas.addEventListener("wheel", (ev) => {
      if (ev.shiftKey) {
        state.view.rot += ev.deltaY * -0.002;
      } else {
        const factor = Math.exp(-ev.deltaY * 0.001);
        state.view.zoom = clamp(state.view.zoom * factor, 0.08, 9);
      }
      ev.preventDefault();
    }, { passive: false });
    canvas.addEventListener("click", pickNode);

    return hud;
  }

  function updateTopFiles() {
    const graph = state.graph;
    if (!graph) return;
    const files = graph.nodes
      .filter((n) => !n.id.startsWith("folder:") && n.id !== "nexus-gate")
      .sort((a, b) => b.weight - a.weight)
      .slice(0, 28);

    function fill(sel) {
      qa(sel).forEach((list) => {
        list.innerHTML = files.map((n, i) =>
          `<li><span>${String(i + 1).padStart(2, "0")}</span><b>${safeText(n.path).slice(0, 52)}</b><em>${Math.round(n.weight || 1)}</em></li>`
        ).join("");
      });
    }
    fill("[data-top-files]");
    fill("[data-top-files-right]");
  }

  function fitFull() {
    const graph = state.graph;
    if (!graph || !graph.nodes.length) return;
    const canvas = document.getElementById("gnx-local-full-canvas");
    const fit = fitCanvas(canvas);
    if (!fit) return;

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    graph.nodes.forEach((n) => {
      minX = Math.min(minX, n.x);
      maxX = Math.max(maxX, n.x);
      minY = Math.min(minY, n.y);
      maxY = Math.max(maxY, n.y);
    });
    const bw = Math.max(1, maxX - minX);
    const bh = Math.max(1, maxY - minY);
    state.view.zoom = clamp(Math.min(fit.w / bw, fit.h / bh) * 0.82, 0.08, 4);
    state.view.x = -(minX + maxX) / 2;
    state.view.y = -(minY + maxY) / 2;
  }

  function pickNode(ev) {
    const graph = state.graph;
    if (!graph) return;
    const canvas = document.getElementById("gnx-local-full-canvas");
    const fit = fitCanvas(canvas);
    if (!fit) return;
    const rect = canvas.getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const my = ev.clientY - rect.top;
    const view = state.view;
    const ca = Math.cos(view.rot), sa = Math.sin(view.rot);

    let best = null;
    let bestD = 9999;
    graph.nodes.forEach((n) => {
      if (state.coreOnly && !(n.kind === "core" || n.kind === "py")) return;
      const x = n.x * ca - n.y * sa;
      const y = n.x * sa + n.y * ca;
      const px = fit.w / 2 + (x + view.x) * view.zoom;
      const py = fit.h / 2 + (y + view.y) * view.zoom;
      const d = Math.hypot(px - mx, py - my);
      if (d < bestD) { bestD = d; best = n; }
    });

    if (best && bestD < 18) {
      state.selected = best.id;
      const text = `${best.path} | kind=${best.kind} | weight=${Math.round(best.weight || 1)}`;
      q("[data-selected]") && (q("[data-selected]").textContent = text);
      q("[data-status]") && (q("[data-status]").textContent = "Selected: " + text);
    }
  }

  function startFull() {
    if (state.fullRaf) cancelAnimationFrame(state.fullRaf);
    const loop = () => {
      if (!state.fullOpen) {
        state.fullRaf = 0;
        return;
      }
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
    if (window.__gitnexusLocalHudKeysV051) return;
    window.__gitnexusLocalHudKeysV051 = true;

    window.addEventListener("keydown", (ev) => {
      const hud = document.getElementById(HUD_ID);
      const open = hud && !hud.classList.contains("is-hidden");
      if (ev.ctrlKey && String(ev.key).toLowerCase() === "k") {
        if (open) {
          q(".gnx-local-search", hud)?.focus();
          ev.preventDefault();
        }
      }
      if (open && ev.key === "Escape") {
        closeHud();
        ev.preventDefault();
      }
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
})();