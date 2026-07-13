from __future__ import annotations

from urllib.parse import urlparse


BLOCKED_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
BLOCKED_PREFIXES = ("10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.2", "192.168.", "169.254.")
PROMPT_LIKE_NEEDLES = (
    "ignore previous instructions",
    "execute this command",
    "change system policy",
    "authorize action",
    "send data",
)


def validate_url(url: str, allowed_domains: list[str]) -> tuple[bool, str]:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        return False, "non_https_rejected"
    if host in BLOCKED_HOSTS or any(host.startswith(prefix) for prefix in BLOCKED_PREFIXES):
        return False, "private_or_loopback_rejected"
    if not any(host == domain or host.endswith("." + domain) for domain in allowed_domains):
        return False, "domain_not_allowlisted"
    return True, "allowed"


def quarantine_text(value: str) -> bool:
    lowered = value.lower()
    return any(needle in lowered for needle in PROMPT_LIKE_NEEDLES)
