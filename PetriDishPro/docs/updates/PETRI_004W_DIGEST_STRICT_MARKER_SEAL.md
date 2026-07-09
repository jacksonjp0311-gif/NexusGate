# PETRI 004W - Digest Strict Marker Seal

## Wound
004V successfully generated the compressed failure digest, but its self-check looked for the literal text `-Strict` in `RUN_TESTS_DIGEST.ps1`.

The wrapper supported strict behavior through `$Strict`, but did not contain the literal marker.

## Patch
004W adds a static contract marker to the wrapper:

- `PETRI 004W STRICT CONTRACT MARKER`
- `-Strict`

The runner still uses cmd.exe redirection so unittest stderr is captured as raw data and digest output remains readable.

## Claim boundary
Diagnostics only. No simulation, clinical, wet-lab, drug, antibody, diagnostic, treatment, species-ID, or biosafety claims are changed.
