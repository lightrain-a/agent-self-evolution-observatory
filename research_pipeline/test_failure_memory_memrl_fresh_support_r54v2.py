from __future__ import annotations

import json
import pathlib
import unittest
from unittest import mock

from . import failure_memory_memrl_fresh_support_r54v2 as v2

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FreshSupportR54V2Test(unittest.TestCase):
    def test_repair_contract_is_sealed_and_binds_runner(self):
        p = ROOT / "generated/d2-failure-memory-provenance-r54v2-interface-repair-contract.json"
        obj = json.loads(p.read_text())
        payload = {k: v for k, v in obj.items() if k != "receipt_sha256"}
        self.assertEqual(obj["receipt_sha256"], v2.v1.r53._digest(payload))
        runner = ROOT / "research_pipeline/failure_memory_memrl_fresh_support_r54v2.py"
        self.assertEqual(obj["bindings"]["v2_runner_sha256"], v2.v1.r53._sha(runner))
        self.assertFalse(obj["validation_execution_authority"])

    def test_v1_hold_records_zero_fresh_support_rows(self):
        p = ROOT / "generated/d2-failure-memory-provenance-r54-v1-pre-retrieval-hold.json"
        obj = json.loads(p.read_text())
        payload = {k: v for k, v in obj.items() if k != "receipt_sha256"}
        self.assertEqual(obj["receipt_sha256"], v2.v1.r53._digest(payload))
        self.assertEqual(obj["accounting"]["fresh_support_rows_observed"], 0)
        self.assertEqual(obj["accounting"]["validation_treatment_outcomes_observed"], 0)

    def test_materialized_builder_inserts_exact_ids_only_in_copy(self):
        manifest = {"execution_manifest": {"source": {"checkout": "/tmp/fake"}, "source_build": {"split": "train.json", "split_sha256": "s", "selected_ids_sha256": "h"}}}
        with mock.patch.object(v2.pathlib.Path, "is_file", return_value=True), \
             mock.patch.object(v2.v1.r53, "_sha", return_value="s"), \
             mock.patch.object(v2.v1.r53, "_load", return_value={}), \
             mock.patch.object(v2.v1.r53, "_materialize_full350_ids", return_value=[str(i) for i in range(350)]), \
             mock.patch.object(v2.v1, "_ids_hash", return_value="h"), \
             mock.patch.object(v2, "_ORIGINAL_BUILDER", return_value=("service", "runner")) as b:
            out = v2.materialized_service_builder(manifest, pathlib.Path("/tmp/out"))
        self.assertEqual(out, ("service", "runner"))
        self.assertNotIn("selected_ids", manifest["execution_manifest"]["source_build"])
        passed_manifest = b.call_args.args[0]
        self.assertEqual(len(passed_manifest["execution_manifest"]["source_build"]["selected_ids"]), 350)


if __name__ == "__main__":
    unittest.main()
