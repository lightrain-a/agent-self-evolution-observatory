from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .config import PROJECT_ROOT
from .paper_first_agent_safety_current_projection import (
    CURRENT_CANDIDATE_STAGE,
    CURRENT_STAGE,
    DEFAULT_MEMORY_BUNDLE,
    DEFAULT_PROGRAM_JSON,
    DEFAULT_RECEIPT,
    project_agent_safety_current_state,
    validate_current_agent_safety_projection,
    write_current_agent_safety_projection,
)
from .paper_first_agent_safety_program_state import validate_agent_safety_program_state


class AgentSafetyCurrentProjectionTest(unittest.TestCase):
    def _base(self) -> dict:
        return json.loads(DEFAULT_PROGRAM_JSON.read_text(encoding="utf-8"))

    def test_final_receipt_supersedes_only_current_status(self) -> None:
        state = project_agent_safety_current_state(
            self._base(),
            generated_at="2026-08-20T12:00:00+00:00",
        )
        self.assertEqual(state["current_stage"], CURRENT_STAGE)
        self.assertEqual(state["candidate_stage"], CURRENT_CANDIDATE_STAGE)
        self.assertEqual(state["historical_projection"]["current_stage"], "CURRENT_SAFETY_SUPPORT_STOP")
        self.assertTrue(state["historical_projection"]["historical_only"])
        self.assertTrue(state["qualification"]["historical_only"])
        self.assertTrue(state["support_realization_adjudication"]["historical_only"])
        self.assertEqual(validate_current_agent_safety_projection(state), [])
        self.assertEqual(validate_agent_safety_program_state(state), [])

    def test_claim_boundary_and_evidence_counts_are_exact(self) -> None:
        state = project_agent_safety_current_state(self._base())
        evidence = state["future_evidence"]
        self.assertTrue(evidence["paper_evidence_ready"])
        self.assertEqual(
            evidence["claim_adjudication"]["supported_status"],
            "SUPPORTED_NARROWLY",
        )
        self.assertEqual(
            evidence["claim_adjudication"]["causal_hold_status"],
            "HOLD_METHOD_IDENTIFICATION",
        )
        self.assertEqual(
            evidence["static_current_safety"],
            {
                "selected_states": 4,
                "qualification_episodes": 12,
                "qualification_violations": 0,
            },
        )
        self.assertEqual(evidence["future_first_violation"]["future_episodes"], 36)
        self.assertEqual(evidence["future_first_violation"]["future_violation_episodes"], 11)
        self.assertEqual(evidence["future_first_violation"]["branches_with_first_violation"], 8)
        self.assertEqual(evidence["future_first_violation"]["states_with_first_violation"], 3)
        self.assertEqual(len(evidence["not_supported_claims"]), 4)
        self.assertFalse(evidence["additional_behavior_execution_authorized"])

    def test_reopen_condition_is_method_hold_not_execution_authority(self) -> None:
        state = project_agent_safety_current_state(self._base())
        reopen = state["future_evidence"]["reopen_condition"]
        self.assertTrue(
            reopen["condition"].startswith(
                "Separate persistent update effect from held-out schedule effect"
            )
        )
        self.assertFalse(reopen["automatic_reopen"])
        self.assertFalse(reopen["new_behavior_execution_authorized"])
        self.assertFalse(state["execution_authorized"])
        self.assertFalse(state["authority"]["heldout_future_probe_execution"])
        self.assertEqual(
            state["next_gate"]["name"],
            "SEPARATE_PERSISTENT_UPDATE_FROM_HELDOUT_SCHEDULE",
        )

    def test_generic_receipt_compiler_and_control_design_are_fail_closed(self) -> None:
        state = project_agent_safety_current_state(self._base())
        compiled = state["receipt_compiler_projection"]
        control = state["reopen_control_design"]
        self.assertEqual(
            compiled["compiler_receipt"]["compiler"],
            "generic-evidence-receipt-current-state",
        )
        self.assertFalse(compiled["execution_authorized"])
        self.assertFalse(compiled["scientific_authority"])
        self.assertEqual(
            control["status"],
            "DESIGN_COMPILED_GATES_UNSATISFIED",
        )
        self.assertEqual(control["requirements_passed"], 2)
        self.assertEqual(control["requirements_on_hold"], 5)
        self.assertFalse(control["automatic_authorization"])
        self.assertFalse(control["execution_authorized"])
        self.assertFalse(control["gpu_authorized"])
        self.assertEqual(
            state["next_gate"]["control_design_sha256"],
            control["design_sha256"],
        )

        mutated = json.loads(json.dumps(state))
        mutated["reopen_control_design"]["execution_authorized"] = True
        self.assertTrue(validate_current_agent_safety_projection(mutated))

    def test_projection_is_idempotent(self) -> None:
        first = project_agent_safety_current_state(
            self._base(),
            generated_at="2026-08-20T12:00:00+00:00",
        )
        second = project_agent_safety_current_state(
            first,
            generated_at="2026-08-20T12:00:00+00:00",
        )
        self.assertEqual(first, second)

    def test_validator_rejects_stale_current_stage(self) -> None:
        state = project_agent_safety_current_state(self._base())
        state["current_stage"] = "CURRENT_SAFETY_SUPPORT_STOP"
        self.assertIn(
            "current Agent Safety stage is not derived from final paper evidence",
            validate_current_agent_safety_projection(state),
        )

    def test_writer_emits_json_and_js_from_same_projection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            json_path = root / "state.json"
            js_path = root / "state.js"
            state = write_current_agent_safety_projection(
                base_state_path=DEFAULT_PROGRAM_JSON,
                receipt_path=DEFAULT_RECEIPT,
                memory_bundle_path=DEFAULT_MEMORY_BUNDLE,
                json_path=json_path,
                js_path=js_path,
                generated_at="2026-08-20T12:00:00+00:00",
            )
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), state)
            self.assertTrue(js_path.read_text(encoding="utf-8").startswith(
                "window.AGENT_SAFETY_PROGRAM_STATE = "
            ))


if __name__ == "__main__":
    unittest.main()
