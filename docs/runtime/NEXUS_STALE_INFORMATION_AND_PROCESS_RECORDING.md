# Nexus Stale Information and Process Recording Rule

Version: v0.1.5

Purpose: prevent root README drift and preserve the actual process used to evolve NexusGate.

## Stale Information Rule

The root README is compact and must stay under the test-enforced line ceiling. It should name only current operator organs and link to deeper docs.

When a runtime organ changes, update:

```text
README.md
docs/runtime/*
state/process/*
tests/*
```

## Process Recording Rule

Every evolution script must leave future systems with:

```text
WHAT WAS DONE
REFLECTIVE CHANGE LOG
VERIFIER
STABILITY LOCK
```

The stability lock must include branch, commit, push status, workspace status, and whether residue cleanup passed.

## Clean Lock Rule

A script must not report final stability while `git status --short` is dirty, except when intentionally showing a blocked state.

## Tracked Report Rule

Never delete tracked report files with `Remove-Item .\reports\*.json`.

Use:

```powershell
git restore --worktree -- .\reports
git clean -fd -- .\reports
git restore --worktree -- .\reports
```

Tracked files are restored. Untracked generated files are removed. This prevents false residue wounds caused by deleting historical evidence files.

## Untracked Directory Rule

Use `git status --short --untracked-files=all` for pre-stage residue checks. Plain `git status --short` can collapse intended new files into directory summaries such as `?? state/process/`, which causes false residue failures.
## Neural Activity visual close lesson

The failure sequence was useful:

```text
- iframe collapsed
- canvas preview collapsed
- SVG/DOM preview finally displayed
- surrogate preview was incorrect
- AA fixed the architecture by embedding the real source program
```

Lesson: once visibility is solved, return to the real source of truth rather than preserving a workaround.
