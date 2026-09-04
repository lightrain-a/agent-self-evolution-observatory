from __future__ import annotations

import copy
import json
import math
import unittest

from research_pipeline.agent_constraint_externality_confirmatory_preexec import (
    ARMS,
    BRANCHES,
    DEV_FAMILY_COUNT,
    N_CANDIDATES,
    PreexecError,
    build_freeze_artifact,
    decide_N_star,
    decide_repeat_count_after_three,
    decide_repeat_count_after_two,
    decide_target_only_eligibility,
    select_confirmatory_panel,
    sha256_value,
    stable_family_order,
)


def dev_rows(repeats=(1, 2), target_flip_cells=0, crr_shift_cells=0, invalid=False):
    rows = []
    cell = 0
    for fi in range(DEV_FAMILY_COUNT):
        family = f"DEV-{fi+1:02d}"
        for ai, arm in enumerate(ARMS):
            for bi, branch in enumerate(BRANCHES):
                cell += 1
                base_target = ((fi + ai + bi) % 3) != 0
                # Vary family/arm/branch effects without using a common mean-only pattern.
                base_crr = min(1.0, max(0.0, 0.05 * fi + 0.05 * ai + (0.10 if branch == "REAL_REPAIR" else 0.0)))
                for repeat in repeats:
                    target = base_target
                    crr = base_crr
                    if repeat == 2 and cell <= target_flip_cells:
                        target = not target
                    if repeat == 2 and cell <= crr_shift_cells:
                        crr = min(1.0, base_crr + 0.5)
                    if repeat == 3:
                        # Third repeat returns to the base condition by default.
                        target = base_target
                        crr = base_crr
                    rows.append({
                        "family_id": family,
                        "arm": arm,
                        "branch": branch,
                        "repeat": repeat,
                        "target_success": bool(target),
                        "crr": float(crr),
                        "valid": not invalid,
                    })
    return rows


