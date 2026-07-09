
from __future__ import annotations

import datetime as dt
import math
import random
from typing import Any


def _grid(n: int, value: float = 0.0) -> list[list[float]]:
    return [[float(value) for _ in range(n)] for _ in range(n)]


def _diffuse(field: list[list[float]], rate: float) -> list[list[float]]:
    n = len(field)
    out = _grid(n)
    for y in range(n):
        ym = max(0, y - 1)
        yp = min(n - 1, y + 1)
        row = field[y]
        for x in range(n):
            xm = max(0, x - 1)
            xp = min(n - 1, x + 1)
            avg = (field[ym][x] + field[yp][x] + row[xm] + row[xp] + row[x]) / 5.0
            out[y][x] = max(0.0, row[x] * (1.0 - rate) + avg * rate)
    return out


def _seed_blob(n: int, rng: random.Random, center_x: float, center_y: float, radius: float, mass: float) -> list[list[float]]:
    g = _grid(n)
    for y in range(n):
        for x in range(n):
            dx = (x / max(1, n - 1)) - center_x
            dy = (y / max(1, n - 1)) - center_y
            d = math.sqrt(dx * dx + dy * dy)
            if d <= radius:
                noise = 0.70 + rng.random() * 0.60
                g[y][x] = mass * (1.0 - d / max(radius, 0.001)) * noise
    return g


def _organisms(preset: str) -> list[dict[str, Any]]:
    base = [
        {"id": "ecoli_like", "label": "E. coli-like fast grower", "growth": 0.105, "death": 0.010, "motility": 0.135, "toxin_sensitivity": 0.58, "nutrient_need": 0.70, "color": "cyan"},
        {"id": "bacillus_like", "label": "Bacillus-like resilient spore former", "growth": 0.070, "death": 0.007, "motility": 0.082, "toxin_sensitivity": 0.30, "nutrient_need": 0.52, "color": "gold"},
        {"id": "yeast_like", "label": "Yeast-like slow colony", "growth": 0.052, "death": 0.006, "motility": 0.035, "toxin_sensitivity": 0.22, "nutrient_need": 0.44, "color": "violet"},
        {"id": "predator_microbe", "label": "Predator microbe", "growth": 0.038, "death": 0.016, "motility": 0.155, "toxin_sensitivity": 0.38, "nutrient_need": 0.35, "predator": True, "color": "red"},
    ]
    if preset == "antibiotic_selection":
        base.append({"id": "resistant_variant", "label": "Antibiotic-resistant variant", "growth": 0.072, "death": 0.008, "motility": 0.105, "toxin_sensitivity": 0.075, "nutrient_need": 0.62, "color": "green"})
    if preset == "cellular_tissue_interaction":
        base = [
            {"id": "epithelial_like", "label": "Normal epithelial-like cells", "growth": 0.045, "death": 0.006, "motility": 0.025, "toxin_sensitivity": 0.18, "nutrient_need": 0.55, "color": "cyan"},
            {"id": "immune_like", "label": "Immune-like mobile cells", "growth": 0.030, "death": 0.010, "motility": 0.165, "toxin_sensitivity": 0.25, "nutrient_need": 0.50, "color": "green"},
            {"id": "cancer_like", "label": "Cancer-like overgrowth clone", "growth": 0.082, "death": 0.008, "motility": 0.055, "toxin_sensitivity": 0.20, "nutrient_need": 0.82, "color": "magenta"},
            {"id": "infected_like", "label": "Infected stressed cells", "growth": 0.040, "death": 0.020, "motility": 0.045, "toxin_sensitivity": 0.42, "nutrient_need": 0.68, "color": "amber"},
        ]
    return base


