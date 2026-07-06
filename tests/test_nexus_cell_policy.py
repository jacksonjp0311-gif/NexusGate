import unittest
from nexus_gate.nexus_cell.boundary.matcher import host_matches
from nexus_gate.nexus_cell.boundary.policy import boundary_decision
from nexus_gate.nexus_cell.policy import DEFAULT_POLICY, evaluate_policy

class TestNexusCellPolicy(unittest.TestCase):
    def test_default_deny(self):
        decision = evaluate_policy({"runner": "unknown"}, DEFAULT_POLICY)
        self.assertFalse(decision["allow"])
        self.assertEqual(decision["reason"], "default_deny")
    def test_mock_runner_allowed(self):
        decision = evaluate_policy({"runner": "mock"}, DEFAULT_POLICY)
        self.assertTrue(decision["allow"])
        self.assertEqual(decision["rule"], "allow_mock_local_readonly")
    def test_host_wildcard(self):
        self.assertTrue(host_matches("*.example.com", "api.example.com"))
        self.assertTrue(host_matches("*.example.com", "a.b.example.com"))
        self.assertFalse(host_matches("*.example.com", "example.com"))
    def test_boundary_default_deny(self):
        decision = boundary_decision({"host": "evil.test"}, [{"name": "allow_api", "match": {"host": "api.example.com"}, "action": "allow"}])
        self.assertEqual(decision["action"], "deny")
if __name__ == "__main__":
    unittest.main()
