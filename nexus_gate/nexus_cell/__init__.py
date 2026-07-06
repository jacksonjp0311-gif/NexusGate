"""NexusCell read-only execution-governance planner.

Boundary: this package plans and scores. It does not execute commands,
create sandboxes, inject secrets, mount host paths, mutate git, or claim rollback.
"""

VERSION = "0.8.5"

__all__ = ["VERSION"]
