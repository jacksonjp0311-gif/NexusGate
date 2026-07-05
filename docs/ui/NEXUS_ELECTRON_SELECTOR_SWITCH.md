# NEXUS Electron Selector Switch

Version: v0.6.3 portal UI surface

## Purpose

The Electron HUD now includes a subtle local reasoning selector.

The selector begins as a quiet triangular glyph. When the selected local voice changes, it animates into a Celtic-knot-like form, pulses the role color, and settles back into a crystalline state.

## Roles

```text
FAST     -> Phi-3 quick recommendation voice
BALANCED -> Phi-3 balanced recommendation voice
DEEP     -> Mistral deeper recommendation voice
HANDOFF  -> ChatGPT/Codex packet mode
```

## Boundary

The selector is UI planning context only.

It does not:

- call models
- execute shell
- mutate repo files
- grant authority
- bypass NEXUS gates
- promote memory

The selector shows the recommended governed PowerShell command. The human chooses whether to run it.

## Intended Feel

Subtle until clicked. On interaction:

```text
triangle -> knot pulse -> crystalline settle
```

This reinforces the NEXUS principle:

```text
selection is not execution
recommendation is not authority
```
