from __future__ import annotations

import hashlib
import json
import pathlib
import types
import unittest

from .failure_memory_memrl_q5v2_qualification_r45m1 import (
    Q5B_FORMAT_INSTRUCTION,
    Q5_QUERY,
    _processed_memories,
)


ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "generated/d2-failure-memory-provenance-r45m1-q5v2-qualification-contract.json"
DIFF = ROOT / "generated/d2-failure-memory-provenance-r45m1-q5v2-prompt-contract-diff.json"


def validate_receipt(path: pathlib.Path) -> dict:
    row = json.loads(path.read_text())
    got = row.pop("receipt_sha256")
    expected = hashlib.sha256(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if got != expected:
        raise AssertionError((got, expected))
    return row


class Q5V2QualificationTests(unittest.TestCase):
    def test_q5a_user_instruction_does_not_repair_format(self) -> None:
        self.assertNotIn("Act: bash", Q5_QUERY)
        self.assertNotIn("fenced", Q5_QUERY)
        self.assertIn("SUPPORT_OK", Q5_QUERY)

    def test_q5b_is_explicit_and_diagnostic_only(self) -> None:
        self.assertIn("first characters", Q5B_FORMAT_INSTRUCTION)
        self.assertIn("Act: bash", Q5B_FORMAT_INSTRUCTION)
        self.assertIn("one bash script", Q5B_FORMAT_INSTRUCTION)
        contract = validate_receipt(CONTRACT)
        self.assertFalse(contract["Q5b"]["can_release_scientific_execution"])

    def test_static_diff_closes_scientific_changes(self) -> None:
        row = validate_receipt(DIFF)
        self.assertEqual(row["status"], "PASS")
        audit = row["audit"]
        self.assertEqual(audit["non_whitelisted_scientific_difference_count"], 0)
        for key in (
            "parser_changed", "scientific_source_prompt_changed",
            "LLB_DEFAULT_SYSTEM_PROMPT_changed",
            "build_llb_system_prompt_task_os_changed",
            "source_build_runner_changed", "arm_semantics_changed",
            "model_changed", "temperature_changed", "max_tokens_changed",
        ):
            self.assertIs(audit[key], False)
        self.assertEqual(audit["validation_exposure"], 0)
        self.assertEqual(audit["scientific_source_exposure"], 0)

    def test_memory_categories_match_frozen_runner_semantics(self) -> None:
        rows = [
            {"metadata": types.SimpleNamespace(success=True), "memory_id": "yes"},
            {"metadata": types.SimpleNamespace(success=False), "memory_id": "no"},
        ]
        processed = _processed_memories(rows)
        self.assertEqual([x["memory_id"] for x in processed["successed"]], ["yes"])
        self.assertEqual([x["memory_id"] for x in processed["failed"]], ["no"])


if __name__ == "__main__":
    unittest.main()
