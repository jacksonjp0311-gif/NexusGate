"""CLI compiler for NEXUS GATE self-healing feedback."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from .engine import compile_self_healing, write_self_healing_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexus-self-heal", description="Compile NEXUS self-healing recommendation report")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    report = compile_self_healing(args.root)
    write_self_healing_report(report, args.root)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE self-healing status: {report.status}")
        print(f"dominant_pressure_source: {report.dominant_pressure_source}")

    # warn is not a failing exit. Self-healing warnings are routed, not fatal.
    return


if __name__ == "__main__":
    main()
