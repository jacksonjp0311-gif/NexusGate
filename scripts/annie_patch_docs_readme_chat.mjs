import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const target = path.join(repoRoot, "docs", "README.md");

const original = fs.readFileSync(target, "utf8");

const already = "| Chat interface governance | `chat/` |";
if (original.includes(already)) {
  console.log("[OK] docs/README.md already references docs/chat. Skipping.");
  process.exit(0);
}

const lines = original.split(/\r?\n/);

let changed = false;
const out = [];

for (const line of lines) {
  if (line.trim() === "| UI / Electron / Portal | `ui/` |") {
    out.push(already);
    out.push(line);
    changed = true;
  } else {
    out.push(line);
  }
}

if (!changed) {
  console.error("[FAIL] Could not find docs/README.md Start Points row for UI / Electron / Portal.");
  process.exit(2);
}

const patched = out.join("\r\n");
fs.writeFileSync(target, patched, "utf8");
console.log("[OK] Inserted docs/chat into docs/README.md Start Points table.");
console.log("bytes:", original.length, "->", patched.length);
