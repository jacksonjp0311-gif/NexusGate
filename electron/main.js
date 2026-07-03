const { app, BrowserWindow, ipcMain } = require("electron");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const repoRoot = path.resolve(__dirname, "..");

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

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 780,
    minWidth: 960,
    minHeight: 640,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  win.loadFile(path.join(__dirname, "renderer", "index.html"));
}

ipcMain.handle("nexus:readSurface", async (_event, relativePath) => {
  const target = resolveRepoPath(relativePath);
  return fs.promises.readFile(target, "utf8");
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
