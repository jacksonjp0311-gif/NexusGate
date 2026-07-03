const { app, BrowserWindow, ipcMain } = require("electron");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const repoRoot = path.resolve(__dirname, "..");
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
  "reports/tui/nexus_tui_ai_handoff_latest.txt",
  "reports/tui/nexus_tui_snapshot_latest.html",
  "reports/tui/nexus_tui_surface_latest.json"
]);

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
