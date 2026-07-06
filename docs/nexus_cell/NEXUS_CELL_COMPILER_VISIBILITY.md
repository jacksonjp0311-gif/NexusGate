# NexusCell Compiler Visibility

Version: v0.8.4D

## Purpose

NexusCell planner evidence is now visible to the gated compiler.

The compiler checks that the NexusCell doctrine, planner, manifest, CLI surface, and Desktop Portal access exist and remain bounded.

## Gate

```text
nexus_cell_planner_visibility
```

The gate verifies:

```text
NexusCell static surfaces exist.
Manifest status is compiler_visible_planner_no_execution.
Forbidden boundaries include execute code, enable backend, and claim rollback.
The planner can build a read-only plan.
The planner boundary keeps execution disabled.
Optional report/state outputs are visible when present.
```

## Boundary

```text
Compiler visibility is not execution authority.
Compiler visibility is not containment.
Compiler visibility is not rollback.
Compiler visibility is not a production security proof.
```

## Law

```text
No planner promotion without compiler visibility.
No execution claim from compiler visibility alone.
No backend enablement without a later authority gate.
```
