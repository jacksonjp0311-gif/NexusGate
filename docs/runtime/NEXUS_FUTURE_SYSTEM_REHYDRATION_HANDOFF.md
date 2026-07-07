# Nexus Future System Rehydration Handoff

Version: v0.1.5

Purpose: allow a future human, ChatGPT session, Codex session, or local agent with no chat context to enter NexusGate and continue development from repository evidence.

No chat context required. The repository is the origin.

## Read First

```text
README.md
docs/README.md
docs/ENTRYPOINTS.md
docs/runtime/NEXUS_SCRIPT_EVOLUTION_RUN_CONTRACT.md
docs/runtime/NEXUS_REFLECTIVE_LOCAL_LOOP.md
docs/runtime/NEXUS_FAILURE_INTELLIGENCE_DISTRIBUTOR.md
state/process/nexus_process_rehydration_manifest.v0.1.5.json
```

## Current Process Spine

```text
human intent
-> repo rehydration
-> smallest safe patch
-> reflective local run
-> compact failure intelligence
-> safe self-heal for known wounds only
-> retry
-> verifier
-> residue clean
-> commit only when authorized
-> push only when authorized
-> stability lock
```

## Authority Boundary

The loop may classify, suggest, patch intended files, run verifiers, and retry deterministic known-safe repairs inside an explicitly authorized script.

The loop may not claim autonomous authority, production security, correctness proof, perfect sandboxing, or memory truth.

## Future Operator Rule

Before generating a new script, load the latest process manifest and latest failure intelligence packet. If they contradict chat memory, repository evidence wins.
