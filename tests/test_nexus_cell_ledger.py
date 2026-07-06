import tempfile, unittest
from pathlib import Path
from nexus_gate.nexus_cell.ledger import GENESIS_HASH, append_event, ledger_summary, read_events

class TestNexusCellLedger(unittest.TestCase):
    def test_hashchain_appends(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            one=append_event(root, {"type":"test","n":1})
            two=append_event(root, {"type":"test","n":2})
            events=read_events(root)
            self.assertEqual(len(events),2)
            self.assertEqual(one["previous_ledger_hash"], GENESIS_HASH)
            self.assertEqual(two["previous_ledger_hash"], one["ledger_hash"])
            self.assertEqual(ledger_summary(root)["latest_ledger_hash"], two["ledger_hash"])
if __name__ == "__main__":
    unittest.main()
