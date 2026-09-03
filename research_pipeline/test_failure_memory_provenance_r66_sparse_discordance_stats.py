import math
import unittest
from pathlib import Path

from research_pipeline.failure_memory_provenance_r66_sparse_discordance_stats import build, clopper_pearson


class R66SparseDiscordanceStatsTest(unittest.TestCase):
    def test_clopper_pearson_known_sparse_bounds(self):
        lo0, hi0 = clopper_pearson(0, 32)
        lo1, hi1 = clopper_pearson(1, 32)
        self.assertEqual(lo0, 0.0)
        self.assertAlmostEqual(hi0, 0.12797599984079655, places=10)
        self.assertAlmostEqual(lo1, 0.00039300969541375153, places=10)
        self.assertAlmostEqual(hi1, 0.18343510046636374, places=10)

    def test_current_qwen_llama_conservative_intervals(self):
        root = Path(__file__).resolve().parents[1]
        result = build(
            root / "generated/d2-failure-memory-provenance-r56-qwen-ab-identification-result.json",
            root / "generated/d2-failure-memory-provenance-r61-llama-ab-identification-result.json",
        )
        by = {row["model"]: row for row in result["models"]}
        q = by["Qwen2.5-7B-Instruct"]
        l = by["Meta-Llama-3.1-8B-Instruct"]
        self.assertAlmostEqual(q["conservative_paired_risk_difference_ci95"][0], -0.1275829901453828, places=10)
        self.assertAlmostEqual(q["conservative_paired_risk_difference_ci95"][1], 0.18343510046636374, places=10)
        self.assertAlmostEqual(l["conservative_paired_risk_difference_ci95"][0], -0.22541599162833906, places=10)
        self.assertAlmostEqual(l["conservative_paired_risk_difference_ci95"][1], 0.22541599162833906, places=10)
        self.assertFalse(q["positive_15pp_effect_excluded"])
        self.assertFalse(l["positive_15pp_effect_excluded"])
        self.assertFalse(q["plus_minus_15pp_equivalence_established"])
        self.assertFalse(l["plus_minus_15pp_equivalence_established"])
        self.assertFalse(result["adjudication"]["plus_minus_15pp_equivalence_established_for_both_models"])
        self.assertFalse(result["adjudication"]["population_plus_15pp_excluded_for_both_models"])


if __name__ == "__main__":
    unittest.main()
