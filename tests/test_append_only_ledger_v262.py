from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from nexus_gate.ledger.append_only import append_hash_chained_event, verify_hash_chain


class AppendOnlyLedgerV262Tests(unittest.TestCase):
    def test_chain_append_and_verify(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            first = append_hash_chained_event(ledger, {"event_type": "one"}, producer="test")
            second = append_hash_chained_event(ledger, {"event_type": "two"}, producer="test")
            packet = verify_hash_chain(ledger)
            self.assertTrue(packet["chain_valid"])
            self.assertEqual(packet["chain_length"], 2)
            self.assertEqual(second["previous_event_hash"], first["event_hash"])

    def test_tampered_row_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            append_hash_chained_event(ledger, {"event_type": "one"}, producer="test")
            row = json.loads(ledger.read_text(encoding="utf-8"))
            row["event_type"] = "tampered"
            ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
            packet = verify_hash_chain(ledger)
            self.assertFalse(packet["chain_valid"])
            self.assertGreater(packet["hash_mismatches"], 0)


if __name__ == "__main__":
    unittest.main()
