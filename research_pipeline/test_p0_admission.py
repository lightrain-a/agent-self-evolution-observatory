from __future__ import annotations

import unittest

from .p0_admission import build_p0_admission_state, validate_p0_admission_state


class P0AdmissionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_p0_admission_state()

    def test_all_active_directions_enter_p0_with_complete_settings(self) -> None:
        self.assertEqual(validate_p0_admission_state(self.state), [])
        self.assertEqual(self.state["summary"]["active_p0"], 20)
        self.assertEqual(self.state["summary"]["admitted"], 20)
        self.assertEqual(self.state["summary"]["transitioned_from_p0_ready"], 16)
        self.assertEqual(self.state["summary"]["settings_complete"], 20)

    def test_codes_are_stable_and_standalones_are_numbered(self) -> None:
        by_id = {row["idea_id"]: row for row in self.state["cards"]}
        self.assertEqual(by_id["active-causal-minimal-rollback"]["code"], "A-6")
        self.assertEqual(by_id["counterfactual-evolution-decision-controller"]["code"], "A-7")
        self.assertEqual(by_id["replicated-effect-memory-gate"]["code"], "B-8")
        self.assertEqual(by_id["cross-task-effect-transport-certificate"]["code"], "B-9")
        self.assertEqual(by_id["constraint-complete-typed-memory-order-logic"]["code"], "B-10")
        self.assertEqual(by_id["bounded-probe-api-transition-operator"]["code"], "E-3")
        self.assertEqual(by_id["interventional-permission-triage-under-ceiling"]["code"], "E-4")

    def test_p0_entry_does_not_fake_execution_authorization(self) -> None:
        self.assertEqual(self.state["summary"]["execution_authorized"], 2)
        self.assertEqual(self.state["summary"]["execution_blocked_or_pending"], 18)
        transitioned = [row for row in self.state["cards"] if (row.get("p0_entry") or {}).get("date") == "2026-08-11"]
        self.assertEqual(len(transitioned), 16)
        self.assertTrue(all(not row["execution_preflight"]["execution_authorized"] for row in transitioned))
        self.assertTrue(all(row["setup"]["max_gpus"] == 1 and row["setup"]["gpu_hours_cap"] <= 12 for row in transitioned))


if __name__ == "__main__":
    unittest.main()
