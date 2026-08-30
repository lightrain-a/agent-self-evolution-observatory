from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .b1_memrl_alfworld_adjudication import _binom_two_sided_p, _clopper_pearson
from .b1_memrl_alfworld_target_execution import _pair_summary
from .b1_memrl_alfworld_target_plan import ARMS, compile_target_execution_plan, content_hash, sha_text


class B1MemRLAlfworldTargetPipelineTest(unittest.TestCase):
    def fixture(self, root: Path):
        source_dir = root / "source"; source_dir.mkdir()
        preflight = {
            "paper_id":"D2-PAPER-FAILURE-MEMORY-PROVENANCE","status":"FRESH_SUBSTRATE_G1_G8_PREFLIGHT_PASS","manifest_sha256":"m"*64,
            "authority":{"scientific":False,"paper":False,"experiment":False,"provider":False,"gpu":False,"submission":False},
            "statistics":{"pilot_n":2,"confirmatory_n":3},
            "task_partition":{"pilot_targets":[{"family":"f1","relative_gamefile":"p1","gamefile_sha256":"1"*64},{"family":"f2","relative_gamefile":"p2","gamefile_sha256":"2"*64}],
              "confirmatory_targets":[{"family":"f1","relative_gamefile":"c1","gamefile_sha256":"3"*64},{"family":"f2","relative_gamefile":"c2","gamefile_sha256":"4"*64},{"family":"f3","relative_gamefile":"c3","gamefile_sha256":"5"*64}]},
        }
        support = {"status":"SOURCE_PROVENANCE_SUPPORT_PASS","pilot_execution_authorized":True,"preflight_manifest_sha256":"m"*64,"receipt_sha256":"s"*64,"summary":{"support_met":True}}
        for i, provenance in enumerate(("failure","success","failure","success")):
            body=f"body-{i}"; row={"execution_valid":True,"source_index":i,"family":f"s{i}","true_provenance":provenance,"memory_body":body,"memory_body_sha256":sha_text(body),"preflight_manifest_sha256":"m"*64}
            (source_dir/f"{i:02d}.json").write_text(json.dumps(row))
        pp=root/"preflight.json"; sp=root/"source-support.json"; pp.write_text(json.dumps(preflight)); sp.write_text(json.dumps(support))
        return pp,sp

    def test_plan_assignment_is_index_only_and_freezes_both_phases(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); pp,sp=self.fixture(root)
            plan=compile_target_execution_plan(preflight_path=pp,source_support_path=sp,output_dir=root,generated_at="x")
            self.assertEqual([r["source_index"] for r in plan["assignments"]["pilot"]],[0,1])
            self.assertEqual([r["source_index"] for r in plan["assignments"]["confirmatory"]],[2,3,0])
            self.assertFalse(plan["pairing_uses_source_provenance"]); self.assertFalse(plan["pairing_uses_target_outcome"]); self.assertFalse(plan["pairing_uses_pilot_outcome"])
            self.assertEqual(plan["assignments"]["pilot"][0]["arm_patch_sha256"]["A1_CONTENT_ONLY"],plan["assignments"]["pilot"][0]["arm_patch_sha256"]["A7_BACKEND_ONLY_LABEL"])
            self.assertEqual(plan["plan_sha256"],content_hash(plan,exclude={"generated_at","plan_sha256"}))

    def test_pair_summary_enforces_no_channel_and_detects_utilization(self):
        base={arm:{"execution_valid":True,"patch_sha256":arm,"actions":["a"],"terminal_success":0,"first_action":"a"} for arm in ARMS}
        base["A1_CONTENT_ONLY"]["patch_sha256"]="same";base["A7_BACKEND_ONLY_LABEL"]["patch_sha256"]="same"
        base["A2_TRUTHFUL_VISIBLE_PROVENANCE"]["actions"]=["b"];base["A2_TRUTHFUL_VISIBLE_PROVENANCE"]["first_action"]="b"
        row=_pair_summary(base,{"target_index":0,"family":"f","relative_gamefile":"g","source_index":1,"source_memory_body_sha256":"h","true_provenance":"failure"})
        self.assertTrue(row["no_channel_negative_control_exact"]);self.assertTrue(row["memory_utilization_observed"]);self.assertTrue(row["first_action_changed_vs_A0"]["A2_TRUTHFUL_VISIBLE_PROVENANCE"])

    def test_exact_sign_test_and_interval_boundaries(self):
        self.assertAlmostEqual(_binom_two_sided_p(0,4),0.125)
        self.assertEqual(_binom_two_sided_p(0,0),1.0)
        lo,hi=_clopper_pearson(2,4)
        self.assertGreater(lo,0);self.assertLess(hi,1);self.assertLess(lo,0.5);self.assertGreater(hi,0.5)


if __name__ == "__main__": unittest.main()
