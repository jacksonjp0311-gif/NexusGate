# NEX Append-Only Chat

Version: v0.6.9

## Purpose

NEX chat responses now appear once in the conversation stream.

Before this repair, the same NEX answer could appear twice:

1. as a normal chat message; and
2. mirrored into the pinned `NEX AI Output` card.

That made the interface feel like it was echoing itself.

## New Chat Contract

- The pinned NEX output card keeps the startup greeting/status.
- Human messages append downward.
- NEX responses append downward.
- Long responses scroll inside their message body.
- The full chat viewport scrolls downward as the conversation grows.
- NEX does not mirror the same answer into the pinned card.

## Stop Transmission

The Stop Transmission button is enabled only while NEX is actively processing.

It remains bounded to the active NEX child process and does not grant shell authority.

## Boundary

This is a UI behavior repair only.

It does not change model authority, repo mutation rules, or the human authorization boundary.
