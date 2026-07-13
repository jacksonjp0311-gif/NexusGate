param(
    [ValidateSet("begin", "status", "end", "abort", "verify", "list", "replay-verify")]
    [string]$Command = "status",
    [string]$Provider = "codex",
    [string]$SessionId = "manual",
    [string]$InteractionId = "",
    [string]$Tag = "Declared AI touch session.",
    [string]$Disposition = "pending_review"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

switch ($Command) {
    "begin" { python -m nexus_gate.intelligence.cli touch-begin --root . --provider $Provider --session-id $SessionId --intent $Tag --json }
    "status" { python -m nexus_gate.intelligence.cli touch-status --root . --interaction-id $InteractionId --json }
    "end" { python -m nexus_gate.intelligence.cli touch-end --root . --interaction-id $InteractionId --disposition $Disposition --json }
    "abort" { python -m nexus_gate.intelligence.cli touch-abort --root . --interaction-id $InteractionId --json }
    "verify" { python -m nexus_gate.intelligence.cli touch-verify --root . --interaction-id $InteractionId --json }
    "list" { python -m nexus_gate.intelligence.cli touch-list --root . --json }
    "replay-verify" { python -m nexus_gate.intelligence.cli touch-replay-verify --root . --json }
}
