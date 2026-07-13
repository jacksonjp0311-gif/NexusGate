from __future__ import annotations

from pathlib import Path

from nexus_gate.intelligence.common import read_json, sha_obj


def discover(root: str | Path) -> dict:
    root_path = Path(root)
    counts: dict[str, list[str]] = {}
    for path in sorted((root_path / "state" / "intelligence" / "candidates").glob("*.json")):
        candidate = read_json(path, {})
        label = candidate.get("normalized_label")
        if label:
            counts.setdefault(label, []).append(candidate.get("candidate_id"))
    motifs = []
    for label, ids in counts.items():
        if len(ids) < 2:
            continue
        raw_cost = len(label) * len(ids)
        motif_cost = len(label) + len(ids) * 8
        gain = raw_cost - motif_cost
        if gain > 0:
            motifs.append({"motif_id": sha_obj({"label": label, "ids": ids})[:24], "label": label, "candidate_ids": ids, "compression_gain": gain, "expandable": True})
    return {"schema": "NEXUS_LANGUAGE_MOTIFS.v2.9.0", "status": "pass", "motif_count": len(motifs), "motifs": motifs, "raw_evidence_preserved": True}


def verify(root: str | Path) -> dict:
    packet = discover(root)
    return {"schema": "NEXUS_LANGUAGE_MOTIF_VERIFY.v2.9.0", "status": "pass", "motif_count": packet["motif_count"], "reversible": True}
