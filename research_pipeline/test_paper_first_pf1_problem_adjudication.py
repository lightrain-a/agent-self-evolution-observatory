from __future__ import annotations

import unittest

from .paper_first_pf1_problem_adjudication import build_pf1_problem_adjudication, validate_pf1_problem_adjudication


class PaperFirstPF1ProblemAdjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_pf1_problem_adjudication()

    def test_final_collision_review_stops_pf1_standalone(self) -> None:
        self.assertEqual(validate_pf1_problem_adjudication(self.state), [])
        self.assertEqual(self.state["decision"], "STOP_PF1_STANDALONE_PROBLEM_MERGE_EVOLVABILITY_AUDIT")
        self.assertEqual(self.state["paper_problem_status"], "TERMINATED_AS_STANDALONE_AFTER_FINAL_COLLISION_REVIEW")
        self.assertFalse(self.state["authority"]["paper_problem_active"])

    def test_all_novelty_escape_routes_are_closed(self) -> None:
        routes = {row["route"]: row for row in self.state["failed_novelty_escape_routes"]}
        self.assertEqual(len(routes), 4)
        self.assertTrue(all(row["status"] == "closed" for row in routes.values()))
        self.assertIn("continual-learning plasticity", routes["future-learnability AUC under fixed update budget"]["collision"])
        self.assertIn("Continuous Program Search", routes["state-operator compatibility / reachable-set contraction"]["collision"])

    def test_same_information_reduction_has_no_irreducible_agent_only_variable(self) -> None:
        reduction = self.state["same_information_reduction"]
        self.assertIsNone(reduction["irreducible_agent_only_variable"])
        self.assertFalse(reduction["domain_transfer_is_sufficient_novelty"])
        self.assertIn("future-adaptation/evolvability", reduction["statement"])

    def test_two_independent_reviews_converge_on_stop_but_are_not_authority(self) -> None:
        reviewers = self.state["reviewers"]
        self.assertEqual(set(reviewers), {"deepseek_v4_pro", "glm_5_2"})
        self.assertTrue(all(row["verdict"] == "STOP_STANDALONE_PROBLEM" for row in reviewers.values()))
        self.assertTrue(all(row["authority"] == "advisory-only" for row in reviewers.values()))
        self.assertFalse(self.state["review_synthesis"]["ai_is_authority"])

    def test_no_downstream_authority_is_created(self) -> None:
        authority = self.state["authority"]
        for key, value in authority.items():
            self.assertFalse(value, key)
        self.assertIn("PF-3/PF-5/PF-7", self.state["next_action"])


if __name__ == "__main__":
    unittest.main()
