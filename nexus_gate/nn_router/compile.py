"""Compile NEXUS bounded NN router report and handoff packets."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .contract import VERSION, build_policy_manifest, build_route_decision, normalize_target_role, selected_roles
from .detect import DEFAULT_MODELS_ROOT, assign_roles, detect_ollama_inventory
from .ollama_client import call_local_ollama
from .tesseract_neural_network import build_tesseract_neural_network_response


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _safe_write_text(path: Path, content: str) -> None:
    _ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8", newline="\n")


def _safe_write_json(path: Path, payload: Dict[str, object]) -> None:
    _ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _public_models_root(models_root: Path) -> str:
    try:
        resolved = models_root.resolve()
    except OSError:
        resolved = models_root.absolute()

    try:
        home = Path.home().resolve()
        relative = resolved.relative_to(home)
        return "%USERPROFILE%\\" + str(relative).replace("/", "\\")
    except ValueError:
        return "<models-root>"


def _replace_case_variants(value: str, old: str, new: str) -> str:
    result = value.replace(old, new)
    result = result.replace(old.replace("\\", "/"), new.replace("\\", "/"))
    return result


def _path_candidates(path: Path) -> List[str]:
    """Return path spellings that may appear on Windows/local/CI.

    GitHub Actions Windows can expose temp paths with short 8.3 segments
    such as RUNNER~1 while Path.resolve() may produce a different spelling.
    Public reports must sanitize all visible spellings.
    """
    candidates: List[str] = []

    for item in (path, path.absolute()):
        text = str(item)
        if text and text not in candidates:
            candidates.append(text)

    for strict in (False, True):
        try:
            text = str(path.resolve(strict=strict))
            if text and text not in candidates:
                candidates.append(text)
        except OSError:
            pass

    normalized: List[str] = []
    for item in candidates:
        for variant in (item, item.replace("\\", "/")):
            if variant and variant not in normalized:
                normalized.append(variant)

    return sorted(normalized, key=len, reverse=True)


def _sanitize_public(value: Any, root: Path, models_root: Path) -> Any:
    """Remove machine-specific paths from reports.

    Root replacement intentionally happens before model-root replacement. In
    tests and special local layouts, root and models_root can overlap. Repo root
    must remain the primary origin marker; model roots outside the repo become
    the model marker or a %USERPROFILE%-relative path.
    """
    public_models = _public_models_root(models_root)
    root_candidates = _path_candidates(root)
    models_candidates = _path_candidates(models_root)

    if isinstance(value, dict):
        return {key: _sanitize_public(item, root, models_root) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_public(item, root, models_root) for item in value]
    if isinstance(value, str):
        text = value
        for candidate in root_candidates:
            text = _replace_case_variants(text, candidate, "<repo-root>")
        for candidate in models_candidates:
            text = _replace_case_variants(text, candidate, public_models)
        return text
    return value
def _packet_lines(title: str, report: Dict[str, object]) -> List[str]:
    intent = str(report.get("intent", ""))
    target_role = str(report.get("target_role", "ALL"))
    assignments = report.get("role_assignments", {})
    policy = report.get("policy", {})
    router_law = policy.get("router_law", []) if isinstance(policy, dict) else []

    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"- Version: {VERSION}")
    lines.append(f"- Generated UTC: {report.get('generated_utc')}")
    lines.append(f"- Intent: {intent}")
    lines.append(f"- Target role: {target_role}")
    lines.append("- Boundary: recommendation-only; human authorizes durable mutation.")
    lines.append("")
    lines.append("## Canonical Rules")
    lines.append("")
    if isinstance(router_law, list):
        for item in router_law:
            lines.append(f"- {item}")
    lines.append("")
    lines.append("## Role Assignments")
    lines.append("")
    if isinstance(assignments, dict):
        for role in ["FAST", "BALANCED", "DEEP", "TNN", "HANDOFF"]:
            value = assignments.get(role, {})
            if isinstance(value, dict):
                model = value.get("model") or "none"
                available = value.get("available")
                reason = value.get("reason")
                lines.append(f"- {role}: model={model}; available={available}; reason={reason}")
    lines.append("")
    lines.append("## Recommended Next Work")
    lines.append("")
    lines.append("1. Inspect the generated NN router report.")
    lines.append("2. Treat local model text as recommendation context only.")
    lines.append("3. Use role-targeted DEEP reasoning when Mistral inspection is required.")
    lines.append("4. Route durable repo mutation through NEXUS gates and human authorization.")
    lines.append("5. Preserve evidence ledger and replay requirements before compounding.")
    lines.append("")
    lines.append("## BB/EGAT Packet")
    lines.append("")
    lines.append("- BB/EGAT prepares the reasoning packet.")
    lines.append("- Phi-3 is FAST/BALANCED when present.")
    lines.append("- Mistral is DEEP when present.")
    lines.append("- ChatGPT/Codex receive compressed handoff packets.")
    lines.append("- NEXUS gates tool/action authority.")
    lines.append("- Human remains durable authority.")
    lines.append("")
    model_responses = report.get("model_responses", [])
    if isinstance(model_responses, list) and model_responses:
        lines.append("## Optional Local Model Responses")
        lines.append("")
        for response in model_responses:
            if isinstance(response, dict):
                role = response.get("role")
                model = response.get("model")
                ok = response.get("ok")
                lines.append(f"### {role} / {model} / ok={ok}")
                lines.append("")
                text = str(response.get("response") or response.get("error") or "")
                if text:
                    lines.append(text.strip())
                    lines.append("")
    return lines


def build_distribution(
    root: Path,
    intent: str,
    models_root: Optional[Path] = None,
    call_model: bool = False,
    target_role: str = "ALL",
) -> Dict[str, object]:
    models_root = models_root or DEFAULT_MODELS_ROOT
    target_role = normalize_target_role(target_role)
    raw_inventory = detect_ollama_inventory(models_root)
    assignments = assign_roles(raw_inventory)
    policy = build_policy_manifest()
    roles = selected_roles(target_role)

    route_decisions = []
    for role in roles:
        decision = build_route_decision(
            intent=intent,
            role=role,
            inventory=raw_inventory.get("models", {}),
            call_model=call_model,
            route_kind="handoff" if role == "HANDOFF" else "recommendation",
        )
        route_decisions.append(decision.to_dict())

    model_responses = []
    if call_model:
        call_roles = ["FAST", "DEEP", "TNN"] if target_role == "ALL" else [role for role in roles if role != "HANDOFF"]
        for role in call_roles:
            if role == "TNN":
                model_responses.append(build_tesseract_neural_network_response(intent=intent))
                continue
            assignment = assignments.get(role, {})
            model = assignment.get("model") if isinstance(assignment, dict) else None
            if model:
                model_responses.append(call_local_ollama(model=str(model), intent=intent, role=role))

    raw_report: Dict[str, object] = {
        "version": VERSION,
        "generated_utc": _utc_now(),
        "intent": intent,
        "target_role": target_role,
        "root": str(root),
        "models_root": str(models_root),
        "policy": policy,
        "inventory": raw_inventory,
        "role_assignments": assignments,
        "route_decisions": route_decisions,
        "model_responses": model_responses,
        "outputs": {
            "report": "reports/nexus_nn_router_report_latest.json",
            "chatgpt_handoff": "reports/CHATGPT_HANDOFF_LATEST.md",
            "codex_handoff": "reports/CODEX_HANDOFF_LATEST.md",
            "state": "state/nexus_nn_router_index.v0.6.4.json",
        },
        "authority_boundary": {
            "models": "recommendation_only",
            "handoffs": "compressed_context_only",
            "tool_execution": "blocked_from_model_output",
            "repo_mutation": "human_authorized_after_gates",
            "role_targeting": "explicit_role_required_for_deep_test",
        },
    }
    return _sanitize_public(raw_report, root=root, models_root=models_root)


def write_outputs(root: Path, report: Dict[str, object]) -> None:
    report_path = root / "reports" / "nexus_nn_router_report_latest.json"
    state_path = root / "state" / "nexus_nn_router_index.v0.6.4.json"
    chatgpt_path = root / "reports" / "CHATGPT_HANDOFF_LATEST.md"
    codex_path = root / "reports" / "CODEX_HANDOFF_LATEST.md"

    _safe_write_json(report_path, report)
    _safe_write_json(state_path, {
        "version": VERSION,
        "generated_utc": report.get("generated_utc"),
        "target_role": report.get("target_role"),
        "models_root": report.get("models_root"),
        "role_assignments": report.get("role_assignments"),
        "route_decisions": report.get("route_decisions"),
        "policy": report.get("policy"),
    })

    _safe_write_text(chatgpt_path, "\n".join(_packet_lines("NEXUS ChatGPT Handoff Latest", report)) + "\n")
    _safe_write_text(codex_path, "\n".join(_packet_lines("NEXUS Codex Handoff Latest", report)) + "\n")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compile NEXUS bounded NN model router outputs.")
    parser.add_argument("--root", default=".", help="Repo root.")
    parser.add_argument("--intent", default="What should we do next?", help="Recommendation intent.")
    parser.add_argument("--models-root", default=str(DEFAULT_MODELS_ROOT), help="Local Ollama models root.")
    parser.add_argument("--call-model", action="store_true", help="Optionally call local Ollama loopback API.")
    parser.add_argument("--role", default="ALL", choices=["ALL", "FAST", "BALANCED", "DEEP", "TNN", "HANDOFF"], help="Target a specific router role.")
    parser.add_argument("--json", action="store_true", help="Print report JSON to stdout.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    models_root = Path(args.models_root).expanduser()
    report = build_distribution(
        root=root,
        intent=args.intent,
        models_root=models_root,
        call_model=bool(args.call_model),
        target_role=args.role,
    )
    write_outputs(root=root, report=report)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps({
            "ok": True,
            "version": VERSION,
            "report": "reports/nexus_nn_router_report_latest.json",
            "state": "state/nexus_nn_router_index.v0.6.4.json",
            "call_model": bool(args.call_model),
            "target_role": args.role,
        }, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
