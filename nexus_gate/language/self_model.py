from __future__ import annotations

from pathlib import Path

from nexus_gate.intelligence.common import read_json, write_json


REPORT = Path("reports") / "nexus_self_model_latest.json"


def build(root: str | Path) -> dict:
    root_path = Path(root)
    registry = read_json(root_path / "registry" / "nexus_command_registry.v2.6.2.json", {})
    readme = (root_path / "README.md").read_text(encoding="utf-8-sig", errors="replace") if (root_path / "README.md").exists() else ""
    commands = sorted(item.get("command_registry_id") for item in registry.get("commands", []) if item.get("command_registry_id"))
    packet = {
        "schema": "NEXUS_SELF_MODEL.v2.9.0",
        "status": "pass",
        "version_evidence": "v2.9.0 Geometric Language Intelligence Engine" if "v2.9.0" in readme else "v2.8.0 baseline or updating",
        "command_count": len(commands),
        "commands": commands,
        "capabilities": ["ai_touch_receipts", "deterministic_intelligence_extraction", "sparse_language_activation", "grounded_query", "conductance_preference"],
        "experimental_capabilities": ["geometric_token_field", "motif_compression", "language_conductance_calibration"],
        "blocked_claims": ["frontier_parity", "consciousness", "agi", "autonomous_authority", "production_safety"],
        "authority_boundaries": ["human_authorization_required", "language_recommendation_only", "telemetry_observational_only"],
        "evidence": ["README.md", "registry/nexus_command_registry.v2.6.2.json"],
    }
    write_json(root_path / REPORT, packet)
    return packet


def verify(root: str | Path) -> dict:
    packet = build(root)
    return {"schema": "NEXUS_SELF_MODEL_VERIFY.v2.9.0", "status": "pass" if packet["command_count"] else "warn", "evidence": packet["evidence"]}
