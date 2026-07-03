"""CLI for the NEXUS GATE AI feedback interface."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from .interface import write_ai_feedback_interface


def main() -> None:
    parser = argparse.ArgumentParser(prog="nexus-feedback-interface", description="Write AI-readable feedback interface surfaces")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    report = write_ai_feedback_interface(args.root)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"NEXUS GATE feedback interface status: {report.status}")
        print(f"AI context: {report.ai_context_path}")
        print(f"Feedback log: {report.markdown_log_path}")


if __name__ == "__main__":
    main()
