from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
R3 = ROOT / "paper_drafts/e2-state-regeneration-r3-20260903"
EVAL = R3 / "sections/05_evaluation_contract.tex"
INTRO = R3 / "sections/01_intro.tex"
RESULTS = R3 / "sections/06_current_results.tex"
DISCUSSION = R3 / "sections/07_discussion.tex"
APPENDIX = R3 / "sections/08_appendix.tex"
STATUS = R3 / "MANUSCRIPT_STATUS.md"
M3 = ROOT / "generated/e2-r17-exact-evidence-frozen-state-regeneration-m3-proposal-20260903.md"


class ManuscriptR3V4R1AlignmentTests(unittest.TestCase):
    def test_primary_bridge_estimand_is_balanced_generator_factor(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("G_{\\mathrm{MAIN},A}(s)", text)
        self.assertIn("\\tfrac{1}{2}\\left[G_W(s)+G_{F,A}(s)\\right]", text)
        self.assertIn("Only this raw Q1 gate may open VALIDATION", text)
        self.assertNotIn("The generator question passes SCREEN if mean $G_F>0$", text)

    def test_generic_controls_classify_interpretation_not_q1_authority(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("classify interpretation without deciding whether Q1 exists", text)
        self.assertIn("cannot erase an independently passed Q1 complete-method effect", text)
        self.assertIn("diagnosis-cardinality-informed", text)

    def test_bridge_realization_metric_is_commensurate_dx_minus_da(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("D_X(s)", text)
        self.assertIn("D_A(s)", text)
        self.assertIn("E_{\\mathrm{REAL}}(s) &= D_X(s)-D_A(s)", text)
        self.assertIn("[p_A(q)-p_B(q)]^2", text)
        self.assertNotIn("D_U(s)", text)

    def test_free_b_is_sensitivity_only_and_never_replaces_a(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("B is a prespecified sensitivity/mechanism realization and never replaces A", text)
        self.assertIn("FF4\\_FREE\\_B does not enter either primary gate", text)
        self.assertIn("They never replace $G_{\\mathrm{MAIN},A}$", text)

    def test_state_sha_aliasing_is_explicit(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("states are partitioned by full skill SHA-256", text)
        self.assertIn("state-treatment contrast exactly zero", text)
        self.assertIn("their state-realization contrast is defined as zero", text)

    def test_q4_is_a_parked_moderator_not_primary_gate(self) -> None:
        text = "\n".join(
            p.read_text(encoding="utf-8") for p in (INTRO, EVAL, RESULTS, DISCUSSION)
        )
        self.assertIn("parked moderator", text)
        self.assertIn("cannot veto Q1--Q3", text)
        self.assertIn("explicitly drops failure-evidence superiority", text)

    def test_completed_result_claims_remain_narrow(self) -> None:
        text = RESULTS.read_text(encoding="utf-8")
        self.assertIn("mean rejected-witness-minus-winner contrast is $+0.0231$", text)
        self.assertIn("state-regeneration instability in one controlled development case", text)
        self.assertIn("does not currently claim that the typed compiler improves downstream utility", text)

    def test_m3_metric_is_not_silently_rewritten_by_bridge_alignment(self) -> None:
        m3 = M3.read_text(encoding="utf-8")
        status = STATUS.read_text(encoding="utf-8")
        self.assertIn("D_U - D_A > 0", m3)
        self.assertIn("must **not** silently rewrite the M3R contract", status)

    def test_v4r1_review_is_still_pending_not_falsely_passed(self) -> None:
        text = STATUS.read_text(encoding="utf-8")
        self.assertIn("has **not** produced a valid reviewer verdict yet", text)
        self.assertIn("zero assistant turns", text)
        self.assertNotIn("PASS_V4_R1_PREEXECUTION_DESIGN` has been obtained", text)

    def test_appendix_matches_orthogonal_claim_logic(self) -> None:
        text = APPENDIX.read_text(encoding="utf-8")
        self.assertIn("equal-weight generator-factor main effect", text)
        self.assertIn("cannot veto Q1", text)
        self.assertIn("Failure of a generic control or realization/moderator subtest instead narrows", text)


if __name__ == "__main__":
    unittest.main()
