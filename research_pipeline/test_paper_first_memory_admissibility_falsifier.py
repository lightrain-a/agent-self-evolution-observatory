from __future__ import annotations

import unittest

from .paper_first_memory_admissibility_falsifier import action_skeleton, memory_action_skeletons


class MemoryAdmissibilityFalsifierTest(unittest.TestCase):
    def test_action_skeleton_wildcards_movable_object_but_preserves_landmark(self) -> None:
        self.assertEqual(action_skeleton("go to cabinet 3"), "go|cabinet")
        self.assertEqual(action_skeleton("take mug 2 from cabinet 3"), "take|*|cabinet")
        self.assertEqual(action_skeleton("move apple 1 to garbagecan 1"), "place|*|garbagecan")
        self.assertEqual(action_skeleton("clean soapbar 1 with sinkbasin 1"), "clean|*|sinkbasin")
        self.assertEqual(action_skeleton("heat apple 1 with microwave 1"), "heat|*|microwave")
        self.assertEqual(action_skeleton("inventory"), "inventory")

    def test_memory_parser_uses_only_numbered_procedure_lines(self) -> None:
        text = """Experience X. Goal pattern: pick_clean_then_place_in_recep.
A previous successful episode used this procedure:
1. go to sinkbasin 1
2. take soapbar 1 from countertop 1
3. clean soapbar 1 with sinkbasin 1
Use it only when it fits the current goal and state.
"""
        self.assertEqual(
            memory_action_skeletons(text),
            {"go|sinkbasin", "take|*|countertop", "clean|*|sinkbasin"},
        )

    def test_different_movable_object_same_symbolic_command_matches(self) -> None:
        memory = action_skeleton("take mug 1 from countertop 1")
        current = action_skeleton("take apple 2 from countertop 1")
        self.assertEqual(memory, current)


if __name__ == "__main__":
    unittest.main()
