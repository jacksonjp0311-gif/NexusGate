from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.epochs.seal import build_epoch_integrity_seal


ROOT = Path(__file__).resolve().parents[1]


class EpochIntegritySealV261Tests(unittest.TestCase):
    def test_epoch_seal_builds_source_root_identity(self) -> None:
        packet = build_epoch_integrity_seal(ROOT)["manifest"]
        self.assertEqual(packet["schema"], "NEXUS_SOURCE_EPOCH.v2.6.2")
        self.assertEqual(packet["product_version"], "2.6.2")
        self.assertIn(packet["epoch_state"], {"sealed_clean", "sealed_working_tree", "dehydrated"})
        self.assertEqual(len(packet["source_root"]), 64)
        self.assertEqual(len(packet["epoch_id"]), 64)
        self.assertGreater(packet["source_surface_count"], 20)
        self.assertTrue(packet["checks"]["commit_sha_not_primary_epoch"])
        self.assertIn("treat_commit_sha_as_primary_epoch", packet["blocked_actions"])
        self.assertFalse(packet["authority_boundary"]["autonomous_authority"])

    def test_epoch_cli_writes_pointer_epoch_dir_and_chain(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "nexus_gate.epochs.seal", "--root", ".", "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        packet = json.loads(proc.stdout)
        epoch_id = packet["epoch_id"]
        self.assertTrue((ROOT / "reports" / "nexus_epoch_integrity_seal_latest.json").exists())
        self.assertTrue((ROOT / "state" / "latest_epoch_pointer.json").exists())
        self.assertTrue((ROOT / "state" / "epochs" / epoch_id / "epoch_manifest.json").exists())
        self.assertTrue((ROOT / "state" / "epochs" / epoch_id / "origin_packet.json").exists())
        self.assertTrue((ROOT / "state" / "epochs" / epoch_id / "source_index.json").exists())
        self.assertTrue((ROOT / "state" / "epochs" / epoch_id / "compatibility_packet.json").exists())
        ledger = ROOT / "ledger" / "epoch_chain.jsonl"
        self.assertTrue(ledger.exists())
        last = json.loads([line for line in ledger.read_text(encoding="utf-8-sig").splitlines() if line][-1])
        self.assertEqual(last["epoch_id"], epoch_id)
        self.assertIn("event_hash", last)
        self.assertIn("previous_event_hash", last)

    def test_command_surfaces_and_docs_expose_epoch_seal(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        human = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        algorithms = (ROOT / "docs" / "algorithms" / "NEXUS_CORE_ALGORITHMS.md").read_text(encoding="utf-8-sig")
        discoveries = (ROOT / "nexus_gate" / "discoveries" / "cards.py").read_text(encoding="utf-8-sig")
        self.assertIn('"epoch-seal"', ps)
        self.assertIn("nexus_gate.epochs.seal", ps)
        self.assertIn("epoch-seal)", sh)
        self.assertIn("nexus_gate.epochs.seal", human)
        self.assertIn("v2.6.2 Causal Action Receipt Loop", readme)
        self.assertIn("reports/nexus_epoch_integrity_seal_latest.json", agents)
        self.assertIn("Epoch Integrity Seal Algorithm", algorithms)
        self.assertIn("epoch-integrity-seal", discoveries)
        self.assertTrue((ROOT / "docs" / "design" / "EPOCH_INTEGRITY_SEAL_DESIGN.md").exists())
        self.assertTrue((ROOT / "docs" / "protocols" / "EPOCH_INTEGRITY_SEAL_PROTOCOL.md").exists())


if __name__ == "__main__":
    unittest.main()
