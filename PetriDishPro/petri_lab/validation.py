from __future__ import annotations

import math
from typing import Any

CLAIM_BOUNDARY = "Simulation artifacts are exploratory model outputs only. Not clinical, diagnostic, treatment, wet-lab, biosafety, public-health, or regulatory evidence."


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _as_int(value: Any, default: int = 0) -> int:
    try:
        if isinstance(value, bool):
            return default
        if isinstance(value, (int, float, str)):
            return int(float(value))
    except Exception:
        return default
    return default


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, bool):
            return default
        if isinstance(value, (int, float, str)) and math.isfinite(float(value)):
            return float(value)
    except Exception:
        return default
    return default


def _density_from_result(result: dict[str, Any]) -> Any:
    fields = result.get("fields")
    if isinstance(fields, dict) and isinstance(fields.get("density"), list):
        return fields.get("density")
    density = result.get("density")
    if isinstance(density, dict):
        if isinstance(density.get("normalized"), list):
            return density.get("normalized")
        if isinstance(density.get("raw_downsampled"), list):
            return density.get("raw_downsampled")
        if isinstance(density.get("raw"), list):
            return density.get("raw")
    if isinstance(density, list):
        return density
    return None


def _grid_size_from_result(result: dict[str, Any], density: Any = None) -> int:
    raw = result.get("grid", result.get("grid_size", result.get("size", 0)))
    if isinstance(raw, dict):
        for key in ("size", "grid_size", "grid", "n", "width", "height", "rows", "cols", "columns"):
            value = _as_int(raw.get(key), 0)
            if value > 0:
                return value
    value = _as_int(raw, 0)
    if value > 0:
        return value
    metrics = result.get("metrics")
    if isinstance(metrics, dict):
        for key in ("grid_size", "grid", "size"):
            value = _as_int(metrics.get(key), 0)
            if value > 0:
                return value
    if isinstance(density, list) and density:
        return len(density)
    return 0


def _steps_from_result(result: dict[str, Any]) -> int:
    value = _as_int(result.get("steps", 0), 0)
    if value > 0:
        return value
    grid = result.get("grid")
    if isinstance(grid, dict):
        for key in ("steps", "step_count", "iterations"):
            value = _as_int(grid.get(key), 0)
            if value > 0:
                return value
    metrics = result.get("metrics")
    if isinstance(metrics, dict):
        for key in ("steps", "step_count", "iterations"):
            value = _as_int(metrics.get(key), 0)
            if value > 0:
                return value
    timeseries = result.get("timeseries")
    if isinstance(timeseries, list) and timeseries:
        return max(1, len(timeseries) - 1)
    curves = _curves_from_result(result)
    if isinstance(curves, dict) and curves:
        lengths = [len(v) for v in curves.values() if isinstance(v, list)]
        if lengths:
            return max(lengths)
    return 0


def _curves_from_result(result: dict[str, Any]) -> Any:
    curves = result.get("population_curves")
    if isinstance(curves, dict) and curves:
        return curves
    curves = result.get("curves")
    if isinstance(curves, dict) and curves:
        return curves
    converted: dict[str, list[float]] = {}
    skip = {"step", "t", "time", "total_density", "nutrient_total", "toxin_total", "waste_total", "oxygen_total", "mean_nutrient", "mean_oxygen", "mean_toxin", "mean_waste"}
    row_source = curves
    if not isinstance(row_source, list):
        row_source = result.get("timeseries")
    if isinstance(row_source, list):
        for row in row_source:
            if not isinstance(row, dict):
                continue
            nested = row.get("populations")
            if isinstance(nested, dict):
                for key, value in nested.items():
                    if _finite_number(value):
                        converted.setdefault(str(key), []).append(float(value))
            for key, value in row.items():
                if key in skip or key == "populations":
                    continue
                if _finite_number(value):
                    converted.setdefault(str(key), []).append(float(value))
    if converted:
        return converted
    return curves


def _organism_count(result: dict[str, Any], curves: Any) -> int:
    organisms = result.get("organisms")
    if isinstance(organisms, list) and organisms:
        return len(organisms)
    if isinstance(organisms, dict) and organisms:
        return len(organisms)
    final_pop = result.get("final_population")
    if isinstance(final_pop, dict) and final_pop:
        return len(final_pop)
    metrics = result.get("metrics")
    if isinstance(metrics, dict):
        value = _as_int(metrics.get("organism_count", 0), 0)
        if value > 0:
            return value
    if isinstance(curves, dict) and curves:
        return len(curves)
    return 0


