const { app, BrowserWindow, ipcMain } = require("electron");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const repoRoot = path.resolve(__dirname, "..");
const appIconPath = path.join(repoRoot, 'electron', 'assets', 'icons', 'nexus_gate.ico');
const isSmoke = process.argv.includes("--smoke");
const smokeReportPath = path.join(repoRoot, "reports", "nexus_electron_smoke_report_latest.json");

if (isSmoke) {
  app.disableHardwareAcceleration();
}

const READ_SURFACES = new Set([
  "state/ai_feedback_context_latest.json",
  "docs/feedback/FEEDBACK_LOG.md",
  "reports/nexus_feedback_interface_report_latest.json",
  "reports/nexus_self_healing_report_latest.json",
  "reports/nexus_reflective_loop_report_latest.json",
  "reports/nexus_domain_intelligence_report_latest.json",
  "state/nexus_lineage_manifest_latest.json",
  "state/interface_adapter_contract_index.v0.3.7.json",
  "state/domain_intelligence_index.v0.4.0.json",
  "state/repo_native_learning_index.v0.4.0.json",
  "state/codex_orchestration_index.v0.4.0.json",
  "reports/tui/nexus_tui_ai_handoff_latest.txt",
  "reports/tui/nexus_tui_snapshot_latest.html",
  "reports/tui/nexus_tui_surface_latest.json"
]);

const NEX_CHAT_ROLES = new Set(["FAST", "BALANCED", "DEEP", "HANDOFF"]);
const NEX_MAX_PROMPT_CHARS = 4000;

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

function runNexPython(args) {
  return new Promise((resolve) => {
    const child = spawn("python", args, {
      cwd: repoRoot,
      shell: false,
      windowsHide: true
    });

    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
    child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
    child.on("error", (error) => {
      resolve({ code: -1, stdout, stderr: stderr + error.message });
    });
    child.on("close", (code) => {
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
      writeSmokeReport("fail", { error: description, code });
      app.quit();
    });
  }

  win.loadFile(path.join(__dirname, "renderer", "index.html"));
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
      windowsHide: true
    });

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
ipcMain.handle("nexus:getContract", async () => ({
  readSurfaces: Array.from(READ_SURFACES),
  allowlistedCommands: Array.from(ALLOWLISTED_COMMANDS),
  boundary: "Electron shell is presentation only and does not own NEXUS authority."
}));

app.whenReady().then(createWindow);

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

