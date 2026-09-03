from __future__ import annotations

import json
import pathlib
import unittest

from research_pipeline.failure_memory_memrl_final_adjudication_r57 import OUTPUT, build, digest


class FinalAdjudicationR57Test(unittest.TestCase):
    def test_primary_result_is_exact_complete_run_result(self) -> None:
        r = build()
        p = r["primary_terminal_result"]
        self.assertEqual((p["A_content_only_successes"], p["A_content_only_total"]), (15, 32))
        self.assertEqual((p["B_raw_provenance_successes"], p["B_raw_provenance_total"]), (16, 32))
        self.assertEqual(p["paired_effect"], 0.03125)
        self.assertEqual((p["B_only_success"], p["A_only_success"], p["discordant_pairs"]), (1, 0, 1))
        self.assertEqual(p["preregistered_ci95_paired_cluster_bootstrap"], [0.0, 0.09375])
        self.assertEqual(p["preregistered_exact_two_sided_signflip_p"], 1.0)
        self.assertFalse(p["effect_relevance_floor_met"])

    def test_mechanism_diagnostic_cannot_upgrade_primary_claim(self) -> None:
        r = build()
        m = r["postconfirmatory_descriptive_mechanism"]
        self.assertFalse(m["inferential_authority"])
        self.assertEqual(m["first_executable_action_diff_clusters"], 9)
        self.assertEqual(m["terminal_outcome_diff_clusters"], 1)
        self.assertEqual(m["sole_terminal_discordant_task_id"], "252")
        self.assertTrue(m["task_252_R39_adapter_audit"]["actionable_content_identical"])

    def test_nonclaims_are_explicit(self) -> None:
        r = build()
        self.assertFalse(r["scientific_adjudication"]["zero_effect_proof"])
        self.assertEqual(r["remaining_scientific_scope"]["C_D_status"], "NOT_EXECUTED")
        self.assertEqual(r["remaining_scientific_scope"]["PSMG_efficacy_status"], "NOT_IDENTIFIED")
        self.assertTrue(all(r["forbidden_claims"].values()))

    def test_generated_receipt_is_sealed(self) -> None:
        r = build()
        self.assertEqual(r["receipt_sha256"], digest({k: v for k, v in r.items() if k != "receipt_sha256"}))
        if OUTPUT.exists():
            disk = json.loads(OUTPUT.read_text(encoding="utf-8"))
            self.assertEqual(disk, r)


if __name__ == "__main__":
    unittest.main()
