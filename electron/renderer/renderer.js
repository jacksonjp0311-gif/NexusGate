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
const stopButton = document.getElementById("nex-stop-button");
const telemetryHud = document.getElementById("telemetry-hud");
const systemErrorHud = document.getElementById("system-error-hud");
const systemErrorClose = document.getElementById("system-error-close");

let allowlistedCommands = [];
let nexBusy = false;
let nexStopRequested = false;
let telemetryLoopHandle = null;
const SELECTOR_UI_ONLY_BOUNDARY = "Selector changes UI planning context only. It does not call models, execute shell, mutate repo files, or grant authority.";
const NEX_MODEL_RESPONSE_STAGE_MARKER = 'stage: "nex_model_response"';
const NEX_MODEL_BRIDGE_STAGE_MARKER = 'stage: "nex_model_bridge"';
const NEX_TIMEOUT_ERROR_HUD_BOUNDARY = "Model response ok=false is system evidence and opens the red HUD, not normal AI output.";
const NEX_CHAT_APPEND_ONLY_BOUNDARY = "append-only chat: NEX responses appear once in the conversation stream and are not mirrored into the pinned output card.";

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
  row.classList.toggle("system-error-message", String(meta || "").toLowerCase().includes("system-error"));

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

function resetChatToNexGreeting(greeting) {
  if (consoleStream && nexAiCard) {
    consoleStream.innerHTML = "";
    consoleStream.appendChild(nexAiCard);
  }

  writeOutput(greeting, { preTranslated: true });

  const meta = nexAiCard?.querySelector("header small");
  if (meta) meta.textContent = "ready / recommendation-only";

  const label = nexAiCard?.querySelector("header strong");
  if (label) label.textContent = "NEX";
}

const NEX_LOCAL_MODEL_REFUSAL_CODE = "WinError 10061";

function reflectNexFailure(text, role) {
  const raw = String(text || "");
  const lower = raw.toLowerCase();

  if (lower.includes("winerror 10061") || raw.includes(NEX_LOCAL_MODEL_REFUSAL_CODE) || lower.includes("actively refused") || lower.includes("connection refused")) {
    return [
      "NEX REFLECTIVE FEEDBACK",
      "=======================",
      `Status: local model bridge blocked for ${role}. Trigger: ${NEX_LOCAL_MODEL_REFUSAL_CODE} / connection refused.`,
      "",
      "What this means:",
      "- The NEX chat bridge reached the local reasoning route.",
      "- The selected local model server refused the connection.",
      "- This usually means Ollama is not running on the local API port.",
      "",
      "Next bounded test:",
      "1. Start Ollama or open the Ollama desktop service.",
      "2. Run: ollama list",
      "3. Run: ollama run mistral \"reply with NEX ready\"",
      "4. Return to Electron and send the message again.",
      "",
      "Boundary:",
      "NEX did not execute model output, mutate files, or grant authority."
    ].join("\n");
  }

  return raw;
}
function pushConsole(level, text) {
  appendChat("ai", `[${level}] ${text}`, "system event");
}

async function ensureLocalOllamaBackend() {
  if (!window.nexus.ensureOllama) return;
  try {
    const result = await window.nexus.ensureOllama();
    const label = result.ok ? `ollama ${result.status}` : `ollama ${result.status || "blocked"}`;
    setTelemetryText("hud-ollama", label);
    setTelemetryText("telemetry-status", result.ok ? "backend online" : "backend blocked");
    return result;
  } catch (error) {
    setTelemetryText("telemetry-status", "backend blocked");
    return { ok: false, error: error.message };
  }
}
function classifySystemError(rawText) {
  const raw = String(rawText || "");
  const lower = raw.toLowerCase();

  if (lower.includes("timed out") || lower.includes("timeout")) {
    return {
      cause: "local model response timeout",
      recommendations: [
        "Use FAST / Phi-3 for the next bounded test.",
        "Keep DEEP / Mistral for shorter prompts until runtime pressure is visible.",
        "Open System Monitor and inspect CPU/RAM/Ollama pressure.",
        "Use Stop Transmission if the local model stalls again."
      ]
    };
  }

  if (lower.includes("winerror 10061") || lower.includes("connection refused") || lower.includes("actively refused")) {
    return {
      cause: "local Ollama endpoint unavailable",
      recommendations: [
        "Let the entry portal start the hidden Ollama backend.",
        "Confirm System Monitor shows Ollama online.",
        "Retry FAST / Phi-3 before DEEP / Mistral.",
        "If blocked, restart the desktop portal rather than opening a second Ollama shell."
      ]
    };
  }

  if (lower.includes("cuda") || lower.includes("0xc0000409") || lower.includes("llama-server process no longer running")) {
    return {
      cause: "GPU/CUDA runner failure",
      recommendations: [
        "Keep NEX CPU fallback enabled.",
        "Use FAST / Phi-3 first.",
        "Do not switch back to GPU until driver/runtime compatibility is fixed.",
        "Preserve num_gpu=0 for NEX local calls."
      ]
    };
  }

  if (lower.includes("_env_int") || lower.includes("nameerror") || lower.includes("traceback")) {
    return {
      cause: "local router/runtime code error",
      recommendations: [
        "Run the focused unit test for the failing module.",
        "Run the full test suite before committing.",
        "Do not treat this as model output; this is system evidence.",
        "Patch the local bridge and verify by readback."
      ]
    };
  }

  return {
    cause: "local bridge returned a non-zero status",
    recommendations: [
      "Inspect the system-compiled report below.",
      "Run the focused test tied to the failing surface.",
      "Retry FAST / Phi-3 after the blocker is removed.",
      "Keep model output recommendation-only."
    ]
  };
}

