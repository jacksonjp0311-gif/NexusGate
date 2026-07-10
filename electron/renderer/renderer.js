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
const modelSelectorHud = document.getElementById("model-selector-hud");
const modelSelectorToggle = document.getElementById("model-selector-toggle");
const modelSelectorClose = document.getElementById("model-selector-close");
const selectorHudOpen = document.getElementById("selector-hud-open"); // optional: left glyph was removed in v0.8.1 // optional: left glyph was removed in v0.8.1
const selectorHudStatus = document.getElementById("selector-hud-status");
const nexAiCard = document.getElementById("nex-ai-card");
const sendButton = document.getElementById("nex-send-button");
const stopButton = document.getElementById("nex-stop-button");
const telemetryHud = document.getElementById("telemetry-hud");
const metaOrchestratorHud = document.getElementById("meta-orchestrator-hud");
const systemErrorHud = document.getElementById("system-error-hud");
const systemErrorClose = document.getElementById("system-error-close");
const petriOpen = document.getElementById("petri-open");
const petriMiniBody = document.getElementById("petri-mini-body");
const petriMiniCanvas = document.getElementById("petri-mini-canvas");

let allowlistedCommands = [];
let nexBusy = false;
let ollamaReady = null; // null=unknown, true=ready, false=offline
let nexStopRequested = false;
let telemetryLoopHandle = null;
let petriLoopHandle = null;
let petriAnimationStarted = false;
let petriPreviewStartMs = Date.now();
let latestPetriState = null;
let modelSelectorHudBound = false;
const SELECTOR_UI_ONLY_BOUNDARY = "Selector changes UI planning context only. It does not call models, execute shell, mutate repo files, or grant authority.";
const NEX_MODEL_RESPONSE_STAGE_MARKER = 'stage: "nex_model_response"';
const NEX_MODEL_BRIDGE_STAGE_MARKER = 'stage: "nex_model_bridge"';
const NEX_TIMEOUT_ERROR_HUD_BOUNDARY = "Model response ok=false is system evidence and opens the red HUD, not normal AI output.";
const NEX_CHAT_APPEND_ONLY_BOUNDARY = "append-only chat: NEX responses appear once in the conversation stream and are not mirrored into the pinned output card.";
const NEX_SHELL_RELAY_MODE_BOUNDARY = "Shell relay mode runs only allowlisted NEXUS lanes through the hidden PowerShell bridge; no arbitrary shell.";
const NEX_ARBITRARY_POWERSHELL_BLOCK_MARKER = "arbitrary PowerShell is blocked";
const NEX_HANDOFF_ACTION_SHELL_BOUNDARY = "HANDOFF selection can run human-authorized ChatGPT/Codex action scripts through the hidden PowerShell bridge; never from autonomous model output.";
const META_ORCHESTRATOR_SURFACE = "reports/nexus_meta_orchestrator_gate_latest.json";

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
    label: "FAST -> Phi-4-mini",
    command: ".\\scripts\\nexus.ps1 fast -Tag \"Quick bounded recommendation.\" -CallModel",
    note: "FAST selected. Phi-4-mini hot recommendation voice is active for local planning."
  },
  BALANCED: {
    label: "BALANCED -> Phi-4-mini",
    command: ".\\scripts\\nexus.ps1 balanced -Tag \"Balanced bounded recommendation.\" -CallModel",
    note: "BALANCED selected. Phi-4-mini balanced recommendation voice is active for local planning."
  },
  DEEP: {
    label: "DEEP -> Mistral",
    command: ".\\scripts\\nexus.ps1 deep -Tag \"Use Mistral for DEEP recommendation.\" -CallModel",
    note: "DEEP selected. Mistral is the deeper recommendation voice; output remains non-authoritative."
  },
  TNN: {
    label: "TNN -> Tesseract Neural Network",
    command: ".\\scripts\\nexus.ps1 tnn -Tag \"Read Tesseract Neural Network state.\" -CallModel",
    note: "Tesseract Neural Network selected. Minimal governed NN surface is active."
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
  document.dispatchEvent(new CustomEvent("nexus:message-rendered", { detail: { kind, meta } }));
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
    ollamaReady = Boolean(result.ok);
    return result;
  } catch (error) {
    setTelemetryText("telemetry-status", "backend blocked");
    ollamaReady = false;
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
        "Use FAST / Phi-4-mini for the next bounded test.",
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
        "Retry FAST / Phi-4-mini before DEEP / Mistral.",
        "If blocked, restart the desktop portal rather than opening a second Ollama shell."
      ]
    };
  }

  if (lower.includes("cuda") || lower.includes("0xc0000409") || lower.includes("llama-server process no longer running")) {
    return {
      cause: "GPU/CUDA runner failure",
      recommendations: [
        "Keep NEX CPU fallback enabled.",
        "Use FAST / Phi-4-mini first.",
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
      "Retry FAST / Phi-4-mini after the blocker is removed.",
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

function setTelemetryHtml(id, html) {
  const node = document.getElementById(id);
  if (node) node.innerHTML = html;
}

function normalizeArray(value) {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function renderTelemetryRows(rows, empty = "No telemetry entries.") {
  const normalized = normalizeArray(rows).filter(Boolean);
  if (!normalized.length) return `<div class="telemetry-row muted">${safeText(empty)}</div>`;
  return normalized.map((row) => {
    const name = row.ProcessName || row.Name || row.DeviceID || row.InterfaceDescription || "unknown";
    const primary = row.WorkingSet64 !== undefined ? formatBytes(row.WorkingSet64)
      : row.FreeSpace !== undefined ? `${formatBytes(row.FreeSpace)} free`
      : row.LinkSpeed || row.Status || "";
    const secondary = row.CPU !== undefined ? `cpu ${Number(row.CPU || 0).toFixed(1)}`
      : row.Size !== undefined ? `${formatBytes(row.Size)} total`
      : row.SentBytes !== undefined ? `sent ${formatBytes(row.SentBytes)} / recv ${formatBytes(row.ReceivedBytes)}`
      : row.MacAddress || "";
    return `<div class="telemetry-row"><strong>${safeText(name)}</strong><span>${safeText(primary)}</span><em>${safeText(secondary)}</em></div>`;
  }).join("");
}

function renderProcessManagerRows(rows) {
  const normalized = normalizeArray(rows).filter(Boolean);
  if (!normalized.length) return `<div class="telemetry-row muted">No process telemetry.</div>`;
  return [
    `<div class="process-manager-head"><span>PID</span><span>Process</span><span>CPU</span><span>Memory</span><span>Action</span></div>`,
    ...normalized.map((row) => {
      const allowed = row.terminate_allowed === true;
      const button = allowed
        ? `<button class="terminate-process-button" type="button" data-terminate-pid="${safeText(row.pid)}" data-terminate-name="${safeText(row.name)}">End</button>`
        : `<span class="protected-process-badge">Guarded</span>`;
      return [
        `<div class="process-manager-row">`,
        `<span>${safeText(row.pid)}</span>`,
        `<strong>${safeText(row.name || "unknown")}</strong>`,
        `<span>${Number(row.cpu_percent || 0).toFixed(1)}%</span>`,
        `<span>${formatBytes(row.memory_bytes)} / ${Number(row.memory_percent || 0).toFixed(1)}%</span>`,
        button,
        `</div>`
      ].join("");
    })
  ].join("");
}

function renderTelemetryTextList(items, empty = "No recommendations.") {
  const normalized = normalizeArray(items).filter(Boolean);
  if (!normalized.length) return `<div class="telemetry-row muted">${safeText(empty)}</div>`;
  return normalized.map((item, index) => (
    `<div class="telemetry-row"><strong>${String(index + 1).padStart(2, "0")}</strong><span>${safeText(item)}</span></div>`
  )).join("");
}

async function openPetriDishPro() {
  setTelemetryText("petri-status", "opening");
  try {
    if (!window.nexus.openPetriDishPro) {
      throw new Error("PetriDishPro bridge is not exposed.");
    }
    const result = await window.nexus.openPetriDishPro();
    setTelemetryText("petri-status", result.ok ? result.status || "open" : result.status || "blocked");
    if (!result.ok) {
      appendChat("ai", `PetriDishPro launch blocked: ${result.path || "unknown path"}`, "NEX / PetriDishPro");
    }
  } catch (error) {
    setTelemetryText("petri-status", "blocked");
    appendChat("ai", `PetriDishPro launch failed: ${error.message}`, "NEX / PetriDishPro");
  }
}

function wrapPetriCoordinate(value, limit) {
  const span = limit * 2;
  let wrapped = ((value + limit) % span + span) % span - limit;
  if (!Number.isFinite(wrapped)) wrapped = 0;
  return wrapped;
}

function drawPetriMiniLensBackground(ctx, cx, cy, radius, t) {
  ctx.save();
  ctx.globalAlpha = 0.56;
  ctx.strokeStyle = "rgba(39, 244, 255, 0.055)";
  ctx.lineWidth = 1;
  for (let i = 0; i < 26; i += 1) {
    const y = cy - radius + (i * radius * 2 / 26);
    ctx.beginPath();
    ctx.moveTo(cx - radius, y + Math.sin(i + t * 0.18) * 8);
    ctx.bezierCurveTo(cx - radius * 0.26, y - 12, cx + radius * 0.26, y + 14, cx + radius, y + Math.cos(i) * 8);
    ctx.stroke();
  }
  const vignette = ctx.createRadialGradient(cx, cy, radius * 0.25, cx, cy, radius);
  vignette.addColorStop(0.1, "rgba(255,255,255,0.035)");
  vignette.addColorStop(0.78, "rgba(0,0,0,0.03)");
  vignette.addColorStop(1, "rgba(0,0,0,0.74)");
  ctx.fillStyle = vignette;
  ctx.fillRect(cx - radius, cy - radius, radius * 2, radius * 2);
  ctx.restore();
}

function drawPetriMiniRod(ctx, size, color, phase, t) {
  const length = size * 3.4;
  const bend = Math.sin(t * 1.1 + phase) * size * 0.42;
  ctx.lineWidth = Math.max(1.6, size * 0.7);
  ctx.lineCap = "round";
  ctx.strokeStyle = color;
  ctx.globalAlpha = 0.72;
  ctx.beginPath();
  ctx.moveTo(-length * 0.5, bend * 0.22);
  ctx.quadraticCurveTo(0, bend, length * 0.5, -bend * 0.22);
  ctx.stroke();
  ctx.globalAlpha = 0.48;
  ctx.strokeStyle = "rgba(234, 255, 255, 0.78)";
  ctx.lineWidth = 0.85;
  ctx.stroke();
}

function drawPetriPreview() {
  if (!petriMiniCanvas) return;
  const rect = petriMiniCanvas.getBoundingClientRect();
  const width = Math.max(1, Math.floor(rect.width));
  const height = Math.max(1, Math.floor(rect.height));
  if (petriMiniCanvas.width !== width || petriMiniCanvas.height !== height) {
    petriMiniCanvas.width = width;
    petriMiniCanvas.height = height;
  }
  const ctx = petriMiniCanvas.getContext("2d");
  if (!ctx) return;
  const t = (Date.now() - petriPreviewStartMs) / 1000;
  ctx.clearRect(0, 0, width, height);
  const cx = width / 2;
  const cy = height * 0.52;
  const radius = Math.min(width, height) * 0.46;

  ctx.save();
  const bg = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius * 1.65);
  bg.addColorStop(0, "rgba(9, 32, 42, 0.94)");
  bg.addColorStop(0.58, "rgba(2, 14, 28, 0.96)");
  bg.addColorStop(1, "rgba(1, 7, 18, 1)");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, width, height);

  ctx.save();
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.clip();
  ctx.fillStyle = "rgba(2, 8, 20, 0.98)";
  ctx.fillRect(cx - radius, cy - radius, radius * 2, radius * 2);
  drawPetriMiniLensBackground(ctx, cx, cy, radius, t);

  const particles = latestPetriState?.particles || [];
  particles.forEach((particle, index) => {
    const wx = wrapPetriCoordinate(Number(particle.x || 0) + Number(particle.vx || 0) * t * 5.4, 1.35);
    const wy = wrapPetriCoordinate(Number(particle.y || 0) + Number(particle.vy || 0) * t * 5.4, 0.82);
    const x = cx + wx * radius * 0.7;
    const y = cy + wy * radius * 0.7;
    if ((x - cx) ** 2 + (y - cy) ** 2 > (radius * 0.96) ** 2) return;
    ctx.globalAlpha = 0.14 + Math.min(0.38, Number(particle.z || 0) * 0.26);
    ctx.fillStyle = "rgba(180, 230, 255, 0.48)";
    ctx.beginPath();
    ctx.arc(x, y, Math.max(0.6, Number(particle.z || 0) * 1.8), 0, Math.PI * 2);
    ctx.fill();
  });

  const cells = latestPetriState?.cells || [];
  cells.forEach((cell, index) => {
    const behavior = cell.behavior || {};
    const phase = Number(cell.phase || index * 0.37);
    const motility = Number(behavior.motility ?? 0.65);
    const wx = wrapPetriCoordinate(Number(cell.x || 0) + Number(cell.vx || 0) * t * 4.8 * motility + Math.sin(t * 0.22 + phase) * 0.012, 1.25);
    const wy = wrapPetriCoordinate(Number(cell.y || 0) + Number(cell.vy || 0) * t * 4.8 * motility + Math.cos(t * 0.2 + phase) * 0.008, 0.76);
    const x = cx + wx * radius * 0.78;
    const y = cy + wy * radius * 0.78;
    if ((x - cx) ** 2 + (y - cy) ** 2 > (radius * 0.95) ** 2) return;
    const color = cell.color || "#27f4ff";
    const morph = cell.morphology || "rod";
    const size = Math.max(2.3, Number(cell.radius || 0.014) * radius * 4.1);
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate((Number(cell.angle || 0)) + Math.sin(t + phase) * 0.18);
    ctx.shadowColor = color;
    ctx.shadowBlur = 8;
    ctx.globalAlpha = 0.78;
    ctx.fillStyle = color;
    ctx.strokeStyle = "rgba(234, 255, 255, 0.92)";
    if (morph === "yeast" || morph === "budding_yeast") {
      ctx.beginPath();
      ctx.arc(0, 0, size * 0.95, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(size * 0.72, -size * 0.22, size * 0.52, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    } else if (morph === "coccus" || morph === "amoeboid") {
      if (morph === "amoeboid") {
        ctx.beginPath();
        for (let i = 0; i < 9; i += 1) {
          const a = (i * Math.PI * 2 / 9) + phase * 0.18;
          const rr = size * (0.85 + Math.sin(phase + t + i) * 0.24);
          const px = Math.cos(a) * rr;
          const py = Math.sin(a) * rr;
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      } else {
        ctx.beginPath();
        ctx.arc(0, 0, size, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
      }
    } else {
      drawPetriMiniRod(ctx, size, color, phase, t);
    }
    ctx.restore();
  });
  ctx.restore();

  ctx.globalAlpha = 1;
  ctx.strokeStyle = "rgba(39, 244, 255, 0.88)";
  ctx.lineWidth = 1.4;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.stroke();
  ctx.globalAlpha = 0.26;
  ctx.beginPath();
  ctx.ellipse(cx, cy, radius * 1.08, radius * 0.74, 0, 0, Math.PI * 2);
  ctx.stroke();

  ctx.globalAlpha = 0.92;
  ctx.fillStyle = "rgba(234, 252, 255, 0.92)";
  ctx.font = "700 10px Consolas, monospace";
  ctx.textAlign = "center";
  ctx.fillText("2 um", cx, Math.max(14, cy - radius + 16));
  ctx.strokeStyle = "rgba(234, 252, 255, 0.78)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(cx - 48, Math.max(10, cy - radius + 10));
  ctx.lineTo(cx - 16, Math.max(10, cy - radius + 10));
  ctx.moveTo(cx + 16, Math.max(10, cy - radius + 10));
  ctx.lineTo(cx + 48, Math.max(10, cy - radius + 10));
  ctx.stroke();

  ctx.restore();
  requestAnimationFrame(drawPetriPreview);
}

async function refreshPetriPreview() {
  if (!window.nexus.getPetriDishProState) return;
  try {
    latestPetriState = await window.nexus.getPetriDishProState();
    const counts = latestPetriState.counts || {};
    setTelemetryText("petri-status", latestPetriState.exists ? "live" : "missing");
    setTelemetryText("petri-counts", `cells ${counts.cells ?? 0} / particles ${counts.particles ?? 0}`);
  } catch (error) {
    setTelemetryText("petri-status", "blocked");
    setTelemetryText("petri-counts", "preview unavailable");
  }
}

function startPetriPreviewLoop() {
  if (!petriLoopHandle) {
    refreshPetriPreview();
    petriLoopHandle = setInterval(refreshPetriPreview, 3000);
  }
  if (!petriAnimationStarted) {
    petriAnimationStarted = true;
    requestAnimationFrame(drawPetriPreview);
  }
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
    setTelemetryText("hud-monitor-state", telemetry.analysis?.status || "stable");
    setTelemetryText("hud-process-count", telemetry.windows?.process_count ?? "--");
    setTelemetryText("hud-uptime", `${Math.round((telemetry.platform?.uptime_seconds || 0) / 60)} min`);
    setTelemetryText("hud-analysis-summary", telemetry.analysis?.summary || "Telemetry analysis unavailable.");
    setTelemetryHtml("hud-process-list", renderProcessManagerRows(telemetry.windows?.task_manager_processes));
    setTelemetryHtml("hud-storage-list", renderTelemetryRows(telemetry.windows?.logical_disks, "No local disk telemetry."));
    setTelemetryHtml("hud-network-list", [
      `<div class="telemetry-subhead">Adapters</div>`,
      renderTelemetryRows(telemetry.windows?.network_adapters, "No active network adapters."),
      `<div class="telemetry-subhead">Counters</div>`,
      renderTelemetryRows(telemetry.windows?.network_stats, "No network counters.")
    ].join(""));
    setTelemetryHtml("hud-recommendations-list", renderTelemetryTextList(telemetry.analysis?.recommendations, "No recommendations."));
    setTelemetryHtml("hud-options-list", renderTelemetryTextList(telemetry.analysis?.options, "No analysis options."));
    setTelemetryText("telemetry-status", "live");
  } catch (error) {
    setTelemetryText("telemetry-status", "blocked");
    setTelemetryText("hud-monitor-state", "blocked");
    setTelemetryText("hud-analysis-summary", `Telemetry unavailable: ${error.message}`);
    setTelemetryHtml("hud-recommendations-list", renderTelemetryTextList([`Telemetry unavailable: ${error.message}`]));
  }
}

function toggleTelemetryHud(force) {
  if (!telemetryHud) return;
  const next = typeof force === "boolean" ? force : !telemetryHud.classList.contains("is-expanded");
  telemetryHud.classList.toggle("is-expanded", next);
  telemetryHud.toggleAttribute("hidden", !next);
  telemetryHud.style.display = next ? "" : "none";
  if (next) refreshTelemetry();
}

function activateTelemetryTab(tabName) {
  document.querySelectorAll("[data-telemetry-tab]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.telemetryTab === tabName);
  });
  document.querySelectorAll("[data-telemetry-panel]").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.telemetryPanel === tabName);
  });
}

async function requestTerminateProcess(pid, name) {
  const numericPid = Number(pid);
  if (!Number.isInteger(numericPid) || numericPid <= 0) return;
  const label = name || `PID ${numericPid}`;
  const confirmed = window.confirm(`End process ${label} (${numericPid})?\n\nNEXUS will block protected/self processes.`);
  if (!confirmed) return;
  setTelemetryText("hud-process-action-status", `terminating ${label} / ${numericPid}`);
  try {
    const result = await window.nexus.terminateProcess({ pid: numericPid, name });
    setTelemetryText("hud-process-action-status", result.ok ? `terminated ${label} / ${numericPid}` : `blocked ${label}: ${result.error || result.stderr || "unknown"}`);
    appendChat("ai", JSON.stringify(result, null, 2), "NEX / task-manager / human-clicked");
    refreshTelemetry();
  } catch (error) {
    setTelemetryText("hud-process-action-status", `terminate failed: ${error.message}`);
  }
}

function renderMetaOrchestratorPanels(panels) {
  const root = document.getElementById("meta-orchestrator-panels");
  if (!root) return;
  root.innerHTML = "";
  (Array.isArray(panels) ? panels : []).forEach((panel, index) => {
    const details = document.createElement("details");
    details.open = index === 0;
    const summary = document.createElement("summary");
    const label = document.createElement("span");
    label.textContent = panel.title || panel.panel_id || "Panel";
    const status = document.createElement("strong");
    status.textContent = panel.status || "unknown";
    summary.appendChild(label);
    summary.appendChild(status);
    const body = document.createElement("pre");
    body.textContent = JSON.stringify({
      summary: panel.summary,
      details: panel.details
    }, null, 2);
    details.appendChild(summary);
    details.appendChild(body);
    root.appendChild(details);
  });
}

async function refreshMetaOrchestratorHud() {
  try {
    const exists = window.nexus.surfaceExists ? await window.nexus.surfaceExists(META_ORCHESTRATOR_SURFACE) : true;
    if (!exists) {
      throw new Error("Run .\\scripts\\nexus.ps1 meta-orchestrator to generate this surface.");
    }
    const packet = JSON.parse(await window.nexus.readSurface(META_ORCHESTRATOR_SURFACE));
    setTelemetryText("meta-orchestrator-status", packet.status || "unknown");
    setTelemetryText("meta-orchestrator-loop", packet.recommended_next_loop || "unknown");
    setTelemetryText("hud-meta-status", packet.status || "unknown");
    setTelemetryText("hud-meta-loop", packet.recommended_next_loop || "unknown");
    setTelemetryText("hud-meta-command", packet.recommended_next_command || "No command declared.");
    setTelemetryText("hud-meta-raw", JSON.stringify(packet, null, 2));
    renderMetaOrchestratorPanels(packet.panels || []);
  } catch (error) {
    setTelemetryText("meta-orchestrator-status", "missing");
    setTelemetryText("meta-orchestrator-loop", "generate");
    setTelemetryText("hud-meta-status", "missing");
    setTelemetryText("hud-meta-loop", "meta-orchestrator");
    setTelemetryText("hud-meta-command", ".\\scripts\\nexus.ps1 meta-orchestrator");
    setTelemetryText("hud-meta-raw", `Meta-orchestrator report unavailable: ${error.message}`);
    renderMetaOrchestratorPanels([{
      title: "Generate Surface",
      status: "blocked",
      summary: "The HUD is read-only and needs the report surface first.",
      details: { command: ".\\scripts\\nexus.ps1 meta-orchestrator" }
    }]);
  }
}

function toggleMetaOrchestratorHud(force) {
  if (!metaOrchestratorHud) return;
  const next = typeof force === "boolean" ? force : !metaOrchestratorHud.classList.contains("is-expanded");
  metaOrchestratorHud.classList.toggle("is-expanded", next);
  metaOrchestratorHud.toggleAttribute("hidden", !next);
  metaOrchestratorHud.style.display = next ? "" : "none";
  if (next) refreshMetaOrchestratorHud();
}
function toggleModelSelectorHud(force) {
  if (!modelSelectorHud) return;
  const next = typeof force === "boolean" ? force : !modelSelectorHud.classList.contains("is-expanded");
  modelSelectorHud.classList.toggle("is-expanded", next);
  modelSelectorHud.toggleAttribute("hidden", !next);
  modelSelectorHud.style.display = next ? "" : "none";
  modelSelectorToggle?.setAttribute("aria-expanded", String(next));
}

function bindModelSelectorHud() {
  if (modelSelectorHudBound) return;
  modelSelectorHudBound = true;
  modelSelectorToggle?.addEventListener("click", () => toggleModelSelectorHud());
  modelSelectorClose?.addEventListener("click", () => toggleModelSelectorHud(false));
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
  if (selectorHudStatus) selectorHudStatus.textContent = setting.label;

  pushConsole("NEXUS", `${setting.note} Selector source=${source}.`);
}

function initRoleSelector() {
  bindModelSelectorHud();
  if (!roleSelect) return;
  roleSelect.addEventListener("change", () => setSelectorRole(roleSelect.value, "select"));
  selectorSwitch?.addEventListener("click", () => { setSelectorRole(roleSelect.value, "glyph"); toggleModelSelectorHud(true); });
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

function parseGovernedChatCommand(raw) {
  const text = String(raw || "").trim();
  const lower = text.toLowerCase();

  if (lower.startsWith("/run ")) {
    const lane = text.slice(5).trim().split(/\s+/)[0] || "";
    return { kind: "lane", lane, raw: text, relay: true };
  }

  if (lower === "/run") {
    return { kind: "help", raw: text, relay: true };
  }

  if (text.startsWith("/")) {
    const lane = text.slice(1).trim().split(/\s+/)[0] || "";
    return { kind: "lane", lane, raw: text, relay: false };
  }

  return null;
}

function formatRelayOutput(lane, result) {
  const code = Number(result?.code ?? -1);
  const ok = code === 0;
  const rawEvidence = String(result?.stdout || result?.stderr || "No lane output returned.").trim();
  let evidence = rawEvidence;
  let parsedStatus = "";
  let parsedSystem = "";

  try {
    const parsed = JSON.parse(rawEvidence);
    parsedStatus = parsed.status || parsed.result || parsed.kind || "";
    parsedSystem = parsed.system || parsed.version || "";
    evidence = JSON.stringify(parsed, null, 2);
  } catch (_error) {
    evidence = rawEvidence;
  }

  const clipped = evidence.length > 7000
    ? `${evidence.slice(0, 7000)}\n\n[relay evidence clipped at 7000 chars]`
    : evidence;

  const resultWord = ok ? "PASS" : "BLOCKED";
  const statusText = parsedStatus ? `${resultWord} / ${parsedStatus}` : resultWord;
  const systemText = parsedSystem ? `\nSystem: ${parsedSystem}` : "";

  return [
    "NEX SHELL RELAY REPORT",
    "======================",
    `What ran: scripts/nexus.ps1 ${lane}`,
    `Result: ${statusText}`,
    `Exit code: ${Number.isNaN(code) ? "unknown" : code}${systemText}`,
    "",
    "Human-readable meaning:",
    ok
      ? "The governed NEXUS lane completed through the local hidden bridge."
      : "The governed NEXUS lane returned a blocker or non-zero bridge result.",
    "",
    "Evidence:",
    clipped || "No evidence returned.",
    "",
    "Next allowed action:",
    ok
      ? "Review this report, then choose the next governed lane or ask NEX for a recommendation."
      : "Inspect the blocker above. Do not promote memory, mutate files, or compound until the lane is clean.",
    "",
    "Boundary:",
    NEX_SHELL_RELAY_MODE_BOUNDARY
  ].join("\n");
}

function relayHelpText() {
  const lanes = allowlistedCommands.length ? allowlistedCommands.join(", ") : "status, feedback, interconnect, compact, pack";
  return [
    "NEX SHELL RELAY MODE",
    "====================",
    "Use /run <lane> to run a governed local lane without leaving chat.",
    "",
    `Allowed lanes: ${lanes}`,
    "",
    "Examples:",
    "/run status",
    "/run interconnect",
    "/run feedback",
    "/run compact",
    "/run pack",
    "",
    "Boundary:",
    NEX_SHELL_RELAY_MODE_BOUNDARY
  ].join("\n");
}

async function runGovernedLane(lane) {
  if (!allowlistedCommands.includes(lane)) {
    const blocked = [
      "NEX SHELL RELAY BLOCKED",
      "=======================",
      `Requested lane: ${lane || "empty"}`,
      `Allowed lanes: ${allowlistedCommands.join(", ")}`,
      "",
      "Reason:",
      "The chat relay only runs allowlisted NEXUS lanes. arbitrary PowerShell is blocked.",
      "",
      "Boundary:",
      NEX_SHELL_RELAY_MODE_BOUNDARY
    ].join("\n");

    pushConsole("WARN", `Lane '${lane}' is not allowlisted in Electron.`);
    writeOutput(blocked, { preTranslated: true });
    appendChat("ai", blocked, "NEX / shell-relay / blocked");
    return;
  }

  activeLane.textContent = lane;
  statusEl.textContent = "running";
  setProcessing(true);
  setBuffer(24, "relay");
  pushConsole("NEXUS", `Shell relay engaged for governed lane '${lane}'.`);

  try {
    setBuffer(52, "relay");
    const result = await window.nexus.runLane(lane);
    const relayReport = formatRelayOutput(lane, result);

    setBuffer(result.code === 0 ? 100 : 0, result.code === 0 ? "complete" : "blocked");
    writeOutput(relayReport, { preTranslated: true });
    statusEl.textContent = result.code === 0 ? "stable" : "blocked";
    appendChat("ai", relayReport, `NEX / shell-relay / lane=${lane}`);
  } catch (error) {
    const relayReport = [
      "NEX SHELL RELAY EXCEPTION",
      "=========================",
      `What ran: scripts/nexus.ps1 ${lane}`,
      "Result: BLOCKED",
      "",
      "Evidence:",
      error.stack || error.message,
      "",
      "Boundary:",
      NEX_SHELL_RELAY_MODE_BOUNDARY
    ].join("\n");

    setBuffer(0, "error");
    statusEl.textContent = "blocked";
    writeOutput(relayReport, { preTranslated: true });
    appendChat("ai", relayReport, `NEX / shell-relay / exception lane=${lane}`);
  } finally {
    setProcessing(false);
  }
}
function extractPowerShellFence(text) {
  const raw = String(text || "").trim();
  const fenced = raw.match(/```(?:powershell|ps1|pwsh)?\s*([\s\S]*?)```/i);
  return (fenced ? fenced[1] : raw).trim();
}

function parseHandoffShellAction(raw) {
  const text = String(raw || "").trim();
  const lower = text.toLowerCase();

  if (lower === "/handoff" || lower === "/handoff help") {
    return { kind: "help" };
  }

  if (lower.startsWith("/handoff run")) {
    if (currentRole() !== "HANDOFF") {
      return { kind: "blocked_role", scriptText: "" };
    }
    const scriptText = extractPowerShellFence(text.slice("/handoff run".length));
    return { kind: "run", scriptText };
  }

  if (lower.startsWith("/handoff stage")) {
    const scriptText = extractPowerShellFence(text.slice("/handoff stage".length));
    return { kind: "stage", scriptText };
  }

  return null;
}

function handoffShellHelpText() {
  return [
    "NEX HANDOFF ACTION SHELL",
    "=======================",
    "Set Local Voice / Relay to HANDOFF.",
    "",
    "Then paste a ChatGPT/Codex script into chat like this:",
    "",
    "/handoff run",
    "```powershell",
    "# script goes here",
    "```",
    "",
    "What happens:",
    "- Electron writes the script to reports/handoff_queue/<time>/handoff_action.ps1",
    "- Hidden PowerShell runs it with cwd at the repo root",
    "- Output returns here as a compact report",
    "- No visible PowerShell window is required",
    "",
    "Boundary:",
    NEX_HANDOFF_ACTION_SHELL_BOUNDARY
  ].join("\n");
}

function formatHandoffShellResult(result) {
  const code = Number(result?.code ?? -1);
  const ok = code === 0;
  const stdout = String(result?.stdout || "").trim();
  const stderr = String(result?.stderr || "").trim();
  const evidence = [stdout, stderr ? `STDERR:\n${stderr}` : ""].filter(Boolean).join("\n\n") || "No process output returned.";
  const clipped = evidence.length > 9000 ? `${evidence.slice(0, 9000)}\n\n[handoff evidence clipped at 9000 chars]` : evidence;

  return [
    "NEX HANDOFF ACTION REPORT",
    "========================",
    "What ran: human-authorized HANDOFF script",
    `Result: ${ok ? "PASS" : "BLOCKED"}`,
    `Exit code: ${Number.isNaN(code) ? "unknown" : code}`,
    result?.script_path ? `Script path: ${result.script_path}` : "",
    result?.report_path ? `Report path: ${result.report_path}` : "",
    "",
    "Human-readable meaning:",
    ok
      ? "The script completed through the hidden local PowerShell bridge."
      : "The script was blocked or returned a non-zero exit code.",
    "",
    "Evidence:",
    clipped,
    "",
    "Next allowed action:",
    ok
      ? "Review the output, then ask ChatGPT/NEX for the next governed patch or lane."
      : "Inspect the blocker. Do not push or compound until the failure is resolved.",
    "",
    "Boundary:",
    result?.boundary || NEX_HANDOFF_ACTION_SHELL_BOUNDARY
  ].filter(Boolean).join("\n");
}

async function runHandoffShellAction(scriptText) {
  if (!scriptText || !scriptText.trim()) {
    const blocked = [
      "NEX HANDOFF ACTION BLOCKED",
      "=========================",
      "Reason: no script text was provided after /handoff run.",
      "",
      handoffShellHelpText()
    ].join("\n");
    appendChat("ai", blocked, "NEX / handoff-shell / blocked");
    writeOutput(blocked, { preTranslated: true });
    return;
  }

  if (!window.nexus.runHandoffScript) {
    const blocked = [
      "NEX HANDOFF ACTION BLOCKED",
      "=========================",
      "Reason: preload does not expose runHandoffScript.",
      "",
      "Boundary:",
      NEX_HANDOFF_ACTION_SHELL_BOUNDARY
    ].join("\n");
    appendChat("ai", blocked, "NEX / handoff-shell / blocked");
    writeOutput(blocked, { preTranslated: true });
    return;
  }

  activeLane.textContent = "handoff:shell";
  statusEl.textContent = "handoff-running";
  setProcessing(true);
  setBuffer(22, "handoff");
  pushConsole("NEXUS", "HANDOFF action shell engaged. Hidden PowerShell bridge is running the authorized script.");

  try {
    setBuffer(48, "handoff");
    const result = await window.nexus.runHandoffScript({
      scriptText,
      role: "HANDOFF",
      source: "nex_chat_handoff",
      authorized: true,
      timeoutMs: 900000
    });
    const report = formatHandoffShellResult(result);
    setBuffer(result.code === 0 ? 100 : 0, result.code === 0 ? "complete" : "blocked");
    statusEl.textContent = result.code === 0 ? "stable" : "blocked";
    writeOutput(report, { preTranslated: true });
    appendChat("ai", report, "NEX / HANDOFF / action-shell");
  } catch (error) {
    const report = [
      "NEX HANDOFF ACTION EXCEPTION",
      "===========================",
      "Result: BLOCKED",
      "",
      "Evidence:",
      error.stack || error.message,
      "",
      "Boundary:",
      NEX_HANDOFF_ACTION_SHELL_BOUNDARY
    ].join("\n");
    setBuffer(0, "error");
    statusEl.textContent = "blocked";
    writeOutput(report, { preTranslated: true });
    appendChat("ai", report, "NEX / HANDOFF / action-shell-error");
  } finally {
    setProcessing(false);
  }
}
function isSimpleNexConversation(text) {
  const value = String(text || "").trim();
  if (!value) return false;
  if (value.startsWith("/")) return false;
  if (/^(run|status|evolve|reflect|feedback|interconnect|handoff|git|commit|push|pull|shell|powershell|python|npm|node)\b/i.test(value)) return false;
  if (/\b(commit|push|delete|mutate|execute|run script|apply patch|write file|stage files|repo mutation)\b/i.test(value)) return false;
  if (/^(hey|hi|hello|yo|sup|you there|are you there|u there|ping|testing|test|what's up|whats up)\??!?$/i.test(value)) return true;
  if (/^(what do you think|thoughts|help me|can you|tell me|explain|walk me through|talk to me)/i.test(value)) return true;
  return value.length <= 260;
}

function naturalNexGreeting(prompt, role) {
  const mode = role === "FAST" ? "FAST / Phi-4-mini"
    : role === "BALANCED" ? "BALANCED / Phi-4-mini"
    : role === "DEEP" ? "DEEP / Mistral"
    : role === "TNN" ? "Tesseract Neural Network"
    : role === "HANDOFF" ? "HANDOFF / ChatGPT-Codex"
    : role;
  const value = String(prompt || "").trim().toLowerCase();
  if (/^(you there|are you there|u there|ping|testing|test)\??!?$/.test(value)) {
    return `Yeah, I'm here. ${mode} is active. Send me what you want to work on.`;
  }
  if (/^(hey|hi|hello|yo|sup|what's up|whats up)\??!?$/.test(value)) {
    return `Hey, I'm here. ${mode} is active. What are we working on?`;
  }
  return `I'm here. ${mode} is active. Talk to me normally, or use /run when you want a governed lane.`;
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
    if (isSimpleNexConversation(prompt)) {
      const greeting = naturalNexGreeting(prompt, role);
      appendChat("ai", greeting, `NEX / ${role} / conversational`);
      writeOutput(greeting, { preTranslated: true });
      statusEl.textContent = "stable";
      setBuffer(100, "complete");
      return;
    }
    // Offline graceful degradation: if the local model endpoint is blocked, keep chat responsive
    // and route without calling a model (evidence-forward, recommendation-only).
    const ollama = await ensureLocalOllamaBackend();
    const canCallModel = (role !== "HANDOFF") && (ollama?.ok !== false);
    if (!canCallModel && role !== "HANDOFF") {
      pushConsole("WARN", "Local model endpoint is blocked; routing without --call-model.");
    }
    if (!window.nexus.askNex) {
      throw new Error("NEX chat bridge is not exposed by preload.");
    }

    const result = await window.nexus.askNex({
      prompt,
      role,
      callModel: canCallModel
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
  startPetriPreviewLoop();
  setBuffer(10, "hydrate");
  toggleTelemetryHud(false);
  toggleMetaOrchestratorHud(false);
  clearSystemErrorHud();
  bindModelSelectorHud();

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
document.querySelectorAll("[data-telemetry-tab]").forEach((button) => {
  button.addEventListener("click", () => activateTelemetryTab(button.dataset.telemetryTab));
});
telemetryHud?.addEventListener("click", (event) => {
  const button = event.target?.closest?.("[data-terminate-pid]");
  if (!button) return;
  requestTerminateProcess(button.dataset.terminatePid, button.dataset.terminateName || "");
});
document.getElementById("meta-orchestrator-popout")?.addEventListener("click", () => toggleMetaOrchestratorHud());
document.getElementById("meta-orchestrator-close")?.addEventListener("click", () => toggleMetaOrchestratorHud(false));
petriOpen?.addEventListener("click", openPetriDishPro);
petriMiniBody?.addEventListener("click", openPetriDishPro);
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

  const handoffAction = parseHandoffShellAction(raw);
  if (handoffAction?.kind === "help") {
    appendChat("human", raw, "handoff shell help");
    const help = handoffShellHelpText();
    appendChat("ai", help, "NEX / HANDOFF / action-shell-help");
    writeOutput(help, { preTranslated: true });
    return;
  }

  if (handoffAction?.kind === "blocked_role") {
    const blocked = [
      "NEX HANDOFF ACTION BLOCKED",
      "=========================",
      "Reason: Local Voice / Relay must be set to HANDOFF before /handoff run can execute a script.",
      "",
      "Boundary:",
      NEX_HANDOFF_ACTION_SHELL_BOUNDARY
    ].join("\n");
    appendChat("human", raw, "handoff shell blocked");
    appendChat("ai", blocked, "NEX / HANDOFF / blocked");
    writeOutput(blocked, { preTranslated: true });
    return;
  }

  if (handoffAction?.kind === "stage") {
    const staged = [
      "NEX HANDOFF ACTION STAGED",
      "========================",
      "The script was recognized but not executed.",
      "",
      "Run it with /handoff run when you are ready.",
      "",
      "Boundary:",
      NEX_HANDOFF_ACTION_SHELL_BOUNDARY
    ].join("\n");
    appendChat("human", raw, "handoff shell staged");
    appendChat("ai", staged, "NEX / HANDOFF / staged");
    writeOutput(staged, { preTranslated: true });
    return;
  }

  if (handoffAction?.kind === "run") {
    appendChat("human", "/handoff run [script]", "HANDOFF action authorized");
    await runHandoffShellAction(handoffAction.scriptText);
    return;
  }
  const command = parseGovernedChatCommand(raw);
  if (command?.kind === "help") {
    appendChat("human", raw, "shell relay help");
    const help = relayHelpText();
    appendChat("ai", help, "NEX / shell-relay / help");
    writeOutput(help, { preTranslated: true });
    return;
  }

  if (command?.kind === "lane") {
    appendChat("human", raw, command.relay ? "shell relay request" : "slash command");
    await runGovernedLane(command.lane);
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

