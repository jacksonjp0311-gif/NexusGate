(() => {
  const VERSION = "v0.4.1";
  const MINI_DOCK_ID = "gitnexus-core-left-dock";
  const HUD_ID = "gitnexus-standalone-hud";
  const STATE_KEY = "__gitnexusStandaloneHudV041";

  const state = window[STATE_KEY] || (window[STATE_KEY] = {
    graph: null,
    mode: "all",
    labels: true,
    edges: true,
    miniRaf: 0,
    fullRaf: 0,
    fullVisible: false,
    transform: { x: 0, y: 0, scale: 1, rot: 0 },
    dragging: false,
    rotating: false,
    dragStart: { x: 0, y: 0 },
    selected: null,
    loaded: false,
    resizeTimer: 0,
    bound: false
  });

  const CORE_DENY = [
    /(^|[\\/])reports([\\/]|$)/i,
    /(^|[\\/])state([\\/]|$)/i,
    /(^|[\\/])ledger([\\/]|$)/i,
    /compact_compile_logs/i,
    /_latest\.json/i,
    /\.jsonl\b/i,
    /\.bak/i,
    /Tesseract Neural Network[\\/](memory|state)/i,
    /GITNEXUS[\\/](reports|state|ledger)/i,
    /nexus_gitnexus_/i,
    /nexus_conversation_output_bridge/i,
    /test_nexus_conversation_output_bridge/i
  ];

  function q(sel, root = document) { return root.querySelector(sel); }
  function qa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function esc(value) {
    return String(value || "").replace(/[<>&]/g, (ch) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[ch]));
  }

  function fileKind(path) {
    const p = String(path || "");
    if (/\.py$/i.test(p)) return "python";
    if (/\.(js|ts|jsx|tsx|html|css)$/i.test(p)) return "ui";
    if (/test/i.test(p)) return "test";
    if (/\.(md|txt)$/i.test(p)) return "doc";
    if (/\.(json|jsonl)$/i.test(p)) return "state";
    return "core";
  }

  function colorFor(kind) {
    return {
      python: "#55f7ff",
      ui: "#ffaa00",
      test: "#b46cff",
      doc: "#5f8dff",
      state: "#7dff4d",
      core: "#45f0d0",
      symbol: "#7dff4d"
    }[kind] || "#55f7ff";
  }

  function shouldHideCore(label) {
    return CORE_DENY.some((rx) => rx.test(String(label || "")));
  }

  function fallbackGraph() {
    const files = [
      "nexus_gate/core/packets.py",
      "nexus_gate/runtime/router.py",
      "nexus_gate/compiler/compiler.py",
      "nexus_gate/compiler/gates.py",
      "nexus_gate/adapters/registry.py",
      "nexus_gate/adapters/local_demo.py",
      "nexus_gate/receptors/registry.py",
      "nexus_gate/receptors/compatibility.py",
      "nexus_gate/geometric_memory/score.py",
      "nexus_gate/nexus_cell/plan.py",
      "nexus_gate/nexus_cell/policy.py",
      "nexus_gate/nexus_cell/context_bridge.py",
      "nexus_gate/bridge/runtime.py",
      "nexus_gate/self_healing/engine.py"
    ];

    const nodes = files.map((name, i) => ({
      id: name,
      label: name,
      kind: fileKind(name),
      cluster: fileKind(name),
      hot: i < 6,
      size: i < 6 ? 6 : 4
    }));

    const edges = [];
    for (let i = 1; i < nodes.length; i++) edges.push({ source: nodes[0].id, target: nodes[i].id });
    for (let i = 0; i < nodes.length - 1; i++) if (i % 2 === 0) edges.push({ source: nodes[i].id, target: nodes[i + 1].id });

    return { nodes, edges, counts: { files: nodes.length, symbols: 64, edges: edges.length, changed: 0 } };
  }

  function normalizeGraph(raw) {
    if (!raw || typeof raw !== "object") return fallbackGraph();

    let nodes = [];
    let edges = [];
    const countsIn = raw.counts || {};

    if (Array.isArray(raw.nodes)) {
      nodes = raw.nodes.map((n, i) => {
        const label = String(n.label || n.name || n.path || n.id || `node:${i}`);
        return {
          id: String(n.id || n.key || label),
          label,
          kind: n.kind || n.type || fileKind(label),
          cluster: n.cluster || n.kind || n.type || fileKind(label),
          hot: Boolean(n.hot || n.imported || n.changed),
          size: Number(n.size || n.weight || n.degree || (n.hot ? 7 : 4))
        };
      });
    }

    if (Array.isArray(raw.edges)) {
      edges = raw.edges.map((e) => ({
        source: String(e.source || e.from || e.src || e.a || ""),
        target: String(e.target || e.to || e.dst || e.b || "")
      })).filter((e) => e.source && e.target);
    }

    const listKeys = ["top_imported_files", "top_files", "changed_files", "affected_files", "files"];
    for (const key of listKeys) {
      if (Array.isArray(raw[key])) {
        raw[key].forEach((value, i) => {
          const label = typeof value === "string" ? value : String(value.path || value.name || value.file || JSON.stringify(value));
          if (!nodes.some((n) => n.id === label)) {
            nodes.push({ id: label, label, kind: fileKind(label), cluster: fileKind(label), hot: key.includes("top") || key.includes("changed"), size: key.includes("top") ? 7 : 4 });
          }
          if (i > 0 && nodes[0]) edges.push({ source: nodes[0].id, target: label });
        });
      }
    }

    if (raw.impact && Array.isArray(raw.impact.changed_files)) {
      raw.impact.changed_files.forEach((value, i) => {
        const label = String(value);
        if (!nodes.some((n) => n.id === label)) {
          nodes.push({ id: label, label, kind: fileKind(label), cluster: fileKind(label), hot: true, size: 5 });
        }
        if (i > 0 && nodes[0]) edges.push({ source: nodes[0].id, target: label });
      });
    }

    if (nodes.length < 5) return fallbackGraph();

    const counts = {
      files: Number(countsIn.files || nodes.filter((n) => n.kind !== "symbol").length || nodes.length),
      symbols: Number(countsIn.symbols || nodes.length),
      edges: Number(countsIn.edges || edges.length),
      changed: Number(countsIn.changed_files || countsIn.changed || nodes.filter((n) => n.hot).length)
    };

    return { nodes, edges, counts };
  }

  async function fetchJson(path) {
    const res = await fetch(path, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  async function loadGraph() {
    if (state.loaded && state.graph) return state.graph;

    const paths = [
      "../../GITNEXUS/state/gitnexus_graph_latest.json",
      "../../state/gitnexus/gitnexus_graph_latest.json",
      "../../GITNEXUS/reports/gitnexus_report_latest.json",
      "../../reports/gitnexus_report_latest.json"
    ];

    for (const path of paths) {
      try {
        const raw = await fetchJson(path);
        state.graph = normalizeGraph(raw);
        state.loaded = true;
        return state.graph;
      } catch (_) {}
    }

    state.graph = fallbackGraph();
    state.loaded = true;
    return state.graph;
  }

  function visibleGraph() {
    const graph = state.graph || fallbackGraph();
    if (state.mode !== "core") return graph;

    const nodes = graph.nodes.filter((n) => !shouldHideCore(n.label));
    const ids = new Set(nodes.map((n) => n.id));
    const edges = graph.edges.filter((e) => ids.has(e.source) && ids.has(e.target));
    return { nodes, edges, counts: graph.counts };
  }

  function layoutGraph(graph, mini) {
    const nodes = graph.nodes.map((n) => ({ ...n }));
    const clusters = [...new Set(nodes.map((n) => n.cluster || n.kind || "core"))];
    const clusterIndex = new Map(clusters.map((c, i) => [c, i]));
    const count = Math.max(1, nodes.length);

    nodes.forEach((node, i) => {
      const ci = clusterIndex.get(node.cluster || node.kind || "core") || 0;
      const arm = ci / Math.max(1, clusters.length) * Math.PI * 2;
      const ring = Math.sqrt((i + 1) / count);
      const radius = mini ? 0.11 + ring * 0.84 : 0.08 + ring * 0.88;
      const spiral = i * 0.39;
      node.x = Math.cos(arm + spiral * 0.21) * radius;
      node.y = Math.sin(arm + spiral * 0.21) * radius;
      node.color = colorFor(node.kind);
      node.radius = clamp(Number(node.size || 4), 2.5, mini ? 5.5 : 9);
    });

    return { nodes, edges: graph.edges };
  }

  function fitCanvas(canvas) {
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    const w = Math.max(160, Math.floor(rect.width));
    const h = Math.max(140, Math.floor(rect.height));
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

  function renderGraph(canvas, mini, time) {
    const fit = fitCanvas(canvas);
    if (!fit) return;

    const { ctx, w, h } = fit;
    const graph = layoutGraph(visibleGraph(), mini);
    const cx = w / 2;
    const cy = h / 2;
    const baseScale = Math.min(w, h) * (mini ? 0.40 : 0.43);
    const rot = mini ? (time || performance.now()) * 0.00022 : state.transform.rot;
    const scale = mini ? 1 : state.transform.scale;
    const ox = mini ? 0 : state.transform.x;
    const oy = mini ? 0 : state.transform.y;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#020712";
    ctx.fillRect(0, 0, w, h);

    const glow = ctx.createRadialGradient(cx, cy, 2, cx, cy, Math.min(w, h) * 0.50);
    glow.addColorStop(0, "rgba(0,240,255,0.16)");
    glow.addColorStop(0.38, "rgba(255,170,0,0.08)");
    glow.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, w, h);

    function world(n) {
      const x0 = n.x * baseScale * scale;
      const y0 = n.y * baseScale * scale;
      const c = Math.cos(rot);
      const s = Math.sin(rot);
      return { x: cx + ox + x0 * c - y0 * s, y: cy + oy + x0 * s + y0 * c };
    }

    const byId = new Map(graph.nodes.map((n) => [n.id, n]));

    if (state.edges) {
      ctx.lineWidth = mini ? 0.8 : 1;
      graph.edges.forEach((e, idx) => {
        const a = byId.get(e.source);
        const b = byId.get(e.target);
        if (!a || !b) return;
        const pa = world(a);
        const pb = world(b);
        ctx.beginPath();
        ctx.moveTo(pa.x, pa.y);
        ctx.lineTo(pb.x, pb.y);
        ctx.strokeStyle = idx % 5 === 0 ? "rgba(255,170,0,0.18)" : "rgba(0,240,255,0.10)";
        ctx.stroke();
      });
    }

    graph.nodes.forEach((n) => {
      const p = world(n);
      const r = mini ? n.radius : n.radius * clamp(scale, 0.55, 1.25);
      ctx.shadowBlur = n.hot ? 18 : 10;
      ctx.shadowColor = n.hot ? "rgba(255,170,0,0.55)" : "rgba(0,240,255,0.40)";
      ctx.fillStyle = n.hot ? "#ffaa00" : n.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.fill();

      if (n.hot || r > 6) {
        ctx.strokeStyle = "#7dff4d";
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      if (!mini && state.labels && r >= 3.5) {
        ctx.shadowBlur = 0;
        ctx.fillStyle = "rgba(220,255,255,0.88)";
        ctx.font = "10px Consolas, monospace";
        const label = String(n.label || n.id).split(/[\\/]/).slice(-2).join("/");
        ctx.fillText(label.slice(0, 42), p.x + r + 4, p.y - r - 2);
      }
    });

    if (state.selected && !mini) {
      const sel = byId.get(state.selected);
      if (sel) {
        const p = world(sel);
        ctx.shadowBlur = 24;
        ctx.shadowColor = "rgba(125,255,77,0.9)";
        ctx.strokeStyle = "#7dff4d";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 18 * scale, 0, Math.PI * 2);
        ctx.stroke();
      }
    }
  }

  function dockGeometry() {
    const neural = qa("aside, section, article, div")
      .map((node) => ({ rect: node.getBoundingClientRect(), text: String(node.textContent || "").toUpperCase() }))
      .filter((item) =>
        item.rect.width >= 220 &&
        item.rect.width <= 400 &&
        item.rect.left >= -8 &&
        item.rect.left < 105 &&
        item.text.includes("NEURAL ACTIVITY")
      )
      .sort((a, b) => (b.rect.width * b.rect.height) - (a.rect.width * a.rect.height))[0]?.rect;

    const footer = qa("footer, section, div")
      .map((node) => ({ rect: node.getBoundingClientRect(), text: String(node.textContent || "").toUpperCase() }))
      .filter((item) => item.text.includes("GOVERNANCE") && item.text.includes("SYSTEM BUS"))
      .sort((a, b) => b.rect.top - a.rect.top)[0]?.rect;

    const footerTop = footer && footer.top > window.innerHeight * 0.5 ? footer.top : window.innerHeight - 48;
    const left = neural ? Math.max(6, neural.left) : 8;
    const width = neural ? Math.max(260, Math.min(390, neural.width)) : 310;
    const top = neural ? Math.min(neural.bottom + 12, footerTop - 260) : Math.round(window.innerHeight * 0.60);
    const height = Math.max(220, footerTop - top - 10);
    return { left: Math.round(left), top: Math.round(top), width: Math.round(width), height: Math.round(height) };
  }

  function ensureMiniDock() {
    let dock = document.getElementById(MINI_DOCK_ID);
    if (!dock) {
      dock = document.createElement("section");
      dock.id = MINI_DOCK_ID;
      document.body.appendChild(dock);
    }

    qa("#" + MINI_DOCK_ID).slice(1).forEach((n) => n.remove());

    const g = dockGeometry();
    dock.className = "gnx-mini-dock";
    dock.dataset.version = VERSION;
    dock.style.left = g.left + "px";
    dock.style.top = g.top + "px";
    dock.style.width = g.width + "px";
    dock.style.height = g.height + "px";

    if (!dock.querySelector(".gnx-mini-v041")) {
      dock.innerHTML = `
        <section class="gnx-mini-v041">
          <div class="gnx-mini-head">
            <div class="gnx-mini-brand">
              <span class="gnx-orb"></span>
              <div>
                <div class="gnx-mini-title">GITNEXUS</div>
                <div class="gnx-mini-sub">CODEGRAPH GEOMETRY</div>
              </div>
            </div>
            <button class="gnx-mini-open" type="button">OPEN</button>
          </div>
          <button class="gnx-mini-canvas-button" type="button" title="Open GITNEXUS HUD">
            <canvas id="gnx-mini-canvas-v041"></canvas>
            <span class="gnx-mini-caption">LIVE CODEGRAPH</span>
          </button>
        </section>
      `;
      q(".gnx-mini-open", dock)?.addEventListener("click", openFullHud);
      q(".gnx-mini-canvas-button", dock)?.addEventListener("click", openFullHud);
    }

    return dock;
  }

  function buildFullHud() {
    let hud = document.getElementById(HUD_ID);
    if (hud) return hud;

    hud = document.createElement("section");
    hud.id = HUD_ID;
    hud.className = "gnx-hud-v041 is-hidden";
    hud.innerHTML = `
      <div class="gnx-hud-top">
        <div class="gnx-hud-brand">
          <span class="gnx-orb"></span>
          <div>
            <div class="gnx-hud-title">GITNEXUS</div>
            <div class="gnx-hud-sub">NEXUSGATE CODEGRAPH INTELLIGENCE</div>
          </div>
        </div>
        <input class="gnx-search" placeholder="Search nodes, files, symbols... Ctrl+K" />
        <button class="gnx-btn" data-gnx-fit>FIT</button>
        <button class="gnx-btn" data-gnx-zoom-in>+</button>
        <button class="gnx-btn" data-gnx-zoom-out>-</button>
        <button class="gnx-btn" data-gnx-turn-left>TURN</button>
        <button class="gnx-btn" data-gnx-turn-right>TURN</button>
        <button class="gnx-btn" data-gnx-edges>EDGES</button>
        <button class="gnx-btn" data-gnx-labels>LABELS</button>
        <button class="gnx-btn" data-gnx-scope-all>ALL</button>
        <button class="gnx-btn" data-gnx-scope-core>CORE</button>
        <button class="gnx-btn gnx-close" data-gnx-close>CLOSE</button>
      </div>
      <div class="gnx-hud-body">
        <aside class="gnx-side gnx-left">
          <h3>EXPLORER</h3>
          <div class="gnx-stat-grid">
            <div><span>FILES</span><b data-gnx-files>--</b></div>
            <div><span>SYMBOLS</span><b data-gnx-symbols>--</b></div>
            <div><span>EDGES</span><b data-gnx-edge-count>--</b></div>
            <div><span>MODE</span><b data-gnx-mode>ALL</b></div>
          </div>
          <div class="gnx-list" data-gnx-file-list></div>
        </aside>
        <main class="gnx-main">
          <div class="gnx-help">DRAG = PAN &nbsp;&nbsp; WHEEL = ZOOM &nbsp;&nbsp; ALT-DRAG / SHIFT-WHEEL = ROTATE</div>
          <canvas id="gnx-full-canvas-v041"></canvas>
          <div class="gnx-selected" data-gnx-selected>No node selected.</div>
        </main>
        <aside class="gnx-side gnx-right">
          <h3>RECOMMENDATION</h3>
          <div class="gnx-rec">Evidence-only graph. Inspect affected files before durable mutation.</div>
          <h3>TOP FILES</h3>
          <div class="gnx-list" data-gnx-top-list></div>
          <h3>SELECTED NODE</h3>
          <div class="gnx-rec" data-gnx-selected-copy>No node selected.</div>
        </aside>
      </div>
      <div class="gnx-hud-foot">
        <span>No autonomous authority.</span>
        <span>No shell execution from model output.</span>
        <span>No NexusCell policy change.</span>
      </div>
    `;

    document.body.appendChild(hud);

    q("[data-gnx-close]", hud)?.addEventListener("click", closeFullHud);
    q("[data-gnx-fit]", hud)?.addEventListener("click", fitFullGraph);
    q("[data-gnx-zoom-in]", hud)?.addEventListener("click", () => { state.transform.scale = clamp(state.transform.scale * 1.18, 0.2, 6); });
    q("[data-gnx-zoom-out]", hud)?.addEventListener("click", () => { state.transform.scale = clamp(state.transform.scale / 1.18, 0.2, 6); });
    q("[data-gnx-turn-left]", hud)?.addEventListener("click", () => { state.transform.rot -= 0.18; });
    q("[data-gnx-turn-right]", hud)?.addEventListener("click", () => { state.transform.rot += 0.18; });
    q("[data-gnx-edges]", hud)?.addEventListener("click", () => { state.edges = !state.edges; updateHudText(); });
    q("[data-gnx-labels]", hud)?.addEventListener("click", () => { state.labels = !state.labels; updateHudText(); });
    q("[data-gnx-scope-all]", hud)?.addEventListener("click", () => { state.mode = "all"; updateHudText(); });
    q("[data-gnx-scope-core]", hud)?.addEventListener("click", () => { state.mode = "core"; updateHudText(); });
    q(".gnx-search", hud)?.addEventListener("input", (ev) => selectBySearch(ev.target.value));

    attachCanvasInteractions(q("#gnx-full-canvas-v041", hud));
    updateHudText();
    return hud;
  }

  function updateHudText() {
    const hud = document.getElementById(HUD_ID);
    if (!hud) return;
    const graph = visibleGraph();
    const counts = graph.counts || {};
    const set = (sel, value) => { const node = q(sel, hud); if (node) node.textContent = String(value); };
    set("[data-gnx-files]", counts.files || graph.nodes.length);
    set("[data-gnx-symbols]", counts.symbols || graph.nodes.length);
    set("[data-gnx-edge-count]", counts.edges || graph.edges.length);
    set("[data-gnx-mode]", state.mode.toUpperCase());

    const list = q("[data-gnx-file-list]", hud);
    if (list) {
      list.innerHTML = graph.nodes.slice(0, 28).map((n, i) =>
        `<div class="gnx-row"><span>${String(i + 1).padStart(2, "0")}</span><span>${esc(n.label)}</span></div>`
      ).join("");
    }

    const top = q("[data-gnx-top-list]", hud);
    if (top) {
      top.innerHTML = graph.nodes.filter((n) => n.hot).slice(0, 18).map((n, i) =>
        `<div class="gnx-row hot"><span>${String(i + 1).padStart(2, "0")}</span><span>${esc(n.label)}</span></div>`
      ).join("");
    }

    if (state.selected) {
      set("[data-gnx-selected]", `Selected: ${state.selected}`);
      set("[data-gnx-selected-copy]", state.selected);
    }

    [
      ["[data-gnx-scope-all]", state.mode === "all"],
      ["[data-gnx-scope-core]", state.mode === "core"],
      ["[data-gnx-edges]", state.edges],
      ["[data-gnx-labels]", state.labels]
    ].forEach(([sel, active]) => q(sel, hud)?.setAttribute("data-active", active ? "true" : "false"));
  }

  function selectBySearch(value) {
    const needle = String(value || "").toLowerCase().trim();
    if (!needle) return;
    const graph = visibleGraph();
    const hit = graph.nodes.find((n) => String(n.label).toLowerCase().includes(needle));
    if (hit) {
      state.selected = hit.id;
      updateHudText();
    }
  }

  function closeFullHud() {
    const hud = document.getElementById(HUD_ID);
    if (hud) hud.classList.add("is-hidden");
    state.fullVisible = false;
    if (state.fullRaf) {
      cancelAnimationFrame(state.fullRaf);
      state.fullRaf = 0;
    }
  }

  function openFullHud() {
    const hud = buildFullHud();
    hud.classList.remove("is-hidden");
    hud.style.display = "grid";
    state.fullVisible = true;
    fitFullGraph();
    updateHudText();
    startFullAnimation();
  }

  function fitFullGraph() {
    state.transform.x = 0;
    state.transform.y = 0;
    state.transform.scale = 1;
    state.transform.rot = 0;
  }

  function attachCanvasInteractions(canvas) {
    if (!canvas || canvas.dataset.bound === "true") return;
    canvas.dataset.bound = "true";

    canvas.addEventListener("mousedown", (ev) => {
      state.dragging = true;
      state.rotating = ev.altKey || ev.button === 1;
      state.dragStart = { x: ev.clientX, y: ev.clientY };
      ev.preventDefault();
    });

    window.addEventListener("mouseup", () => {
      if (!state.fullVisible) return;
      state.dragging = false;
      state.rotating = false;
    });

    window.addEventListener("mousemove", (ev) => {
      if (!state.fullVisible || !state.dragging) return;
      const dx = ev.clientX - state.dragStart.x;
      const dy = ev.clientY - state.dragStart.y;
      state.dragStart = { x: ev.clientX, y: ev.clientY };

      if (state.rotating) {
        state.transform.rot += dx * 0.006;
      } else {
        state.transform.x += dx;
        state.transform.y += dy;
      }
    });

    canvas.addEventListener("wheel", (ev) => {
      if (!state.fullVisible) return;
      ev.preventDefault();
      if (ev.shiftKey) {
        state.transform.rot += ev.deltaY > 0 ? 0.12 : -0.12;
        return;
      }
      const factor = ev.deltaY > 0 ? 0.90 : 1.10;
      state.transform.scale = clamp(state.transform.scale * factor, 0.2, 6);
    }, { passive: false });

    canvas.addEventListener("dblclick", fitFullGraph);
  }

  function startMiniAnimation() {
    if (state.miniRaf) return;
    const loop = (time) => {
      const canvas = document.getElementById("gnx-mini-canvas-v041");
      if (canvas) renderGraph(canvas, true, time);
      state.miniRaf = requestAnimationFrame(loop);
    };
    state.miniRaf = requestAnimationFrame(loop);
  }

  function startFullAnimation() {
    if (state.fullRaf) return;
    const loop = (time) => {
      if (!state.fullVisible) {
        state.fullRaf = 0;
        return;
      }
      const canvas = document.getElementById("gnx-full-canvas-v041");
      if (canvas) renderGraph(canvas, false, time);
      state.fullRaf = requestAnimationFrame(loop);
    };
    state.fullRaf = requestAnimationFrame(loop);
  }

  function scheduleLayout() {
    if (state.resizeTimer) clearTimeout(state.resizeTimer);
    state.resizeTimer = setTimeout(() => ensureMiniDock(), 100);
  }

  async function boot() {
    await loadGraph();
    ensureMiniDock();
    updateHudText();
    startMiniAnimation();
  }

  function bindRuntimeSafeHotkeys() {
    if (state.bound) return;
    state.bound = true;

    window.addEventListener("keydown", (ev) => {
      const hud = document.getElementById(HUD_ID);
      const open = hud && !hud.classList.contains("is-hidden");

      if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "k") {
        openFullHud();
        q(".gnx-search", document.getElementById(HUD_ID))?.focus();
        ev.preventDefault();
        return;
      }

      if (!open) return;

      if (ev.key === "[") {
        state.transform.rot -= 0.18;
        ev.preventDefault();
      }
      if (ev.key === "]") {
        state.transform.rot += 0.18;
        ev.preventDefault();
      }
      if (ev.key === "Escape") {
        closeFullHud();
        ev.preventDefault();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => { boot(); bindRuntimeSafeHotkeys(); }, { once: true });
  } else {
    boot();
    bindRuntimeSafeHotkeys();
  }

  window.addEventListener("load", boot);
  window.addEventListener("resize", scheduleLayout);
  window.gitnexusOpenHud = openFullHud;
  window.gitnexusCloseHud = closeFullHud;
  window.gitnexusScopeAll = () => { state.mode = "all"; updateHudText(); };
  window.gitnexusScopeCore = () => { state.mode = "core"; updateHudText(); };
})();