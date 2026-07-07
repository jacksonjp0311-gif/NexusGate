"""Ollama model inventory detection for NEXUS NN router v0.6.2."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .contract import ROLE_PREFERENCES, RoleAssignment, choose_model


DEFAULT_MODELS_ROOT = Path.home() / "OneDrive" / "Desktop" / ".ollama" / "models"


def _safe_read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _digest_to_blob_name(digest: str) -> Optional[str]:
    if not isinstance(digest, str):
        return None
    if digest.startswith("sha256:"):
        return "sha256-" + digest.split(":", 1)[1]
    return None


def _walk_manifest_files(manifest_root: Path) -> Iterable[Path]:
    if not manifest_root.exists():
        return []
    return [item for item in manifest_root.rglob("*") if item.is_file()]


def _name_from_manifest_path(manifest_file: Path, models_root: Path) -> str:
    try:
        relative_parts = manifest_file.relative_to(models_root).parts
    except ValueError:
        relative_parts = manifest_file.parts

    if "manifests" in relative_parts:
        idx = relative_parts.index("manifests")
        tail = relative_parts[idx + 1 :]
        if len(tail) >= 2:
            model_name = tail[-2]
            tag = tail[-1]
            return f"{model_name}:{tag}"

    return manifest_file.name


def _referenced_digests(manifest_data: Optional[dict]) -> Set[str]:
    referenced: Set[str] = set()
    if not isinstance(manifest_data, dict):
        return referenced

    config = manifest_data.get("config")
    if isinstance(config, dict):
        blob_name = _digest_to_blob_name(config.get("digest"))
        if blob_name:
            referenced.add(blob_name)

    layers = manifest_data.get("layers")
    if isinstance(layers, list):
        for layer in layers:
            if isinstance(layer, dict):
                blob_name = _digest_to_blob_name(layer.get("digest"))
                if blob_name:
                    referenced.add(blob_name)

    return referenced


def detect_ollama_inventory(models_root: Optional[os.PathLike] = None) -> Dict[str, object]:
    """Detect local Ollama model manifests without invoking ollama.

    The function reads manifest JSON files under the local Ollama models
    directory. It does not call shell commands, does not read secrets, and does
    not access external services.
    """
    root = Path(models_root) if models_root else DEFAULT_MODELS_ROOT
    root = root.expanduser()

    manifests_root = root / "manifests"
    blobs_root = root / "blobs"

    manifest_files = list(_walk_manifest_files(manifests_root))
    models: Dict[str, dict] = {}
    referenced_blobs: Set[str] = set()

    for manifest_file in manifest_files:
        manifest_data = _safe_read_json(manifest_file)
        name = _name_from_manifest_path(manifest_file, root)
        referenced = _referenced_digests(manifest_data)
        referenced_blobs.update(referenced)

        model_type = None
        quantization = None
        if name.startswith("mistral:"):
            model_type = "7.2B"
            quantization = "Q4_K_M"
        if name.startswith("tnn-phi4-mini:") or name.startswith("phi4:"):
            model_type = "Phi-4-mini"
            quantization = "Q4_K_M"
        if name.startswith("phi3:"):
            model_type = "3.8B"
            quantization = "Q4_0"

        models[name] = {
            "name": name,
            "manifest_path": str(manifest_file),
            "manifest_present": True,
            "referenced_blob_count": len(referenced),
            "type": model_type,
            "quant": quantization,
        }

    blob_files = set()
    total_blob_size = 0
    if blobs_root.exists():
        for blob in blobs_root.rglob("*"):
            if blob.is_file():
                blob_files.add(blob.name)
                try:
                    total_blob_size += blob.stat().st_size
                except OSError:
                    pass

    missing_blobs = sorted([blob for blob in referenced_blobs if blob not in blob_files])
    orphan_blobs = sorted([blob for blob in blob_files if blob not in referenced_blobs])

    return {
        "models_root": str(root),
        "models_root_exists": root.exists(),
        "manifest_count": len(manifest_files),
        "blob_count": len(blob_files),
        "total_blob_size_bytes": total_blob_size,
        "total_blob_size_gb": round(total_blob_size / (1024 ** 3), 2),
        "models": models,
        "missing_blobs": missing_blobs,
        "orphan_blobs": orphan_blobs,
        "ollama_models_env": os.environ.get("OLLAMA_MODELS"),
    }


def assign_roles(inventory: Dict[str, object]) -> Dict[str, dict]:
    models = inventory.get("models", {})
    if not isinstance(models, dict):
        models = {}

    assignments: Dict[str, dict] = {}
    for role in ROLE_PREFERENCES.keys():
        assignment = choose_model(models, role)
        assignments[role] = assignment.to_dict()

    handoff = choose_model(models, "HANDOFF")
    assignments["HANDOFF"] = handoff.to_dict()
    return assignments