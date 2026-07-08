
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

VERSION = "0.9.3"
MODE = "nexus_ai_loop_toolkit"

TOOLS = [
    "repo-radar",
    "scope-hygiene",
    "claim-boundary-audit",
    "surface-map",
    "stale-surface-scan",
    "next-action-router",
    "handoff-pack",
    "dependency-preflight",
    "alignment-score",
    "boundary-scan",
    "release-brief",
    "evolution-radar",
]

BOUNDARY = {
    "repo_mutation_enabled": False,
    "git_stage_enabled": False,
    "git_commit_enabled": False,
    "git_push_enabled": False,
    "network_enabled": False,
    "secrets_enabled": False,
    "autonomous_authority": False,
    "arbitrary_command_execution": False,
}


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _run(root: Path, argv: list[str], timeout: int = 30) -> dict[str, Any]:
    try:
        p = subprocess.run(argv, cwd=str(root), capture_output=True, text=True, timeout=timeout, check=False)
        return {"argv": argv, "ok": p.returncode == 0, "returncode": p.returncode, "stdout": p.stdout[-5000:], "stderr": p.stderr[-3000:]}
    except Exception as exc:
        return {"argv": argv, "ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}


def _git(root: Path, *args: str) -> dict[str, Any]:
    return _run(root, ["git", *args])


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def _read_text(path: Path, limit: int = 200000) -> str:
    try:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8-sig", errors="replace")[:limit]
    except Exception:
        return ""


def _status_lines(root: Path) -> list[str]:
    out = _git(root, "status", "--short").get("stdout", "")
    return [line for line in out.splitlines() if line.strip()]


def _changed_paths(root: Path) -> list[str]:
    paths = []
    for line in _status_lines(root):
        p = line[3:].strip()
        if " -> " in p:
            p = p.split(" -> ", 1)[1].strip()
        paths.append(p.strip('"'))
    return paths


def _category(path: str) -> str:
    p = path.replace("\\", "/")
    lower = p.lower()
    if ".bak" in lower or lower.endswith(".tmp") or "backup" in lower:
        return "backup_residue"
    if p.startswith("reports/") or p.startswith("logs/") or p.startswith("electron/reports/"):
        return "runtime_report"
    if p.startswith("ledger/") or "/ledger/" in p:
        return "ledger_churn"
    if p.startswith("state/"):
        return "state_surface"
    if p.startswith("tests/"):
        return "test_surface"
    if p.startswith("docs/") or p.endswith(".md"):
        return "doc_surface"
    if p.startswith("nexus_gate/") or p.endswith(".py"):
        return "python_surface"
    if p.startswith("electron/"):
        return "electron_surface"
    if p.startswith("loops/"):
        return "loop_registry"
    return "other"


def _registry(root: Path) -> dict[str, Any]:
    return _read_json(root / "loops" / "nexus_loop_registry.v0.1.json", {})


def _cards(root: Path) -> dict[str, Any]:
    return _read_json(root / "state" / "loops" / "nexus_loop_cards_latest.json", {})


def _compiler(root: Path) -> dict[str, Any]:
    return _read_json(root / "reports" / "nexus_compile_report_latest.json", {})


def repo_radar(root: Path) -> dict[str, Any]:
    reg = _registry(root)
    cards = _cards(root)
    comp = _compiler(root)
    head = _git(root, "rev-parse", "--short", "HEAD").get("stdout", "").strip()
    branch = _git(root, "branch", "--show-current").get("stdout", "").strip()
    status = _status_lines(root)
    return {
        "head": head,
        "branch": branch,
        "dirty": bool(status),
        "changed_count": len(status),
        "loop_count": len(reg.get("loops", {})),
        "card_count": cards.get("card_count", len(cards.get("cards", []))),
        "compiler_status": comp.get("status", "unknown"),
        "available_loops": sorted(reg.get("loops", {}).keys()),
        "recommended_loop": "scope-hygiene" if status else "evolution-radar",
    }


def scope_hygiene(root: Path) -> dict[str, Any]:
    paths = _changed_paths(root)
    by_category: dict[str, list[str]] = {}
    for p in paths:
        by_category.setdefault(_category(p), []).append(p)
    residue_categories = {"backup_residue", "runtime_report", "ledger_churn"}
    intended_candidates = [p for p in paths if _category(p) not in residue_categories]
    residue_candidates = [p for p in paths if _category(p) in residue_categories]
    return {
        "changed_count": len(paths),
        "by_category": by_category,
        "intended_candidates": intended_candidates[:200],
        "residue_candidates": residue_candidates[:200],
        "staging_rule": "stage_intended_files_only",
        "recommendation": "review_residue_before_commit" if residue_candidates else "scope_clean_enough_for_targeted_stage",
    }


def claim_boundary_audit(root: Path) -> dict[str, Any]:
    targets = [root / "README.md", root / "chatgpt" / "scripts.md"] + list((root / "docs").rglob("*.md"))[:300]
    risky = ["guaranteed", "proves alignment", "proof of safety", "autonomous authority", "cannot fail", "production safe"]
    findings = []
    for path in targets:
        if not path.exists() or not path.is_file():
            continue
        text = _read_text(path).lower()
        for token in risky:
            if token in text:
                rel = str(path.relative_to(root)).replace("\\", "/")
                findings.append({"path": rel, "token": token})
    return {
        "scanned_files": len(targets),
        "findings": findings[:100],
        "finding_count": len(findings),
        "recommendation": "review_claim_boundary_language" if findings else "claim_boundary_clean",
        "note": "Findings are review prompts, not proof of an invalid claim.",
    }


def surface_map(root: Path) -> dict[str, Any]:
    groups = {}
    for top in ["nexus_gate", "docs", "tests", "scripts", "loops", "state", "reports", "electron"]:
        base = root / top
        if not base.exists():
            groups[top] = {"exists": False, "files": 0}
            continue
        files = [p for p in base.rglob("*") if p.is_file()]
        groups[top] = {"exists": True, "files": len(files), "sample": [str(p.relative_to(root)).replace("\\", "/") for p in files[:12]]}
    return {"surface_groups": groups, "primary_organs": ["README", "loop_registry", "loop_cards", "compiler", "NexusCell", "GITNEXUS", "HUD"]}


def stale_surface_scan(root: Path) -> dict[str, Any]:
    scan_paths = [root / "README.md", root / "ROADMAP.md", root / "pyproject.toml", root / "docs" / "versioning" / "NEXUS_CHANGELOG.md", root / "docs" / "updates" / "UPDATE_CHART.md"]
    hits = []
    for path in scan_paths:
        text = _read_text(path)
        for idx, line in enumerate(text.splitlines(), start=1):
            if "v0.9.2" in line or "v0.9.1" in line:
                hits.append({"path": str(path.relative_to(root)).replace("\\", "/"), "line": idx, "text": line[:240]})
    return {"lineage_hits": hits[:120], "hit_count": len(hits), "note": "Older version hits can be valid lineage; inspect only current-state claims."}


def next_action_router(root: Path) -> dict[str, Any]:
    status = _status_lines(root)
    comp = _compiler(root)
    failed = [g.get("gate") for g in comp.get("gates", []) if isinstance(g, dict) and g.get("status") == "fail"]
    if failed:
        rec = "compiler-wound-focus"
        why = "compiler has failed gates"
    elif status:
        rec = "scope-hygiene"
        why = "working tree has local changes"
    else:
        rec = "evolution-radar"
        why = "tree appears clean and ready for next evolution planning"
    return {"recommended_loop": rec, "why": why, "failed_gates": failed, "dirty": bool(status), "changed_count": len(status)}


def handoff_pack(root: Path) -> dict[str, Any]:
    return {
        "repo": str(root),
        "radar": repo_radar(root),
        "scope": scope_hygiene(root),
        "next_action": next_action_router(root),
        "cards_path": "state/loops/nexus_loop_cards_latest.json",
        "doctrine": "Read README.md and chatgpt/scripts.md before coding.",
    }


def dependency_preflight(root: Path) -> dict[str, Any]:
    checks = {}
    for name, argv in {
        "python": [sys.executable, "--version"],
        "git": ["git", "--version"],
        "node": ["node", "--version"],
        "npm": ["npm", "--version"],
        "powershell": ["powershell", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
    }.items():
        if shutil.which(argv[0]) or argv[0] == sys.executable:
            checks[name] = _run(root, argv, timeout=10)
        else:
            checks[name] = {"ok": False, "reason": "not_found_on_path"}
    return {"platform": platform.platform(), "checks": checks}


def alignment_score(root: Path) -> dict[str, Any]:
    signals = {
        "readme": (root / "README.md").exists(),
        "script_doctrine": (root / "chatgpt" / "scripts.md").exists(),
        "loop_registry": (root / "loops" / "nexus_loop_registry.v0.1.json").exists(),
        "loop_cards": (root / "state" / "loops" / "nexus_loop_cards_latest.json").exists(),
        "compiler_report": (root / "reports" / "nexus_compile_report_latest.json").exists(),
        "authority_boundary_false": not bool(_registry(root).get("authority_boundary", {}).get("autonomous_authority", True)),
    }
    score = round(sum(1 for v in signals.values() if v) / max(1, len(signals)), 3)
    return {"score": score, "signals": signals, "recommendation": "release-brief" if score >= 0.85 else "repo-radar"}


def boundary_scan(root: Path) -> dict[str, Any]:
    reg = _registry(root)
    boundary = reg.get("authority_boundary", {})
    bad_boundary = {k: boundary.get(k) for k in ["autonomous_authority", "arbitrary_command_execution", "network_enabled", "secrets_enabled", "git_write_enabled", "memory_promotion_enabled", "self_authorization_enabled"] if boundary.get(k) is not False}
    mutating_commands = [k for k, v in reg.get("allowed_commands", {}).items() if isinstance(v, dict) and v.get("mutates")]
    mutating_loops = [k for k, v in reg.get("loops", {}).items() if isinstance(v, dict) and v.get("mutates")]
    return {"boundary_drift": bad_boundary, "mutating_commands": mutating_commands, "mutating_loops": mutating_loops, "status": "pass" if not bad_boundary and not mutating_commands and not mutating_loops else "review"}


def release_brief(root: Path) -> dict[str, Any]:
    return {"radar": repo_radar(root), "alignment": alignment_score(root), "boundary": boundary_scan(root), "next_action": next_action_router(root)}


def evolution_radar(root: Path) -> dict[str, Any]:
    candidates = [
        {"id": "hud-loop-renderer", "why": "Render loop cards in Electron as human cards.", "loop_to_start": "hud-loop-sync"},
        {"id": "scope-cleaner-simulation", "why": "Add dry-run cleanup plans without deletion.", "loop_to_start": "scope-hygiene"},
        {"id": "wound-timeline-hud", "why": "Show gate wounds and seals as a timeline.", "loop_to_start": "wound-indexed-resume"},
        {"id": "claim-boundary-ci", "why": "Add claim-boundary audit to compiler gates.", "loop_to_start": "claim-boundary-audit"},
        {"id": "next-action-autocomplete", "why": "Let AI choose loops from packet evidence.", "loop_to_start": "next-action-router"},
    ]
    return {"candidates": candidates, "recommended_first": candidates[0]}


def build_toolkit_packet(root: str | Path, tool: str, intent: str = "") -> dict[str, Any]:
    root = Path(root).resolve()
    if tool not in TOOLS:
        raise ValueError(f"Unknown tool {tool!r}; expected one of {', '.join(TOOLS)}")
    builders = {
        "repo-radar": repo_radar,
        "scope-hygiene": scope_hygiene,
        "claim-boundary-audit": claim_boundary_audit,
        "surface-map": surface_map,
        "stale-surface-scan": stale_surface_scan,
        "next-action-router": next_action_router,
        "handoff-pack": handoff_pack,
        "dependency-preflight": dependency_preflight,
        "alignment-score": alignment_score,
        "boundary-scan": boundary_scan,
        "release-brief": release_brief,
        "evolution-radar": evolution_radar,
    }
    data = builders[tool](root)
    return {
        "version": VERSION,
        "mode": MODE,
        "tool": tool,
        "intent": intent,
        "generated_utc": _utc(),
        "status": "pass",
        "boundary": BOUNDARY,
        "data": data,
        "claim_boundary": "AI loop toolkit packets are local evidence. They do not grant autonomous authority, execution authority, git write authority, safety proof, security proof, or correctness proof.",
    }


def write_outputs(root: Path, packet: dict[str, Any]) -> None:
    tool = packet["tool"].replace("-", "_")
    report = root / "reports" / f"nexus_loop_toolkit_{tool}_latest.json"
    state = root / "state" / "loops" / f"toolkit_{tool}_latest.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    state.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    report.write_text(encoded, encoding="utf-8")
    state.write_text(encoded, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEXUS AI loop toolkit packet emitter.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--tool", default="repo-radar", choices=TOOLS)
    parser.add_argument("--intent", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    packet = build_toolkit_packet(root, args.tool, args.intent)
    if not args.no_write:
        write_outputs(root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(json.dumps({"ok": True, "tool": packet["tool"], "mode": packet["mode"], "status": packet["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
