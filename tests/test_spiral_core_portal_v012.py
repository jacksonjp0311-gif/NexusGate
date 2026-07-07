import json
import pathlib
import re
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PORTAL = REPO_ROOT / "scripts" / "desktop" / "open_nexus_gate_console.ps1"
DOC = REPO_ROOT / "docs" / "runtime" / "NEXUS_SPIRAL_CORE_PORTAL.md"
MANIFEST = REPO_ROOT / "state" / "portal" / "spiral_core_portal_manifest.v0.1.2.json"


def read_portal() -> str:
    return PORTAL.read_text(encoding="utf-8-sig")


def portal_section(text: str) -> str:
    return text.split("NEXUS_SPIRAL_CORE_ASCII_BEGIN", 1)[1].split("NEXUS_SPIRAL_CORE_ASCII_END", 1)[0]


def write_portal_lines(text: str):
    lines = []
    for raw in text.splitlines():
        match = re.search(r'Write-Portal\s+"(.*)"\s+"([A-Za-z]+)"', raw)
        if match:
            lines.append((match.group(1), match.group(2)))
    return lines


def route_lines(text: str):
    return [
        (line, color) for line, color in write_portal_lines(text)
        if re.search(r"\[\d+\]\s+", line) or "[Q]" in line
    ]


def has_route_with_color(text: str, route_fragment: str, color: str) -> bool:
    return any(route_fragment in line and line_color == color for line, line_color in route_lines(text))


class TestSpiralCorePortalV012(unittest.TestCase):
    def test_spiral_core_identity_is_default_menu_face(self):
        text = read_portal()
        self.assertIn("NEXUS GATE :: SPIRAL CORE PORTAL", text)
        self.assertIn("N E X U S   G A T E", text)
        self.assertIn("S P I R A L   C O R E   P O R T A L", text)
        self.assertIn("NEXUS_SPIRAL_CORE_ASCII_BEGIN", text)
        self.assertIn("NEXUS_SPIRAL_CORE_ASCII_END", text)

    def test_visual_balance_has_black_hole_core_not_flat_band(self):
        text = read_portal()
        section = portal_section(text)
        self.assertIn("01110010 01101111", section)
        self.assertIn("(  )", section)
        self.assertIn("''", section)
        self.assertIn("######", section)
        self.assertIn(".:-+*################*+-:.", section)
        self.assertNotIn("_   _ _______", section)
        self.assertNotIn("| \\ | |", section)

    def test_selector_color_hierarchy_is_blue_and_cyan_only(self):
        text = read_portal()
        live_routes = route_lines(text)
        self.assertGreaterEqual(len(live_routes), 14)
        live_colors = {color for _, color in live_routes}
        self.assertTrue(live_colors.issubset({"Cyan", "Blue"}), live_colors)
        self.assertNotIn("Yellow", live_colors)
        self.assertNotIn("Magenta", live_colors)
        self.assertNotIn("Green", live_colors)

        self.assertTrue(has_route_with_color(text, "[1]  Open NexusGate", "Cyan"))
        self.assertTrue(has_route_with_color(text, "[2]  Dev Mode / Handoff Console", "Blue"))
        self.assertTrue(has_route_with_color(text, "[3]  Status / health surface", "Cyan"))
        self.assertTrue(has_route_with_color(text, "[8]  Failure Modes / Doctor", "Blue"))
        self.assertTrue(has_route_with_color(text, "[11] NexusShell / Operator", "Blue"))
        self.assertTrue(has_route_with_color(text, "[13] Neural Activity / Cathedral", "Cyan"))

    def test_selector_block_is_left_aligned(self):
        text = read_portal()
        live_routes = route_lines(text)
        leading_spaces = [len(line) - len(line.lstrip(" ")) for line, _ in live_routes]
        self.assertGreaterEqual(len(live_routes), 14)
        self.assertLessEqual(max(leading_spaces), 4)
        self.assertEqual(min(leading_spaces), 2)

    def test_doctrine_lines_and_legacy_markers_remain_visible_to_tests(self):
        text = read_portal()
        self.assertIn("WE DO NOT OBEY CHAOS. WE GOVERN THRESHOLDS.", text)
        self.assertIn("AUTHORITY IS EARNED. ACCESS IS EVIDENCE.", text)
        self.assertIn("Rule: models recommend; human authorizes durable mutation.", text)
        self.assertIn("Flow: portal -> surface -> evidence -> gate -> durable commit.", text)

        self.assertIn("The gate does not give intelligence authority.", text)
        self.assertIn("The gate gives authority a visible path through intelligence.", text)
        self.assertIn("NEXUS GATE :: DESKTOP ENTRY PORTAL", text)
        self.assertIn("cyber ice-blue gateway for human + AI intelligence flow", text)

    def test_all_routes_remain_rendered_and_handled(self):
        text = read_portal()
        for route in [
            "[1]  Open NexusGate",
            "[2]  Dev Mode / Handoff Console",
            "[3]  Status / health surface",
            "[4]  Terminal TUI surface",
            "[5]  NN router health",
            "[6]  Ask NEXUS router",
            "[7]  Open repo folder",
            "[8]  Failure Modes / Doctor",
            "[9]  GitHub / README / Docs",
            "[9] GitHub / README / Docs",
            "[10] NexusCell / Containment",
            "[11] NexusShell / Operator",
            "[12] NexusCell - Containment Cell / Gate",
            "[13] Neural Activity / Cathedral",
            "[Q]  Quit",
        ]:
            self.assertIn(route, text)

        for choice in ['"1"', '"2"', '"3"', '"4"', '"5"', '"6"', '"7"', '"8"', '"9"', '"10"', '"11"', '"12"', '"13"']:
            self.assertIn(f"$choice -eq {choice}", text)

        self.assertIn("Invoke-NexusNeuralActivity", text)
        self.assertIn("Invoke-NexusShellConsole", text)
        self.assertIn("Invoke-NexusCellExecutionGateConsole", text)

    def test_no_mojibake_or_unicode_block_art_remains_in_launcher(self):
        text = read_portal()
        for bad in ["Ã¢", "â•”", "â–ˆ", "â—", "âŠ", "âŠ"]:
            self.assertNotIn(bad, text)

    def test_spiral_core_lines_stay_within_terminal_width(self):
        text = read_portal()
        string_literals = [line for line, _ in write_portal_lines(text)]
        self.assertTrue(string_literals)
        self.assertLessEqual(max(len(line) for line in string_literals), 124)

    def test_docs_and_manifest_lock_visual_only_boundary(self):
        doc = DOC.read_text(encoding="utf-8-sig")
        self.assertIn("Close H visual correction", doc)
        self.assertIn("blue and light-blue", doc)
        self.assertIn("keeps the tightened black-hole/event-horizon core", doc)
        self.assertIn("visual and navigational only", doc)
        self.assertIn("Neural Activity / Cathedral", doc)

        data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        self.assertEqual(data["version"], "v0.1.2-close-h")
        self.assertTrue(data["no_authority_change"])
        self.assertTrue(data["no_execution_change"])
        self.assertTrue(data["ascii_only_portal_art"])
        self.assertEqual(data["selector_color_hierarchy"]["default"], "Cyan")
        self.assertEqual(data["selector_color_hierarchy"]["alternate"], "Blue")
        self.assertIn("Green", data["disallowed_selector_colors"])
        self.assertIn("13", data["preserved_routes"])


if __name__ == "__main__":
    unittest.main()
