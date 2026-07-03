const laneRoot = document.getElementById("lanes");
const output = document.getElementById("output");
const statusEl = document.getElementById("status");

function setText(id, value) {
  document.getElementById(id).textContent = value ?? "unknown";
}

function writeOutput(text) {
  output.textContent = text || "No output.";
}

async function loadSurfaceState() {
  const contract = await window.nexus.getContract();
  document.getElementById("boundary").textContent = contract.boundary;

  laneRoot.innerHTML = "";
  for (const lane of contract.allowlistedCommands) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = lane;
    button.addEventListener("click", async () => {
      statusEl.textContent = `running ${lane}`;
      const result = await window.nexus.runLane(lane);
      writeOutput(result.stdout || result.stderr);
      statusEl.textContent = result.code === 0 ? "pass" : "failed";
    });
    laneRoot.appendChild(button);
  }

  const raw = await window.nexus.readSurface("reports/tui/nexus_tui_surface_latest.json");
  const state = JSON.parse(raw);
  setText("health", state.health?.health_score);
  setText("pressure", state.health?.evidence_pressure);
  setText("graph", state.graph?.status);
  setText("next", state.health?.next_action);
  writeOutput(JSON.stringify(state, null, 2));
  statusEl.textContent = "ready";
}

loadSurfaceState().catch((error) => {
  statusEl.textContent = "blocked";
  writeOutput(error.stack || error.message);
});
