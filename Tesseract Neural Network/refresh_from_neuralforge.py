"""Explicit optional refresh from NeuralForge into NexusGate-local TNN receipts.

This is not used by default runtime. It is a manual import/update tool.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from tnn_surface import LOCAL_BUNDLE_PATH, LOCAL_STATE_PATH, TNN_VERSION, write_json

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
    except (OSError, json.JSONDecodeError) as error:
        return {"parse_error": str(error), "path": str(path)}


def refresh(neuralforge_root: Optional[Path] = None) -> Dict[str, Any]:
    root = neuralforge_root or default_neuralforge_root()
    if not root:
        return {
            "ok": False,
            "refreshed": False,
            "blocked_reasons": ["NeuralForge root not found."],
            "bundle_path": str(LOCAL_BUNDLE_PATH),
        }

    receipts: Dict[str, Any] = {}
    missing: list[str] = []
    for name, rel in RECEIPT_PATHS.items():
        value = read_json(root / rel)
        if value is None:
            missing.append(name)
        else:
            receipts[name] = value

    bundle = {
        "ok": True,
        "source": "explicit_neuralforge_refresh",
        "source_root": str(root),
        "self_contained": True,
        "neuralforge_required": False,
        "receipts": receipts,
        "missing_receipts": missing,
        "blocked_reasons": [],
        "tnn_version": TNN_VERSION,
        "claim_boundary": "Local cached receipt bundle. NeuralForge was only used as an explicit refresh source.",
    }
    write_json(LOCAL_BUNDLE_PATH, bundle)
    write_json(LOCAL_STATE_PATH, {
        "ok": True,
        "refreshed": True,
        "tnn_version": TNN_VERSION,
        "source_root": str(root),
        "bundle_path": str(LOCAL_BUNDLE_PATH),
        "missing_receipts": missing,
    })
    return {
        "ok": True,
        "refreshed": True,
        "bundle_path": str(LOCAL_BUNDLE_PATH),
        "state_path": str(LOCAL_STATE_PATH),
        "missing_receipts": missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--neuralforge-root", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.neuralforge_root).resolve() if args.neuralforge_root else None
    result = refresh(root)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)


if __name__ == "__main__":
    main()
