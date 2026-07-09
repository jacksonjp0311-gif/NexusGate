from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MAX_SNIPPET = 900

def read(path: str | None) -> str:
    if not path:
        return ""
    p = Path(path)
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def last_nonempty_lines(text: str, limit: int = 14) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    return lines[-limit:]

def clip(text: str, limit: int = MAX_SNIPPET) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[clipped {len(text) - limit} chars; raw log saved]"

def parse_counts(text: str) -> dict:
    counts = {}
    ran = re.findall(r"Ran\s+(\d+)\s+tests?", text)
    if ran:
        counts["tests"] = int(ran[-1])
    failed = re.findall(r"FAILED\s+\(([^)]+)\)", text)
    if failed:
        counts["status"] = "failed"
        for part in failed[-1].split(","):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                try:
                    counts[k.strip()] = int(v.strip())
                except ValueError:
                    counts[k.strip()] = v.strip()
    elif re.search(r"\bOK\b", text):
        counts["status"] = "passed"
    else:
        counts["status"] = "unknown"
    return counts

def parse_failing_tests(text: str) -> list[dict]:
    out = []
    for kind, name, suite in re.findall(r"^(FAIL|ERROR):\s+(.+?)\s+\((.+?)\)\s*$", text, re.M):
        out.append({"kind": kind, "test": name, "suite": suite})
    return out

def parse_root_errors(text: str) -> list[str]:
    patterns = [
        r"AssertionError:[^\n]+(?:\n[-+? ][^\n]+){0,8}",
        r"KeyError:\s*[^\n]+",
        r"AttributeError:\s*[^\n]+",
        r"TypeError:\s*[^\n]+",
        r"NameError:\s*[^\n]+",
        r"RuntimeError:\s*[^\n]+",
        r"ImportError:\s*[^\n]+",
        r"ModuleNotFoundError:\s*[^\n]+",
    ]
    found = []
    for pattern in patterns:
        for m in re.finditer(pattern, text):
            item = m.group(0).strip()
            if item and item not in found:
                found.append(item)
    return found[:12]

def parse_gate_failures(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        if " FAIL:" in line and "GATE_" in line:
            lines.append(line.strip())
    return lines[-8:]

def parse_command_failures(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        if "failed with exit code" in line:
            out.append(line.strip())
    return out[-6:]

def infer_actions(root_errors: list[str], failing_tests: list[dict], text: str) -> list[str]:
    blob = "\n".join(root_errors) + "\n" + text[-3000:]
    actions = []
    if "KeyError: 'cards'" in blob:
        actions.append("Add or restore top-level `cards` in config/preset_cards.json.")
    if "KeyError: 'metrics'" in blob:
        actions.append("Add or restore top-level `metrics` in config/metric_cards.json.")
    if "ampicillin_like_proxy" in blob:
        actions.append("Patch the ampicillin_like_proxy card shape only; avoid rewriting the whole registry.")
    if "neutralizing_antibody_proxy" in blob:
        actions.append("Patch the neutralizing_antibody_proxy card shape only; preserve source-gated claim boundary.")
    if "total_cells" in blob or "shannon_diversity" in blob or "dominance_index" in blob:
        actions.append("Patch metric card nested chart markers only: sparkline/area/bar as required by tests.")
    if "PETRI_PRESET_CARD_REGISTRY" in blob or "PETRI_PRESET_CARDS" in blob:
        actions.append("Keep stable schema id `PETRI_PRESET_CARD_REGISTRY.v0.4o`; put newer version in `content_version`.")
    if "PETRI_METRIC_CARD_REGISTRY" in blob or "PETRI_METRIC_CARDS" in blob:
        actions.append("Keep stable schema id `PETRI_METRIC_CARD_REGISTRY.v0.4o`; put newer version in `content_version`.")
    if "AttributeError: type object 'datetime.datetime' has no attribute 'datetime'" in blob:
        actions.append("Replace dynamic datetime import with `import datetime as dt` and `dt.datetime.now(dt.timezone.utc)`.")
    if "assertIn" in blob and "dict" in blob:
        actions.append("A test dumped a full dict. Use the named failing test and root error to add the missing key/marker only.")
    if failing_tests:
        names = ", ".join(f"{t['kind']}:{t['test']}" for t in failing_tests[:4])
        actions.append(f"Patch only the contract exercised by: {names}.")
    if not actions:
        actions.append("Open raw stderr and inspect the first FAIL/ERROR block; do not patch unrelated surfaces.")
    return actions

def digest(stdout: str, stderr: str, raw_paths: dict | None = None) -> dict:
    text = (stdout or "") + "\n" + (stderr or "")
    failing_tests = parse_failing_tests(text)
    root_errors = parse_root_errors(text)
    return {
        "status": parse_counts(text),
        "gate_failures": parse_gate_failures(text),
        "command_failures": parse_command_failures(text),
        "failing_tests": failing_tests,
        "root_errors": root_errors,
        "actions": infer_actions(root_errors, failing_tests, text),
        "tail": last_nonempty_lines(text, 12),
        "raw_paths": raw_paths or {},
    }

def to_markdown(data: dict) -> str:
    status = data.get("status", {})
    lines = [
        "# Failure Digest",
        "",
        f"- status: **{status.get('status', 'unknown')}**",
        f"- tests: `{status.get('tests', 'unknown')}`",
        f"- failures: `{status.get('failures', 0)}`",
        f"- errors: `{status.get('errors', 0)}`",
        "",
    ]

    if data.get("gate_failures"):
        lines += ["## Failed Gate", ""]
        for item in data["gate_failures"]:
            lines.append(f"- `{item}`")
        lines.append("")

    if data.get("command_failures"):
        lines += ["## Failed Command", ""]
        for item in data["command_failures"]:
            lines.append(f"- `{item}`")
        lines.append("")

    if data.get("failing_tests"):
        lines += ["## Failing Tests", ""]
        for t in data["failing_tests"]:
            lines.append(f"- **{t['kind']}** `{t['test']}` in `{t['suite']}`")
        lines.append("")

    if data.get("root_errors"):
        lines += ["## Root Error Signals", ""]
        for item in data["root_errors"][:8]:
            lines.append("```text")
            lines.append(clip(item, 700))
            lines.append("```")
        lines.append("")

    if data.get("actions"):
        lines += ["## Next Actions", ""]
        for item in data["actions"]:
            lines.append(f"- {item}")
        lines.append("")

    if data.get("raw_paths"):
        lines += ["## Raw Logs", ""]
        for k, v in data["raw_paths"].items():
            lines.append(f"- {k}: `{v}`")
        lines.append("")

    lines += ["## Tail", "", "```text"]
    lines.extend(data.get("tail", []))
    lines.append("```")
    return "\n".join(lines).rstrip() + "\n"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout")
    ap.add_argument("--stderr")
    ap.add_argument("--out-json")
    ap.add_argument("--out-md")
    ap.add_argument("--print", action="store_true")
    args = ap.parse_args()

    stdout = read(args.stdout)
    stderr = read(args.stderr)
    raw_paths = {"stdout": args.stdout or "", "stderr": args.stderr or ""}
    data = digest(stdout, stderr, raw_paths)
    md = to_markdown(data)

    if args.out_json:
        Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_json).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_md).write_text(md, encoding="utf-8")
    if args.print:
        print(md)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
