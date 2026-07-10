(() => {
  const FULL_PATH = "../../neural_activity/index.html";
  const EMBED_PATH = "../../neural_activity/index.html?embed=1&preview=1&aa=1";
  const VERSION = "close-aa";
  let repoGraphRefreshHandle = null;

  function imp(el, prop, value) {
    if (!el) return;
    el.style.setProperty(prop, value, "important");
  }

  function block(el) {
    imp(el, "display", "block");
    imp(el, "visibility", "visible");
    imp(el, "opacity", "1");
    return el;
  }

  function make(tag, cls) {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    return block(el);
  }

  function openNeuralActivity() {
    const popup = window.open(
      FULL_PATH,
      "nexus_neural_activity",
      "width=1280,height=820,resizable=yes,scrollbars=no,menubar=no,toolbar=no,location=no,status=no"
    );
    if (popup) {
      setTimeout(() => pushRepoGraph(popup), 400);
      setTimeout(() => pushRepoGraph(popup), 1200);
      setTimeout(() => fireNeuralImpulse(popup, "popout-open"), 1400);
    }
    if (!popup) window.location.href = FULL_PATH;
  }

  async function loadRepoGraph() {
    if (!window.nexus || !window.nexus.getNeuralRepoGraph) return null;
    try {
      return await window.nexus.getNeuralRepoGraph();
    } catch (_error) {
      return null;
    }
  }

  async function pushRepoGraph(targetWindow) {
    const graph = await loadRepoGraph();
    if (!graph || !targetWindow || targetWindow.closed) return;
    targetWindow.postMessage({ type: "NEXUS_NEURAL_REPO_GRAPH", graph }, "*");
  }

  function fireNeuralImpulse(targetWindow, reason) {
    if (!targetWindow || targetWindow.closed) return;
    targetWindow.postMessage({ type: "NEXUS_NEURAL_TRIGGER_IMPULSE", reason: reason || "nexus-bridge" }, "*");
  }

  function setLight(light, ok) {
    if (!light) return;
    light.classList.remove("is-green", "is-red");
    light.classList.add(ok ? "is-green" : "is-red");
    imp(light, "background", ok ? "#78ff9a" : "#ff3355");
    imp(light, "box-shadow", ok ? "0 0 10px #78ff9a" : "0 0 10px #ff3355");
    light.title = ok ? "Live" : "Loading";
    light.setAttribute("aria-label", ok ? "Neural Activity live" : "Neural Activity loading");
  }

  function claimHost(host) {
    host.dataset.neuralActivityMounted = VERSION;
    host.dataset.neuralActivityPanel = "runtime-mounted";
    host.classList.add("neural-activity-panel");

    block(host);
    imp(host, "position", "relative");
    imp(host, "height", "clamp(300px, 36vh, 430px)");
    imp(host, "min-height", "clamp(300px, 36vh, 430px)");
    imp(host, "max-height", "clamp(300px, 36vh, 430px)");
    imp(host, "padding", "0");
    imp(host, "overflow", "hidden");
    imp(host, "box-sizing", "border-box");
    imp(host, "background", "linear-gradient(180deg, rgba(0,240,255,0.08), rgba(0,0,0,0.10))");
  }

  function headerStyle(header, titleRow, light, title, button) {
    block(header);
    imp(header, "position", "absolute");
    imp(header, "top", "8px");
    imp(header, "left", "8px");
    imp(header, "right", "8px");
    imp(header, "height", "30px");
    imp(header, "display", "grid");
    imp(header, "grid-template-columns", "minmax(0, 1fr) 58px");
    imp(header, "align-items", "center");
    imp(header, "gap", "8px");
    imp(header, "z-index", "1000");
    imp(header, "box-sizing", "border-box");

    imp(titleRow, "display", "inline-flex");
    imp(titleRow, "align-items", "center");
    imp(titleRow, "gap", "7px");
    imp(titleRow, "min-width", "0");
    imp(titleRow, "height", "100%");
    imp(titleRow, "padding", "0 8px");
    imp(titleRow, "border", "1px solid rgba(0,240,255,0.25)");
    imp(titleRow, "background", "rgba(1,2,4,0.70)");
    imp(titleRow, "box-shadow", "inset 0 0 18px rgba(0,240,255,0.09)");

    block(light);
    imp(light, "width", "9px");
    imp(light, "height", "9px");
    imp(light, "min-width", "9px");
    imp(light, "border-radius", "999px");
    imp(light, "border", "1px solid rgba(255,255,255,0.25)");
    setLight(light, false);

    block(title);
    imp(title, "color", "#00f0ff");
    imp(title, "font-size", "10px");
    imp(title, "line-height", "1");
    imp(title, "letter-spacing", "0.8px");
    imp(title, "text-transform", "uppercase");
    imp(title, "text-shadow", "0 0 8px rgba(0,240,255,0.35)");
    imp(title, "white-space", "nowrap");
    imp(title, "overflow", "hidden");
    imp(title, "text-overflow", "ellipsis");

    block(button);
    imp(button, "height", "30px");
    imp(button, "width", "58px");
    imp(button, "padding", "0");
    imp(button, "border", "1px solid rgba(0,240,255,0.62)");
    imp(button, "background", "linear-gradient(135deg, rgba(0,240,255,0.22), rgba(0,0,0,0.20))");
    imp(button, "color", "#00f0ff");
    imp(button, "text-transform", "uppercase");
    imp(button, "letter-spacing", "1px");
    imp(button, "font-size", "9px");
    imp(button, "cursor", "pointer");
  }

  function bodyStyle(body) {
    block(body);
    imp(body, "position", "absolute");
    imp(body, "left", "8px");
    imp(body, "right", "8px");
    imp(body, "top", "46px");
    imp(body, "bottom", "8px");
    imp(body, "width", "auto");
    imp(body, "height", "auto");
    imp(body, "min-height", "160px");
    imp(body, "overflow", "hidden");
    imp(body, "border", "1px solid rgba(0,240,255,0.38)");
    imp(body, "background", "#010204");
    imp(body, "box-shadow", "inset 0 0 40px rgba(0,240,255,0.12), 0 0 18px rgba(0,240,255,0.08)");
    imp(body, "box-sizing", "border-box");
    imp(body, "z-index", "20");
  }

  function frameStyle(frame) {
    block(frame);
    imp(frame, "position", "absolute");
    imp(frame, "left", "0");
    imp(frame, "top", "0");
    imp(frame, "right", "0");
    imp(frame, "bottom", "0");
    imp(frame, "width", "100%");
    imp(frame, "height", "100%");
    imp(frame, "min-width", "100%");
    imp(frame, "min-height", "100%");
    imp(frame, "border", "0");
    imp(frame, "background", "#010204");
    imp(frame, "z-index", "30");
  }

  function mountPanel() {
    const host = document.querySelector(".left-stack > .empty-selector-panel");
    if (!host) return;

    claimHost(host);

    const header = make("div", "neural-activity-header");
    const titleRow = make("div", "neural-activity-title-wrap");
    const light = make("span", "neural-activity-light is-red");
    const title = make("div", "neural-activity-title");
    title.textContent = "NEURAL ACTIVITY";

    const button = make("button", "neural-activity-popout");
    button.type = "button";
    button.textContent = "OPEN";
    button.addEventListener("click", openNeuralActivity);

    const body = make("div", "neural-activity-body");
    bodyStyle(body);

    const frame = document.createElement("iframe");
    frame.className = "neural-activity-live-frame";
    frame.title = "Live Neural Activity Preview";
    frame.loading = "eager";
    frame.src = EMBED_PATH + "&t=" + Date.now();
    frame.setAttribute("allow", "fullscreen");
    frame.addEventListener("load", () => setLight(light, true));
    frame.addEventListener("load", () => {
      pushRepoGraph(frame.contentWindow);
      fireNeuralImpulse(frame.contentWindow, "mini-load");
    });
    frame.addEventListener("error", () => setLight(light, false));
    frameStyle(frame);

    titleRow.appendChild(light);
    titleRow.appendChild(title);
    header.appendChild(titleRow);
    header.appendChild(button);
    body.appendChild(frame);
    host.replaceChildren(header, body);
    body.addEventListener("pointerdown", () => {
      pushRepoGraph(frame.contentWindow);
      fireNeuralImpulse(frame.contentWindow, "mini-pointer");
    });

    headerStyle(header, titleRow, light, title, button);
    bodyStyle(body);
    frameStyle(frame);
  }

  function boot() {
    mountPanel();
    requestAnimationFrame(mountPanel);
    setTimeout(mountPanel, 150);
    setTimeout(mountPanel, 600);
    if (!repoGraphRefreshHandle) {
      repoGraphRefreshHandle = setInterval(() => {
        document.querySelectorAll(".neural-activity-live-frame").forEach((frame) => pushRepoGraph(frame.contentWindow));
      }, 8000);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener("load", boot);
  window.addEventListener("resize", mountPanel);
  window.addEventListener("focus", () => {
    document.querySelectorAll(".neural-activity-live-frame").forEach((frame) => pushRepoGraph(frame.contentWindow));
  });
})();
