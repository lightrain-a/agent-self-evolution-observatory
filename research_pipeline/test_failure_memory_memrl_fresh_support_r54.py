from __future__ import annotations

import hashlib
import json
import pathlib
import unittest

from . import failure_memory_memrl_fresh_support_r54 as r54

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FreshSupportR54Test(unittest.TestCase):
    def test_rank_encoding_is_explicit_and_deterministic(self):
        sig = ("chmod", "cp", "grep", "mkdir", "sed")
        expected = hashlib.sha256(
            b"B1-R53-VALIDATION-20260902|cluster|chmod|cp|grep|mkdir|sed"
        ).hexdigest()
        self.assertEqual(r54._cluster_rank(sig), expected)
        tid = "107"
        expected_member = hashlib.sha256(
            b"B1-R53-VALIDATION-20260902|member|107"
        ).hexdigest()
        self.assertEqual(r54._member_rank(tid), expected_member)

    def test_signature_is_exact_sorted_skill_list(self):
        self.assertEqual(r54._signature({"skill_list": ["sed", "chmod", "cp"]}), ("chmod", "cp", "sed"))

    def test_contract_is_sealed_and_zero_outcome(self):
        p = ROOT / "generated/d2-failure-memory-provenance-r54-full350-fresh-support-contract.json"
        obj = json.loads(p.read_text())
        observed = obj["receipt_sha256"]
        payload = {k: v for k, v in obj.items() if k != "receipt_sha256"}
        self.assertEqual(observed, r54.r53._digest(payload))
        op = obj["operationalization"]
        self.assertEqual(op["expected_fresh_cluster_count"], 108)
        self.assertEqual(op["minimum_eligible_clusters"], 40)
        self.assertEqual(op["validation_treatment_outcomes_observed"], 0)
        self.assertFalse(obj["validation_execution_authority"])

    def test_contract_binds_current_runner(self):
        p = ROOT / "generated/d2-failure-memory-provenance-r54-full350-fresh-support-contract.json"
        obj = json.loads(p.read_text())
        runner = ROOT / "research_pipeline/failure_memory_memrl_fresh_support_r54.py"
        self.assertEqual(obj["bindings"]["runner_sha256"], r54.r53._sha(runner))


if __name__ == "__main__":
    unittest.main()
