from __future__ import annotations

import unittest

from research_pipeline.agent_safety_g1_mcta_runtime_binding import (
    LOCAL_PAIR_IDS,
    OPEN_ENDED_HOLD_PAIR_IDS,
    RuntimeBindingError,
    primitive_events,
    runtime_binding_disposition,
)


class MCTARuntimeBindingTest(unittest.TestCase):
    def test_eight_local_pairs_and_two_open_ended_holds_partition_panel(self) -> None:
        self.assertEqual(len(LOCAL_PAIR_IDS), 8)
        self.assertEqual(len(OPEN_ENDED_HOLD_PAIR_IDS), 2)
        self.assertFalse(LOCAL_PAIR_IDS & OPEN_ENDED_HOLD_PAIR_IDS)
        self.assertEqual(
            LOCAL_PAIR_IDS | OPEN_ENDED_HOLD_PAIR_IDS,
            {f"MCT-{i:02d}" for i in range(10)},
        )

    def test_dispositions_fail_closed(self) -> None:
        self.assertEqual(runtime_binding_disposition("MCT-00"), "LOCAL_DETERMINISTIC_BINDING_DEFINED")
        self.assertEqual(runtime_binding_disposition("MCT-03"), "HOLD_OPEN_ENDED_SEARCH_OUTPUT_BINDING")
        with self.assertRaises(RuntimeBindingError):
            runtime_binding_disposition("MCT-99")

    def test_primitive_snapshot_normalization(self) -> None:
        got = primitive_events({
            "events": [
                {"primitive": "fill_title", "ts": 1},
                {"primitive": ""},
                {"kind": "ignored"},
                {"primitive": "activate_submit_post", "ts": 2},
            ]
        })
        self.assertEqual(got, ["fill_title", "activate_submit_post"])


if __name__ == "__main__":
    unittest.main()
