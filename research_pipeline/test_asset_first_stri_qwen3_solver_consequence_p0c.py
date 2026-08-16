from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .asset_first_stri_qwen3_solver_consequence_p0c import analyze, validate_p0a_inputs


class SolverConsequenceP0CTest(unittest.TestCase):
    @staticmethod
    def contract():
        return {
            "counterfactual_reuse": {
                "split_weights": {"skill_003": 1/3, "skill_004": 1/3, "skill_015": 1/3},
                "merge_003_015_weights": {"skill_003": 0.25, "skill_004": 0.5, "skill_015": 0.25},
                "merge_004_015_weights": {"skill_003": 0.5, "skill_004": 0.25, "skill_015": 0.25},
            },
            "statistics": {"bootstrap_replicates": 200, "bootstrap_seed": 7, "meaningful_effect_margin_absolute_p_hat": 0.05},
        }

    def test_strong_go_when_both_mixture_effects_exceed_margin(self):
        values={"skill_003":[1.0]*16,"skill_004":[1.0]*16,"skill_015":[0.0]*16}
        out=analyze(values,self.contract())
        self.assertEqual(out["decision"],"STRONG_ONE_STEP_SOLVER_CONSEQUENCE")
        self.assertTrue(all(row["pass"] for row in out["witness_results"].values()))

    def test_partial_when_only_one_merge_clears_margin(self):
        values={"skill_003":[1.0]*16,"skill_004":[2/3]*16,"skill_015":[2/3]*16}
        out=analyze(values,self.contract())
        self.assertEqual(out["decision"],"PARTIAL_ONE_STEP_SOLVER_CONSEQUENCE")
        self.assertEqual(sum(row["pass"] for row in out["witness_results"].values()),1)

    def test_stop_when_source_difficulty_is_equal(self):
        values={"skill_003":[2/3]*16,"skill_004":[2/3]*16,"skill_015":[2/3]*16}
        out=analyze(values,self.contract())
        self.assertEqual(out["decision"],"STOP_ONE_STEP_UTILITY_CONSEQUENCE")

    def test_input_binding_requires_p0a_go_and_exact_raw_sha(self):
        with tempfile.TemporaryDirectory() as td:
            raw=Path(td)/"raw.jsonl";raw.write_text("".join(json.dumps({"source_skill_id":"skill_003","source_index":i})+"\n" for i in range(72)))
            digest=hashlib.sha256(raw.read_bytes()).hexdigest()
            good=validate_p0a_inputs({}, {"decision":"DYNAMIC_PARTIAL_OVERLAP_REPRESENTATION_SENSITIVITY_SUPPORTED","protocol_valid_for_scientific_update":True,"raw_sha256":digest},raw)
            self.assertTrue(good["pass"])
            bad=validate_p0a_inputs({}, {"decision":"STOP","protocol_valid_for_scientific_update":True,"raw_sha256":"0"*64},raw)
            self.assertFalse(bad["pass"])
            self.assertIn("p0a-not-go",bad["errors"])
            self.assertIn("raw-sha-mismatch",bad["errors"])

if __name__=="__main__": unittest.main()
