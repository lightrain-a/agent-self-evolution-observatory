from __future__ import annotations
import hashlib,json,pathlib,unittest
from research_pipeline import failure_memory_paired_id_reporting_r75 as r75

ROOT=pathlib.Path(__file__).resolve().parents[1]
RECEIPT=ROOT/"generated/d2-failure-memory-provenance-r75-historical-paired-id-audit.json"


def valid_receipt(x):
    r=x["receipt_sha256"]; y=dict(x); y.pop("receipt_sha256")
    return r==hashlib.sha256(json.dumps(y,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

class PairedIdReportingR75Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.x=json.loads(RECEIPT.read_text(encoding="utf-8"))

    def test_receipt_is_content_addressed_and_bound_to_raw_completed_ledgers(self):
        self.assertTrue(valid_receipt(self.x))
        self.assertEqual(self.x["bindings"]["qwen_r56_completed_ab_arms_file_sha256"],"b96f350ba4006055d4c090ddfe677dec6aea14507ecb4cf2a15a0540667f318c")
        self.assertEqual(self.x["bindings"]["llama_r61_completed_ab_arms_file_sha256"],"34747ca158bf33a354516b3480975483b6214e3c00fc97e78325ae663f04af38")

    def test_qwen_success_set_is_nested_with_task_252_as_sole_gain(self):
        q=self.x["Qwen2.5-7B-Instruct"]
        self.assertEqual((q["left_success_count"],q["right_success_count"]),(15,16))
        self.assertEqual(q["left_only_success_task_ids"],[])
        self.assertEqual(q["right_only_success_task_ids"],["252"])
        self.assertEqual(q["both_success_count"],15)
        self.assertEqual(q["both_fail_count"],16)
        self.assertEqual(q["success_set_subset_relation"],"A_content_only_strict_subset_of_B_raw_provenance")
        self.assertAlmostEqual(q["success_set_jaccard"],15/16)

    def test_llama_zero_net_effect_hides_four_task_substitutions(self):
        l=self.x["Meta-Llama-3.1-8B-Instruct"]
        self.assertEqual((l["left_success_count"],l["right_success_count"]),(17,17))
        self.assertEqual(l["net_success_count_difference_right_minus_left"],0)
        self.assertEqual(l["left_only_success_task_ids"],["125","327"])
        self.assertEqual(l["right_only_success_task_ids"],["136","193"])
        self.assertEqual(l["discordant_task_ids"],["125","136","193","327"])
        self.assertEqual(l["both_success_count"],15)
        self.assertEqual(l["both_fail_count"],13)
        self.assertAlmostEqual(l["success_set_jaccard"],15/19)
        self.assertAlmostEqual(l["outcome_discordance_fraction"],4/32)
        self.assertFalse(l["same_success_task_set"])

    def test_equal_counts_do_not_imply_same_success_ids(self):
        rows=[
            {"task_id":"1","arm":"P","terminal_success":True},
            {"task_id":"1","arm":"T","terminal_success":False},
            {"task_id":"2","arm":"P","terminal_success":False},
            {"task_id":"2","arm":"T","terminal_success":True},
        ]
        s=r75.paired_id_summary(rows,"P","T")
        self.assertEqual(s["left_success_count"],s["right_success_count"])
        self.assertEqual(s["net_success_count_difference_right_minus_left"],0)
        self.assertEqual(s["left_only_success_task_ids"],["1"])
        self.assertEqual(s["right_only_success_task_ids"],["2"])
        self.assertFalse(s["same_success_task_set"])
        self.assertEqual(s["outcome_discordance_fraction"],1.0)

    def test_future_contract_requires_id_level_reporting_without_changing_r72(self):
        c=r75.future_reporting_contract()
        self.assertEqual(c["required_contrasts"]["Qwen_primary"],{"left":"P_neutral","right":"T_truthful","planned_n":66})
        self.assertEqual(c["required_contrasts"]["Llama_replication"],{"left":"P_neutral","right":"T_truthful","planned_n":66})
        self.assertIn("left_only_success_task_ids",c["required_fields_per_contrast"])
        self.assertIn("right_only_success_task_ids",c["required_fields_per_contrast"])
        self.assertIn("success_set_jaccard",c["required_fields_per_contrast"])
        self.assertFalse(c["changes_R72_R73_inferential_gate"])
        self.assertFalse(c["changes_R72_R73_execution_schedule"])
        self.assertEqual(c["new_trajectories_required"],0)

    def test_cross_executor_overlap_is_descriptive_only(self):
        for arm in ["A_content_only","B_raw_provenance"]:
            s=self.x["cross_executor"][arm]
            self.assertEqual(s["inferential_role"],"descriptive_only_no_pooling")
        self.assertAlmostEqual(self.x["cross_executor"]["A_content_only"]["success_set_jaccard"],11/21)
        self.assertAlmostEqual(self.x["cross_executor"]["B_raw_provenance"]["success_set_jaccard"],12/21)

if __name__=="__main__":unittest.main()
