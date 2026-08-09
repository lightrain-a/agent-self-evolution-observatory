from __future__ import annotations

import unittest

from .iclr_idea_factory import build_iclr_idea_bank, validate_bank


class IclrIdeaBankTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_iclr_idea_bank()
        cls.ideas = cls.payload["passed_ideas"]

    def test_target_and_size(self) -> None:
        self.assertEqual(self.payload["target_venue"], "ICLR")
        self.assertGreaterEqual(len(self.ideas), 24)
        self.assertEqual(validate_bank(self.payload), [])
        self.assertEqual(self.payload["summary"]["tracks"], 8)

    def test_seven_review_gates(self) -> None:
        for idea in self.ideas:
            with self.subTest(idea=idea["id"]):
                self.assertEqual(len(idea["reviews"]), 7)
                self.assertTrue(all(review["verdict"] == "pass" for review in idea["reviews"]))
                self.assertTrue(all(review["score"] >= 4 for review in idea["reviews"]))

    def test_generality_and_resource_policy(self) -> None:
        for idea in self.ideas:
            with self.subTest(idea=idea["id"]):
                self.assertGreaterEqual(len(idea["domains"]), 2)
                self.assertLessEqual(idea["budget"]["max_gpus"], 2)
                self.assertLessEqual(idea["budget"]["gpu_hours"], 48)
                self.assertTrue(idea["experiment_protocol"])
                self.assertTrue(idea["models"])
                self.assertTrue(idea["datasets"])

    def test_human_intuition_method_substance_and_original_task_gates(self) -> None:
        for idea in self.ideas:
            with self.subTest(idea=idea["id"]):
                self.assertTrue(idea["core_intuition"]["zh"])
                self.assertTrue(idea["concrete_example"]["zh"])
                substance = idea["method_substance"]
                self.assertEqual(
                    set(substance),
                    {"persistent_update_object", "learning_signal", "independent_truth", "matched_simplification", "decisive_falsifier"},
                )
                self.assertTrue(all(substance[key]["zh"] and substance[key]["en"] for key in substance))
                original = idea["original_task_evaluation"]
                self.assertIn("paired", original["paired_measurement"]["en"].lower())
                self.assertIn("worst", original["primary_endpoints"]["en"].lower())
                self.assertIn(idea["parent_merge_gate"]["status"], {"not-applicable", "merge-if-tied", "merged"})

    def test_method_redesign_round_20260810_is_specific_and_sourced(self) -> None:
        by_id = {idea["id"]: idea for idea in self.ideas}
        b4 = by_id["causally-verified-experience-admission"]
        self.assertEqual(b4["parent_merge_gate"]["parent_id"], "regression-gated-self-evolution")
        self.assertEqual(b4["parent_merge_gate"]["status"], "merge-if-tied")
        self.assertIn("K=6", b4["method_logic"]["zh"])
        self.assertIn("same k=6", b4["strongest_baseline"]["en"].lower())

        b6 = by_id["memory-half-life"]
        self.assertIn("reuse", b6["core_intuition"]["en"].lower())
        self.assertIn("memory off/on", b6["method_logic"]["en"].lower())
        self.assertIn("recency+frequency", b6["strongest_baseline"]["en"].lower())

        c1 = by_id["self-label-confidence-flow"]
        self.assertIn("label-event dag", c1["method_logic"]["en"].lower())
        self.assertIn("independent-anchor", c1["strongest_baseline"]["en"].lower())
        self.assertIn("effective evidence", c1["method_logic"]["en"].lower())

        d1 = by_id["counterexample-generating-curriculum"]
        self.assertIn("1-minimal", d1["method_logic"]["en"].lower())
        self.assertIn("without minimization", d1["strongest_baseline"]["en"].lower())
        self.assertIn("1-minimal", d1["method_substance"]["learning_signal"]["en"].lower())

        f3 = by_id["recovery-conditioned-experience"]
        self.assertIn("p0a", f3["method_logic"]["en"].lower())
        self.assertIn("typed δs", f3["method_logic"]["en"].lower())
        self.assertIn("exact program state", f3["method_substance"]["independent_truth"]["en"].lower())

        redesigned_ids = (
            "regression-gated-self-evolution",
            "compositional-update-compatibility",
            "lineage-aware-rollback",
            "outcome-equivalent-trajectory-contrast",
            "contradiction-preserving-consolidation",
            "retrieval-interference-auditor",
            "causally-verified-experience-admission",
            "local-counterexample-memory-repair",
            "memory-half-life",
            "self-label-confidence-flow",
            "evaluator-coadaptation-guard",
            "counterexample-generating-curriculum",
            "workflow-generalization-certificate",
            "workflow-branch-credit",
            "world-model-error-gated-learning",
            "irreversible-action-counterfactuals",
            "recovery-conditioned-experience",
        )
        self.assertEqual(len(redesigned_ids), 17)
        for idea_id in redesigned_ids:
            with self.subTest(redesign=idea_id):
                idea = by_id[idea_id]
                iteration = idea.get("redesign_iteration") or {}
                self.assertEqual(iteration.get("round"), "2026-08-10")
                self.assertTrue(iteration.get("verdict"))
                self.assertTrue((iteration.get("summary") or {}).get("zh"))
                fresh = idea.get("fresh_reducibility_check") or {}
                self.assertEqual(fresh.get("review_date"), "2026-08-10")
                self.assertGreaterEqual(len(fresh.get("sources") or []), 2)
                self.assertTrue(all(str(source.get("url", "")).startswith("https://") for source in fresh["sources"]))
                self.assertGreaterEqual(len(idea["method_logic"]["zh"]), 40)
                self.assertGreaterEqual(len(idea["strongest_baseline"]["zh"]), 20)
                self.assertGreaterEqual(len(idea["stop_condition"]["zh"]), 20)

        self.assertEqual(by_id["outcome-equivalent-trajectory-contrast"]["title"]["zh"], "跨过程验证经验蒸馏")
        self.assertEqual(by_id["workflow-generalization-certificate"]["title"]["zh"], "成对编辑效应工作流更新策略")
        self.assertEqual(by_id["world-model-error-gated-learning"]["title"]["zh"], "决策翻转驱动的转移准入")
        self.assertEqual(by_id["causally-verified-experience-admission"]["parent_merge_gate"]["parent_id"], "regression-gated-self-evolution")
        self.assertEqual(by_id["workflow-branch-credit"]["parent_merge_gate"]["parent_id"], "workflow-generalization-certificate")

    def test_primary_open_weight_and_api_policy(self) -> None:
        policy = self.payload["policy"]
        self.assertTrue(policy["primary_open_weight_required"])
        self.assertTrue(policy["commercial_api_optional_only"])
        for key in ("core_intuition_required", "concrete_example_required", "method_substance_required", "original_task_evaluation_required", "parent_merge_gate_required"):
            self.assertTrue(policy[key], key)
        for idea in self.ideas:
            role = idea["experiment_protocol"]["commercial_api_role"]
            self.assertIn("optional", role["en"].lower())
            self.assertIn("核心", role["zh"])

    def test_ranking_and_web_review(self) -> None:
        self.assertEqual([idea["rank"] for idea in self.ideas], list(range(1, len(self.ideas) + 1)))
        self.assertEqual(sorted(idea["programmatic_rank"] for idea in self.ideas), list(range(1, len(self.ideas) + 1)))
        verdict_order = {"pass": 0, "revise": 1, "pending": 2, "block": 3}
        verdicts = [verdict_order[idea["external_verdict"]] for idea in self.ideas]
        self.assertTrue(all(left <= right for left, right in zip(verdicts, verdicts[1:])))
        for verdict in verdict_order:
            priorities = [idea["priority"] for idea in self.ideas if idea["external_verdict"] == verdict]
            self.assertTrue(all(left >= right for left, right in zip(priorities, priorities[1:])))
        reviewed = [idea for idea in self.ideas if idea["external_reviews"]]
        self.assertTrue(any(idea["id"] == "regression-gated-self-evolution" for idea in reviewed))
        summary = self.payload["summary"]
        self.assertEqual(summary["project_web_gpt_reviewed"], len(reviewed))
        self.assertEqual(summary["project_web_gpt_pending"], len(self.ideas) - len(reviewed))
        self.assertEqual(summary["project_web_gpt_complete"], len(reviewed) == len(self.ideas))
        counts = summary["external_verdict_counts"]
        for verdict in ("pass", "revise", "block", "pending"):
            self.assertEqual(counts[verdict], sum(idea["external_verdict"] == verdict for idea in self.ideas))


if __name__ == "__main__":
    unittest.main()
