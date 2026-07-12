from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SYSTEM = "NEXUS_DISCOVERY_CARDS"
VERSION = "0.2.0"
SCHEMA = "NEXUS_DISCOVERY_CARD_SET.v0.2.0"
LATEST_PATH = Path("state/discoveries/nexus_discovery_cards_latest.json")
VERSIONED_PATH = Path("state/discoveries/nexus_discovery_cards.v0.2.0.json")

CLAIM_BOUNDARY = (
    "Discovery cards preserve local engineering discoveries as reproducible cards. "
    "They do not prove correctness, safety, security, production readiness, scientific truth, "
    "mathematical proof, or autonomous authority."
)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_discovery_cards(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    cards = [
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.1.0",
            "discovery_id": "predictive-gate-timing-runtime-pressure",
            "version": "0.1.0",
            "title": "Predictive Gate Timing / Runtime Pressure Model",
            "status": "active",
            "summary": "Timeouts and slow gates are not just failures; they are runtime pressure signals that can guide cheaper next gates.",
            "math": {
                "baseline": "median_duration = median(durations)",
                "p90": "p90_duration = percentile(durations, 0.90)",
                "drift": "drift_ratio = latest_duration / median_duration",
                "adaptive_timeout": "timeout = max(min_timeout, min(max_timeout, p90 * 1.5))",
                "control_loop": "observe -> estimate -> compare -> classify -> recommend -> record",
            },
            "code_references": [
                "nexus_gate/loops/predictive_timing.py::build_predictive_timing_packet",
                "nexus_gate/loops/predictive_timing.py::_analyze_steps",
                "nexus_gate/loops/predictive_timing.py::_gate_selection_policy",
                "nexus_gate/loops/predictive_timing.py::write_outputs",
            ],
            "algorithm_card_refs": [
                "runtime-pressure-model",
                "adaptive-timeout-budgeting",
                "gate-selection-policy",
                "certificate-resume-policy",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 predictive-timing",
                "Inspect reports/nexus_predictive_gate_timing_latest.json",
                "Inspect ledger/runtime_gate_timings.jsonl",
                "Use the recommendation before repeating full evolve",
            ],
            "evidence_surfaces": [
                "reports/nexus_predictive_gate_timing_latest.json",
                "state/loops/nexus_predictive_gate_timing_latest.json",
                "ledger/runtime_gate_timings.jsonl",
                "state/algorithms/nexus_algorithm_cards_latest.json",
            ],
            "next_versions": [
                "v0.2: add confidence intervals and per-gate trend windows",
                "v0.3: add predictive-evolve dry-run planner",
                "v0.4: surface timing pressure in Electron/System Monitor HUD",
            ],
            "boundary": "Recommendation-only. It may guide gate choice; it may not skip required final evolve before commit.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "predictive-evolve-dry-run-planner",
            "version": "0.2.0",
            "title": "Predictive Evolve Dry-Run Planner",
            "status": "active",
            "summary": "Predictive timing becomes more useful when wrapped in a dry-run plan that orders the next cheapest gate while preserving the final evolve seal.",
            "math": {
                "scope_policy": "scope = classify(changed_files)",
                "pressure_policy": "pressure = max_level(runtime_pressure)",
                "plan_rule": "plan = [predictive-timing, targeted_gate(scope, pressure), final_evolve_seal]",
                "authority_rule": "commit_allowed = final_evolve_passed and human_authorized",
                "control_loop": "estimate -> classify -> plan -> require seal -> record",
            },
            "code_references": [
                "nexus_gate/loops/predictive_evolve.py::build_predictive_evolve_plan",
                "nexus_gate/loops/predictive_evolve.py::_plan_steps",
                "nexus_gate/loops/predictive_timing.py::build_predictive_timing_packet",
            ],
            "algorithm_card_refs": [
                "predictive-evolve-planner-algorithm",
                "gate-selection-policy",
                "runtime-pressure-model",
                "certificate-resume-policy",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 predictive-evolve",
                "Inspect reports/nexus_predictive_evolve_plan_latest.json",
                "Run any recommended targeted gate manually",
                "Run .\\scripts\\nexus.ps1 evolve before commit",
            ],
            "evidence_surfaces": [
                "reports/nexus_predictive_evolve_plan_latest.json",
                "state/loops/nexus_predictive_evolve_plan_latest.json",
                "reports/nexus_predictive_gate_timing_latest.json",
                "state/algorithms/nexus_algorithm_cards_latest.json",
            ],
            "next_versions": [
                "v0.3: add HUD runtime pressure visibility",
                "v0.4: add confidence windows and EWMA pressure smoothing",
                "v0.5: add certificate resume planning",
            ],
            "boundary": "Dry-run and recommendation-only. It may recommend targeted gates; it may not execute them or skip full evolve before commit.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "certificate-resume-gate-fingerprint",
            "version": "0.2.0",
            "title": "Certificate Resume Gate Fingerprint",
            "status": "active",
            "summary": "Passed gates can become local resume evidence when their logs and current git scope are hashed, but certificates never replace the final evolve seal.",
            "math": {
                "evidence_hash": "evidence_sha256 = sha256(gate_log_bytes)",
                "input_fingerprint": "input_fingerprint = sha256(gate_id + git_scope_hash + gate_log_bytes)",
                "resume_rule": "resume_gate = first(status in {fail, timeout})",
                "commit_rule": "commit_allowed = final_evolve_passed and human_authorized",
                "control_loop": "gate -> hash -> certify -> fail point -> recommend resume -> require seal",
            },
            "code_references": [
                "nexus_gate/loops/certificate_resume.py::build_certificate_resume_packet",
                "nexus_gate/loops/certificate_resume.py::_certificate_for",
                "nexus_gate/loops/certificate_resume.py::_latest_human_surface",
            ],
            "algorithm_card_refs": [
                "certificate-resume-policy",
                "predictive-evolve-planner-algorithm",
                "compiler-gate-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 certificate-resume",
                "Inspect reports/nexus_certificate_resume_report_latest.json",
                "Fix the active wound if a resume gate is present",
                "Run .\\scripts\\nexus.ps1 evolve before commit",
            ],
            "evidence_surfaces": [
                "reports/nexus_certificate_resume_report_latest.json",
                "state/loops/nexus_certificate_resume_latest.json",
                "reports/human_surface/*",
            ],
            "next_versions": [
                "v0.2: compare certificate fingerprints across changed inputs",
                "v0.3: recommend exact targeted rerun command per gate",
                "v0.4: show certificate status in System Monitor HUD",
            ],
            "boundary": "Recommendation-only. Certificates may recommend resume points; they may not claim correctness or skip final evolve before commit.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "cortex-versioned-vector-memory",
            "version": "0.1.0",
            "title": "Cortex Versioned Vector Memory",
            "status": "active",
            "summary": "Cortex memory can become cheaper and more governable when semantic vectors are stored as versioned float32 blobs instead of legacy JSON strings.",
            "math": {
                "payload_reduction": "reduction = 1 - blob_payload_bytes / legacy_payload_bytes",
                "observed_reduction": "1 - 1545000 / 2366490 = 0.3471",
                "query_delta": "delta_ms = legacy_mean_query_ms - blob_mean_query_ms",
                "observed_query_delta": "242.630 ms - 183.011 ms = 59.619 ms",
                "format_rule": "current = vector_bytes startswith CTXV1",
            },
            "code_references": [
                "Cortex/cortex/embeddings.py::vector_to_bytes",
                "Cortex/cortex/embeddings.py::deserialize_vector",
                "Cortex/cortex/store.py::migrate_vectors",
                "Cortex/cortex/store.py::vector_format_status",
                "nexus_gate/cortex/compile.py::compile_gate",
            ],
            "algorithm_card_refs": [
                "versioned-vector-blob-storage-algorithm",
                "cortex-sync-protocol-algorithm",
                "compiler-gate-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 sync-cortex -Tag \"C:\\Users\\jacks\\OneDrive\\Desktop\\Cortex\"",
                "cd Cortex",
                "python -m cortex --home ..\\state\\cortex_memory migrate-vectors --repo nexus-gate --json",
                "python -m Cortex.benchmarks.vector_migration_benchmark",
                ".\\scripts\\nexus.ps1 cortex",
            ],
            "evidence_surfaces": [
                "reports/nexus_cortex_gate_latest.json",
                "reports/nexus_cortex_sync_report_latest.json",
                "reports/nexus_cortex_vector_benchmark_latest.json",
                "docs/runtime/NEXUS_CORTEX.md",
            ],
            "next_versions": [
                "v0.2: add benchmark trend ledger for vector payload/query measurements",
                "v0.3: expose Cortex vector health in Meta-Orchestrator/System Monitor HUD",
                "v0.4: add safe bootstrap refresh lane after source sync",
            ],
            "boundary": "Local memory optimization only. It does not prove retrieval correctness, model understanding, safety, security, or mutation authority.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "predictive-memory-orchestrator",
            "version": "0.1.0",
            "title": "Predictive Memory Orchestrator",
            "status": "active",
            "summary": "NEXUS can reduce wasted validation cycles when Cortex memory health, vector benchmark trends, algorithm cards, discovery cards, and predictive evolve plans are fused into one recommendation-only packet.",
            "math": {
                "memory_gain": "gain = vector_payload_reduction_percent + max(query_delta_ms, 0)",
                "card_readiness": "ready = missing_algorithms == 0 and missing_discoveries == 0",
                "gate_rule": "next = cortex_repair if memory_unhealthy else predictive_evolve_next_step",
                "authority_rule": "commit_allowed = final_evolve_passed and human_authorized",
                "control_loop": "memory -> cards -> timing -> recommend -> record -> require seal",
            },
            "code_references": [
                "nexus_gate/loops/predictive_memory_orchestrator.py::build_predictive_memory_orchestrator",
                "nexus_gate/loops/predictive_memory_orchestrator.py::_cortex_status",
                "nexus_gate/loops/predictive_memory_orchestrator.py::_recommend",
                "nexus_gate/loops/predictive_evolve.py::build_predictive_evolve_plan",
            ],
            "algorithm_card_refs": [
                "predictive-memory-orchestrator-algorithm",
                "predictive-evolve-planner-algorithm",
                "versioned-vector-blob-storage-algorithm",
                "cortex-sync-protocol-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 cortex",
                ".\\scripts\\nexus.ps1 predictive-evolve",
                ".\\scripts\\nexus.ps1 predictive-memory",
                "Inspect reports/nexus_predictive_memory_orchestrator_latest.json",
                "Run .\\scripts\\nexus.ps1 evolve before commit",
            ],
            "evidence_surfaces": [
                "reports/nexus_predictive_memory_orchestrator_latest.json",
                "state/loops/nexus_predictive_memory_orchestrator_latest.json",
                "ledger/cortex_benchmark_trends.jsonl",
                "reports/nexus_cortex_gate_latest.json",
                "reports/nexus_predictive_evolve_plan_latest.json",
            ],
            "next_versions": [
                "v0.2: add Cortex certificate refresh lane",
                "v0.3: expose predictive memory state in Electron System Monitor HUD",
                "v0.4: add retrieval confidence trend rows after Cortex query runs",
            ],
            "boundary": "Recommendation-only. It may choose the next evidence lane; it may not execute the plan, mutate memory, or skip final evolve before commit.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "authority-monotonicity-law",
            "version": "0.1.0",
            "title": "Authority Monotonicity Law",
            "status": "active",
            "summary": "NEXUS can transform intelligence, but authority may only be preserved or reduced as packets move through adapters, models, memory, HUDs, compilers, and certificates.",
            "math": {
                "authority_rule": "A_out subseteq A_in intersection P_allowed",
                "violation": "exists capability in A_out where capability notin A_in or notin P_allowed",
                "control_loop": "inspect authority -> normalize fields -> reject authority increases -> preserve boundary",
            },
            "code_references": [
                "nexus_gate/runtime/router.py",
                "nexus_gate/cortex/compile.py::_is_read_only_authority",
                "nexus_gate/nexus_cell/authority.py",
            ],
            "algorithm_card_refs": [
                "authority-monotonicity-algorithm",
                "authority-gate-algorithm",
                "cortex-certificate-refresh-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 origin-seal",
                ".\\scripts\\nexus.ps1 cortex",
                "Verify no generated packet grants mutation authority from read-only input",
            ],
            "evidence_surfaces": [
                "reports/nexus_origin_seal_latest.json",
                "reports/nexus_cortex_gate_latest.json",
                "reports/nexus_meta_orchestrator_gate_latest.json",
            ],
            "next_versions": [
                "v0.2: compile blocked-action dictionaries from one policy kernel",
                "v0.3: add automated authority monotonicity test fixtures",
            ],
            "boundary": "Authority law only. It does not grant authority, execution, git write, network access, or safety proof.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "evidence-freshness-law",
            "version": "0.1.0",
            "title": "Evidence Freshness Law",
            "status": "active",
            "summary": "Repository evidence outranks stdout only when schema, origin hash, producer compatibility, relevant inputs, and freshness policy still match the current repository state.",
            "math": {
                "fresh_evidence": "valid = schema_ok and origin_hash_ok and producer_compatible and inputs_unchanged and freshness_ok",
                "stale_rule": "stale evidence is diagnostic, not admissible truth",
                "control_loop": "locate packet -> validate schema -> compare origin -> compare inputs -> admit or demote",
            },
            "code_references": [
                "nexus_gate/origin/seal.py::build_origin_seal",
                "nexus_gate/loops/certificate_resume.py::build_certificate_resume_packet",
                "nexus_gate/loops/wound_compression.py",
            ],
            "algorithm_card_refs": [
                "evidence-freshness-algorithm",
                "origin-seal-algorithm",
                "certificate-resume-policy",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 origin-seal",
                "Inspect state/nexus_origin_manifest_latest.json",
                "Compare origin_manifest_hash before trusting stale reports",
            ],
            "evidence_surfaces": [
                "state/nexus_origin_manifest_latest.json",
                "reports/nexus_origin_seal_latest.json",
                "reports/human_surface/*",
            ],
            "next_versions": [
                "v0.2: add per-report origin hash checks",
                "v0.3: reject stale report truth in wound compression",
            ],
            "boundary": "Freshness is an admissibility rule. It does not prove correctness, safety, or production readiness.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "gate-dependency-invalidation",
            "version": "0.1.0",
            "title": "Gate Dependency Invalidation",
            "status": "active",
            "summary": "Passed gates become useful certificates only when the relevant input, toolchain, and gate-contract fingerprints still match.",
            "math": {
                "reuse_rule": "reuse(gate) = prior_pass and hash(inputs_now)==hash(inputs_then) and toolchain_now==toolchain_then and contract_now==contract_then",
                "invalidate_rule": "changed input or changed contract or changed toolchain -> rerun gate",
                "control_loop": "record dependencies -> compare before reuse -> recommend resume -> require final evolve",
            },
            "code_references": [
                "nexus_gate/loops/certificate_resume.py",
                "nexus_gate/loops/predictive_evolve.py",
                "nexus_gate/loops/predictive_timing.py",
            ],
            "algorithm_card_refs": [
                "gate-dependency-invalidation-algorithm",
                "certificate-resume-policy",
                "predictive-evolve-planner-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 certificate-resume",
                "Inspect reports/nexus_certificate_resume_report_latest.json",
                "Require .\\scripts\\nexus.ps1 evolve before commit",
            ],
            "evidence_surfaces": [
                "reports/nexus_certificate_resume_report_latest.json",
                "reports/human_surface/*",
                "ledger/runtime_gate_timings.jsonl",
            ],
            "next_versions": [
                "v0.2: hash explicit gate dependency sets",
                "v0.3: add dependency graph HUD panel",
            ],
            "boundary": "Gate reuse is recommendation-only and never skips final evolve before commit.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "reflexive-non-sovereignty",
            "version": "0.1.0",
            "title": "Reflexive Non-Sovereignty",
            "status": "active",
            "summary": "NEXUS may observe, diagnose, recommend, validate, and remember itself without gaining the authority to authorize itself.",
            "math": {
                "law": "self_observation != self_authorization",
                "mutation_rule": "durable_mutation_allowed = human_authorized and required_gates_passed",
                "control_loop": "self-observe -> recommend -> human gate -> controlled action -> receipt",
            },
            "code_references": [
                "nexus_gate/origin/seal.py",
                "nexus_gate/loops/meta_orchestrator_gate.py",
                "nexus_gate/nexus_cell/runner.py",
            ],
            "algorithm_card_refs": [
                "authority-monotonicity-algorithm",
                "causal-memory-closure-algorithm",
                "controlled-lane-receipt-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 meta-orchestrator",
                ".\\scripts\\nexus.ps1 origin-seal",
                "Confirm recommendation surfaces cannot self-authorize mutation",
            ],
            "evidence_surfaces": [
                "reports/nexus_meta_orchestrator_gate_latest.json",
                "reports/nexus_origin_seal_latest.json",
                "state/loops/nexus_meta_orchestrator_gate.v1.1.3.json",
            ],
            "next_versions": [
                "v0.2: add canonical decision envelope",
                "v0.3: add end-to-end receipt-to-memory promotion test",
            ],
            "boundary": "Self-observation and self-diagnosis are not self-authority.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "lineage-entropy",
            "version": "0.1.0",
            "title": "Lineage Entropy",
            "status": "active",
            "summary": "Multiple inconsistent current-version declarations are a measurable health signal. Origin Seal reduces ambiguity by declaring one product identity and preserving older strings as subsystem lineage.",
            "math": {
                "lineage_entropy": "distinct_current_identities + stale_origin_surfaces + unsealed_commits + incompatible_schema_refs",
                "reduction_rule": "canonical_origin_manifest lowers identity ambiguity without deleting subsystem lineage",
                "control_loop": "scan identity surfaces -> classify product/subsystem -> seal manifest -> track entropy",
            },
            "code_references": [
                "nexus_gate/origin/seal.py::build_origin_seal",
                "state/nexus_origin_manifest_latest.json",
                "README.md::Human Director Box",
            ],
            "algorithm_card_refs": [
                "origin-seal-algorithm",
                "evidence-freshness-algorithm",
                "lineage-topology-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 origin-seal",
                "Inspect legacy_version_lineage in state/nexus_origin_manifest_latest.json",
                "Use the origin seal as current identity during rehydration",
            ],
            "evidence_surfaces": [
                "state/nexus_origin_manifest_latest.json",
                "state/nexus_lineage_manifest_latest.json",
                "README.md",
            ],
            "next_versions": [
                "v0.2: add numeric lineage entropy score",
                "v0.3: add origin drift warning to Meta-Orchestrator",
            ],
            "boundary": "Lineage entropy is an orientation metric, not a correctness or production readiness proof.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "self-bootstrap-decision-envelope",
            "version": "0.1.0",
            "title": "Self-Bootstrap Decision Envelope",
            "status": "active",
            "summary": "NEXUS can gather its current origin, memory, runtime pressure, wounds, certificates, cards, and git scope into one canonical recommendation packet for fast rehydration.",
            "math": {
                "envelope": "D = select(normalize(origin, memory, timing, wounds, certificates, cards, git_scope))",
                "authority_rule": "selected_action is recommendation_only and requires_human_authorization",
                "bootstrap_loop": "origin -> evidence -> normalized recommendations -> selected next action -> final evolve",
            },
            "code_references": [
                "nexus_gate/decision/envelope.py::build_decision_envelope",
                "reports/nexus_decision_envelope_latest.json",
                "state/decision/nexus_decision_envelope_latest.json",
            ],
            "algorithm_card_refs": [
                "self-bootstrap-decision-envelope-algorithm",
                "decision-envelope-arbitration-algorithm",
                "authority-monotonicity-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 origin-seal",
                ".\\scripts\\nexus.ps1 decision-envelope",
                "Inspect selected_action and blocked_actions before choosing a lane",
            ],
            "evidence_surfaces": [
                "reports/nexus_decision_envelope_latest.json",
                "state/decision/nexus_decision_envelope_latest.json",
                "reports/nexus_origin_seal_latest.json",
            ],
            "next_versions": [
                "v0.2: feed decision envelope into Electron Meta-Orchestrator HUD",
                "v0.3: add canonical decision envelope schema tests for every recommendation source",
            ],
            "boundary": "Self-bootstrap is self-orientation, not self-execution or self-authorization.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "coherence-continuity-threshold",
            "version": "0.1.0",
            "title": "Coherence Continuity Threshold",
            "status": "active",
            "summary": "NEXUS crosses a coherence threshold when origin, memory, runtime pressure, wounds, policy, cards, and decision evidence compile into one shared field for fast rehydration.",
            "math": {
                "field": "F = coherence(origin, memory, timing, wounds, policy, certificates, git_scope)",
                "score": "C = 100 - drift_penalties - missing_surface_penalties - dirty_scope_pressure - card_readiness_penalty",
                "authority_rule": "coherence_guides_routing and not coherence_grants_authority",
            },
            "code_references": [
                "nexus_gate/coherence/field.py::build_coherence_field",
                "reports/nexus_coherence_field_latest.json",
                "state/coherence/nexus_coherence_field_latest.json",
            ],
            "algorithm_card_refs": [
                "coherence-field-algorithm",
                "governed-agent-continuity-algorithm",
                "authority-monotonicity-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 origin-seal",
                ".\\scripts\\nexus.ps1 decision-envelope",
                ".\\scripts\\nexus.ps1 coherence-field",
            ],
            "evidence_surfaces": [
                "reports/nexus_coherence_field_latest.json",
                "reports/nexus_decision_envelope_latest.json",
                "policy/authority_laws.json",
            ],
            "next_versions": [
                "v0.2: wire coherence field into Electron System Monitor HUD",
                "v0.3: make recommendation arbitration consume coherence score causally",
            ],
            "boundary": "Coherence is an operating field for orientation, not proof, authority, or autonomous mutation.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "causal-coherence-routing",
            "version": "0.1.0",
            "title": "Causal Coherence Routing",
            "status": "active",
            "summary": "Coherence becomes useful when it changes recommendation pressure without becoming authority.",
            "math": {
                "arbiter_score": "severity + source_priority + confidence - cost - blockers - stale_penalty + coherence_adjustment",
                "selection": "selected_route = argmax(score(candidate_recommendations, coherence_field))",
                "boundary": "selected_route != executed_route unless human_authorized and gates_passed",
            },
            "code_references": [
                "nexus_gate/decision/arbiter.py::arbitrate_recommendations",
                "nexus_gate/decision/envelope.py::build_decision_envelope",
                "reports/nexus_decision_envelope_latest.json",
            ],
            "algorithm_card_refs": [
                "causal-coherence-routing-algorithm",
                "coherence-field-algorithm",
                "decision-envelope-arbitration-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 coherence-field",
                ".\\scripts\\nexus.ps1 decision-envelope",
                "Inspect arbiter.scored_recommendations and selected_action",
            ],
            "evidence_surfaces": [
                "reports/nexus_coherence_field_latest.json",
                "reports/nexus_decision_envelope_latest.json",
                "docs/protocols/CAUSAL_COHERENCE_ROUTING_PROTOCOL.md",
            ],
            "next_versions": [
                "v0.2: add outcome feedback from selected route to arbiter calibration",
                "v0.3: expose arbiter score in Electron System Monitor HUD",
            ],
            "boundary": "Causal coherence is routing pressure only; it is not execution, proof, or authority.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "recommendation-outcome-learning",
            "version": "0.1.0",
            "title": "Recommendation Outcome Learning",
            "status": "active",
            "summary": "A recommendation becomes reusable intelligence only after the system records an outcome and computes route fitness.",
            "math": {
                "route_fitness": "outcome_score + coherence_bonus",
                "source_reliability": "(passes + 0.5 * warnings) / runs",
                "weight_adjustment": "(source_reliability - 0.5) * 12",
            },
            "code_references": [
                "nexus_gate/outcomes/learn.py::build_outcome_report",
                "ledger/recommendation_outcomes.jsonl",
                "state/coherence/arbiter_calibration_latest.json",
            ],
            "algorithm_card_refs": [
                "outcome-feedback-algorithm",
                "arbiter-calibration-algorithm",
                "pressure-memory-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 decision-envelope",
                ".\\scripts\\nexus.ps1 coherence-field",
                ".\\scripts\\nexus.ps1 outcome-learn",
            ],
            "evidence_surfaces": [
                "reports/nexus_recommendation_outcome_latest.json",
                "state/coherence/arbiter_calibration_latest.json",
                "state/coherence/pressure_memory_latest.json",
            ],
            "next_versions": [
                "v0.2: record explicit command duration and output hashes",
                "v0.3: expose route fitness in Electron System Monitor HUD",
            ],
            "boundary": "Outcome learning calibrates recommendation pressure. It is not proof, execution, or authority.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "generated-surface-source-separation",
            "version": "0.1.0",
            "title": "Generated Surface / Source Separation",
            "status": "active",
            "summary": "Recurring post-evolve dirty state is two mixed signals: generated evidence exhaust and source mutation. Separating them keeps source changes visible while making generated churn cleanable.",
            "math": {
                "dirty_scope": "dirty = generated_tracked + generated_untracked + source_dirty",
                "cleanable": "cleanable = allowlisted(generated_tracked + generated_untracked)",
                "safety": "source_dirty_after_clean = source_dirty_before_clean",
            },
            "code_references": [
                "nexus_gate/hygiene/runtime_churn.py::build_runtime_hygiene_report",
                "reports/nexus_runtime_hygiene_latest.json",
                "scripts/nexus.ps1",
            ],
            "algorithm_card_refs": [
                "runtime-churn-hygiene-algorithm",
                "scope-hygiene-algorithm",
                "authority-gate-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 runtime-hygiene",
                ".\\scripts\\nexus.ps1 clean-runtime",
                "Inspect remaining_source_dirty before staging.",
            ],
            "evidence_surfaces": [
                "reports/nexus_runtime_hygiene_latest.json",
                ".gitignore",
                "git status --short",
            ],
            "next_versions": [
                "v0.2: install local post-commit hook for optional automatic clean-runtime",
                "v0.3: add HUD warning when source_dirty remains after cleanup",
            ],
            "boundary": "Runtime hygiene may clean allowlisted generated surfaces only. It is not source deletion, proof, authority, or unbounded git cleanup.",
        }
    ]
    return {
        "schema": SCHEMA,
        "system": SYSTEM,
        "version": VERSION,
        "generated_at_utc": _utc(),
        "card_count": len(cards),
        "cards": cards,
        "portal_entry": "[18] Discoveries",
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_discovery_cards(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    packet = build_discovery_cards(root)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    for rel in (LATEST_PATH, VERSIONED_PATH):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS discovery cards.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_discovery_cards(args.root)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"wrote {packet['card_count']} NEXUS discovery cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
