from __future__ import annotations


def torch_status() -> dict[str, object]:
    try:
        import torch  # type: ignore

        return {"available": True, "version": getattr(torch, "__version__", "unknown"), "mode": "optional_local"}
    except Exception as exc:
        return {"available": False, "version": None, "mode": "standard_library_fallback", "reason": str(exc)}
