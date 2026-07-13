from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nexus_gate.decision.arbiter import arbitrate_recommendations
from nexus_gate.field.conductance import build_conductance_field, replay_verify
from nexus_gate.field.laplacian import electrical_flow


ROOT = Path(__file__).resolve().parents[1]


class LanguageConductanceV290Tests(unittest.TestCase):
    def test_parallel_complete_routes_split_current(self) -> None:
        packet = build_conductance_field(ROOT)
        routes = packet["route_scores"]
        active = [route for route, score in routes.items() if score["route_flow"] > 0]
        self.assertGreaterEqual(len(active), 3)
        self.assertEqual(packet["field_boundary"]["non_adaptive_authorization_gate"], "downstream_application_invariant")

    def test_electrical_flow_divides_across_equal_routes(self) -> None:
        flow = electrical_flow(
            ["source", "a", "b", "sink"],
            [
                {"edge_id": "s-a", "source": "source", "target": "a", "conductance": 1.0},
                {"edge_id": "a-z", "source": "a", "target": "sink", "conductance": 1.0},
                {"edge_id": "s-b", "source": "source", "target": "b", "conductance": 1.0},
                {"edge_id": "b-z", "source": "b", "target": "sink", "conductance": 1.0},
            ],
            "source",
            "sink",
        )
        outgoing = [edge["abs_flow"] for edge in flow["edge_flows"] if edge["source"] == "source"]
        self.assertAlmostEqual(outgoing[0], outgoing[1], places=5)

    def test_conductance_changes_rank_but_not_authorization(self) -> None:
        recs = [
            {"source": "predictive-evolve", "action": "predictive-timing", "command": ".\\scripts\\nexus.ps1 predictive-evolve", "severity": "medium", "confidence": 0.7, "estimated_cost": "bounded", "source_packet_hash": "x", "conductance_field": {"bounded_adjustment": 6.25}},
            {"source": "runtime-hygiene", "action": "inspect_dirty_scope", "command": ".\\scripts\\nexus.ps1 runtime-hygiene", "severity": "medium", "confidence": 0.7, "estimated_cost": "bounded", "source_packet_hash": "x", "conductance_field": {"bounded_adjustment": -6.25}},
        ]
        arbiter = arbitrate_recommendations(recs, {}, {})
        self.assertEqual(arbiter["selected"]["source"], "predictive-evolve")
        self.assertEqual(arbiter["selected"]["arbiter_factors"]["conductance_adjustment"], 6.25)
        self.assertIn("may not execute", arbiter["boundary"])

    def test_stale_or_absent_field_adjustment_is_zero(self) -> None:
        rec = {"source": "runtime-hygiene", "action": "inspect_dirty_scope", "command": "runtime-hygiene", "severity": "medium", "confidence": 0.5}
        arbiter = arbitrate_recommendations([rec], {}, {})
        self.assertEqual(arbiter["selected"]["arbiter_factors"]["conductance_adjustment"], 0.0)

    def test_replay_detects_telemetry_direct_persistent_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            history = root / "state" / "field" / "nexus_conductance_history.jsonl"
            history.parent.mkdir(parents=True)
            event = {
                "event_id": "bad",
                "event_type": "conductance_weight_update",
                "edge_id": "x",
                "conductance_after": 1.0,
                "source": "telemetry",
                "previous_event_hash": "genesis",
            }
            from nexus_gate.field.conductance import _event_hash

            event["event_hash"] = _event_hash(event)
            history.write_text(__import__("json").dumps(event, sort_keys=True) + "\n", encoding="utf-8")
            report = replay_verify(root)
            self.assertEqual(report["status"], "fail")
            self.assertIn("telemetry_direct_persistent_update", report["errors"])


if __name__ == "__main__":
    unittest.main()
