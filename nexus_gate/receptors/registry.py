from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ReceptorManifest:
    receptor_id: str
    owner_adapter_id: str
    surface_type: str
    accepted_schema_families: list[str]
    allowed_actions: list[str]
    requires_authority_for_actions: list[str]
    capability_bits: list[str]
    claim_boundary: str = "Receptor manifest is local compatibility evidence only."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReceptorRegistryEntry:
    manifest: ReceptorManifest
    registered_at_utc: str
    status: str = "registered"


class ReceptorRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, ReceptorRegistryEntry] = {}

    def register(self, manifest: ReceptorManifest) -> ReceptorRegistryEntry:
        self.validate_manifest(manifest)
        entry = ReceptorRegistryEntry(
            manifest=manifest,
            registered_at_utc=datetime.now(timezone.utc).isoformat(),
            status="registered",
        )
        self._entries[manifest.receptor_id] = entry
        return entry

    def get(self, receptor_id: str) -> ReceptorRegistryEntry | None:
        return self._entries.get(receptor_id)

    def list_manifests(self) -> list[ReceptorManifest]:
        return [entry.manifest for entry in self._entries.values()]

    @staticmethod
    def validate_manifest(manifest: ReceptorManifest) -> None:
        if not manifest.receptor_id:
            raise ValueError("receptor_id is required")
        if not manifest.owner_adapter_id:
            raise ValueError("owner_adapter_id is required")
        if not manifest.accepted_schema_families:
            raise ValueError("accepted_schema_families cannot be empty")
        if not manifest.allowed_actions:
            raise ValueError("allowed_actions cannot be empty")
        if "accept_statepacket" not in manifest.capability_bits:
            raise ValueError("capability_bits must include accept_statepacket")
        if "compatibility_check" not in manifest.capability_bits:
            raise ValueError("capability_bits must include compatibility_check")


def manifest_from_dict(data: dict[str, Any]) -> ReceptorManifest:
    return ReceptorManifest(**data)


def load_receptor_manifests(path: str | Path) -> list[ReceptorManifest]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "receptors" in data:
        return [manifest_from_dict(item) for item in data["receptors"]]
    if isinstance(data, list):
        return [manifest_from_dict(item) for item in data]
    if isinstance(data, dict):
        return [manifest_from_dict(data)]
    raise ValueError("Unsupported receptor manifest format")


def main() -> None:
    parser = argparse.ArgumentParser(description="NEXUS GATE receptor registry utility")
    parser.add_argument("--manifest", default="registry/receptors.local_demo.v0.1.8.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    registry = ReceptorRegistry()
    manifests = load_receptor_manifests(args.manifest)
    entries = [registry.register(manifest) for manifest in manifests]
    output = {
        "system": "NEXUS GATE",
        "version": "0.1.8-receptor-registry",
        "status": "pass",
        "registered": [entry.manifest.to_dict() for entry in entries],
        "claim_boundary": "Receptor registry utility is local validation evidence only.",
    }
    if args.json:
        print(json.dumps(output, indent=2))
    else:
        for entry in entries:
            print(f"Registered receptor: {entry.manifest.receptor_id}")


if __name__ == "__main__":
    main()
