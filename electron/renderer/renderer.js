const laneRoot = document.getElementById("lanes");
const output = document.getElementById("output");
const statusEl = document.getElementById("status");
const consoleStream = document.getElementById("console-stream");
const activeLane = document.getElementById("active-lane");
const operatorForm = document.getElementById("operator-form");
const operatorCommand = document.getElementById("operator-command");
const roleSelect = document.getElementById("role-select");
const selectorSwitch = document.getElementById("selector-switch");
const roleModel = document.getElementById("role-model");
const roleCommand = document.getElementById("role-command");
const copyRoleCommand = document.getElementById("copy-role-command");
const nexAiCard = document.getElementById("nex-ai-card");
const sendButton = document.getElementById("nex-send-button");

let allowlistedCommands = [];
let nexBusy = false;
const SELECTOR_UI_ONLY_BOUNDARY = "Selector changes UI planning context only. It does not call models, execute shell, mutate repo files, or grant authority.";

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
  "nn-health": "NN",
  fast: "FS",
  balanced: "BL",
  deep: "DP",
  "align-score": "AS"
};

const roleSettings = {
  FAST: {
    label: "FAST -> Phi-3",
    command: ".\\scripts\\nexus.ps1 fast -Tag \"Quick bounded recommendation.\" -CallModel",
    note: "FAST selected. Phi-3 quick recommendation voice is active for local planning."
  },
  BALANCED: {
    label: "BALANCED -> Phi-3",
    command: ".\\scripts\\nexus.ps1 balanced -Tag \"Balanced bounded recommendation.\" -CallModel",
    note: "BALANCED selected. Phi-3 balanced recommendation voice is active for local planning."
  },
  DEEP: {
    label: "DEEP -> Mistral",
    command: ".\\scripts\\nexus.ps1 deep -Tag \"Use Mistral for DEEP recommendation.\" -CallModel",
    note: "DEEP selected. Mistral is the deeper recommendation voice; output remains non-authoritative."
  },
  HANDOFF: {
    label: "HANDOFF -> ChatGPT/Codex",
    command: ".\\scripts\\nexus.ps1 nn-health",
    note: "HANDOFF selected. ChatGPT/Codex packet mode requires no local model authority."
  }
};

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value ?? "unknown";
}

function safeText(value) {
  return String(value || "").replace(/[<>&]/g, (ch) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[ch]));
}

