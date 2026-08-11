from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .p0_admission import build_p0_admission_state, validate_p0_admission_state, write_p0_admission_state


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
        self.assertEqual(self.state["summary"]["execution_authorized"], 0)
        for idea_id in ("replicated-effect-memory-gate","cross-task-effect-transport-certificate"):
            row=next(card for card in self.state["cards"] if card["idea_id"]==idea_id)
            self.assertFalse(row["execution_preflight"]["execution_authorized"])
            self.assertEqual(row["execution_preflight"]["blockers"],["economy-gate","p0-complete-second-model-hold"])
        self.assertEqual(self.state["summary"]["economy_ready"], 0)
        self.assertEqual(self.state["economy_gate"]["summary"]["matched_simplification_stops"], 12)
        self.assertEqual(self.state["economy_gate"]["summary"]["substrate_stops"], 4)
        self.assertEqual(self.state["summary"]["execution_blocked_or_pending"], 20)
        transitioned = [row for row in self.state["cards"] if (row.get("p0_entry") or {}).get("date") == "2026-08-11"]
        self.assertEqual(len(transitioned), 16)
        self.assertTrue(all(not row["execution_preflight"]["execution_authorized"] for row in transitioned))
        self.assertTrue(all(row["setup"]["max_gpus"] == 1 and row["setup"]["gpu_hours_cap"] <= 12 for row in transitioned))
        b10=next(row for row in transitioned if row["idea_id"]=="constraint-complete-typed-memory-order-logic")
        self.assertEqual(b10["execution_preflight"]["blockers"],["economy-gate","p0-stop-await-human-review"])
        self.assertEqual(b10["execution_preflight"]["gpu0"]["status"],"stop-matched-nary-equivalent")
        a6=next(row for row in transitioned if row["idea_id"]=="active-causal-minimal-rollback")
        self.assertEqual(a6["execution_preflight"]["blockers"],["economy-gate","p0-stop-await-human-review"])
        self.assertEqual(a6["execution_preflight"]["gpu0"]["status"],"stop-matched-group-testing-equivalent")
        e3=next(row for row in transitioned if row["idea_id"]=="bounded-probe-api-transition-operator")
        self.assertEqual(e3["execution_preflight"]["blockers"],["economy-gate","p0-stop-await-human-review"])
        self.assertEqual(e3["execution_preflight"]["gpu0"]["status"],"stop-stateful-deterministic-pex-ceiling")
        e4=next(row for row in transitioned if row["idea_id"]=="interventional-permission-triage-under-ceiling")
        self.assertEqual(e4["execution_preflight"]["blockers"],["economy-gate","p0-stop-await-human-review"])
        self.assertEqual(e4["execution_preflight"]["gpu0"]["status"],"stop-matched-boolean-rule-equivalent")

    def test_public_admission_compacts_economy_compiler_details(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); write_p0_admission_state(root/'state.json',root/'state.js'); public=json.loads((root/'state.json').read_text())
        self.assertEqual(public['summary']['economy_ready'],0)
        for card in public['cards']:
            econ=card['execution_preflight']['economy_gate']
            for gate in econ['gates']:
                self.assertNotIn('evidence',gate)


if __name__ == "__main__":
    unittest.main()
