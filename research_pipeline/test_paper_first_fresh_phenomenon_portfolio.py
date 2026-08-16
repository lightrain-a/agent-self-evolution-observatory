from __future__ import annotations

import unittest

from research_pipeline.paper_first_fresh_phenomenon_portfolio import (
    ACTIVE_F0_LIMIT,
    build_fresh_phenomenon_portfolio,
    validate_fresh_phenomenon_portfolio,
)


class FreshPhenomenonPortfolioTest(unittest.TestCase):
    def execution_capability(self) -> dict:
        return {
            "controller_verified": True,
            "valid": True,
            "idea_id": "PA-01-EVIDENCE-ECHO",
            "plan_hash": "f7c1b8cce177a0efff84cfcf404ef436cf89ead1648548bcd6d633aa3c80a621",
            "authority_id": "authority-demo",
            "run_id": "run-demo",
            "server_id": "52",
            "gpu_lease_ids": ["lease-demo"],
        }

    def echo_receipt(self) -> dict:
        return {
            "decision": "KEEP_AS_ACTIVE_F0_NOT_PAPER_IDEA",
            "title": "Evidence Echo",
            "source_primary_ref": "arXiv:2608.07527",
            "source_substrate": {
                "host": "52",
                "run": "demo",
                "aggregate_jsonl_sha256": "a" * 64,
                "raw_visible_pages_locked_across_policies": True,
                "second_retrieval_ranking_locked_across_active_policies": True,
            },
            "scope": {"units": 128},
            "observed_signal": {
                "negative_evidence_baseline_unanswerable_false_answer_rate": 0.109375,
                "naive_summary_unanswerable_false_answer_rate": 0.21875,
                "naive_summary_induced_false_answers": 7,
                "naive_summary_fixed_false_answers": 0,
                "naive_summary_exact_paired_p": 0.015625,
                "naive_summary_answerable_exact_net_delta": 0.0,
            },
            "next_f0": {
                "required_arms": [
                    "RAW_ONLY",
                    "ECHO_EXTRACTIVE",
                    "VERBATIM_DUPLICATE",
                    "TOKEN_MATCHED_NEUTRAL",
                    "DEDUP_WARNING",
                ],
                "gpu_authorized": False,
            },
        }

    def memory(self) -> dict:
        return {
            "shadow_dead_end_memory": {
                "hold_objects": [
                    {
                        "source_candidate_id": "SHADOW-P07-C01",
                        "support_status": "SUPPORT_UNAVAILABLE_FOR_FROZEN_PROBLEM_FALSIFIER",
                        "reopen_only_if": "release harness histories",
                    },
                    {
                        "source_candidate_id": "SHADOW-P11-C02",
                        "support_status": "SUPPORT_UNAVAILABLE_FOR_FROZEN_PROBLEM_FALSIFIER",
                        "reopen_only_if": "release defense histories",
                    },
                    {
                        "source_candidate_id": "X",
                        "title": "Procedural-composition transfer-calibration boundary for high-TRS spatial lessons",
                        "support_status": "SUPPORT_UNAVAILABLE_FOR_FROZEN_PROBLEM_FALSIFIER",
                        "reopen_only_if": "release spatial retrieval logs",
                    },
                ]
            }
        }

    def defense_closure(self) -> dict:
        return {
            "principle_dead_end_certified": True,
            "experiment_run_for_this_readjudication": False,
            "fresh_phenomenon_closure": {
                "source_ref": "arXiv:2608.12977",
                "closure_scope": "backbone-dependent ASR/BU/UA overrestriction operating-point phenomenon only",
            },
            "principle_diagnosis": {
                "counter_explanation": {
                    "same_information_or_scope_matched": True,
                    "same_information_reduction_verified": True,
                    "positive_support": True,
                    "reopen_condition": "reopen only for a matched structural residual beyond the frontier",
                }
            },
            "authority": {"experiment_alone_authorizes_dead_end": False},
        }

    def spatial_closure(self) -> dict:
        return {
            "principle_dead_end_certified": True,
            "experiment_run_for_this_readjudication": False,
            "fresh_phenomenon_closure": {
                "source_ref": "arXiv:2608.12743",
                "closure_scope": "high-TRS qualitative failure cases attributed to visual grounding",
            },
            "principle_diagnosis": {
                "counter_explanation": {
                    "same_information_or_scope_matched": True,
                    "same_information_reduction_verified": True,
                    "positive_support": True,
                    "reopen_condition": "reopen only for matched compatibility residual after grounding control",
                }
            },
            "authority": {"experiment_alone_authorizes_dead_end": False},
        }

    def echo_f0_stop_result(self) -> dict:
        return {
            "candidate_id": "PA-01-EVIDENCE-ECHO",
            "execution_status": "AUTHORIZED_BOUNDED_F0_EXECUTION_COMPLETED",
            "scientific_status": "STOP_GENERIC_PROMPT_REDUCTION_NOT_BEATEN",
            "frozen_contract": {
                "runtime_sha256": "f64ae7c42f5e02b2f18abd67e4a784e3790b3c75107a4140666d9faa1c39842e",
                "operationalization_repair_sha256": "8965c54594356a87e642ebe3cc4cd76eb899ece5e6436eb96f097d09473aad30",
                "analysis_sha256": "a" * 64,
                "rows_sha256": "b" * 64,
            },
            "execution_integrity": {
                "rc": 0,
                "units": 96,
                "rows": 480,
                "unanswerable_units": 64,
                "answerable_units": 32,
                "unauthorized_prior_rows_reused": False,
                "permit_status": "consumed-completed",
                "experiment_authority_released": True,
                "gpu_lease_released": True,
            },
            "false_answer_rate": {
                "RAW_ONLY": 0.140625,
                "ECHO_EXTRACTIVE": 0.171875,
                "VERBATIM_DUPLICATE": 0.234375,
                "TOKEN_MATCHED_NEUTRAL": 0.140625,
                "DEDUP_WARNING": 0.28125,
            },
            "effects": {
                "echo_minus_raw_false": 0.03125,
                "verbatim_minus_raw_false": 0.09375,
            },
            "paired_tests": {"raw_to_echo": {"exact_two_sided_p": 0.6875}},
            "preregistered_gate_diagnosis": {
                "strongest_generic_reduction_beaten": False,
                "echo_specific_effect_threshold_met": False,
            },
            "scientific_authority": False,
        }

    def build(self, **overrides) -> dict:
        kwargs = {
            "evidence_echo": self.echo_receipt(),
            "evidence_echo_f0_result": {},
            "primary_state": {"summary": {"verified": 32, "empirical_fact_candidates": 107}},
            "dead_end_memory": self.memory(),
            "defense_readjudication": self.defense_closure(),
            "spatial_readjudication": self.spatial_closure(),
        }
        kwargs.update(overrides)
        return build_fresh_phenomenon_portfolio(**kwargs)

    def test_design_ready_candidate_holds_without_execution_capability(self) -> None:
        state = self.build()
        self.assertEqual([], validate_fresh_phenomenon_portfolio(state))
        self.assertEqual("F0_EXECUTION_HOLD", state["status"])
        self.assertEqual(0, state["summary"]["active_f0"])
        self.assertEqual(1, state["summary"]["design_ready_f0"])
        self.assertEqual(1, state["summary"]["hold_execution"])
        self.assertEqual(1, state["summary"]["hold_support"])
        self.assertEqual(2, state["summary"]["stop_reduction"])
        echo = next(row for row in state["candidates"] if row["candidate_id"] == "PA-01-EVIDENCE-ECHO")
        self.assertEqual("HOLD_EXECUTION", echo["status"])
        self.assertFalse(echo["execution_readiness"]["execution_ready"])
        self.assertFalse(echo["execution_readiness"]["unauthorized_partial_run_ingestable"])

        defense = next(row for row in state["candidates"] if row["candidate_id"] == "PA-02-DEFENSE-RESTRICTIVENESS")
        self.assertEqual("STOP_REDUCTION", defense["status"])
        self.assertEqual("PRINCIPLE_CLOSED_SAME_INFORMATION_REDUCTION", defense["support_status"])
        self.assertEqual("reopen only for a matched structural residual beyond the frontier", defense["reopen_only_if"])

        spatial = next(row for row in state["candidates"] if row["candidate_id"] == "PA-04-SPATIAL-MEMORY-CONFLICT")
        self.assertEqual("STOP_REDUCTION", spatial["status"])
        self.assertEqual("PRINCIPLE_CLOSED_VISUAL_GROUNDING_REDUCTION", spatial["support_status"])
        self.assertEqual("reopen only for matched compatibility residual after grounding control", spatial["reopen_only_if"])
        self.assertEqual(0, state["summary"]["canonical_problem_gate_added"])
        self.assertTrue(all(row["scientific_authority"] is False for row in state["candidates"]))

    def test_controller_verified_capability_consumes_single_active_f0_slot(self) -> None:
        state = self.build(execution_capability=self.execution_capability())
        self.assertEqual([], validate_fresh_phenomenon_portfolio(state))
        self.assertEqual(ACTIVE_F0_LIMIT, state["summary"]["active_f0"])
        self.assertEqual(0, state["summary"]["hold_execution"])
        active = [row for row in state["candidates"] if row["status"] == "ACTIVE_F0"]
        self.assertEqual(["PA-01-EVIDENCE-ECHO"], [row["candidate_id"] for row in active])
        self.assertTrue(active[0]["execution_readiness"]["execution_ready"])

    def test_authorized_negative_f0_releases_active_slot_and_stops_scout(self) -> None:
        state = self.build(evidence_echo_f0_result=self.echo_f0_stop_result())
        self.assertEqual([], validate_fresh_phenomenon_portfolio(state))
        self.assertEqual(0, state["summary"]["active_f0"])
        self.assertEqual(3, state["summary"]["stop_reduction"])
        echo = next(row for row in state["candidates"] if row["candidate_id"] == "PA-01-EVIDENCE-ECHO")
        self.assertEqual("STOP_REDUCTION", echo["status"])
        self.assertEqual("F0_REDUCED_BY_GENERIC_PROMPT_EFFECT", echo["support_status"])
        self.assertEqual("STOP_GENERIC_PROMPT_REDUCTION_NOT_BEATEN", echo["evidence"]["f0_scientific_status"])
        self.assertFalse(echo["authority"]["gpu"])

    def test_weak_retrospective_signal_does_not_consume_slot(self) -> None:
        receipt = self.echo_receipt()
        receipt["observed_signal"]["naive_summary_exact_paired_p"] = 0.2
        state = self.build(evidence_echo=receipt)
        self.assertEqual(0, state["summary"]["active_f0"])
        echo = next(row for row in state["candidates"] if row["candidate_id"] == "PA-01-EVIDENCE-ECHO")
        self.assertEqual("HOLD_SUPPORT", echo["status"])
        self.assertEqual("INCOMPLETE_RECEIPT", echo["support_status"])
        self.assertEqual([], validate_fresh_phenomenon_portfolio(state))

    def test_active_f0_has_no_scientific_or_gpu_authority(self) -> None:
        state = self.build(execution_capability=self.execution_capability())
        echo = next(row for row in state["candidates"] if row["candidate_id"] == "PA-01-EVIDENCE-ECHO")
        self.assertFalse(echo["paper_problem_claimed"])
        for key in ("problem_gate", "paper_design", "method", "experiment", "p0", "gpu", "full_experiment"):
            self.assertFalse(echo["authority"][key])
        self.assertTrue(echo["execution_readiness"]["execution_ready"])

    def test_defense_closure_fails_closed_if_same_information_reduction_is_unverified(self) -> None:
        closure = self.defense_closure()
        closure["principle_diagnosis"]["counter_explanation"]["same_information_reduction_verified"] = False
        state = self.build(defense_readjudication=closure)
        defense = next(row for row in state["candidates"] if row["candidate_id"] == "PA-02-DEFENSE-RESTRICTIVENESS")
        self.assertEqual("HOLD_SUPPORT", defense["status"])
        self.assertNotEqual("PRINCIPLE_CLOSED_SAME_INFORMATION_REDUCTION", defense["support_status"])

    def test_spatial_closure_fails_closed_if_primary_explanation_is_not_verified(self) -> None:
        closure = self.spatial_closure()
        closure["principle_diagnosis"]["counter_explanation"]["same_information_reduction_verified"] = False
        state = self.build(spatial_readjudication=closure)
        spatial = next(row for row in state["candidates"] if row["candidate_id"] == "PA-04-SPATIAL-MEMORY-CONFLICT")
        self.assertEqual("HOLD_SUPPORT", spatial["status"])
        self.assertNotEqual("PRINCIPLE_CLOSED_VISUAL_GROUNDING_REDUCTION", spatial["support_status"])


if __name__ == "__main__":
    unittest.main()
