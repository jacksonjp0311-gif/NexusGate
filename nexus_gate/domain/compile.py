"""CLI compiler for the NEXUS GATE domain intelligence orchestrator."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys

from .domain_intelligence import compile_domain_intelligence, write_domain_intelligence_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexus-domain", description="Compile NEXUS domain intelligence evidence")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    report = compile_domain_intelligence(args.root)
    write_domain_intelligence_report(report, args.root)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE domain intelligence status: {report.status}")
        print(f"next_action: {report.next_action}")

    if report.status == "fail":
        sys.exit(1)


if __name__ == "__main__":
    main()
