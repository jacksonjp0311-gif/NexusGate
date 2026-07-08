import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const targetPath = path.join(repoRoot, "electron", "renderer", "renderer.js");

const original = fs.readFileSync(targetPath, "utf8");
let patched = original;

// 1) Add a persistent ollama status flag near the top-level runtime flags.
if (!patched.includes("let nexBusy")) {
  console.error("[FAIL] Unexpected renderer.js shape (missing nexBusy). Aborting.");
  process.exit(2);
}
if (patched.includes("let ollamaReady")) {
  console.log("[OK] renderer.js already has ollamaReady (offline mode already patched). Skipping.");
  process.exit(0);
}

patched = patched.replace(
  "let allowlistedCommands = [];\r\nlet nexBusy = false;",
  "let allowlistedCommands = [];\r\nlet nexBusy = false;\r\nlet ollamaReady = null; // null=unknown, true=ready, false=offline"
);

// 2) Ensure ensureLocalOllamaBackend stores readiness.
if (!patched.includes("async function ensureLocalOllamaBackend()")) {
  console.error("[FAIL] Missing ensureLocalOllamaBackend in renderer.js");
  process.exit(2);
}

const okNeedle = "    setTelemetryText(\"telemetry-status\", result.ok ? \"backend online\" : \"backend blocked\");\r\n    return result;";
if (!patched.includes(okNeedle)) {
  console.error("[FAIL] Could not find expected telemetry return line (ok path) to patch.");
  process.exit(2);
}
patched = patched.replace(
  okNeedle,
  "    setTelemetryText(\"telemetry-status\", result.ok ? \"backend online\" : \"backend blocked\");\r\n    ollamaReady = Boolean(result.ok);\r\n    return result;"
);

const errNeedle = "    setTelemetryText(\"telemetry-status\", \"backend blocked\");\r\n    return { ok: false, error: error.message };";
if (!patched.includes(errNeedle)) {
  console.error("[FAIL] Could not find expected telemetry return line (error path) to patch.");
  process.exit(2);
}
patched = patched.replace(
  errNeedle,
  "    setTelemetryText(\"telemetry-status\", \"backend blocked\");\r\n    ollamaReady = false;\r\n    return { ok: false, error: error.message };"
);

// 3) Force offline graceful degradation: if Ollama is blocked, do not call the model.
const askNexNeedle = "      callModel: role !== \"HANDOFF\"";
if (!patched.includes(askNexNeedle)) {
  console.error("[FAIL] Could not find askNex callModel field to patch.");
  process.exit(2);
}

const sendStartNeedle = "  try {\r\n    setBuffer(42, \"routing\");\r\n    if (!window.nexus.askNex) {";
if (!patched.includes(sendStartNeedle)) {
  console.error("[FAIL] Could not find sendNexMessage try block to patch.");
  process.exit(2);
}

patched = patched.replace(
  sendStartNeedle,
  "  try {\r\n    setBuffer(42, \"routing\");\r\n    // Offline graceful degradation: if the local model endpoint is blocked, keep chat responsive\r\n    // and route without calling a model (evidence-forward, recommendation-only).\r\n    const ollama = await ensureLocalOllamaBackend();\r\n    const canCallModel = (role !== \"HANDOFF\") && (ollama?.ok !== false);\r\n    if (!canCallModel && role !== \"HANDOFF\") {\r\n      pushConsole(\"WARN\", \"Local model endpoint is blocked; routing without --call-model.\");\r\n    }\r\n    if (!window.nexus.askNex) {"
);

patched = patched.replace(
  askNexNeedle,
  "      callModel: canCallModel"
);

if (patched === original) {
  console.error("[FAIL] Patch resulted in no changes.");
  process.exit(2);
}

fs.writeFileSync(targetPath, patched, "utf8");
console.log("[OK] Patched renderer.js for offline graceful degradation.");
console.log("bytes:", original.length, "->", patched.length);
