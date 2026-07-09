# NEXUS Phi Wound Ollama Adapter

v1.0.1 adds a non-interactive local adapter for Phi-4 Mini through Ollama.

The human Orange CLI launcher remains useful for manual chat, but NexusGate must not call an interactive `Read-Host` loop during a gate. The adapter calls the local Ollama HTTP endpoint directly and prints one compact JSON object to stdout.

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\nexus-gate"
.\scripts\nexus.ps1 wound-compress -Tag "adapter live test"
.\scripts\nexus.ps1 phi-wound-gpu -Tag "adapter live test"
```

If Ollama is not running:

```powershell
ollama serve
ollama pull phi4-mini
```

Boundary: Phi recommends. NexusGate verifies. Human authorizes durable mutation. The adapter has no git, shell, secret, network-external, patch-apply, or autonomous authority.