class ConfirmatoryPreexecTest(unittest.TestCase):
    def test_repeat_r2_passes_when_disagreement_is_small(self):
        out = decide_repeat_count_after_two(dev_rows(target_flip_cells=3, crr_shift_cells=3))
        self.assertEqual(out["status"], "REPEAT_QUALIFICATION_PASS_R2")
        self.assertEqual(out["R_star"], 2)
        self.assertLessEqual(out["target_disagreement_rate"], 0.10)
        self.assertLessEqual(out["mean_absolute_crr_repeat_difference"], 0.10)

    def test_repeat_r3_trigger_is_direction_blind(self):
        out = decide_repeat_count_after_two(dev_rows(target_flip_cells=5, crr_shift_cells=5))
        self.assertEqual(out["status"], "REPEAT_QUALIFICATION_REQUIRE_R3")
        self.assertTrue(out["third_development_repeat_required"])
        self.assertNotIn("effect", " ".join(out.keys()).lower())

    def test_repeat_stops_above_hard_instability_ceiling(self):
        out = decide_repeat_count_after_two(dev_rows(target_flip_cells=9, crr_shift_cells=18))
        self.assertEqual(out["status"], "REPEAT_QUALIFICATION_STOP_STOCHASTICITY_TOO_HIGH")
        self.assertIsNone(out["R_star"])

    def test_r3_pass_requires_three_repeat_stability(self):
        out = decide_repeat_count_after_three(dev_rows(repeats=(1, 2, 3), target_flip_cells=5, crr_shift_cells=5))
        self.assertEqual(out["status"], "REPEAT_QUALIFICATION_PASS_R3")
        self.assertEqual(out["R_star"], 3)

    def test_technical_invalidity_never_selects_more_repeats(self):
        out = decide_repeat_count_after_two(dev_rows(invalid=True))
        self.assertEqual(out["status"], "REPEAT_QUALIFICATION_INVALID_TECHNICAL_UNIT")
        self.assertIsNone(out["R_star"])

    def test_target_only_eligibility_requires_half_point_uptake_and_same_snapshot(self):
        rows = [
            {"branch": "NO_UPDATE", "repeat": 1, "target_success": False, "valid": True, "snapshot_sha256": "s", "repair_sha256": ""},
            {"branch": "NO_UPDATE", "repeat": 2, "target_success": False, "valid": True, "snapshot_sha256": "s", "repair_sha256": ""},
            {"branch": "REAL_REPAIR", "repeat": 1, "target_success": True, "valid": True, "snapshot_sha256": "s", "repair_sha256": "r"},
            {"branch": "REAL_REPAIR", "repeat": 2, "target_success": False, "valid": True, "snapshot_sha256": "s", "repair_sha256": "r"},
        ]
        out = decide_target_only_eligibility(source_failure_valid=True, repair_artifact_valid=True, interface_valid=True, rows=rows, R_star=2)
        self.assertTrue(out["eligible"])
        self.assertEqual(out["target_uptake_delta"], 0.5)
        self.assertFalse(out["post_topology_target_outcomes_may_change_eligibility"])
        drifted = copy.deepcopy(rows)
        drifted[-1]["snapshot_sha256"] = "other"
        out2 = decide_target_only_eligibility(source_failure_valid=True, repair_artifact_valid=True, interface_valid=True, rows=drifted, R_star=2)
        self.assertFalse(out2["eligible"])

    def test_target_only_eligibility_rejects_subthreshold_uptake(self):
        rows = [
            {"branch": branch, "repeat": repeat, "target_success": (branch == "REAL_REPAIR" and repeat == 1) or (branch == "NO_UPDATE" and repeat == 1), "valid": True, "snapshot_sha256": "s", "repair_sha256": "r" if branch == "REAL_REPAIR" else ""}
            for branch in BRANCHES for repeat in (1, 2)
        ]
        out = decide_target_only_eligibility(source_failure_valid=True, repair_artifact_valid=True, interface_valid=True, rows=rows, R_star=2)
        self.assertFalse(out["eligible"])
        self.assertEqual(out["target_uptake_delta"], 0.0)

    def test_precision_selection_emits_dispersion_not_development_direction(self):
        rows = dev_rows(target_flip_cells=0, crr_shift_cells=0)
        out = decide_N_star(rows, R_star=2)
        self.assertEqual(out["status"], "PRECISION_QUALIFICATION_PASS")
        self.assertIn(out["N_star"], N_CANDIDATES)
        self.assertFalse(out["development_effect_mean_emitted"])
        self.assertFalse(out["development_effect_sign_emitted"])
        self.assertFalse(out["selection_uses_effect_direction"])
        serialized = json.dumps(out).lower()
        self.assertNotIn('"mean_rq', serialized)
        self.assertNotIn('"sign_rq', serialized)

    def test_precision_selection_is_invariant_to_global_effect_sign_flip(self):
        rows = dev_rows()
        out1 = decide_N_star(rows, R_star=2)
        flipped = copy.deepcopy(rows)
        # Swap branch labels within every condition: RQ1/RQ2 effect signs reverse, dispersion does not.
        for row in flipped:
            row["branch"] = "REAL_REPAIR" if row["branch"] == "NO_UPDATE" else "NO_UPDATE"
        out2 = decide_N_star(flipped, R_star=2)
        self.assertEqual(out1["N_star"], out2["N_star"])
        self.assertAlmostEqual(out1["conservative_loo_sd_rq1"], out2["conservative_loo_sd_rq1"])
        self.assertAlmostEqual(out1["conservative_loo_sd_rq2"], out2["conservative_loo_sd_rq2"])

    def test_panel_selection_uses_frozen_hash_order_and_never_backfills_post_topology(self):
        ids = [f"CONF-{i:02d}" for i in range(24)]
        order = stable_family_order(ids)
        eligibility = {fid: True for fid in ids}
        eligibility[order[0]] = False
        out = select_confirmatory_panel(eligibility, 16)
        self.assertEqual(out["status"], "CONFIRMATORY_PANEL_FROZEN")
        expected = [fid for fid in order if eligibility[fid]][:16]
        self.assertEqual(out["selected_family_ids"], expected)
        self.assertFalse(out["post_topology_backfill_allowed"])
        self.assertEqual(out["selected_family_ids_sha256"], sha256_value(expected))

    def test_panel_support_fails_instead_of_shrinking_n(self):
        ids = [f"CONF-{i:02d}" for i in range(24)]
        eligibility = {fid: (i < 15) for i, fid in enumerate(ids)}
        out = select_confirmatory_panel(eligibility, 16)
        self.assertEqual(out["status"], "CONFIRMATORY_SUPPORT_STOP_INSUFFICIENT_PRE_TOPOLOGY_ELIGIBLE_FAMILIES")
        self.assertEqual(out["eligible_count"], 15)

    def test_freeze_artifact_has_zero_authority_and_exact_rules(self):
        out = build_freeze_artifact()
        self.assertEqual(out["status"], "ZERO_PROVIDER_PREEXEC_FREEZE_COMPLETE_EXECUTION_AUTHORITY_CLOSED")
        self.assertEqual(out["target_only_verification"]["eligibility_uptake_delta_min"], 0.50)
        self.assertIn("0.10", out["repeat_qualification"]["R2_rule"])
        self.assertIn("0.20", out["repeat_qualification"]["hard_stop"])
        self.assertEqual(out["precision_freeze"]["planning_se_max"], 0.10)
        self.assertTrue(all(value is False for value in out["authority"].values()))
        self.assertEqual(out["scientific_provider_calls_created"], 0)
        self.assertEqual(out["scientific_outcomes_created"], 0)


if __name__ == "__main__":
    unittest.main()