function titleCase(value) {
  return String(value || "").replace(/[._-]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
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
  lines.push("NEX SUMMARY");
  lines.push("===========");
  if (data.system || data.version || data.status) {
    lines.push(`System: ${data.system || "NEXUS GATE"}`);
    if (data.version) lines.push(`Version: ${data.version}`);
    if (data.status) lines.push(`Status: ${statusWord(data.status)}`);
  }
  if (data.target_role) lines.push(`Target role: ${data.target_role}`);
  if (data.health) {
    lines.push("");
    lines.push("Health:");
    lines.push(`- Score: ${normalizeHealth(data.health.health_score)}`);
    lines.push(`- Evidence pressure: ${data.health.evidence_pressure || "unknown"}`);
    lines.push(`- Dominant pressure: ${data.health.dominant_pressure || data.health.dominant_pressure_source || "none"}`);
    if (data.health.next_action) lines.push(`- Next action: ${data.health.next_action}`);
  }
  if (data.role_assignments) {
    lines.push("");
    lines.push("Local roles:");
    Object.entries(data.role_assignments).forEach(([role, item]) => {
      lines.push(`- ${role}: ${item.model || "none"} / available=${item.available}`);
    });
  }
  if (Array.isArray(data.model_responses) && data.model_responses.length) {
    lines.push("");
    lines.push("Model response:");
    data.model_responses.forEach((item) => {
      lines.push(`- ${item.role} / ${item.model} / ok=${item.ok}`);
      if (item.response) lines.push(String(item.response).trim());
      if (item.error) lines.push(`ERROR: ${item.error}`);
    });
  }
  if (Array.isArray(data.drift_flags) && data.drift_flags.length) {
    lines.push("");
    lines.push("Drift flags:");
    data.drift_flags.forEach((item) => lines.push(`- ${item}`));
  }
  if (data.next_action || data.next_recommendation) {
    lines.push("");
    lines.push(`Next: ${data.next_action || data.next_recommendation}`);
  }
  if (data.boundary || data.claim_boundary || data.authority_boundary) {
    lines.push("");
    lines.push("Boundary:");
    lines.push(typeof data.authority_boundary === "object" ? JSON.stringify(data.authority_boundary, null, 2) : (data.boundary || data.claim_boundary));
  }
  return lines.join("\n");
}

function summarizeLogText(text) {
  const lines = String(text || "").split(/\r?\n/);
  const ok = lines.filter((line) => line.includes("[OK]")).length;
  const warn = lines.filter((line) => line.includes("[WARN]")).length;
  const fail = lines.filter((line) => line.includes("[FAIL]") || line.includes("FAILED")).length;
  const summary = [];
  summary.push("NEX SUMMARY");
  summary.push("===========");
  summary.push(fail > 0 ? "Overall: ATTENTION NEEDED" : warn > 0 ? "Overall: PASS WITH WARNINGS" : ok > 0 ? "Overall: PASS" : "Overall: OUTPUT RECEIVED");
  summary.push("");
  summary.push(`OK lines: ${ok}`);
  summary.push(`Warning lines: ${warn}`);
  summary.push(`Failure lines: ${fail}`);
  const important = lines.filter((line) => line.includes("[FAIL]") || line.includes("[WARN]") || line.toLowerCase().includes("next action")).slice(0, 12);
  if (important.length) {
    summary.push("");
    important.forEach((line) => summary.push(`- ${line}`));
  }
  return summary.join("\n");
}

function translateEvidence(raw) {
  const text = String(raw || "").trim();
  if (!text) return "NEX SUMMARY\n===========\nNo output.";
  try {
    return summarizeJsonObject(JSON.parse(text));
  } catch (error) {
    return summarizeLogText(text);
  }
}

function writeOutput(raw, options = {}) {
  const text = raw || "No output.";
  const human = options.preTranslated ? text : translateEvidence(text);
  output.textContent = human;
  output.scrollTop = 0;
}

function appendChat(kind, text, meta = "") {
  const row = document.createElement("article");
  row.className = `chat-message ${kind === "human" ? "human-message" : "ai-message"}`;

  const avatar = document.createElement("div");
  avatar.className = kind === "human" ? "human-avatar" : "nex-avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.innerHTML = `<span>${kind === "human" ? "YOU" : "NEX"}</span>`;

  const body = document.createElement("div");
  body.className = "message-body";

  const header = document.createElement("header");
  header.innerHTML = `<strong>${kind === "human" ? "Human" : "NEX"}</strong><small>${safeText(meta)}</small>`;

  const pre = document.createElement("pre");
  pre.textContent = text;

  body.appendChild(header);
  body.appendChild(pre);
  row.appendChild(avatar);
  row.appendChild(body);

  consoleStream.appendChild(row);
  while (consoleStream.children.length > 24) {
    consoleStream.removeChild(consoleStream.firstElementChild);
  }
  consoleStream.scrollTop = consoleStream.scrollHeight;
}

function pushConsole(level, text) {
  appendChat("ai", `[${level}] ${text}`, "system event");
}

function setClock() {
  document.getElementById("system-time").textContent = new Date().toISOString().slice(0, 19).replace("T", " ");
}

function setBuffer(value, state = "") {
  const numeric = Math.max(0, Math.min(100, Number(value) || 0));
  const fill = document.getElementById("buffer-fill");
  const label = document.getElementById("buffer-value");
  const track = document.querySelector(".electric-chain");
  if (fill) fill.style.width = `${numeric}%`;
  if (label) label.textContent = `${numeric}%`;
  if (track) {
    track.classList.toggle("is-collecting", numeric > 0 && numeric < 100);
    track.classList.toggle("is-complete", numeric >= 100);
    if (state) track.dataset.state = state;
  }
}

function setProcessing(active) {
  nexBusy = active;
  document.body.classList.toggle("nex-processing", active);
  nexAiCard?.classList.toggle("is-processing", active);
  if (sendButton) sendButton.disabled = active;
}

function currentRole() {
  return roleSettings[roleSelect?.value] ? roleSelect.value : "DEEP";
}

function setSelectorRole(role, source = "change") {
  const normalized = roleSettings[role] ? role : "DEEP";
  const setting = roleSettings[normalized];

  if (selectorSwitch) {
    selectorSwitch.dataset.role = normalized;
    selectorSwitch.classList.remove("is-awake");
    void selectorSwitch.offsetWidth;
    selectorSwitch.classList.add("is-awake");
    window.setTimeout(() => selectorSwitch.classList.remove("is-awake"), 850);
  }
  if (roleModel) roleModel.textContent = setting.label;
  if (roleCommand) roleCommand.textContent = setting.command;

  pushConsole("NEXUS", `${setting.note} Selector source=${source}.`);
}

function initRoleSelector() {
  if (!roleSelect || !selectorSwitch) return;
  roleSelect.addEventListener("change", () => setSelectorRole(roleSelect.value, "select"));
  selectorSwitch.addEventListener("click", () => setSelectorRole(roleSelect.value, "glyph"));
  copyRoleCommand?.addEventListener("click", async () => {
    const command = roleCommand?.textContent || "";
    if (!command) return;
    try {
      await navigator.clipboard.writeText(command);
      pushConsole("NEXUS", "Selector command copied to clipboard.");
    } catch (error) {
      pushConsole("WARN", "Clipboard unavailable; command remains visible in selector.");
    }
  });
  setSelectorRole(roleSelect.value || "DEEP", "init");
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
  setProcessing(true);
  setBuffer(24, "lane");
  pushConsole("NEXUS", `Lane '${lane}' engaged. Initializing governed run...`);

  try {
    setBuffer(52, "lane");
    const result = await window.nexus.runLane(lane);
    setBuffer(result.code === 0 ? 100 : 0, "lane");
    writeOutput(result.stdout || result.stderr || "No lane output.");
    statusEl.textContent = result.code === 0 ? "stable" : "blocked";
    appendChat("ai", translateEvidence(result.stdout || result.stderr || "No lane output."), `lane=${lane}`);
  } catch (error) {
    setBuffer(0, "lane");
    statusEl.textContent = "blocked";
    writeOutput(error.stack || error.message, { preTranslated: true });
    pushConsole("WARN", "Lane execution failed inside governed bridge.");
  } finally {
    setProcessing(false);
  }
}

async function sendNexMessage(prompt) {
  if (nexBusy) return;
  const role = currentRole();
  appendChat("human", prompt, `role=${role}`);
  activeLane.textContent = `nex:${role.toLowerCase()}`;
  statusEl.textContent = "thinking";
  setProcessing(true);
  setBuffer(18, "collecting");
  writeOutput("NEX is collecting chain evidence...", { preTranslated: true });

  try {
    setBuffer(42, "routing");
    if (!window.nexus.askNex) {
      throw new Error("NEX chat bridge is not exposed by preload.");
    }

    const result = await window.nexus.askNex({
      prompt,
      role,
      callModel: role !== "HANDOFF"
    });

    setBuffer(78, "reasoning");

    const report = result.report || {};
    const modelResponses = Array.isArray(report.model_responses) ? report.model_responses : [];
    const responseText = modelResponses.map((item) => item.response || item.error || "").filter(Boolean).join("\n\n").trim();

    let visible = responseText;
    if (!visible) {
      visible = translateEvidence(JSON.stringify(report || {
        status: result.code === 0 ? "pass" : "review",
        stderr: result.stderr,
        stdout: result.stdout
      }, null, 2));
    }

    if (result.code !== 0) {
      visible = `NEX bridge returned non-zero status.\n\n${result.stderr || result.stdout || visible}`;
    }

    appendChat("ai", visible, `NEX / ${role} / recommendation-only`);
    writeOutput(visible, { preTranslated: true });
    statusEl.textContent = result.code === 0 ? "stable" : "blocked";
    setBuffer(result.code === 0 ? 100 : 0, "complete");
  } catch (error) {
    const message = `NEX chat bridge failed: ${error.message}\n\nCheck that Python is available, Ollama is running for local model calls, and the selected role is allowlisted.`;
    appendChat("ai", message, `NEX / ${role} / blocked`);
    writeOutput(message, { preTranslated: true });
    statusEl.textContent = "blocked";
    setBuffer(0, "error");
  } finally {
    setProcessing(false);
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
  setBuffer(10, "hydrate");

  const contract = await window.nexus.getContract();
  allowlistedCommands = contract.allowlistedCommands || [];
  renderLanes(allowlistedCommands);
  initRoleSelector();
  setBuffer(25, "hydrate");

  let state;
  try {
    const surface = "reports/tui/nexus_tui_surface_latest.json";
    if (!await window.nexus.surfaceExists(surface)) throw new Error("optional TUI surface is not present");
    const raw = await window.nexus.readSurface(surface);
    state = JSON.parse(raw);
    setBuffer(70, "hydrate");
  } catch (error) {
    pushConsole("WARN", "TUI surface missing. Hydrating from AI feedback context.");
    const raw = await window.nexus.readSurface("state/ai_feedback_context_latest.json");
    const context = JSON.parse(raw);
    state = buildFallbackState(context);
    setBuffer(55, "hydrate");
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

  const greeting = "NEX online. Chat is now routed through the bounded NEX bridge. Select FAST, BALANCED, DEEP, or HANDOFF, then press Enter to send.";
  writeOutput(greeting, { preTranslated: true });
  appendChat("ai", greeting, "ready / recommendation-only");
  statusEl.textContent = "stable";
  document.body.dataset.ready = "true";
  setBuffer(100, "complete");
}

document.getElementById("refresh")?.addEventListener("click", () => {
  pushConsole("AI", "Latest handoff surfaces are already loaded.");
  setBuffer(100, "complete");
});

operatorCommand?.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    operatorForm?.requestSubmit();
  }
  if (event.key === "Enter" && event.shiftKey) {
    // Shift+Enter newline.
  }
});

operatorForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const raw = operatorCommand.value.trim();
  if (!raw) return;

  operatorCommand.value = "";

  if (raw.startsWith("/study ")) {
    const summary = raw.slice("/study ".length).trim();
    const packet = {
      type: "study_packet_draft",
      status: "pending_operator_packet_backend",
      summary,
      next_action: "Route this study request through TUI/PowerShell if it should become durable repo memory.",
      boundary: "Electron input is operator intent only. It does not self-authorize, mutate the repo, or run arbitrary shell."
    };
    appendChat("human", raw, "study draft");
    appendChat("ai", translateEvidence(JSON.stringify(packet, null, 2)), "draft only");
    writeOutput(JSON.stringify(packet, null, 2));
    setBuffer(100, "complete");
    return;
  }

  const lane = raw.startsWith("/") ? raw.slice(1).trim() : "";
  if (lane) {
    appendChat("human", raw, "slash command");
    await runGovernedLane(lane);
    return;
  }

  await sendNexMessage(raw);
});

loadSurfaceState().catch((error) => {
  document.body.dataset.ready = "false";
  statusEl.textContent = "blocked";
  setProcessing(false);
  setBuffer(0, "error");
  writeOutput(error.stack || error.message, { preTranslated: true });
});

