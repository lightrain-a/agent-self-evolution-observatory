from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
R4 = ROOT / "paper_drafts/e2-state-regeneration-r4-20260903"
EVAL = R4 / "sections/05_evaluation_contract.tex"
RESULTS = R4 / "sections/06_current_results.tex"
DISCUSSION = R4 / "sections/07_discussion.tex"
APPENDIX = R4 / "sections/08_appendix.tex"
STATUS = R4 / "MANUSCRIPT_STATUS.md"
M3R2 = ROOT / "generated/e2-r17-exact-evidence-frozen-state-regeneration-m3r2-proposal-20260903.md"
SUPER = ROOT / "generated/e2-r17-m3r-metric-supersession-20260903.json"


class ManuscriptR4M3R2AlignmentTests(unittest.TestCase):
    def test_m3_uses_repaired_commensurate_metric(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("D_X^{\\mathrm{M3}}", text)
        self.assertIn("D_A^{\\mathrm{M3}}", text)
        self.assertIn("E_{\\mathrm{REAL}}^{\\mathrm{M3}}", text)
        self.assertIn("\\mathrm{mean}_q[p_A(q)-p_B(q)]^2", text)
        self.assertIn("supersedes the unused earlier $D_U-D_A$ statistic", text)

    def test_m3_budget_and_states_are_not_expanded(self) -> None:
        text = "\n".join(
            p.read_text(encoding="utf-8") for p in (EVAL, RESULTS, APPENDIX, STATUS)
        )
        self.assertIn("72 new actor units", STATUS.read_text(encoding="utf-8"))
        self.assertIn("no updater call", text.lower())
        for short in ("97e28b4862", "596bd30b49", "fb5454a27f", "6df40f6170"):
            self.assertIn(short, text)

    def test_m3r2_supersession_is_explicit_and_preexecution(self) -> None:
        status = STATUS.read_text(encoding="utf-8")
        proposal = M3R2.read_text(encoding="utf-8")
        sup = SUPER.read_text(encoding="utf-8")
        self.assertIn("f8fb39d2289fdc3af2baa7bec23fe9c12087c1d1", status)
        self.assertIn("No M3R outcome exists", proposal)
        self.assertIn('"scientific_outcomes": 0', sup)
        self.assertIn('"execution_authority": false', sup)

    def test_m3_claim_remains_local_not_population_variance(self) -> None:
        text = "\n".join(
            p.read_text(encoding="utf-8") for p in (EVAL, RESULTS, DISCUSSION, APPENDIX, STATUS)
        )
        self.assertIn("selected-case localization", text)
        self.assertIn("not a population variance estimate", text)

    def test_m4_v4r1_primary_logic_is_preserved(self) -> None:
        text = EVAL.read_text(encoding="utf-8")
        self.assertIn("G_{\\mathrm{MAIN},A}(s)", text)
        self.assertIn("Only this raw Q1 gate may open VALIDATION", text)
        self.assertIn("classify interpretation without deciding whether Q1 exists", text)
        self.assertIn("cannot veto Q1--Q3", text)

    def test_v4r1_review_is_still_pending(self) -> None:
        text = STATUS.read_text(encoding="utf-8")
        self.assertIn("has **not** produced a valid reviewer verdict yet", text)
        self.assertIn("zero assistant turns", text)


if __name__ == "__main__":
    unittest.main()
