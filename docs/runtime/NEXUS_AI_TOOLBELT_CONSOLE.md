# NEXUS AI Toolbelt Console

Toolbelt Console Integration.

## Bash / WSL Smoke Policy

PowerShell is the primary Windows operator surface. Bash parity source must remain present in `scripts/nexus.sh`, but runtime Bash smoke is environment-conditional: Git Bash, WSL, or another functional `bash` must be available. If Windows reports that WSL has no installed distributions, the local closer records a skipped Bash runtime smoke instead of treating missing WSL as an architecture failure.
