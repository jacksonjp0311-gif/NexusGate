const { app, BrowserWindow, ipcMain, shell } = require("electron");
const fs = require("fs");
const path = require("path");
const os = require("os");
const http = require("http");
const { spawn } = require("child_process");

const repoRoot = path.resolve(__dirname, "..");
const appIconPath = path.join(repoRoot, 'electron', 'assets', 'icons', 'nexus_gate.ico');
const isSmoke = process.argv.includes("--smoke");
const gotSingleInstanceLock = isSmoke || app.requestSingleInstanceLock();
if (!gotSingleInstanceLock) {
  app.quit();
}
let mainWindow = null;
let petriWindow = null;
let petriIpcRegistered = false;
const petriDishProRoot = path.join(repoRoot, "PetriDishPro");
const petriElectronRoot = path.join(petriDishProRoot, "electron");
const neuralRepoGraphPath = path.join(repoRoot, "state", "neural_activity", "repo_neural_graph_latest.json");

app.on("second-instance", () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
  }
});

const smokeReportPath = path.join(repoRoot, "reports", "nexus_electron_smoke_report_latest.json");
let smokeReportWritten = false;

if (isSmoke) {
  app.setPath("userData", path.join(os.tmpdir(), `nexus-gate-electron-smoke-${process.pid}`));
  app.disableHardwareAcceleration();
}

const READ_SURFACES = new Set([
  "state/ai_feedback_context_latest.json",
  "docs/feedback/FEEDBACK_LOG.md",
  "reports/nexus_feedback_interface_report_latest.json",
  "reports/nexus_self_healing_report_latest.json",
  "reports/nexus_reflective_loop_report_latest.json",
  "reports/nexus_domain_intelligence_report_latest.json",
  "reports/nexus_meta_orchestrator_gate_latest.json",
  "reports/nexus_loop_orchestration_report_latest.json",
  "state/nexus_lineage_manifest_latest.json",
  "state/interface_adapter_contract_index.v0.3.7.json",
  "state/domain_intelligence_index.v0.4.0.json",
  "state/repo_native_learning_index.v0.4.0.json",
  "state/codex_orchestration_index.v0.4.0.json",
  "state/loops/nexus_loop_orchestration_latest.json",
  "reports/tui/nexus_tui_ai_handoff_latest.txt",
  "reports/tui/nexus_tui_snapshot_latest.html",
  "reports/tui/nexus_tui_surface_latest.json",
  "state/neural_activity/repo_neural_graph_latest.json"
]);

const NEX_CHAT_ROLES = new Set(["FAST", "BALANCED", "DEEP", "TNN", "HANDOFF"]);
const NEX_MAX_PROMPT_CHARS = 4000;
const HANDOFF_SCRIPT_MAX_CHARS = 180000;
let activeNexChild = null;
let managedOllamaProcess = null;
let lastCpuSample = null;

function ollamaTagsReady(timeoutMs = 900) {
  return new Promise((resolve) => {
    const request = http.get("http://127.0.0.1:11434/api/tags", { timeout: timeoutMs }, (response) => {
      response.resume();
      resolve(response.statusCode >= 200 && response.statusCode < 500);
    });
    request.on("timeout", () => {
      request.destroy();
      resolve(false);
    });
    request.on("error", () => resolve(false));
  });
}

function resolveOllamaBinary() {
  const candidates = [
    process.env.OLLAMA_EXE,
    path.join(os.homedir(), "AppData", "Local", "Programs", "Ollama", "ollama.exe"),
    path.join(process.env.LOCALAPPDATA || "", "Programs", "Ollama", "ollama.exe"),
    "ollama"
  ].filter(Boolean);

  for (const candidate of candidates) {
    if (candidate === "ollama" || fs.existsSync(candidate)) return candidate;
  }
  return "ollama";
}

function resolveOllamaModels() {
  const explicit = process.env.OLLAMA_MODELS;
  if (explicit && fs.existsSync(explicit)) return explicit;
  return path.join(os.homedir(), ".ollama", "models");
}

