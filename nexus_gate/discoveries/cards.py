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
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "control-state-adversarial-testing",
            "version": "0.1.0",
            "title": "Control-State Adversarial Testing",
            "status": "active",
            "summary": "Routing loops need tests for pathological control values, not only happy-path evidence flow. Zero, sentinels, overconfident scores, tied scores, and stale epochs are control wounds.",
            "math": {
                "coherence_state": "state = classify(score); score=0 => critical",
                "confidence": "confidence = clamp(raw, 0, 1)",
                "deterministic_route": "selected = max(score, severity, source_priority, source, action)",
                "freshness": "fresh = commit_match and source_status_hash_match and input_snapshot_hash_match",
            },
            "code_references": [
                "nexus_gate/coherence/states.py",
                "nexus_gate/state/snapshot.py",
                "nexus_gate/decision/arbiter.py",
                "nexus_gate/loops/wounds.py",
            ],
            "algorithm_card_refs": [
                "causal-loop-hardening-algorithm",
                "causal-coherence-routing-algorithm",
                "authority-gate-algorithm",
            ],
            "replication_steps": [
                "python -m unittest discover -s tests -p \"test_causal_coherence_routing_v210.py\"",
                ".\\scripts\\nexus.ps1 decision-envelope",
                ".\\scripts\\nexus.ps1 coherence-field",
            ],
            "evidence_surfaces": [
                "reports/nexus_decision_envelope_latest.json",
                "reports/nexus_coherence_field_latest.json",
                "docs/design/CAUSAL_LOOP_HARDENING_DESIGN.md",
            ],
            "next_versions": [
                "v0.2: add epoch mismatch blocking instead of only stale scoring",
                "v0.3: add oscillation tests across multiple decision/coherence cycles",
            ],
            "boundary": "Adversarial testing improves route reliability. It does not prove correctness, safety, or autonomous authority.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "triadic-geometric-lattice-routing",
            "version": "0.1.0",
            "title": "Triadic Geometric Lattice Routing",
            "status": "active",
            "summary": "A route is strongest when evidence freshness, geometric efficiency, and authority alignment are all strong. Multiplicative alignment prevents one axis from masking collapse in another.",
            "math": {
                "alignment": "cuberoot(evidence * geometry * authority)",
                "arbiter_adjustment": "(alignment - 0.65) * 18",
                "axis_boundary": "high geometry cannot compensate for missing authority or stale evidence",
            },
            "code_references": [
                "nexus_gate/lattice/triadic.py::build_triadic_lattice",
                "nexus_gate/decision/arbiter.py::score_recommendation",
                "nexus_gate/decision/envelope.py::build_decision_envelope",
            ],
            "algorithm_card_refs": [
                "triadic-geometric-lattice-algorithm",
                "causal-loop-hardening-algorithm",
                "gitnexus-impact-extraction-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 triadic-lattice",
                ".\\scripts\\nexus.ps1 decision-envelope",
                "Inspect arbiter.scored_recommendations[].arbiter_factors.triadic_lattice_adjustment",
            ],
            "evidence_surfaces": [
                "reports/nexus_triadic_lattice_latest.json",
                "state/lattice/nexus_triadic_lattice_latest.json",
                "reports/nexus_decision_envelope_latest.json",
            ],
            "next_versions": [
                "v0.2: feed live GitNexus centrality and bridge-risk directly into geometry axis",
                "v0.3: expose lattice alignment in System Monitor and GitNexus HUDs",
            ],
            "boundary": "Triadic routing is recommendation pressure only. It cannot execute, mutate, grant authority, or skip final evolve.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "evidence-distillation-graph",
            "version": "0.1.0",
            "title": "Evidence Distillation Graph",
            "status": "active",
            "summary": "Heavy evidence can be compressed into hash-backed graph nodes so NEXUS keeps recurring structure while releasing generated exhaust under a retention policy.",
            "math": {
                "compression": "raw_surface -> hash + summary + links + retention_policy",
                "efficient_coding": "keep salient signal; remove repeated predictable payload",
                "pruning_gate": "prunable = distilled and hashed and not protected and human_authorized",
                "emergence_candidate": "motif = recurrence(route + coherence + outcome)",
            },
            "code_references": [
                "nexus_gate/distillation/graph.py::build_evidence_distillation_graph",
                "reports/nexus_evidence_distillation_report_latest.json",
                "state/distillation/nexus_evidence_graph_latest.json",
            ],
            "algorithm_card_refs": [
                "evidence-distillation-algorithm",
                "provenance-preserving-pruning-algorithm",
                "concept-graph-compression-algorithm",
                "emergence-detection-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 distill",
                "Inspect graph_metrics, pruning_policy, and emergence.",
                "Run .\\scripts\\nexus.ps1 evolve before any durable pruning decision.",
            ],
            "evidence_surfaces": [
                "reports/nexus_evidence_distillation_report_latest.json",
                "state/distillation/nexus_evidence_graph_latest.json",
                "ledger/evidence_distillation.jsonl",
            ],
            "next_versions": [
                "v0.2: compare graph hashes across epochs",
                "v0.3: promote repeated motifs into discovery candidates automatically",
            ],
            "boundary": "Distillation compresses evidence into graph memory. It does not delete source, self-authorize pruning, prove truth, or replace final evolve.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "epoch-integrity-seal",
            "version": "0.1.0",
            "title": "Epoch Integrity Seal",
            "status": "active",
            "summary": "Temporal graph learning needs identity that exists before commit. Source-root epochs let NEXUS compare evidence, memory, and route outcomes across runs without depending on a future commit hash.",
            "math": {
                "source_root": "MerkleRoot(sha256(path + NUL + file_sha256) for canonical source files)",
                "epoch_id": "SHA256(source_root + parent_epoch_id + runtime_contract_version)",
                "chain_event": "event_hash = SHA256(previous_event_hash + epoch_id + source_root + generated_at_utc)",
                "coherence_rule": "latest pointer is convenience; immutable epoch directory + append-only ledger are durable memory",
            },
            "code_references": [
                "nexus_gate/epochs/seal.py::build_epoch_integrity_seal",
                "reports/nexus_epoch_integrity_seal_latest.json",
                "state/latest_epoch_pointer.json",
                "ledger/epoch_chain.jsonl",
            ],
            "algorithm_card_refs": [
                "epoch-integrity-seal-algorithm",
                "evidence-distillation-algorithm",
                "causal-loop-hardening-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 epoch-seal",
                "Inspect state/latest_epoch_pointer.json.",
                "Compare state/epochs/<epoch_id>/epoch_manifest.json across future runs.",
            ],
            "evidence_surfaces": [
                "reports/nexus_epoch_integrity_seal_latest.json",
                "state/latest_epoch_pointer.json",
                "state/epochs/<epoch_id>/epoch_manifest.json",
                "ledger/epoch_chain.jsonl",
            ],
            "next_versions": [
                "v0.2: graph epoch delta comparison",
                "v0.3: post-commit attestation binding",
                "v0.4: stale packet rejection by source-root contract",
            ],
            "boundary": "Epoch sealing provides source identity and temporal ordering. It cannot execute, self-authorize, prove correctness, or replace final evolve.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "no-receipt-no-learning",
            "version": "0.1.0",
            "title": "No Receipt, No Learning",
            "status": "active",
            "summary": "NEXUS may not learn from a route unless recommendation, authorization, execution, effects, validation, and learnability receipts bind the outcome causally.",
            "math": {
                "causal_confidence": "K = E * A * X * W * V * (1 - F)",
                "hard_zero": "missing authorization OR stale epoch OR command mismatch OR missing execution receipt -> K = 0",
                "learnability": "K >= 0.85 AND admissible epochs AND validation passed",
            },
            "code_references": [
                "nexus_gate/actions/cli.py",
                "registry/nexus_command_registry.v2.6.2.json",
                "ledger/action_receipts.jsonl",
            ],
            "algorithm_card_refs": [
                "causal-action-lifecycle-algorithm",
                "causal-confidence-algorithm",
                "receipt-gated-calibration-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 action-recommend",
                ".\\scripts\\nexus.ps1 action-chain-verify",
                "Authorize and execute only by explicit human command.",
            ],
            "evidence_surfaces": [
                "state/actions/<action_id>/recommendation.json",
                "state/actions/<action_id>/authorization.json",
                "state/actions/<action_id>/execution.json",
                "state/actions/<action_id>/validation.json",
                "state/actions/<action_id>/learning.json",
            ],
            "next_versions": [
                "v0.2: route model calibration from three independent learnable receipts",
                "v0.3: effect-set instrumentation beyond Git write surfaces",
            ],
            "boundary": "Receipt learning is local causal-attribution evidence only. It does not grant autonomous authority or prove global correctness.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "generated-visualization-state-not-source",
            "version": "0.1.0",
            "title": "Generated Visualization State Must Not Pollute Source Identity",
            "status": "active",
            "summary": "Live neural visualization caches can change because time changed, not because NEXUS evolved. Runtime graph churn must be excluded from Source Epoch identity and classified as generated runtime cache.",
            "math": {
                "structural_graph_hash": "SHA256(deterministic nodes + deterministic edges)",
                "excluded_fields": "generated_at_utc, absolute_source_root, mtime, process state",
            },
            "code_references": [
                "electron/main.js::buildNeuralRepoGraph",
                "nexus_gate/hygiene/runtime_churn.py",
                "nexus_gate/epochs/seal.py::_is_generated_or_ignored",
            ],
            "algorithm_card_refs": [
                "source-epoch-identity-algorithm",
                "append-only-ledger-transaction-algorithm",
            ],
            "replication_steps": [
                "Open Neural Activity and refresh graph.",
                ".\\scripts\\nexus.ps1 runtime-hygiene",
                ".\\scripts\\nexus.ps1 epoch-seal",
            ],
            "evidence_surfaces": [
                "state/neural_activity/repo_neural_graph_latest.json",
                "state/neural_activity/repo_neural_graph_manifest_latest.json",
                "reports/nexus_runtime_hygiene_latest.json",
            ],
            "next_versions": [
                "v0.2: graph epoch delta comparison",
                "v0.3: source-node to evidence-node compression map",
            ],
            "boundary": "Visualization state supports operator awareness. It is not source identity, memory proof, or authority.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "local-success-is-not-durable-learning",
            "version": "0.1.0",
            "title": "Local Success Is Not Durable Learning",
            "status": "active",
            "summary": "A command can execute successfully while still being non-learnable because effects are missing, final evolve did not pass, the epoch is working-tree-only, or confounders remain.",
            "math": {
                "causal_confidence": "K = E * A * R * X * W * V * F * D",
                "durable_gate": "final_evolve_passed AND clean_epoch_admissible AND no high confounder pressure",
                "hard_zero": "unknown evidence does not equal pass",
            },
            "code_references": [
                "nexus_gate/actions/cli.py::finalize",
                "reports/nexus_first_learning_readiness_latest.json",
            ],
            "algorithm_card_refs": [
                "final-evolve-learning-proof-algorithm",
                "receipt-dependency-enforcement-algorithm",
                "replay-safe-calibration-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 first-learning-readiness",
                "Run a receipt lifecycle only after explicit human authorization.",
                "Inspect learning.json blocking_reasons before any calibration claim.",
            ],
            "evidence_surfaces": [
                "state/actions/<action_id>/learning.json",
                "reports/nexus_first_learning_readiness_latest.json",
            ],
            "next_versions": [
                "v0.2: first clean epoch learning rehearsal",
                "v0.3: calibration approval command",
            ],
            "boundary": "Durable learning is local calibration evidence only. It does not prove global correctness or grant authority.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "authorization-is-temporal-causal-evidence",
            "version": "0.1.0",
            "title": "Authorization Is Temporal Causal Evidence",
            "status": "active",
            "summary": "Authorization is valid only for one action, one command definition, one argument hash, one source epoch, and one expiry window.",
            "math": {
                "authorization_valid": "entry_hash_match AND args_hash_match AND epoch_match AND now <= expires_at",
                "stale_rule": "registry change OR source change -> STALE",
                "expiry_rule": "now > expires_at -> EXPIRED",
            },
            "code_references": [
                "nexus_gate/actions/cli.py::_verify_authorization_for_execution",
                "registry/nexus_command_registry.v2.6.2.json",
            ],
            "algorithm_card_refs": [
                "authorization-expiry-algorithm",
                "registry-definition-binding-algorithm",
                "human-authorization-binding-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 action-recommend",
                ".\\scripts\\nexus.ps1 action-authorize -ActionId \"<id>\"",
                "Change source or registry and verify execution blocks as stale.",
            ],
            "evidence_surfaces": [
                "state/actions/<action_id>/authorization.json",
                "state/actions/<action_id>/lifecycle.json",
            ],
            "next_versions": [
                "v0.2: UI expiry countdown",
                "v0.3: explicit reauthorization packet",
            ],
            "boundary": "Authorization evidence binds a local action. It is not reusable, delegable, or identity proof.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "source-identity-is-not-runtime-activity",
            "version": "0.1.0",
            "title": "Source Identity Is Not Runtime Activity",
            "status": "active",
            "summary": "A successful governed action may intentionally write runtime receipts, reports, and observations without changing the Source Epoch that defines NEXUS identity.",
            "math": {
                "source_epoch": "hash(canonical_source + runtime_contract + schema_compatibility)",
                "experience": "hash(source_epoch + action_id + execution_hash + effect_hash + validation_hash)",
                "rule": "expected_runtime_mutation != source_drift",
            },
            "code_references": [
                "nexus_gate/actions/cli.py::experience_seal",
                "nexus_gate/actions/cli.py::action_final_evolve",
                "nexus_gate/epochs/seal.py::build_epoch_integrity_seal",
            ],
            "algorithm_card_refs": [
                "identity-plane-experience-plane-plasticity-plane-algorithm",
                "verified-experience-seal-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 experience-readiness",
                ".\\scripts\\nexus.ps1 experience-chain-verify",
                "Confirm runtime receipts do not become autonomous source authority.",
            ],
            "evidence_surfaces": [
                "state/experiences/<experience_id>/experience_manifest.json",
                "ledger/experience_chain.jsonl",
                "reports/nexus_experience_readiness_latest.json",
            ],
            "next_versions": ["v0.2: move local runtime memory outside canonical source identity"],
            "boundary": "This discovery separates identity from experience. It does not permit untracked source mutation or automatic learning.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "receipt-presence-is-not-receipt-validity",
            "version": "0.1.0",
            "title": "Receipt Presence Is Not Receipt Validity",
            "status": "active",
            "summary": "A receipt file is only evidence after its hash, schema, action identity, ledger event, and lifecycle order are recomputed and verified.",
            "math": {
                "valid_receipt": "hash_match AND schema_valid AND action_match AND ledger_event_present",
                "valid_sequence": "valid_receipts AND ordered_stages AND prerequisite_stages_present",
                "rule": "present_file != admissible_evidence",
            },
            "code_references": [
                "nexus_gate/actions/cli.py::_verify_receipt",
                "nexus_gate/actions/cli.py::semantic_verify",
            ],
            "algorithm_card_refs": [
                "semantic-action-chain-verification-algorithm",
                "receipt-dependency-enforcement-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 action-semantic-verify -ActionId \"<id>\"",
                "Tamper with a receipt in a fixture and confirm verification fails closed.",
            ],
            "evidence_surfaces": [
                "reports/nexus_action_semantic_verify_latest.json",
                "ledger/action_receipts.jsonl",
            ],
            "next_versions": ["v0.2: expose semantic failures in Electron action HUD"],
            "boundary": "Semantic verification is local evidence only. It does not prove global correctness or security.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "verified-experience-before-plasticity",
            "version": "0.1.0",
            "title": "Verified Experience Before Plasticity",
            "status": "active",
            "summary": "NEXUS may organize memory from verified experiences, but route calibration remains explicit, bounded, replay-safe, and human authorized.",
            "math": {
                "plasticity_gate": "semantic_pass AND experience_sealed AND learning_eligible AND calibration_authorized",
                "sample_rule": "one experience may inform; three independent experiences may influence",
                "coherence": "geometric_mean(identity, causal, experience, calibration, sample_sufficiency)",
            },
            "code_references": [
                "nexus_gate/actions/cli.py::calibration_status",
                "nexus_gate/actions/cli.py::calibration_apply",
                "nexus_gate/actions/cli.py::adaptive_coherence",
            ],
            "algorithm_card_refs": [
                "adaptive-coherence-measurement-algorithm",
                "emergence-observation-algorithm",
                "replay-safe-calibration-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 adaptive-coherence",
                ".\\scripts\\nexus.ps1 emergence-report",
                ".\\scripts\\nexus.ps1 calibration-status -ActionId \"<experience-id>\"",
            ],
            "evidence_surfaces": [
                "reports/nexus_adaptive_coherence_latest.json",
                "reports/nexus_emergence_observation_latest.json",
                "reports/nexus_calibration_status_latest.json",
            ],
            "next_versions": ["v0.2: benchmark route improvement over uncalibrated baseline"],
            "boundary": "Plasticity changes recommendation pressure only after explicit authorization. It never creates autonomous authority.",
        },
        {
            "schema": "NEXUS_DISCOVERY_CARD.v0.2.0",
            "discovery_id": "breath-as-vital-sign-compression",
            "version": "0.1.0",
            "title": "Breath As Vital-Sign Compression",
            "status": "active",
            "summary": "A small read-only pulse can compress freshness, runtime pressure, and Git scope into an inhale/hold/exhale phase for the next human or AI pass.",
            "math": {
                "pressure": "100 - fail_penalty - warn_penalty - stale_penalty - dirty_penalty",
                "phase": "critical -> hold; canonical_change -> exhale; stale -> inhale; elevated_pressure -> hold; stable -> inhale",
                "rule": "breath != authority AND breath != evolve_pass",
            },
            "code_references": [
                "nexus_gate/breath/pulse.py::build_breath_packet",
                "nexus_gate/breath/pulse.py::_rhythm",
            ],
            "algorithm_card_refs": [
                "breath-pulse-algorithm",
                "runtime-churn-hygiene-algorithm",
                "adaptive-coherence-measurement-algorithm",
            ],
            "replication_steps": [
                ".\\scripts\\nexus.ps1 breath",
                "Inspect reports/nexus_breath_pulse_latest.json for phase, pressure, freshness, and next command.",
            ],
            "evidence_surfaces": [
                "reports/nexus_breath_pulse_latest.json",
                "state/breath/nexus_breath_pulse_latest.json",
            ],
            "next_versions": ["v0.2: surface breath phase in Electron System Monitor and TUI header"],
            "boundary": "Breath is read-only orientation. It cannot execute, self-authorize, calibrate, mutate source, or replace evolve.",
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
