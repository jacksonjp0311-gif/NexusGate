# NEX Adaptive CPU Inference

Version: v0.7.1

## Purpose

NEX local model calls now use an adaptive CPU-bounded Ollama profile.

The observed system state showed CPU inference working but under pressure:

- CPU load spiked during calls.
- RAM pressure reached the 90%+ range.
- Local model responses could time out.

## Runtime Policy

NEX keeps local model calls CPU-stable and short:

- `num_gpu: 0`
- FAST: `num_ctx=1024`, `num_predict=96`, timeout 150s
- BALANCED: `num_ctx=1536`, `num_predict=140`, timeout 180s
- DEEP: `num_ctx=2048`, `num_predict=180`, timeout 240s
- `keep_alive=10m`

Operators may override with environment variables:

- `NEXUS_OLLAMA_NUM_CTX`
- `NEXUS_OLLAMA_NUM_PREDICT`
- `NEXUS_OLLAMA_NUM_THREAD`
- `NEXUS_OLLAMA_TIMEOUT_SECONDS`
- `NEXUS_OLLAMA_KEEP_ALIVE`

## Error HUD

A model response with `ok: false`, including timeouts, is treated as a system error.

The red HUD is compiled from local system evidence and is not AI-generated.

## Boundary

The adaptive policy does not execute tools, mutate files, read secrets, write external APIs, or grant model authority.
