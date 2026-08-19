from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_f0_contract import (
    BRANCH_PROBES,
    BUDGET,
    QUAL,
    STATE_SHA,
    append_update,
    build_plan,
    qualification_seed,
    write_zero_model_ledger,
)


class AgentSafetyR9F0ContractTest(unittest.TestCase):
    def fixture_bundle(self, root: Path) -> dict:
        states = {}
        for sid in STATE_SHA:
            path = root / f"{sid}.txt"
            path.write_text(f"Query: base {sid}\n<action>\nclick('1')\n</action>\n", encoding="utf-8")
            states[sid] = {"state_id": sid, "site_stratum": sid.rsplit('-', 1)[0], "path": str(path), "sha256": STATE_SHA[sid]}
        future = [
            {"step": 1, "sha256": "a" * 64, "text": "Query: future one\n"},
            {"step": 2, "sha256": "b" * 64, "text": "Query: future two\n"},
            {"step": 3, "sha256": "c" * 64, "text": "Query: future three\n"},
        ]
        return {"states": states, "future_units": future}

    def test_qualification_seeds_are_predeclared_and_state_independent(self) -> None:
        seeds = [qualification_seed(bid) for bid in QUAL]
        self.assertEqual(len(set(seeds)), 3)
        self.assertTrue(all(0 <= seed <= 0x7FFFFFFF for seed in seeds))
        self.assertEqual(seeds, [qualification_seed(bid) for bid in QUAL])

    def test_future_append_serializer_is_cumulative_and_stable(self) -> None:
        first = append_update("base\n", "unit1\n")
        second = append_update(first, "unit2\n")
        self.assertEqual(first, "base\n\nunit1\n")
        self.assertEqual(second, "base\n\nunit1\n\nunit2\n")

    def test_write_ahead_plan_is_exactly_12_plus_36_and_never_selects_replacements(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan = build_plan(self.fixture_bundle(Path(td)))
        self.assertEqual(len(plan["episodes"]), 48)
        self.assertEqual(sum(row["phase"] == "qualification" for row in plan["episodes"]), 12)
        self.assertEqual(sum(row["phase"] == "future" for row in plan["episodes"]), 36)
        self.assertEqual(plan["budget"], BUDGET)
        self.assertTrue(plan["replacement_state_after_qualification_outcomes_forbidden"])
        self.assertEqual(plan["agent_max_retry"], 1)
        self.assertEqual(plan["openai_client_max_retries"], 0)
        self.assertEqual(plan["browser_max_steps"], 4)
        for row in plan["episodes"]:
            self.assertEqual(row["max_agent_model_calls"], 4)
            self.assertEqual(row["classifier_model_evaluations"], 1)
        for seed, probes in BRANCH_PROBES.items():
            observed = [row["behavior_id"] for row in plan["episodes"] if row.get("branch_seed") == int(seed)]
            self.assertEqual(observed, probes * 4)

    def test_zero_model_ledger_does_not_claim_execution(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = self.fixture_bundle(root)
            plan = build_plan(bundle)
            receipt = write_zero_model_ledger(bundle, plan, root / "out")
            self.assertEqual(receipt["status"], "READY_R9_F0_ZERO_MODEL_LEDGER")
            self.assertEqual((receipt["provider_calls_executed"], receipt["gpu_calls_executed"], receipt["harmful_behavior_executions"]), (0, 0, 0))
            self.assertFalse(receipt["execution_started"])
            self.assertTrue((root / "out" / "episode-plan.json").is_file())


if __name__ == "__main__":
    unittest.main()
