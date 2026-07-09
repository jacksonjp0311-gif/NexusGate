import json
import subprocess
import sys
import unittest
from pathlib import Path

class ParticleState004NTests(unittest.TestCase):
    def root(self):
        return Path(__file__).resolve().parents[1]

    def test_particle_state_module_uses_correct_datetime(self):
        text = (self.root() / "petri_lab" / "particle_state.py").read_text(encoding="utf-8")
        self.assertIn("dt.datetime.now", text)
        self.assertNotIn('__import__("datetime").datetime.datetime', text)

    def test_latest_particle_report_exists_and_points_to_artifacts(self):
        root = self.root()
        latest = root / "reports" / "bio" / "petri_particle_state_latest.json"
        if not latest.exists():
            subprocess.run([sys.executable, "-m", "petri_lab.particle_state", "--root", "."], cwd=root, check=True)
        data = json.loads(latest.read_text(encoding="utf-8-sig"))
        blob = json.dumps(data)
        for name in ["cells.json", "particles.json", "interactions.json", "fields.json"]:
            self.assertIn(name, blob)

    def test_electron_particle_bridge_visible(self):
        root = self.root()
        main = (root / "electron" / "main.js").read_text(encoding="utf-8")
        preload = (root / "electron" / "preload.js").read_text(encoding="utf-8")
        app = (root / "electron" / "renderer" / "app.js").read_text(encoding="utf-8")
        self.assertIn("petri:readParticleState", main)
        self.assertIn("readParticleState", preload)
        self.assertIn("loadParticleArtifactState", app)
        self.assertIn("applyParticleArtifactsToWorld", app)
        self.assertIn("Python biology kernel -> cells.json", app)

if __name__ == "__main__":
    unittest.main()
