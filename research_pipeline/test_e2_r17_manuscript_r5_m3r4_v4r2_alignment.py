from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
R5 = ROOT / "paper_drafts/e2-state-regeneration-r5-20260904"
INTRO = R5 / "sections/01_intro.tex"
EVAL = R5 / "sections/05_evaluation_contract.tex"
RESULTS = R5 / "sections/06_current_results.tex"
DISCUSSION = R5 / "sections/07_discussion.tex"
APPENDIX = R5 / "sections/08_appendix.tex"
STATUS = R5 / "MANUSCRIPT_STATUS.md"
M3R4 = ROOT / "generated/e2-r17-exact-evidence-frozen-state-regeneration-m3r4-proposal-20260904.md"
M3R4_REVIEW = ROOT / "generated/e2-r17-m3r4-preexecution-review-pass-20260904.json"
V4R2 = ROOT / "generated/e2-r17-state-compiler-bridge-protocol-v4-r2-20260903.md"
V4R2_REVIEW = ROOT / "generated/e2-r17-state-compiler-bridge-v4r2-preexecution-rereview-20260904.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ManuscriptR5AlignmentTests(unittest.TestCase):
    def test_current_protocol_hashes_are_exact(self) -> None:
        self.assertEqual(
            sha256(M3R4),
            "2ee4d928725fbb6a3dbe02b81ca4e8fcc69fe618c995593ed050e5e8c35381b6",
        )
        self.assertEqual(
            sha256(V4R2),
            "1bc74c6f98e38535cb3865dcd41fb244b7d17c295db0ee9835937cc1034f9ef7",
        )

    def test_both_current_designs_have_independent_preexecution_pass_receipts(self) -> None:
        m3 = json.loads(M3R4_REVIEW.read_text(encoding="utf-8"))
        bridge = json.loads(V4R2_REVIEW.read_text(encoding="utf-8"))
        self.assertEqual(m3["verdict"], "PASS_PREEXECUTION_DESIGN")
        self.assertEqual(bridge["verdict"], "PASS_PREEXECUTION_DESIGN")
        self.assertFalse(m3["authority"]["m3r4_actor_execution"])
        self.assertFalse(bridge["authority"]["bridge_stage_a"])

    def test_m3r4_uses_only_two_states_and_four_fully_fresh_actor_observations_per_task(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("FF\\_R1", text)
        self.assertIn("FF\\_R2", text)
        self.assertIn("$2$ states $\\times 18$ tasks $\\times 2$ replicates $=72$ actor units", text)
        self.assertIn("Historical exact-replay actor outcomes do not count", text)
        self.assertIn("Historical FF\\_HIST and WIN\\_COMMON remain descriptive background only", text)
        self.assertNotIn("four already-existing persistent artifacts", text)

    def test_m3r4_exact_inference_requires_cross_task_factorization(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("cross-task conditional factorization", text)
        self.assertIn("\\mathrm{Binomial}(n_2,1/3)", text)
        self.assertIn("does not require equal task-specific success probabilities or exchangeability of task identities", text)
        self.assertIn("no automatic rerun is authorized", text)

    def test_bridge_primary_is_balanced_q1_and_free_b_is_not_primary(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("G_{\\mathrm{MAIN},A}(s)", text)
        self.assertIn("Only this Q1 gate may open VALIDATION", text)
        self.assertIn("FF4\\_FREE\\_B never enters the primary gate", text)
        self.assertIn("They never replace $G_{\\mathrm{MAIN},A}$", text)

    def test_bridge_q2_is_explicitly_ff4_specific(self) -> None:
        text = "\n".join(p.read_text(encoding="utf-8") for p in (INTRO, EVAL, RESULTS, DISCUSSION, APPENDIX))
        self.assertIn("FF4-specific", text)
        self.assertIn("cannot explain the Winner-side contribution", text)
        self.assertIn("cannot explain or mediate the Winner-side contribution", text)

    def test_bridge_state_sha_aliasing_is_universal(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("all} FREE, COMP, and generic-control artifacts", text)
        self.assertIn("FREE$\\leftrightarrow$COMP", text)
        self.assertIn("COMP$\\leftrightarrow$generic", text)
        self.assertIn("FREE\\_A$\\leftrightarrow$FREE\\_B", text)

    def test_bridge_q3_propensity_identity_is_model_conditional(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("conditionally iid/independent stationary actor model", text)
        self.assertIn("observed directional Q3 result remains descriptive", text)
        self.assertNotIn("under exchangeable conditional actor realizations", text)

    def test_completed_scientific_numbers_are_unchanged(self) -> None:
        text = RESULTS.read_text(encoding="utf-8")
        self.assertIn("mean rejected-witness-minus-winner contrast is $+0.0231$", text)
        self.assertIn("First-Fail is 17/18 while WIN-C is 13/18", text)
        self.assertIn("15/18 versus 14/18", text)
        self.assertIn("16/18 versus 12/18", text)
        self.assertIn("Fresh updater realization 1 yields 15/18", text)
        self.assertIn("realization 2 yields 11/18 versus 12/18", text)

    def test_r5_keeps_all_scientific_execution_unauthorized(self) -> None:
        text = STATUS.read_text(encoding="utf-8")
        for phrase in (
            "M3R4 actor execution",
            "M4/Bridge search-pool acquisition",
            "FREE_A/FREE_B updater execution",
            "SCREEN or VALIDATION outcome opening",
            "E3",
            "public benchmark",
            "submission",
        ):
            self.assertIn(phrase, text)
        self.assertIn("does **not** authorize", text)

    def test_old_m3r2_v4r1_are_chronology_only_not_current_tex(self) -> None:
        tex = "\n".join(p.read_text(encoding="utf-8") for p in R5.rglob("*.tex"))
        self.assertNotIn("M3R2", tex)
        self.assertNotIn("V4-R1", tex)
        self.assertNotIn("D_U-D_A", tex)


if __name__ == "__main__":
    unittest.main()
