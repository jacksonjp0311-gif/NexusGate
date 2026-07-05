# NEX Dev Mode / Handoff Console

Version: v0.7.6

## Purpose

Dev Mode is the lightweight coding room for NEXUS Gate.

The full Electron UI remains the operator dashboard. Dev Mode gives the human a faster local surface for:

- git status
- runtime residue cleanup
- compiler summary
- full tests
- latest HANDOFF report review
- opening the full Electron UI when needed

## Launcher Position

The desktop entry portal exposes:

1. Open NexusGate
2. Dev Mode / Handoff Console
3. Status / health surface
4. Terminal TUI surface
5. NN router health
6. Ask NEXUS router
7. Open repo folder

## Boundary

Dev Mode streams local evidence and runs existing repo commands.

It does not grant model-output authority, bypass tests, bypass the compiler, or mutate durable source without human authorization.
