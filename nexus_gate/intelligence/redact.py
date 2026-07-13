from __future__ import annotations

import math
import re
from typing import Any

from .common import sha_text


RULES = {
    "bearer_token": re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]{16,}"),
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    "password_url": re.compile(r"(?i)(https?://[^:/\s]+:)([^@\s]+)(@)"),
    "api_key": re.compile(r"(?i)\b(?:api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?([a-z0-9_\-./+=]{12,})"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "precise_coordinates": re.compile(r"\b-?\d{1,2}\.\d{5,}\s*,\s*-?\d{1,3}\.\d{5,}\b"),
    "high_entropy": re.compile(r"\b[A-Za-z0-9+/=_-]{32,}\b"),
}

PROMPT_LIKE = {
    "instruction_override": re.compile(r"(?i)\b(ignore|override|forget)\b.{0,40}\b(previous|system|developer)\b.{0,40}\b(instructions|message|policy)\b"),
    "secret_request": re.compile(r"(?i)\b(reveal|print|exfiltrate|send)\b.{0,30}\b(secret|token|password|api key)\b"),
    "tool_imitation": re.compile(r"(?i)\b(tool_call|function_call|execute_command|shell_command)\b"),
    "authority_claim": re.compile(r"(?i)\b(authorize|grant permission|bypass gate|modify policy)\b"),
    "role_imitation": re.compile(r"(?i)\b(system message|developer message|you are now)\b"),
}


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {char: value.count(char) for char in set(value)}
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in counts.values())


def redact_text(text: str) -> tuple[str, dict[str, Any]]:
    redacted = text
    matches: dict[str, int] = {}
    for name, pattern in RULES.items():
        count = 0

        def repl(match: re.Match[str]) -> str:
            nonlocal count
            token = match.group(0)
            if name == "high_entropy" and _entropy(token) < 4.2:
                return token
            count += 1
            return f"[REDACTED:{name}:{sha_text(token)[:12]}]"

        redacted = pattern.sub(repl, redacted)
        if count:
            matches[name] = count
    report = {
        "fields_scanned": 1,
        "matches_found": sum(matches.values()),
        "matches_redacted": sum(matches.values()),
        "redaction_rules": sorted(RULES),
        "redaction_hash": sha_text(redacted),
        "matches_by_rule": matches,
        "status": "pass",
    }
    return redacted, report


def quarantine_report(text: str) -> dict[str, Any]:
    hits = [name for name, pattern in PROMPT_LIKE.items() if pattern.search(text or "")]
    return {
        "status": "quarantined" if hits else "clear",
        "prompt_like_classifications": hits,
        "raw_text_routed_to_instruction_plane": False,
        "text_hash": sha_text(text or ""),
    }
