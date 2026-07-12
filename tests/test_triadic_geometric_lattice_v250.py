from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.decision.arbiter import arbitrate_recommendations
from nexus_gate.decision.envelope import build_decision_envelope
from nexus_gate.lattice.triadic import build_triadic_lattice


ROOT = Path(__file__).resolve().parents[1]


class TriadicGeometricLatticeV250Tests(unittest.TestCase):
    def test_lattice_packet_scores_three_axes_without_authority(self) -> None:
        recs = [
            {
                "source": "git-scope",
                "action": "inspect_dirty_scope",
                "command": ".\\scripts\\nexus.ps1 preflight-json",
                "source_packet_hash": "abc",
                "source_packet_freshness": {"fresh": True},
            }
        ]
        packet = build_triadic_lattice(ROOT, recs)
        self.assertEqual(packet["schema"], "NEXUS_TRIADIC_GEOMETRIC_LATTICE.v2.5.0")
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertIn("evidence", packet["triad"])
        self.assertIn("geometry", packet["triad"])
        self.assertIn("authority", packet["triad"])
        self.assertEqual(len(packet["route_alignments"]), 1)
        alignment = packet["route_alignments"][0]
        self.assertGreater(alignment["alignment"], 0)
        self.assertIn("arbiter_adjustment", alignment)
        self.assertIn("promote_geometry_to_authority", packet["blocked_actions"])
        self.assertIn("does not execute", packet["claim_boundary"])

    def test_lattice_adjustment_reaches_arbiter(self) -> None:
        recs = [
            {
                "source": "git-scope",
                "action": "inspect_dirty_scope",
                "command": ".\\scripts\\nexus.ps1 preflight-json",
                "why": "bounded geometry",
                "severity": "medium",
                "confidence": 0.8,
                "estimated_cost": "short",
                "source_packet_hash": "abc",
                "triadic_lattice": {"arbiter_adjustment": 5.0},
            }
        ]
        result = arbitrate_recommendations(recs)
        self.assertEqual(result["schema"], "NEXUS_RECOMMENDATION_ARBITER.v2.5.0")
        self.assertEqual(result["selected"]["arbiter_factors"]["triadic_lattice_adjustment"], 5.0)
        self.assertEqual(result["lattice_input"]["routes_with_alignment"], 1)

    def test_decision_envelope_contains_lattice(self) -> None:
        packet = build_decision_envelope(ROOT, intent="triadic lattice test")
        self.assertEqual(packet["schema"], "NEXUS_DECISION_ENVELOPE.v2.5.0")
        self.assertEqual(packet["version"], "2.5.0")
        self.assertEqual(packet["mode"], "triadic_lattice_decision_envelope")
        self.assertIn("triadic_lattice", packet)
        self.assertEqual(packet["triadic_lattice"]["schema"], "NEXUS_TRIADIC_GEOMETRIC_LATTICE.v2.5.0")
        self.assertIn("triadic_lattice_adjustment", packet["arbiter"]["selected"]["arbiter_factors"])

    def test_cli_and_command_surfaces_expose_lattice(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "nexus_gate.lattice.triadic", "--root", ".", "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertEqual(packet["schema"], "NEXUS_TRIADIC_GEOMETRIC_LATTICE.v2.5.0")
        self.assertTrue((ROOT / "reports" / "nexus_triadic_lattice_latest.json").exists())
        self.assertTrue((ROOT / "state" / "lattice" / "nexus_triadic_lattice_latest.json").exists())
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('"triadic-lattice"', ps)
        self.assertIn("nexus_gate.lattice.triadic", ps)
        self.assertIn("triadic-lattice)", sh)
        self.assertIn("nexus_gate.lattice.triadic", human)
        self.assertIn("16f2_triadic_lattice", human)

    def test_docs_and_cards_record_lattice(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        algorithms = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8-sig")
        discoveries = (ROOT / "nexus_gate" / "discoveries" / "cards.py").read_text(encoding="utf-8-sig")
        self.assertIn("v2.5.0 Triadic Geometric Lattice", readme)
        self.assertIn("Triadic Geometric Lattice Algorithm", algorithms)
        self.assertIn("triadic-geometric-lattice-routing", discoveries)
        self.assertTrue((ROOT / "docs" / "design" / "TRIADIC_GEOMETRIC_LATTICE_DESIGN.md").exists())
        self.assertTrue((ROOT / "docs" / "protocols" / "TRIADIC_GEOMETRIC_LATTICE_PROTOCOL.md").exists())


if __name__ == "__main__":
    unittest.main()
