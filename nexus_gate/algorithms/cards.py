from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SYSTEM = "NEXUS_ALGORITHM_CARDS"
VERSION = "0.3.0"
SCHEMA = "NEXUS_ALGORITHM_CARD_SET.v0.3.0"
SOURCE_DOC = Path("docs/algorithms/NEXUS_CORE_ALGORITHMS.md")
LATEST_PATH = Path("state/algorithms/nexus_algorithm_cards_latest.json")
VERSIONED_PATH = Path("state/algorithms/nexus_algorithm_cards.v0.3.0.json")

CLAIM_BOUNDARY = (
    "Algorithm cards are local reasoning and orchestration descriptions only. "
    "They do not prove correctness, safety, security, production readiness, "
    "scientific truth, mathematical proof, model understanding, or autonomous authority."
)

AUTHORITY_BOUNDARY = {
    "autonomous_authority": False,
    "arbitrary_command_execution": False,
    "git_write_enabled": False,
    "network_enabled": False,
    "secrets_enabled": False,
    "memory_promotion_enabled": False,
    "human_authorization_required_for_mutation": True,
}


def _slug(title: str) -> str:
    text = title.lower().replace("/", " ")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "algorithm"


def _parse_algorithm_sections(text: str) -> list[dict[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
    sections: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        flow = ""
        code_match = re.search(r"```text\s*(.*?)\s*```", body, flags=re.DOTALL)
        if code_match:
            flow = " ".join(code_match.group(1).strip().split())
        summary = re.sub(r"```.*?```", "", body, flags=re.DOTALL).strip()
        summary = " ".join(summary.split())
        sections.append(
            {
                "title": title,
                "algorithm_id": _slug(title),
                "flow": flow,
                "summary": summary,
            }
        )
    return sections


def build_algorithm_cards(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    source = root / SOURCE_DOC
    text = source.read_text(encoding="utf-8-sig")
    cards = []
    for order, section in enumerate(_parse_algorithm_sections(text), start=1):
        title = section["title"]
        cards.append(
            {
                "schema": "NEXUS_ALGORITHM_CARD.v0.3.0",
                "order": order,
                "algorithm_id": section["algorithm_id"],
                "title": title,
                "source_doc": str(SOURCE_DOC).replace("\\", "/"),
                "flow": section["flow"],
                "summary": section["summary"],
                "operator_use": _operator_use(title),
                "inputs": _inputs_for(title),
                "outputs": _outputs_for(title),
                "failure_modes": _failure_modes_for(title),
                "authority_boundary": AUTHORITY_BOUNDARY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    return {
        "schema": SCHEMA,
        "system": SYSTEM,
        "version": VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_doc": str(SOURCE_DOC).replace("\\", "/"),
        "card_count": len(cards),
        "cards": cards,
        "discovered_algorithms": [
            "predictive-gate-timing",
            "runtime-pressure-model",
            "adaptive-timeout-budgeting",
            "gate-selection-policy",
            "certificate-resume-policy",
            "predictive-evolve-planner-algorithm",
        ],
        "claim_boundary": CLAIM_BOUNDARY,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }


def _operator_use(title: str) -> str:
    lowered = title.lower()
    if "predictive" in lowered or "runtime pressure" in lowered:
        return "Use before expensive validation to choose bounded timeouts and reduce wasted Codex/operator cycles."
    if "rehydration" in lowered:
        return "Use at session start or after context loss."
    if "failure" in lowered:
        return "Use after a failing gate before applying another patch."
    if "compiler" in lowered:
        return "Use before claiming a local pass."
    if "authority" in lowered:
        return "Use before mutation or execution routing."
    return "Use as a compact reasoning card for the related NEXUS lane."


def _inputs_for(title: str) -> list[str]:
    lowered = title.lower()
    if "predictive" in lowered or "runtime pressure" in lowered:
        return ["human_surface_duration_history", "gate_status_history", "repo_scope_counts"]
    if "rehydration" in lowered:
        return ["README.md", "AGENTS.md", "docs", "state", "reports"]
    if "route" in lowered:
        return ["StatePacket", "schema", "authority", "route_map"]
    return ["local_repo_evidence", "human_intent", "bounded_context"]


def _outputs_for(title: str) -> list[str]:
    lowered = title.lower()
    if "predictive" in lowered or "runtime pressure" in lowered:
        return ["runtime_pressure", "recommended_timeout_seconds", "recommended_next_command"]
    if "failure" in lowered:
        return ["failure_class", "evidence_summary", "bounded_retry"]
    if "compiler" in lowered:
        return ["pass_warn_fail_report", "claim_boundary"]
    return ["algorithm_card", "bounded_recommendation"]


def _failure_modes_for(title: str) -> list[str]:
    lowered = title.lower()
    modes = ["unsupported_claim", "stale_evidence", "authority_boundary_drift"]
    if "predictive" in lowered or "runtime pressure" in lowered:
        modes.extend(["too_few_samples", "outlier_overfit", "timeout_budget_drift"])
    if "compiler" in lowered:
        modes.append("gate_bypass_attempt")
    return modes


def write_algorithm_cards(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    packet = build_algorithm_cards(root)
    encoded = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    for rel in (LATEST_PATH, VERSIONED_PATH):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS algorithm cards.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packet = write_algorithm_cards(args.root)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"wrote {packet['card_count']} NEXUS algorithm cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