async function ensureOllamaBackend() {
  if (await ollamaTagsReady()) {
    return {
      ok: true,
      status: "already_running",
      endpoint: "http://127.0.0.1:11434",
      hidden_backend: true,
      boundary: "Ollama service is used only as a local model endpoint."
    };
  }

  const binary = resolveOllamaBinary();
  const modelsPath = resolveOllamaModels();
  const env = {
    ...process.env,
    CUDA_VISIBLE_DEVICES: process.env.CUDA_VISIBLE_DEVICES || "-1",
    NEXUS_OLLAMA_NUM_GPU: process.env.NEXUS_OLLAMA_NUM_GPU || "0",
    OLLAMA_MODELS: modelsPath
  };

  try {
    managedOllamaProcess = spawn(binary, ["serve"], {
      cwd: repoRoot,
      shell: false,
      detached: true,
      windowsHide: true,
      stdio: "ignore",
      env
    });
    managedOllamaProcess.unref();
  } catch (error) {
    return {
      ok: false,
      status: "start_failed",
      error: error.message,
      binary,
      modelsPath,
      boundary: "No shell authority granted; hidden backend launch failed."
    };
  }

  for (let attempt = 0; attempt < 20; attempt += 1) {
    if (await ollamaTagsReady(700)) {
      return {
        ok: true,
        status: "started_hidden",
        endpoint: "http://127.0.0.1:11434",
        pid: managedOllamaProcess?.pid,
        modelsPath,
        cpu_fallback: true,
        boundary: "Started hidden Ollama backend only; no repo mutation, tool authority, or model-output execution."
      };
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  return {
    ok: false,
    status: "not_ready_after_start",
    endpoint: "http://127.0.0.1:11434",
    pid: managedOllamaProcess?.pid,
    modelsPath,
    boundary: "NEX can report the blocker; it may not self-repair without human authorization."
  };
}
function sampleCpuTimes() {
  const cpus = os.cpus();
  let idle = 0;
  let total = 0;
  for (const cpu of cpus) {
    idle += cpu.times.idle;
    total += Object.values(cpu.times).reduce((sum, value) => sum + value, 0);
  }
  return { idle, total };
}

function readCpuPercent() {
  const current = sampleCpuTimes();
  if (!lastCpuSample) {
    lastCpuSample = current;
    return 0;
  }
  const idleDelta = current.idle - lastCpuSample.idle;
  const totalDelta = current.total - lastCpuSample.total;
  lastCpuSample = current;
  if (totalDelta <= 0) return 0;
  return Math.max(0, Math.min(100, (1 - idleDelta / totalDelta) * 100));
}

function runFixedPowerShell(scriptText, timeoutMs = 1800) {
  return new Promise((resolve) => {
    const child = spawn("powershell.exe", [
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-Command",
      scriptText
    ], {
      cwd: repoRoot,
      shell: false,
      windowsHide: true
    });

    let stdout = "";
    let stderr = "";
    const timer = setTimeout(() => {
      try { child.kill(); } catch (_error) {}
      resolve({ ok: false, stdout, stderr: stderr + "telemetry timeout" });
    }, timeoutMs);

    child.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
    child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
    child.on("error", (error) => {
      clearTimeout(timer);
      resolve({ ok: false, stdout, stderr: stderr + error.message });
    });
    child.on("close", (code) => {
      clearTimeout(timer);
      resolve({ ok: code === 0, stdout, stderr, code });
    });
  });
}

function timestampForPath() {
  return new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
}
function persistHandoffReport(reportPath, report) {
  const fallbackRoot = path.join(repoRoot, "reports", "handoff_queue", "recovered");
  const targetPath = reportPath || path.join(fallbackRoot, `handoff_action_report_${timestampForPath()}.json`);

  function writeReport(target) {
    fs.mkdirSync(path.dirname(target), { recursive: true });
    report.report_path = target;
    fs.writeFileSync(target, JSON.stringify(report, null, 2), "utf8");
    return target;
  }

  try {
    return writeReport(targetPath);
  } catch (error) {
    fs.mkdirSync(fallbackRoot, { recursive: true });
    const fallbackPath = path.join(fallbackRoot, `handoff_action_report_${timestampForPath()}.json`);
    report.original_report_path = targetPath;
    report.report_write_error = error.message;
    return writeReport(fallbackPath);
  }
}

function sanitizeHandoffScriptText(value) {
  const text = String(value || "").replace(/\0/g, "").trim();
  if (!text) {
    throw new Error("HANDOFF action script is empty.");
  }
  if (text.length > HANDOFF_SCRIPT_MAX_CHARS) {
    throw new Error(`HANDOFF action script exceeds ${HANDOFF_SCRIPT_MAX_CHARS} characters.`);
  }
  return text;
}

function scanHandoffScriptText(text) {
  const blocked = [];
  const checks = [
    { name: "format_volume", pattern: /\bFormat-Volume\b/i },
    { name: "set_execution_policy", pattern: /\bSet-ExecutionPolicy\b/i },
    { name: "invoke_expression", pattern: /\bInvoke-Expression\b|\biex\b/i },
    { name: "global_c_drive_delete", pattern: /Remove-Item[\s\S]{0,80}(C:\\|C:\/)[\s\S]{0,80}-Recurse[\s\S]{0,80}-Force/i },
    { name: "download_pipe_to_shell", pattern: /(Invoke-WebRequest|iwr|curl|wget)[\s\S]{0,120}\|[\s\S]{0,80}(powershell|pwsh|cmd)/i }
  ];

  for (const check of checks) {
    if (check.pattern.test(text)) blocked.push(check.name);
  }

  return blocked;
}

function runHandoffPowerShell(scriptText, packet = {}) {
  return new Promise((resolve) => {
    const text = sanitizeHandoffScriptText(scriptText);
    const blocked = scanHandoffScriptText(text);
    if (blocked.length) {
      resolve({
        code: 91,
        stdout: "",
        stderr: `HANDOFF action blocked by safety scan: ${blocked.join(", ")}`,
        blocked,
        boundary: "HANDOFF shell bridge rejected a high-risk script pattern before execution."
      });
      return;
    }

    const handoffRoot = path.join(repoRoot, "reports", "handoff_queue", timestampForPath());
    fs.mkdirSync(handoffRoot, { recursive: true });

    const scriptPath = path.join(handoffRoot, "handoff_action.ps1");
    const reportPath = path.join(handoffRoot, "handoff_action_report.json");
    const metadataPath = path.join(handoffRoot, "handoff_action_metadata.json");

    const header = [
      "# NEXUS HANDOFF ACTION SHELL v0.7.4",
      "# Human-authorized local script executed through Electron hidden PowerShell bridge.",
      "# Boundary: ChatGPT/NEX text is not authority; the human initiated /handoff run.",
      ""
    ].join("\r\n");

    fs.writeFileSync(scriptPath, header + text + "\r\n", "utf8");
    fs.writeFileSync(metadataPath, JSON.stringify({
      system: "NEXUS GATE",
      version: "0.7.4-handoff-action-shell",
      generated_at_utc: new Date().toISOString(),
      source: String(packet.source || "handoff_chat"),
      role: String(packet.role || "HANDOFF"),
      authorized: Boolean(packet.authorized),
      cwd: repoRoot,
      script_path: scriptPath,
      boundary: "PowerShell is hidden execution substrate. The human uses HANDOFF chat as the front door."
    }, null, 2), "utf8");

    const child = spawn("powershell.exe", [
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      scriptPath
    ], {
      cwd: repoRoot,
      shell: false,
      windowsHide: true,
      env: {
        ...process.env,
        CUDA_VISIBLE_DEVICES: process.env.CUDA_VISIBLE_DEVICES || "-1",
        NEXUS_OLLAMA_NUM_GPU: process.env.NEXUS_OLLAMA_NUM_GPU || "0",
        NEXUS_HANDOFF_ACTION_SHELL: "1"
      }
    });

    activeNexChild = child;
    let stdout = "";
    let stderr = "";
    const timeoutMs = Math.max(30000, Math.min(Number(packet.timeoutMs || 900000), 1800000));
    const timer = setTimeout(() => {
      try { child.kill(); } catch (_error) {}
      stderr += "\nHANDOFF action timeout.";
    }, timeoutMs);

    child.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
    child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
    child.on("error", (error) => {
      clearTimeout(timer);
      if (activeNexChild === child) activeNexChild = null;
      const report = {
        system: "NEXUS GATE",
        version: "0.7.4-handoff-action-shell",
        status: "blocked",
        code: -1,
        stdout,
        stderr: stderr + error.message,
        script_path: scriptPath,
        report_path: reportPath,
        boundary: "HANDOFF script failed before process start."
      };
      persistHandoffReport(reportPath, report);
      resolve(report);
    });
    child.on("close", (code) => {
      clearTimeout(timer);
      if (activeNexChild === child) activeNexChild = null;
      const report = {
        system: "NEXUS GATE",
        version: "0.7.4-handoff-action-shell",
        status: code === 0 ? "pass" : "blocked",
        code,
        stdout,
        stderr,
        script_path: scriptPath,
        metadata_path: metadataPath,
        report_path: reportPath,
        boundary: "HANDOFF chat executed a human-authorized script through hidden PowerShell. This does not grant autonomous authority."
      };
      persistHandoffReport(reportPath, report);
      resolve(report);
    });
  });
}
async function readWindowsTelemetry() {
  const script = `
$ErrorActionPreference = "SilentlyContinue"
$gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1 Name,AdapterRAM,DriverVersion
$disk = Get-PSDrive -Name C | Select-Object -First 1 Used,Free
$ollama = @(Get-Process ollama,llama-server -ErrorAction SilentlyContinue | Select-Object ProcessName,Id,CPU,WorkingSet64)
$gpuLoad = $null
try {
  $samples = Get-Counter '\\GPU Engine(*)\\Utilization Percentage' -ErrorAction Stop
  $gpuLoad = [Math]::Round((($samples.CounterSamples | Measure-Object CookedValue -Sum).Sum), 1)
} catch { $gpuLoad = $null }
[pscustomobject]@{
  gpu_name = $gpu.Name
  gpu_adapter_ram = $gpu.AdapterRAM
  gpu_driver = $gpu.DriverVersion
  gpu_load_percent = $gpuLoad
  disk_c_free = $disk.Free
  disk_c_used = $disk.Used
  ollama_processes = $ollama
} | ConvertTo-Json -Depth 5
`;
  const result = await runFixedPowerShell(script, 2200);
  if (!result.ok) {
    return { ok: false, error: result.stderr || "windows telemetry unavailable" };
  }
  try {
    return { ok: true, ...JSON.parse(result.stdout || "{}") };
  } catch (error) {
    return { ok: false, error: error.message, raw: result.stdout };
  }
}
function sanitizeNexPrompt(value) {
  const text = String(value || "").replace(/\0/g, "").trim();
  if (!text) {
    throw new Error("NEX prompt is empty.");
  }
  if (text.length > NEX_MAX_PROMPT_CHARS) {
    throw new Error(`NEX prompt exceeds ${NEX_MAX_PROMPT_CHARS} characters.`);
  }
  return text;
}

function normalizeNexRole(value) {
  const role = String(value || "DEEP").toUpperCase();
  if (!NEX_CHAT_ROLES.has(role)) {
    throw new Error(`NEX role is not allowlisted: ${value}`);
  }
  return role;
}

function readJsonIfPresent(filePath) {
  try {
    if (!fs.existsSync(filePath)) return null;
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    return { parse_error: error.message };
  }
}

function neuralPathHash(value) {
  let hash = 2166136261;
  for (const ch of String(value || "")) {
    hash ^= ch.charCodeAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16);
}

function shouldSkipNeuralPath(relativePath, entryName) {
  const normalized = String(relativePath || "").replace(/\\/g, "/");
  const blockedNames = new Set([".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache"]);
  if (blockedNames.has(entryName)) return true;
  if (normalized.includes("/node_modules/") || normalized.includes("/.git/") || normalized.includes("/__pycache__/")) return true;
  if (normalized.endsWith(".tar.gz") || normalized.endsWith(".zip") || normalized.endsWith(".pyc")) return true;
  return false;
}

function classifyNeuralPath(relativePath, isDirectory) {
  if (isDirectory) return relativePath ? "folder" : "root";
  const ext = path.extname(relativePath).toLowerCase();
  if (ext === ".py") return "python";
  if (ext === ".js" || ext === ".mjs" || ext === ".cjs") return "javascript";
  if (ext === ".html" || ext === ".css") return "interface";
  if (ext === ".json") return "state";
  if (ext === ".md") return "doctrine";
  if (ext === ".ps1" || ext === ".sh" || ext === ".bat") return "operator_lane";
  return "artifact";
}

function buildNeuralRepoGraph() {
  const generatedAtUtc = new Date().toISOString();
  const nodes = [{
    id: "repo:nexus-gate",
    path: ".",
    name: "nexus-gate",
    type: "root",
    depth: 0,
    weight: 10,
    modified: fs.statSync(repoRoot).mtimeMs
  }];
  const edges = [];
  const queue = [{ abs: repoRoot, rel: "", parentId: "repo:nexus-gate", depth: 0 }];
  const maxNodes = 720;
  const maxDepth = 5;

  while (queue.length && nodes.length < maxNodes) {
    const current = queue.shift();
    let entries = [];
    try {
      entries = fs.readdirSync(current.abs, { withFileTypes: true });
    } catch (_error) {
      continue;
    }

    entries
      .filter((entry) => !shouldSkipNeuralPath(path.join(current.rel, entry.name), entry.name))
      .sort((a, b) => Number(b.isDirectory()) - Number(a.isDirectory()) || a.name.localeCompare(b.name))
      .forEach((entry) => {
        if (nodes.length >= maxNodes) return;
        const rel = path.join(current.rel, entry.name).replace(/\\/g, "/");
        const abs = path.join(current.abs, entry.name);
        const isDirectory = entry.isDirectory();
        let stat = null;
        try { stat = fs.statSync(abs); } catch (_error) {}
        const id = `repo:${neuralPathHash(rel)}`;
        nodes.push({
          id,
          path: rel,
          name: entry.name,
          type: classifyNeuralPath(rel, isDirectory),
          depth: current.depth + 1,
          weight: isDirectory ? 3.2 : Math.max(0.7, Math.min(4.5, Math.log10((stat?.size || 1) + 10))),
          size: stat?.size || 0,
          modified: stat?.mtimeMs || 0
        });
        edges.push({
          from: current.parentId,
          to: id,
          type: isDirectory ? "folder_branch" : "file_synapse",
          weight: isDirectory ? 0.9 : 0.35
        });
        if (isDirectory && current.depth + 1 < maxDepth) {
          queue.push({ abs, rel, parentId: id, depth: current.depth + 1 });
        }
      });
  }

  const graph = {
    system: "NEXUS GATE",
    surface: "neural_activity_repo_graph",
    version: "v0.1.2",
    generated_at_utc: generatedAtUtc,
    source_root: repoRoot,
    node_count: nodes.length,
    edge_count: edges.length,
    nodes,
    edges,
    claim_boundary: "Repo Neural Activity graph is read-only filesystem evidence for visualization. It does not grant execution authority, mutation authority, safety proof, or autonomous operation."
  };

  try {
    fs.mkdirSync(path.dirname(neuralRepoGraphPath), { recursive: true });
    fs.writeFileSync(neuralRepoGraphPath, JSON.stringify(graph, null, 2), "utf8");
  } catch (_error) {}
  return graph;
}

function readPetriJsonIfPresent(relPath, fallback = null) {
  try {
    const target = path.join(petriDishProRoot, relPath);
    if (!fs.existsSync(target)) return fallback;
    return JSON.parse(fs.readFileSync(target, "utf8"));
  } catch (_error) {
    return fallback;
  }
}

function listPetriRuns() {
  const runsDir = path.join(petriDishProRoot, "artifacts", "bio", "runs");
  if (!fs.existsSync(runsDir)) return [];
  return fs.readdirSync(runsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => {
      const runId = entry.name;
      const runDir = path.join(runsDir, runId);
      const payload = readPetriJsonIfPresent(path.join("artifacts", "bio", "runs", runId, "run.json"), {}) || {};
      return {
        run_id: runId,
        preset: payload.preset || payload.experiment?.preset || "unknown",
        status: payload.validation?.status || payload.validation_status || "unknown",
        dominant: payload.dominant || payload.metrics?.dominant || payload.metrics?.dominant_name || "unknown",
        modified: fs.statSync(runDir).mtimeMs
      };
    })
    .sort((a, b) => b.modified - a.modified)
    .slice(0, 12);
}

function readPetriRunFile(index, key) {
  const fileName = index?.files?.[key];
  const runDir = index?.run_dir || path.join("artifacts", "bio", "runs", index?.run_id || "petri_preview");
  if (!fileName || !runDir) return null;
  const runDirCandidate = path.isAbsolute(runDir) ? runDir : path.join(petriDishProRoot, runDir);
  let resolvedRunDir = path.resolve(runDirCandidate);
  const resolvedRoot = path.resolve(petriDishProRoot);
  if (!resolvedRunDir.startsWith(resolvedRoot + path.sep)) {
    resolvedRunDir = path.join(resolvedRoot, "artifacts", "bio", "runs", index?.run_id || "petri_preview");
  }
  if (!resolvedRunDir.startsWith(resolvedRoot + path.sep)) return null;
  try {
    return JSON.parse(fs.readFileSync(path.join(resolvedRunDir, fileName), "utf8"));
  } catch (_error) {
    return null;
  }
}

function buildPetriPreviewState() {
  const index = readPetriJsonIfPresent("reports/bio/petri_particle_state_latest.json", {}) || {};
  const cellsPacket = readPetriRunFile(index, "cells") || {};
  const particlesPacket = readPetriRunFile(index, "particles") || {};
  const cells = Array.isArray(cellsPacket.cells) ? cellsPacket.cells : [];
  const particles = Array.isArray(particlesPacket.particles) ? particlesPacket.particles : [];
  return {
    system: "NEXUS GATE",
    surface: "petridishpro_mini_preview",
    source_root: petriDishProRoot,
    exists: fs.existsSync(petriDishProRoot),
    run_id: index.run_id || "unknown",
    generated_utc: index.generated_utc || null,
    counts: index.counts || {
      cells: cells.length,
      particles: particles.length,
      interactions: 0
    },
    cells: cells.slice(0, 160).map((cell) => ({
      id: cell.id,
      organism_id: cell.organism_id,
      label: cell.label,
      morphology: cell.morphology,
      behavior: cell.behavior || {},
      color: cell.color,
      x: Number(cell.x || 0),
      y: Number(cell.y || 0),
      vx: Number(cell.vx || 0),
      vy: Number(cell.vy || 0),
      angle: Number(cell.angle || 0),
      phase: Number(cell.phase || 0),
      radius: Number(cell.radius || cell.size || 0.012)
    })),
    particles: particles.slice(0, 180).map((particle) => ({
      id: particle.id,
      type: particle.type,
      x: Number(particle.x || 0),
      y: Number(particle.y || 0),
      vx: Number(particle.vx || 0),
      vy: Number(particle.vy || 0),
      z: Number(particle.z || 0)
    })),
    claim_boundary: index.claim_boundary || "PetriDishPro preview is deterministic simulation evidence only; it is not microscopy, clinical, species-identification, treatment, or biosafety evidence.",
    boundary: "Read-only PetriDishPro preview packet. NEXUS mini UI may reflect it; it may not self-authorize wet-lab, medical, or arbitrary shell actions."
  };
}

function registerPetriIpc() {
  if (petriIpcRegistered) return;
  petriIpcRegistered = true;
  ipcMain.handle("petri:readConfig", async () => readPetriJsonIfPresent("config/petri_science_config.v0.4c.json", {}));
  ipcMain.handle("petri:readOrganisms", async () => readPetriJsonIfPresent("config/organisms.json", {}));
  ipcMain.handle("petri:readFieldProfiles", async () => readPetriJsonIfPresent("config/field_profiles.json", {}));
  ipcMain.handle("petri:readLatest", async () => readPetriJsonIfPresent("reports/bio/petri_run_latest.json", {}));
  ipcMain.handle("petri:listRuns", async () => listPetriRuns());
  ipcMain.handle("petri:openArtifacts", async () => {
    const target = path.join(petriDishProRoot, "artifacts", "bio", "runs");
    fs.mkdirSync(target, { recursive: true });
    await shell.openPath(target);
    return { opened: target };
  });
  ipcMain.handle("petri:readPresetCards", async () => readPetriJsonIfPresent("config/preset_cards.json", {}));
  ipcMain.handle("petri:readMetricCards", async () => readPetriJsonIfPresent("config/metric_cards.json", {}));
  ipcMain.handle("petri:readParticleState", async () => {
    const index = readPetriJsonIfPresent("reports/bio/petri_particle_state_latest.json", {}) || {};
    const readMaybe = (value) => {
      if (!value) return null;
      const full = path.isAbsolute(value) ? value : path.join(petriDishProRoot, value);
      try {
        return JSON.parse(fs.readFileSync(full, "utf8"));
      } catch (_error) {
        return null;
      }
    };
    return {
      index,
      cells: readMaybe(index.cells_path || index.cells || index.cell_path),
      particles: readMaybe(index.particles_path || index.particles || index.particle_path),
      interactions: readMaybe(index.interactions_path || index.interactions),
      fields: readMaybe(index.fields_path || index.fields)
    };
  });
  ipcMain.handle("petri:run", async (_event, args = {}) => {
    const preset = String(args.preset || "microbial_competition").replace(/[^a-z0-9_\-]/gi, "");
    const steps = Math.max(1, Math.min(600, Number(args.steps || 120)));
    const grid = Math.max(16, Math.min(160, Number(args.grid || 64)));
    const pyArgs = ["-m", "petri_lab.cli", "--root", ".", "--preset", preset, "--steps", String(steps), "--grid", String(grid), "--json"];
    return new Promise((resolve) => {
      const child = spawn("python", pyArgs, {
        cwd: petriDishProRoot,
        shell: false,
        windowsHide: true,
        env: { ...process.env, PYTHONUTF8: "1" }
      });
      let stdout = "";
      let stderr = "";
      child.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
      child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
      child.on("close", (code) => {
        let parsed = null;
        try {
          parsed = JSON.parse(stdout.trim().split(/\r?\n/).filter(Boolean).pop() || "{}");
        } catch (_error) {}
        resolve({
          code,
          stdout,
          stderr,
          result: parsed,
          latest: readPetriJsonIfPresent("reports/bio/petri_run_latest.json", {}),
          boundary: "PetriDishPro runs inside its own bounded science workbench surface; NEXUS does not grant arbitrary shell authority."
        });
      });
    });
  });
}

function openPetriDishProWindow() {
  if (!fs.existsSync(path.join(petriElectronRoot, "renderer", "index.html"))) {
    return { ok: false, status: "missing", path: petriDishProRoot };
  }
  registerPetriIpc();
  if (petriWindow && !petriWindow.isDestroyed()) {
    petriWindow.show();
    petriWindow.maximize();
    petriWindow.focus();
    return { ok: true, status: "focused", path: petriDishProRoot };
  }
  petriWindow = new BrowserWindow({
    width: 1800,
    height: 1000,
    minWidth: 1220,
    minHeight: 760,
    title: "PetriDishPro",
    backgroundColor: "#02070b",
    webPreferences: {
      preload: path.join(petriElectronRoot, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });
  petriWindow.on("closed", () => { petriWindow = null; });
  petriWindow.loadFile(path.join(petriElectronRoot, "renderer", "index.html"));
  petriWindow.once("ready-to-show", () => {
    if (petriWindow && !petriWindow.isDestroyed()) petriWindow.maximize();
  });
  petriWindow.maximize();
  return {
    ok: true,
    status: "opened",
    path: petriDishProRoot,
    boundary: "Fixed PetriDishPro window launcher only; no NEXUS lane authority is delegated."
  };
}

function runNexPython(args) {
  return new Promise((resolve) => {
    const child = spawn("python", args, {
      cwd: repoRoot,
      shell: false,
      windowsHide: true,
      env: {
        ...process.env,
        CUDA_VISIBLE_DEVICES: process.env.CUDA_VISIBLE_DEVICES || "-1",
        NEXUS_OLLAMA_NUM_GPU: process.env.NEXUS_OLLAMA_NUM_GPU || "0",
        OLLAMA_MODELS: process.env.OLLAMA_MODELS || resolveOllamaModels()
      }
    });

    activeNexChild = child;
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
    child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
    child.on("error", (error) => {
      if (activeNexChild === child) activeNexChild = null;
      resolve({ code: -1, stdout, stderr: stderr + error.message });
    });
    child.on("close", (code) => {
      if (activeNexChild === child) activeNexChild = null;
      resolve({ code, stdout, stderr });
    });
  });
}
const ALLOWLISTED_COMMANDS = new Set([
  "evolve",
  "interface",
  "feedback",
  "heal",
  "status",
  "compact",
  "interconnect",
  "runtime",
  "pack"
]);

function resolveRepoPath(relativePath) {
  const normalized = relativePath.replace(/\\/g, "/");
  if (!READ_SURFACES.has(normalized)) {
    throw new Error(`Surface is not allowlisted: ${relativePath}`);
  }

  const resolved = path.resolve(repoRoot, normalized);
  if (!resolved.startsWith(repoRoot + path.sep)) {
    throw new Error("Resolved path escaped repository root.");
  }
  return resolved;
}

function writeSmokeReport(status, extra = {}) {
  if (smokeReportWritten) return;
  smokeReportWritten = true;
  fs.mkdirSync(path.dirname(smokeReportPath), { recursive: true });
  fs.writeFileSync(smokeReportPath, JSON.stringify({
    system: "NEXUS GATE",
    version: "0.3.6-electron-hud-smoke",
    status,
    generated_at_utc: new Date().toISOString(),
    app_title: "NEXUS GATE",
    smoke_mode: true,
    read_surfaces: Array.from(READ_SURFACES),
    allowlisted_commands: Array.from(ALLOWLISTED_COMMANDS),
    blocked_actions: [
      "arbitrary_shell_commands",
      "external_api_write",
      "secret_access",
      "self_authorize",
      "memory_promotion_without_evidence",
      "ungated_repo_mutation",
      "mutate_graph_state",
      "bypass_evolve"
    ],
    claim_boundary: "Electron HUD smoke is local runtime evidence only. It does not package an EXE, prove production readiness, grant shell authority, or authorize autonomous action.",
    ...extra
  }, null, 2), "utf8");
}

async function waitForRendererReady(win) {
  const started = Date.now();
  while (Date.now() - started < 8000) {
    const state = await win.webContents.executeJavaScript("document.body.dataset.ready || ''");
    if (state === "true" || state === "false") {
      return state === "true";
    }
    await new Promise((resolve) => setTimeout(resolve, 150));
  }
  return false;
}

function createWindow() {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.focus();
    return mainWindow;
  }
  const win = new BrowserWindow({
    icon: appIconPath,
    width: 1280,
    height: 720,
    minWidth: 960,
    minHeight: 640,
    show: !isSmoke,
    title: "NEXUS GATE",
    backgroundColor: "#020617",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  if (isSmoke) {
    setTimeout(() => {
      if (!smokeReportWritten) {
        writeSmokeReport("fail", { error: "renderer smoke timed out", code: "timeout" });
        app.quit();
      }
    }, 10000);
    win.webContents.once("did-finish-load", async () => {
      try {
        const title = await win.webContents.executeJavaScript("document.title");
        const ready = await waitForRendererReady(win);
        writeSmokeReport(ready ? "pass" : "fail", { renderer_title: title, renderer_ready: ready });
      } catch (error) {
        writeSmokeReport("fail", { error: error.message });
      } finally {
        app.quit();
      }
    });
    win.webContents.once("did-fail-load", (_event, code, description) => {
      if (code === -3) return;
      writeSmokeReport("fail", { error: description, code });
      app.quit();
    });
  }

  mainWindow = win;
  win.on("closed", () => { mainWindow = null; });
  win.loadFile(path.join(__dirname, "renderer", "index.html"));
  return win;
}

ipcMain.handle("nexus:readSurface", async (_event, relativePath) => {
  const target = resolveRepoPath(relativePath);
  return fs.promises.readFile(target, "utf8");
});

ipcMain.handle("nexus:surfaceExists", async (_event, relativePath) => {
  const target = resolveRepoPath(relativePath);
  return fs.existsSync(target);
});

ipcMain.handle("nexus:runLane", async (_event, lane) => {
  if (!ALLOWLISTED_COMMANDS.has(lane)) {
    throw new Error(`NEXUS lane is not allowlisted: ${lane}`);
  }

  const script = path.join(repoRoot, "scripts", "nexus.ps1");
  const args = [
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    script,
    lane
  ];

  return new Promise((resolve) => {
    const child = spawn("powershell.exe", args, {
      cwd: repoRoot,
      shell: false,
      windowsHide: true,
      env: { ...process.env, CUDA_VISIBLE_DEVICES: process.env.CUDA_VISIBLE_DEVICES || "-1", NEXUS_OLLAMA_NUM_GPU: process.env.NEXUS_OLLAMA_NUM_GPU || "0" }
    });

    activeNexChild = child;
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("close", (code) => {
      resolve({ code, stdout, stderr });
    });
  });
});

ipcMain.handle("nexus:runHandoffScript", async (_event, packet = {}) => {
  if (!packet || packet.authorized !== true) {
    return {
      code: 90,
      status: "blocked",
      stdout: "",
      stderr: "HANDOFF action requires explicit human /handoff run authorization.",
      boundary: "No model output may execute as shell authority."
    };
  }
  return runHandoffPowerShell(packet.scriptText, packet);
});
ipcMain.handle("nexus:askNex", async (_event, packet = {}) => {
  const prompt = sanitizeNexPrompt(packet.prompt);
  const role = normalizeNexRole(packet.role);
  const callModel = Boolean(packet.callModel) && role !== "HANDOFF";

  const args = [
    "-m",
    "nexus_gate.nn_router.compile",
    "--root",
    ".",
    "--intent",
    prompt,
    "--role",
    role,
    "--json"
  ];

  if (callModel) {
    args.push("--call-model");
  }

  const result = await runNexPython(args);
  const reportPath = path.join(repoRoot, "reports", "nexus_nn_router_report_latest.json");
  const report = readJsonIfPresent(reportPath);

  return {
    code: result.code,
    stdout: result.stdout,
    stderr: result.stderr,
    role,
    callModel,
    report,
    boundary: "NEX chat is recommendation-only. It does not execute model output, mutate repo files from model output, or grant authority."
  };
});
ipcMain.handle("nexus:stopNex", async () => {
  if (!activeNexChild) {
    return { stopped: false, status: "idle" };
  }
  const pid = activeNexChild.pid;
  try {
    activeNexChild.kill();
    activeNexChild = null;
    return { stopped: true, pid, boundary: "Stopped active NEX model transmission only. No repo mutation or shell authority granted." };
  } catch (error) {
    return { stopped: false, pid, error: error.message };
  }
});

ipcMain.handle("nexus:openPetriDishPro", async () => openPetriDishProWindow());
ipcMain.handle("nexus:getPetriDishProState", async () => buildPetriPreviewState());
ipcMain.handle("nexus:getNeuralRepoGraph", async () => buildNeuralRepoGraph());

ipcMain.handle("nexus:getTelemetry", async () => {
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const cpuPercent = readCpuPercent();
  const windowsTelemetry = await readWindowsTelemetry();
  return {
    system: "NEXUS GATE",
    version: "0.6.6-local-telemetry-hud",
    generated_at_utc: new Date().toISOString(),
    cpu: {
      cores: os.cpus().length,
      model: os.cpus()[0]?.model || "unknown",
      load_percent: Number(cpuPercent.toFixed(1))
    },
    memory: {
      total_bytes: totalMem,
      free_bytes: freeMem,
      used_percent: Number((((totalMem - freeMem) / totalMem) * 100).toFixed(1))
    },
    platform: {
      type: os.type(),
      release: os.release(),
      uptime_seconds: Math.round(os.uptime())
    },
    windows: windowsTelemetry,
    boundary: "Read-only local telemetry. NEX may observe CPU/RAM/GPU/process pressure but may not self-authorize repair or mutation."
  };
});
ipcMain.handle("nexus:ensureOllama", async () => ensureOllamaBackend());
ipcMain.handle("nexus:getContract", async () => ({
  readSurfaces: Array.from(READ_SURFACES),
  allowlistedCommands: Array.from(ALLOWLISTED_COMMANDS),
  boundary: "Electron shell is presentation only and does not own NEXUS authority."
}));

app.whenReady().then(async () => {
  if (!gotSingleInstanceLock) return;
  await ensureOllamaBackend();
  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
