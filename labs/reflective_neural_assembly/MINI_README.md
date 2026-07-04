# NEXUS Reflective Neural Assembly Lab v0.5.0

This is an isolated NEXUS lab for NeuralForge-inspired adaptive telemetry and recommendation experiments.

It is:

- isolated from NEXUS core command lanes
- recommendation-only
- parent intelligence emitter compatible
- telemetry codec compatible
- standard-library-first
- optional-neural only when local dependencies already exist

It is not:

- an autonomous repair engine
- an arbitrary shell surface
- an external API writer
- a parent repo mutator
- a secret reader
- an authority source
- no self-authorization
- no arbitrary shell
- no parent repo mutation

Boundary law:

```text
NeuralForge observes, learns, predicts, and recommends.
NEXUS gates.
The human authorizes.
No neural layer self-applies fixes.
```

Run:

```powershell
python .\labs\reflective_neural_assembly\run_neural_assembly.py --intent "What should we do next?"
```

Test:

```powershell
python -m unittest discover -s labs/reflective_neural_assembly/tests
```

Report:

```text
labs/reflective_neural_assembly/reports/neural_assembly_report_latest.json
```
