"""CLI compiler for NEXUS GATE interconnect graph."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys

from .graph import build_interconnect, write_interconnect_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexus-interconnect", description="Compile governed interconnect graph")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    args = parser.parse_args()

    report = build_interconnect(args.root)
    write_interconnect_report(report, args.root)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE interconnect status: {report.status}")
        print(f"nodes: {len(report.nodes)}")
        print(f"edges: {len(report.edges)}")

    if report.status != "pass":
        sys.exit(1)


if __name__ == "__main__":
    main()
