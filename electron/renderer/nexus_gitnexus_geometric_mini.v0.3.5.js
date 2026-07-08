(() => {
  const VERSION = "v0.3.5";
  const DOCK_ID = "gitnexus-core-left-dock";

  function q(sel, root = document) { return root.querySelector(sel); }
  function qa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  function cleanText(value) {
    return String(value || "").replace(/[^\x20-\x7E]/g, "").trim();
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

    qa("button, [role='button'], .gitnexus-control-btn, .gitnexus-pill, .gitnexus-mini-pill", root).forEach((node) => {
      const raw = String(node.textContent || "").trim();
      if (!raw) return;
      const ascii = cleanText(raw);
      if (ascii !== raw || /A.|Ãƒ|Ã‚|ï¿½/.test(raw)) {
        const match = fixes.find(([rx]) => rx.test(raw) || rx.test(ascii));
        node.textContent = match ? match[1] : (ascii || "TURN");
      }
    });

    qa("*", root).forEach((node) => {
      if (node.children.length) return;
      const raw = String(node.textContent || "").trim();
      if (!raw || raw.length > 32) return;
      if (/[^\x00-\x7F]/.test(raw) || /A.|Ãƒ|Ã‚|ï¿½/.test(raw)) {
        const ascii = cleanText(raw);
        const match = fixes.find(([rx]) => rx.test(raw) || rx.test(ascii));
        if (match) node.textContent = match[1];
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

    const candidates = [
      "[data-gn-open-big-hud]",
      "[data-gn-open-big]",
      "[data-gn-open-hud]",
      "[data-gitnexus-open-big]",
      "#gitnexus-open-big-hud"
    ];

    for (const sel of candidates) {
      const node = q(sel);
      if (node && !node.closest("#" + DOCK_ID)) {
        try { node.click(); return; } catch (_) {}
      }
    }

    window.dispatchEvent(new CustomEvent("gitnexus:open-big-hud"));
  }

  function dockGeometry() {
    const leftRail = qa("aside, section, article, div")
      .map((node) => ({ node, rect: node.getBoundingClientRect(), text: String(node.textContent || "").toUpperCase() }))
      .filter((item) =>
        item.rect.left >= -4 &&
        item.rect.left < 90 &&
        item.rect.width >= 220 &&
        item.rect.width <= 390 &&
        item.text.includes("NEURAL ACTIVITY")
      )
      .sort((a, b) => (b.rect.width * b.rect.height) - (a.rect.width * a.rect.height))[0];

    const neural = leftRail ? leftRail.rect : null;

    const footer = qa("footer, section, div")
      .map((node) => ({ node, rect: node.getBoundingClientRect(), text: String(node.textContent || "").toUpperCase() }))
      .filter((item) => item.text.includes("GOVERNANCE") && item.text.includes("SYSTEM BUS"))
      .sort((a, b) => b.rect.top - a.rect.top)[0];

    const footerTop = footer && footer.rect.top > window.innerHeight * 0.55 ? footer.rect.top : window.innerHeight - 50;
    const left = neural ? Math.max(6, neural.left) : 8;
    const width = neural ? Math.max(260, neural.width) : 310;
    const top = neural ? Math.min(neural.bottom + 12, footerTop - 260) : Math.round(window.innerHeight * 0.60);
    const height = Math.max(240, footerTop - top - 10);

    return { left, top, width, height };
  }

  function positionDock(dock) {
    const g = dockGeometry();
    dock.style.position = "fixed";
    dock.style.left = g.left + "px";
    dock.style.top = g.top + "px";
    dock.style.width = g.width + "px";
    dock.style.height = g.height + "px";
    dock.style.zIndex = "620";
    dock.style.display = "block";
    dock.style.visibility = "visible";
    dock.style.opacity = "1";
  }

  function ensureDock() {
    let dock = document.getElementById(DOCK_ID);
    if (!dock) {
      dock = document.createElement("section");
      dock.id = DOCK_ID;
      document.body.appendChild(dock);
    }

    dock.dataset.gitnexusMini = VERSION;
    dock.className = "gitnexus-geometric-mini-dock";
    positionDock(dock);

    const old = q(".gitnexus-geometric-mini", dock);
    if (!old) {
      dock.innerHTML = `
        <section class="gitnexus-geometric-mini" data-version="${VERSION}">
          <div class="gitnexus-geo-head">
            <div class="gitnexus-geo-brand">
              <span class="gitnexus-geo-orb"></span>
              <div>
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

      q(".gitnexus-geo-open", dock)?.addEventListener("click", openBigHud);
      q(".gitnexus-geo-canvas-button", dock)?.addEventListener("click", openBigHud);
    }

    return dock;
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

  function drawGeometry() {
    const canvas = document.getElementById("gitnexus-geometric-mini-canvas");
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    const w = Math.max(180, Math.floor(rect.width));
    const h = Math.max(160, Math.floor(rect.height));

    if (canvas.width !== Math.floor(w * dpr) || canvas.height !== Math.floor(h * dpr)) {
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#020712";
    ctx.fillRect(0, 0, w, h);

    const counts = getCounts();
    const now = performance.now() * 0.00022;
    const rnd = seededRandom(counts.files + counts.edges);

    const cx = w * 0.50;
    const cy = h * 0.50;
    const maxR = Math.min(w, h) * 0.36;

    const glow = ctx.createRadialGradient(cx, cy, 2, cx, cy, maxR * 1.55);
    glow.addColorStop(0, "rgba(0, 240, 255, 0.18)");
    glow.addColorStop(0.36, "rgba(255, 171, 0, 0.08)");
    glow.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, w, h);

    const nodeCount = Math.min(150, Math.max(72, Math.floor(counts.files / 8)));
    const nodes = [];

    for (let i = 0; i < nodeCount; i++) {
      const arm = i % 9;
      const base = (arm / 9) * Math.PI * 2 + now;
      const radius = maxR * (0.15 + 0.86 * Math.pow(i / nodeCount, 0.70));
      const jitter = (rnd() - 0.5) * 0.78;
      const angle = base + jitter + Math.sin(now * 2 + i * 0.17) * 0.18;
      nodes.push({
        x: cx + Math.cos(angle) * radius,
        y: cy + Math.sin(angle) * radius,
        r: 1.4 + rnd() * 3.4,
        hot: i % 11 === 0,
        gold: i % 7 === 0
      });
    }

    ctx.lineWidth = 1;
    for (let i = 0; i < nodes.length; i++) {
      const n = nodes[i];
      if (i % 2 === 0) {
        ctx.strokeStyle = n.gold ? "rgba(255, 171, 0, 0.38)" : "rgba(0, 240, 255, 0.22)";
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(n.x, n.y);
        ctx.stroke();
      }
      if (i % 13 === 0) {
        const m = nodes[(i + 23) % nodes.length];
        ctx.strokeStyle = "rgba(0, 240, 255, 0.08)";
        ctx.beginPath();
        ctx.moveTo(n.x, n.y);
        ctx.lineTo(m.x, m.y);
        ctx.stroke();
      }
    }

    ctx.shadowBlur = 18;
    ctx.shadowColor = "rgba(0, 240, 255, 0.5)";
    for (const n of nodes) {
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
    ctx.shadowColor = "rgba(255, 171, 0, 0.7)";
    ctx.fillStyle = "#ffaa00";
    ctx.beginPath();
    ctx.arc(cx, cy, 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.shadowBlur = 16;
    ctx.shadowColor = "rgba(0, 240, 255, 0.8)";
    ctx.strokeStyle = "#55f7ff";
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.arc(cx, cy, 15, now, Math.PI * 2 + now);
    ctx.stroke();

    requestAnimationFrame(drawGeometry);
  }

  function boot() {
    sanitizeToolbarLabels(document);
    const dock = ensureDock();
    positionDock(dock);

    if (!window.__gitnexusGeometricMiniDrawing) {
      window.__gitnexusGeometricMiniDrawing = true;
      requestAnimationFrame(drawGeometry);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener("load", boot);
  window.addEventListener("resize", boot);
  window.setInterval(boot, 1800);
})();