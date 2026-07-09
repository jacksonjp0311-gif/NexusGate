from __future__ import annotations
import csv, datetime as dt, json, math, random
from pathlib import Path
from typing import Any
from .presets import get_preset
from .validation import validate_run

def clamp(v: float, lo: float=0.0, hi: float=1.0) -> float: return lo if v < lo else hi if v > hi else v
def empty(n: int, v: float=0.0) -> list[list[float]]: return [[v for _ in range(n)] for _ in range(n)]
def diffuse(g: list[list[float]], rate: float) -> list[list[float]]:
    if rate <= 0: return [r[:] for r in g]
    n, out, stay, share = len(g), empty(len(g)), max(0, 1-rate), rate/4
    for y in range(n):
        ym, yp = max(0,y-1), min(n-1,y+1)
        for x in range(n):
            xm, xp = max(0,x-1), min(n-1,x+1)
            out[y][x] = g[y][x]*stay + (g[ym][x]+g[yp][x]+g[y][xm]+g[y][xp])*share
    return out

def rgrid(g): return [[round(clamp(v,0,9),5) for v in row] for row in g]
def sumg(g): return sum(sum(r) for r in g)
def maxg(g): return max(max(r) for r in g) if g else 0.0

def fields(n: int, rng: random.Random, mode: str):
    nutrient, oxygen, toxin, waste = empty(n), empty(n), empty(n), empty(n)
    c, s = (n-1)/2, max(1,n/2)
    for y in range(n):
        for x in range(n):
            radial = math.sqrt(((x-c)/s)**2 + ((y-c)/s)**2)
            nutrient[y][x] = clamp(0.82 - 0.22*radial + rng.uniform(-.035,.035), .05, 1)
            oxygen[y][x] = clamp(0.78 - 0.12*radial + rng.uniform(-.025,.025), .08, 1)
            toxin[y][x] = 0.02
            if mode == "antibiotic_gradient": toxin[y][x] = clamp(0.08 + 0.62*(x/max(1,n-1)) + rng.uniform(-.025,.025),0,1)
            if mode == "tissue_oxygen": oxygen[y][x] = clamp(0.96 - 0.34*radial + rng.uniform(-.015,.015), .05, 1); toxin[y][x] = .01
            if mode == "biofilm": nutrient[y][x] = clamp(0.72 - 0.12*radial + 0.16*math.sin(x/6)*math.cos(y/7), .05, 1); toxin[y][x] = clamp(.04 + .12*radial,0,.55)
    return {"nutrient": nutrient, "oxygen": oxygen, "toxin": toxin, "waste": waste}

def seed_orgs(n, organisms, rng):
    out, cx, cy, rad = {}, (n-1)/2, (n-1)/2, max(3,n*.24)
    for idx, org in enumerate(organisms):
        g, angle, spread, mass = empty(n), (idx/max(1,len(organisms)))*math.tau+rng.uniform(-.15,.15), max(2,int(n*.055)), float(org.get("seed_mass",.06))
        sx, sy = int(clamp((cx+math.cos(angle)*rad)/max(1,n-1))*(n-1)), int(clamp((cy+math.sin(angle)*rad)/max(1,n-1))*(n-1))
        for y in range(max(0,sy-spread), min(n,sy+spread+1)):
            for x in range(max(0,sx-spread), min(n,sx+spread+1)):
                d = math.sqrt((x-sx)**2+(y-sy)**2)/max(1,spread)
                if d <= 1.35: g[y][x] = max(g[y][x], mass*math.exp(-(d*d)*1.6)+rng.uniform(0,.004))
        out[org["id"]] = g
    return out

def combine(densities):
    first = next(iter(densities.values())); n = len(first); out = empty(n)
    for g in densities.values():
        for y in range(n):
            for x in range(n): out[y][x] += g[y][x]
    return out

