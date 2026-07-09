# NEXUS Toolbelt Bash Smoke Policy

Bash parity source is required for every Toolbelt console command.

Bash runtime smoke is environment-conditional on Windows. If `bash` resolves to WSL but WSL has no installed Linux distribution, the runtime smoke is recorded as an environment skip, not an architecture failure.

Required source parity tokens:

```text
toolbelt)
toolbelt-start)
toolbelt-dashboard)
toolbelt-next)
toolbelt-ship)
toolbelt|toolbelt-dashboard
```

PowerShell remains the primary Windows operator surface. Bash/Git Bash/WSL parity is source-verified and runtime-smoked only when a functional Bash runtime exists.
