from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from . import asset_first_stri_skillrl_final_policy_p0e_principle_disposition as disposition
from . import asset_first_stri_skillrl_final_policy_p0e_same_information_screen as screen
from . import asset_first_stri_skillrl_final_policy_p0e_statistical_resolution_audit as stat_audit


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SkillRLP0EPostNegativeTest(unittest.TestCase):
    def test_registered_effect_floor_is_not_mcnemar_resolved(self) -> None:
        self.assertEqual(stat_audit.exact_mcnemar_two_sided_unidirectional(3), 0.25)
        minimum = next(
            k for k in range(1, 25)
            if stat_audit.exact_mcnemar_two_sided_unidirectional(k) < 0.05
        )
        self.assertEqual(minimum, 6)
        self.assertEqual(minimum / 24, 0.25)

    def test_statistical_audit_keeps_persistent_dead_end_uncertified(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            analysis = root / "analysis.json"
            panel = root / "panel.json"
            analysis.write_text(
                json.dumps(
                    {
                        "experiment_id": "x",
                        "outcome": "STOP_FIXED_POLICY_DYNAMIC_BRIDGE",
                        "qualified": True,
                        "qualified_units": 24,
                        "metrics": {
                            "paired_disagreement": {
                                "B_vs_A": 0.0,
                                "C_vs_A": 0.0,
                                "D_vs_A": 0.0,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            panel.write_text(
                json.dumps({"local_causal_tasks": [{"id": i} for i in range(12)]}),
                encoding="utf-8",
            )
            out = stat_audit.run(analysis, panel)
            self.assertTrue(out["experimental_stop_rule_valid"])
            self.assertFalse(out["persistent_principle_dead_end_statistically_certified"])
            self.assertEqual(
                out["recommended_principle_layer_disposition"],
                "REGISTERED_REALIZATION_STOP_PRINCIPLE_NOT_PERSISTENT_DEAD_END",
            )

    def test_same_information_comparison_does_not_reward_weaker_B(self) -> None:
        out = screen.compare(
            [0.0, 0.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
        )
        self.assertEqual(out["B_gt_C"], 0)
        self.assertEqual(out["C_gt_B"], 2)
        self.assertFalse(out["B_dominance_supported_at_0_05"])

    def test_portable_principle_disposition_stays_unresolved(self) -> None:
        generated = PROJECT_ROOT / "generated"
        result = disposition.run(
            PROJECT_ROOT,
            generated / "asset-first-stri-skillrl-final-policy-p0e-qualified-stop-diagnosis-20260817.json",
            generated / "asset-first-stri-skillrl-final-policy-p0e-same-information-screen-20260817.json",
            generated / "asset-first-stri-skillrl-final-policy-p0e-statistical-resolution-audit-20260817.json",
            generated / "asset-first-stri-skillrl-final-policy-p0e-postnegative-review-panel-20260817.json",
        )
        self.assertTrue(result["experimental_stop_valid"])
        self.assertFalse(result["persistent_principle_dead_end_certified"])
        self.assertEqual(result["principle_disposition"], "METHOD_NEGATIVE_PRINCIPLE_UNRESOLVED")
        self.assertEqual(
            result["failure_asset_library_snapshot"]["summary"]["principle_dead_ends"],
            0,
        )
        self.assertFalse(result["new_gpu_authorized"])
        self.assertTrue(result["stage2_confirmation_locked"])


if __name__ == "__main__":
    unittest.main()
