from __future__ import annotations

import datetime as dt
import argparse
import json
import math
import random
from pathlib import Path
from typing import Any

SCHEMA = "PETRI_PARTICLE_STATE.v0.4m"


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return fallback


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _stable_seed(text: str) -> int:
    h = 2166136261
    for ch in str(text):
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h or 33


def _run_dir(root: Path, run_id: str) -> Path:
    return root / "artifacts" / "bio" / "runs" / run_id


def _latest_receipt(root: Path) -> dict[str, Any]:
    return _read_json(root / "reports" / "bio" / "petri_run_latest.json", {})


def _registry(root: Path) -> dict[str, Any]:
    return _read_json(root / "config" / "organisms.json", {"organisms": []})


def _fields(root: Path) -> dict[str, Any]:
    return _read_json(root / "config" / "field_profiles.json", {"fields": {}})


def _id_from_slug(slug: str, organisms: list[dict[str, Any]]) -> str:
    raw = str(slug or "")
    for org in organisms:
        if org.get("id") == raw:
            return raw
        if raw in org.get("legacy_slugs", []):
            return str(org.get("id"))
    return raw


def _population_map(receipt: dict[str, Any], registry: dict[str, Any]) -> dict[str, float]:
    organisms = list(registry.get("organisms", []))
    out: dict[str, float] = {}

    ts = receipt.get("timeseries") or receipt.get("population_curves") or receipt.get("curves") or []
    if isinstance(ts, list) and ts:
        last = ts[-1] if isinstance(ts[-1], dict) else {}
        pop = last.get("populations") or last.get("population") or {}
        if isinstance(pop, dict):
            for slug, value in pop.items():
                out[_id_from_slug(slug, organisms)] = float(value or 0)

    if isinstance(receipt.get("organisms"), list):
        for item in receipt["organisms"]:
            if not isinstance(item, dict):
                continue
            oid = _id_from_slug(item.get("slug") or item.get("id") or item.get("name"), organisms)
            val = item.get("population", item.get("final_population", item.get("value", item.get("count", 0))))
            out[oid] = float(val or out.get(oid, 0) or 0)

    for org in organisms:
        oid = str(org.get("id"))
        if org.get("enabled", True) and out.get(oid, 0) <= 0:
            out[oid] = float(org.get("baseline_population", 20) or 20)
    return out


def _state_for_cell(org: dict[str, Any], rng: random.Random) -> str:
    render = org.get("morphology", {}).get("render_type", "rod")
    behavior = org.get("behavior", {})
    if render == "rod_spore" and rng.random() < float(behavior.get("sporulation", 0.3)) * 0.22:
        return "spore"
    if render == "amoeboid" and rng.random() < float(behavior.get("encystment", 0.3)) * 0.16:
        return "cyst"
    if render == "budding_yeast" and rng.random() < float(behavior.get("budding", 0.5)) * 0.45:
        return "budding"
    return "active"


