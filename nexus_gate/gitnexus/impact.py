
from __future__ import annotations
import argparse, datetime as _dt, hashlib, json
from pathlib import Path
from typing import Any

VERSION = "v0.9.1"
MODE = "gitnexus_impact_bridge_read_only"

def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()

def _sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode("utf-8")).hexdigest()

def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except Exception:
        return None

def _extract_paths(obj: Any, limit: int = 240) -> list[str]:
    found: set[str] = set()
    keys = {"path", "file", "filePath", "source", "target", "name", "id"}
    def walk(x: Any, depth: int = 0) -> None:
        if depth > 6 or len(found) >= limit:
            return
        if isinstance(x, dict):
            for k, v in x.items():
                if k in keys and isinstance(v, str) and ("/" in v or "\\" in v) and not v.startswith("http"):
                    found.add(v.replace("\\", "/"))
                walk(v, depth + 1)
        elif isinstance(x, list):
            for item in x[:limit]:
                walk(item, depth + 1)
    walk(obj)
    return sorted(found)[:limit]

def build_impact_packet(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root).resolve()
    candidates = [
        root / "state" / "gitnexus" / "gitnexus_graph_latest.json",
        root / "GITNEXUS" / "state" / "gitnexus_graph_latest.json",
        root / "reports" / "gitnexus_report_latest.json",
        root / "GITNEXUS" / "reports" / "gitnexus_report_latest.json",
        root / "state" / "interconnect_graph.v0.2.2.json",
    ]
    selected = None
    data = None
    for path in candidates:
        data = _read_json(path)
        if data is not None:
            selected = path
            break
    paths = _extract_paths(data) if data is not None else []
    core_markers = ["README.md", "pyproject.toml", "nexus_gate/compiler/compiler.py", "nexus_gate/nexus_cell/policy.py"]
    impacted = sorted(set(paths + [p for p in core_markers if (root / p).exists()]))[:240]
    hot = [p for p in impacted if p.endswith(".py") or p.startswith("nexus_gate/")]
    packet = {
        "version": VERSION,
        "mode": MODE,
        "generated_utc": _utc_now(),
        "graph_source": str(selected.relative_to(root)).replace("\\", "/") if selected else None,
        "graph_source_present": selected is not None,
        "impacted_files": impacted,
        "hot_files": hot[:80],
        "impact_counts": {"impacted": len(impacted), "hot": len(hot)},
        "nexuscell_lane": "gitnexus-impact",
        "boundary": {
            "read_only": True,
            "execution_enabled": False,
            "repo_mutation_enabled": False,
            "git_write_enabled": False,
            "network_enabled": False,
            "model_output_authority": False,
        },
        "claim_boundary": "GITNEXUS impact bridge emits local evidence only; it does not execute, mutate, authorize, prove safety, or write git history.",
    }
    packet["impact_packet_id"] = _sha(packet)
    return packet

def write_outputs(root: str | Path, packet: dict[str, Any]) -> None:
    root = Path(root).resolve()
    state = root / "state" / "gitnexus" / "gitnexus_impact_packet_latest.json"
    report_json = root / "reports" / "gitnexus_impact_report_latest.json"
    report_md = root / "reports" / "gitnexus_impact_report_latest.md"
    state.parent.mkdir(parents=True, exist_ok=True)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    state.write_text(encoded, encoding="utf-8")
    report_json.write_text(encoded, encoding="utf-8")
    report_md.write_text("# GITNEXUS Impact Report v0.9.1\n\n" + f"Packet: `{packet['impact_packet_id']}`\n\n" + f"Impacted files: {packet['impact_counts']['impacted']}\n\n" + "Boundary: evidence-only; no execution; no mutation; no git write.\n", encoding="utf-8")

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build read-only GITNEXUS impact packet.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    packet = build_impact_packet(args.root)
    if not args.no_write:
        write_outputs(args.root, packet)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(json.dumps({"ok": True, "mode": packet["mode"], "impact_packet_id": packet["impact_packet_id"]}, indent=2))
    return 0
