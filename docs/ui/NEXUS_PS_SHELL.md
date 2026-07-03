# NEXUS GATE PowerShell Operator Shell

The NEXUS GATE PowerShell Operator Shell is now a compatibility alias for the Hermes-style terminal TUI launched from PowerShell.

## Command

```powershell
.\scripts\nexus.ps1 ui
```

or directly:

```powershell
.\scripts\nexus_ui.ps1
```

## Interface

The compatibility surface preserves these older Windows Forms markers for tests and handoff continuity:

```text
System.Windows.Forms
ComboBox
ProgressBar
RichTextBox
Process Lane dropdown
RUN / STOP / CLEAR controls
Open Feedback Log
Open AI Context
Progress / buffer bar
Colored output stream
Feedback summary panel
Human feedback lane
AI feedback lane
Debugging lane
Self-healing lane
Reflection / next-action lane
```

The active implementation is `scripts/nexus_tui.ps1`; `scripts/nexus_ui.ps1` launches that terminal TUI instead of reviving the broken Windows Forms implementation.

## Color Meaning

```text
Blue    = NEXUS / feedback / AI context events
Green   = pass / OK
Yellow  = warning / pressure
Red     = fail / error
White   = neutral output
```

## Purpose

This UI is an operator surface over the existing governed CLI. It does not bypass NEXUS gates.
