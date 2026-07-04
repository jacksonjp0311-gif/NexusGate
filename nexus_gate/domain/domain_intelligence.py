from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


DOMAINS = ["biology", "technology", "code", "math", "physics", "systems", "human_ai", "governance"]
SCHEMAS = [
    "source_card.schema.json",
    "concept_card.schema.json",
    "claim_card.schema.json",
    "equation_card.schema.json",
    "simulation_card.schema.json",
    "code_pattern_card.schema.json",
    "orchestration_card.schema.json",
]
CLAIM_BOUNDARY = (
    "Domain intelligence compilation is local development evidence only. It does not prove scientific truth, "
    "medical validity, physical law, mathematical proof, code correctness, safety, security, production readiness, "
    "model understanding, or autonomous authority."
)


@dataclass
class DomainIntelligenceReport:
    system: str
    version: str
    status: str
    generated_at_utc: str
    domains: list[str]
    checks: list[dict[str, Any]] = field(default_factory=list)
    read_surfaces: list[str] = field(default_factory=list)
    write_surfaces: list[str] = field(default_factory=list)
    allowed_study_modes: list[str] = field(default_factory=list)
    blocked_claims: list[str] = field(default_factory=list)
    next_action: str = ""
    claim_boundary: str = CLAIM_BOUNDARY


def _check(name: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"check": name, "status": "pass" if passed else "fail", "evidence": evidence}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compile_domain_intelligence(root: str | Path = ".") -> DomainIntelligenceReport:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    doctrine_paths = [
        "docs/intelligence/DOMAIN_INTELLIGENCE_ORCHESTRATOR.md",
        "docs/intelligence/REPO_NATIVE_LEARNING.md",
        "docs/intelligence/CROSS_DOMAIN_SYNTHESIS_PROTOCOL.md",
        "docs/codex/CODEX_ORCHESTRATION_PROTOCOL.md",
    ]
    missing_doctrine = [rel for rel in doctrine_paths if not (root / rel).exists()]
    checks.append(_check("domain_doctrine_exists", not missing_doctrine, {"missing": missing_doctrine}))

    missing_domains = [domain for domain in DOMAINS if not (root / "domains" / domain / "README.md").exists()]
    checks.append(_check("domain_readmes_exist", not missing_domains, {"missing": missing_domains}))

    missing_schemas = [name for name in SCHEMAS if not (root / "domains" / "_schemas" / name).exists()]
    checks.append(_check("domain_schemas_exist", not missing_schemas, {"missing": missing_schemas}))

    state_paths = [
        "state/domain_intelligence_index.v0.4.0.json",
        "state/repo_native_learning_index.v0.4.0.json",
        "state/codex_orchestration_index.v0.4.0.json",
    ]
    missing_state = [rel for rel in state_paths if not (root / rel).exists()]
    checks.append(_check("domain_state_indexes_exist", not missing_state, {"missing": missing_state}))

    domain_index = _read_json(root / "state/domain_intelligence_index.v0.4.0.json")
    codex_index = _read_json(root / "state/codex_orchestration_index.v0.4.0.json")
    blocked_claims = list(domain_index.get("blocked_claims", []))

    checks.append(_check("blocked_claims_declared", bool(blocked_claims), {"blocked_claims": blocked_claims}))

    biology = _read_text(root / "domains/biology/README.md")
    math = _read_text(root / "domains/math/README.md")
    physics = _read_text(root / "domains/physics/README.md")
    code = _read_text(root / "domains/code/README.md")
    synthesis = _read_text(root / "docs/intelligence/CROSS_DOMAIN_SYNTHESIS_PROTOCOL.md")
    codex = _read_text(root / "docs/codex/CODEX_ORCHESTRATION_PROTOCOL.md")

    checks.append(_check("biology_safety_boundary_present", "not medical authority" in biology and "unsafe wet-lab" in biology, {"domain": "biology"}))
    checks.append(_check("math_proof_conjecture_boundary_present", "conjecture" in math and "theorem" in math and "proof" in math, {"domain": "math"}))
    checks.append(_check("physics_dimensional_simulation_boundary_present", "dimensional" in physics and "simulation" in physics, {"domain": "physics"}))
    checks.append(_check("code_test_boundary_present", "tests" in code and "production readiness" in code, {"domain": "code"}))
    checks.append(_check("cross_domain_analogy_boundary_present", "No metaphor becomes fact without evidence." in synthesis and "No simulation becomes real-world proof." in synthesis, {"doc": "CROSS_DOMAIN_SYNTHESIS_PROTOCOL.md"}))
    checks.append(_check("codex_no_self_authorization_boundary_present", "Rehydrate before patching." in codex and "cannot self-authorize" in codex, {"doc": "CODEX_ORCHESTRATION_PROTOCOL.md"}))

    status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    next_action = "Continue with .\\scripts\\nexus.ps1 reflect and .\\scripts\\nexus.ps1 evolve." if status == "pass" else "Repair domain intelligence gaps and rerun .\\scripts\\nexus.ps1 domain."

    return DomainIntelligenceReport(
        system="NEXUS GATE",
        version="0.4.0-domain-intelligence-orchestrator",
        status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        domains=DOMAINS,
        checks=checks,
        read_surfaces=doctrine_paths + state_paths + ["domains/README.md"],
        write_surfaces=["reports/nexus_domain_intelligence_report_latest.json", "docs/feedback/operator_packets/*.json"],
        allowed_study_modes=["study", "extract", "map", "model", "simulate", "test", "gate", "reflect", "compress", "rehydrate", "orchestrate"],
        blocked_claims=blocked_claims,
        next_action=next_action,
    )


def write_domain_intelligence_report(report: DomainIntelligenceReport, root: str | Path = ".") -> Path:
    reports = Path(root).resolve() / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    latest = reports / "nexus_domain_intelligence_report_latest.json"
    latest.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return latest
