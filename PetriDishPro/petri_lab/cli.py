
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .engine import run_simulation
from .validation import validate_run


def _write_artifacts(root: Path, result: dict) -> dict:
    run_id = result["run_id"]
    artifact_dir = root / "artifacts" / "bio" / "runs" / run_id
    reports_dir = root / "reports" / "bio"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    validation = validate_run(result)
    result["validation"] = validation

    run_json = artifact_dir / "run.json"
    run_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (reports_dir / "petri_run_latest.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    density_packet = {
        "run_id": run_id,
        "preset": result.get("preset"),
        "grid": result.get("grid"),
        "density": result.get("fields", {}).get("density", []),
        "nutrient": result.get("fields", {}).get("nutrient", []),
        "toxin": result.get("fields", {}).get("toxin", []),
        "oxygen": result.get("fields", {}).get("oxygen", []),
        "waste": result.get("fields", {}).get("waste", []),
    }
    (artifact_dir / "density_latest.json").write_text(json.dumps(density_packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (reports_dir / "petri_density_latest.json").write_text(json.dumps(density_packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    pop_csv = artifact_dir / "population.csv"
    curves = result.get("population_curves", {})
    names = list(curves.keys())
    with pop_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["step"] + names + ["total"])
        total = result.get("population_total_curve", [])
        for idx in range(len(total)):
            writer.writerow([idx] + [curves[name][idx] for name in names] + [total[idx]])

    summary = [
        "# Petri Dish Pro Run Summary",
        "",
        f"- Run: `{run_id}`",
        f"- Preset: `{result.get('preset')}`",
        f"- Grid: `{result.get('grid')}`",
        f"- Steps: `{result.get('steps')}`",
        f"- Validation: `{validation.get('status')}`",
        "",
        "## Latest populations",
    ]
    for name, value in sorted(result.get("population_latest", {}).items()):
        summary.append(f"- `{name}`: {value}")
    summary.extend(["", "## Claim Boundary", "", result.get("claim_boundary", "")])
    summary_md = "\n".join(summary).rstrip() + "\n"
    (artifact_dir / "summary.md").write_text(summary_md, encoding="utf-8")
    (reports_dir / "petri_summary_latest.md").write_text(summary_md, encoding="utf-8")

    return {
        "artifact_dir": str(artifact_dir),
        "latest_run": str(reports_dir / "petri_run_latest.json"),
        "latest_density": str(reports_dir / "petri_density_latest.json"),
        "latest_summary": str(reports_dir / "petri_summary_latest.md"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Petri Dish Pro organism simulations.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--preset", default="microbial_competition", choices=["microbial_competition", "antibiotic_selection", "cellular_tissue_interaction"])
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--grid", type=int, default=48)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    result = run_simulation(preset=args.preset, steps=args.steps, grid=args.grid, seed=args.seed)
    artifacts = _write_artifacts(root, result)
    payload = {
        "status": result.get("validation", {}).get("status", "unknown"),
        "run_id": result.get("run_id"),
        "preset": args.preset,
        "artifacts": artifacts,
        "population_latest": result.get("population_latest", {}),
        "claim_boundary": result.get("claim_boundary"),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if not args.json:
        print(f"Petri Dish Pro run {payload['run_id']} status={payload['status']}")
        print(f"Latest report: {artifacts['latest_run']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
