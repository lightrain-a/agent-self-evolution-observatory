from __future__ import annotations

import json
import unittest
from pathlib import Path

from .behavior_formal_goal_coupling import analyze_goal_state

SYNTHETIC = Path(__file__).with_name("behavior_formal_goal_coupling_synthetic_cases_20260828.json")

EXPECTED = {
    "S01_INDEPENDENT_FOUR": (4, 4, 0, 1, 1, 0, 0),
    "S02_CHAIN_FOUR": (4, 4, 3, 4, 1, 0, 0),
    "S03_TWO_COMPONENTS": (4, 4, 2, 2, 1, 0, 0),
    "S04_DISJUNCTION_SHARED": (3, 3, 3, 3, 2, 0, 1),
    "S05_QUANTIFIER_SHARED_WITHIN_SCOPE": (2, 2, 1, 2, 3, 1, 0),
    "S06_DISJOINT_QUANTIFIER_SCOPES_SAME_RAW_VAR": (4, 4, 2, 2, 3, 2, 0),
    "S07_NEGATION_AND_DUPLICATE": (3, 2, 1, 2, 2, 0, 0),
    "S08_NESTED_LOGIC_DEPTH": (3, 3, 3, 3, 4, 1, 2),
    "S09_EXACT_COUNT_QUANTIFIER": (2, 2, 1, 2, 3, 1, 0),
    "S10_PAIR_QUANTIFIER": (3, 3, 2, 3, 4, 1, 0),
}


class BehaviorFormalGoalCouplingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SYNTHETIC.read_text(encoding="utf-8"))
        cls.by_id = {row["id"]: row for row in cls.spec["cases"]}

    def test_frozen_synthetic_oracle_all_cases(self) -> None:
        self.assertEqual(set(self.by_id), set(EXPECTED))
        keys = (
            "atomic_occurrence_count",
            "atomic_goal_count",
            "shared_argument_edge_count",
            "largest_connected_component_size",
            "goal_logic_depth",
            "quantifier_count",
            "branch_operator_count",
        )
        for case_id, expected in EXPECTED.items():
            with self.subTest(case_id=case_id):
                actual = analyze_goal_state(self.by_id[case_id]["goal_state"])
                self.assertEqual(tuple(actual[key] for key in keys), expected)
                self.assertEqual(actual["unbound_variable_count"], 0)

    def test_adding_uncoupled_atom_increases_size_not_edges(self) -> None:
        base = analyze_goal_state([["clean", "cup_1"], ["inside", "book_1", "drawer_1"]])
        larger = analyze_goal_state([["clean", "cup_1"], ["inside", "book_1", "drawer_1"], ["cooked", "potato_1"]])
        self.assertEqual(larger["atomic_goal_count"], base["atomic_goal_count"] + 1)
        self.assertEqual(larger["shared_argument_edge_count"], base["shared_argument_edge_count"])
        self.assertGreaterEqual(larger["largest_connected_component_size"], base["largest_connected_component_size"])

    def test_adding_shared_atom_increases_coupling(self) -> None:
        base = analyze_goal_state([["clean", "cup_1"], ["inside", "book_1", "drawer_1"]])
        coupled = analyze_goal_state([["clean", "cup_1"], ["inside", "book_1", "drawer_1"], ["ontop", "cup_1", "drawer_1"]])
        self.assertGreater(coupled["shared_argument_edge_count"], base["shared_argument_edge_count"])
        self.assertGreater(coupled["largest_connected_component_size"], base["largest_connected_component_size"])

    def test_ground_object_renaming_invariance(self) -> None:
        left = analyze_goal_state([["ontop", "cup_1", "tray_1"], ["inside", "tray_1", "cabinet_1"], ["clean", "cup_1"]])
        right = analyze_goal_state([["ontop", "bowl_9", "plate_7"], ["inside", "plate_7", "drawer_5"], ["clean", "bowl_9"]])
        for key in ("atomic_goal_count", "shared_argument_edge_count", "largest_connected_component_size", "goal_logic_depth"):
            self.assertEqual(left[key], right[key])

    def test_bound_variable_alpha_renaming_invariance(self) -> None:
        left = analyze_goal_state([["forall", ["?x", "-", "cup.n.01"], ["and", ["clean", "?x"], ["ontop", "?x", "table_1"]]]])
        right = analyze_goal_state([["forall", ["?z", "-", "cup.n.01"], ["and", ["clean", "?z"], ["ontop", "?z", "table_1"]]]])
        self.assertEqual(left, right)

    def test_disjoint_quantifier_scopes_do_not_false_couple_same_raw_variable(self) -> None:
        result = analyze_goal_state(self.by_id["S06_DISJOINT_QUANTIFIER_SCOPES_SAME_RAW_VAR"]["goal_state"])
        self.assertEqual(result["shared_argument_edge_count"], 2)
        self.assertEqual(result["largest_connected_component_size"], 2)

    def test_duplicate_signed_atom_does_not_inflate_primary_graph(self) -> None:
        result = analyze_goal_state(self.by_id["S07_NEGATION_AND_DUPLICATE"]["goal_state"])
        self.assertEqual(result["atomic_occurrence_count"], 3)
        self.assertEqual(result["atomic_goal_count"], 2)
        self.assertEqual(result["duplicate_atomic_occurrences"], 1)
        self.assertEqual(result["shared_argument_edge_count"], 1)

    def test_unbound_variable_is_fail_visible(self) -> None:
        result = analyze_goal_state([["clean", "?x"]])
        self.assertEqual(result["unbound_variable_count"], 1)

    def test_empty_goal_is_explicit_zero(self) -> None:
        result = analyze_goal_state([])
        self.assertEqual(result["atomic_goal_count"], 0)
        self.assertEqual(result["largest_connected_component_size"], 0)
        self.assertEqual(result["goal_logic_depth"], 0)


if __name__ == "__main__":
    unittest.main()
