from __future__ import annotations

import unittest
from collections import Counter

from .e2_r17_controlled_suite_schema import (
    DISTRACTOR_COUNTS,
    L9_PROFILES,
    add_distractors,
    answer_cells,
    new_book,
    seeded_rng,
)
from .e2_r17_semantic_transfer_builders import BUILDERS, FAMILY_SPECS


class SemanticTransferBuilderTest(unittest.TestCase):
    def _build(self, family: str, profile: int):
        depth, distractor_level, ambiguity = L9_PROFILES[profile]
        task_id = f"semantic-transfer-test-{family}-{profile}"
        wb = new_book(task_id)
        rng = seeded_rng(task_id)
        add_distractors(wb, DISTRACTOR_COUNTS[distractor_level], rng, ambiguity)
        instruction, answer_position, expected = BUILDERS[family](wb, rng, depth, ambiguity, task_id)
        return wb, instruction, answer_position, expected

    def test_all_profiles_build_and_obey_semantic_rule(self) -> None:
        for family, spec in FAMILY_SPECS.items():
            for profile in range(len(L9_PROFILES)):
                with self.subTest(family=family, profile=profile):
                    wb, instruction, answer_position, expected = self._build(family, profile)
                    try:
                        self.assertTrue(instruction)
                        self.assertTrue(answer_cells(answer_position))
                        self.assertEqual(spec["semantic_type"], expected["semantic_type"])
                        self.assertEqual(spec["matched_skeleton"], expected["matched_skeleton"])
                        if spec["semantic_type"] == "PROCEDURAL_TRANSFORMATION":
                            self.assertGreaterEqual(int(expected["reusable_transform_steps"]), 2)
                            self.assertEqual(1, int(expected["binding_candidate_count"]))
                        else:
                            self.assertLessEqual(int(expected["reusable_transform_steps"]), 1)
                            self.assertGreaterEqual(int(expected["binding_candidate_count"]), 2)
                    finally:
                        wb.close()

    def test_each_skeleton_crosses_both_semantic_types(self) -> None:
        skeletons: dict[str, set[str]] = {}
        for spec in FAMILY_SPECS.values():
            skeletons.setdefault(str(spec["matched_skeleton"]), set()).add(str(spec["semantic_type"]))
        self.assertEqual(3, len(skeletons))
        for semantic_types in skeletons.values():
            self.assertEqual({"PROCEDURAL_TRANSFORMATION", "INSTANCE_BINDING_LOCALIZATION"}, semantic_types)

    def test_binding_shortcuts_do_not_have_fixed_position(self) -> None:
        positions = {
            "foreign_key_binding_left": Counter(),
            "foreign_key_binding_right": Counter(),
            "header_source_binding": Counter(),
            "named_region_binding": Counter(),
        }
        for family in ("foreign_key_binding", "header_source_binding", "named_region_binding"):
            for profile in range(len(L9_PROFILES)):
                wb, _, _, expected = self._build(family, profile)
                try:
                    if family == "foreign_key_binding":
                        positions["foreign_key_binding_left"][expected["left_candidate_order"].index(expected["left_key"])] += 1
                        positions["foreign_key_binding_right"][expected["right_candidate_order"].index(expected["right_key"])] += 1
                    elif family == "header_source_binding":
                        positions["header_source_binding"][expected["candidate_order"].index(expected["authoritative_header"])] += 1
                    else:
                        positions["named_region_binding"][expected["region_order"].index(expected["region_label"])] += 1
                finally:
                    wb.close()
        for label, counts in positions.items():
            with self.subTest(label=label):
                self.assertGreaterEqual(len(counts), 2)


if __name__ == "__main__":
    unittest.main()
