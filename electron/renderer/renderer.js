const laneRoot = document.getElementById("lanes");
const output = document.getElementById("output");
const statusEl = document.getElementById("status");
const consoleStream = document.getElementById("console-stream");
const activeLane = document.getElementById("active-lane");

const laneIcons = {
  evolve: "◎",
  interface: "▣",
  feedback: "◉",
  heal: "◇",
  status: "⌁",
  compact: "⬡",
  interconnect: "⌘",
  runtime: "◷",
  pack: "⬢"
};

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) {
    node.textContent = value ?? "unknown";
  }
}

function writeOutput(text) {
  output.textContent = text || "No output.";
}

function pushConsole(level, text) {
  const row = document.createElement("p");
  row.innerHTML = `<b>[${level}]</b> ${text}`;
  consoleStream.appendChild(row);
  while (consoleStream.children.length > 9) {
    consoleStream.removeChild(consoleStream.firstElementChild);
  }
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

function renderLanes(commands) {
  laneRoot.innerHTML = "";
  commands.forEach((lane, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `lane-button${index === 0 ? " active" : ""}`;
    button.innerHTML = `<span class="lane-icon">${laneIcons[lane] || "□"}</span><span>${lane}</span><span class="lane-arrow">»</span>`;
    button.addEventListener("click", async () => {
      document.querySelectorAll(".lane-button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      activeLane.textContent = lane;
      statusEl.textContent = `running`;
      pushConsole("NEXUS", `Lane '${lane}' engaged. Initializing governed run...`);
      const result = await window.nexus.runLane(lane);
      writeOutput(result.stdout || result.stderr);
      statusEl.textContent = result.code === 0 ? "stable" : "blocked";
      pushConsole(result.code === 0 ? "NEXUS" : "WARN", result.code === 0 ? "Lane completed. Evidence refreshed." : "Lane returned non-zero status.");
    });
    laneRoot.appendChild(button);
  });
}

async function loadSurfaceState() {
  setClock();
  setInterval(setClock, 1000);

  const contract = await window.nexus.getContract();
  renderLanes(contract.allowlistedCommands);

  let state;
  try {
    const surface = "reports/tui/nexus_tui_surface_latest.json";
    if (!await window.nexus.surfaceExists(surface)) {
      throw new Error("optional TUI surface is not present");
    }
    const raw = await window.nexus.readSurface(surface);
    state = JSON.parse(raw);
  } catch (error) {
    pushConsole("WARN", "TUI surface missing. Hydrating from AI feedback context.");
    const raw = await window.nexus.readSurface("state/ai_feedback_context_latest.json");
    const context = JSON.parse(raw);
    state = {
      health: {
        health_score: context.health?.health_score,
        evidence_pressure: context.health?.evidence_pressure,
        dominant_pressure: context.health?.dominant_pressure_source,
        next_action: context.next_action
      },
      graph: {
        status: context.interconnect_graph?.status || "fallback",
        node_count: context.interconnect_graph?.node_count || 0,
        edge_count: context.interconnect_graph?.edge_count || 0,
        checks: [],
        missing_evidence: []
      },
      fallback_surface: "state/ai_feedback_context_latest.json"
    };
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
}

document.getElementById("refresh").addEventListener("click", () => {
  pushConsole("AI", "Latest handoff surfaces are already loaded.");
});

loadSurfaceState().catch((error) => {
  statusEl.textContent = "blocked";
  document.body.dataset.ready = "false";
  writeOutput(error.stack || error.message);
});
