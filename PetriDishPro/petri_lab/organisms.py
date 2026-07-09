from __future__ import annotations

from .schemas import OrganismSpec


def ecoli_like() -> OrganismSpec:
    return OrganismSpec(
        id="fast_microbe",
        label="Fast Microbe",
        kind="microbe",
        initial_cells=44,
        growth_rate=0.092,
        death_rate=0.004,
        motility=0.075,
        nutrient_affinity=0.32,
        oxygen_affinity=0.30,
        toxin_sensitivity=0.55,
        waste_sensitivity=0.08,
        resistance=0.05,
        color="#00f0ff",
        notes="Fast nutrient-responsive bacterial-like population; exploratory only.",
    )


def bacillus_like() -> OrganismSpec:
    return OrganismSpec(
        id="spore_former",
        label="Spore Former",
        kind="microbe",
        initial_cells=28,
        growth_rate=0.052,
        death_rate=0.002,
        motility=0.040,
        nutrient_affinity=0.50,
        oxygen_affinity=0.28,
        toxin_sensitivity=0.25,
        waste_sensitivity=0.05,
        resistance=0.35,
        color="#ffaa00",
        notes="Stress-tolerant spore-former style preset; not a strain model.",
    )


def yeast_like() -> OrganismSpec:
    return OrganismSpec(
        id="yeast_colony",
        label="Yeast-like Colony",
        kind="microbe",
        initial_cells=18,
        growth_rate=0.038,
        death_rate=0.003,
        motility=0.018,
        nutrient_affinity=0.42,
        oxygen_affinity=0.50,
        toxin_sensitivity=0.20,
        waste_sensitivity=0.09,
        resistance=0.20,
        carrying_capacity_share=1.25,
        color="#cc88ff",
        notes="Slow colony-forming eukaryote-like preset.",
    )


def predator_microbe() -> OrganismSpec:
    return OrganismSpec(
        id="predator_microbe",
        label="Predator Microbe",
        kind="predator",
        initial_cells=12,
        growth_rate=0.018,
        death_rate=0.006,
        motility=0.095,
        nutrient_affinity=0.80,
        oxygen_affinity=0.35,
        toxin_sensitivity=0.25,
        waste_sensitivity=0.06,
        resistance=0.15,
        consumes_prey=True,
        prey_ids=["fast_microbe", "yeast_colony"],
        predation_rate=0.045,
        color="#ff2bd6",
        notes="Toy predator population that consumes selected prey biomass.",
    )


def resistant_variant() -> OrganismSpec:
    return OrganismSpec(
        id="resistant_variant",
        label="Resistant Variant",
        kind="microbe",
        initial_cells=16,
        growth_rate=0.047,
        death_rate=0.004,
        motility=0.052,
        nutrient_affinity=0.45,
        oxygen_affinity=0.26,
        toxin_sensitivity=0.12,
        waste_sensitivity=0.07,
        resistance=0.82,
        produces_toxin=0.0015,
        color="#59ff6b",
        notes="Antibiotic-resistant style clone; simplified selection dynamics only.",
    )


def immune_like_cell() -> OrganismSpec:
    return OrganismSpec(
        id="immune_like",
        label="Immune-like Cell",
        kind="cell",
        initial_cells=20,
        growth_rate=0.020,
        death_rate=0.004,
        motility=0.070,
        nutrient_affinity=0.62,
        oxygen_affinity=0.50,
        toxin_sensitivity=0.20,
        waste_sensitivity=0.05,
        consumes_prey=True,
        prey_ids=["infected_cell", "cancer_like"],
        predation_rate=0.030,
        color="#88ccff",
        notes="Immune-effector-like toy agent.",
    )


def cancer_like_cell() -> OrganismSpec:
    return OrganismSpec(
        id="cancer_like",
        label="Cancer-like Clone",
        kind="cell",
        initial_cells=20,
        growth_rate=0.068,
        death_rate=0.003,
        motility=0.045,
        nutrient_affinity=0.28,
        oxygen_affinity=0.18,
        toxin_sensitivity=0.35,
        waste_sensitivity=0.03,
        resistance=0.30,
        carrying_capacity_share=1.50,
        color="#ff4b4b",
        notes="Aggressive proliferative clone toy model; not oncology validation.",
    )


def infected_cell() -> OrganismSpec:
    return OrganismSpec(
        id="infected_cell",
        label="Infected Cell",
        kind="cell",
        initial_cells=14,
        growth_rate=0.045,
        death_rate=0.006,
        motility=0.025,
        nutrient_affinity=0.52,
        oxygen_affinity=0.44,
        toxin_sensitivity=0.25,
        waste_sensitivity=0.07,
        produces_toxin=0.001,
        color="#ff8844",
        notes="Infected phenotype-like toy agent.",
    )


ORGANISM_LIBRARY = {
    "fast_microbe": ecoli_like,
    "spore_former": bacillus_like,
    "yeast_colony": yeast_like,
    "predator_microbe": predator_microbe,
    "resistant_variant": resistant_variant,
    "immune_like": immune_like_cell,
    "cancer_like": cancer_like_cell,
    "infected_cell": infected_cell,
}
