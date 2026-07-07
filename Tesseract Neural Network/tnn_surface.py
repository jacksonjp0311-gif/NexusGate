"""Self-contained Tesseract Neural Network surface for NexusGate.

TNN v0.1.1 runs from the NexusGate repository without requiring the
NeuralForge checkout at runtime. NeuralForge can be used only as an explicit
refresh source through refresh_from_neuralforge.py.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

TNN_VERSION = "nexus.tesseract_neural_network.v0.1.1"
TNN_MODEL_NAME = "Tesseract Neural Network/self-contained-receipt-core"

TNN_ROOT = Path(__file__).resolve().parent
RECEIPTS_DIR = TNN_ROOT / "receipts"
STATE_DIR = TNN_ROOT / "state"
LOCAL_BUNDLE_PATH = RECEIPTS_DIR / "receipt_bundle_latest.json"
LOCAL_STATE_PATH = STATE_DIR / "tnn_state_latest.json"

DEFAULT_BUNDLE: Dict[str, Any] = {
    "ok": True,
    "source": "nexusgate_local_seed",
    "root_found": True,
    "neuralforge_required": False,
    "self_contained": True,
    "receipts": {
        "source_intake": {
            "ok": True,
            "registry_allowed": True,
            "live_pull_allowed": False,
            "scraping_allowed": False,
            "raw_collection_allowed": False,
            "mutation_allowed": False,
            "claim_boundary": "NexusGate-local TNN seed; no live network calls, scraping, raw collection, or mutation.",
            "source_count": 0,
            "source_intake_version": "tnn.local_seed.v0.1.1",
        }
    },
    "missing_receipts": ["control_bundle", "approval", "sandbox_plan"],
    "blocked_reasons": [],
}


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError) as error:
        return {"parse_error": str(error), "path": str(path)}


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_local_bundle() -> Dict[str, Any]:
    bundle = read_json(LOCAL_BUNDLE_PATH)
    if bundle is None:
        bundle = dict(DEFAULT_BUNDLE)
        write_json(LOCAL_BUNDLE_PATH, bundle)
    bundle.setdefault("ok", True)
    bundle.setdefault("self_contained", True)
    bundle.setdefault("neuralforge_required", False)
    bundle.setdefault("receipts", {})
    bundle.setdefault("missing_receipts", [])
    bundle.setdefault("blocked_reasons", [])
    return bundle


def bool_text(value: Any) -> str:
    if value is True:
        return "True"
    if value is False:
        return "False"
    return "unknown"


def summarize(bundle: Dict[str, Any], intent: str) -> str:
    lines = [
        "TESSERACT NEURAL NETWORK",
        "========================",
        f"Intent: {intent}",
        f"Version: {TNN_VERSION}",
        "",
        "Status: ONLINE",
        "Runtime: NexusGate-local self-contained core",
        f"NeuralForge required: {bool_text(bundle.get('neuralforge_required'))}",
        f"Self-contained: {bool_text(bundle.get('self_contained'))}",
        "",
    ]

    receipts = bundle.get("receipts", {})
    control = receipts.get("control_bundle", {}) if isinstance(receipts, dict) else {}
    approval = receipts.get("approval", {}) if isinstance(receipts, dict) else {}
    sandbox = receipts.get("sandbox_plan", {}) if isinstance(receipts, dict) else {}
    source = receipts.get("source_intake", {}) if isinstance(receipts, dict) else {}

    if isinstance(control, dict) and control:
        proposals = control.get("patch_proposal_receipts") or []
        lines.extend([
            "Control bundle:",
            f"- ok: {bool_text(control.get('ok'))}",
            f"- ready_for_human_review: {bool_text(control.get('ready_for_human_review'))}",
            f"- proposals: {len(proposals) if isinstance(proposals, list) else 'unknown'}",
            f"- mutation_allowed: {bool_text(control.get('mutation_allowed'))}",
            "",
        ])

    if isinstance(approval, dict) and approval:
        lines.extend([
            "Approval:",
            f"- decision: {approval.get('decision', approval.get('approval_status', 'unknown'))}",
            f"- approved_by_human: {bool_text(approval.get('approved_by_human'))}",
            f"- next_step_unlocked: {approval.get('next_step_unlocked', 'unknown')}",
            f"- mutation_allowed: {bool_text(approval.get('mutation_allowed'))}",
            "",
        ])

    if isinstance(sandbox, dict) and sandbox:
        lines.extend([
            "Sandbox plan:",
            f"- ok: {bool_text(sandbox.get('ok'))}",
            f"- planning_allowed: {bool_text(sandbox.get('planning_allowed'))}",
            f"- mutation_allowed: {bool_text(sandbox.get('mutation_allowed'))}",
            f"- apply_allowed: {bool_text(sandbox.get('apply_allowed'))}",
            "",
        ])

    if isinstance(source, dict) and source:
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
        lines.append("Missing optional receipts: " + ", ".join(str(x) for x in missing))
        lines.append("")

    lines.extend([
        "Recommendation:",
        "Use TNN as the governed NexusGate NN lane. It can operate from NexusGate-local state without NeuralForge as a runtime dependency.",
        "",
        "Boundary:",
        "Recommendation-only. No shell execution, no patch application, no main-branch mutation, no live API pulls, no scraping, no autonomous authority.",
    ])
    return "\n".join(lines)


def build_model_response(intent: str) -> Dict[str, Any]:
    bundle = load_local_bundle()
    response = {
        "role": "TNN",
        "model": TNN_MODEL_NAME,
        "ok": bool(bundle.get("ok", True)),
        "response": summarize(bundle, intent),
        "tnn_version": TNN_VERSION,
        "self_contained": True,
        "neuralforge_required": False,
        "receipt_bundle": bundle,
    }
    write_json(LOCAL_STATE_PATH, {
        "ok": response["ok"],
        "role": response["role"],
        "model": response["model"],
        "tnn_version": TNN_VERSION,
        "self_contained": True,
        "neuralforge_required": False,
        "last_intent": intent,
        "local_bundle": str(LOCAL_BUNDLE_PATH),
    })
    return response


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", default="Read Tesseract Neural Network state.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    response = build_model_response(args.intent)
    print(json.dumps(response, indent=2, sort_keys=True) if args.json else response["response"])


if __name__ == "__main__":
    main()
