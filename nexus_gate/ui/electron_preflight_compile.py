"""CLI compiler for the NEXUS GATE Electron scaffold preflight."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys

from .electron_preflight import compile_electron_preflight, write_electron_preflight_report


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="nexus-electron-preflight",
        description="Compile the presentation-only Electron scaffold preflight report",
    )
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    args = parser.parse_args()

    report = compile_electron_preflight(args.root)
    write_electron_preflight_report(report, args.root)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE Electron preflight status: {report.status}")

    if report.status != "pass":
        sys.exit(1)


if __name__ == "__main__":
    main()
