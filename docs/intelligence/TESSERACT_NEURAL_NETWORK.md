# Tesseract Neural Network v0.2.0

TNN is now a NexusGate-local neural chat brain targeting Mistral through Ollama.

```text
NexusGate chat
→ TNN surface
→ TNN chat engine
→ TNN context + memory + receipts
→ tnn-mistral:latest / mistral:latest
→ snappy operator response
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
