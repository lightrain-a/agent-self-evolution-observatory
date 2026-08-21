from __future__ import annotations

import unittest

from .p22_retrieval_budget_harness import (
    CAL_IDS,
    EVAL_IDS,
    FEATURES,
    K_VALUES,
    MEMORY_IDS,
    bm25_rank,
    prediction_manifest,
    tokens,
)


class P22RetrievalBudgetHarnessTest(unittest.TestCase):
    def test_frozen_split_and_k_contract(self):
        self.assertEqual(len(MEMORY_IDS), 30)
        self.assertEqual(len(set(MEMORY_IDS) | set(CAL_IDS) | set(EVAL_IDS)), 34)
        self.assertEqual(K_VALUES, (1, 3, 5, 10, 20, "all"))

    def test_tokenizer_and_bm25_are_deterministic(self):
        self.assertIn("人工", tokens("人工智能 AI_2026"))
        pool = [
            {"memory_id": "M00", "source_task_id": "0", "content": "黄金 上海 价格", "content_sha256": "0"},
            *[
                {"memory_id": f"M{i:02d}", "source_task_id": str(i), "content": f"其他 信息 {i}", "content_sha256": str(i)}
                for i in range(1, 30)
            ],
        ]
        one = bm25_rank("上海黄金价格", pool)
        two = bm25_rank("上海黄金价格", pool)
        self.assertEqual(one, two)
        self.assertEqual(one[0]["memory_id"], "M00")

    def _probe(self):
        rows = []
        for task_id in (*CAL_IDS, *EVAL_IDS):
            for index, kval in enumerate(K_VALUES):
                k_int = 30 if kval == "all" else int(kval)
                base = 0.1 + 0.03 * index + (0.02 if task_id in EVAL_IDS else 0.0)
                rows.append(
                    {
                        "task_id": task_id,
                        "k": kval,
                        "k_int": k_int,
                        "features": {
                            "k": k_int / 30,
                            "similarity_mean": base,
                            "similarity_min": base / 2,
                            "similarity_max": base * 1.5,
                            "similarity_q25": base * 0.75,
                            "similarity_q50": base,
                            "similarity_q75": base * 1.25,
                            "similarity_slope": 0.01 * (index + 1),
                            "task_embedding_projection_0": 0.1 if task_id in CAL_IDS else 0.2,
                            "task_embedding_projection_1": -0.2 if task_id.endswith("7") or task_id.endswith("0") else 0.3,
                        },
                    }
                )
        return {"status": "P22_OFFLINE_HARNESS_PROBE_PASS", "offline_probe_sha256": "a" * 64, "baseline_features": rows}

    def test_prediction_manifest_rejects_evaluation_leakage(self):
        calibration = [{"task_id": task_id, "k": kval, "success": int(index % 2 == 0)} for task_id in CAL_IDS for index, kval in enumerate(K_VALUES)]
        calibration.append({"task_id": EVAL_IDS[0], "k": 1, "success": 1})
        with self.assertRaisesRegex(ValueError, "evaluation outcome"):
            prediction_manifest(self._probe(), calibration)

    def test_prediction_manifest_is_committed_before_evaluation_outcomes(self):
        calibration = [{"task_id": task_id, "k": kval, "success": int(index in {1, 2})} for task_id in CAL_IDS for index, kval in enumerate(K_VALUES)]
        manifest = prediction_manifest(self._probe(), calibration)
        self.assertEqual(manifest["status"], "P22_EVALUATION_PREDICTIONS_COMMITTED")
        self.assertEqual(len(manifest["evaluation_predictions"]), 2)
        self.assertEqual(len(manifest["prediction_manifest_sha256"]), 64)
        self.assertFalse(manifest["baseline"]["evaluation_outcomes_visible_during_fit"])
        self.assertEqual(manifest["baseline"]["features"], list(FEATURES))


if __name__ == "__main__":
    unittest.main()
