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
  pack: "PK"
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

function titleCase(value) {
  return String(value || "")
    .replace(/[._-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function normalizeHealth(value) {
  if (value === null || value === undefined) return "unknown";
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return String(value);
  return numeric <= 1 ? (numeric * 100).toFixed(1) : numeric.toFixed(1);
}

function statusWord(status) {
  const value = String(status || "").toLowerCase();
  if (value === "pass") return "PASS";
  if (value === "warn") return "WARN";
  if (value === "fail") return "FAIL";
  if (value === "present") return "PRESENT";
  if (value === "patched") return "PATCHED";
  if (value === "stable") return "STABLE";
  return String(status || "unknown").toUpperCase();
}

function summarizeJsonObject(data) {
  const lines = [];
  lines.push("HUMAN SUMMARY");
  lines.push("=============");

  if (data.system || data.version || data.status) {
    lines.push(`System: ${data.system || "NEXUS GATE"}`);
    if (data.version) lines.push(`Version: ${data.version}`);
    if (data.status) lines.push(`Status: ${statusWord(data.status)}`);
  }

  if (data.health) {
    lines.push("");
    lines.push("Health:");
    lines.push(`- Score: ${normalizeHealth(data.health.health_score)}`);
    lines.push(`- Evidence pressure: ${data.health.evidence_pressure || "unknown"}`);
    lines.push(`- Dominant pressure: ${data.health.dominant_pressure || data.health.dominant_pressure_source || "none"}`);
    if (data.health.next_action) lines.push(`- Next action: ${data.health.next_action}`);
  }

  if (data.graph) {
    lines.push("");
    lines.push("Graph / Interconnect:");
    lines.push(`- Status: ${data.graph.status || "unknown"}`);
    lines.push(`- Nodes: ${data.graph.node_count ?? 0}`);
    lines.push(`- Links: ${data.graph.edge_count ?? 0}`);
    if (Array.isArray(data.graph.missing_evidence) && data.graph.missing_evidence.length) {
      lines.push(`- Missing evidence: ${data.graph.missing_evidence.length}`);
    }
  }

  if (Array.isArray(data.checks)) {
    const pass = data.checks.filter((item) => item.status === "pass").length;
    const warn = data.checks.filter((item) => item.status === "warn").length;
    const fail = data.checks.filter((item) => item.status === "fail").length;
    lines.push("");
    lines.push("Checks:");
    lines.push(`- Passed: ${pass}`);
    lines.push(`- Warnings: ${warn}`);
    lines.push(`- Failed: ${fail}`);
    data.checks.slice(0, 10).forEach((item) => {
      lines.push(`  - ${titleCase(item.check)}: ${statusWord(item.status)}`);
    });
    if (data.checks.length > 10) {
      lines.push(`  - plus ${data.checks.length - 10} more checks in raw evidence`);
    }
  }

  if (Array.isArray(data.domains)) {
    lines.push("");
    lines.push(`Domains: ${data.domains.join(", ")}`);
  }

  if (Array.isArray(data.blocked_claims)) {
    lines.push("");
    lines.push("Blocked claims:");
    data.blocked_claims.forEach((item) => lines.push(`- ${titleCase(item)}`));
  }

  if (data.next_action) {
    lines.push("");
    lines.push(`Next action: ${data.next_action}`);
  }

  if (data.fallback_surface) {
    lines.push("");
    lines.push("Fallback:");
    lines.push(`- Source: ${data.fallback_surface}`);
    if (data.note) lines.push(`- Note: ${data.note}`);
  }

  if (data.boundary || data.claim_boundary || data.authority_boundary) {
    lines.push("");
    lines.push("Boundary:");
    lines.push(data.boundary || data.claim_boundary || data.authority_boundary);
  }

  return lines.join("\n");
}

function summarizeLogText(text) {
  const lines = String(text || "").split(/\r?\n/);
  const ok = lines.filter((line) => line.includes("[OK]")).length;
  const warn = lines.filter((line) => line.includes("[WARN]")).length;
  const fail = lines.filter((line) => line.includes("[FAIL]") || line.includes("FAILED")).length;
  const ng = lines.filter((line) => line.includes("[NG]")).length;

  const reportLines = lines.filter((line) => line.includes("=>"));
  const passedReports = reportLines.filter((line) => line.toLowerCase().includes("=> pass")).length;
  const presentReports = reportLines.filter((line) => line.toLowerCase().includes("=> present")).length;
  const missingReports = reportLines.filter((line) => line.toLowerCase().includes("=> missing")).length;

  const healthLine = lines.find((line) => line.toLowerCase().includes("health score"));
  const pressureLine = lines.find((line) => line.toLowerCase().includes("evidence pressure"));
  const nextLine = lines.find((line) => line.toLowerCase().includes("next action"));

  const summary = [];
  summary.push("HUMAN SUMMARY");
  summary.push("=============");

  if (fail > 0) {
    summary.push("Overall: ATTENTION NEEDED");
  } else if (warn > 0) {
    summary.push("Overall: PASS WITH WARNINGS");
  } else if (ok > 0 || passedReports > 0) {
    summary.push("Overall: PASS");
  } else {
    summary.push("Overall: OUTPUT RECEIVED");
  }

  summary.push("");
  summary.push("Signal counts:");
  summary.push(`- OK lines: ${ok}`);
  summary.push(`- Warning lines: ${warn}`);
  summary.push(`- Failure lines: ${fail}`);
  summary.push(`- NEXUS process lines: ${ng}`);

  if (reportLines.length) {
    summary.push("");
    summary.push("Report status:");
    summary.push(`- Passing reports: ${passedReports}`);
    summary.push(`- Present state/docs: ${presentReports}`);
    summary.push(`- Missing reports: ${missingReports}`);
  }

  if (healthLine || pressureLine || nextLine) {
    summary.push("");
    summary.push("Health summary:");
    if (healthLine) summary.push(`- ${healthLine.replace(/^\[OK\]\s*/, "")}`);
    if (pressureLine) summary.push(`- ${pressureLine.replace(/^\[OK\]\s*/, "")}`);
    if (nextLine) summary.push(`- ${nextLine.replace(/^\[OK\]\s*/, "")}`);
  }

  const important = lines.filter((line) =>
    line.includes("[FAIL]") ||
    line.includes("[WARN]") ||
    line.toLowerCase().includes("next action") ||
    line.toLowerCase().includes("failed")
  ).slice(0, 12);

  if (important.length) {
    summary.push("");
    summary.push("Important lines:");
    important.forEach((line) => summary.push(`- ${line}`));
  }

  return summary.join("\n");
}

function translateEvidence(raw) {
  const text = String(raw || "").trim();
  if (!text) return "HUMAN SUMMARY\n=============\nNo output.";

  try {
    const parsed = JSON.parse(text);
    return summarizeJsonObject(parsed);
  } catch (error) {
    return summarizeLogText(text);
  }
}

function writeOutput(raw, options = {}) {
  const text = raw || "No output.";
  const human = translateEvidence(text);
  const showRaw = options.showRaw !== false;
  output.textContent = showRaw
    ? `${human}\n\nRAW EVIDENCE\n============\n${text}`
    : human;
  output.scrollTop = 0;
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
    pushConsole(result.code === 0 ? "NEXUS" : "WARN", result.code === 0 ? "Lane completed. Evidence translated." : "Lane returned non-zero status.");
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
      next_action: "Route this study request through TUI/PowerShell if it should become durable repo memory.",
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
    next_action: "Use an allowlisted lane or TUI/PowerShell if this note should become repo evidence.",
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