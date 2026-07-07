(() => {
  const PATCH = "nexus-ui-balanced-chat-layout-v0-1-6";
  if (window.__nexusUiBalancedChatLayoutV016) return;
  window.__nexusUiBalancedChatLayoutV016 = true;

  function style() {
    if (document.getElementById(PATCH + "-style")) return;
    const s = document.createElement("style");
    s.id = PATCH + "-style";
    s.textContent = `
      :root {
        --nexus-side-rail-width: clamp(240px, 17vw, 300px);
        --nexus-left-spacer-height: clamp(210px, 24vh, 310px);
        --nexus-center-chat-max-width: min(1240px, calc(100vw - (2 * var(--nexus-side-rail-width)) - 56px));
      }
      [data-nexus-hidden-lane-context="true"] { display: none !important; }
      .nexus-left-blank-spacer {
        display:block!important;
        min-height:var(--nexus-left-spacer-height)!important;
        height:var(--nexus-left-spacer-height)!important;
        margin-top:12px!important;
        border:1px solid rgba(0,240,255,.28)!important;
        background:linear-gradient(135deg,rgba(0,240,255,.035),rgba(0,0,0,.18)),rgba(0,12,28,.34)!important;
        box-shadow:inset 0 0 22px rgba(0,240,255,.045)!important;
        box-sizing:border-box!important;
      }
      .nexus-balanced-side-rail {
        width:var(--nexus-side-rail-width)!important;
        min-width:var(--nexus-side-rail-width)!important;
        max-width:var(--nexus-side-rail-width)!important;
        box-sizing:border-box!important;
      }
      .nexus-balanced-center-chat {
        width:100%!important;
        max-width:var(--nexus-center-chat-max-width)!important;
        margin-left:auto!important;
        margin-right:auto!important;
        box-sizing:border-box!important;
      }
      .nexus-balanced-three-column-grid {
        grid-template-columns:var(--nexus-side-rail-width) minmax(720px,1fr) var(--nexus-side-rail-width)!important;
      }
    `;
    document.head.appendChild(s);
  }

  function txt(n){ return (n && n.textContent ? n.textContent : "").replace(/\s+/g," ").trim(); }
  function has(n, t){ return txt(n).toUpperCase().includes(t.toUpperCase()); }

  function findText(t) {
    const nodes = Array.from(document.querySelectorAll("body *"));
    return nodes.find(n => Array.from(n.childNodes || []).filter(c => c.nodeType === Node.TEXT_NODE).map(c => c.textContent || "").join(" ").toUpperCase().includes(t.toUpperCase()))
      || nodes.find(n => has(n,t));
  }

  function panel(n) {
    let c = n;
    for (let i=0; c && i<8; i++, c=c.parentElement) {
      if (!c.getBoundingClientRect) continue;
      const r = c.getBoundingClientRect();
      const k = `${c.className || ""} ${c.id || ""} ${c.getAttribute("role") || ""}`.toLowerCase();
      if ((k.includes("panel") || k.includes("card") || k.includes("box") || k.includes("context") || k.includes("lane") || k.includes("region")) &&
          r.width > 120 && r.width < 430 && r.height > 40 && r.height < 380) return c;
    }
    return n;
  }

  function column(n) {
    let c = n;
    for (let i=0; c && i<10; i++, c=c.parentElement) {
      if (!c.getBoundingClientRect) continue;
      const r = c.getBoundingClientRect();
      if (r.height > 260 && r.width > 140 && r.width < 540) return c;
    }
    return null;
  }

  function common(a,b) {
    if (!a || !b) return null;
    const s = new Set(); for (let x=a; x; x=x.parentElement) s.add(x);
    for (let y=b; y; y=y.parentElement) if (s.has(y)) return y;
    return null;
  }

  function center() {
    const seed = document.querySelector('input[placeholder*="Ask NEX" i], textarea[placeholder*="Ask NEX" i], input[placeholder*="HUMAN CHAT" i], textarea[placeholder*="HUMAN CHAT" i]')
      || findText("HUMAN CHAT") || findText("NEX AI OUTPUT");
    if (!seed) return null;
    let c = seed;
    for (let i=0; c && i<12; i++, c=c.parentElement) {
      if (!c.getBoundingClientRect) continue;
      const r = c.getBoundingClientRect();
      if (r.width > 520 && r.height > 250) return c;
    }
    return seed.parentElement || seed;
  }

  function apply() {
    style();
    let leftRail = null;
    const laneSeed = document.querySelector('[data-panel*="lane-context" i], [id*="lane-context" i], [class*="lane-context" i]') || findText("LANE CONTEXT");
    if (laneSeed) {
      const p = panel(laneSeed);
      leftRail = column(p);
      p.setAttribute("data-nexus-hidden-lane-context", "true");
      if (leftRail && !leftRail.querySelector(".nexus-left-blank-spacer")) {
        const spacer = document.createElement("div");
        spacer.className = "nexus-left-blank-spacer";
        spacer.setAttribute("aria-hidden", "true");
        spacer.setAttribute("data-nexus-ui", "lane-context-spacer-v0.1.6");
        p.insertAdjacentElement("afterend", spacer);
      }
    }
    if (!leftRail) {
      const ps = findText("PROCESS LANES");
      leftRail = ps ? column(ps) : null;
    }
    const rightSeed = findText("HEALTH SCORE");
    const rightRail = rightSeed ? column(rightSeed) : null;
    const mid = center();

    if (leftRail) leftRail.classList.add("nexus-balanced-side-rail");
    if (rightRail) rightRail.classList.add("nexus-balanced-side-rail");
    if (mid) mid.classList.add("nexus-balanced-center-chat");

    const grid = common(leftRail, rightRail);
    if (grid && getComputedStyle(grid).display.includes("grid")) grid.classList.add("nexus-balanced-three-column-grid");

    document.documentElement.setAttribute("data-nexus-ui-balanced-chat-layout", "v0.1.6");
  }

  function run(){ requestAnimationFrame(() => { try { apply(); } catch(e) { console.warn("[Nexus UI Balance v0.1.6]", e); } }); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run, {once:true}); else run();
  new MutationObserver(run).observe(document.documentElement, {childList:true, subtree:true});
})();