def generate_particle_state(root: str | Path = ".", run_id: str | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    receipt = _latest_receipt(root)
    registry = _registry(root)
    fields_cfg = _fields(root)
    organisms = [o for o in registry.get("organisms", []) if o.get("enabled", True)]
    run_id = run_id or str(receipt.get("run_id") or "petri_preview")
    out_dir = _run_dir(root, run_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    pop = _population_map(receipt, registry)
    seed = _stable_seed(run_id + json.dumps(sorted(pop.items())))
    rng = random.Random(seed)

    cells: list[dict[str, Any]] = []
    particles: list[dict[str, Any]] = []
    interactions: list[dict[str, Any]] = []

    total = max(1.0, sum(pop.get(str(o.get("id")), 0.0) for o in organisms))
    for idx, org in enumerate(organisms):
        oid = str(org.get("id"))
        value = float(pop.get(oid, org.get("baseline_population", 20) or 20))
        portion = max(0.025, value / total)
        count = max(8, min(360, int(round(225 * portion))))
        render = org.get("morphology", {}).get("render_type", "rod")
        behavior = org.get("behavior", {})
        cluster_angle = idx / max(1, len(organisms)) * math.tau - math.pi / 2
        cx = math.cos(cluster_angle) * 0.42
        cy = math.sin(cluster_angle) * 0.26
        cluster_r = 0.16 + 0.47 * math.sqrt(portion)
        for i in range(count):
            a = rng.random() * math.tau
            rr = (rng.random() ** 0.62) * cluster_r
            x = cx + math.cos(a) * rr + (rng.random() - 0.5) * 0.10
            y = cy + math.sin(a) * rr + (rng.random() - 0.5) * 0.08
            x = max(-1.28, min(1.28, x))
            y = max(-0.78, min(0.78, y))
            motility = float(behavior.get("motility", 0.3) or 0.3)
            vx = (rng.random() - 0.5) * 0.014 * max(0.1, motility)
            vy = (rng.random() - 0.5) * 0.014 * max(0.1, motility)
            state = _state_for_cell(org, rng)
            radius = {
                "rod": 0.012,
                "rod_spore": 0.013,
                "budding_yeast": 0.023,
                "amoeboid": 0.034,
                "coccus": 0.014,
            }.get(render, 0.014) * (0.85 + rng.random() * 0.65)
            cells.append({
                "id": f"{oid}_{i:04d}",
                "organism_id": oid,
                "label": org.get("label", oid),
                "x": round(x, 6),
                "y": round(y, 6),
                "vx": round(vx, 7),
                "vy": round(vy, 7),
                "angle": round(rng.random() * math.tau, 6),
                "phase": round(rng.random() * math.tau, 6),
                "radius": round(radius, 6),
                "morphology": render,
                "state": state,
                "color": org.get("color", "#27f4ff"),
                "behavior": {
                    "growth_rate": behavior.get("growth_rate", 0.5),
                    "motility": behavior.get("motility", 0.3),
                    "chemotaxis": behavior.get("chemotaxis", 0.0),
                    "predation": behavior.get("predation", 0.0),
                    "biofilm_bias": behavior.get("biofilm_bias", 0.0),
                },
                "source": org.get("dataset", {}).get("primary", "registry"),
            })

    for i in range(320):
        particles.append({
            "id": f"particle_{i:04d}",
            "x": round(rng.random() * 2.7 - 1.35, 6),
            "y": round(rng.random() * 1.6 - 0.8, 6),
            "z": round(rng.random(), 6),
            "vx": round((rng.random() - 0.5) * 0.03, 7),
            "vy": round((rng.random() - 0.5) * 0.03, 7),
            "type": "media_particle",
        })

    predators = [c for c in cells if c.get("morphology") == "amoeboid"]
    prey = [c for c in cells if c.get("morphology") != "amoeboid"]
    for p in predators[:40]:
        if not prey:
            break
        nearest = min(prey, key=lambda q: (q["x"] - p["x"]) ** 2 + (q["y"] - p["y"]) ** 2)
        interactions.append({
            "type": "predator_prey_proximity",
            "source": p["id"],
            "target": nearest["id"],
            "distance": round(math.hypot(nearest["x"] - p["x"], nearest["y"] - p["y"]), 6),
        })

    fields = {
        "schema": "PETRI_FIELDS_STATE.v0.4m",
        "run_id": run_id,
        "profiles": fields_cfg.get("fields", {}),
        "field_grid": {"space": "normalized_dish", "radius": 1.0, "note": "renderer clips to circular dish"},
    }

    state = {
        "schema": SCHEMA,
        "run_id": run_id,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "seed": seed,
        "counts": {"cells": len(cells), "particles": len(particles), "interactions": len(interactions)},
        "selected_default": [str(o.get("id")) for o in organisms],
        "claim_boundary": "Deterministic simulated spatial state. Not microscopy evidence, clinical evidence, species identification, treatment guidance, or biosafety evidence.",
        "files": {
            "cells": "cells.json",
            "particles": "particles.json",
            "interactions": "interactions.json",
            "fields": "fields.json",
        },
    }

    _write_json(out_dir / "cells.json", {"schema": SCHEMA, "run_id": run_id, "cells": cells})
    _write_json(out_dir / "particles.json", {"schema": SCHEMA, "run_id": run_id, "particles": particles})
    _write_json(out_dir / "interactions.json", {"schema": SCHEMA, "run_id": run_id, "interactions": interactions})
    _write_json(out_dir / "fields.json", fields)
    _write_json(out_dir / "particle_state_index.json", state)

    reports = root / "reports" / "bio"
    reports.mkdir(parents=True, exist_ok=True)
    _write_json(reports / "petri_particle_state_latest.json", {**state, "run_dir": str(out_dir)})
    return {"run_id": run_id, "run_dir": str(out_dir), "state": state}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Petri Dish Pro particle-state artifacts.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args(argv)
    result = generate_particle_state(args.root, args.run_id)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
