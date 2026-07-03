"""CLI compiler for the NEXUS GATE feedback engine."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys

from .engine import compile_feedback, write_feedback_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexus-feedback", description="Compile NEXUS GATE feedback report")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    args = parser.parse_args()

    report = compile_feedback(args.root)
    write_feedback_report(report, args.root)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE feedback status: {report.status}")
        print(f"health_score: {report.health_score}")

    if report.status not in {"pass", "warn"}:
        sys.exit(1)


if __name__ == "__main__":
    main()
