const laneRoot = document.getElementById("lanes");
const output = document.getElementById("output");
const statusEl = document.getElementById("status");
const consoleStream = document.getElementById("console-stream");
const activeLane = document.getElementById("active-lane");
const operatorForm = document.getElementById("operator-form");
const operatorCommand = document.getElementById("operator-command");

let allowlistedCommands = [];

const laneIcons = {
  evolve: "EV",
  interface: "IF",
  feedback: "FB",
  heal: "HL",
  status: "ST",
  compact: "CP",
  interconnect: "IC",
  runtime: "RT",
  pack: "PK",
  reflect: "RF",
  domain: "DM"
};

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) {
    node.textContent = value ?? "unknown";
  }
}

function safeText(value) {
  return String(value || "").replace(/[<>&]/g, (ch) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[ch]));
}

function writeOutput(text) {
  output.textContent = text || "No output.";
  output.scrollTop = output.scrollHeight;
}

function pushConsole(level, text) {
  const row = document.createElement("p");
  row.innerHTML = `<b>[${safeText(level)}]</b> ${safeText(text)}`;
  consoleStream.appendChild(row);
  while (consoleStream.children.length > 12) {
    consoleStream.removeChild(consoleStream.firstElementChild);
  }
  consoleStream.scrollTop = consoleStream.scrollHeight;
}

function setClock() {
  document.getElementById("system-time").textContent = new Date().toISOString().slice(0, 19).replace("T", " ");
}

function normalizeHealth(value) {
  if (value === null || value === undefined) return "unknown";
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return String(value);
  return numeric <= 1 ? (numeric * 100).toFixed(1) : numeric.toFixed(1);
}

function setBuffer(value) {
  const numeric = Math.max(0, Math.min(100, Number(value) || 0));
  const fill = document.getElementById("buffer-fill");
  const label = document.getElementById("buffer-value");
  if (fill) fill.style.width = `${numeric}%`;
  if (label) label.textContent = `${numeric}%`;
}

async function runGovernedLane(lane) {
  if (!allowlistedCommands.includes(lane)) {
    pushConsole("WARN", `Lane '${lane}' is not allowlisted in Electron.`);
    writeOutput(JSON.stringify({
      type: "blocked_lane_request",
      lane,
      allowlistedCommands,
      boundary: "Electron may request only lanes declared by the Electron contract. This is not arbitrary shell access."
    }, null, 2));
    return;
  }

  activeLane.textContent = lane;
  statusEl.textContent = "running";
  setBuffer(20);
  pushConsole("NEXUS", `Lane '${lane}' engaged. Initializing governed run...`);

  try {
    setBuffer(45);
    const result = await window.nexus.runLane(lane);
    setBuffer(result.code === 0 ? 100 : 0);
    writeOutput(result.stdout || result.stderr || "No lane output.");
    statusEl.textContent = result.code === 0 ? "stable" : "blocked";
    pushConsole(result.code === 0 ? "NEXUS" : "WARN", result.code === 0 ? "Lane completed. Evidence refreshed." : "Lane returned non-zero status.");
  } catch (error) {
    setBuffer(0);
    statusEl.textContent = "blocked";
    writeOutput(error.stack || error.message);
    pushConsole("WARN", "Lane execution failed inside governed bridge.");
  }
}