def run_experiment(root: str|Path, preset_name="microbial_competition", steps=90, grid_size=56, seed: int|None=None) -> dict[str, Any]:
    root = Path(root).resolve(); preset = get_preset(preset_name); rng = random.Random(seed if seed is not None else preset.get("seed",1234))
    n, steps = max(12,min(int(grid_size),96)), max(1,min(int(steps),400)); organisms = preset["organisms"]
    f, densities, ts, cap = fields(n,rng,preset.get("field_mode","soft_gradient")), seed_orgs(n,organisms,rng), [], 1.15
    for step in range(steps+1):
        total = combine(densities); pops = {oid: sumg(g) for oid,g in densities.items()}
        ts.append({"step":step,"populations":{k:round(v,6) for k,v in pops.items()},"total_density":round(sum(pops.values()),6),"mean_nutrient":round(sumg(f["nutrient"])/(n*n),6),"mean_oxygen":round(sumg(f["oxygen"])/(n*n),6),"mean_toxin":round(sumg(f["toxin"])/(n*n),6),"mean_waste":round(sumg(f["waste"])/(n*n),6)})
        if step == steps: break
        old = {oid: diffuse(g, float(next(o for o in organisms if o["id"]==oid).get("motility",.05))) for oid,g in densities.items()}
        nxt, growth, death, before = {oid: empty(n) for oid in old}, empty(n), empty(n), combine(old)
        for org in organisms:
            oid, src, dst = org["id"], old[org["id"]], nxt[org["id"]]
            for y in range(n):
                for x in range(n):
                    d = src[y][x]; nut=f["nutrient"][y][x]; oxy=f["oxygen"][y][x]; tox=f["toxin"][y][x]; waste=f["waste"][y][x]
                    ge = d*org["growth_rate"]*(nut/(nut+org["nutrient_affinity"]))*(oxy/(oxy+org["oxygen_dependence"]))*max(0,1-before[y][x]/cap)
                    de = d*(org["death_rate"] + org["toxin_sensitivity"]*(1-org.get("resistance",0))*tox*.075 + org["waste_sensitivity"]*waste*.05)
                    dst[y][x] = min(cap, max(0, d+ge-de)); growth[y][x] += max(0,ge); death[y][x] += max(0,de)
        for org in organisms:
            if org.get("predation",0) <= 0: continue
            pg = nxt[org["id"]]
            for prey_id in [p for p in org.get("prey",[]) if p in nxt]:
                prey = nxt[prey_id]
                for y in range(n):
                    for x in range(n):
                        eaten = min(prey[y][x], org["predation"]*pg[y][x]*prey[y][x]/(.05+prey[y][x]+pg[y][x]))
                        prey[y][x] -= eaten; pg[y][x] = min(cap, pg[y][x]+eaten*.38)
        for k, rate in [("nutrient",.035),("oxygen",.055),("toxin",.02),("waste",.03)]: f[k] = diffuse(f[k], rate)
        for y in range(n):
            for x in range(n):
                f["nutrient"][y][x] = clamp(f["nutrient"][y][x]-growth[y][x]*.045+.0015)
                f["oxygen"][y][x] = clamp(f["oxygen"][y][x]-growth[y][x]*.030+.0020)
                f["waste"][y][x] = clamp(f["waste"][y][x]+death[y][x]*.080+before[y][x]*.0008)
                f["toxin"][y][x] = clamp(f["toxin"][y][x]*.996)
                if preset.get("field_mode") == "antibiotic_gradient" and int(steps*.25) <= step <= int(steps*.70): f["toxin"][y][x] = clamp(f["toxin"][y][x]+.004*(x/max(1,n-1)))
        densities = nxt
    final_density, final_pop = combine(densities), {oid: round(sumg(g),6) for oid,g in densities.items()}
    dominant = max(final_pop.items(), key=lambda kv: kv[1])[0] if final_pop else None
    run_id = f"petri_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{preset_name}"
    result = {"schema":"PETRI_DISH_PRO_RUN.v0.3","run_id":run_id,"generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"preset":preset_name,"title":preset.get("title",preset_name),"description":preset.get("description",""),"claim_level":"educational_research_simulation_only","claim_boundary":"Exploratory model output only. Not clinical, diagnostic, treatment, wet-lab, biosafety, or regulatory evidence.","grid":{"size":n,"steps":steps,"seed":seed if seed is not None else preset.get("seed",1234)},"organisms":organisms,"timeseries":ts,"final_population":final_pop,"dominant_organism":dominant,"fields":{"density":rgrid(final_density),"nutrient":rgrid(f["nutrient"]),"oxygen":rgrid(f["oxygen"]),"toxin":rgrid(f["toxin"]),"waste":rgrid(f["waste"]),"organism_density":{oid:rgrid(g) for oid,g in densities.items()}},"metrics":{"max_density":round(maxg(final_density),6),"total_population":round(sum(final_pop.values()),6),"mean_nutrient_final":round(sumg(f["nutrient"])/(n*n),6),"mean_oxygen_final":round(sumg(f["oxygen"])/(n*n),6),"mean_toxin_final":round(sumg(f["toxin"])/(n*n),6),"mean_waste_final":round(sumg(f["waste"])/(n*n),6)}}
    result["validation"] = validate_run(result); write_artifacts(root, result); return result

def write_artifacts(root: Path, result: dict[str, Any]):
    reports = root/"reports"/"bio"; reports.mkdir(parents=True, exist_ok=True); run_dir = root/"artifacts"/"bio"/"runs"/result["run_id"]; run_dir.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(result, indent=2, sort_keys=True)+"\n"; (reports/"petri_run_latest.json").write_text(txt, encoding="utf-8"); (run_dir/"run.json").write_text(txt, encoding="utf-8")
    density = {"run_id":result["run_id"],"preset":result["preset"],"grid":result["grid"],"organisms":[{"id":o["id"],"name":o["name"],"color":o.get("color","#00e5ff")} for o in result["organisms"]],"fields":result["fields"]}
    dtxt=json.dumps(density, indent=2, sort_keys=True)+"\n"; (reports/"petri_density_latest.json").write_text(dtxt,encoding="utf-8"); (run_dir/"density.json").write_text(dtxt,encoding="utf-8")
    (run_dir/"validation.json").write_text(json.dumps(result["validation"], indent=2, sort_keys=True)+"\n", encoding="utf-8")
    ids=[o["id"] for o in result["organisms"]]
    with (run_dir/"population.csv").open("w", encoding="utf-8", newline="") as fh:
        w=csv.writer(fh); w.writerow(["step","total_density","mean_nutrient","mean_oxygen","mean_toxin","mean_waste",*ids])
        for row in result["timeseries"]: w.writerow([row["step"],row["total_density"],row["mean_nutrient"],row["mean_oxygen"],row["mean_toxin"],row["mean_waste"],*[row["populations"].get(i,0) for i in ids]])
    summary = f"# Petri Dish Pro Run: {result['title']}\n\n- Run ID: `{result['run_id']}`\n- Preset: `{result['preset']}`\n- Dominant organism: `{result['dominant_organism']}`\n- Validation: `{result['validation']['status']}`\n\n## Claim Boundary\n{result['claim_boundary']}\n\n## Final Population\n" + "\n".join([f"- `{k}`: {v}" for k,v in result["final_population"].items()]) + "\n"
    (reports/"petri_summary_latest.md").write_text(summary, encoding="utf-8"); (run_dir/"summary.md").write_text(summary, encoding="utf-8")
