# NEX HANDOFF Action Shell

Version: v0.7.4

## Purpose

The HANDOFF selection is the ChatGPT/Codex action lane.

The human should not need to manually open PowerShell to run scripts supplied by ChatGPT. PowerShell remains the hidden execution substrate behind Electron.

## Human Flow

1. Select `HANDOFF / ChatGPT-Codex`.
2. Paste an action script into NEX chat:

```powershell
/handoff run
```powershell
# script goes here
```
```

3. Electron writes the script under `reports/handoff_queue/<timestamp>/handoff_action.ps1`.
4. Electron runs it with hidden `powershell.exe`, `shell: false`, and repo root as cwd.
5. NEX chat returns a compact action report.

## Output Contract

- What ran
- Result
- Exit code
- Script path
- Report path
- Human-readable meaning
- Evidence
- Next allowed action
- Boundary

## Governance Boundary

This does not give NEX autonomous shell authority.

Execution requires a human-initiated `/handoff run` message while the local voice is set to HANDOFF.

Model output cannot self-execute, promote memory, mutate files without human authorization, or bypass the repo gates.