function renderLanes(commands) {
  laneRoot.innerHTML = "";
  commands.forEach((lane, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `lane-button${index === 0 ? " active" : ""}`;

    const icon = document.createElement("span");
    icon.className = "lane-icon";
    icon.textContent = laneIcons[lane] || "--";

    const label = document.createElement("span");
    label.textContent = lane;

    const arrow = document.createElement("span");
    arrow.className = "lane-arrow";
    arrow.textContent = ">";

    button.appendChild(icon);
    button.appendChild(label);
    button.appendChild(arrow);

    button.addEventListener("click", async () => {
      document.querySelectorAll(".lane-button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      await runGovernedLane(lane);
    });

    laneRoot.appendChild(button);
  });
}

function buildFallbackState(context) {
  return {
    health: {
      health_score: context.health?.health_score,
      evidence_pressure: context.health?.evidence_pressure,
      dominant_pressure: context.health?.dominant_pressure_source,
      next_action: context.next_action
    },
    graph: {
      status: context.interconnect_graph?.status || "context-fallback",
      node_count: context.interconnect_graph?.node_count || 0,
      edge_count: context.interconnect_graph?.edge_count || 0,
      checks: [],
      missing_evidence: []
    },
    fallback_surface: "state/ai_feedback_context_latest.json",
    note: "TUI surface is missing; run .\\scripts\\nexus.ps1 tui and use /surface or /snapshot for full dashboard state."
  };
}

async function loadSurfaceState() {
  setClock();
  setInterval(setClock, 1000);
  setBuffer(10);

  const contract = await window.nexus.getContract();
  allowlistedCommands = contract.allowlistedCommands || [];
  renderLanes(allowlistedCommands);
  setBuffer(25);

  let state;
  try {
    const surface = "reports/tui/nexus_tui_surface_latest.json";
    if (!await window.nexus.surfaceExists(surface)) {
      throw new Error("optional TUI surface is not present");
    }
    const raw = await window.nexus.readSurface(surface);
    state = JSON.parse(raw);
    setBuffer(70);
  } catch (error) {
    pushConsole("WARN", "TUI surface missing. Hydrating from AI feedback context.");
    const raw = await window.nexus.readSurface("state/ai_feedback_context_latest.json");
    const context = JSON.parse(raw);
    state = buildFallbackState(context);
    setBuffer(55);
  }

  const health = normalizeHealth(state.health?.health_score);
  setText("health", health);
  setText("pressure", state.health?.evidence_pressure);
  setText("dominant", state.health?.dominant_pressure);
  setText("trend", state.graph?.status);
  setText("graph", state.graph?.status);
  setText("next", state.health?.next_action);
  setText("link-count", state.graph?.edge_count);
  setText("graph-health", state.graph?.status);
  setText("reflection-count", state.graph?.node_count);
  setText("insight-count", state.graph?.checks?.length ?? 0);
  setText("heal-count", state.graph?.missing_evidence?.length ?? 0);
  setText("note-count", 3);
  setText("error-count", 0);
  writeOutput(JSON.stringify(state, null, 2));
  pushConsole("NEXUS", "Context loaded. Governance strict. Health baseline synchronized.");
  pushConsole("AI", "Summary ready. AI handoff package is available.");
  statusEl.textContent = "stable";
  document.body.dataset.ready = "true";
  setBuffer(100);
}

document.getElementById("refresh")?.addEventListener("click", () => {
  pushConsole("AI", "Latest handoff surfaces are already loaded.");
  setBuffer(100);
});

operatorCommand?.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && event.ctrlKey) {
    event.preventDefault();
    operatorForm?.requestSubmit();
  }
});

operatorForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const raw = operatorCommand.value.trim();
  if (!raw) return;

  operatorCommand.value = "";
  pushConsole("HUMAN", raw);

  if (raw.startsWith("/study ")) {
    const summary = raw.slice("/study ".length).trim();
    writeOutput(JSON.stringify({
      type: "study_packet_draft",
      status: "pending_operator_packet_backend",
      summary,
      boundary: "Electron input is operator intent only. It does not self-authorize, mutate the repo, or run arbitrary shell."
    }, null, 2));
    setBuffer(100);
    return;
  }

  const lane = raw.startsWith("/") ? raw.slice(1).trim() : "";
  if (lane) {
    await runGovernedLane(lane);
    return;
  }

  writeOutput(JSON.stringify({
    type: "operator_note",
    status: "captured_in_ui_only",
    note: raw,
    boundary: "UI note is not durable repo memory until routed through a governed NEXUS lane."
  }, null, 2));
  setBuffer(100);
});

loadSurfaceState().catch((error) => {
  statusEl.textContent = "blocked";
  document.body.dataset.ready = "false";
  setBuffer(0);
  writeOutput(error.stack || error.message);
});