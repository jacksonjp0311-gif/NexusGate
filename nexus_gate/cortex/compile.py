from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time


def _run(engine: Path, home: Path, args: list[str]) -> dict:
    completed = subprocess.run(
        [sys.executable, "-m", "cortex", "--home", str(home), *args, "--json"],
        cwd=engine, capture_output=True, text=True, timeout=90, check=False,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"ok": False, "stdout": completed.stdout[-1000:], "stderr": completed.stderr[-1000:]}
    return {"returncode": completed.returncode, "payload": payload}


def compile_gate(root: Path, task: str) -> dict:
    engine = root / "Cortex"
    home = root / "state" / "cortex_memory"
    doctor = _run(engine, home, ["doctor", "--repo", "nexus-gate"])
    packet = _run(engine, home, ["nexus-packet", "--repo", "nexus-gate", "--task", task])
    doctor_payload = doctor["payload"]
    packet_payload = packet["payload"]
    checks = {
        "engine_present": engine.is_dir(),
        "database_integrity": bool(doctor_payload.get("database_integrity")),
        "certificate_verified": doctor_payload.get("governor", {}).get("components", {}).get("integrity") == 1.0,
        "vector_storage_current": doctor_payload.get("vector_format", {}).get("legacy_or_invalid", 0) == 0,
        "packet_shape": all(key in packet_payload for key in ("intent", "evidence", "authority", "context")),
        "read_only_authority": packet_payload.get("authority", {}).get("cortex_may_mutate") is False,
    }
    status = "ready" if all(checks.values()) else "constrained"
    return {"schema_version": "1.0", "kind": "nexus_cortex_gate", "generated_at": time.time(), "status": status, "checks": checks, "doctor": doctor_payload, "packet": packet_payload, "claim_boundary": "Read-only Cortex orientation evidence only; it does not grant authority or replace NEXUS gates."}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile NEXUS's read-only Cortex gate.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--intent", default="Orient the next governed NEXUS task.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    report = compile_gate(root, args.intent)
    path = root / "reports" / "nexus_cortex_gate_latest.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"NEXUS Cortex gate: {report['status']}")


if __name__ == "__main__":
    main()
