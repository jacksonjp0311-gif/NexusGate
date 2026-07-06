from __future__ import annotations
import hashlib
from nexus_gate.nexus_cell.secrets.redaction import contains_raw_secret, redact_text
def secret_reference(name: str): return {"name":name,"name_hash":hashlib.sha256(name.encode("utf-8")).hexdigest()}
def apply_secret_veil(text: str): return {"raw_secret_detected":contains_raw_secret(text),"redacted":redact_text(text),"boundary":"Secrets may be referenced by hash or name, but raw secrets must not appear in payloads, receipts, stdout/stderr, or ledger entries."}
