# NEXUS GATE Electron Shell Scaffold

This folder is the local Electron operator HUD surface.

It is presentation only:

```text
read declared evidence surfaces
request allowlisted NEXUS lanes
render operator state
```

It does not own NEXUS logic, execute arbitrary shell commands, mutate graph state, self-authorize, access secrets, write external APIs, bypass evolve, or prove validation.

The current runtime is installed locally with `electron/package-lock.json` committed for reproducible installs. It is not packaged as an EXE and does not own NEXUS logic or authority.
