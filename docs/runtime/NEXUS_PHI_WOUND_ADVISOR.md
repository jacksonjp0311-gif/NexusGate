# NEXUS Phi Wound Advisor

v1.0.0 adds a local Phi-4 Mini wound-advice lane. It is separate from ChatGPT and separate from git authority.

```text
gate fails -> wound-compress -> Phi Wound Advisor -> printed repair plan -> deterministic gate rerun
```

## Commands

```powershell
.\scripts\nexus.ps1 phi-wound -Tag "<failed gate>"
.\scripts\nexus.ps1 phi-wound -Tag "<failed gate>" -CallModel
.\scripts\nexus.ps1 phi-wound-gpu -Tag "<failed gate>"
```

```bash
bash scripts/nexus.sh phi-wound "<failed gate>"
bash scripts/nexus.sh phi-wound --call-model "<failed gate>"
bash scripts/nexus.sh phi-wound-gpu "<failed gate>"
```

## Local GPU Phi-4 Mini hook

Set a local command when you want the GPU model gate:

```powershell
$env:NEXUS_PHI4_MINI_COMMAND = '"C:\Users\jacks\OneDrive\Desktop\Phi4Mini-OrangeCLI\Launch-Phi4MiniCLI.cmd"'
.\scripts\nexus.ps1 phi-wound-gpu -Tag "<failed gate>"
```

The command receives the compact wound prompt through stdin unless it contains `{prompt_file}` or `{prompt}`.

## Boundary

Phi recommends. NexusGate verifies. Human authorizes durable mutation. The compiler decides trust.

Forbidden actions: shell execution, git stage, git commit, git push, network access, secret access, and patch application without human authorization.

## Self-heal roadmap

v1.0.0 is advisor-only. The next layer may add human-authorized deterministic self-heal lanes, but the model itself will still not receive repo authority.
