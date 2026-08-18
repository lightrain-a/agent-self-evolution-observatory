from __future__ import annotations

import unittest
from pathlib import Path

from research_pipeline.config import PROJECT_ROOT
from research_pipeline.pace_bench_transport_f0 import _source_revision_support, analyze_transport, summarize_source_experiment


def result(task: str, strategy: str, stage: int, score: float, *, provider: str = "openai-compatible") -> dict:
    return {
        "task_id": task,
        "task_path": f"Category/{task}",
        "target_environment": f"Stage-{stage}",
        "strategy": strategy,
        "provider": provider,
        "model": "qwen-test" if provider != "mock" else "mock",
        "mode": "adaptation",
        "attempt_budget": 6,
        "best_score": score,
        "success": score >= 99.0,
        "error_type": "stagnation",
        "analysis": {"error_type": "stagnation"},
        "token_usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
        "attempts": [
            {"attempt": 0, "phase": "reference", "score": 0.0, "code": "source"},
            {"attempt": 1, "phase": "revision", "score": score / 3, "code": f"{strategy}-{task}-a", "generation": {"model": "resolved-test", "token_usage": {"total_tokens": 60}}},
            {"attempt": 2, "phase": "revision", "score": score / 2, "code": f"{strategy}-{task}-b", "generation": {"model": "resolved-test", "token_usage": {"total_tokens": 60}}},
        ],
    }


class PaceBenchTransportF0Test(unittest.TestCase):
    def test_mock_is_plumbing_only(self) -> None:
        rows = [result("S_01", "tree_of_thoughts", 1, 10.0, provider="mock")]
        out = analyze_transport(rows)
        self.assertEqual("HOLD_ONLY_SYNTHETIC_OR_MOCK_TRAJECTORIES", out["decision"])
        self.assertFalse(out["scientific_result_available"])

    def test_go_requires_bidirectional_cross_stage_reversal(self) -> None:
        rows = []
        # Four of six tasks reverse; two reverse A->B and two B->A.
        patterns = [
            (80, 20, 20, 80),
            (70, 30, 30, 70),
            (20, 80, 80, 20),
            (30, 70, 70, 30),
            (80, 20, 70, 30),
            (20, 80, 30, 70),
        ]
        for i, (a1, b1, a4, b4) in enumerate(patterns, 1):
            task = f"T_{i:02d}"
            rows += [
                result(task, "A", 1, a1), result(task, "B", 1, b1),
                result(task, "A", 4, a4), result(task, "B", 4, b4),
            ]
        out = analyze_transport(rows)
        self.assertEqual("GO_SEARCH_CONTROL_TRANSPORT_FAILURE_PHENOMENON", out["decision"])
        best = out["best_supported_strategy_pair"]
        self.assertEqual(6, best["strict_non_tied_tasks"])
        self.assertEqual(4, best["strict_reversals"])
        self.assertTrue(best["bidirectional_reversal"])

    def test_unidirectional_stage_effect_reduces_to_global_control(self) -> None:
        rows = []
        # Every task flips A->B. This is a global stage effect, not task-specific transport heterogeneity.
        for i in range(1, 7):
            task = f"T_{i:02d}"
            rows += [
                result(task, "A", 1, 80), result(task, "B", 1, 20),
                result(task, "A", 4, 20), result(task, "B", 4, 80),
            ]
        out = analyze_transport(rows)
        self.assertEqual("STOP_OR_REDUCE_TO_STAGE_CONDITIONED_GLOBAL_SEARCH_CONTROL", out["decision"])
        self.assertFalse(out["best_supported_strategy_pair"]["bidirectional_reversal"])

    def test_real_coverage_below_six_holds(self) -> None:
        rows = []
        for i in range(1, 4):
            task = f"T_{i:02d}"
            rows += [
                result(task, "A", 1, 80), result(task, "B", 1, 20),
                result(task, "A", 4, 20), result(task, "B", 4, 80),
            ]
        out = analyze_transport(rows)
        self.assertEqual("HOLD_INSUFFICIENT_REAL_MULTISTRATEGY_STAGE_COVERAGE", out["decision"])
        self.assertFalse(out["scientific_result_available"])

    def test_source_experiment_cost_never_pretends_real_provider_run_was_zero_call(self) -> None:
        rows = [result("S_01", "A", 1, 30), result("S_01", "A", 4, 40)]
        cost = summarize_source_experiment(rows)
        self.assertEqual(cost["real_provider_result_records"], 2)
        self.assertEqual(cost["attempt_generation_records"], 4)
        self.assertEqual(cost["provider_call_count_provable_lower_bound"], 4)
        self.assertIsNone(cost["provider_call_count_exact"])
        self.assertFalse(cost["exact_provider_response_receipts_complete"])
        self.assertEqual(cost["aggregate_token_usage"]["total_tokens"], 240)
        self.assertEqual(cost["resolved_models_in_attempt_records"], {"resolved-test": 4})

    def test_source_revision_support_is_diagnostic_only(self) -> None:
        positive = result("S_01", "codeevolve", 1, 90)
        negative = result("K_01", "codeevolve", 1, -30)
        support = _source_revision_support([positive, negative])
        self.assertEqual(support["eligible_source_stage_units"], 2)
        self.assertEqual(support["positive_source_revision_units"], 1)
        self.assertFalse(support["scientific_authority"])

    def test_generated_receipt_is_public_safe(self) -> None:
        path = PROJECT_ROOT / "generated" / "pace-bench-search-control-transport-f0-20260818.json"
        text = path.read_text(encoding="utf-8")
        for prefix in ("/home/", "/tmp/", "/data/"):
            self.assertNotIn(prefix, text)


if __name__ == "__main__":
    unittest.main()
