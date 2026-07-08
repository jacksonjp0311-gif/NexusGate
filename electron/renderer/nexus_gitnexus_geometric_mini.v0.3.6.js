(() => {
  const VERSION = "v0.3.6";
  const DOCK_ID = "gitnexus-core-left-dock";
  const STATE_KEY = "__gitnexusGeometricMiniV036";

  function q(sel, root = document) { return root.querySelector(sel); }
  function qa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  const state = window[STATE_KEY] || (window[STATE_KEY] = {
    mounted: false,
    raf: 0,
    resizeTimer: 0,
    observer: null,
    lastDockRect: ""
  });

  function cleanAscii(value) {
    return String(value || "").replace(/[^\x20-\x7E]/g, "").trim();
  }

  function sanitizeToolbarLabels(root = document) {
    const canonical = [
      [/FIT/i, "FIT"],
      [/TURN|ROT/i, "TURN"],
      [/EDGE/i, "EDGES"],
      [/LABEL/i, "LABELS"],
      [/CLOSE/i, "CLOSE"],
      [/RISK/i, "RISK HIGH"],
      [/EVIDENCE/i, "EVIDENCE ONLY"]
    ];

    qa("button, [role='button'], .gitnexus-control-btn, .gitnexus-pill, .gitnexus-mini-pill", root).forEach((node) => {
      const raw = String(node.textContent || "").trim();
      if (!raw) return;
      const ascii = cleanAscii(raw);
      if (ascii !== raw || /Ãƒ|Ã‚|ï¿½|Aï¿½/.test(raw)) {
        const match = canonical.find(([rx]) => rx.test(raw) || rx.test(ascii));
        node.textContent = match ? match[1] : (ascii || "TURN");
      }
    });
  }

  function getBigHud() {
    return document.getElementById("gitnexus-big-hud") ||
      q("[data-gitnexus-big-hud]") ||
      q(".gitnexus-big") ||
      q(".gitnexus-big-hud");
  }

  function openBigHud() {
    const hud = getBigHud();
    if (hud) {
      hud.hidden = false;
      hud.classList.remove("is-hidden");
      hud.style.display = "grid";
      hud.style.visibility = "visible";
      hud.style.opacity = "1";
    }

    const openers = [
      "[data-gn-open-big-hud]",
      "[data-gn-open-big]",
      "[data-gn-open-hud]",
      "[data-gitnexus-open-big]",
      "#gitnexus-open-big-hud"
    ];

    for (const sel of openers) {
      const node = q(sel);
      if (node && !node.closest("#" + DOCK_ID)) {
        try { node.click(); return; } catch (_) {}
      }
    }

    window.dispatchEvent(new CustomEvent("gitnexus:open-big-hud"));
  }

  function dockGeometry() {
    const candidates = qa("aside, section, article, div")
      .map((node) => ({
        node,
        rect: node.getBoundingClientRect(),
        text: String(node.textContent || "").toUpperCase()
      }))
      .filter((item) =>
        item.rect.width >= 220 &&
        item.rect.width <= 390 &&
        item.rect.left >= -8 &&
        item.rect.left < 90 &&
        item.text.includes("NEURAL ACTIVITY")
      )
      .sort((a, b) => (b.rect.width * b.rect.height) - (a.rect.width * a.rect.height));

    const neural = candidates.length ? candidates[0].rect : null;

    const footerHits = qa("footer, section, div")
      .map((node) => ({
        node,
        rect: node.getBoundingClientRect(),
        text: String(node.textContent || "").toUpperCase()
      }))
      .filter((item) => item.text.includes("GOVERNANCE") && item.text.includes("SYSTEM BUS"))
      .sort((a, b) => b.rect.top - a.rect.top);

    const footerTop = footerHits.length && footerHits[0].rect.top > window.innerHeight * 0.5
      ? footerHits[0].rect.top
      : (window.innerHeight - 48);

    const left = neural ? Math.max(6, neural.left) : 8;
    const width = neural ? Math.max(260, Math.min(380, neural.width)) : 310;
    const top = neural ? Math.min(neural.bottom + 12, footerTop - 260) : Math.round(window.innerHeight * 0.60);
    const height = Math.max(220, footerTop - top - 10);

    return {
      left: Math.round(left),
      top: Math.round(top),
      width: Math.round(width),
      height: Math.round(height)
    };
  }

  function removeDuplicateDocks() {
    const all = qa("#" + DOCK_ID);
    if (all.length > 1) {
      all.slice(1).forEach((node) => node.remove());
    }

    qa(".gitnexus-exact-mini-shell, .gitnexus-mini-mirror-shell").forEach((node) => {
      const host = node.closest("#" + DOCK_ID);
      if (host && !host.querySelector(".gitnexus-geometric-mini")) {
        node.remove();
      }
    });
  }

  function ensureDock() {
    removeDuplicateDocks();

    let dock = document.getElementById(DOCK_ID);
    if (!dock) {
      dock = document.createElement("section");
      dock.id = DOCK_ID;
      document.body.appendChild(dock);
    }

    dock.dataset.gitnexusMini = VERSION;
    dock.className = "gitnexus-geometric-mini-dock";

    if (!dock.querySelector(".gitnexus-geometric-mini")) {
      dock.innerHTML = `
        <section class="gitnexus-geometric-mini" data-version="${VERSION}">
          <div class="gitnexus-geo-head">
            <div class="gitnexus-geo-brand">
              <span class="gitnexus-geo-orb"></span>
              <div class="gitnexus-geo-copy">
                <div class="gitnexus-geo-title">GITNEXUS</div>
                <div class="gitnexus-geo-sub">CODEGRAPH GEOMETRY</div>
              </div>
            </div>
            <button class="gitnexus-geo-open" type="button">OPEN</button>
          </div>
          <button class="gitnexus-geo-canvas-button" type="button" title="Open GITNEXUS HUD">
            <canvas id="gitnexus-geometric-mini-canvas"></canvas>
            <div class="gitnexus-geo-overlay">
              <span>LIVE CODEGRAPH</span>
              <b>CLICK TO OPEN HUD</b>
            </div>
          </button>
        </section>
      `;

      const openBtn = q(".gitnexus-geo-open", dock);
      const canvasBtn = q(".gitnexus-geo-canvas-button", dock);
      if (openBtn) openBtn.addEventListener("click", openBigHud);
      if (canvasBtn) canvasBtn.addEventListener("click", openBigHud);
    }

    return dock;
  }

  function applyDockPosition(dock) {
    const g = dockGeometry();
    const sig = `${g.left}|${g.top}|${g.width}|${g.height}`;

    dock.style.position = "fixed";
    dock.style.left = g.left + "px";
    dock.style.top = g.top + "px";
    dock.style.width = g.width + "px";
    dock.style.height = g.height + "px";
    dock.style.zIndex = "620";
    dock.style.display = "block";
    dock.style.visibility = "visible";
    dock.style.opacity = "1";

    state.lastDockRect = sig;
  }

  function getCounts() {
    const text = document.body ? document.body.textContent || "" : "";
    const fileMatch = text.match(/files[\s\S]{0,16}?(\d{2,5})/i);
    const edgeMatch = text.match(/edges[\s\S]{0,16}?(\d{2,5})/i);
    return {
      files: fileMatch ? Number(fileMatch[1]) : 871,
      edges: edgeMatch ? Number(edgeMatch[1]) : 480
    };
  }

  function seededRandom(seed) {
    let t = seed >>> 0;
    return function () {
      t += 0x6D2B79F5;
      let x = Math.imul(t ^ (t >>> 15), 1 | t);
      x ^= x + Math.imul(x ^ (x >>> 7), 61 | x);
      return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
    };
  }

  function fitCanvas(canvas) {
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    const w = Math.max(180, Math.floor(rect.width));
    const h = Math.max(150, Math.floor(rect.height));
    const targetW = Math.floor(w * dpr);
    const targetH = Math.floor(h * dpr);

    if (canvas.width !== targetW || canvas.height !== targetH) {
      canvas.width = targetW;
      canvas.height = targetH;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx, w, h };
  }

  function drawFrame(time) {
    const canvas = document.getElementById("gitnexus-geometric-mini-canvas");
    if (!canvas || !canvas.isConnected) {
      state.raf = requestAnimationFrame(drawFrame);
      return;
    }

    const fit = fitCanvas(canvas);
    if (!fit) {
      state.raf = requestAnimationFrame(drawFrame);
      return;
    }

    const { ctx, w, h } = fit;
    const counts = getCounts();
    const t = (time || performance.now()) * 0.00024;
    const rnd = seededRandom(counts.files + counts.edges + 17);

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#020712";
    ctx.fillRect(0, 0, w, h);

    const cx = w * 0.5;
    const cy = h * 0.52;
    const maxR = Math.min(w, h) * 0.34;

    const glow = ctx.createRadialGradient(cx, cy, 2, cx, cy, maxR * 1.6);
    glow.addColorStop(0, "rgba(0,240,255,0.16)");
    glow.addColorStop(0.40, "rgba(255,170,0,0.08)");
    glow.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, w, h);

    const nodeCount = Math.min(160, Math.max(74, Math.floor(counts.files / 8)));
    const nodes = [];

    for (let i = 0; i < nodeCount; i++) {
      const arm = i % 8;
      const base = (arm / 8) * Math.PI * 2 + t * 0.8;
      const radius = maxR * (0.10 + 0.90 * Math.pow(i / nodeCount, 0.72));
      const jitter = (rnd() - 0.5) * 0.72;
      const angle = base + jitter + Math.sin(t * 3 + i * 0.14) * 0.14;
      nodes.push({
        x: cx + Math.cos(angle) * radius,
        y: cy + Math.sin(angle) * radius,
        r: 1.4 + rnd() * 3.5,
        hot: i % 11 === 0,
        gold: i % 7 === 0
      });
    }

    ctx.lineWidth = 1;
    for (let i = 0; i < nodes.length; i++) {
      const n = nodes[i];
      if (i % 2 === 0) {
        ctx.strokeStyle = n.gold ? "rgba(255,170,0,0.34)" : "rgba(0,240,255,0.18)";
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(n.x, n.y);
        ctx.stroke();
      }
      if (i % 13 === 0) {
        const m = nodes[(i + 21) % nodes.length];
        ctx.strokeStyle = "rgba(0,240,255,0.08)";
        ctx.beginPath();
        ctx.moveTo(n.x, n.y);
        ctx.lineTo(m.x, m.y);
        ctx.stroke();
      }
    }

    ctx.shadowBlur = 16;
    for (const n of nodes) {
      ctx.shadowColor = n.gold ? "rgba(255,170,0,0.45)" : "rgba(0,240,255,0.40)";
      ctx.fillStyle = n.gold ? "#ffaa00" : n.hot ? "#7dff4d" : "#55f7ff";
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fill();

      if (n.hot) {
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 0.8;
        ctx.stroke();
      }
    }

    ctx.shadowBlur = 24;
    ctx.shadowColor = "rgba(255,170,0,0.65)";
    ctx.fillStyle = "#ffaa00";
    ctx.beginPath();
    ctx.arc(cx, cy, 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.shadowBlur = 14;
    ctx.shadowColor = "rgba(0,240,255,0.7)";
    ctx.strokeStyle = "#55f7ff";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.arc(cx, cy, 15, t, Math.PI * 2 + t);
    ctx.stroke();

    state.raf = requestAnimationFrame(drawFrame);
  }

  function startAnimation() {
    if (state.raf) return;
    state.raf = requestAnimationFrame(drawFrame);
  }

  function scheduleLayout() {
    if (state.resizeTimer) {
      clearTimeout(state.resizeTimer);
    }
    state.resizeTimer = window.setTimeout(() => {
      const dock = ensureDock();
      applyDockPosition(dock);
    }, 80);
  }

  function boot() {
    sanitizeToolbarLabels(document);
    const dock = ensureDock();
    applyDockPosition(dock);
    startAnimation();

    if (!state.observer) {
      state.observer = new MutationObserver(() => {
        const dockNow = document.getElementById(DOCK_ID);
        if (!dockNow) {
          state.mounted = false;
          ensureDock();
          scheduleLayout();
        }
        removeDuplicateDocks();
      });

      state.observer.observe(document.body, { childList: true, subtree: true });
    }

    state.mounted = true;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener("load", boot);
  window.addEventListener("resize", scheduleLayout);
  window.gitnexusGeometricMiniMount = boot;
})();