def run_simulation(preset: str = "microbial_competition", steps: int = 100, grid: int = 48, seed: int = 1337) -> dict[str, Any]:
    if grid < 16:
        grid = 16
    if grid > 96:
        grid = 96
    if steps < 1:
        steps = 1
    rng = random.Random(seed)
    organisms = _organisms(preset)

    nutrient = _grid(grid, 0.74)
    toxin = _grid(grid, 0.02)
    oxygen = _grid(grid, 0.82)
    waste = _grid(grid, 0.0)

    # spatial gradients and antibiotic front
    for y in range(grid):
        for x in range(grid):
            nx = x / max(1, grid - 1)
            ny = y / max(1, grid - 1)
            nutrient[y][x] = max(0.05, min(1.0, 0.90 - 0.28 * math.sqrt((nx - 0.5) ** 2 + (ny - 0.5) ** 2) + rng.uniform(-0.025, 0.025)))
            oxygen[y][x] = max(0.05, min(1.0, 0.96 - 0.36 * ny + rng.uniform(-0.015, 0.015)))
            if preset == "antibiotic_selection":
                toxin[y][x] = max(0.0, min(1.0, 0.10 + 0.82 * nx + rng.uniform(-0.025, 0.025)))
            if preset != "antibiotic_selection":
                toxin[y][x] = max(0.0, min(0.32, 0.03 + 0.11 * nx + rng.uniform(-0.010, 0.010)))

    species: dict[str, list[list[float]]] = {}
    centers = [(0.30, 0.33), (0.68, 0.34), (0.38, 0.70), (0.70, 0.68), (0.50, 0.50)]
    for idx, org in enumerate(organisms):
        cx, cy = centers[idx % len(centers)]
        species[org["id"]] = _seed_blob(grid, rng, cx, cy, 0.13, 0.20 if not org.get("predator") else 0.08)

    curves: dict[str, list[float]] = {org["id"]: [] for org in organisms}
    total_curve: list[float] = []

    for _step in range(steps):
        total_density = _grid(grid)
        for field in species.values():
            for y in range(grid):
                for x in range(grid):
                    total_density[y][x] += field[y][x]

        next_species: dict[str, list[list[float]]] = {}
        prey_total = _grid(grid)
        for org in organisms:
            if not org.get("predator"):
                field = species[org["id"]]
                for y in range(grid):
                    for x in range(grid):
                        prey_total[y][x] += field[y][x]

        for org in organisms:
            oid = org["id"]
            field = _diffuse(species[oid], org["motility"])
            out = _grid(grid)
            for y in range(grid):
                for x in range(grid):
                    density = field[y][x]
                    capacity_pressure = max(0.0, 1.0 - total_density[y][x] / 1.65)
                    nut = nutrient[y][x] / (nutrient[y][x] + org["nutrient_need"] + 1e-6)
                    oxy = oxygen[y][x] / (oxygen[y][x] + 0.32)
                    growth = org["growth"] * density * nut * oxy * capacity_pressure
                    death = (org["death"] + org["toxin_sensitivity"] * toxin[y][x] * 0.035 + waste[y][x] * 0.014) * density
                    pred_gain = 0.0
                    if org.get("predator"):
                        pred_gain = 0.055 * density * min(1.0, prey_total[y][x])
                    value = max(0.0, density + growth + pred_gain - death)
                    out[y][x] = min(1.9, value)
                    nutrient[y][x] = max(0.0, nutrient[y][x] - growth * 0.045 - density * 0.0004)
                    oxygen[y][x] = max(0.0, oxygen[y][x] - density * 0.00055)
                    waste[y][x] = min(1.0, waste[y][x] + max(0.0, death) * 0.020 + density * 0.00028)
            next_species[oid] = out
        species = next_species
        nutrient = _diffuse(nutrient, 0.045)
        toxin = _diffuse(toxin, 0.025)
        oxygen = _diffuse(oxygen, 0.065)
        waste = _diffuse(waste, 0.030)

        total_pop = 0.0
        for org in organisms:
            pop = sum(sum(row) for row in species[org["id"]])
            curves[org["id"]].append(round(pop, 6))
            total_pop += pop
        total_curve.append(round(total_pop, 6))

    density = _grid(grid)
    for field in species.values():
        for y in range(grid):
            for x in range(grid):
                density[y][x] += field[y][x]
    max_density = max(max(row) for row in density) or 1.0
    density_norm = [[round(v / max_density, 5) for v in row] for row in density]

    run_id = "petri_" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    return {
        "schema": "PETRI_DISH_PRO_RUN.v0.3.003C",
        "run_id": run_id,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "preset": preset,
        "steps": steps,
        "grid": grid,
        "seed": seed,
        "organisms": organisms,
        "population_curves": curves,
        "population_total_curve": total_curve,
        "population_latest": {k: v[-1] if v else 0.0 for k, v in curves.items()},
        "fields": {
            "density": density_norm,
            "nutrient": [[round(v, 5) for v in row] for row in nutrient],
            "toxin": [[round(v, 5) for v in row] for row in toxin],
            "oxygen": [[round(v, 5) for v in row] for row in oxygen],
            "waste": [[round(v, 5) for v in row] for row in waste],
        },
        "claim_boundary": "Educational/research simulation only. Not diagnostic, clinical, wet-lab, or safety proof.",
    }
