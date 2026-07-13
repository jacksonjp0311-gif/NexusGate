from __future__ import annotations

import unittest
from pathlib import Path

from nexus_gate.language.activation import activate
from nexus_gate.language.corpus import build_graph
from nexus_gate.language.retrieval import query
from nexus_gate.language.self_model import build as build_self_model
from nexus_gate.language.token_field import realize
from nexus_gate.language.tokenizer import tokenize


ROOT = Path(__file__).resolve().parents[1]


class GeometricLanguageModelV290Tests(unittest.TestCase):
    def test_tokenizer_preserves_code_tokens(self) -> None:
        tokens = tokenize("Run nexus.cortex-refresh for nexus_gate/field/conductance.py")
        normalized = [token.normalized for token in tokens]
        self.assertIn("nexus.cortex-refresh", normalized)
        self.assertIn("nexus_gate/field/conductance.py", normalized)

    def test_query_maps_learning_question_and_is_grounded(self) -> None:
        packet = query(ROOT, "What is NEXUS permitted to learn?")
        self.assertEqual(packet["schema"], "NEXUS_LANGUAGE_QUERY.v2.9.0")
        self.assertEqual(packet["intent"]["selected"], "inspect_learning")
        self.assertTrue(packet["grounding"])
        self.assertFalse(packet["authority_boundary"]["may_execute"])

    def test_unsupported_question_abstains(self) -> None:
        packet = query(ROOT, "Who won a private chess game on Mars yesterday?")
        self.assertIn(packet["intent"]["selected"], {"unknown_or_out_of_scope", "inspect_status"})
        if packet["intent"]["selected"] == "unknown_or_out_of_scope":
            self.assertIn("does not currently have verified evidence", packet["answer"])

    def test_activation_converges_and_caps(self) -> None:
        graph, _ = build_graph(ROOT)
        seed = next(iter(graph.nodes))
        result = activate(graph, {seed: 10.0})
        self.assertLessEqual(max(result["activations"].values()), 1.0)
        self.assertLessEqual(result["iterations"], 8)

    def test_self_model_is_evidence_bound(self) -> None:
        packet = build_self_model(ROOT)
        self.assertIn("README.md", packet["evidence"])
        self.assertIn("autonomous_authority", packet["blocked_claims"])

    def test_token_field_is_deterministic_and_preserves_commands(self) -> None:
        output = realize("Use nexus.language-query now", seed=42)
        self.assertIn("nexus.language-query", output["text"])
        self.assertEqual(output, realize("Use nexus.language-query now", seed=42))


if __name__ == "__main__":
    unittest.main()
