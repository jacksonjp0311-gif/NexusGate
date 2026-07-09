
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from petri_lab.engine import run_simulation
from petri_lab.validation import validate_result, validate_run


class TestPetriDishProEngine(unittest.TestCase):
    def test_microbe_run_validates(self):
        result = run_simulation(preset="microbial_competition", steps=12, grid=24, seed=3)
        receipt = validate_result(result)
        self.assertEqual(receipt["status"], "pass")
        self.assertIn("density", result["fields"])
        self.assertGreater(sum(result["population_latest"].values()), 0)

    def test_antibiotic_selection_has_resistant_variant(self):
        result = run_simulation(preset="antibiotic_selection", steps=8, grid=24, seed=4)
        ids = {org["id"] for org in result["organisms"]}
        self.assertIn("resistant_variant", ids)
        self.assertEqual(validate_run(result)["status"], "pass")

    def test_cli_emits_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                [sys.executable, "-m", "petri_lab.cli", "--root", td, "--preset", "cellular_tissue_interaction", "--steps", "6", "--grid", "20", "--json"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertTrue((Path(td) / "reports" / "bio" / "petri_run_latest.json").exists())


if __name__ == "__main__":
    unittest.main()
