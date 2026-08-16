from __future__ import annotations

import unittest

from research_pipeline.paper_first_fresh_phenomenon_portfolio import (
    ACTIVE_F0_LIMIT,
    build_fresh_phenomenon_portfolio,
    validate_fresh_phenomenon_portfolio,
)


class FreshPhenomenonPortfolioTest(unittest.TestCase):
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
                "required_arms": ["RAW_ONLY", "ECHO_EXTRACTIVE", "VERBATIM_DUPLICATE", "TOKEN_MATCHED_NEUTRAL", "DEDUP_WARNING"],
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

    def test_only_audited_candidate_consumes_active_f0_slot(self) -> None:
        state = build_fresh_phenomenon_portfolio(
            evidence_echo=self.echo_receipt(),
            primary_state={"summary": {"verified": 32, "empirical_fact_candidates": 107}},
            dead_end_memory=self.memory(),
        )
        self.assertEqual([], validate_fresh_phenomenon_portfolio(state))
        self.assertEqual(ACTIVE_F0_LIMIT, state["summary"]["active_f0"])
        active = [row for row in state["candidates"] if row["status"] == "ACTIVE_F0"]
        self.assertEqual(["PA-01-EVIDENCE-ECHO"], [row["candidate_id"] for row in active])
        self.assertEqual(3, state["summary"]["hold_support"])
        self.assertEqual(0, state["summary"]["canonical_problem_gate_added"])
        self.assertTrue(all(row["scientific_authority"] is False for row in state["candidates"]))

    def test_weak_retrospective_signal_does_not_consume_slot(self) -> None:
        receipt = self.echo_receipt()
        receipt["observed_signal"]["naive_summary_exact_paired_p"] = 0.2
        state = build_fresh_phenomenon_portfolio(
            evidence_echo=receipt,
            primary_state={"summary": {}},
            dead_end_memory=self.memory(),
        )
        self.assertEqual(0, state["summary"]["active_f0"])
        echo = next(row for row in state["candidates"] if row["candidate_id"] == "PA-01-EVIDENCE-ECHO")
        self.assertEqual("HOLD_SUPPORT", echo["status"])
        self.assertEqual("INCOMPLETE_RECEIPT", echo["support_status"])
        self.assertEqual([], validate_fresh_phenomenon_portfolio(state))

    def test_active_f0_has_no_scientific_or_gpu_authority(self) -> None:
        state = build_fresh_phenomenon_portfolio(
            evidence_echo=self.echo_receipt(),
            primary_state={"summary": {}},
            dead_end_memory=self.memory(),
        )
        echo = next(row for row in state["candidates"] if row["candidate_id"] == "PA-01-EVIDENCE-ECHO")
        self.assertFalse(echo["paper_problem_claimed"])
        self.assertFalse(echo["authority"]["problem_gate"])
        self.assertFalse(echo["authority"]["paper_design"])
        self.assertFalse(echo["authority"]["experiment"])
        self.assertFalse(echo["authority"]["gpu"])


if __name__ == "__main__":
    unittest.main()
