from __future__ import annotations

import argparse
import json

from nexus_gate.core.packets import StatePacket
from nexus_gate.runtime.router import NexusRouter


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexus", description="NEXUS GATE CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    inspect = sub.add_parser("inspect-packet")
    inspect.add_argument("packet_json")

    route = sub.add_parser("route")
    route.add_argument("packet_json")

    args = parser.parse_args()

    with open(args.packet_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    packet = StatePacket(**data)

    if args.cmd == "inspect-packet":
        print(json.dumps(data, indent=2))
        return

    if args.cmd == "route":
        decision = NexusRouter().route(packet)
        print(json.dumps(decision.__dict__, indent=2))
        return


if __name__ == "__main__":
    main()