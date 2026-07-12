# Causal Action Receipt Protocol

The receipt lifecycle is:

`PROPOSED -> AUTHORIZED -> EXECUTING -> EXECUTED -> VALIDATED -> LEARNABLE`

Terminal states are:

`DENIED`, `EXPIRED`, `STALE`, `ABORTED`, `FAILED`, `CONFOUNDED`, `INVALID`, `NOT_LEARNABLE`.

Authorization must bind:

- `command_registry_id`
- normalized arguments
- arguments hash
- pre-action Source Epoch

Execution must resolve through `registry/nexus_command_registry.v2.6.2.json`. Raw shell strings are not authority objects.

Validation and learning require epoch integrity, authorization binding, execution binding, effect comparison, validation coverage, and low confounder pressure.
