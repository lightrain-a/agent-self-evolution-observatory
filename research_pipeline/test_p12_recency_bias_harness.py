from __future__ import annotations

import unittest
from collections import Counter

from .p12_recency_bias_harness import (
    ANALYSIS_PROTOCOL,
    CANDIDATE_ID,
    CONTRACT_SHA256,
    HARNESS_PLAN_SHA256,
    FAMILIES,
    LIBRARY_STAGES,
    PHASES,
    PROVIDER_CALL_CAP,
    RECENCY_POLICIES,
    adjudicate_rollouts,
    analysis_split,
    difficulty_calibration_pairs,
    difficulty_summary,
    evaluation_tasks,
    mock_skills,
    offline_probe,
    rank_skills,
    retrieval_pairing_checks,
    rollout_units,
    skill_calibration_bundles,
    validate_frozen_skills,
)


class P12RecencyBiasHarnessTest(unittest.TestCase):
    def test_offline_probe_freezes_exact_104_call_design(self):
        state=offline_probe()
        self.assertEqual(state["status"],"P12_OFFLINE_HARNESS_PROBE_PASS")
        self.assertEqual(state["candidate_id"],CANDIDATE_ID)
        self.assertEqual(state["contract_sha256"],CONTRACT_SHA256)
        self.assertEqual(state["harness_plan_sha256"],HARNESS_PLAN_SHA256)
        self.assertEqual(state["provider_call_upper_bound"],PROVIDER_CALL_CAP)
        self.assertEqual(PROVIDER_CALL_CAP,104)
        self.assertTrue(all(state["checks"].values()))

    def test_evaluation_is_12_matched_scenarios_x_two_phases(self):
        tasks=evaluation_tasks()
        self.assertEqual(len(tasks),24)
        self.assertEqual(Counter(x["phase"] for x in tasks),{"BACKWARD_LOOKING":12,"FORWARD_LOOKING":12})
        by={}
        for row in tasks: by.setdefault(row["scenario_id"],[]).append(row)
        self.assertEqual(len(by),12)
        for rows in by.values():
            self.assertEqual({x["phase"] for x in rows},set(PHASES))
            self.assertEqual(len({x["retrieval_query_sha256"] for x in rows}),1)
            self.assertEqual(len({tuple(sorted(x["difficulty_signature"].items())) for x in rows}),1)

    def test_calibration_sets_are_disjoint_from_evaluation(self):
        eval_ids={x["scenario_id"] for x in evaluation_tasks()}
        difficulty={x["pair_id"] for x in difficulty_calibration_pairs()}
        skill_examples={e["example_id"] for b in skill_calibration_bundles() for e in b["examples"]}
        self.assertFalse(eval_ids & difficulty)
        self.assertFalse(eval_ids & skill_examples)
        self.assertFalse(difficulty & skill_examples)
        self.assertEqual(len(difficulty_calibration_pairs()),4)
        self.assertEqual(len(skill_calibration_bundles()),4)

    def test_mock_library_is_balanced_and_pair_retrieval_is_exact(self):
        skills=mock_skills()
        self.assertEqual(validate_frozen_skills(skills),[])
        self.assertEqual(Counter(x["family"] for x in skills),{family:2 for family in FAMILIES})
        checks=retrieval_pairing_checks(skills)
        self.assertTrue(checks["passed"],checks["errors"])
        units=rollout_units(skills)
        self.assertEqual(len(units),96)
        self.assertEqual(Counter((x["library_stage"],x["recency_policy"]) for x in units),{(stage,policy):24 for stage in LIBRARY_STAGES for policy in RECENCY_POLICIES})

    def test_recency_policy_changes_only_ranking_formula_not_static_similarity(self):
        task=evaluation_tasks()[0];skills=mock_skills()
        for stage in LIBRARY_STAGES:
            u=rank_skills(skills,task,stage,"UNIFORM")
            r=rank_skills(skills,task,stage,"EXPONENTIAL_HALF_LIFE_2_SKILLS")
            static_u={x["skill_id"]:x["static_similarity"] for x in u}
            static_r={x["skill_id"]:x["static_similarity"] for x in r}
            self.assertEqual(static_u,static_r)
            self.assertEqual({x["skill_id"] for x in u},{x["skill_id"] for x in r})

    def _receipts(self, mode: str):
        rows=[]
        for unit in rollout_units(mock_skills()):
            success=True
            if mode=="forward-recency-harm" and unit["phase"]=="FORWARD_LOOKING" and unit["recency_policy"]=="EXPONENTIAL_HALF_LIFE_2_SKILLS":
                success=False
            row=dict(unit);row.update({"status":"UNIT_COMPLETE","valid_execution":True,"task_success":success})
            rows.append(row)
        return rows

    def test_adjudication_reduces_invariant_outcomes_and_survives_clear_interaction(self):
        difficulty={"passed":True,"phase_accuracy":{"BACKWARD_LOOKING":0.75,"FORWARD_LOOKING":0.75},"scientific_authority":False}
        reduced=adjudicate_rollouts(self._receipts("all-success"),difficulty)
        self.assertEqual(reduced["outcome"],"REDUCTION_SUPPORTED")
        residual=adjudicate_rollouts(self._receipts("forward-recency-harm"),difficulty)
        self.assertEqual(residual["outcome"],"RESIDUAL_SURVIVES")
        self.assertGreaterEqual(residual["direct_interaction"]["heldout"],0.25)
        self.assertGreaterEqual(residual["candidate"]["heldout_brier_improvement"],0.02)

    def test_difficulty_gate_requires_below_ceiling_and_phase_match(self):
        pairs=difficulty_calibration_pairs()
        good=[{"pair_id":p["pair_id"],"backward_success":i<3,"forward_success":i<3} for i,p in enumerate(pairs)]
        self.assertTrue(difficulty_summary(good)["passed"])
        ceiling=[{"pair_id":p["pair_id"],"backward_success":True,"forward_success":True} for p in pairs]
        self.assertFalse(difficulty_summary(ceiling)["passed"])
        mismatch=[{"pair_id":p["pair_id"],"backward_success":i<3,"forward_success":i<1} for i,p in enumerate(pairs)]
        self.assertFalse(difficulty_summary(mismatch)["passed"])

    def test_analysis_split_and_thresholds_are_preoutcome_frozen(self):
        split=analysis_split()
        self.assertEqual((len(split["fit"]),len(split["heldout"])),(8,4))
        self.assertFalse(set(split["fit"])&set(split["heldout"]))
        self.assertIn("heldout direct interaction >=0.25",ANALYSIS_PROTOCOL["residual_survives"])
        self.assertIn("<=0.125",ANALYSIS_PROTOCOL["reduction_supported"])


if __name__=="__main__": unittest.main()
