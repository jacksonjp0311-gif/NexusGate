# Nexus Reflective Local Loop

Version: v0.1.4

Purpose: run validation gates through a local reflective loop that captures failure, preserves the original exit code, compiles the wound, applies known safe self-heals, retries, and prints a final human-readable stability lock.

This is not autonomous authority. It only applies narrow deterministic self-heals that are encoded in the script and visible in the output.

## Loop

```text
run gate
-> capture stdout/stderr
-> preserve original exit code
-> compile failure
-> classify known wound
-> apply safe local self-heal
-> retry
-> log reflective change
-> finish with WHAT WAS DONE / REFLECTIVE CHANGE LOG / VERIFIER / STABILITY LOCK
```

## Current safe self-heals

```text
unittest module import wound:
python -m unittest tests.test_x
-> python -m unittest discover -s tests -p test_x.py

git push stderr wound:
raw git push redirection
-> cmd.exe wrapped push capture
```

Unknown failures stay blocked and produce a compact report.
