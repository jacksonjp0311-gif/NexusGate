from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from nexus_gate.loops.certificate_resume import build_certificate_resume_packet


ROOT = Path(__file__).resolve().parents[1]


class CertificateResumeTests(unittest.TestCase):
    def test_packet_hashes_passed_gate_evidence(self) -> None:
        packet = build_certificate_resume_packet(ROOT)
        self.assertEqual(packet["schema"], "NEXUS_CERTIFICATE_RESUME.v0.1.0")
        self.assertIn(packet["status"], {"pass", "warn"})
        self.assertTrue(packet["final_evolve_required_before_commit"])
        self.assertIn("skip_final_evolve_before_commit", packet["blocked_actions"])
        self.assertFalse(packet["authority_boundary"]["skip_final_evolve"])
        self.assertFalse(packet["authority_boundary"]["repo_mutation"])
        for cert in packet["passed_gate_certificates"]:
            self.assertRegex(cert["evidence_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(cert["input_fingerprint_sha256"], r"^[0-9a-f]{64}$")

    def test_cli_writes_report_and_state(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "nexus_gate.loops.certificate_resume", "--root", ".", "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertEqual(packet["schema"], "NEXUS_CERTIFICATE_RESUME.v0.1.0")
        self.assertTrue((ROOT / "reports" / "nexus_certificate_resume_report_latest.json").exists())
        self.assertTrue((ROOT / "state" / "loops" / "nexus_certificate_resume_latest.json").exists())

    def test_command_surfaces_expose_certificate_resume(self) -> None:
        ps = (ROOT / "scripts" / "nexus.ps1").read_text(encoding="utf-8-sig")
        sh = (ROOT / "scripts" / "nexus.sh").read_text(encoding="utf-8-sig")
        self.assertIn('"certificate-resume"', ps)
        self.assertIn("nexus_gate.loops.certificate_resume", ps)
        self.assertIn("certificate-resume)", sh)
        self.assertIn("nexus_gate.loops.certificate_resume", sh)


if __name__ == "__main__":
    unittest.main()
