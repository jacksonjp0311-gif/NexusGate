from __future__ import annotations
import re
SECRET_PATTERNS=[re.compile(r"sk-[A-Za-z0-9_-]{20,}"),re.compile(r"ghp_[A-Za-z0-9_]{20,}"),re.compile(r"AKIA[0-9A-Z]{16}"),re.compile(r"-----BEGIN .* PRIVATE KEY-----",re.DOTALL),re.compile(r"OPENAI_API_KEY\s*=\s*[^\s]+",re.IGNORECASE),re.compile(r"AWS_SECRET_ACCESS_KEY\s*=\s*[^\s]+",re.IGNORECASE)]
def redact_text(value: str)->str:
    out=value
    for p in SECRET_PATTERNS: out=p.sub("[REDACTED_SECRET]",out)
    return out
def contains_raw_secret(value: str)->bool: return any(p.search(value) for p in SECRET_PATTERNS)
