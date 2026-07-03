# NEXUS GATE v0.2.2 Feedback + Interconnect Surface

This version adds three operator lanes:

```powershell
.\scripts\nexus.ps1 feedback
.\scripts\nexus.ps1 interconnect
.\scripts\nexus.ps1 compact
```

And one combined evolution lane:

```powershell
.\scripts\nexus.ps1 evolve
```

## Purpose

The system is moving from isolated compiler reports into an adaptive feedback loop:

```text
compiler reports
  -> evidence compaction pressure
  -> interconnect graph
  -> feedback report
  -> next bounded action
```

## Laws

```text
No feedback without compiled reports.
No interconnect without governed edges.
No compaction without manifest.
No CLI evolution without human-readable surface.
No new runtime lane without feedback visibility.
```

## Reports

```text
reports/nexus_feedback_report_latest.json
reports/nexus_interconnect_report_latest.json
reports/nexus_evidence_compaction_report_latest.json
state/interconnect_graph.v0.2.2.json
```

Claim boundary: this is local development evidence, not production validation.

## v0.2.6 AI Agent Interconnection

The interconnect graph now declares AI/operator process surfaces as governed nodes:

```text
feedback:ai_context
  -> ai_agent:codex_process
  -> feedback:operator_packets
  -> operator:tui
  -> reports:tui_exports
  -> ai_agent:codex_process
```

This captures the local Codex/ChatGPT handoff loop as evidence-routed architecture. It does not grant autonomous write authority, external API authority, memory promotion authority, or correctness claims.

New laws:

```text
No AI handoff without feedback context.
No AI handoff without feedback log.
No autonomous self-authorization.
No UI bypass of compiler/evolve gates.
The UI must never own the logic.
Certificate before compounding.
```

## v0.2.7 Domain Interconnection

The interconnect graph now includes domain profiles for CLI formatting, bio, chem, coding, and neural model routes.

```text
terminal:cli_format
domain:bio
domain:chem
domain:coding
domain:neural
schema:domain_interop_profile
```

These nodes provide routing contracts and evidence expectations. They do not validate biology, chemistry, source code correctness, model correctness, or safety.
