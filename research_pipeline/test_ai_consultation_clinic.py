from __future__ import annotations

import unittest

from .ai_consultation_clinic import build_ai_consultation_clinic_state, validate_ai_consultation_clinic_state


class AIConsultationClinicTest(unittest.TestCase):
    def setUp(self) -> None:
        self.state = build_ai_consultation_clinic_state()

    def test_five_non_authoritative_checkpoints(self) -> None:
        self.assertEqual(validate_ai_consultation_clinic_state(self.state), [])
        self.assertEqual(self.state["summary"]["checkpoints"], 5)
        self.assertEqual(self.state["summary"]["pre_gpu_checkpoints"], 3)
        self.assertEqual(self.state["summary"]["ai_authoritative_checkpoints"], 0)
        self.assertFalse(self.state["policy"]["ai_vote_can_authorize_gpu"])
        self.assertFalse(self.state["policy"]["ai_vote_can_emit_method_pass_fail"])

    def test_panel_is_independent_and_findings_compile_to_controls(self) -> None:
        self.assertTrue(self.state["panel"]["independent_first_round"])
        self.assertTrue(self.state["panel"]["failed_or_empty_model_response_is_missing_not_pass"])
        self.assertTrue(self.state["policy"]["high_risk_findings_must_be_compiled_into_machine_checks"])
        for checkpoint in self.state["checkpoints"]:
            self.assertTrue(checkpoint["required_outputs"])
            self.assertTrue(checkpoint["compile_to"])


if __name__ == "__main__":
    unittest.main()
