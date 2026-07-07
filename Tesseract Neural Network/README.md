# Tesseract Neural Network

Self-contained minimal NexusGate NN core for Tesseract governance state.

This folder intentionally avoids vendoring NeuralForge. Runtime reads NexusGate-local receipt cache first:

```text
receipts/receipt_bundle_latest.json
state/tnn_state_latest.json
```

NeuralForge is optional and only used through explicit refresh:

```powershell
python ".\Tesseract Neural Network\refresh_from_neuralforge.py" --json
```

Boundary: recommendation-only, no shell execution, no patch application, no live API pull, no scraping, no autonomous authority.
