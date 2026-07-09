# PETRI 005Q2 - Test Harness Seal

## Wound
005Q applied the emergency visual recovery and passed static contract, but its PowerShell test harness ran:

`python -m unittest discover -s tests`

directly with PowerShell redirection. Python unittest writes progress dots to stderr, and PowerShell promoted that native stderr stream into `NativeCommandError` before the script could inspect the exit code.

## Patch
005Q2 does not reintroduce the invasive 005O/005P/005P2 overlays. It verifies the 005Q safe recovery state and runs strict tests through a Python subprocess capture layer:

- stdout and stderr are captured safely,
- stderr progress dots no longer become a PowerShell parser/native-command failure,
- strict exit code is still enforced,
- recovery binding remains `drugInjectionSafeRecovery005Q.js` only.

## Claim boundary
Harness and recovery verification only. No wet-lab, diagnostic, treatment, dosing, susceptibility, affinity, species-ID, clinical, or biosafety claim is added.
