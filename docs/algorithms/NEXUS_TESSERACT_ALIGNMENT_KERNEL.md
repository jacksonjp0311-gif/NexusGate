# NEXUS Tesseract Alignment Kernel v0.8.3A

## Kernel

```text
K = Intent x Evidence x Authority x Context
```

Each request becomes a four-coordinate state before repair or compounding.

## Axis Contracts

| Axis | Question | Gate |
|---|---|---|
| Intent | What is the human asking? | Must be explicit enough to route. |
| Evidence | What does the repo prove? | Must cite tests, compiler, docs, logs, or state. |
| Authority | Who can mutate? | Human authorization required. |
| Context | What is relevant now? | Must be sliced, not dumped. |

## Theory Mappings

| Theory | Nexus Function |
|---|---|
| LFTE | typed depth projection |
| EIMT | drift-gated episodic retrieval |
| RCMA | cross-modal latent remapping |
| TRAT | attractor persistence and bounded deviation |

## Alignment Score Contract

```text
axis_complete = count(populated_axes) / 4
drift_ok = EIMT drift <= threshold
authority_ok = human approval or read-only recommendation
evidence_ok = compiler/test/doc evidence present
attractor_ok = TRAT deviation within bounded route

geometry_pass = axis_complete == 1 and drift_ok and authority_ok and evidence_ok and attractor_ok
```

## Runtime Rule

No memory promotion, model-role tuning, context-slice promotion, or repair continuation may claim a geometry pass without an emitted manifest or test evidence.


## Runtime Packet Algorithm v0.8.3C

```text
issue -> compact intent -> evidence refs -> authority mode -> context refs -> axis score -> read-only geometry packet
```

The runtime stub always refuses repair authority. It prepares speed packets; it does not mutate.
