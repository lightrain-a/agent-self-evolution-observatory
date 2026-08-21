from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .p15_order_effect_protocol_v2 import (
    MAX_REPAIR_PROVIDER_CALLS,
    build_repair_plan,
    extract_solution_code,
    provider_archive_payload,
)


class P15OrderEffectProtocolV2Test(unittest.TestCase):
    def test_archive_keeps_text_response_id_calls_and_usage(self):
        payload=provider_archive_payload({"requested_model":"kimi-k3","resolved_model":"kimi-k3","response_id":"resp-1","status":"completed","text":"def solve(records):\n    return records","function_calls":[],"usage":{"total_tokens":10}})
        self.assertEqual(payload["response_id"],"resp-1")
        self.assertIn("def solve",payload["text"])
        self.assertEqual(payload["usage"]["total_tokens"],10)

    def test_code_extraction_prefers_function_and_strictly_allows_code_text(self):
        call={"function_calls":[{"name":"submit_solution","arguments":json.dumps({"python_code":"def solve(records):\n    return records"})}],"text":"ignored"}
        self.assertEqual(extract_solution_code(call)[1],"FUNCTION_CALL")
        self.assertEqual(extract_solution_code({"function_calls":[],"text":"def solve(records):\n    return records"})[1],"TEXT_FALLBACK")
        self.assertEqual(extract_solution_code({"function_calls":[],"text":"```python\ndef solve(records):\n    return records\n```"})[1],"TEXT_FALLBACK")
        with self.assertRaises(ValueError):
            extract_solution_code({"function_calls":[],"text":"Here is code:\ndef solve(records):\n    return records"})
        with self.assertRaises(ValueError):
            extract_solution_code({"function_calls":[{"name":"submit_solution","arguments":"{}"},{"name":"submit_solution","arguments":"{}"}],"text":""})

    def test_repair_plan_retries_only_old_protocol_failures_and_counts_budget(self):
        with tempfile.TemporaryDirectory() as td:
            study=Path(td);(study/"units").mkdir()
            failure={"failure_manifest_sha256":"b"*64,"provider_calls_charged":10,"remaining_model_call_budget":150,"protocol_failures":[{"unit_id":"T1-NO-SKILL"},{"unit_id":"T1-PERM-4"},{"unit_id":"T1-PERM-5"}]}
            (study/"runtime-failure-manifest-v1.json").write_text(json.dumps(failure))
            (study/"harness-manifest.json").write_text(json.dumps({"harness_manifest_sha256":"a"*64}))
            existing=["T1-NO-SKILL",*[f"T1-PERM-{i}" for i in range(1,7)],*[f"T1-SINGLE-{i}" for i in range(1,4)]]
            for uid in existing:
                status="UNIT_PROTOCOL_FAILURE" if uid in {"T1-NO-SKILL","T1-PERM-4","T1-PERM-5"} else "UNIT_COMPLETE"
                (study/"units"/f"{uid}.json").write_text(json.dumps({"unit_id":uid,"status":status}))
            plan=build_repair_plan(study)
            self.assertEqual(plan["replacement_provider_call_cap"],MAX_REPAIR_PROVIDER_CALLS)
            self.assertEqual(plan["retry_units"],["T1-NO-SKILL","T1-PERM-4","T1-PERM-5"])
            self.assertEqual(len(plan["unstarted_units"]),40)
            self.assertTrue(plan["scientific_object_unchanged"])
            self.assertTrue(plan["protocol_only_change"])


if __name__=="__main__": unittest.main()
