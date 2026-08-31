from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_pipeline.asset_first_stri_reasoningbank_p1_core import write_json
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_adjudicate import (
    PASS_DECISION, adjudicate,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runner import INDEX
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import load_payload


class ReasoningBankP1Q10AdjudicateTest(unittest.TestCase):
    def paths(self, root: Path) -> tuple[Path, Path, Path, Path]:
        return (
            root / "adjudication.json",
            root / "manifest.json",
            root / "differential.json",
            root / "memory.json",
        )

    def test_terminal_index_qualifies_outcome_blind(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output, manifest, differential, memory = self.paths(root)
            result = adjudicate(
                INDEX, output, manifest, differential, memory
            )
            payload = load_payload(output)
        self.assertTrue(result["implementation_qualified"])
        self.assertEqual(result["decision"], PASS_DECISION)
        self.assertTrue(all(payload["qualification_checks"].values()))
        self.assertEqual(
            payload["descriptive_task_outcomes"]["resolved_count"], 10
        )
        self.assertFalse(
            payload["descriptive_task_outcomes"][
                "used_for_implementation_qualification"
            ]
        )
        self.assertFalse(
            payload["authorization"]["full_p1_execution_authorized"]
        )
        self.assertTrue(
            payload["authorization"]["full_p1_preregistration_authorized"]
        )

    def test_partial_index_holds_without_using_task_outcomes(self) -> None:
        partial = load_payload(INDEX)
        partial["execution_complete"] = False
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            index = root / "index.json"
            write_json(index, partial)
            output, manifest, differential, memory = self.paths(root)
            result = adjudicate(
                index, output, manifest, differential, memory
            )
            payload = load_payload(output)
        self.assertFalse(result["implementation_qualified"])
        self.assertFalse(
            payload["qualification_checks"][
                "all_ten_persisted_once_in_frozen_order"
            ]
        )
        self.assertFalse(
            payload["authorization"]["full_p1_preregistration_authorized"]
        )

    def test_refuses_to_overwrite_canonical_style_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output, manifest, differential, memory = self.paths(root)
            output.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "refusing to overwrite"):
                adjudicate(
                    INDEX, output, manifest, differential, memory
                )


if __name__ == "__main__":
    unittest.main()
