from __future__ import annotations

import unittest

from .paper_first_skill_validation_transfer_f0 import (
    CANDIDATE_ID,
    SOURCE_DEPLOYMENT_ROLES,
    SOURCE_FAMILIES,
    SOURCE_LEARNING_ROLES,
    analyze_rows,
    build_plan,
)


def outcomes(mean: float) -> list[int]:
    if abs(mean - 0.0) < 1e-9:
        return [0, 0, 0]
    if abs(mean - 1 / 3) < 1e-9:
        return [1, 0, 0]
    if abs(mean - 2 / 3) < 1e-9:
        return [1, 1, 0]
    if abs(mean - 1.0) < 1e-9:
        return [1, 1, 1]
    raise ValueError(mean)


def arm_rows(local_means: list[float], deployment_means: list[float]) -> list[dict]:
    rows: list[dict] = []
    for i in range(SOURCE_FAMILIES):
        family = f"F{i:02d}"
        # Primary T1-T3 are required for protocol completeness but are not the
        # local validation statistic; frozen within-env replay is.
        for role, passed in zip(SOURCE_LEARNING_ROLES, [0, 0, 0]):
            rows.append({"family_id": family, "task_role": role, "replay_mode": "primary", "passed": passed})
        for role, passed in zip(SOURCE_DEPLOYMENT_ROLES, outcomes(deployment_means[i])):
            rows.append({"family_id": family, "task_role": role, "replay_mode": "primary", "passed": passed})
        for role, passed in zip(SOURCE_LEARNING_ROLES, outcomes(local_means[i])):
            rows.append({"family_id": family, "task_role": role, "replay_mode": "within_env_replay", "passed": passed})
    return rows


class SkillValidationTransferF0Test(unittest.TestCase):
    def test_plan_is_zero_authority_and_content_addressed(self) -> None:
        plan = build_plan()
        self.assertEqual(CANDIDATE_ID, plan["candidate_id"])
        self.assertEqual(30, plan["unit"]["family_count"])
        self.assertEqual(["raw_trajectory_rag", "selfgen_experience_always"], plan["execution"]["arms"])
        self.assertEqual(270, plan["execution"]["tasks_per_arm"])
        self.assertEqual(64, len(plan["plan_sha256"]))
        self.assertFalse(plan["paper_problem_claimed"])
        self.assertFalse(plan["scientific_authority"])
        self.assertTrue(all(v is False for v in plan["authority"].values()))

    def test_go_requires_non_degenerate_selection_inversion(self) -> None:
        raw_local = [1 / 3] * 15 + [2 / 3] * 15
        skill_local = [2 / 3] * 15 + [1 / 3] * 15

        # 18/30 local decisions invert at deployment; both deployment arms win
        # on 15 families, so this is not a global-arm dominance artifact.
        raw_deploy: list[float] = []
        skill_deploy: list[float] = []
        for i in range(30):
            local_skill = i < 15
            invert = (i < 9) or (15 <= i < 24)
            deploy_skill = (not local_skill) if invert else local_skill
            if deploy_skill:
                raw_deploy.append(1 / 3)
                skill_deploy.append(2 / 3)
            else:
                raw_deploy.append(2 / 3)
                skill_deploy.append(1 / 3)

        out = analyze_rows(
            arm_rows(raw_local, raw_deploy),
            arm_rows(skill_local, skill_deploy),
        )
        self.assertEqual(
            "GO_SELECTION_VALIDITY_PROBLEM_TO_SEED_B_REPLICATION_AND_CURRENT_SOURCE_REVIEW",
            out["status"],
        )
        self.assertEqual(30, out["support"]["joint_decisive_families"])
        self.assertEqual(18, out["support"]["inversions"])
        self.assertAlmostEqual(0.6, out["support"]["inversion_rate"])
        self.assertGreaterEqual(out["deployment"]["oracle_minus_local_selector_regret"], 0.08)
        self.assertGreaterEqual(out["deployment"]["bootstrap_regret_ci95"][0], 0.03)
        self.assertFalse(out["paper_problem_authorized"])
        self.assertFalse(out["experiment_authorized"])

    def test_global_arm_dominance_stops_instead_of_becoming_a_problem(self) -> None:
        raw_local = [1 / 3] * 30
        skill_local = [2 / 3] * 30
        raw_deploy = [1 / 3] * 30
        skill_deploy = [2 / 3] * 30
        out = analyze_rows(
            arm_rows(raw_local, raw_deploy),
            arm_rows(skill_local, skill_deploy),
        )
        self.assertEqual(
            "STOP_LOCAL_VALIDATION_PROBLEM_NOT_IDENTIFIED_OR_GLOBAL_ARM_REDUCTION_SUFFICIENT",
            out["status"],
        )
        self.assertFalse(out["gates"]["local_raw_wins"])
        self.assertFalse(out["gates"]["deployment_raw_wins"])
        self.assertEqual(0, out["support"]["inversions"])

    def test_protocol_mismatch_is_inconclusive(self) -> None:
        raw_local = [1 / 3] * 30
        skill_local = [2 / 3] * 30
        raw_deploy = [1 / 3] * 30
        skill_deploy = [2 / 3] * 30
        raw = arm_rows(raw_local, raw_deploy)
        raw = [row for row in raw if row["family_id"] != "F29"]
        out = analyze_rows(raw, arm_rows(skill_local, skill_deploy))
        self.assertEqual("INCONCLUSIVE_SUPPORT_OR_PROTOCOL_MISMATCH", out["status"])
        self.assertTrue(out["errors"])
        self.assertFalse(out["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
