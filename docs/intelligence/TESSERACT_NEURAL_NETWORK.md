# Tesseract Neural Network v0.2.0

TNN is now a NexusGate-local neural chat brain targeting Mistral through Ollama.

```text
NexusGate chat
â†’ TNN surface
â†’ TNN chat engine
â†’ TNN context + memory + receipts
â†’ tnn-mistral:latest / mistral:latest
â†’ snappy operator response
```

## Weight strategy

Raw Mistral weights are not copied into the repo. TNN adapts the existing local `mistral:latest` weights through an Ollama Modelfile:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\Tesseract Neural Network\brain\build_tnn_mistral.ps1"
```

This creates:

```text
tnn-mistral:latest
```

## Boundary

TNN is recommendation-only. It can chat and reason through local Mistral, but it cannot execute shell commands, mutate files, scrape, perform live API pulls, or claim autonomous authority.


## v0.2.0E Fast Timeout Seal

Ollama socket timeouts are converted into bounded TNN chat packets instead of router crashes. Snappy mode uses a 6-second fast gate, 1024 context, and 120-token response target.
## v0.2.0F Chat Renderer Seal

	nn-chat now renders the actual TNN response body from eports/nexus_nn_router_report_latest.json instead of only printing the router envelope.
## v0.2.0G Viewer Renderer Seal

	nn-chat now invokes the router and then renders the actual TNN response body through Tesseract Neural Network/brain/view_latest_chat.py. This avoids injecting a large PowerShell helper into the command switch and keeps the shell parser stable.
## v0.2.0H Fast Prewarm Seal

TNN disables fallback on timeout by default so a slow model does not double latency. prewarm_tnn_mistral.py keeps 	nn-mistral:latest resident before chat. Snappy mode targets 6 seconds, 768 context, and 80 generated tokens.
## v0.2.0I Turbo Context Seal

TNN turbo chat removes heavy memory/context from the default path. It sends only intent, core local flags, and the boundary to Mistral. Deep memory can be re-enabled with TNN_INCLUDE_MEMORY=1. Turbo mode targets 512 context and 48 generated tokens.
## v0.2.0J Streaming Chat Seal

	nn-chat now uses Tesseract Neural Network/brain/stream_chat.py for live operator chat. It prints the chat header immediately, streams Ollama tokens as they arrive, writes TNN memory, and avoids waiting for the router envelope before showing the answer.
## v0.2.0K Operator Alignment Seal

TNN streaming chat is locked to NexusGate repo/product engineering. If local Mistral drifts into offensive cyber language such as targets, attack strategy, entry points, exploitation, or credential access, the stream pivots to a safe operator-alignment response.
## v0.2.0L Stream Guard v2 Seal

TNN streaming chat now buffers short output spans before printing, allowing defensive engineering phrases such as harden against vulnerabilities while blocking offensive drift phrases before they reach the terminal. It records time-to-first-token and total latency.
## v0.2.0M Fast Scaffold Seal

TNN chat now prints an immediate safe operator scaffold before waiting for local Mistral. The fast lane uses an 8-second model budget by default; stream_chat.py --deep keeps the longer full-Mistral path for deeper reasoning.
## v0.2.0N Runtime Health Seal

TNN now includes ench_tnn_runtime.py, which runs the fast scaffold chat lane, captures scaffold/TTFT/total latency, classifies the local model state as hot/warm/slow/offline, and writes eports/tnn_runtime_health_latest.json for future Electron health badges.
## v0.2.0O Partial Stream Hygiene Seal

TNN no longer prints useless partial model fragments such as a single word when the fast model budget is hit. Meaningful partials are labeled as TNN // MISTRAL PARTIAL; otherwise the scaffold remains primary and the health report records model_budget_hit, partial_chars, and stream completion state.
## v0.2.0P Operator Command Seal

TNN now exposes shell-level operator commands:

- 	nn-chat â€” instant scaffold plus short-budget streaming Mistral lane.
- 	nn-health â€” writes and prints the latest TNN runtime health badge report.
- 	nn-warm â€” prewarms 	nn-mistral:latest.
- 	nn-deep â€” runs the longer full-Mistral stream path.

This makes TNN usable as a local operator surface rather than only a Python backend.
## v0.2.0Q Operator Command ValidateSet Seal

The 	nn-health, 	nn-warm, and 	nn-deep commands are now admitted through the scripts/nexus.ps1 ValidateSet gate and wired to their switch handlers. This repairs the v0.2.0P shell whitelist wound.
## v0.2.0R Warm Hygiene Seal

	nn-warm is now bounded and operator-safe. Slow/cold Ollama responses produce TNN WARM // NOT READY plus eports/tnn_warm_latest.json instead of raw Python traceback. The scaffold lane remains available even when local Mistral is cold.
## v0.2.0S Model Doctor Seal

TNN now exposes 	nn-doctor, a local Ollama/Mistral diagnostic command. It checks Ollama CLI/API availability, installed/running model state, probes 	nn-mistral:latest, classifies the backend, and writes eports/tnn_model_doctor_latest.json plus .md.
## v0.2.0T Phi-4-mini Hot Lane Seal

TNN hot-lane chat now targets 	nn-phi4-mini:latest, built from the first available Phi-4-mini Ollama candidate. Mistral remains preserved as the 	nn-deep lane via 	nn-mistral:latest. Phi-3 models are removed only after Phi-4-mini is pulled, the TNN hot model is created, and the smoke test passes.
## v0.2.0U Phi-4 Hot Lane Resume Seal

Close U resumes the Phi-4-mini hot lane after the Close T validation harness wound. Phi-4-mini was successfully pulled, 	nn-phi4-mini:latest was created, Phi-3 was removed, and the repo now defaults the TNN hot lane to Phi-4-mini while preserving Mistral as 	nn-deep.
## v0.2.0V Hot Lane Label Hygiene Seal

TNN stream labels are now dynamic. Phi-4-mini hot lane output renders as TNN // HOT MODEL STREAM and Tesseract Neural Network/phi4-mini-hot-brain, while Mistral deep lane output renders as TNN // DEEP MODEL STREAM and Tesseract Neural Network/mistral-deep-brain.
