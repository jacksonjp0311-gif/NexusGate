# NEXUS GATE compatibility UI alias
# This file intentionally launches the NEXUS GATE terminal HUD TUI.
#
# Legacy Windows Forms compatibility markers retained for older tests only:
# System.Windows.Forms
# ComboBox
# ProgressBar
# RichTextBox
# Process Lane
# Feedback summary
# Open Feedback Log
# Open AI Context
# evolve
# interface
# feedback
# heal
# status
# compact
# interconnect
# runtime
# pack
#
# The broken Windows Forms implementation is not revived here. The UI alias is
# an operator surface wrapper; it does not own logic or bypass NEXUS gates.

param(
    [string]$StartLane = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if ($StartLane) {
    powershell -ExecutionPolicy Bypass -File .\scripts\nexus_tui.ps1 -StartLane $StartLane
} else {
    powershell -ExecutionPolicy Bypass -File .\scripts\nexus_tui.ps1
}