function buildSystemErrorReport({ stage, role, code, stderr, stdout, report }) {
  const raw = [stderr, stdout].filter(Boolean).join("\n").trim();
  const classified = classifySystemError(raw);
  const reportStatus = report?.status || report?.kind || "runtime";
  const lines = [
    "NEX SYSTEM ERROR REPORT",
    "=======================",
    "Compiled by: NEXUS renderer/system bridge",
    `Stage: ${stage || "unknown"}`,
    `Role: ${role || "unknown"}`,
    `Exit code: ${code ?? "unknown"}`,
    `Report status: ${reportStatus}`,
    "",
    "How it happened:",
    classified.cause,
    "",
    "System recommendations:",
    ...classified.recommendations.map((item, index) => `${index + 1}. ${item}`),
    "",
    "Raw system evidence:",
    raw ? raw.slice(0, 5000) : "No stderr/stdout was returned."
  ];

  return {
    title: "NEX bridge blocked",
    stage: stage || "unknown",
    code: String(code ?? "unknown"),
    cause: classified.cause,
    chatText: lines.join("\n")
  };
}

function showSystemErrorHud(payload) {
  if (!systemErrorHud) return;
  document.body.classList.add("system-error-active");
  systemErrorHud.hidden = false;
  systemErrorHud.classList.add("is-visible");
  setTelemetryText("system-error-title", payload.title || "NEX bridge blocked");
  setTelemetryText("system-error-stage", payload.stage || "unknown");
  setTelemetryText("system-error-cause", payload.cause || "unknown");
  setTelemetryText("system-error-code", payload.code || "unknown");
  setTelemetryText("system-error-report", payload.chatText || "No system report.");
}

function clearSystemErrorHud() {
  document.body.classList.remove("system-error-active");
  if (systemErrorHud) {
    systemErrorHud.hidden = true;
    systemErrorHud.classList.remove("is-visible");
  }
}

