"""Read-only geometry packet compiler for NEXUS GATE.

This module creates a compact Intent/Evidence/Authority/Context packet before
model calls, reducing broad repo scans and keeping model prompts bounded.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .manifest import load_contract_manifest
from .score import axis_complete, build_gate_flags

VERSION = "0.8.3C"


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _safe_write_json(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _compact_text(value: str, limit: int = 360) -> str:
    text = " ".join((value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 4].rstrip() + " ..."


def _split_refs(value: str) -> List[str]:
    refs: List[str] = []
    for raw in (value or "").replace(";", ",").split(","):
        item = raw.strip()
        if item and item not in refs:
            refs.append(item)
    return refs


def _infer_default_context(root: Path) -> List[str]:
    candidates = [
        "README.md",
        "docs/ENTRYPOINTS.md",
        "docs/algorithms/NEXUS_CORE_ALGORITHMS.md",
        "docs/intelligence/NEXUS_GEOMETRIC_MEMORY_ROUTER.md",
        "docs/algorithms/NEXUS_TESSERACT_ALIGNMENT_KERNEL.md",
        "docs/memory/EIMT_RUNTIME_MEMORY_CONTRACT.md",
        "state/nexus_geometric_memory_manifest.v0.8.3.json",
    ]
    return [item for item in candidates if (root / item).exists()]


def build_geometry_packet(
    root: Path,
    intent: str,
    evidence: str = "",
    authority: str = "read_only",
    context: str = "",
) -> Dict[str, Any]:
    root = root.resolve()
    manifest = load_contract_manifest(root)

    evidence_refs = _split_refs(evidence)
    context_refs = _split_refs(context)
    if not context_refs:
        context_refs = _infer_default_context(root)

    axis_status = {
        "Intent": bool((intent or "").strip()),
        "Evidence": bool(evidence_refs) or (root / "reports").exists() or (root / "tests").exists(),
        "Authority": bool((authority or "").strip()),
        "Context": bool(context_refs),
    }

    complete = axis_complete(axis_status)
    flags = build_gate_flags(axis_status, authority)

    packet: Dict[str, Any] = {
        "version": VERSION,
        "generated_utc": _utc_now(),
        "mode": "read_only_runtime_stub",
        "intent": _compact_text(intent),
        "axes": {
            "Intent": {"ok": axis_status["Intent"], "value": _compact_text(intent)},
            "Evidence": {"ok": axis_status["Evidence"], "refs": evidence_refs or ["tests/", "reports/", "compiler gate"]},
            "Authority": {
                "ok": axis_status["Authority"],
                "value": authority or "read_only",
                "boundary": "human_authorized_only_for_mutation",
            },
            "Context": {"ok": axis_status["Context"], "refs": context_refs},
        },
        "axis_complete": complete,
        "gate_flags": flags,
        "geometry_pass": False,
        "reason": "read_only_runtime_stub_no_repair_authority",
        "latency_plan": {
            "goal": "reduce broad model prompts by compiling bounded geometry packets first",
            "model_prompt_policy": "send intent + evidence refs + authority boundary + sliced context only",
            "avoid": ["whole_repo_dump", "uncited_memory", "autonomous_repair"],
        },
        "source_theory_stack": manifest.get("source_theory_stack", {}),
        "contract_status": manifest.get("status", "unknown"),
        "outputs": {
            "report": "reports/nexus_geometric_memory_packet_latest.json",
            "state": "state/nexus_geometric_memory_runtime_latest.json",
        },
    }
    return packet


def compile_geometry_packet(
    root: Path,
    intent: str,
    evidence: str = "",
    authority: str = "read_only",
    context: str = "",
    write_outputs: bool = True,
) -> Dict[str, Any]:
    packet = build_geometry_packet(root=root, intent=intent, evidence=evidence, authority=authority, context=context)
    if write_outputs:
        _safe_write_json(root / "reports" / "nexus_geometric_memory_packet_latest.json", packet)
        _safe_write_json(root / "state" / "nexus_geometric_memory_runtime_latest.json", {
            "version": VERSION,
            "generated_utc": packet["generated_utc"],
            "mode": packet["mode"],
            "axis_complete": packet["axis_complete"],
            "geometry_pass": packet["geometry_pass"],
            "reason": packet["reason"],
            "outputs": packet["outputs"],
        })
    return packet


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compile a read-only NEXUS geometric memory packet.")
    parser.add_argument("--root", default=".", help="Repo root.")
    parser.add_argument("--intent", default="What should we do next?", help="Human intent or issue summary.")
    parser.add_argument("--evidence", default="", help="Comma-separated evidence refs.")
    parser.add_argument("--authority", default="read_only", help="Authority mode. Default: read_only.")
    parser.add_argument("--context", default="", help="Comma-separated context refs.")
    parser.add_argument("--json", action="store_true", help="Print packet JSON.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    packet = compile_geometry_packet(
        root=root,
        intent=args.intent,
        evidence=args.evidence,
        authority=args.authority,
        context=args.context,
        write_outputs=True,
    )

    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(json.dumps({
            "ok": True,
            "version": VERSION,
            "report": packet["outputs"]["report"],
            "state": packet["outputs"]["state"],
            "axis_complete": packet["axis_complete"],
            "geometry_pass": packet["geometry_pass"],
            "reason": packet["reason"],
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
