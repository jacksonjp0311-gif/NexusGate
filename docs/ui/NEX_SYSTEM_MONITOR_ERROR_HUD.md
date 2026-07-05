# NEX System Monitor and Error HUD

Version: v0.7.0

## Purpose

NEX now separates normal chat from system faults.

Normal NEX responses append once in the chat stream. The pinned NEX output card is not used as a mirror.

## Real-Time Monitor

The expanded System Monitor HUD is closed on startup.

The mini monitor remains visible in the feedback panel and refreshes once per second.

The expanded yellow HUD opens only when the operator presses `System Monitor`.

## Stop Transmission

The Stop Transmission button is positioned outside the buffer animation and is enabled only while NEX is processing.

## System Error HUD

When the NEX bridge returns a non-zero result or throws a local runtime exception:

- the NEX chat surface turns red;
- a red system HUD appears;
- the HUD contains a system-compiled report;
- the report explains how the fault happened;
- the report gives deterministic recommendations from local system evidence.

This report is not model-generated AI text. It is compiled from exit code, stderr/stdout, bridge stage, role, and local runtime evidence.

## Boundary

The error HUD is observe/report only.

It does not execute model output, mutate files, grant authority, self-repair, or bypass NEXUS gates.
