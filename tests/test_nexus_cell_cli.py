import json, subprocess, sys, unittest
from pathlib import Path
from nexus_gate.nexus_cell.cli import doctor, run_cmd

class TestNexusCellCli(unittest.TestCase):
    def test_doctor_returns_success_on_repo_root(self):
        root=Path(__file__).resolve().parents[1]
        result=doctor(root)
        self.assertTrue(result["ok"], result["missing"])
    def test_mock_runner_produces_receipt(self):
        root=Path(__file__).resolve().parents[1]
        result=run_cmd(root, "mock", "NexusCell/examples/hello.ps1")
        self.assertTrue(result["ok"])
        self.assertIn("receipt_id", result["receipt"])
        self.assertEqual(result["runner"], "mock")
    def test_cli_doctor_success(self):
        root=Path(__file__).resolve().parents[1]
        completed=subprocess.run([sys.executable,"-m","nexus_gate.nexus_cell.cli","doctor","--root",str(root)],text=True,capture_output=True,check=False)
        self.assertEqual(completed.returncode,0,completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["ok"])
    def test_cli_run_mock_success(self):
        root=Path(__file__).resolve().parents[1]
        completed=subprocess.run([sys.executable,"-m","nexus_gate.nexus_cell.cli","run","--root",str(root),"--runner","mock","--payload","NexusCell/examples/hello.ps1"],text=True,capture_output=True,check=False)
        self.assertEqual(completed.returncode,0,completed.stderr)
        payload=json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertIn("receipt_id", payload["receipt"])
if __name__ == "__main__":
    unittest.main()
