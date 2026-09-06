from __future__ import annotations

import unittest
from pathlib import Path

from scripts.analyze_e2_r17_m3r4 import classify

ROOT = Path(__file__).resolve().parents[1]


class M3R4PostMeasurementGateTests(unittest.TestCase):
    def _metrics(self, **updates):
        row = {
            "state_sha_alias": False,
            "within_task_iid_stationarity_qualified": True,
            "cross_task_factorization_qualified": True,
            "e_real": 0.2,
            "exact_one_sided_p": 0.01,
        }
        row.update(updates)
        return row

    def test_pass_requires_positive_exact_and_both_qualifications(self) -> None:
        self.assertEqual(
            classify(self._metrics()),
            "M3R4_SELECTED_CASE_STATE_REALIZATION_LOCALIZATION_PASS",
        )

    def test_nonpositive_excess_downgrades_mechanism(self) -> None:
        self.assertEqual(
            classify(self._metrics(e_real=0.0)),
            "ACTOR_NOISE_NOT_EXCLUDED / DOWNGRADE_STATE_REGENERATION_MECHANISM",
        )

    def test_positive_but_p_above_alpha_is_descriptive_only(self) -> None:
        self.assertEqual(
            classify(self._metrics(exact_one_sided_p=0.06)),
            "M3R4_OBSERVED_EXCESS_ONLY_NO_PROPENSITY_LOCALIZATION",
        )

    def test_within_task_blocker_preempts_numerical_pass(self) -> None:
        self.assertEqual(
            classify(self._metrics(within_task_iid_stationarity_qualified=False)),
            "M3R4_WITHIN_TASK_INFERENCE_ASSUMPTION_BLOCKED",
        )

    def test_cross_task_blocker_preempts_numerical_pass(self) -> None:
        self.assertEqual(
            classify(self._metrics(cross_task_factorization_qualified=False)),
            "M3R4_CROSS_TASK_FACTORIZATION_BLOCKED",
        )

    def test_state_alias_forces_zero_localization_class(self) -> None:
        self.assertEqual(
            classify(self._metrics(state_sha_alias=True)),
            "M3R4_STATE_SHA_ALIAS_ZERO_LOCALIZATION",
        )

    def test_completion_audit_never_opens_trajectory_json(self) -> None:
        source = (ROOT / "scripts/audit_e2_r17_m3r4_completion.py").read_text(encoding="utf-8")
        self.assertNotIn("load_json(trajectory", source)
        self.assertNotIn("trajectory.get(\"score\")", source)
        self.assertIn("sha256_file(trajectory)", source)

    def test_analyzer_binds_single_use_analysis_authorization_before_score_read(self) -> None:
        source = (ROOT / "scripts/analyze_e2_r17_m3r4.py").read_text(encoding="utf-8")
        auth_check = source.index("analysis_auth.get(\"status\")")
        score_read = source.index("raw_score = trajectory.get(\"score\")")
        self.assertLess(auth_check, score_read)


if __name__ == "__main__":
    unittest.main()
