# NEX Inner Ollama Shell

Version: v0.6.8

## Purpose

The Desktop Entry Portal now prepares the local Ollama backend before Electron opens.

The user no longer needs to open a separate PowerShell window for `ollama serve`.

## Sequence

1. User chooses `1. Open NexusGate`.
2. Portal runs Electron preflight.
3. Portal checks `http://127.0.0.1:11434/api/tags`.
4. If Ollama is already online, it proceeds.
5. If Ollama is offline, the portal starts `ollama serve` as a hidden inner backend process.
6. Portal launches Electron.
7. Electron also enforces a single NEXUS window and verifies Ollama at startup.

## Stability Repairs

- Electron now uses a single-instance lock to prevent repeated NEXUS windows.
- `runNexPython` now passes CPU-stable model environment variables to the model child process.
- Ollama client now parses `NEXUS_OLLAMA_NUM_GPU` safely so bad or blank environment values cannot crash NEX.
- Stop Transmission tracks the active NEX model child, not unrelated lane children.

## Boundary

The inner backend is not a general shell.

It only starts the local Ollama model server. It does not execute model output, mutate repo files, read secrets, write external APIs, or grant authority.
