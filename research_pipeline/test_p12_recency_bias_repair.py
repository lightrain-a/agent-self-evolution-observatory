from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .p12_recency_bias_repair import (
    FAILED_PAIR,
    REPLACEMENT_CALL_CAP,
    build_repair_plan,
)


class P12RecencyBiasRepairTest(unittest.TestCase):
    def test_repair_plan_retries_only_failed_cyclic_pair_and_preserves_budget(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/"difficulty").mkdir()
            (root/"harness-implementation-manifest.json").write_text(json.dumps({"harness_manifest_sha256":"a"*64}))
            (root/"runtime-failure-manifest-v1.json").write_text(json.dumps({"failure_manifest_sha256":"b"*64}))
            plan=build_repair_plan(root)
            self.assertEqual(plan["retry"]["pair_id"],FAILED_PAIR)
            self.assertEqual(plan["retry"]["old_max_output_tokens"],600)
            self.assertEqual(plan["retry"]["new_max_output_tokens"],1200)
            self.assertEqual(plan["replacement_provider_call_cap"],REPLACEMENT_CALL_CAP)
            self.assertEqual(REPLACEMENT_CALL_CAP,101)
            self.assertEqual(plan["provider_calls_already_charged"]+plan["replacement_provider_call_cap"],105)
            self.assertTrue(plan["scientific_object_unchanged"])
            self.assertTrue(plan["protocol_only_change"])
            self.assertEqual(plan["reuse_completed_difficulty"],["D-LINEAR-1","D-QUADRATIC-1","D-ALTERNATING2-1"])


if __name__=="__main__": unittest.main()
