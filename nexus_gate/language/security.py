from __future__ import annotations

from nexus_gate.intelligence.redact import quarantine_report


def classify_untrusted_text(text: str, provenance: str = "external_text") -> dict:
    report = quarantine_report(text)
    return {
        "schema": "NEXUS_LANGUAGE_SECURITY_CLASSIFICATION.v2.9.0",
        "provenance_type": provenance,
        "authority_assigned_by_text": False,
        "instruction_plane_admitted": False,
        "quarantine": report,
    }
