from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import csv
import json

from .validation import validate_result


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_curves_csv(path: Path, result: Dict[str, Any]) -> None:
    curves = result.get("curves", [])
    path.parent.mkdir(parents=True, exist_ok=True)
    if not curves:
        path.write_text("step\n", encoding="utf-8")
        return
    keys = list(curves[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in curves:
            writer.writerow(row)


def write_summary(path: Path, result: Dict[str, Any], validation: Dict[str, Any]) -> None:
    metrics = result.get("metrics", {})
    exp = result.get("experiment", {})
    lines = []
    lines.append(f"# Petri Dish Pro Run — {result.get('run_id')}\n")
    lines.append(f"Experiment: **{exp.get('name')}**\n")
    lines.append(f"Preset: `{exp.get('preset')}`\n")
    lines.append(f"Validation: **{validation.get('status')}**\n")
    lines.append("\n## Metrics\n")
    for key, value in metrics.items():
        lines.append(f"- `{key}`: {value}\n")
    lines.append("\n## Organisms\n")
    for org in result.get("organisms", []):
        lines.append(f"- **{org.get('label')}** (`{org.get('id')}`): final population {org.get('final_population')} — {org.get('notes')}\n")
    lines.append("\n## Claim Boundary\n")
    lines.append(result.get("claim_boundary", ""))
    lines.append("\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(lines), encoding="utf-8")



def _rgb_for_value(v: float) -> str:
    v = max(0.0, min(1.0, float(v or 0.0)))
    r = int(min(255, 20 + 30 * v + 80 * (v ** 3)))
    g = int(min(255, 70 + 210 * v))
    b = int(min(255, 120 + 135 * (v ** 0.5)))
    return f"rgb({r},{g},{b})"


def write_density_svg(path: Path, result: Dict[str, Any], size: int = 720) -> None:
    matrix = result.get("density", {}).get("normalized", [])
    path.parent.mkdir(parents=True, exist_ok=True)
    if not matrix:
        path.write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>", encoding="utf-8")
        return
    n = len(matrix)
    cell = size / max(1, n)
    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 {size} {size}'>",
        "<rect width='100%' height='100%' fill='#020611'/>",
        "<defs><radialGradient id='lens'><stop offset='0%' stop-color='white' stop-opacity='.10'/><stop offset='65%' stop-color='#00f0ff' stop-opacity='.03'/><stop offset='100%' stop-color='black' stop-opacity='.64'/></radialGradient></defs>",
    ]
    for y, row in enumerate(matrix):
        for x, v in enumerate(row):
            if v <= 0.003:
                continue
            opacity = min(0.95, 0.12 + float(v) * 0.95)
            parts.append(f"<rect x='{x*cell:.3f}' y='{y*cell:.3f}' width='{cell+0.25:.3f}' height='{cell+0.25:.3f}' fill='{_rgb_for_value(v)}' opacity='{opacity:.3f}'/>")
    parts.append(f"<circle cx='{size/2}' cy='{size/2}' r='{size*0.49}' fill='url(#lens)'/>")
    parts.append(f"<circle cx='{size/2}' cy='{size/2}' r='{size*0.485}' fill='none' stroke='#00f0ff' stroke-opacity='.28' stroke-width='3'/>")
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_artifact_bundle(root: Path, result: Dict[str, Any]) -> Dict[str, str]:
    validation = validate_result(result)
    run_id = result.get("run_id", "petri_run")
    run_dir = root / "artifacts" / "runs" / run_id
    reports = root / "reports"
    run_dir.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    experiment = result.get("experiment", {})
    density_payload = {
        "run_id": run_id,
        "density": result.get("density"),
        "fields": result.get("fields"),
        "snapshots": result.get("snapshots", []),
        "organisms": result.get("organisms", []),
    }

    write_json(run_dir / "run.json", result)
    write_json(run_dir / "experiment.json", experiment)
    write_json(run_dir / "density.json", density_payload)
    write_density_svg(run_dir / "density_preview.svg", result)
    write_json(run_dir / "validation.json", validation)
    write_curves_csv(run_dir / "populations.csv", result)
    write_summary(run_dir / "summary.md", result, validation)

    write_json(reports / "latest_run.json", result)
    write_json(reports / "latest_density.json", density_payload)
    write_density_svg(reports / "latest_density_preview.svg", result)
    write_json(reports / "latest_validation.json", validation)
    write_summary(reports / "latest_summary.md", result, validation)

    return {
        "run_dir": str(run_dir),
        "latest_run": str(reports / "latest_run.json"),
        "latest_density": str(reports / "latest_density.json"),
        "latest_summary": str(reports / "latest_summary.md"),
        "latest_density_preview": str(reports / "latest_density_preview.svg"),
        "latest_validation": str(reports / "latest_validation.json"),
        "status": validation.get("status", "unknown"),
    }
