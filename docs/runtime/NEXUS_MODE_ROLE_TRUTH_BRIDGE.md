# NEXUS Mode Role Truth Bridge v0.2.0ZX

This seal repairs the failed ZW bridge by writing manifest and bridge files as UTF-8 without BOM and removing literal legacy role tokens from active bridge/manifest surfaces.

## Role truth

- FAST -> tnn-phi4-mini:latest
- BALANCED -> tnn-phi4-mini:latest
- DEEP -> tnn-mistral:latest
- TNN -> Tesseract Neural Network/phi4-mini-hot-brain
- HANDOFF -> ChatGPT-Codex relay

Boundary remains recommendation-only.
## v0.2.0ZY Router Test Alignment

The NN router contract and tests now align with the active Phi-4-mini truth layer. FAST and BALANCED expect 	nn-phi4-mini:latest instead of the retired Phi-4-mini model family.
## v0.2.0ZZ Fake Ollama Fixture Alignment

The NN router fake Ollama inventory fixture now creates 
egistry.ollama.ai/library/tnn-phi4-mini/latest, producing 	nn-phi4-mini:latest in router inventory instead of the retired Phi-4-mini mini fixture.

## v0.2.0ZAC Active Stale-Token Repair

The repair scans active router/truth files, records stale token hits before patching, rewrites files as UTF-8 without BOM, normalizes the fake Ollama fixture to `tnn-phi4-mini/latest`, and preserves model inventory truth as `tnn-phi4-mini:latest`.
