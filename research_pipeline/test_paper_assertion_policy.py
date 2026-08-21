from __future__ import annotations

import unittest

from .paper_assertion_policy import PAPER_ASSERTION_POLICY, audit_manuscript_sources, experiment_debt_for_claim, resolve_manuscript_stance


class PaperAssertionPolicyTest(unittest.TestCase):
    def test_manuscript_completion_is_independent_of_evidence_completion(self) -> None:
        self.assertTrue(PAPER_ASSERTION_POLICY["manuscript_completion_is_separate_from_evidence_completion"])
        self.assertTrue(PAPER_ASSERTION_POLICY["complete_paper_may_retain_experiment_debt"])
        self.assertTrue(PAPER_ASSERTION_POLICY["complete_paper_requires_claim_ledger"])
        self.assertTrue(PAPER_ASSERTION_POLICY["complete_paper_requires_manuscript_qa"])

    def test_unrefuted_hypothesis_remains_active(self) -> None:
        self.assertEqual(resolve_manuscript_stance("INCONCLUSIVE"), "ACTIVE_UNREFUTED_HYPOTHESIS")
        row = experiment_debt_for_claim("C6", "INCONCLUSIVE", ["shuffled no-memory control"])
        self.assertTrue(row["retain_in_manuscript"])
        self.assertFalse(row["claim_narrowing_required"])
        self.assertEqual(row["experiment_debt"], ["shuffled no-memory control"])

    def test_refuted_claim_exits_mainline(self) -> None:
        self.assertEqual(resolve_manuscript_stance("REFUTED"), "REMOVE_OR_REFORMULATE_REFUTED_CLAIM")

    def test_manuscript_lint_requires_single_limitation_section(self) -> None:
        sources = {
            "main.tex": "\\section{Introduction}\nStrong active claim.\n",
            "sections/06_limitations_conclusion.tex": "\\section{Limitations}\nOne missing experiment is recorded here.\n",
        }
        audit = audit_manuscript_sources(sources, limitations_source="sections/06_limitations_conclusion.tex")
        self.assertTrue(audit["passed"], audit["violations"])

    def test_manuscript_lint_rejects_distributed_limitation_and_forbidden_prose(self) -> None:
        sources = {
            "main.tex": (
                "\\section{Introduction}\n"
                "We do not claim X but Y. The system uses alpha, beta, and gamma.\n"
            ),
            "sections/06_limitations_conclusion.tex": "\\section{Limitations}\nScope note.\n",
        }
        audit = audit_manuscript_sources(sources, limitations_source="sections/06_limitations_conclusion.tex")
        rules = {row["rule"] for row in audit["violations"]}
        self.assertIn("distributed_limitation_language", rules)
        self.assertIn("not_but_contrast", rules)
        self.assertIn("serial_enumeration_sentence", rules)


if __name__ == "__main__":
    unittest.main()
