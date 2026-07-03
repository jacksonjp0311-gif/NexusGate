# NEXUS GATE Feedback System

This directory is the canonical two-way feedback interface for humans, Codex-like agents, ChatGPT sessions, and future AI systems working on this repository.

## Read Order for Any AI

```text
1. state/ai_feedback_context_latest.json
2. docs/feedback/FEEDBACK_LOG.md
3. reports/nexus_feedback_report_latest.json
4. reports/nexus_self_healing_report_latest.json
5. reports/nexus_interconnect_report_latest.json
6. reports/nexus_evidence_compaction_report_latest.json
```

## Purpose

NEXUS GATE is a governed agentic transfer boundary. The feedback system lets an AI understand:

```text
current health
evidence pressure
interconnect graph status
self-healing recommendation state
next bounded action
allowed command surface
claim boundaries
```

## Two-Way Protocol

```text
AI reads the feedback context.
AI proposes a typed recommendation.
AI does not assume autonomous write authority.
Human-authorized patch applies the change.
Patch runs .\scripts\nexus.ps1 evolve.
Feedback interface appends FEEDBACK_LOG.md.
```

## Hard Locks

```text
No feedback without compiled reports.
No AI handoff without ai_feedback_context_latest.json.
No self-healing without typed recommendation.
No recommendation may write directly.
No dry-run may write target surfaces.
No apply gate may execute without explicit human authorization.
No repair closure without validation evidence.
No autonomous commit from self-healing recommendation.
```

## PowerShell Surface

```powershell
.\scripts\nexus.ps1 interface
.\scripts\nexus.ps1 feedback
.\scripts\nexus.ps1 heal
.\scripts\nexus.ps1 evolve
```

Claim boundary: this feedback system is local development evidence only. It does not prove correctness, security, safety, production readiness, external validation, or autonomous authority.
