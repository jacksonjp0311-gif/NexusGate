from __future__ import annotations

import argparse
import json

from . import extract, promote, touch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEXUS AI touch and intelligence receipts.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["touch-status", "touch-list", "touch-verify", "touch-replay-verify", "intelligence-status", "intelligence-candidates", "intelligence-replay-verify"]:
        item = sub.add_parser(name)
        item.add_argument("--root", default=".")
        item.add_argument("--json", action="store_true")
        item.add_argument("--interaction-id", default="")
    begin = sub.add_parser("touch-begin")
    begin.add_argument("--root", default=".")
    begin.add_argument("--provider", default="codex")
    begin.add_argument("--session-id", required=True)
    begin.add_argument("--intent", default="")
    begin.add_argument("--model-identifier", default=None)
    begin.add_argument("--json", action="store_true")
    end = sub.add_parser("touch-end")
    end.add_argument("--root", default=".")
    end.add_argument("--interaction-id", required=True)
    end.add_argument("--disposition", required=True)
    end.add_argument("--json", action="store_true")
    abort = sub.add_parser("touch-abort")
    abort.add_argument("--root", default=".")
    abort.add_argument("--interaction-id", required=True)
    abort.add_argument("--json", action="store_true")
    ext = sub.add_parser("extract")
    ext.add_argument("--root", default=".")
    ext.add_argument("--interaction-id", required=True)
    ext.add_argument("--json", action="store_true")
    prom = sub.add_parser("promote")
    prom.add_argument("--root", default=".")
    prom.add_argument("--candidate-id", required=True)
    prom.add_argument("--level", type=int, default=2)
    prom.add_argument("--human-authorized", action="store_true")
    prom.add_argument("--json", action="store_true")
    rej = sub.add_parser("reject")
    rej.add_argument("--root", default=".")
    rej.add_argument("--candidate-id", required=True)
    rej.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "touch-begin":
        result = touch.begin(args.root, args.provider, args.session_id, args.intent, args.model_identifier)
    elif args.command == "touch-end":
        result = touch.end(args.root, args.interaction_id, args.disposition)
    elif args.command == "touch-abort":
        result = touch.abort(args.root, args.interaction_id)
    elif args.command in {"touch-status", "touch-list"}:
        result = touch.status(args.root, getattr(args, "interaction_id", "") or None)
    elif args.command == "touch-verify":
        result = touch.verify(args.root, getattr(args, "interaction_id", "") or None)
    elif args.command == "touch-replay-verify":
        result = touch.replay_verify(args.root)
    elif args.command == "extract":
        result = extract.extract_from_interaction(args.root, args.interaction_id)
    elif args.command == "intelligence-status":
        result = extract.status(args.root)
    elif args.command == "intelligence-candidates":
        result = promote.list_candidates(args.root)
    elif args.command == "promote":
        result = promote.promote(args.root, args.candidate_id, args.level, args.human_authorized)
    elif args.command == "reject":
        result = promote.reject(args.root, args.candidate_id)
    else:
        result = promote.replay_verify(args.root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0 if result.get("status") in {"pass", "warn", "blocked", "rejected"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
