from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TestHumanSurfaceStepTimeout(unittest.TestCase):
    def test_human_surface_steps_are_timeout_bounded(self):
        script = (ROOT / "scripts" / "nexus_human.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("NEXUS_HUMAN_STEP_TIMEOUT_SECONDS", script)
        self.assertIn("[int]$TimeoutSeconds = $StepTimeoutSeconds", script)
        self.assertIn("Wait-Job -Job $job -Timeout $TimeoutSeconds", script)
        self.assertIn("NEXUS step timeout after ${TimeoutSeconds}s.", script)
        self.assertIn("[[NEXUS_EXIT_CODE:", script)
        self.assertIn("$code = 124", script)


if __name__ == "__main__":
    unittest.main()
