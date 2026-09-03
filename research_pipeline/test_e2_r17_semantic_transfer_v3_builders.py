from __future__ import annotations

import random
import unittest

from research_pipeline.e2_r17_controlled_suite_schema import new_book
from research_pipeline.e2_r17_semantic_transfer_v3_builders import (
    BINDING,
    BUILDERS,
    EXPECTED_GENERATION_RUNTIME,
    PROCEDURAL,
    SEMANTIC_TYPES,
    SKELETONS,
    generation_runtime_fingerprint,
    observable_route,
    visible_router_features,
)


class SemanticTransferV3BuildersTest(unittest.TestCase):
    def test_all_crossed_cells_route_from_instruction_only(self) -> None:
        for skeleton in SKELETONS:
            for semantic in SEMANTIC_TYPES:
                with self.subTest(skeleton=skeleton, semantic=semantic):
                    wb = new_book(f"test|{skeleton}")
                    instruction, answer_position, _ = BUILDERS[skeleton](wb, random.Random(17), 2, 2, semantic)
                    features = visible_router_features(instruction)
                    self.assertEqual(answer_position, "Result!B2:B4")
                    if semantic == PROCEDURAL:
                        self.assertEqual(observable_route(instruction), "MRW4")
                        self.assertGreaterEqual(features["visible_operation_clause_count"], 3)
                        self.assertLessEqual(features["visible_binding_alternative_count"], 1)
                    else:
                        self.assertEqual(observable_route(instruction), "WIN-C")
                        self.assertGreaterEqual(features["visible_binding_alternative_count"], 2)
                        self.assertLessEqual(features["visible_operation_clause_count"], 2)
                    wb.close()

    def test_generation_runtime_fingerprint_matches_frozen_stack(self) -> None:
        self.assertEqual(generation_runtime_fingerprint(), EXPECTED_GENERATION_RUNTIME)

    def test_router_api_has_no_hidden_metadata_inputs(self) -> None:
        # The callable contract is deliberately instruction-only. This guards
        # against later family/template/semantic lookup being added silently.
        import inspect

        self.assertEqual(list(inspect.signature(observable_route).parameters), ["instruction"])
        self.assertEqual(list(inspect.signature(visible_router_features).parameters), ["instruction"])

    def test_semantic_pair_uses_same_pre_branch_rng_prefix(self) -> None:
        # For each skeleton, running the common generator from the same RNG
        # seed must consume the same pre-branch workbook generation. The suite
        # builder performs the stronger byte-identical init-XLSX assertion.
        for skeleton in SKELETONS:
            with self.subTest(skeleton=skeleton):
                books = []
                for semantic in (PROCEDURAL, BINDING):
                    wb = new_book(f"pair|{skeleton}")
                    BUILDERS[skeleton](wb, random.Random(23), 1, 1, semantic)
                    # Compare all non-Result cell values. Result differs by
                    # design before the suite builder blanks answer cells.
                    payload = []
                    for ws in wb.worksheets:
                        if ws.title == "Result":
                            continue
                        payload.append((ws.title, tuple(tuple(cell.value for cell in row) for row in ws.iter_rows())))
                    books.append(tuple(payload))
                    wb.close()
                self.assertEqual(books[0], books[1])


if __name__ == "__main__":
    unittest.main()
