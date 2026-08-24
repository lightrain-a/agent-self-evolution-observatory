from __future__ import annotations

import unittest

from .methodology_controls import build_methodology_controls_state
from .system_architecture import (
    COMPONENT_BINDINGS,
    FUNCTIONAL_LAYERS,
    READING_GROUPS,
    TEMPORAL_FLOW,
    annotate_components,
    build_system_architecture,
)


class SystemArchitectureTest(unittest.TestCase):
    def test_temporal_flow_is_single_ordered_paper_first_lifecycle(self) -> None:
        keys = [row["key"] for row in TEMPORAL_FLOW]
        self.assertEqual(len(keys), 21)
        self.assertEqual(keys[:5], ["scope", "evidence", "novelty", "method", "experiment-blueprint"])
        self.assertEqual(keys[5:10], ["economy-compile", "local-validation", "method-freeze", "full-experiment", "paper-evidence"])
        self.assertEqual(keys[10:20], ["paper-design", "manuscript", "mock-pc", "targeted-repair", "claim-audit", "pdf-qa", "prebuttal", "submission-ready", "submitted", "rebuttal"])
        self.assertEqual(keys[-1], "learn")
        self.assertEqual([row["index"] for row in TEMPORAL_FLOW], list(range(1, 22)))

    def test_reading_groups_cover_the_temporal_flow_without_creating_new_gates(self) -> None:
        self.assertEqual(len(READING_GROUPS), 10)
        self.assertEqual(READING_GROUPS[0]["key"], "overview")
        self.assertTrue(READING_GROUPS[0]["orientation_only"])
        grouped = [stage for row in READING_GROUPS[1:] for stage in row["stage_keys"]]
        self.assertEqual(grouped, [row["key"] for row in TEMPORAL_FLOW])
        self.assertEqual(len(grouped), len(set(grouped)))

    def test_functional_layers_are_distinct_from_temporal_flow(self) -> None:
        keys = [row["key"] for row in FUNCTIONAL_LAYERS]
        self.assertEqual(len(keys), 6)
        self.assertEqual(len(set(keys)), 6)
        self.assertIn("paper-design", keys)
        self.assertIn("experiment-design", keys)
        self.assertIn("scientific-validation", keys)
        self.assertIn("runtime-authority", keys)

    def test_all_declared_component_bindings_are_unique(self) -> None:
        component_keys = [binding[0] for binding in COMPONENT_BINDINGS.values()]
        self.assertEqual(len(COMPONENT_BINDINGS), 33)
        self.assertEqual(len(component_keys), len(set(component_keys)))

    def test_unknown_component_is_visible_not_silently_assigned(self) -> None:
        items = annotate_components([{"component":{"en":"Unknown future component"},"status":"running"}])
        architecture = build_system_architecture(items)
        self.assertEqual(items[0]["primary_layer"], "unassigned")
        self.assertEqual(architecture["summary"]["unassigned_components"], 1)
        self.assertEqual(architecture["unassigned_components"], ["Unknown future component"])

    def test_cross_cutting_controls_attach_to_existing_components_without_new_layer(self) -> None:
        items = annotate_components([
            {"component":{"en":"Wide-search simplification-challenge ideation"},"status":"running"},
            {"component":{"en":"Protocol-validity auditor + research-system replay benchmark"},"status":"running"},
            {"component":{"en":"Literature retrieval + Evidence Integrity layer"},"status":"running"},
        ])
        architecture = build_system_architecture(items, build_methodology_controls_state())
        self.assertEqual(architecture["summary"]["reader_chapters"], 10)
        self.assertEqual(architecture["summary"]["reader_stage_coverage"], 21)
        self.assertEqual(architecture["summary"]["reader_stage_missing"], 0)
        self.assertEqual(architecture["summary"]["reader_stage_duplicates"], 0)
        self.assertEqual(architecture["summary"]["reader_stage_extra"], 0)
        self.assertEqual(set(architecture["stage_group_map"]), {row["key"] for row in TEMPORAL_FLOW})
        self.assertEqual(architecture["summary"]["cross_cutting_controls"], 3)
        self.assertEqual(architecture["summary"]["orphan_cross_cutting_controls"], 0)
        self.assertEqual(architecture["summary"]["functional_layers"], 6)


if __name__ == "__main__":
    unittest.main()
