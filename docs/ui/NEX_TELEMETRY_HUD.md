# NEX Telemetry HUD

Version: v0.6.6

## Purpose

NEX now has a local telemetry station inside the Electron HUD.

The station reads local system pressure and presents it as a cyberpunk yellow popout HUD.

## Surfaces

- CPU load
- RAM pressure
- GPU name
- GPU utilization when Windows exposes GPU Engine counters
- C drive free space
- Ollama / llama-server process presence

## Chat Stability

The center chat viewport is now fixed and scroll-bound. Long NEX responses scroll inside their message body instead of expanding the entire chat surface.

## Transmission Control

A red `Stop Transmission` button can stop the active NEX model call. It only stops the active NEX transmission child process.

It does not grant shell authority, execute model output, mutate repo files, or authorize autonomous repair.

## CPU Fallback

NEX local model calls default to CPU-stable operation:

- `CUDA_VISIBLE_DEVICES=-1`
- `NEXUS_OLLAMA_NUM_GPU=0`
- Ollama request option `num_gpu: 0`

This protects the Electron bridge from the observed CUDA runner crash while preserving human-authorized local reasoning.

## Boundary

Telemetry is observe-only.

NEX may use telemetry as context for recommendations, but it may not self-authorize repairs or mutate the system.
