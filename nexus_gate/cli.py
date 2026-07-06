from __future__ import annotations

import argparse
import json
from pathlib import Path

from nexus_gate.core.packets import StatePacket
from nexus_gate.runtime.router import NexusRouter


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="nexus", description="NEXUS GATE CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    route = sub.add_parser("route")
    route.add_argument("packet_json")

    cell = sub.add_parser("cell")
    cell.add_argument("cell_args", nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)

    if args.cmd == "route":
        data = json.loads(Path(args.packet_json).read_text(encoding="utf-8"))
        packet = StatePacket(**data)
        decision = NexusRouter().route(packet)
        print(json.dumps(decision.__dict__, indent=2))
        return

    if args.cmd == "cell":
        from nexus_gate.nexus_cell.cli import main as cell_main
        cell_main(args.cell_args)
        return


if __name__ == "__main__":
    main()
