from __future__ import annotations

import argparse
import json

from .conductance import build_conductance_field, replay_verify, write_conductance_field


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEXUS sparse conductance field.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("field", "status", "route", "replay-verify", "calibration-proposal"):
        p = sub.add_parser(name)
        p.add_argument("--root", default=".")
        p.add_argument("--intent", default="")
        p.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "replay-verify":
        packet = replay_verify(args.root)
    elif args.command == "calibration-proposal":
        packet = {
            "schema": "NEXUS_CONDUCTANCE_CALIBRATION_PROPOSAL.v2.8.0",
            "status": "warn",
            "proposal": "blocked_without_verified_experience_and_human_authorization",
            "persistent_delta": 0,
        }
    elif args.command == "status":
        packet = build_conductance_field(args.root, args.intent)
    else:
        packet = write_conductance_field(args.root, args.intent)
    print(json.dumps(packet, indent=2, sort_keys=True) if args.json else packet.get("status", "unknown"))
    return 0 if packet.get("status") in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
