"""NexusGate NN-router shim for the repo-local self-contained TNN core."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict


def _load_surface():
    repo_root = Path(__file__).resolve().parents[2]
    surface = repo_root / "Tesseract Neural Network" / "tnn_surface.py"
    spec = importlib.util.spec_from_file_location("nexusgate_tesseract_neural_network_surface", surface)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load Tesseract Neural Network surface: {surface}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_tesseract_neural_network_response(intent: str) -> Dict[str, Any]:
    module = _load_surface()
    return module.build_model_response(intent)
