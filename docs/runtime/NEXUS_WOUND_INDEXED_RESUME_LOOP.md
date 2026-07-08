# NEXUS Wound-Indexed Resume Loop

The wound-indexed resume loop records current continuation state so future closers do not rerun green gates unnecessarily.

Surfaces: `reports/nexus_resume_packet_latest.json`, `reports/nexus_resume_packet_latest.md`, `state/loops/wound_indexed_resume_latest.json`.

Rule: passed gates are certificates unless their input paths changed; failed gates become active wounds; next closer starts at the wound.