function startTelemetryLoop() {
  if (telemetryLoopHandle) return;
  refreshTelemetry();
  telemetryLoopHandle = setInterval(refreshTelemetry, 1000);
}
function formatBytes(value) {
  const numeric = Number(value || 0);
  if (!numeric) return "--";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = numeric;
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size = size / 1024;
    index += 1;
  }
  return `${size.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function setTelemetryText(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
}

async function refreshTelemetry() {
  if (!window.nexus.getTelemetry) return;
  try {
    const telemetry = await window.nexus.getTelemetry();
    const cpu = telemetry.cpu?.load_percent ?? 0;
    const ram = telemetry.memory?.used_percent ?? 0;
    const gpuRaw = telemetry.windows?.gpu_load_percent;
    const gpu = gpuRaw === null || gpuRaw === undefined ? "--" : `${Math.min(100, Number(gpuRaw)).toFixed(1)}%`;
    const gpuName = telemetry.windows?.gpu_name || "unknown";
    const diskFree = formatBytes(telemetry.windows?.disk_c_free);
    const ollamaCount = Array.isArray(telemetry.windows?.ollama_processes)
      ? telemetry.windows.ollama_processes.length
      : telemetry.windows?.ollama_processes ? 1 : 0;

    setTelemetryText("tm-cpu", `${Number(cpu).toFixed(1)}%`);
    setTelemetryText("tm-ram", `${Number(ram).toFixed(1)}%`);
    setTelemetryText("tm-gpu", gpu);
    setTelemetryText("hud-cpu", `${Number(cpu).toFixed(1)}%`);
    setTelemetryText("hud-ram", `${Number(ram).toFixed(1)}%`);
    setTelemetryText("hud-gpu", gpu);
    setTelemetryText("hud-gpu-name", gpuName);
    setTelemetryText("hud-disk", diskFree);
    setTelemetryText("hud-ollama", ollamaCount > 0 ? `online / ${ollamaCount}` : "not detected");
    setTelemetryText("telemetry-status", "live");
    setTelemetryText("hud-telemetry-raw", JSON.stringify(telemetry, null, 2));
  } catch (error) {
    setTelemetryText("telemetry-status", "blocked");
    setTelemetryText("hud-telemetry-raw", `Telemetry unavailable: ${error.message}`);
  }
}

function toggleTelemetryHud(force) {
  if (!telemetryHud) return;
  const next = typeof force === "boolean" ? force : !telemetryHud.classList.contains("is-expanded");
  telemetryHud.classList.toggle("is-expanded", next);
  telemetryHud.toggleAttribute("hidden", !next);
  if (next) refreshTelemetry();
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
  if (stopButton) stopButton.disabled = !active;
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
  clearSystemErrorHud();
  nexStopRequested = false;

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
    const modelError = modelResponses.find((item) => item && item.ok === false);

    let visible = responseText;
    if (!visible) {
      visible = translateEvidence(JSON.stringify(report || {
        status: result.code === 0 ? "pass" : "review",
        stderr: result.stderr,
        stdout: result.stdout
      }, null, 2));
    }

    if (result.code !== 0 || modelError) {
      const modelEvidence = modelError ? JSON.stringify(modelError, null, 2) : "";
      const systemReport = buildSystemErrorReport({
        stage: modelError ? "nex_model_response" : "nex_model_bridge",
        role,
        code: result.code,
        stderr: [result.stderr, modelEvidence].filter(Boolean).join("\n"),
        stdout: result.stdout,
        report
      });
      showSystemErrorHud(systemReport);
      visible = systemReport.chatText;
    }

    visible = reflectNexFailure(visible, role);

    appendChat("ai", visible, (!modelError && result.code === 0) ? `NEX / ${role} / recommendation-only` : `NEX / ${role} / system-error`);
    statusEl.textContent = (!modelError && result.code === 0) ? "stable" : "blocked";
    setBuffer((!modelError && result.code === 0) ? 100 : 0, (!modelError && result.code === 0) ? "complete" : "error");
  } catch (error) {
    const systemReport = buildSystemErrorReport({
      stage: "nex_chat_exception",
      role,
      code: -1,
      stderr: error.stack || error.message,
      stdout: "",
      report: {}
    });
    showSystemErrorHud(systemReport);
    appendChat("ai", systemReport.chatText, `NEX / ${role} / system-error`);
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
  ensureLocalOllamaBackend();
  startTelemetryLoop();
  setBuffer(10, "hydrate");
  toggleTelemetryHud(false);
  clearSystemErrorHud();

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
    // Startup fallback is reflected in telemetry panels, not as an opening chat message.
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

  const greeting = "Hello. I am NEX - your bounded reflective intelligence surface. Select a local voice, ask one thing, and I will return recommendation-only feedback with any blocker made clear.";
  resetChatToNexGreeting(greeting);
  statusEl.textContent = "stable";
  document.body.dataset.ready = "true";
  setBuffer(100, "complete");
}

document.getElementById("refresh")?.addEventListener("click", () => {
  pushConsole("AI", "Latest handoff surfaces are already loaded.");
  setBuffer(100, "complete");
});

document.getElementById("telemetry-popout")?.addEventListener("click", () => toggleTelemetryHud());
document.getElementById("telemetry-close")?.addEventListener("click", () => toggleTelemetryHud(false));
systemErrorClose?.addEventListener("click", () => clearSystemErrorHud());

stopButton?.addEventListener("click", async () => {
  nexStopRequested = true;
  setBuffer(0, "stopped");
  statusEl.textContent = "stopping";
  try {
    const result = await window.nexus.stopNex();
    appendChat("ai", `Transmission stop requested.\n\n${JSON.stringify(result, null, 2)}`, "NEX / stopped / recommendation-only");
  } catch (error) {
    appendChat("ai", `Stop transmission failed: ${error.message}`, "NEX / stop blocked");
  } finally {
    setProcessing(false);
    statusEl.textContent = "stable";
  }
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











