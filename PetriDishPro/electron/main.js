const { app, BrowserWindow, ipcMain, shell } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const repoRoot = path.resolve(__dirname, "..");
function safeJsonRead(relPath, fallback = null) { try { return JSON.parse(fs.readFileSync(path.join(repoRoot, relPath), "utf8")); } catch (err) { return fallback; } }
function listRuns() {
  const runsDir = path.join(repoRoot, "artifacts", "bio", "runs");
  if (!fs.existsSync(runsDir)) return [];
  return fs.readdirSync(runsDir, { withFileTypes: true }).filter(d => d.isDirectory()).map(d => {
    const runId = d.name; const receipt = path.join(runsDir, runId, "run.json"); let payload = {};
    if (fs.existsSync(receipt)) { try { payload = JSON.parse(fs.readFileSync(receipt, "utf8")); } catch {} }
    return { run_id: runId, preset: payload.preset || payload.experiment?.preset || "unknown", status: payload.validation?.status || payload.validation_status || "unknown", dominant: payload.dominant || payload.metrics?.dominant || payload.metrics?.dominant_name || "unknown", modified: fs.statSync(path.join(runsDir, runId)).mtimeMs };
  }).sort((a, b) => b.modified - a.modified).slice(0, 12);
}
function createWindow() {
  const win = new BrowserWindow({ width: 1680, height: 940, minWidth: 1220, minHeight: 760, backgroundColor: "#02070b", webPreferences: { preload: path.join(__dirname, "preload.js"), contextIsolation: true, nodeIntegration: false, sandbox: false } });
  win.loadFile(path.join(__dirname, "renderer", "index.html"));
  if (process.argv.includes("--smoke")) win.webContents.once("did-finish-load", () => setTimeout(() => app.quit(), 1000));
}
app.whenReady().then(createWindow);
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
ipcMain.handle("petri:readConfig", async () => safeJsonRead("config/petri_science_config.v0.4c.json", {}));
ipcMain.handle("petri:readOrganisms", async () => safeJsonRead("config/organisms.json", {}));
ipcMain.handle("petri:readFieldProfiles", async () => safeJsonRead("config/field_profiles.json", {}));
ipcMain.handle("petri:readLatest", async () => safeJsonRead("reports/bio/petri_run_latest.json", {}));
ipcMain.handle("petri:listRuns", async () => listRuns());
ipcMain.handle("petri:openArtifacts", async () => { const p = path.join(repoRoot, "artifacts", "bio", "runs"); fs.mkdirSync(p, { recursive: true }); await shell.openPath(p); return { opened: p }; });
ipcMain.handle("petri:run", async (_event, args) => {
  const preset = String(args?.preset || "microbial_competition").replace(/[^a-z0-9_\-]/gi, "");
  const steps = Math.max(1, Math.min(600, Number(args?.steps || 120)));
  const grid = Math.max(16, Math.min(160, Number(args?.grid || 64)));
  const pyArgs = ["-m", "petri_lab.cli", "--root", ".", "--preset", preset, "--steps", String(steps), "--grid", String(grid), "--json"];
  return await new Promise((resolve) => {
    const child = spawn("python", pyArgs, { cwd: repoRoot, shell: false, windowsHide: true, env: { ...process.env, PYTHONUTF8: "1" } });
    let stdout = ""; let stderr = "";
    child.stdout.on("data", d => stdout += d.toString()); child.stderr.on("data", d => stderr += d.toString());
    child.on("close", code => { let parsed = null; try { parsed = JSON.parse(stdout.trim().split(/\r?\n/).filter(Boolean).pop() || "{}"); } catch {} resolve({ code, stdout, stderr, result: parsed, latest: safeJsonRead("reports/bio/petri_run_latest.json", {}) }); });
  });
});

ipcMain.handle("petri:readParticleState", async () => {
  const index = safeJsonRead("reports/bio/petri_particle_state_latest.json", {});
  function readMaybe(p) {
    if (!p) return null;
    try {
      const full = path.isAbsolute(p) ? p : path.join(repoRoot, p);
      return JSON.parse(fs.readFileSync(full, "utf8"));
    } catch (err) {
      return null;
    }
  }
  const cells = readMaybe(index.cells_path || index.cells || index.cell_path);
  const particles = readMaybe(index.particles_path || index.particles || index.particle_path);
  const interactions = readMaybe(index.interactions_path || index.interactions);
  const fields = readMaybe(index.fields_path || index.fields);
  return { index, cells, particles, interactions, fields };
});

ipcMain.handle("petri:readPresetCards", async () => safeJsonRead("config/preset_cards.json", {}));
ipcMain.handle("petri:readMetricCards", async () => safeJsonRead("config/metric_cards.json", {}));
