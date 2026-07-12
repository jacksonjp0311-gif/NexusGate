from __future__ import annotations

from typing import Any


INACTIVE_WOUND_KEYS = {None, "", "none", "null", "clear", "inactive", "no_active_wound"}


def has_active_wound(wound: dict[str, Any]) -> bool:
    if wound.get("status") == "fail":
        return True
    key = wound.get("active_wound_key")
    if key is None:
        return False
    if isinstance(key, str):
        return key.strip().lower() not in INACTIVE_WOUND_KEYS
    return bool(key)
