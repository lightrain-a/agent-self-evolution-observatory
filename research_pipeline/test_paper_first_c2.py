from __future__ import annotations

import unittest

from .paper_first_c2_contract import build_c2_contract
from .paper_first_c2_local import adjudicate_c2_outcomes, _repeat_equal, _semantic_contract


class PaperFirstC2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_c2_contract()

    def test_contract_freezes_strict_ten_and_no_scaleup(self) -> None:
        contract = self.contract
        self.assertEqual(len(contract["strict_units"]), 10)
        self.assertEqual(len(contract["excluded_units"]), 1)
        self.assertEqual(contract["frozen_gate"]["go"]["valid_units"], 10)
        self.assertEqual(contract["frozen_gate"]["go"]["minimum_nonzero_tau_units"], 9)
        self.assertEqual(contract["frozen_gate"]["go"]["minimum_parent_sign_concordant_units"], 9)
        self.assertEqual(contract["frozen_gate"]["go"]["parent_sign_concordance_role"], "binding GO gate from the conservative reviewer intersection")
        self.assertTrue(contract["frozen_gate"]["go"]["same_memory_cross_context_sign_reversal_required"])
        self.assertTrue(contract["post_c2"]["C3_locked"])
        self.assertFalse(contract["post_c2"]["full_experiment_authorized"])
        self.assertEqual(contract["runtime"]["policy_mode"], "react-family")
        self.assertEqual(contract["runtime"]["memory_patch"], "")
        self.assertEqual(contract["runtime"]["max_total_steps"], 50)

    def _perfect_outcomes(self):
        inv = {row["unit_id"]: row for row in __import__("json").loads(
            __import__("pathlib").Path(__file__).with_name("paper_first_c2_support_inventory_20260812.json").read_text(encoding="utf-8")
        )["units"]}
        rows = []
        for unit_id in self.contract["strict_units"]:
            row = inv[unit_id]
            tau = int(row["controlled_delta"])
            rows.append({
                "unit_id": unit_id,
                "memory_id": row["memory_id"],
                "target_family": row["target_family"],
                "parent_controlled_delta": int(row["controlled_delta"]),
                "tau_A": tau,
                "nonzero_tau": tau != 0,
                "parent_sign_concordant": True,
            })
        return rows

    def test_exact_go_rule(self) -> None:
        result = adjudicate_c2_outcomes(self.contract, 10, self._perfect_outcomes())
        self.assertEqual(result["decision"], "C2_GO_RETURN_TO_PAPER_ADJUDICATION")
        self.assertEqual(result["metrics"]["nonzero_tau_units"], 10)
        self.assertEqual(result["metrics"]["parent_sign_concordant_units"], 10)
        self.assertTrue(result["metrics"]["same_memory_cross_context_sign_reversal"])

    def test_any_precheck_loss_stops(self) -> None:
        result = adjudicate_c2_outcomes(self.contract, 9, self._perfect_outcomes())
        self.assertEqual(result["decision"], "C2_STOP_CONTROLLED_ACTION_MECHANISM_NOT_SUPPORTED")

    def test_only_eight_nonzero_units_stop(self) -> None:
        rows = self._perfect_outcomes()
        protected_memory = self.contract["frozen_gate"]["go"]["sign_flip_memory_id"]
        changed = 0
        for row in rows:
            if row["memory_id"] == protected_memory:
                continue
            row["tau_A"] = 0
            row["nonzero_tau"] = False
            row["parent_sign_concordant"] = False
            changed += 1
            if changed >= 2:
                break
        result = adjudicate_c2_outcomes(self.contract, 10, rows)
        self.assertEqual(result["metrics"]["nonzero_tau_units"], 8)
        self.assertEqual(result["decision"], "C2_STOP_CONTROLLED_ACTION_MECHANISM_NOT_SUPPORTED")

    def test_only_eight_parent_sign_concordant_units_stop(self) -> None:
        rows = self._perfect_outcomes()
        flip_memory = self.contract["frozen_gate"]["go"]["sign_flip_memory_id"]
        changed = 0
        for row in rows:
            if row["memory_id"] == flip_memory:
                continue
            row["parent_sign_concordant"] = False
            changed += 1
            if changed >= 2:
                break
        result = adjudicate_c2_outcomes(self.contract, 10, rows)
        self.assertEqual(result["metrics"]["parent_sign_concordant_units"], 8)
        self.assertEqual(result["decision"], "C2_STOP_CONTROLLED_ACTION_MECHANISM_NOT_SUPPORTED")

    def test_missing_context_reversal_stops(self) -> None:
        rows = self._perfect_outcomes()
        flip_memory = self.contract["frozen_gate"]["go"]["sign_flip_memory_id"]
        changed = next(row for row in rows if row["memory_id"] == flip_memory and row["parent_controlled_delta"] < 0)
        changed["tau_A"] = 1
        changed["parent_sign_concordant"] = False
        result = adjudicate_c2_outcomes(self.contract, 10, rows)
        self.assertFalse(result["metrics"]["same_memory_cross_context_sign_reversal"])
        self.assertEqual(result["decision"], "C2_STOP_CONTROLLED_ACTION_MECHANISM_NOT_SUPPORTED")

    def test_contract_resume_ignores_generated_at_only(self) -> None:
        left = {"generated_at": "t1", "paper_id": "x", "gate": {"k": 1}}
        right = {"generated_at": "t2", "paper_id": "x", "gate": {"k": 1}}
        changed = {"generated_at": "t2", "paper_id": "x", "gate": {"k": 2}}
        self.assertEqual(_semantic_contract(left), _semantic_contract(right))
        self.assertNotEqual(_semantic_contract(left), _semantic_contract(changed))

    def test_repeat_equality_is_exact(self) -> None:
        trace = {
            "success": 1, "score": 1.0, "steps": 7, "terminated": True,
            "every_action_admissible": True, "forced_action_admissible": True,
            "post_forced_has_support": True, "invalid_choice_count": 0,
            "action_sequence_sha256": "a", "observation_sequence_sha256": "b", "branchpoint_sha256": "c",
        }
        self.assertTrue(_repeat_equal(trace, dict(trace)))
        changed = dict(trace); changed["action_sequence_sha256"] = "different"
        self.assertFalse(_repeat_equal(trace, changed))


if __name__ == "__main__":
    unittest.main()
