"""Print latest TNN chat response from NexusGate router report."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    report_path = repo_root / "reports" / "nexus_nn_router_report_latest.json"
    if not report_path.exists():
        print("TNN // NO REPORT")
        print('next: run .\\scripts\\nexus.ps1 tnn-chat -Tag "hello" -CallModel')
        return

    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    responses = report.get("model_responses") or []
    tnn = next((item for item in responses if item.get("role") == "TNN"), None)
    if not tnn:
        print("TNN // NO RESPONSE")
        print(f"report: {report_path}")
        return

    print("")
    print("TNN CHAT")
    print("--------")
    print(tnn.get("response") or "TNN // EMPTY RESPONSE")
    print("")
    print(f"model: {tnn.get('model')}")
    if tnn.get("backend_model"):
        print(f"backend: {tnn.get('backend_model')}")
    packet = tnn.get("chat_packet") or {}
    if packet.get("latency_ms") is not None:
        print(f"latency_ms: {packet.get('latency_ms')}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
