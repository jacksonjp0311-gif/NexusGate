# Tesseract Neural Network v0.1.1

TNN is now self-contained inside NexusGate.

```text
NexusGate/
└─ Tesseract Neural Network/
   ├─ tnn_surface.py
   ├─ refresh_from_neuralforge.py
   ├─ receipts/receipt_bundle_latest.json
   ├─ state/tnn_state_latest.json
   ├─ schemas/receipt_bundle.schema.json
   ├─ manifest.json
   ├─ receipt_paths.json
   └─ portal_entry.json
```

Runtime does not require NeuralForge. NeuralForge is only an explicit refresh source.

## Command

```powershell
.\scripts\nexus.ps1 tnn -Tag "Read Tesseract Neural Network state." -CallModel
```

## Boundary

Recommendation-only. No shell execution, patch application, main-branch mutation, live API pulls, scraping, or autonomous authority.
