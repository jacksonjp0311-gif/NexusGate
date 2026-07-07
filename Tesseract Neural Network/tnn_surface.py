"""Tesseract Neural Network minimal surface for NexusGate."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

TNN_VERSION = "nexus.tesseract_neural_network.v0.1.0"
TNN_MODEL_NAME = "Tesseract Neural Network/minimal-receipt-surface"

RECEIPT_PATHS = {
    "control_bundle": "artifacts/tpn/control_bundle_report_v1_13_latest.json",
    "approval": "artifacts/tpn/approval_report_v1_14_latest.json",
    "sandbox_plan": "artifacts/tpn/sandbox_plan_report_v1_15_latest.json",
    "source_intake": "artifacts/tpn/source_intake_report_v1_16_latest.json",
}


def default_neuralforge_root() -> Optional[Path]:
    for candidate in [
        os.environ.get("NEURALFORGE_ROOT", ""),
        str(Path.home() / "OneDrive" / "Desktop" / "NeuralForge"),
        str(Path.home() / "Desktop" / "NeuralForge"),
    ]:
        if candidate:
            path = Path(candidate).expanduser()
            if path.exists() and path.is_dir():
                return path.resolve()
    return None


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else None
    except Exception as error:
        return {"parse_error": str(error), "path": str(path)}


def bool_text(value: Any) -> str:
    if value is True:
        return "True"
    if value is False:
        return "False"
    return "unknown"


def collect_receipts(neuralforge_root: Optional[Path] = None) -> Dict[str, Any]:
    root = neuralforge_root or default_neuralforge_root()
    if not root:
        return {
            "ok": False,
            "root_found": False,
            "neuralforge_root": "",
            "receipts": {},
            "missing_receipts": list(RECEIPT_PATHS.keys()),
            "blocked_reasons": ["NeuralForge root not found."],
        }

    receipts: Dict[str, Any] = {}
    missing: list[str] = []
    for name, rel in RECEIPT_PATHS.items():
        value = read_json(root / rel)
        if value is None:
            missing.append(name)
        else:
            receipts[name] = value

    return {
        "ok": True,
        "root_found": True,
        "neuralforge_root": str(root),
        "receipts": receipts,
        "missing_receipts": missing,
        "blocked_reasons": [],
    }


def summarize(bundle: Dict[str, Any], intent: str) -> str:
    lines = [
        "TESSERACT NEURAL NETWORK",
        "========================",
        f"Intent: {intent}",
        f"Version: {TNN_VERSION}",
        "",
    ]
    if not bundle.get("root_found"):
        lines.extend([
            "Status: BLOCKED",
            "Reason: NeuralForge root not found.",
            "",
            "Boundary: no shell execution, no patch application, no live API pull, no scraping, no autonomous mutation.",
        ])
        return "\n".join(lines)

    receipts = bundle.get("receipts", {})
    control = receipts.get("control_bundle", {}) if isinstance(receipts, dict) else {}
    approval = receipts.get("approval", {}) if isinstance(receipts, dict) else {}
    sandbox = receipts.get("sandbox_plan", {}) if isinstance(receipts, dict) else {}
    source = receipts.get("source_intake", {}) if isinstance(receipts, dict) else {}

    lines.append("Status: ONLINE")
    lines.append(f"NeuralForge: {bundle.get('neuralforge_root')}")
    lines.append("")

    if control:
        proposals = control.get("patch_proposal_receipts") or []
        lines.extend([
            "Control bundle:",
            f"- ok: {bool_text(control.get('ok'))}",
            f"- ready_for_human_review: {bool_text(control.get('ready_for_human_review'))}",
            f"- proposals: {len(proposals) if isinstance(proposals, list) else 'unknown'}",
            f"- mutation_allowed: {bool_text(control.get('mutation_allowed'))}",
            "",
        ])
    if approval:
        lines.extend([
            "Approval:",
            f"- decision: {approval.get('decision', approval.get('approval_status', 'unknown'))}",
            f"- approved_by_human: {bool_text(approval.get('approved_by_human'))}",
            f"- next_step_unlocked: {approval.get('next_step_unlocked', 'unknown')}",
            f"- mutation_allowed: {bool_text(approval.get('mutation_allowed'))}",
            "",
        ])
    if sandbox:
        lines.extend([
            "Sandbox plan:",
            f"- ok: {bool_text(sandbox.get('ok'))}",
            f"- planning_allowed: {bool_text(sandbox.get('planning_allowed'))}",
            f"- mutation_allowed: {bool_text(sandbox.get('mutation_allowed'))}",
            f"- apply_allowed: {bool_text(sandbox.get('apply_allowed'))}",
            "",
        ])
    if source:
        lines.extend([
            "Source intake:",
            f"- registry_allowed: {bool_text(source.get('registry_allowed'))}",
            f"- live_pull_allowed: {bool_text(source.get('live_pull_allowed'))}",
            f"- scraping_allowed: {bool_text(source.get('scraping_allowed'))}",
            f"- raw_collection_allowed: {bool_text(source.get('raw_collection_allowed'))}",
            "",
        ])

    missing = bundle.get("missing_receipts") or []
    if missing:
        lines.append("Missing receipts: " + ", ".join(str(x) for x in missing))
        lines.append("")
    lines.extend([
        "Recommendation: use Tesseract Neural Network as the governed NexusGate NN lane.",
        "Boundary: recommendation-only; no shell execution, patch application, main-branch mutation, live API pulls, scraping, or autonomous authority.",
    ])
    return "\n".join(lines)


def build_model_response(intent: str, neuralforge_root: Optional[Path] = None) -> Dict[str, Any]:
    bundle = collect_receipts(neuralforge_root)
    return {
        "role": "TNN",
        "model": TNN_MODEL_NAME,
        "ok": bool(bundle.get("ok")),
        "response": summarize(bundle, intent),
        "tnn_version": TNN_VERSION,
        "receipt_bundle": bundle,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", default="Read Tesseract Neural Network state.")
    parser.add_argument("--neuralforge-root", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.neuralforge_root).resolve() if args.neuralforge_root else None
    response = build_model_response(args.intent, root)
    print(json.dumps(response, indent=2, sort_keys=True) if args.json else response["response"])


if __name__ == "__main__":
    main()
