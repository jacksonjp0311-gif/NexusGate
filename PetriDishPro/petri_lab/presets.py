from __future__ import annotations
from copy import deepcopy
from typing import Any

def organism(oid: str, name: str, kind: str, growth_rate: float, death_rate: float, motility: float, nutrient_affinity: float, toxin_sensitivity: float, oxygen_dependence: float, waste_sensitivity: float, resistance: float=0.0, predation: float=0.0, prey: list[str]|None=None, color: str="#00e5ff", seed_mass: float=0.08) -> dict[str, Any]:
    return {"id": oid, "name": name, "kind": kind, "growth_rate": growth_rate, "death_rate": death_rate, "motility": motility, "nutrient_affinity": nutrient_affinity, "toxin_sensitivity": toxin_sensitivity, "oxygen_dependence": oxygen_dependence, "waste_sensitivity": waste_sensitivity, "resistance": resistance, "predation": predation, "prey": prey or [], "color": color, "seed_mass": seed_mass}

PRESETS = {
    "microbial_competition": {"title":"Microbial Competition Culture", "description":"Fast grower, yeast-like slow grower, spore former, and predator-like consumer compete over nutrient and oxygen fields.", "seed":2203, "field_mode":"soft_gradient", "organisms":[
        organism("ecoli_like","E. coli-like Fast Grower","bacteria",0.115,0.010,0.145,0.20,0.35,0.12,0.08,color="#00f0ff",seed_mass=0.075),
        organism("yeast_like","Yeast-like Slow Grower","fungal",0.066,0.007,0.050,0.28,0.18,0.18,0.06,color="#ffd166",seed_mass=0.070),
        organism("bacillus_like","Bacillus-like Spore Former","bacteria",0.079,0.005,0.070,0.23,0.22,0.14,0.03,resistance=0.25,color="#7cff6b",seed_mass=0.065),
        organism("predator_like","Predator Microbe","predator",0.035,0.012,0.120,0.34,0.30,0.15,0.08,predation=0.020,prey=["ecoli_like","yeast_like"],color="#ff4fd8",seed_mass=0.040)]},
    "antibiotic_selection": {"title":"Antibiotic Selection Pressure", "description":"Sensitive and resistant bacterial variants compete under a toxin pulse and spatial gradient.", "seed":3119, "field_mode":"antibiotic_gradient", "organisms":[
        organism("sensitive_variant","Sensitive Variant","bacteria",0.120,0.009,0.120,0.20,0.92,0.12,0.06,color="#00f0ff",seed_mass=0.10),
        organism("resistant_variant","Resistant Variant","bacteria",0.084,0.011,0.100,0.22,0.78,0.14,0.07,resistance=0.78,color="#ffcc00",seed_mass=0.030),
        organism("neutral_colony","Neutral Background Colony","control",0.050,0.009,0.045,0.26,0.35,0.18,0.05,resistance=0.2,color="#8aa4ff",seed_mass=0.030)]},
    "cellular_tissue": {"title":"Cellular Tissue Interaction", "description":"Epithelial-like cells, immune-like patrol cells, cancer-like proliferators, and infected cells interact through oxygen and waste stress.", "seed":4407, "field_mode":"tissue_oxygen", "organisms":[
        organism("epithelial_like","Normal Epithelial-like Cells","mammalian_cell",0.052,0.005,0.030,0.30,0.10,0.42,0.05,color="#4cc9f0",seed_mass=0.105),
        organism("immune_like","Immune-like Patrol Cells","immune_cell",0.030,0.008,0.165,0.38,0.18,0.28,0.06,predation=0.015,prey=["infected_like","cancer_like"],color="#ffffff",seed_mass=0.035),
        organism("cancer_like","Cancer-like Proliferator","mammalian_cell",0.090,0.007,0.050,0.24,0.20,0.25,0.03,resistance=0.35,color="#ff3366",seed_mass=0.050),
        organism("infected_like","Infected Cell-like State","infected_cell",0.064,0.010,0.040,0.30,0.30,0.32,0.08,color="#b86bff",seed_mass=0.035)]},
    "biofilm_dormancy": {"title":"Biofilm and Dormancy Prototype", "description":"Matrix former, planktonic cells, dormant spores, and phage-like predator form a coarse culture ecology.", "seed":5201, "field_mode":"biofilm", "organisms":[
        organism("matrix_former","Biofilm Matrix Former","bacteria",0.082,0.006,0.035,0.21,0.28,0.13,0.025,resistance=0.34,color="#2effa3",seed_mass=0.080),
        organism("planktonic","Planktonic Motile Cells","bacteria",0.105,0.011,0.170,0.21,0.45,0.14,0.07,color="#00e5ff",seed_mass=0.070),
        organism("dormant_spore","Dormant Spore-like Reserve","spore",0.040,0.002,0.018,0.30,0.16,0.10,0.01,resistance=0.60,color="#ffee77",seed_mass=0.060),
        organism("phage_like","Phage-like Predator Proxy","predator",0.028,0.018,0.190,0.40,0.40,0.12,0.03,predation=0.030,prey=["planktonic","matrix_former"],color="#ff4fd8",seed_mass=0.035)]},
}

def get_preset(name: str) -> dict[str, Any]:
    if name not in PRESETS:
        raise KeyError(f"Unknown preset {name!r}. Valid: {', '.join(sorted(PRESETS))}")
    item = deepcopy(PRESETS[name])
    item["preset"] = name
    return item

def list_presets() -> list[str]:
    return sorted(PRESETS)
