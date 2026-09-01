from __future__ import annotations

import unittest

from research_pipeline.failure_memory_memrl_source_qualification_r46m2 import strict_adjudicate
from research_pipeline.failure_memory_memrl_ab_identification_r48 import (
    arm_order,
    canonical_json,
    exact_two_sided_signflip,
    percentile_ci,
    render_pair,
)
from research_pipeline import failure_memory_memrl_utilization_r47m2 as r47m2


def _digest(v):
    import hashlib, json
    return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


def _seal(v):
    v=dict(v);v["receipt_sha256"]=_digest(v);return v


class StrictR46Tests(unittest.TestCase):
    def base_receipt(self):
        return _seal({
            "paper_id":"D2-PAPER-FAILURE-MEMORY-PROVENANCE",
            "status":"SOURCE_QUALIFICATION_PASS_RETRIEVAL_FROZEN_VALIDATION_STILL_SEALED",
            "both_source_provenance_polarities_retrievable":True,
            "validation_treatment_outcomes_observed":0,
        })

    def frozen(self, missing_primary: int | None = None):
        rows=[]
        for i in range(32): rows.append({"cohort":"primary","validation_task_id":str(i),"has_eligible_frozen_retrieval":i!=missing_primary})
        for i in range(8): rows.append({"cohort":"utilization","validation_task_id":f"u{i}","has_eligible_frozen_retrieval":True})
        return _seal({"paper_id":"D2-PAPER-FAILURE-MEMORY-PROVENANCE","rows":rows,"validation_treatment_outcomes_observed":0})

    def test_requires_all_32_primary_not_merely_32_of_40(self):
        r=strict_adjudicate(self.base_receipt(),self.frozen(missing_primary=3))
        self.assertEqual(r["primary_clusters_with_eligible_frozen_retrieval"],31)
        self.assertFalse(r["all_32_primary_clusters_supported"])
        self.assertTrue(r["status"].startswith("SUPPORT_STOP"))

    def test_all_32_primary_passes(self):
        r=strict_adjudicate(self.base_receipt(),self.frozen())
        self.assertEqual(r["primary_clusters_with_eligible_frozen_retrieval"],32)
        self.assertTrue(r["all_32_primary_clusters_supported"])
        self.assertEqual(r["status"],"SOURCE_QUALIFICATION_PASS_RETRIEVAL_FROZEN_VALIDATION_STILL_SEALED")


class R47M2PlumbingTests(unittest.TestCase):
    def test_command_line_main_rebinds_original_r47_preflight_to_m2(self):
        self.assertIs(r47m2.base.base.preflight, r47m2.preflight)


class ABOperationalizationTests(unittest.TestCase):
    def selected(self):
        return [
            {"eligible":True,"memory_id":"m1","content":"alpha","source_outcome_success":True,"source_task_id":"1","similarity":.8,"q_estimate":.2,"score":.5},
            {"eligible":True,"memory_id":"m2","content":"beta","source_outcome_success":False,"source_task_id":"2","similarity":.7,"q_estimate":.1,"score":.4},
        ]

    def test_renderer_only_adds_provenance_field(self):
        r=render_pair(self.selected(),"x")
        self.assertNotIn("source_outcome_success",r["A_content_only"])
        self.assertIn('"source_outcome_success":true',r["B_raw_provenance"])
        self.assertIn('"source_outcome_success":false',r["B_raw_provenance"])
        self.assertTrue(r["A_content_only"].startswith("[Retrieved Memory Context]\n["))
        self.assertEqual(r["audit"]["only_executor_visible_difference"],"source_outcome_success")

    def test_ineligible_selected_row_fails_closed(self):
        rows=self.selected();rows[0]["eligible"]=False
        with self.assertRaises(RuntimeError): render_pair(rows,"x")

    def test_arm_order_is_deterministic_and_balanced_surface(self):
        self.assertEqual(arm_order(20260825,"107"),arm_order(20260825,"107"))
        self.assertEqual(set(arm_order(20260825,"107")),{"A_content_only","B_raw_provenance"})

    def test_exact_signflip(self):
        self.assertEqual(exact_two_sided_signflip(0,0),1.0)
        self.assertAlmostEqual(exact_two_sided_signflip(5,0),0.0625)
        self.assertEqual(exact_two_sided_signflip(2,2),1.0)

    def test_bootstrap_is_deterministic(self):
        a=percentile_ci([1,0,-1,1],123,reps=1000)
        b=percentile_ci([1,0,-1,1],123,reps=1000)
        self.assertEqual(a,b)

    def test_canonical_json_is_compact_sorted(self):
        self.assertEqual(canonical_json([{"b":2,"a":1}]),'[{"a":1,"b":2}]')


if __name__ == "__main__":
    unittest.main()
