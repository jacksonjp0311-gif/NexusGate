"""Read-only geometric memory routing packet runtime for NEXUS GATE.

The package init is intentionally passive. Importing router here causes a
runpy warning when executing ``python -m nexus_gate.geometric_memory.router``.
Use importlib-backed lazy attribute access for compatibility.
"""

from importlib import import_module

VERSION = "0.8.3F"
__all__ = ["VERSION", "build_geometry_packet", "compile_geometry_packet"]


def __getattr__(name):
    if name in {"build_geometry_packet", "compile_geometry_packet"}:
        router = import_module(".router", __name__)
        return getattr(router, name)
    raise AttributeError(name)

