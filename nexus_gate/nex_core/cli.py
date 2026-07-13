from __future__ import annotations

import argparse
import json

from . import VERSION
from .bus import replay_message_bus
from .chat import answer_nex_core
from .coordinator import cycle_status
from .learn import apply_learning_event, authorize_learning_proposal, propose, replay_verify as learn_replay_verify, status as learn_status
from .teach import begin_teaching_episode, bind_teaching_validation, replay_verify as teach_replay_verify, seal_teaching_episode, status as teach_status, verify_teaching_episode
from .verify import run_before_after_benchmark, verify_adversarial, verify_all, verify_authority_invariants, verify_learning_proposal, verify_model_replay, verify_retention


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEX Cognitive Cycle Engine.")
    sub = parser.add_subparsers(dest="command", required=True)
    commands = [
        "teach-begin", "teach-status", "teach-bind-validation", "teach-seal", "teach-abort", "teach-list", "teach-verify", "teach-replay-verify",
        "chat", "query", "explain", "inner-status", "inner-trace", "cycle-status", "mode-status",
        "learn-status", "learn-propose", "learn-inspect", "learn-authorize", "learn-apply", "learn-reject", "learn-rollback-propose", "learn-replay-verify",
        "verify", "verify-cycle", "verify-learning", "verify-authority", "verify-retention", "verify-benchmark", "verify-adversarial", "verify-replay", "verify-all",
    ]
    for name in commands:
        item = sub.add_parser(name)
        item.add_argument("--root", default=".")
        item.add_argument("--tag", default="")
        item.add_argument("--prompt", default="")
        item.add_argument("--teaching-id", default="")
        item.add_argument("--proposal-id", default="")
        item.add_argument("--disposition", default="pending_review")
        item.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "teach-begin":
        result = begin_teaching_episode(args.root, args.tag or args.prompt or "NEX teaching episode")
    elif args.command in {"teach-status", "teach-list"}:
        result = teach_status(args.root)
    elif args.command == "teach-bind-validation":
        result = bind_teaching_validation(args.root, args.teaching_id or args.tag, args.tag)
    elif args.command == "teach-seal":
        result = seal_teaching_episode(args.root, args.teaching_id or args.tag, args.disposition)
    elif args.command == "teach-abort":
        result = seal_teaching_episode(args.root, args.teaching_id or args.tag, "abandoned")
    elif args.command == "teach-verify":
        result = verify_teaching_episode(args.root, args.teaching_id or args.tag)
    elif args.command == "teach-replay-verify":
        result = teach_replay_verify(args.root)
    elif args.command in {"chat", "query", "explain"}:
        result = answer_nex_core(args.root, args.prompt or args.tag)
    elif args.command == "inner-status":
        result = replay_message_bus(args.root) | {"mode": "inner_status"}
    elif args.command == "inner-trace":
        result = replay_message_bus(args.root) | {"mode": "inner_trace"}
    elif args.command == "cycle-status":
        result = cycle_status(args.root)
    elif args.command == "mode-status":
        result = {"schema": "NEX_MODE_STATUS.v2.10.0", "status": "pass", "mode": "NEX_CORE", "engine": "NGLM", "external_model": "none", "ollama_required": False, "network_required": False, "version": VERSION, "authority_boundary": {"recommendation_only": True, "may_execute": False, "may_authorize": False}}
    elif args.command == "learn-status":
        result = learn_status(args.root)
    elif args.command in {"learn-propose", "learn-inspect", "learn-rollback-propose"}:
        result = propose(args.root)
    elif args.command == "learn-authorize":
        result = authorize_learning_proposal(args.root, args.proposal_id or args.tag)
    elif args.command == "learn-apply":
        result = apply_learning_event(args.root, args.proposal_id or args.tag)
    elif args.command == "learn-reject":
        result = {"schema": "NEX_LEARN_REJECT.v2.10.0", "status": "pass", "proposal_id": args.proposal_id or args.tag, "persistent_learning_applied": False}
    elif args.command == "learn-replay-verify":
        result = learn_replay_verify(args.root)
    elif args.command in {"verify", "verify-cycle", "verify-all"}:
        result = verify_all(args.root)
    elif args.command == "verify-learning":
        result = verify_learning_proposal(args.root, args.proposal_id or args.tag or None)
    elif args.command == "verify-authority":
        result = verify_authority_invariants(args.root)
    elif args.command == "verify-retention":
        result = verify_retention(args.root)
    elif args.command == "verify-benchmark":
        result = run_before_after_benchmark(args.root, args.proposal_id or args.tag or None)
    elif args.command == "verify-adversarial":
        result = verify_adversarial(args.root)
    elif args.command == "verify-replay":
        result = verify_model_replay(args.root)
    else:
        result = {"schema": "NEX_UNKNOWN.v2.10.0", "status": "fail", "command": args.command}
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0 if result.get("status") in {"pass", "warn", "blocked", "verified_existing"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
