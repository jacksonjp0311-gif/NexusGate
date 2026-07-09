from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional


@dataclass
class OrganismSpec:
    id: str
    label: str
    kind: str = "microbe"
    initial_cells: float = 25.0
    growth_rate: float = 0.06
    death_rate: float = 0.004
    motility: float = 0.05
    nutrient_affinity: float = 0.45
    oxygen_affinity: float = 0.25
    toxin_sensitivity: float = 0.2
    waste_sensitivity: float = 0.05
    resistance: float = 0.0
    carrying_capacity_share: float = 1.0
    produces_toxin: float = 0.0
    consumes_prey: bool = False
    prey_ids: List[str] = field(default_factory=list)
    predation_rate: float = 0.0
    color: str = "#00f0ff"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FieldSpec:
    nutrient_level: float = 1.0
    oxygen_level: float = 0.9
    toxin_level: float = 0.0
    waste_level: float = 0.0
    nutrient_hotspots: int = 4
    toxin_spots: int = 1
    edge_antibiotic_gradient: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExperimentSpec:
    id: str
    name: str
    description: str
    preset: str = "custom"
    grid_size: int = 72
    steps: int = 180
    sample_every: int = 1
    seed: int = 1337
    carrying_capacity: float = 28.0
    diffusion_rate: float = 0.08
    nutrient_diffusion: float = 0.03
    toxin_diffusion: float = 0.025
    organisms: List[OrganismSpec] = field(default_factory=list)
    fields: FieldSpec = field(default_factory=FieldSpec)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["organisms"] = [o.to_dict() for o in self.organisms]
        data["fields"] = self.fields.to_dict()
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExperimentSpec":
        organisms = [OrganismSpec(**item) for item in data.get("organisms", [])]
        fields_data = data.get("fields", {}) or {}
        fields = FieldSpec(**fields_data)
        kwargs = dict(data)
        kwargs["organisms"] = organisms
        kwargs["fields"] = fields
        return ExperimentSpec(**kwargs)
