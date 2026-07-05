# NEX Hidden Ollama Backend

Version: v0.6.7

## Purpose

The Electron entry portal now starts or verifies the local Ollama backend invisibly before the NEX window opens.

This removes the need for a second PowerShell box dedicated to `ollama serve`.

## Startup Contract

On Electron startup:

1. NEX checks `http://127.0.0.1:11434/api/tags`.
2. If Ollama is already running, NEX uses the existing local service.
3. If Ollama is not running, NEX starts `ollama serve` as a hidden detached backend process.
4. The backend is launched with CPU-stable defaults:
   - `CUDA_VISIBLE_DEVICES=-1`
   - `NEXUS_OLLAMA_NUM_GPU=0`
   - `OLLAMA_MODELS=%USERPROFILE%\.ollama\models` unless already provided.

## Boundary

The backend launcher is not a general shell.

It only starts the local Ollama model server. It does not execute model output, mutate repo files, request secrets, write external APIs, or authorize repairs.

## Human Rule

Models recommend. Human authorizes durable mutation.
