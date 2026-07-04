from __future__ import annotations

from pathlib import Path
from typing import Any

from assembly.neural.workflow_analyzer import analyze_workflow
from assembly.telemetry.neuralforge_event_codec import append_event, load_events, normalize_event


DEFAULT_LOG = Path(__file__).resolve().parents[2] / "data" / "execution_events.jsonl"


class RealtimeEvolutionEngine:
    def __init__(self, event_log_path: str | Path = DEFAULT_LOG, window_size: int = 50, load_existing: bool = True):
        self.event_log_path = Path(event_log_path)
        self.window_size = window_size
        self.events = load_events(self.event_log_path) if load_existing else []

    def ingest(self, raw_event: dict[str, Any], persist: bool = True) -> dict[str, Any]:
        event = normalize_event(raw_event)
        self.events.append(event)
        self.events = self.events[-self.window_size :]
        if persist:
            append_event(self.event_log_path, event)
        return self.report()

    def report(self) -> dict[str, Any]:
        analysis = analyze_workflow(self.events)
        health = round(max(0.0, 1.0 - analysis["failure_rate"]), 3)
        alerts: list[str] = []
        if analysis["failure_rate"] > 0.25:
            alerts.append("failure pressure elevated")
        if analysis["duration_pattern"].get("pattern") == "trend" and analysis["duration_pattern"].get("slope", 0) > 0:
            alerts.append("duration trend increasing")
        return {
            "health_score": health,
            "alerts": alerts,
            "workflow_predictions": {"next_failure_probability": analysis["next_execution_risk"]},
            "recommendations": analysis["recommendations"],
            "knowledge_entries": [f"observed_events:{analysis['execution_count']}", f"failure_rate:{analysis['failure_rate']}"],
            "analysis": analysis,
            "claim_boundary": "Realtime evolution memory is lab evidence only and cannot apply fixes.",
        }
