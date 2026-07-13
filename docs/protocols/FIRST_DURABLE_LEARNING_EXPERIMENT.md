# First Durable Learning Experiment

The first durable learning run should use a low-risk registered route, preferably `nexus.cortex-refresh`.

Required flow:

```powershell
.\scripts\nexus.ps1 first-learning-readiness
.\scripts\nexus.ps1 action-recommend
.\scripts\nexus.ps1 action-authorize -ActionId "<id>"
.\scripts\nexus.ps1 action-execute -ActionId "<id>"
.\scripts\nexus.ps1 action-effects -ActionId "<id>"
.\scripts\nexus.ps1 action-validate -ActionId "<id>"
.\scripts\nexus.ps1 action-finalize -ActionId "<id>"
```

The run must prioritize observability over novelty. If the epoch is working-tree-only, the action may complete but durable learning must remain blocked.
