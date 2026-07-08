import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const readmePath = path.join(repoRoot, "README.md");
const original = fs.readFileSync(readmePath, "utf8");

const canonical = [
  "Runtime lineage seals:",
  "",
  "- v0.8.1 UI cleanup line",
  "- v0.8.3F geo preflight cleanup and warning seal line",
  "- v0.9.0 Meta Loop Registry",
  "- v0.9.1 origin-aligned GITNEXUS impact bridge",
  "- python -m nexus_gate.geometric_memory.router",
  "- geo-clean",
  "- docs/runtime/NEXUS_NEURAL_ACTIVITY.md",
  "- docs/runtime/NEXUS_SPIRAL_CORE_PORTAL.md",
  "- Failure Intelligence Distributor",
  "",
].join("\r\n");

// Replace the entire lineage block up to the next fenced code block.
// This makes the patch idempotent and cleans duplicates.
const re = /Runtime lineage seals:[\s\S]*?(?=```text)/m;

if (!re.test(original)) {
  console.error("[FAIL] Could not locate Runtime lineage seals block (expected to appear before the first ```text block). ");
  process.exit(2);
}

const patched = original.replace(re, canonical);
fs.writeFileSync(readmePath, patched, "utf8");

console.log("[OK] Normalized README Runtime lineage seals block (idempotent)." );
console.log("bytes:", original.length, "->", patched.length);
