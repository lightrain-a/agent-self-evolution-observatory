from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "generated/e2-r17-state-compiler-bridge-protocol-v3-review-repair-20260903.md"
M3 = ROOT / "generated/e2-r17-exact-evidence-frozen-state-regeneration-m3-proposal-20260903.md"
MANUSCRIPT = ROOT / "paper_drafts/e2-state-regeneration-r2-20260903/main.tex"
STATUS = ROOT / "paper_drafts/e2-state-regeneration-r2-20260903/MANUSCRIPT_STATUS.md"


class ManuscriptReviewRepairTests(unittest.TestCase):
    def test_title_drops_state_generation_variance_claim(self) -> None:
        text = MANUSCRIPT.read_text(encoding="utf-8")
        self.assertIn("State-Regeneration Instability in Self-Evolving Agents", text)
        self.assertNotIn("Diagnosing State-Generation Variance", text)

    def test_protocol_separates_generator_content_and_failure_gates(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("GENERATOR_SCREEN_PASS", text)
        self.assertIn("CONTENT_SCREEN_PASS", text)
        self.assertIn("REJECTED_SOURCE_SCREEN_FAIL", text)
        self.assertIn("cannot veto generator VALIDATION", text)
        self.assertIn("SCOPE_MATCHED_GENERIC_MAX", text)

    def test_bridge_preconditions_use_revised_m3_not_manual_arm_rerun(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("revised M3R exact-evidence frozen-state regeneration audit", text)
        self.assertIn("FF_HIST", text)
        self.assertIn("FF_R1", text)
        self.assertIn("FF_R2", text)
        self.assertIn("WIN_COMMON", text)
        self.assertNotIn("Only G0 + the simplest passing selected arm are remeasured", text)

    def test_validation_primary_does_not_average_second_free_draw(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("G_F_A = J(FF4_COMP) - J(FF4_FREE_A)", text)
        self.assertIn("does not change the primary generator estimand", text)
        self.assertNotIn("G_F_AB = J(FF4_COMP) - J(FF4_FREE_AB)", text)

    def test_m3_reuses_existing_states_and_has_no_updater_authority(self) -> None:
        text = M3.read_text(encoding="utf-8")
        for digest in (
            "97e28b4862ed5817929fa6014eb1ba1401667875d80e03d18c0b54978a185252",
            "596bd30b49935d16f35d51e9eed36e19567332cd8a9104ae50d832f91ffdf04f",
            "fb5454a27faf8182ba1b0d722273c4377d4762815cd1898c3780cc8ff336615e",
            "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
        ):
            self.assertIn(digest, text)
        self.assertIn("72 new actor units", text)
        self.assertIn("No new state synthesis is allowed", text)
        self.assertIn("provider calls;", text)
        self.assertIn("updater calls;", text)
        self.assertIn("D_U - D_A > 0", text)

    def test_r2_status_keeps_recovery_v3_untouched(self) -> None:
        text = STATUS.read_text(encoding="utf-8")
        self.assertIn("does not authorize", text)
        self.assertIn("Recovery V3 execution or modification", text)
        self.assertIn("No partial M2 effect was read", text)


if __name__ == "__main__":
    unittest.main()
