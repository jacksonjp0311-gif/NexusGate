from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "2.3.0"
SCHEMA = "NEXUS_RUNTIME_CHURN_HYGIENE.v2.3.0"
REPORT_LATEST = Path("reports") / "nexus_runtime_hygiene_latest.json"

TRACKED_GENERATED_PATTERNS = [
    "NexusCell/ledger/nexus_cell_continuity.jsonl",
    "Tesseract Neural Network/memory/conversation_latest.json",
    "Tesseract Neural Network/memory/tnn_memory.jsonl",
    "Tesseract Neural Network/state/tnn_state_latest.json",
    "dist/nexus_gate_pack_manifest_latest.json",
    "dist/nexus_gate_source_bundle_latest.tar.gz",
    "docs/feedback/FEEDBACK_LOG.md",
    "ledger/nexus_cell/continuity.jsonl",
    "ledger/nexus_gate_ledger.v0.1.0.jsonl",
    "ledger/recommendation_outcomes.jsonl",
    "reports/CHATGPT_HANDOFF_LATEST.md",
    "reports/CODEX_HANDOFF_LATEST.md",
    "reports/nexus_*_latest.json",
    "reports/nexus_meta_orchestrator_gate.v*.json",
    "state/ai_feedback_context_latest.json",
    "state/algorithms/nexus_algorithm_cards*.json",
    "state/coherence/*.json",
    "state/decision/*.json",
    "state/discoveries/nexus_discovery_cards*.json",
    "state/interconnect_graph.v*.json",
    "state/loops/nexus_loop_orchestration_latest.json",
    "state/loops/nexus_meta_orchestrator_gate.v*.json",
    "state/loops/nexus_toolbelt.v*.json",
    "state/loops/nexus_toolbelt_latest.json",
    "state/neural_activity/repo_neural_graph_latest.json",
    "state/nexus_origin_manifest_latest.json",
    "state/nexus_nn_router_index.v*.json",
]

UNTRACKED_GENERATED_PATTERNS = [
    "dist/nexus_gate_pack_manifest_20*.json",
    "dist/nexus_gate_source_bundle_20*.tar.gz",
    "reports/human_surface/**",
    "reports/tmp/**",
]

BLOCKED_ACTIONS = [
    "delete_source_files",
    "clean_unclassified_paths",
    "git_reset_hard",
    "git_clean_unbounded",
    "remove_user_changes",
    "self_authorize_commit",
]

CLAIM_BOUNDARY = (
    "Runtime hygiene is local generated-surface cleanup evidence only. It may restore "
    "known generated tracked surfaces and remove known untracked generated exhaust. It "
    "does not prove correctness, safety, security, production readiness, or authority."
)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rel(path: str) -> str:
    path = path.replace("\\", "/").strip()
    if len(path) >= 2 and path[0] == '"' and path[-1] == '"':
        path = path[1:-1]
    return path


def _run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def _git_status(root: Path) -> list[dict[str, str]]:
    proc = _run_git(root, ["status", "--porcelain"])
    rows: list[dict[str, str]] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:] if line.startswith("?? ") else line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        rows.append({"status": status, "path": _rel(path)})
    return rows


def _matches(path: str, patterns: list[str]) -> bool:
    path = _rel(path)
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _classify(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    tracked_generated: list[dict[str, str]] = []
    untracked_generated: list[dict[str, str]] = []
    source_dirty: list[dict[str, str]] = []
    for row in rows:
        path = row["path"]
        if row["status"] == "??":
            if _matches(path, UNTRACKED_GENERATED_PATTERNS):
                untracked_generated.append(row)
            else:
                source_dirty.append(row)
        elif _matches(path, TRACKED_GENERATED_PATTERNS):
            tracked_generated.append(row)
        else:
            source_dirty.append(row)
    return {
        "tracked_generated": tracked_generated,
        "untracked_generated": untracked_generated,
        "source_dirty": source_dirty,
    }


def _safe_unlink(root: Path, rel_path: str) -> bool:
    target = (root / rel_path).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return False
    if target.is_file():
        target.unlink()
        return True
    return False


def _write_report(root: Path, payload: dict[str, Any]) -> None:
    path = root / REPORT_LATEST
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_runtime_hygiene_report(root: str | Path, apply: bool = False) -> dict[str, Any]:
    root_path = Path(root).resolve()
    before = _git_status(root_path)
    classified = _classify(before)
    restored: list[str] = []
    removed: list[str] = []
    restore_error = ""

    if apply and classified["tracked_generated"]:
        paths = [row["path"] for row in classified["tracked_generated"]]
        proc = _run_git(root_path, ["restore", "--worktree", "--", *paths])
        if proc.returncode == 0:
            restored = paths
        else:
            restore_error = (proc.stderr or proc.stdout).strip()

    if apply:
        for row in classified["untracked_generated"]:
            if _safe_unlink(root_path, row["path"]):
                removed.append(row["path"])

    after = _git_status(root_path) if apply else before
    after_classified = _classify(after)
    status = "pass" if not after_classified["source_dirty"] else "warn"
    if restore_error:
        status = "fail"

    report = {
        "schema": SCHEMA,
        "system": "NEXUS GATE",
        "version": VERSION,
        "phase": "Runtime Churn Hygiene",
        "mode": "apply" if apply else "dry_run",
        "status": status,
        "generated_at_utc": _utc(),
        "summary": {
            "tracked_generated": len(classified["tracked_generated"]),
            "untracked_generated": len(classified["untracked_generated"]),
            "source_dirty": len(classified["source_dirty"]),
            "restored": len(restored),
            "removed": len(removed),
            "remaining_dirty": len(after),
            "remaining_source_dirty": len(after_classified["source_dirty"]),
        },
        "tracked_generated": classified["tracked_generated"],
        "untracked_generated": classified["untracked_generated"],
        "source_dirty": classified["source_dirty"],
        "restored": restored,
        "removed": removed,
        "remaining_source_dirty": after_classified["source_dirty"],
        "restore_error": restore_error,
        "blocked_actions": BLOCKED_ACTIONS,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_action": (
            "Runtime generated churn cleaned."
            if apply and status == "pass"
            else "Run with --apply after committing intended source changes."
            if not apply
            else "Inspect remaining_source_dirty before staging."
        ),
    }
    _write_report(root_path, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify and clean NEXUS generated runtime churn.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = build_runtime_hygiene_report(args.root, apply=args.apply)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print(
            "NEXUS runtime hygiene: "
            f"{report['status']} generated={summary['tracked_generated'] + summary['untracked_generated']} "
            f"source_dirty={summary['source_dirty']} mode={report['mode']}"
        )
    return 0 if report["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
