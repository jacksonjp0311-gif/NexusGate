from __future__ import annotations

import argparse
import json

from .electron_environment import compile_electron_environment, write_electron_environment_report


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="nexus-electron-environment",
        description="Write the NEXUS GATE Electron environment readiness report.",
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = compile_electron_environment(args.root)
    write_electron_environment_report(report, args.root)
    if args.json:
        print(json.dumps(report.__dict__, indent=2, default=str))
    return 0 if report.status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
