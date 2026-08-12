from __future__ import annotations

import unittest

from .methodology_controls import build_methodology_controls_state
from .system_architecture import (
    COMPONENT_BINDINGS,
    FUNCTIONAL_LAYERS,
    TEMPORAL_FLOW,
    annotate_components,
    build_system_architecture,
)


class SystemArchitectureTest(unittest.TestCase):
    def test_temporal_flow_is_single_ordered_paper_first_lifecycle(self) -> None:
        keys = [row["key"] for row in TEMPORAL_FLOW]
        self.assertEqual(len(keys), 11)
        self.assertEqual(keys[:5], ["scope", "evidence", "novelty", "method", "experiment-blueprint"])
        self.assertEqual(keys[5:9], ["economy-compile", "local-validation", "method-freeze", "full-experiment"])
        self.assertEqual(keys[-2:], ["paper-evidence", "learn"])
        self.assertEqual([row["index"] for row in TEMPORAL_FLOW], list(range(1, 12)))

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
        self.assertEqual(len(COMPONENT_BINDINGS), 27)
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
        self.assertEqual(architecture["summary"]["cross_cutting_controls"], 3)
        self.assertEqual(architecture["summary"]["orphan_cross_cutting_controls"], 0)
        self.assertEqual(architecture["summary"]["functional_layers"], 6)


if __name__ == "__main__":
    unittest.main()
