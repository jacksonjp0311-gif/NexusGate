import unittest
from nexus_gate.nexus_cell.authority import decide_authority
from nexus_gate.nexus_cell.risk import capability_vector_from_action, score_risk

class TestNexusCellRisk(unittest.TestCase):
    def test_git_push_risk_greater_than_git_status(self):
        self.assertGreater(score_risk(capability_vector_from_action("git push origin main")), score_risk(capability_vector_from_action("git status")))
    def test_authority_scope_required_for_mutation(self):
        caps = capability_vector_from_action("git push origin main")
        authority = decide_authority("git push origin main", {"allow": True, "reason": "test"}, caps, authority_scope=[])
        self.assertEqual(authority["decision"], "shadow")
        self.assertEqual(authority["reason"], "authority_missing")
if __name__ == "__main__":
    unittest.main()
