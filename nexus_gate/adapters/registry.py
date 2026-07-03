from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AdapterManifest:
    adapter_id: str
    framework_name: str
    adapter_version: str
    supported_event_types: list[str]
    supported_action_classes: list[str]
    supports_shadow: bool
    supports_trace_export: bool
    supports_replay: bool
    capability_bits: list[str]
    claim_boundary: str = "Adapter manifest is local compatibility evidence only."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdapterRegistryEntry:
    manifest: AdapterManifest
    registered_at_utc: str
    status: str = "registered"


class AdapterRegistry:
    """In-memory adapter registry for local NEXUS GATE validation."""

    def __init__(self) -> None:
        self._entries: dict[str, AdapterRegistryEntry] = {}

    def register(self, manifest: AdapterManifest) -> AdapterRegistryEntry:
        self.validate_manifest(manifest)
        entry = AdapterRegistryEntry(
            manifest=manifest,
            registered_at_utc=datetime.now(timezone.utc).isoformat(),
            status="registered",
        )
        self._entries[manifest.adapter_id] = entry
        return entry

    def get(self, adapter_id: str) -> AdapterRegistryEntry | None:
        return self._entries.get(adapter_id)

    def list_manifests(self) -> list[AdapterManifest]:
        return [entry.manifest for entry in self._entries.values()]

    @staticmethod
    def validate_manifest(manifest: AdapterManifest) -> None:
        if not manifest.adapter_id:
            raise ValueError("adapter_id is required")
        if not manifest.framework_name:
            raise ValueError("framework_name is required")
        if not manifest.supported_event_types:
            raise ValueError("supported_event_types cannot be empty")
        if not manifest.supported_action_classes:
            raise ValueError("supported_action_classes cannot be empty")
        if "normalize_event" not in manifest.capability_bits:
            raise ValueError("capability_bits must include normalize_event")
        if "export_receptors" not in manifest.capability_bits:
            raise ValueError("capability_bits must include export_receptors")


def load_manifest(path: str | Path) -> AdapterManifest:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return AdapterManifest(**data)


def main() -> None:
    parser = argparse.ArgumentParser(description="NEXUS GATE adapter registry utility")
    parser.add_argument("--manifest", default="registry/adapters.local_demo.v0.1.7.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    registry = AdapterRegistry()
    manifest = load_manifest(args.manifest)
    entry = registry.register(manifest)

    output = {
        "system": "NEXUS GATE",
        "version": "0.1.7-adapter-registry",
        "status": "pass",
        "registered": entry.manifest.to_dict(),
        "claim_boundary": "Adapter registry utility is local validation evidence only."
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"Registered adapter: {entry.manifest.adapter_id}")


if __name__ == "__main__":
    main()
