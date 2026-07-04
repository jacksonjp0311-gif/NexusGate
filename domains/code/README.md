# Code Domain

Purpose: study software/code patterns and convert them into tests, schemas, reproducible commands, and gates.

Allowed claims: tested behavior, source-backed API behavior, clearly marked implementation hypotheses.

Blocked claims: production readiness without gates, correctness proof from passing local tests alone, unsupported performance claims.

Required evidence: tests, lint/type status when applicable, reproducible commands, changed files, claim boundary.

Safe study modes: code pattern cards, test design, compiler gate design, failure-mode mapping.

Handoff surfaces: `reports/nexus_domain_intelligence_report_latest.json`, `domains/code/`.

Compiler gates: `python -m unittest discover -s tests`, `.\scripts\nexus.ps1 domain`, `.\scripts\nexus.ps1 evolve`.

Claim boundary: code study is not correctness proof or production readiness.
