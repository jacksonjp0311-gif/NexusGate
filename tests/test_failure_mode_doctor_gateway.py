import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestFailureModeDoctorGateway(unittest.TestCase):
    def test_compact_failure_mode_index(self):
        data = json.loads((ROOT / "state" / "failure_modes" / "nexus_failure_modes.v0.7.9.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(data["schema"], "nexus.failure_modes.compact.v1")
        self.assertIn("FM := id,key,n,who,why,what,when,signs,doctor,retry,authority", data["syntax"])
        self.assertGreaterEqual(len(data["modes"]), 6)
        for entry in data["modes"]:
            for key in ["id", "key", "n", "who", "why", "what", "when", "signs", "doctor", "retry", "authority"]:
                self.assertIn(key, entry)

    def test_index_preserves_launcher_parse_sign(self):
        data = json.loads((ROOT / "state" / "failure_modes" / "nexus_failure_modes.v0.7.9.json").read_text(encoding="utf-8-sig"))
        launcher_mode = next(item for item in data["modes"] if item["key"] == "launcher_parse_failure")
        signs = [str(item).lower() for item in launcher_mode["signs"]]
        self.assertIn("unexpected parser symbol", signs)

    def test_launcher_has_failure_modes_entrypoint(self):
        script = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('Write-Host "8. Failure Modes / Doctor"', script)
        self.assertIn("Invoke-NexusFailureModeDoctorConsole", script)
        self.assertIn("NEXUS FAILURE MODES / DOCTOR", script)
        self.assertIn("Doctor scan current state", script)
        self.assertIn("Safe clean generated residue", script)
        self.assertIn("Retry validation checks", script)

    def test_doctor_uses_safe_untracked_cleanup(self):
        script = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("git ls-files --others --exclude-standard -- reports", script)
        self.assertIn("Doctor classifies and recommends", script)
        self.assertIn("Working tree is clean", script)

    def test_failure_mode_doctor_doc_is_compressed_and_readable(self):
        doc = (ROOT / "docs" / "failure_modes" / "NEXUS_FAILURE_MODE_DOCTOR.md").read_text(encoding="utf-8-sig")
        self.assertIn("NEXUS Failure Mode Doctor", doc)
        self.assertIn("FM := id,key,n,who,why,what,when,signs,doctor,retry,authority", doc)
        self.assertIn("scan -> classify -> explain", doc)
        self.assertIn("Doctor classifies", doc)

    def test_readme_mentions_failure_mode_doctor_gateway(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("Failure Modes / Doctor Gateway", readme)
        self.assertIn("8. Failure Modes / Doctor", readme)
        self.assertIn("human-readable, AI-parsable, and troubleshootable", readme)


if __name__ == "__main__":
    unittest.main()
