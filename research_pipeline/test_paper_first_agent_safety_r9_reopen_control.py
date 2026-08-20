from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_reopen_control import (
    compile_reopen_control_design,
    validate_reopen_control_design,
    write_reopen_control_design,
)


class AgentSafetyR9ReopenControlTest(unittest.TestCase):
    def test_design_is_compiled_but_not_authorized(self) -> None:
        design = compile_reopen_control_design()
        self.assertEqual(design["status"], "DESIGN_COMPILED_GATES_UNSATISFIED")
        self.assertEqual(len(design["frozen_design"]["branch_slots"]), 12)
        self.assertEqual(design["authorization_gate"]["passed"], 2)
        self.assertEqual(design["authorization_gate"]["holds"], 5)
        self.assertFalse(design["execution_authorized"])
        self.assertFalse(design["authorization_gate"]["gpu_authorized"])
        self.assertFalse(any(design["queue_mutation"].values()))
        self.assertEqual(validate_reopen_control_design(design), [])

    def test_design_requires_exact_schedule_and_existing_no_update_surface(self) -> None:
        design = compile_reopen_control_design()
        by_id = {
            row["requirement_id"]: row
            for row in design["authorization_gate"]["requirements"]
        }
        self.assertEqual(
            by_id["EXACT-HELDOUT-SCHEDULE-MANIFEST-MATERIALIZED"]["status"],
            "HOLD",
        )
        self.assertEqual(
            by_id["EXISTING-NO-UPDATE-CONTROL-SURFACE-VERIFIED"]["status"],
            "HOLD",
        )
        self.assertTrue(
            design["frozen_design"]["control"]["update_is_only_allowed_changed_factor"]
        )

    def test_design_preserves_narrow_claim_boundary(self) -> None:
        design = compile_reopen_control_design()
        analysis = design["pre_registered_analysis"]
        self.assertFalse(analysis["population_hazard_estimate"])
        self.assertFalse(analysis["automatic_claim_upgrade"])
        self.assertIn(
            "Independent adjudication required",
            analysis["decision_rules"][2]["scientific_effect"],
        )

    def test_authority_mutation_is_detected(self) -> None:
        design = compile_reopen_control_design()
        design["authorization_gate"]["execution_authorized"] = True
        self.assertIn(
            "R9 control design leaked execution authority",
            validate_reopen_control_design(design),
        )

    def test_writer_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "control.json"
            design = write_reopen_control_design(path)
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                design,
            )


if __name__ == "__main__":
    unittest.main()
