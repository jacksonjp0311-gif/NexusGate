from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


TOKEN_RE = re.compile(r"[A-Za-z]:/[^\s]+|(?:[\w.-]+/)+[\w.-]+|nexus\.[\w.-]+|[A-Za-z_][A-Za-z0-9_.-]*|\d+(?:\.\d+)?|[^\w\s]", re.U)


@dataclass(frozen=True)
class Token:
    text: str
    normalized: str
    kind: str
    casing: str


def _split_identifier(value: str) -> list[str]:
    parts = re.split(r"[_\-.]+", value)
    output: list[str] = []
    for part in parts:
        output.extend(re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", part) or [part])
    return [item for item in output if item]


def tokenize(text: str) -> list[Token]:
    normalized_text = unicodedata.normalize("NFKC", text or "").replace("\\", "/")
    tokens: list[Token] = []
    for match in TOKEN_RE.finditer(normalized_text):
        raw = match.group(0)
        if "/" in raw and not raw.startswith("nexus."):
            tokens.append(Token(raw, raw.lower(), "path", "mixed"))
            continue
        if raw.startswith("nexus."):
            tokens.append(Token(raw, raw.lower(), "command_id", "mixed"))
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_.-]*$", raw):
            kind = "identifier" if any(ch in raw for ch in "_.-") or re.search(r"[a-z][A-Z]", raw) else "word"
            tokens.append(Token(raw, raw.lower(), kind, "upper" if raw.isupper() else "lower" if raw.islower() else "mixed"))
            if kind == "identifier":
                for part in _split_identifier(raw):
                    tokens.append(Token(part, part.lower(), "identifier_part", "mixed"))
            continue
        tokens.append(Token(raw, raw.lower(), "punctuation" if len(raw) == 1 and not raw.isalnum() else "number", "mixed"))
    return tokens


def char_ngrams(text: str, n_min: int = 3, n_max: int = 5) -> list[str]:
    base = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text or "").lower()).strip()
    grams: set[str] = set()
    for n in range(n_min, n_max + 1):
        for i in range(max(0, len(base) - n + 1)):
            grams.add(base[i : i + n])
    return sorted(grams)
