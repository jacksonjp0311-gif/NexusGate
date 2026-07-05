# NEX Chat Stack Color Discipline

Version: v0.7.2

## Purpose

The NEX chat stream must behave like a clean conversation stack.

The observed UI failure was visual overlap: older message rows remained visible behind newer rows and the chat stream did not feel smooth.

## Contract

- Chat rows stack vertically with fixed spacing.
- No human/NEX message row may overlap another row.
- Message bodies own their own internal scroll.
- The chat viewport owns the main conversation scroll.
- The input row is fixed-height and does not collide with the stream.
- Human chat is Iceborg blue.
- NEX chat is vibe-coder cyberpunk green.
- System errors remain red and override normal NEX green.

## Boundary

This is a renderer/CSS discipline patch only.

It does not change model authority, repo mutation, local Ollama policy, or governance gates.
