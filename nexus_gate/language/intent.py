from __future__ import annotations

from .tokenizer import tokenize


INTENTS = {
    "inspect_status": {"status", "pending", "state", "health"},
    "inspect_identity": {"identity", "epoch", "origin", "version"},
    "inspect_experience": {"experience", "action", "receipt", "stopped", "next", "proof"},
    "inspect_learning": {"learn", "learning", "calibration", "promote", "plasticity", "blocked"},
    "inspect_telemetry": {"telemetry", "weather", "solar", "seismic", "orbital"},
    "inspect_conductance": {"conductance", "field", "resistance", "route"},
    "run_validation": {"test", "validate", "evolve", "verify"},
    "plan_change": {"plan", "change", "implement", "build"},
    "repair_failure": {"fix", "failure", "wound", "bug", "error"},
    "explain_architecture": {"architecture", "explain", "system", "plane"},
    "locate_code": {"code", "module", "file", "function"},
    "locate_test": {"test", "tests"},
    "explain_command": {"command", "run"},
    "explain_limitation": {"cannot", "blocked", "limitation"},
    "ask_capability": {"can", "capability", "able"},
    "ask_next_step": {"next", "should", "pending"},
}


def classify(text: str) -> dict:
    terms = {token.normalized for token in tokenize(text)}
    scored = []
    for intent, aliases in INTENTS.items():
        overlap = len(terms & aliases)
        if overlap:
            scored.append((intent, overlap / max(1, len(aliases & terms) + 1)))
    if not scored:
        return {"selected": "unknown_or_out_of_scope", "confidence": 0.0, "alternatives": []}
    scored.sort(key=lambda item: (-item[1], item[0]))
    return {"selected": scored[0][0], "confidence": min(0.95, 0.55 + scored[0][1] * 0.4), "alternatives": [{"intent": name, "confidence": round(conf, 3)} for name, conf in scored[1:4]]}
