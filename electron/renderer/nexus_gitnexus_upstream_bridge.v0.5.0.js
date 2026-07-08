(() => {
  const VERSION = "v0.5.0";
  const MINI_ID = "gitnexus-core-left-dock";
  const HUD_ID = "gitnexus-upstream-hud";
  const STATE_KEY = "__nexusGitNexusUpstreamBridgeV050";

  const state = window[STATE_KEY] || (window[STATE_KEY] = {
    miniRaf: 0,
    resizeTimer: 0,
    activeUrl: "",
    frameLoaded: false
  });

  const GITNEXUS_WEB = "https://gitnexus.vercel.app";
  const LOCAL_SERVER = "http://localhost:4747";
  const PROJECT_NAME = "nexus-gate";

  function q(sel, root = document) { return root.querySelector(sel); }
  function qa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  function upstreamUrl() {
    const url = new URL(GITNEXUS_WEB + "/");
    url.searchParams.set("server", LOCAL_SERVER);
    url.searchParams.set("project", PROJECT_NAME);
    url.searchParams.set("skipGraph", "0");
    return url.toString();
  }

  function localWebUrl() {
    const url = new URL("http://localhost:5173/");
    url.searchParams.set("server", LOCAL_SERVER);
    url.searchParams.set("project", PROJECT_NAME);
    url.searchParams.set("skipGraph", "0");
    return url.toString();
  }

  function dockGeometry() {
    const neural = qa("aside, section, article, div")
      .map((node) => ({ rect: node.getBoundingClientRect(), text: String(node.textContent || "").toUpperCase() }))
      .filter((item) =>
        item.rect.width >= 220 &&
        item.rect.width <= 420 &&
        item.rect.left >= -12 &&
        item.rect.left < 120 &&
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
    const top = neural ? Math.min(neural.bottom + 12, footerTop - 250) : Math.round(window.innerHeight * 0.60);
    const height = Math.max(220, footerTop - top - 10);
    return { left: Math.round(left), top: Math.round(top), width: Math.round(width), height: Math.round(height) };
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
    dock.className = "gnx-up-mini-dock";
    dock.dataset.version = VERSION;
    dock.style.left = geo.left + "px";
    dock.style.top = geo.top + "px";
    dock.style.width = geo.width + "px";
    dock.style.height = geo.height + "px";

    if (!dock.querySelector(".gnx-up-mini")) {
      dock.innerHTML = `
        <section class="gnx-up-mini">
          <div class="gnx-up-mini-head">
            <div class="gnx-up-mini-brand">
              <span class="gnx-up-orb"></span>
              <div>
                <div class="gnx-up-title">GITNEXUS</div>
                <div class="gnx-up-sub">UPSTREAM WEB BRIDGE</div>
              </div>
            </div>
            <button class="gnx-up-open" type="button">OPEN</button>
          </div>
          <button class="gnx-up-mini-body" type="button" title="Open real GitNexus Web UI">
            <canvas id="gnx-up-mini-canvas"></canvas>
            <span class="gnx-up-caption">REAL GITNEXUS HUD</span>
          </button>
        </section>
      `;
      q(".gnx-up-open", dock)?.addEventListener("click", openHud);
      q(".gnx-up-mini-body", dock)?.addEventListener("click", openHud);
    }

    return dock;
  }

  function fitCanvas(canvas) {
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    const w = Math.max(180, Math.floor(rect.width));
    const h = Math.max(145, Math.floor(rect.height));
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

  function drawMini(time) {
    const canvas = document.getElementById("gnx-up-mini-canvas");
    const fit = fitCanvas(canvas);
    if (fit) {
      const { ctx, w, h } = fit;
      const cx = w / 2;
      const cy = h / 2;
      const r0 = Math.min(w, h) * 0.34;
      const t = (time || performance.now()) * 0.00025;

      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "#020712";
      ctx.fillRect(0, 0, w, h);

      const glow = ctx.createRadialGradient(cx, cy, 1, cx, cy, r0 * 1.9);
      glow.addColorStop(0, "rgba(0,240,255,0.15)");
      glow.addColorStop(0.36, "rgba(255,170,0,0.10)");
      glow.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = glow;
      ctx.fillRect(0, 0, w, h);

      const nodes = [];
      const count = 120;
      for (let i = 0; i < count; i++) {
        const arm = i % 5;
        const angle = (arm / 5) * Math.PI * 2 + t + Math.sin(i * 0.31) * 0.35;
        const radius = r0 * (0.16 + Math.sqrt(i / count) * 0.86);
        nodes.push({
          x: cx + Math.cos(angle + i * 0.023) * radius,
          y: cy + Math.sin(angle + i * 0.023) * radius,
          r: i % 17 === 0 ? 4.2 : 2.1 + (i % 5) * 0.25,
          hot: i % 11 === 0
        });
      }

      ctx.lineWidth = 0.8;
      nodes.forEach((n, i) => {
        if (i % 2 !== 0) return;
        ctx.strokeStyle = i % 7 === 0 ? "rgba(255,170,0,0.30)" : "rgba(0,240,255,0.13)";
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(n.x, n.y);
        ctx.stroke();
      });

      nodes.forEach((n, i) => {
        ctx.shadowBlur = n.hot ? 18 : 9;
        ctx.shadowColor = n.hot ? "rgba(255,170,0,0.70)" : "rgba(85,247,255,0.45)";
        ctx.fillStyle = i % 7 === 0 ? "#ffaa00" : i % 3 === 0 ? "#7dff4d" : "#55f7ff";
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fill();
      });

      ctx.shadowBlur = 24;
      ctx.shadowColor = "rgba(255,170,0,0.80)";
      ctx.fillStyle = "#ffaa00";
      ctx.beginPath();
      ctx.arc(cx, cy, 7, 0, Math.PI * 2);
      ctx.fill();
    }

    state.miniRaf = requestAnimationFrame(drawMini);
  }

  function startMini() {
    if (state.miniRaf) return;
    state.miniRaf = requestAnimationFrame(drawMini);
  }

  function ensureHud() {
    let hud = document.getElementById(HUD_ID);
    if (hud) return hud;

    hud = document.createElement("section");
    hud.id = HUD_ID;
    hud.className = "gnx-up-hud is-hidden";
    hud.innerHTML = `
      <div class="gnx-up-hud-top">
        <div class="gnx-up-hud-brand">
          <span class="gnx-up-orb"></span>
          <div>
            <div class="gnx-up-hud-title">GITNEXUS</div>
            <div class="gnx-up-hud-sub">REAL WEB UI / LOCAL BRIDGE MODE</div>
          </div>
        </div>
        <div class="gnx-up-url" data-gnx-url>bridge: ${LOCAL_SERVER}</div>
        <button class="gnx-up-btn" data-gnx-local-web>LOCAL WEB</button>
        <button class="gnx-up-btn" data-gnx-remote-web>REMOTE WEB</button>
        <button class="gnx-up-btn" data-gnx-reload>RELOAD</button>
        <button class="gnx-up-btn" data-gnx-popout>POP OUT</button>
        <button class="gnx-up-btn gnx-up-close" data-gnx-close>CLOSE</button>
      </div>
      <div class="gnx-up-frame-wrap">
        <iframe
          class="gnx-up-frame"
          referrerpolicy="no-referrer"
          allow="clipboard-read; clipboard-write"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-downloads"
        ></iframe>
        <div class="gnx-up-help" data-gnx-help>
          <b>GitNexus bridge mode</b>
          <span>Run <code>scripts\\nexus_gitnexus_upstream.ps1 serve</code> in a second terminal, then reload.</span>
          <span>GitNexus UI is intentionally isolated from NexusGate runtime.</span>
        </div>
      </div>
      <div class="gnx-up-foot">
        <span>Evidence only.</span>
        <span>No NexusCell policy change.</span>
        <span>No shell execution from model output.</span>
      </div>
    `;

    document.body.appendChild(hud);

    q("[data-gnx-close]", hud)?.addEventListener("click", closeHud);
    q("[data-gnx-reload]", hud)?.addEventListener("click", () => loadFrame(state.activeUrl || upstreamUrl()));
    q("[data-gnx-remote-web]", hud)?.addEventListener("click", () => loadFrame(upstreamUrl()));
    q("[data-gnx-local-web]", hud)?.addEventListener("click", () => loadFrame(localWebUrl()));
    q("[data-gnx-popout]", hud)?.addEventListener("click", () => {
      const url = state.activeUrl || upstreamUrl();
      window.open(url, "gitnexus-upstream", "popup,width=1500,height=950");
    });

    const frame = q("iframe", hud);
    frame?.addEventListener("load", () => {
      state.frameLoaded = true;
      const help = q("[data-gnx-help]", hud);
      if (help) help.classList.add("is-minimized");
    });

    return hud;
  }

  function loadFrame(url) {
    const hud = ensureHud();
    const frame = q("iframe", hud);
    const urlNode = q("[data-gnx-url]", hud);
    state.activeUrl = url;
    state.frameLoaded = false;
    if (urlNode) urlNode.textContent = url;
    if (frame) frame.src = url;
    const help = q("[data-gnx-help]", hud);
    if (help) help.classList.remove("is-minimized");
  }

  function openHud() {
    const hud = ensureHud();
    hud.classList.remove("is-hidden");
    if (!state.activeUrl) loadFrame(upstreamUrl());
  }

  function closeHud() {
    const hud = document.getElementById(HUD_ID);
    if (hud) hud.classList.add("is-hidden");
  }

  function scheduleLayout() {
    if (state.resizeTimer) clearTimeout(state.resizeTimer);
    state.resizeTimer = setTimeout(() => ensureMiniDock(), 100);
  }

  function bindKeys() {
    if (window.__gitnexusUpstreamBridgeKeysV050) return;
    window.__gitnexusUpstreamBridgeKeysV050 = true;

    window.addEventListener("keydown", (ev) => {
      const hud = document.getElementById(HUD_ID);
      const open = hud && !hud.classList.contains("is-hidden");
      if (open && ev.key === "Escape") {
        closeHud();
        ev.preventDefault();
      }
    });
  }

  function boot() {
    ensureMiniDock();
    ensureHud();
    startMini();
    bindKeys();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener("load", boot);
  window.addEventListener("resize", scheduleLayout);

  window.nexusOpenGitNexus = openHud;
  window.nexusCloseGitNexus = closeHud;
})();