from __future__ import annotations

from .tokenizer import tokenize


def realize(seed_text: str, max_tokens: int = 40, seed: int = 0) -> dict:
    tokens = [token.text for token in tokenize(seed_text)]
    if not tokens:
        return {"mode": "template_fallback", "text": "NEXUS does not currently have verified evidence to answer that.", "provenance_coverage": 0.0}
    text = " ".join(tokens[:max_tokens])
    return {"mode": "experimental_geometric_token_field", "text": text, "provenance_coverage": 1.0, "seed": seed}
