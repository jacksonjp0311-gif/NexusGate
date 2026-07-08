(() => {
  const VERSION = "v0.3.2";
  const REPORT_PATHS = [
    "../../reports/gitnexus_report_latest.json",
    "../../state/gitnexus/gitnexus_graph_latest.json",
    "../../GITNEXUS/reports/gitnexus_report_latest.json"
  ];

  const state = {
    report: null,
    model: { nodes: [], edges: [], index: new Map(), adjacency: new Map() },
    transform: { tx: 0, ty: 0, scale: 1, rotation: 0 },
    pointer: { dragging: false, mode: "pan", lastX: 0, lastY: 0, node: null },
    selected: null,
    hover: null,
    query: "",
    filters: {
      edges: true,
      labels: true,
      animate: true,
      changedOnly: false,
      symbols: true,
      hotOnly: false
    },
    raf: null,
    miniRaf: null
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

  function clamp(v, min, max) {
    return Math.max(min, Math.min(max, v));
  }

  function hash(str) {
    let h = 2166136261;
    const s = String(str || "");
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function safeName(value) {
    return String(value || "").replace(/^"|"$/g, "");
  }

  function colorFor(path, kind) {
    const p = String(path || "");
    if (kind === "symbol") return "#d36cff";
    if (p.includes("test")) return "#b46cff";
    if (p.endsWith(".py")) return "#55f7ff";
    if (p.endsWith(".js") || p.endsWith(".html") || p.endsWith(".css")) return "#ffaa00";
    if (p.includes("state") || p.includes("reports") || p.includes("ledger")) return "#7dff4d";
    if (p.includes("docs")) return "#5f7cff";
    return "#41f0d0";
  }

  function clusterFor(path, kind) {
    if (kind === "symbol") return 7;
    const p = String(path || "");
    if (p.includes("nexus_cell")) return 1;
    if (p.includes("compiler")) return 2;
    if (p.includes("electron")) return 3;
    if (p.includes("tests")) return 4;
    if (p.includes("state") || p.includes("reports") || p.includes("ledger")) return 5;
    if (p.includes("docs")) return 6;
    return hash(p) % 7;
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
    const top = Math.max(120, Math.min(topFromNeural, footerTop - 230));
    const height = Math.max(206, footerTop - top - 10);
    return { left, top, width, height };
  }

  function positionDock(dock) {
    const g = dockGeometry();
    dock.style.left = g.left + "px";
    dock.style.top = g.top + "px";
    dock.style.width = g.width + "px";
    dock.style.maxHeight = g.height + "px";
  }

  function addNode(nodes, index, node) {
    if (index.has(node.id)) return index.get(node.id);
    const i = nodes.length;
    index.set(node.id, i);
    nodes.push(node);
    return i;
  }

  function buildModel(report) {
    const nodes = [];
    const index = new Map();
    const edges = [];
    const files = Object.keys(report?.files || {});
    const edgeList = Array.isArray(report?.edges) ? report.edges : [];
    const symbols = Array.isArray(report?.symbols) ? report.symbols : [];
    const top = new Set((report?.top_imported_files || []).map((x) => x.file));
    const changed = new Set((report?.impact?.changed_files || []).map((x) => safeName(x)));
    const required = new Set();

    top.forEach((x) => required.add(x));
    changed.forEach((x) => required.add(x));
    edgeList.forEach((e) => {
      required.add(e.source);
      required.add(e.target);
    });

    const orderedFiles = [
      ...Array.from(required),
      ...files.filter((f) => !required.has(f))
    ].slice(0, 720);

    for (const id of orderedFiles) {
      const h = hash(id);
      const cluster = clusterFor(id, "file");
      const ring = 100 + (cluster * 58) + ((h >>> 8) % 95);
      const angle = ((h % 3600) / 3600) * Math.PI * 2;
      const hot = top.has(id);
      const isChanged = changed.has(id);
      addNode(nodes, index, {
        id,
        label: id.split("/").slice(-2).join("/"),
        kind: "file",
        cluster,
        x: Math.cos(angle) * ring,
        y: Math.sin(angle) * ring,
        vx: 0,
        vy: 0,
        pinned: false,
        r: hot ? 7.5 : isChanged ? 6.4 : 3.4,
        color: colorFor(id, "file"),
        hot,
        changed: isChanged,
        meta: report?.files?.[id] || {}
      });
    }

    for (const e of edgeList) {
      const s = index.get(e.source);
      const t = index.get(e.target);
      if (s !== undefined && t !== undefined) edges.push({ s, t, kind: e.kind || "imports", weight: 1 });
    }

    if (state.filters.symbols) {
      const selectedSymbols = symbols
        .filter((s) => index.has(s.file))
        .slice(0, 420);

      for (const sym of selectedSymbols) {
        const parentIndex = index.get(sym.file);
        if (parentIndex === undefined) continue;
        const parent = nodes[parentIndex];
        const id = "symbol:" + sym.file + ":" + sym.name + ":" + sym.line;
        const h = hash(id);
        const angle = ((h % 3600) / 3600) * Math.PI * 2;
        const dist = 18 + (h % 30);
        const childIndex = addNode(nodes, index, {
          id,
          label: sym.name,
          kind: "symbol",
          symbolKind: sym.kind,
          file: sym.file,
          line: sym.line,
          cluster: 7,
          x: parent.x + Math.cos(angle) * dist,
          y: parent.y + Math.sin(angle) * dist,
          vx: 0,
          vy: 0,
          pinned: false,
          r: 2.15,
          color: colorFor(sym.file, "symbol"),
          hot: false,
          changed: changed.has(sym.file),
          meta: sym
        });
        edges.push({ s: parentIndex, t: childIndex, kind: "defines", weight: 0.28 });
      }
    }

    const adjacency = new Map();
    for (const e of edges) {
      const a = nodes[e.s]?.id;
      const b = nodes[e.t]?.id;
      if (!a || !b) continue;
      if (!adjacency.has(a)) adjacency.set(a, new Set());
      if (!adjacency.has(b)) adjacency.set(b, new Set());
      adjacency.get(a).add(b);
      adjacency.get(b).add(a);
    }

    return { nodes, edges, index, adjacency };
  }

  function filteredNodes() {
    const q = state.query.toLowerCase().trim();
    return state.model.nodes.filter((n) => {
      if (state.filters.changedOnly && !n.changed) return false;
      if (state.filters.hotOnly && !n.hot && !n.changed) return false;
      if (!state.filters.symbols && n.kind === "symbol") return false;
      if (q && !(n.id.toLowerCase().includes(q) || n.label.toLowerCase().includes(q))) return false;
      return true;
    });
  }

  function relax(model) {
    const nodes = model.nodes;
    const edges = model.edges.slice(0, 2600);

    for (const e of edges) {
      const a = nodes[e.s];
      const b = nodes[e.t];
      if (!a || !b) continue;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) || 1;
      const desired = e.kind === "defines" ? 28 : 72 + Math.abs(a.cluster - b.cluster) * 18;
      const force = (d - desired) * (e.kind === "defines" ? 0.006 : 0.0035) * (e.weight || 1);
      const fx = dx / d * force;
      const fy = dy / d * force;
      if (!a.pinned) { a.vx += fx; a.vy += fy; }
      if (!b.pinned) { b.vx -= fx; b.vy -= fy; }
    }

    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      const end = Math.min(nodes.length, i + 130);
      for (let j = i + 1; j < end; j++) {
        const b = nodes[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const d2 = dx * dx + dy * dy + 0.01;
        if (d2 > 6400) continue;
        const d = Math.sqrt(d2);
        const force = Math.min(0.8, (a.kind === "symbol" || b.kind === "symbol" ? 20 : 70) / d2);
        const fx = dx / d * force;
        const fy = dy / d * force;
        if (!a.pinned) { a.vx -= fx; a.vy -= fy; }
        if (!b.pinned) { b.vx += fx; b.vy += fy; }
      }
    }

    for (const n of nodes) {
      if (!n.pinned) {
        const pull = n.kind === "symbol" ? 0.0002 : 0.00075;
        n.vx += -n.x * pull;
        n.vy += -n.y * pull;
        n.x += n.vx;
        n.y += n.vy;
      }
      n.vx *= 0.86;
      n.vy *= 0.86;
    }
  }

  function graphBounds(nodes) {
    if (!nodes.length) return { minX: -100, minY: -100, maxX: 100, maxY: 100 };
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const n of nodes) {
      minX = Math.min(minX, n.x);
      minY = Math.min(minY, n.y);
      maxX = Math.max(maxX, n.x);
      maxY = Math.max(maxY, n.y);
    }
    return { minX, minY, maxX, maxY };
  }

  function fitCanvas(canvas) {
    const nodes = filteredNodes();
    const b = graphBounds(nodes.length ? nodes : state.model.nodes);
    const rect = canvas.getBoundingClientRect();
    const w = Math.max(1, b.maxX - b.minX);
    const h = Math.max(1, b.maxY - b.minY);
    const scale = Math.min(rect.width / (w + 220), rect.height / (h + 220));
    state.transform.scale = clamp(scale, 0.08, 4);
    state.transform.rotation = 0;
    state.transform.tx = rect.width / 2 - ((b.minX + b.maxX) / 2) * state.transform.scale;
    state.transform.ty = rect.height / 2 - ((b.minY + b.maxY) / 2) * state.transform.scale;
  }

  function worldToScreen(n, canvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const cx = rect.width / 2;
    const cy = rect.height / 2;
    const cos = Math.cos(state.transform.rotation);
    const sin = Math.sin(state.transform.rotation);
    const rx = n.x * cos - n.y * sin;
    const ry = n.x * sin + n.y * cos;
    return {
      x: (rx * state.transform.scale + state.transform.tx) * dpr,
      y: (ry * state.transform.scale + state.transform.ty) * dpr
    };
  }

  function screenToWorld(canvas, sx, sy) {
    const dpr = window.devicePixelRatio || 1;
    const x = sx / dpr;
    const y = sy / dpr;
    const rx = (x - state.transform.tx) / state.transform.scale;
    const ry = (y - state.transform.ty) / state.transform.scale;
    const cos = Math.cos(-state.transform.rotation);
    const sin = Math.sin(-state.transform.rotation);
    return {
      x: rx * cos - ry * sin,
      y: rx * sin + ry * cos
    };
  }

  function visibleNodeSet() {
    const nodes = filteredNodes();
    return new Set(nodes.map((n) => n.id));
  }

  function draw(canvas) {
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();

    if (canvas.width !== Math.floor(rect.width * dpr) || canvas.height !== Math.floor(rect.height * dpr)) {
      canvas.width = Math.floor(rect.width * dpr);
      canvas.height = Math.floor(rect.height * dpr);
      if (!canvas.dataset.fitDone) {
        fitCanvas(canvas);
        canvas.dataset.fitDone = "1";
      }
    }

    if (state.filters.animate && !state.pointer.dragging) relax(state.model);

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#00040a";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const rad = Math.min(canvas.width, canvas.height) * .46;
    const g = ctx.createRadialGradient(cx, cy, 10, cx, cy, rad);
    g.addColorStop(0, "rgba(255,169,0,.13)");
    g.addColorStop(.28, "rgba(85,247,255,.10)");
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const visible = visibleNodeSet();
    const related = state.selected ? state.model.adjacency.get(state.selected.id) : null;

    if (state.filters.edges) {
      ctx.lineWidth = Math.max(0.35, 0.75 * dpr);
      for (const e of state.model.edges.slice(0, 4200)) {
        const a = state.model.nodes[e.s];
        const b = state.model.nodes[e.t];
        if (!a || !b) continue;
        if (!visible.has(a.id) || !visible.has(b.id)) continue;

        const ap = worldToScreen(a, canvas);
        const bp = worldToScreen(b, canvas);
        const hot = a.hot || b.hot || a.changed || b.changed;
        const selectedEdge = state.selected && (a.id === state.selected.id || b.id === state.selected.id);
        ctx.strokeStyle = selectedEdge ? "rgba(125,255,77,.78)" : hot ? "rgba(255,169,0,.38)" : e.kind === "defines" ? "rgba(211,108,255,.12)" : "rgba(85,247,255,.14)";
        ctx.globalAlpha = selectedEdge ? 1 : e.kind === "defines" ? .42 : .75;
        ctx.beginPath();
        ctx.moveTo(ap.x, ap.y);
        ctx.lineTo(bp.x, bp.y);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }

    for (const n of state.model.nodes) {
      if (!visible.has(n.id)) continue;
      const p = worldToScreen(n, canvas);
      const selected = state.selected?.id === n.id;
      const neighbor = related?.has(n.id);
      const r = (n.r * state.transform.scale * dpr);
      const rr = clamp(r, n.kind === "symbol" ? 1.8 : 2.4, selected ? 16 : n.hot || n.changed ? 11 : 7);

      ctx.beginPath();
      ctx.arc(p.x, p.y, rr, 0, Math.PI * 2);
      ctx.fillStyle = n.color;
      ctx.globalAlpha = selected ? 1 : neighbor ? .95 : n.changed ? .90 : n.hot ? .86 : n.kind === "symbol" ? .48 : .70;
      ctx.fill();

      if (selected || neighbor || n.hot || n.changed) {
        ctx.globalAlpha = selected ? 1 : .85;
        ctx.lineWidth = selected ? 2.2 : 1.35;
        ctx.strokeStyle = selected ? "#ffffff" : n.changed ? "#7dff4d" : n.hot ? "#ffaa00" : "#55f7ff";
        ctx.stroke();
      }
    }

    ctx.globalAlpha = 1;
    if (state.filters.labels) {
      ctx.font = `${10 * dpr}px Consolas`;
      ctx.fillStyle = "rgba(223,251,255,.76)";
      const q = state.query.toLowerCase().trim();
      const labels = state.model.nodes
        .filter((n) => visible.has(n.id) && (n.hot || n.changed || state.selected?.id === n.id || related?.has(n.id) || (q && (n.id.toLowerCase().includes(q) || n.label.toLowerCase().includes(q)))))
        .slice(0, 160);
      for (const n of labels) {
        const p = worldToScreen(n, canvas);
        ctx.fillText(n.label, p.x + 7 * dpr, p.y - 7 * dpr);
      }
    }

    state.raf = requestAnimationFrame(() => draw(canvas));
  }

  function nearestNode(canvas, event) {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const mx = (event.clientX - rect.left) * dpr;
    const my = (event.clientY - rect.top) * dpr;
    const visible = visibleNodeSet();
    let best = null;
    let bestD = Infinity;

    for (const n of state.model.nodes) {
      if (!visible.has(n.id)) continue;
      const p = worldToScreen(n, canvas);
      const d = (p.x - mx) ** 2 + (p.y - my) ** 2;
      if (d < bestD) {
        bestD = d;
        best = n;
      }
    }

    return bestD < 900 ? best : null;
  }

  function selectNode(n) {
    state.selected = n;
    const hud = document.getElementById("gitnexus-big-hud");
    if (!hud) return;
    const selected = hud.querySelector("[data-gn-selected]");
    const selectedPanel = hud.querySelector("[data-gn-node]");
    const edgePanel = hud.querySelector("[data-gn-edges-list]");
    const symbolPanel = hud.querySelector("[data-gn-symbols-list]");

    if (!n) {
      selected.textContent = "No node selected. Click a file/symbol, drag canvas to pan, wheel to zoom, Alt-drag to rotate.";
      selectedPanel.textContent = "No node selected.";
      edgePanel.innerHTML = "";
      return;
    }

    const neighbors = Array.from(state.model.adjacency.get(n.id) || []);
    selected.textContent = "Selected: " + n.id + " | kind=" + n.kind + " | cluster=" + n.cluster + " | neighbors=" + neighbors.length;
    selectedPanel.textContent =
      n.id + "\n\nKind: " + n.kind +
      "\nChanged: " + n.changed +
      "\nHot/imported: " + n.hot +
      "\nColor: " + n.color +
      (n.file ? "\nFile: " + n.file : "") +
      (n.line ? "\nLine: " + n.line : "");

    edgePanel.innerHTML = rows(neighbors.slice(0, 80).map((file, i) => ({ file, index: i + 1 })), "index");

    if (n.kind === "file") {
      const syms = (state.report?.symbols || []).filter((s) => s.file === n.id).slice(0, 80).map((s, i) => ({ file: s.kind + " " + s.name + " : " + s.line, index: i + 1 }));
      symbolPanel.innerHTML = rows(syms, "index");
    }
  }

  function rows(items, countKey) {
    if (!Array.isArray(items) || !items.length) return '<div class="gitnexus-row"><i></i><span>No entries.</span><b>--</b></div>';
    return items.slice(0, 90).map((item, index) => {
      const name = item.file || item.path || String(item);
      const count = item[countKey] ?? item.importer_count ?? item.index ?? "";
      return '<div class="gitnexus-row" data-gn-row="' + encodeURIComponent(name) + '"><i class="gitnexus-dot" style="color:' + colorFor(name) + ';background:' + colorFor(name) + '"></i><span title="' + String(name).replace(/"/g, "&quot;") + '">' + name + '</span><b>' + count + '</b></div>';
    }).join("");
  }

  function attachCanvasInteractions(canvas) {
    canvas.onmousedown = (event) => {
      const n = nearestNode(canvas, event);
      state.pointer.dragging = true;
      state.pointer.lastX = event.clientX;
      state.pointer.lastY = event.clientY;

      if (n && !event.altKey) {
        state.pointer.mode = "node";
        state.pointer.node = n;
        n.pinned = true;
        selectNode(n);
      } else if (event.altKey || event.button === 2) {
        state.pointer.mode = "rotate";
        state.pointer.node = null;
      } else {
        state.pointer.mode = "pan";
        state.pointer.node = null;
      }
    };

    canvas.onmousemove = (event) => {
      const dx = event.clientX - state.pointer.lastX;
      const dy = event.clientY - state.pointer.lastY;
      if (!state.pointer.dragging) {
        const n = nearestNode(canvas, event);
        if (n !== state.hover) state.hover = n;
        return;
      }

      if (state.pointer.mode === "pan") {
        state.transform.tx += dx;
        state.transform.ty += dy;
      } else if (state.pointer.mode === "rotate") {
        state.transform.rotation += dx * 0.006;
      } else if (state.pointer.mode === "node" && state.pointer.node) {
        const rect = canvas.getBoundingClientRect();
        const wx = screenToWorld(canvas, (event.clientX - rect.left) * (window.devicePixelRatio || 1), (event.clientY - rect.top) * (window.devicePixelRatio || 1));
        state.pointer.node.x = wx.x;
        state.pointer.node.y = wx.y;
        state.pointer.node.vx = 0;
        state.pointer.node.vy = 0;
      }

      state.pointer.lastX = event.clientX;
      state.pointer.lastY = event.clientY;
    };

    window.addEventListener("mouseup", () => {
      state.pointer.dragging = false;
      state.pointer.mode = "pan";
      state.pointer.node = null;
    });

    canvas.onwheel = (event) => {
      event.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const mx = event.clientX - rect.left;
      const my = event.clientY - rect.top;
      const before = {
        x: (mx - state.transform.tx) / state.transform.scale,
        y: (my - state.transform.ty) / state.transform.scale
      };
      const factor = event.deltaY < 0 ? 1.12 : 0.89;
      state.transform.scale = clamp(state.transform.scale * factor, 0.06, 8);
      state.transform.tx = mx - before.x * state.transform.scale;
      state.transform.ty = my - before.y * state.transform.scale;
    };

    canvas.ondblclick = (event) => {
      const n = nearestNode(canvas, event);
      if (n) {
        state.query = n.label;
        const input = document.querySelector("[data-gn-search]");
        if (input) input.value = n.label;
        selectNode(n);
      } else {
        fitCanvas(canvas);
      }
    };

    canvas.oncontextmenu = (event) => event.preventDefault();
  }

  function fillHud(hud, report) {
    state.report = report || {};
    state.model = buildModel(state.report);
    hud.querySelector("[data-gn-files]").textContent = text(report?.counts?.files);
    hud.querySelector("[data-gn-symbols]").textContent = text(report?.counts?.symbols);
    hud.querySelector("[data-gn-edge-count]").textContent = text(report?.counts?.edges);
    hud.querySelector("[data-gn-changed]").textContent = text(report?.counts?.changed_files);
    hud.querySelector("[data-gn-risk]").textContent = "Risk " + text(report?.impact?.risk, "scan");
    hud.querySelector("[data-gn-rec]").textContent = text(report?.recommendation?.summary, "Run scripts/nexus_gitnexus.ps1 scan.");

    const changed = (report?.impact?.changed_files || []).map((file, i) => ({ file: safeName(file), index: i + 1 }));
    hud.querySelector("[data-gn-changed-list]").innerHTML = rows(changed, "index");
    hud.querySelector("[data-gn-top]").innerHTML = rows(report?.top_imported_files || [], "importer_count");
    hud.querySelector("[data-gn-symbols-list]").innerHTML = rows((report?.symbols || []).slice(0, 90).map((s, i) => ({ file: s.file + " :: " + s.kind + " " + s.name + " : " + s.line, index: i + 1 })), "index");

    const filters = [
      ["Python", "#55f7ff"], ["Electron/UI", "#ffaa00"], ["Tests", "#b46cff"],
      ["State/Reports", "#7dff4d"], ["Docs", "#5f7cff"], ["Symbols", "#d36cff"]
    ];
    hud.querySelector("[data-gn-filters]").innerHTML = filters.map(([name, color]) =>
      '<div class="gitnexus-filter-item"><i class="gitnexus-dot" style="color:' + color + ';background:' + color + '"></i><span>' + name + '</span><b>tracked</b></div>'
    ).join("");

    hud.querySelectorAll("[data-gn-row]").forEach((row) => {
      row.addEventListener("click", () => {
        const id = decodeURIComponent(row.getAttribute("data-gn-row") || "");
        const idx = state.model.index.get(id);
        if (idx !== undefined) {
          selectNode(state.model.nodes[idx]);
          state.query = "";
          const input = hud.querySelector("[data-gn-search]");
          if (input) input.value = "";
        }
      });
    });
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
        '<div class="gitnexus-search">' +
          '<input data-gn-search placeholder="Search nodes, files, symbols... Ctrl+K" />' +
          '<button class="gitnexus-control-btn" data-gn-fit>Fit</button>' +
          '<button class="gitnexus-control-btn" data-gn-zoom-in>+</button>' +
          '<button class="gitnexus-control-btn" data-gn-zoom-out>-</button>' +
          '<button class="gitnexus-control-btn" data-gn-rotate-left>ÃƒÂ¢Ã…Â¸Ã‚Â²</button><button class="gitnexus-control-btn" data-gn-rotate>Turn</button><button class="gitnexus-control-btn" data-gn-rotate-right>ÃƒÂ¢Ã…Â¸Ã‚Â³</button>' +
          '<button class="gitnexus-control-btn optional" data-gn-edges aria-pressed="true">Edges</button>' +
          '<button class="gitnexus-control-btn optional" data-gn-labels aria-pressed="true">Labels</button>' +
          '<button class="gitnexus-control-btn optional" data-gn-changed>Changed</button>' +
          '<button class="gitnexus-control-btn optional" data-gn-symbols aria-pressed="true">Symbols</button>' +
        '</div>' +
        '<div class="gitnexus-pill-row"><span class="gitnexus-pill" data-gn-risk>Risk</span><span class="gitnexus-pill">Evidence Only</span></div>' +
        '<button class="gitnexus-close" data-gn-close>Close</button>' +
      '</div>' +
      '<div class="gitnexus-big-body">' +
        '<aside class="gitnexus-big-panel gitnexus-sidebar"><h2>Explorer</h2><div class="gitnexus-stat-grid"><div class="gitnexus-stat">Files<b data-gn-files>--</b></div><div class="gitnexus-stat">Symbols<b data-gn-symbols>--</b></div><div class="gitnexus-stat">Edges<b data-gn-edge-count>--</b></div><div class="gitnexus-stat">Changed<b data-gn-changed>--</b></div></div><div class="gitnexus-filter-list" data-gn-filters></div><div class="gitnexus-file-list" data-gn-changed-list></div></aside>' +
        '<main class="gitnexus-big-panel gitnexus-graph-shell"><canvas id="gitnexus-big-canvas"></canvas><div class="gitnexus-canvas-hud"><span>Drag = pan</span><span>Wheel = zoom</span><span>Alt-drag = turn</span><span>Drag node = move</span></div><div class="gitnexus-selected" data-gn-selected>No node selected. Click a file/symbol, drag canvas to pan, wheel to zoom, Alt-drag to rotate.</div></main>' +
        '<aside class="gitnexus-big-panel gitnexus-right"><section><h2>Recommendation</h2><div class="gitnexus-recommendation" data-gn-rec>Run scripts/nexus_gitnexus.ps1 scan.</div></section><section><h2>Top Imported Files</h2><div class="gitnexus-detail-list" data-gn-top></div></section><section><h2>Connected / Symbols</h2><div class="gitnexus-edge-list" data-gn-edges-list></div><div class="gitnexus-symbol-list" data-gn-symbols-list></div></section><section><h2>Selected Node</h2><div class="gitnexus-recommendation" data-gn-node>No node selected.</div></section></aside>' +
      '</div>' +
      '<footer class="gitnexus-big-bottom"><span>No autonomous authority.</span><span>No shell execution from model output.</span><span>No NexusCell policy change.</span></footer>';

    document.body.appendChild(hud);
    return hud;
  }

  function bindHudControls(hud, canvas) {
    const input = hud.querySelector("[data-gn-search]");
    input.oninput = () => { state.query = input.value || ""; };

    hud.querySelector("[data-gn-fit]").onclick = () => fitCanvas(canvas);
    hud.querySelector("[data-gn-zoom-in]").onclick = () => { state.transform.scale = clamp(state.transform.scale * 1.18, 0.06, 8); };
    hud.querySelector("[data-gn-zoom-out]").onclick = () => { state.transform.scale = clamp(state.transform.scale * 0.84, 0.06, 8); };
    hud.querySelector("[data-gn-rotate]").onclick = () => { state.transform.rotation += Math.PI / 12; };
    hud.querySelector("[data-gn-rotate-left]").onclick = () => { state.transform.rotation -= Math.PI / 18; };
    hud.querySelector("[data-gn-rotate-right]").onclick = () => { state.transform.rotation += Math.PI / 18; };

    const toggle = (selector, key) => {
      const btn = hud.querySelector(selector);
      btn.onclick = () => {
        state.filters[key] = !state.filters[key];
        btn.setAttribute("aria-pressed", String(state.filters[key]));
        if (key === "symbols") {
          state.model = buildModel(state.report || {});
          canvas.dataset.fitDone = "";
          fitCanvas(canvas);
        }
      };
    };

    toggle("[data-gn-edges]", "edges");
    toggle("[data-gn-labels]", "labels");
    toggle("[data-gn-changed]", "changedOnly");
    toggle("[data-gn-symbols]", "symbols");

    hud.querySelector("[data-gn-close]").onclick = () => {
      hud.hidden = true;
      if (state.raf) cancelAnimationFrame(state.raf);
      state.raf = null;
    };

    document.addEventListener("keydown", (event) => {
      if (hud.hidden) return;
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        input.focus();
      }
      if (event.key === "Escape") {
        hud.hidden = true;
        if (state.raf) cancelAnimationFrame(state.raf);
        state.raf = null;
      }
    }, { once: false });
  }

  async function openBigHud() {
    const report = await loadReport();
    const hud = createBigHud();
    fillHud(hud, report || {});
    hud.hidden = false;

    if (state.raf) cancelAnimationFrame(state.raf);
    state.query = "";
    state.selected = null;
    state.hover = null;
    state.filters.animate = true;

    const canvas = hud.querySelector("#gitnexus-big-canvas");
    canvas.dataset.fitDone = "";
    attachCanvasInteractions(canvas);
    bindHudControls(hud, canvas);
    setTimeout(() => fitCanvas(canvas), 50);
    requestAnimationFrame(() => draw(canvas));
  }

  function drawMini(canvas, report) {
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    if (canvas.width !== Math.floor(rect.width * dpr) || canvas.height !== Math.floor(rect.height * dpr)) {
      canvas.width = Math.floor(rect.width * dpr);
      canvas.height = Math.floor(rect.height * dpr);
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#010713";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const count = Math.min(64, Math.max(18, Math.floor((report?.counts?.edges || 80) / 10)));
    for (let i = 0; i < count; i++) {
      const a = i / count * Math.PI * 2;
      const r = Math.min(canvas.width, canvas.height) * (0.18 + (hash(i + "mini") % 100) / 450);
      const x = cx + Math.cos(a) * r;
      const y = cy + Math.sin(a) * r;
      ctx.strokeStyle = i % 4 === 0 ? "rgba(255,169,0,.38)" : "rgba(85,247,255,.26)";
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(x, y);
      ctx.stroke();
      ctx.fillStyle = i % 3 === 0 ? "#7dff4d" : "#55f7ff";
      ctx.beginPath();
      ctx.arc(x, y, (i % 5 === 0 ? 2.8 : 1.7) * dpr, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.fillStyle = "#ffaa00";
    ctx.beginPath();
    ctx.arc(cx, cy, 5.5 * dpr, 0, Math.PI * 2);
    ctx.fill();
    state.miniRaf = requestAnimationFrame(() => drawMini(canvas, report));
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

    dock.dataset.gitnexusVersion = VERSION;
    dock.innerHTML =
      '<section id="gitnexus-core-station" class="gitnexus-core-station">' +
        '<div class="gitnexus-core-station-head"><div class="gitnexus-core-title">GITNEXUS</div><div class="gitnexus-core-badge">Evidence</div></div>' +
        '<div class="gitnexus-mini-canvas-wrap"><canvas id="gitnexus-mini-canvas"></canvas><div class="gitnexus-mini-label"><span>Graph Preview</span><span>Live</span></div></div>' +
        '<button type="button" class="gitnexus-core-button">Open GitNexus HUD</button>' +
      '</section>';

    dock.querySelector("button")?.addEventListener("click", openBigHud);
    positionDock(dock);
    createBigHud();

    loadReport().then((data) => {
      const report = data || {};
      if (state.miniRaf) cancelAnimationFrame(state.miniRaf);
      drawMini(dock.querySelector("#gitnexus-mini-canvas"), report);
    });

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

  function gitnexusHudWatchdog() {
    try {
      if (!document.body) return;
      const dock = document.getElementById("gitnexus-core-left-dock");
      if (!dock || !document.body.contains(dock) || !dock.querySelector("#gitnexus-mini-canvas")) {
        boot();
        return;
      }
      dock.dataset.gitnexusVersion = VERSION;
      positionDock(dock);
      if (!document.getElementById("gitnexus-big-hud")) createBigHud();
    } catch (err) {
      try { console.warn("[GITNEXUS HUD] watchdog repair failed", err); } catch (_) {}
    }
  }

  window.gitnexusHudMount = function () {
    boot();
    setTimeout(boot, 120);
    setTimeout(boot, 600);
    setTimeout(boot, 1400);
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", window.gitnexusHudMount, { once: true });
  } else {
    window.gitnexusHudMount();
  }

  window.addEventListener("load", window.gitnexusHudMount);
  window.addEventListener("resize", () => {
    const dock = document.getElementById("gitnexus-core-left-dock");
    if (dock) positionDock(dock);
  });

  window.setInterval(gitnexusHudWatchdog, 1500);
})();
