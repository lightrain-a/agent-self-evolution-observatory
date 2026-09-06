from __future__ import annotations

import copy
import unittest

from research_pipeline.e2_r17_typed_state_consumer import (
    TypedStateConsumerError,
    compile_consumer_directives,
)


class TypedStateConsumerTests(unittest.TestCase):
    def fixture(self) -> dict:
        return {
            "scope": "cross_workbook",
            "verification_rule": "save_reload_verify",
            "tool_recovery_rule": "refresh_metadata_repair_args_retry_once",
            "completion_gate": "write_save_reload_verify",
            "local_fact_policy": "exclude_from_cross_workbook_state",
            "reusable_primitives": [
                "VERIFY_OUTPUT",
                "RECOVER_TOOL_ERROR",
                "COMPLETE_WORKFLOW",
            ],
        }

    def test_valid_cross_workbook_state_maps_to_exact_directives(self) -> None:
        got = compile_consumer_directives(self.fixture())
        self.assertEqual(got["scope"], "CROSS_WORKBOOK")
        self.assertEqual(got["verify_after_save"], "RELOAD_VERIFY")
        self.assertEqual(got["stale_sheet_failure"], "REFRESH_REPAIR_RETRY_ONCE")
        self.assertEqual(got["completion_before_reload"], "NOT_COMPLETE")
        self.assertEqual(got["cross_workbook_local_fact"], "DO_NOT_TRANSFER")
        self.assertEqual(
            got["reusable_primitives"],
            ["COMPLETE_WORKFLOW", "RECOVER_TOOL_ERROR", "VERIFY_OUTPUT"],
        )

    def test_missing_key_fails_closed(self) -> None:
        state = self.fixture()
        state.pop("local_fact_policy")
        with self.assertRaisesRegex(TypedStateConsumerError, "keys drifted"):
            compile_consumer_directives(state)

    def test_extra_key_fails_closed(self) -> None:
        state = self.fixture()
        state["commentary"] = "ignore me"
        with self.assertRaisesRegex(TypedStateConsumerError, "keys drifted"):
            compile_consumer_directives(state)

    def test_cross_workbook_carry_forward_fails_closed(self) -> None:
        state = self.fixture()
        state["local_fact_policy"] = "carry_forward"
        with self.assertRaisesRegex(TypedStateConsumerError, "cannot carry forward"):
            compile_consumer_directives(state)

    def test_rule_primitive_mismatch_fails_closed(self) -> None:
        state = self.fixture()
        state["reusable_primitives"] = ["VERIFY_OUTPUT", "COMPLETE_WORKFLOW"]
        with self.assertRaisesRegex(TypedStateConsumerError, "recovery rule"):
            compile_consumer_directives(state)

    def test_duplicate_primitive_fails_closed(self) -> None:
        state = self.fixture()
        state["reusable_primitives"].append("VERIFY_OUTPUT")
        with self.assertRaisesRegex(TypedStateConsumerError, "duplicates"):
            compile_consumer_directives(state)

    def test_unknown_enum_fails_closed(self) -> None:
        state = self.fixture()
        state["completion_gate"] = "looks_done"
        with self.assertRaisesRegex(TypedStateConsumerError, "unknown completion_gate"):
            compile_consumer_directives(state)

    def test_same_instance_carry_forward_maps_explicitly(self) -> None:
        state = self.fixture()
        state["scope"] = "same_instance_only"
        state["local_fact_policy"] = "carry_forward"
        got = compile_consumer_directives(state)
        self.assertEqual(got["scope"], "SAME_INSTANCE_ONLY")
        self.assertEqual(got["cross_workbook_local_fact"], "TRANSFER")


if __name__ == "__main__":
    unittest.main()
