from __future__ import annotations

import inspect
import unittest

from .ark_provider import ARK_MODELS
from . import problem_search_stage_runner as stage_runner
from .premium_model_policy import (
    MAX_PROVIDER_CONCURRENCY,
    PREMIUM_AUTO,
    PREMIUM_MODELS,
    independent_priority,
    policy_summary,
    preferred_model,
    stage_model_priority,
)


class PremiumModelPolicyTests(unittest.TestCase):
    def test_requested_premium_models_are_supported(self) -> None:
        for model in PREMIUM_MODELS:
            self.assertIn(model, ARK_MODELS)

    def test_high_value_stage_defaults_use_premium_models(self) -> None:
        expected = {
            "problem_generation": "glm-5.3",
            "portfolio_expand": "kimi-k3",
            "portfolio_evolve": "glm-5.3",
            "portfolio_formulate": "glm-5.3",
            "semantic_review": "deepseek-v4-pro",
            "evidence_design": "glm-5.3",
            "evidence_recompile": "kimi-k3",
            "evidence_review": "deepseek-v4-pro",
            "relation_mining": "kimi-k3",
            "relation_lane_review": "glm-5.3",
            "relation_reduction_review": "deepseek-v4-pro",
        }
        for stage, model in expected.items():
            self.assertEqual(preferred_model(stage, PREMIUM_AUTO), model)
            self.assertIn(model, PREMIUM_MODELS)

    def test_explicit_model_override_is_preserved(self) -> None:
        self.assertEqual(preferred_model("evidence_design", "minimax-m3"), "minimax-m3")
        self.assertEqual(preferred_model("semantic_review", "ark-code-latest"), "ark-code-latest")

    def test_designer_and_reviewer_start_from_distinct_families(self) -> None:
        self.assertNotEqual(
            stage_model_priority("evidence_design")[0],
            stage_model_priority("evidence_review")[0],
        )
        self.assertNotEqual(
            stage_model_priority("portfolio_formulate")[0],
            stage_model_priority("semantic_review")[0],
        )
        self.assertNotIn("deepseek-v4-pro", independent_priority("evidence_review", exclude_resolved="deepseek-v4-pro"))

    def test_provider_concurrency_cap_remains_two(self) -> None:
        self.assertEqual(MAX_PROVIDER_CONCURRENCY, 2)
        summary = policy_summary()
        self.assertEqual(summary["max_provider_concurrency"], 2)
        self.assertFalse(summary["scientific_authority"])

    def test_active_stage_runner_defaults_to_premium_auto(self) -> None:
        for fn in (
            stage_runner.expand,
            stage_runner.evolve,
            stage_runner.formulate,
            stage_runner.evidence_design,
            stage_runner.evidence_operationalization_recompile,
            stage_runner.evidence_contract_review,
            stage_runner.review,
        ):
            self.assertEqual(inspect.signature(fn).parameters["model"].default, PREMIUM_AUTO)


if __name__ == "__main__":
    unittest.main()
