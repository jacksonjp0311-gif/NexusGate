from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PetriDishProInterlinkTests(unittest.TestCase):
    def test_nexus_root_bridge_exists(self) -> None:
        readme = (ROOT / "PetriDishPro" / "README.md").read_text(encoding="utf-8-sig")
        manifest = json.loads((ROOT / "PetriDishPro" / "petri_bridge_manifest.v0.1.0.json").read_text(encoding="utf-8-sig"))
        bridge = (ROOT / "PetriDishPro" / "NEXUS_BRIDGE.md").read_text(encoding="utf-8-sig")
        self.assertIn("PetriDishPro / Organism Gate", readme)
        self.assertIn("NEXUS Embedded PetriDishPro Bridge", bridge)
        self.assertEqual(manifest["bridge"], "PetriDishPro")
        self.assertEqual(manifest["source_mode"], "repo_embedded")
        self.assertEqual(manifest["embedded_root"], "PetriDishPro")
        self.assertEqual(manifest["portal"]["menu_entry"], "[15] PetriDishPortal")
        self.assertIn("simulation_as_empirical_proof", manifest["blocked_actions"])
        self.assertIn("not microscopy evidence", manifest["claim_boundary"])

    def test_electron_mini_reads_live_petri_state(self) -> None:
        main = (ROOT / "electron" / "main.js").read_text(encoding="utf-8-sig")
        preload = (ROOT / "electron" / "preload.js").read_text(encoding="utf-8-sig")
        html = (ROOT / "electron" / "renderer" / "index.html").read_text(encoding="utf-8-sig")
        renderer = (ROOT / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8-sig")
        gitnexus = (ROOT / "electron" / "renderer" / "nexus_gitnexus_local_hud.v0.5.3.js").read_text(encoding="utf-8-sig")
        self.assertIn('path.join(repoRoot, "PetriDishPro")', main)
        self.assertNotIn('path.join(os.homedir(), "OneDrive", "Desktop", "PetriDishPro")', main)
        self.assertIn("buildPetriPreviewState", main)
        self.assertIn("nexus:getPetriDishProState", main)
        self.assertIn("getPetriDishProState", preload)
        self.assertIn('id="petri-mini-canvas"', html)
        self.assertIn("NEXUS_PETRIDISH_MINI_LAYOUT_REPAIR_V011", html)
        self.assertIn("drawPetriPreview", renderer)
        self.assertIn("2 um", renderer)
        self.assertIn("refreshPetriPreview", renderer)
        self.assertIn('document.querySelector(".petri-dish-mini")', gitnexus)
        self.assertIn("petriAligned", gitnexus)

    def test_spiral_core_portal_exposes_petridishportal(self) -> None:
        portal = (ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("function Invoke-NexusPetriDishPortal", portal)
        self.assertIn('Join-Path $RepoRoot "PetriDishPro"', portal)
        self.assertIn("[15] PetriDishPortal", portal)
        self.assertIn('$choice -eq "15"', portal)
        self.assertIn("ORGANISM GATE | PETRI DISH PRO", portal)

    def test_docs_and_readme_name_interlink(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        doc = (ROOT / "docs" / "runtime" / "NEXUS_PETRIDISH_PORTAL.md").read_text(encoding="utf-8-sig")
        self.assertIn("PetriDishPortal", readme)
        self.assertIn("PetriDishPortal", doc)
        self.assertIn("embedded PetriDishPro", doc)
        self.assertLess(len(readme.splitlines()), 220)

    def test_petridishpro_source_is_embedded(self) -> None:
        expected = [
            "electron/main.js",
            "electron/renderer/index.html",
            "petri_lab/cli.py",
            "petri_lab/particle_state.py",
            "config/bio/preset_card_registry.json",
            "reports/bio/petri_particle_state_latest.json",
            "artifacts/bio/runs/petri_preview/cells.json",
            "artifacts/bio/runs/petri_preview/particles.json",
        ]
        for rel_path in expected:
            with self.subTest(rel_path=rel_path):
                self.assertTrue((ROOT / "PetriDishPro" / rel_path).exists())


if __name__ == "__main__":
    unittest.main()
