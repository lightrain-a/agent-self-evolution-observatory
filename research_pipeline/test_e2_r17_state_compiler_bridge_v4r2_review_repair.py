from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "generated/e2-r17-state-compiler-bridge-protocol-v4-r2-20260903.md"
REVIEW = ROOT / "generated/e2-r17-v4r1-m3r2-preexecution-oracle-review-20260903.json"


class StateCompilerBridgeV4R2ReviewRepairTest(unittest.TestCase):
    def test_review_verdict_is_revision_not_pass(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")
        self.assertIn('"verdict": "REVISE_BEFORE_STAGE_A"', text)
        self.assertIn('"verdict": "REVISE_M3R2_BEFORE_EXECUTION"', text)
        self.assertNotIn('"verdict": "PASS_V4_R1_PREEXECUTION_DESIGN"', text)

    def test_q3_identity_requires_iid_stationary_actor_model(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("conditionally iid/independent and stationary", text)
        self.assertIn("model-based interpretation", text)
        self.assertIn("observed cross-state-minus-within-state disagreement statistic", text)
        self.assertNotIn("under exchangeable conditional actor realizations", text)

    def test_state_sha_equivalence_is_universal(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("across every arm in the stage", text)
        self.assertIn("FREE↔COMP", text)
        self.assertIn("COMP↔generic", text)
        self.assertIn("FREE↔generic", text)
        self.assertIn("`J_s(arm)` is defined on the state-SHA equivalence class observation", text)

    def test_q2_is_explicitly_ff4_only_and_not_q1_mechanism(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("FF4 trajectory-conditioned diagnosis interpretation", text)
        self.assertIn("FF4-only", text)
        self.assertIn("cannot be used to claim that typed FF4 diagnosis explains the Winner-side component", text)
        self.assertIn("cannot explain or mediate a Q1 main effect", text)

    def test_q1_factorial_estimand_is_unchanged(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("G_MAIN,A(s) = 0.5", text)
        self.assertIn("G_W(s)", text)
        self.assertIn("G_F,A(s)", text)
        self.assertIn("RAW_GENERATOR_SCREEN_PASS", text)
        self.assertIn("RAW_GENERATOR_VALIDATION_PASS", text)

    def test_free_b_stays_out_of_primary_q1(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("`FF4_FREE_B` does **not** enter this gate", text)
        self.assertIn("do not replace `G_MAIN,A`", text)
        self.assertIn("cannot rescue a failed raw generator result", text)

    def test_no_execution_authority_added(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("NO_EXECUTION_AUTHORITY", text)
        self.assertIn("zero authority for", text)
        for item in ("provider calls", "E3", "second backbone", "public benchmark", "paper promotion"):
            self.assertIn(item, text)


if __name__ == "__main__":
    unittest.main()
