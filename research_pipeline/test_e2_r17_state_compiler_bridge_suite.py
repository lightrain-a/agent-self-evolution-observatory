from __future__ import annotations

import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from research_pipeline.e2_r17_controlled_suite_schema import FAMILIES
from research_pipeline.e2_r17_state_compiler_bridge_suite import (
    build_bridge_suite,
    self_check_bridge_suite,
)


class StateCompilerBridgeSuiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name) / "bridge-suite"
        cls.manifest = build_bridge_suite(cls.root)
        cls.check = self_check_bridge_suite(cls.root)
        cls.split = json.loads((cls.root / "bridge_split_manifest.json").read_text(encoding="utf-8"))
        cls.meta = {
            row["id"]: row
            for row in json.loads((cls.root / "bridge_metadata.json").read_text(encoding="utf-8"))
        }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_cardinality(self) -> None:
        self.assertEqual(self.manifest["candidate_task_count"], 162)
        self.assertEqual(self.manifest["formal_task_count"], 120)
        self.assertEqual(self.check["status"], "PASS")

    def test_blocks_are_new_and_do_not_touch_e3(self) -> None:
        ids = set(self.meta)
        self.assertTrue(all(task_id.startswith(("r17-b7-", "r17-b8-", "r17-b9-")) for task_id in ids))
        self.assertFalse(any(task_id.startswith(("r17-b5-", "r17-b6-")) for task_id in ids))

    def test_update_stream_shape_and_family_balance(self) -> None:
        streams = self.split["update_streams"]
        self.assertEqual(len(streams), 12)
        self.assertTrue(all(len(ids) == 8 for ids in streams.values()))
        self.assertEqual(len({task_id for ids in streams.values() for task_id in ids}), 96)
        for group in ("screen_stream_ids", "validation_stream_ids"):
            counts = Counter(
                self.meta[streams[stream_id][0]]["primary_failure_family"]
                for stream_id in self.split[group]
            )
            self.assertEqual(counts, Counter({family: 1 for family in FAMILIES}))

    def test_screen_validation_heldout_are_disjoint_and_balanced(self) -> None:
        screen = set(self.split["screen_heldout"])
        validation = set(self.split["validation_heldout"])
        self.assertEqual(len(screen), 12)
        self.assertEqual(len(validation), 12)
        self.assertFalse(screen & validation)
        for panel in (screen, validation):
            counts = Counter(self.meta[x]["primary_failure_family"] for x in panel)
            self.assertEqual(counts, Counter({family: 2 for family in FAMILIES}))

    def test_heldout_never_enters_update(self) -> None:
        update = {task_id for ids in self.split["update_streams"].values() for task_id in ids}
        heldout = set(self.split["screen_heldout"]) | set(self.split["validation_heldout"])
        self.assertFalse(update & heldout)

    def test_reserve_sizes(self) -> None:
        self.assertEqual(len(self.split["update_reserve_integrity_only"]), 12)
        self.assertEqual(len(self.split["heldout_reserve_integrity_only"]), 30)

    def test_rebuild_is_byte_identical_at_manifest_level(self) -> None:
        other = Path(self.temp.name) / "bridge-suite-2"
        other_manifest = build_bridge_suite(other)
        self.assertEqual(self.manifest["dataset_sha256"], other_manifest["dataset_sha256"])
        self.assertEqual(self.manifest["split_manifest_sha256"], other_manifest["split_manifest_sha256"])


if __name__ == "__main__":
    unittest.main()