def _final_total(result: dict[str, Any], curves: Any) -> float:
    metrics = result.get("metrics")
    if isinstance(metrics, dict):
        for key in ("total_population", "final_total_population", "final_population"):
            value = metrics.get(key)
            if _finite_number(value):
                return float(value)
    final_pop = result.get("final_population")
    if isinstance(final_pop, dict):
        vals = [_as_float(v, 0.0) for v in final_pop.values() if _finite_number(v)]
        if vals:
            return float(sum(vals))
    latest = result.get("population_latest")
    if isinstance(latest, dict):
        vals = [_as_float(v, 0.0) for v in latest.values() if _finite_number(v)]
        if vals:
            return float(sum(vals))
    if isinstance(curves, dict):
        total = 0.0
        seen = False
        for curve in curves.values():
            if isinstance(curve, list) and curve:
                value = curve[-1]
                if _finite_number(value):
                    total += float(value)
                    seen = True
        if seen:
            return total
    density = _density_from_result(result)
    if isinstance(density, list):
        flat = []
        for row in density:
            if isinstance(row, list):
                flat.extend([float(v) for v in row if _finite_number(v)])
        if flat:
            return float(sum(flat))
    return 0.0


def validate_run(result: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []

    if not isinstance(result, dict):
        return {"status": "fail", "passed": False, "failures": ["result is not a dictionary"], "errors": ["result is not a dictionary"], "warnings": [], "claim_boundary": CLAIM_BOUNDARY}

    density = _density_from_result(result)
    curves = _curves_from_result(result)
    grid = _grid_size_from_result(result, density)
    steps = _steps_from_result(result)
    organism_count = _organism_count(result, curves)
    final_total = _final_total(result, curves)

    claim_level = result.get("claim_level")
    if claim_level is not None and claim_level != "educational_research_simulation_only":
        failures.append("claim_level must stay educational_research_simulation_only")

    claim = str(result.get("claim_boundary", CLAIM_BOUNDARY))
    claim_lower = claim.lower()
    if "clinical" not in claim_lower or "diagnostic" not in claim_lower:
        warnings.append("claim boundary should explicitly block clinical and diagnostic use")

    if grid <= 0:
        failures.append("grid size could not be determined")
    if 0 < grid < 8:
        failures.append("grid too small")
    if 0 < grid < 16:
        warnings.append("grid below recommended visual microscope size of 16")
    if steps < 1:
        failures.append("steps must be positive")
    if organism_count <= 0:
        failures.append("no organisms defined")
    if not _finite_number(final_total):
        failures.append("final population is not finite")
    if _finite_number(final_total) and final_total < 0:
        failures.append("final population is negative")

    if not isinstance(curves, dict) or not curves:
        failures.append("population curves missing")
    if isinstance(curves, dict):
        for name, curve in curves.items():
            if not isinstance(curve, list) or not curve:
                failures.append(f"population curve missing for {name}")
                continue
            for value in curve:
                if (not _finite_number(value)) or float(value) < -1e-9:
                    failures.append(f"population curve has invalid values for {name}")
                    break

    if not isinstance(density, list) or not density:
        failures.append("density field missing")
    if isinstance(density, list) and density:
        flat: list[float] = []
        for row in density:
            if not isinstance(row, list):
                failures.append("density field contains non-row value")
                continue
            for value in row:
                if not _finite_number(value):
                    failures.append("density field contains non-numeric values")
                    break
                flat.append(float(value))
        if not flat:
            failures.append("density field empty")
        if flat and max(flat) <= 0:
            failures.append("density field contains no organisms")
        if flat and any(value < -1e-9 for value in flat):
            failures.append("density field contains negative values")

    # Legacy field-surface contract: if fields exists, these should be visible.
    fields = result.get("fields")
    if isinstance(fields, dict):
        for name in ["nutrient", "oxygen", "toxin", "waste"]:
            if name not in fields:
                warnings.append(f"missing field {name}")

    status = "pass" if not failures else "fail"
    return {
        "status": status,
        "passed": status == "pass",
        "failures": failures,
        "errors": list(failures),
        "warnings": warnings,
        "claim_boundary": CLAIM_BOUNDARY,
        "permitted_use": ["education", "exploratory simulation", "UI prototyping", "architecture testing"],
        "not_permitted_use": ["clinical diagnosis", "drug efficacy prediction", "wet-lab proof", "patient-specific recommendation", "public-health forecast"],
        "checks": {
            "claim_level_locked": claim_level in (None, "educational_research_simulation_only"),
            "grid": grid,
            "steps": steps,
            "organism_count": organism_count,
            "curve_count": len(curves) if isinstance(curves, dict) else 0,
            "has_density": isinstance(density, list) and bool(density),
            "final_total_population": round(float(final_total), 6) if _finite_number(final_total) else None,
        },
    }


def validate_result(result: dict[str, Any]) -> dict[str, Any]:
    return validate_run(result)
