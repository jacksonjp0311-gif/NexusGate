# Tesseract Neural Network

Self-contained NexusGate-local neural chat brain.

TNN uses local Mistral through Ollama:

```text
brain/chat_engine.py
brain/ollama_adapter.py
brain/context_builder.py
brain/memory_store.py
brain/system_prompt.md
brain/Modelfile.tnn-mistral
```

Build the adapted local model tag:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\Tesseract Neural Network\brain\build_tnn_mistral.ps1"
```

Run through NexusGate:

```powershell
.\scripts\nexus.ps1 tnn -Tag "Think through the next move." -CallModel
```

Boundary: no raw weights in repo, no hidden chain-of-thought exposure, no shell execution, no patch application, no live API pull, no scraping, no autonomous authority.
