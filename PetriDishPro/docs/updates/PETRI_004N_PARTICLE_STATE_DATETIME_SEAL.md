# PETRI 004N â€” Particle State Datetime Seal

## Wound
004M correctly installed the particle-state module, but artifact generation failed at Gate 04 because `particle_state.py` used an invalid dynamic datetime import:

`__import__("datetime").datetime.datetime.utcnow()`

On this runtime that resolves `datetime` to the class instead of the module chain, causing:

`AttributeError: type object 'datetime.datetime' has no attribute 'datetime'`

## Patch
004N resumes from 004M Gate 03 and fixes only the wounded continuation path:

- replaces the bad datetime call with `dt.datetime.now(dt.timezone.utc)`,
- regenerates particle-state artifacts,
- ensures `reports/bio/petri_particle_state_latest.json` exists,
- adds Electron access for `readParticleState`,
- adds renderer fallback to prefer Python artifact cells when available.

## Claim boundary
Particle-state artifacts are simulated spatial state. They are not microscopy evidence, species identification, clinical data, treatment guidance, wet-lab proof, or biosafety evidence.
