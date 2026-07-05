"""Manifest helpers for the NEXUS Geometric Memory Router."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

CONTRACT_MANIFEST = Path("state/nexus_geometric_memory_manifest.v0.8.3.json")


def load_contract_manifest(root: Path) -> Dict[str, Any]:
    """Load the contract-first manifest.

    Missing manifests return a blocked placeholder instead of raising. This keeps
    the runtime usable as a diagnostic surface during partial rehydration.
    """

    path = root / CONTRACT_MANIFEST
    if not path.exists():
        return {
            "version": "missing",
            "name": "NEXUS Geometric Memory Router",
            "status": "missing_contract_manifest",
            "axes": [],
            "gates": {
                "geometry_pass": "blocked_missing_manifest",
                "model_output": "recommendation_only",
                "repo_mutation": "human_authorized_only",
            },
        }

    return json.loads(path.read_text(encoding="utf-8"))
