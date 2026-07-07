from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def clip(text: str, max_len: int = 280) -> str:
    value = re.sub(r"\s+", " ", str(text)).strip()
    if len(value) > max_len:
        return value[:max_len] + "..."
    return value


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"_load_error": str(exc), "_path": str(path)}


def compile_from_log(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "wound_id": "NO_LOG_FOUND",
            "stage": "unknown",
            "log_path": str(path),
            "failed_count": 0,
            "failures": [],
            "stability_lock": "BLOCKED_UNTIL_LOG_CAPTURED",
        }

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    starts = [i for i, line in enumerate(lines) if re.match(r"^\s*(FAIL|ERROR):\s+", line)]
    failures: list[dict[str, Any]] = []

    for idx, start in enumerate(starts):
        end = starts[idx + 1] - 1 if idx + 1 < len(starts) else len(lines) - 1
        block = lines[start:end + 1]
        header = lines[start]
        kind = "UNKNOWN"
        test = ""
        source = ""
        match = re.match(r"^\s*(FAIL|ERROR):\s+([^\s]+)\s+\(([^)]+)\)", header)
        if match:
            kind, test, source = match.group(1), match.group(2), match.group(3)

        missing_marker = ""
        line_limit = ""
        traceback_heads: list[str] = []
        assertion_summary: list[str] = []

        for raw in block:
            if raw.lstrip().startswith("File "):
                traceback_heads.append(clip(raw, 240))
            if re.search(r"AssertionError|SyntaxError|ParserError|ModuleNotFoundError|ImportError|RuntimeError|Exception", raw):
                assertion_summary.append(clip(raw, 320))
            marker_match = re.search(r"AssertionError:\s+'([^']+)'\s+not found in", raw)
            if marker_match and not missing_marker:
                missing_marker = marker_match.group(1)
            limit_match = re.search(r"AssertionError:\s+(\d+)\s+not less than\s+(\d+)", raw)
            if limit_match and not line_limit:
                line_limit = f"actual={limit_match.group(1)}; max={limit_match.group(2)}"

        suggested_fix = "Inspect compact traceback heads and patch the smallest target surface."
        if missing_marker:
            suggested_fix = f"Add exact marker '{missing_marker}' to the tested document without breaking compactness."
        if line_limit:
            suggested_fix = f"Compact README/docs until line-count invariant passes: {line_limit}."

        failures.append({
            "kind": kind,
            "test": test,
            "source": source,
            "missing_marker": missing_marker,
            "line_limit": line_limit,
            "traceback_heads": traceback_heads[:6],
            "assertion_summary": assertion_summary[:6],
            "suggested_fix": suggested_fix,
        })

    wound_id = "UNKNOWN_FULL_TESTS_WOUND"
    for failure in failures:
        if failure.get("missing_marker"):
            safe = re.sub(r"[^A-Za-z0-9]+", "_", failure["missing_marker"]).strip("_").upper()
            wound_id = f"README_MARKER_WOUND_{safe}"
            break
    if wound_id == "UNKNOWN_FULL_TESTS_WOUND" and failures:
        wound_id = "FULL_TESTS_COMPACT_FAILURE_WOUND"

    return {
        "wound_id": wound_id,
        "stage": "full-tests",
        "log_path": str(path),
        "log_line_count": len(lines),
        "failed_count": len(failures),
        "failures": failures,
        "stability_lock": "BLOCKED_UNTIL_TARGETED_CLOSE_SCRIPT_PASSES_FULL_TESTS",
    }


def find_latest_log() -> Path | None:
    temp = Path(os.environ.get("TEMP", "."))
    candidates = list(temp.glob("nexus_loop_failure_compiler_full-tests.log"))
    candidates += list(temp.glob("*full-tests*.log"))
    candidates = [path for path in candidates if path.exists()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def build_packet(root: Path, log_path: Path | None = None) -> dict[str, Any]:
    latest_json = root / "reports" / "nexus_compiled_failure_latest.json"
    latest_md = root / "reports" / "nexus_compiled_failure_latest.md"

    base = load_json(latest_json)
    if not base or base.get("_load_error"):
        if log_path is None:
            log_path = find_latest_log()
        if log_path is not None:
            base = compile_from_log(log_path)
        else:
            base = {
                "wound_id": "NO_FAILURE_EVIDENCE_FOUND",
                "stage": "unknown",
                "failed_count": 0,
                "failures": [],
                "stability_lock": "BLOCKED_UNTIL_FAILURE_EVIDENCE_EXISTS",
            }

    failures = base.get("failures", [])
    next_close = base.get("next_close_target", "")
    if not next_close and failures:
        next_close = failures[0].get("suggested_fix", "")

    return {
        "version": "0.1.3",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "wound_id": base.get("wound_id", "UNKNOWN_WOUND"),
        "stage": base.get("stage", "unknown"),
        "failed_count": base.get("failed_count", len(failures)),
        "failures": failures,
        "log_path": base.get("log_path", ""),
        "report_markdown": str(latest_md),
        "report_json": str(latest_json),
        "next_close_target": next_close,
        "verifier": [
            "python -m compileall nexus_gate tests",
            "python -m unittest discover -s tests -p test_nexus_cell_*.py",
            "python -m unittest discover -s tests",
            "python -m nexus_gate.compiler --root . --json",
            "git status --short",
        ],
        "stability_lock": base.get("stability_lock", "BLOCKED_UNTIL_TARGETED_CLOSE_SCRIPT_PASSES"),
        "claim_boundary": "Failure intelligence is rehydration evidence only. It is not autonomous authority or proof of correctness.",
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Nexus Failure Intelligence Latest",
        "",
        f"- wound_id: {packet['wound_id']}",
        f"- stage: {packet['stage']}",
        f"- failed_count: {packet['failed_count']}",
        f"- stability_lock: {packet['stability_lock']}",
        f"- next_close_target: {packet.get('next_close_target', '')}",
        "",
        "## Failures",
    ]
    for failure in packet.get("failures", []):
        lines += [
            "",
            f"### {failure.get('kind', 'FAIL')}: {failure.get('test', '')}",
            f"- source: {failure.get('source', '')}",
        ]
        if failure.get("missing_marker"):
            lines.append(f"- missing_marker: {failure['missing_marker']}")
        if failure.get("line_limit"):
            lines.append(f"- line_limit: {failure['line_limit']}")
        lines.append(f"- suggested_fix: {failure.get('suggested_fix', '')}")

    lines += ["", "## Verifier"]
    lines += [f"- {cmd}" for cmd in packet.get("verifier", [])]
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--log-path", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    state_dir = root / "state" / "failure_intelligence"
    reports_dir = root / "reports"
    state_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    log_path = Path(args.log_path) if args.log_path else None
    packet = build_packet(root, log_path)

    latest_state = state_dir / "nexus_failure_intelligence_latest.json"
    latest_md = reports_dir / "nexus_failure_intelligence_latest.md"
    latest_state.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(packet, latest_md)

    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print("Nexus failure intelligence distributed")
        print(f"wound_id: {packet['wound_id']}")
        print(f"failed_count: {packet['failed_count']}")
        print(f"state: {latest_state}")
        print(f"markdown: {latest_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
