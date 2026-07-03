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
