"""CLI compiler for the NEXUS GATE reflective intelligence loop."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys

from .reflective_loop import compile_reflective_loop, write_reflective_loop_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexus-reflect", description="Compile NEXUS reflective intelligence loop evidence")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    report = compile_reflective_loop(args.root)
    write_reflective_loop_report(report, args.root)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE reflective loop status: {report.status}")
        print(f"next_action: {report.next_action}")

    if report.status == "fail":
        sys.exit(1)


if __name__ == "__main__":
    main()
