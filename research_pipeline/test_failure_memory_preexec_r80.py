from __future__ import annotations
import json, pathlib, unittest

from research_pipeline import failure_memory_preexec_r80 as r80

ROOT = pathlib.Path(__file__).resolve().parents[1]
G = ROOT / "generated"


def load(name: str):
    return json.loads((G / name).read_text(encoding="utf-8"))


class FailureMemoryPreexecR80Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = load("d2-failure-memory-provenance-r72-semantic-control-r3-protocol.json")
        cls.panel = load("d2-failure-memory-provenance-r68-semantic-control-panel.json")
        cls.identity = load("d2-failure-memory-provenance-r80-strong-model-identity.json")
        cls.matching = load("d2-failure-memory-provenance-r80-matched-control-rule.json")
        cls.scale = load("d2-failure-memory-provenance-r80-strong-model-scale-freeze.json")
        cls.auth = load("d2-failure-memory-provenance-r80-r72-r73-execution-authority.json")

    def test_receipts(self):
        self.assertTrue(r80.valid(self.protocol))
        self.assertTrue(r80.valid(self.panel))
        self.assertTrue(r80.valid(self.matching))
        self.assertTrue(r80.valid(self.scale))
        self.assertTrue(r80.valid(self.auth))

    def test_strong_model_frozen_before_outcome(self):
        self.assertEqual(self.identity["family"], "Qwen3.5-27B")
        self.assertGreater(self.identity["bytes"], 50_000_000_000)
        self.assertEqual(self.identity["model_calls_observed"], 0)
        self.assertEqual(self.scale["task_outcomes_observed"], 0)
        self.assertTrue(self.scale["no_scale_execution_authority_here"])

    def test_matching_is_outcome_blind_and_complete(self):
        self.assertEqual(len(self.matching["task_covariates"]), 66)
        self.assertEqual(len(self.matching["pair_cost_matrix_rows"]), 66 * 65)
        self.assertTrue(self.matching["control_selection_algorithm"]["outcome_fields_forbidden_in_cost"])
        forbidden = {"terminal_success", "P_terminal_success", "T_terminal_success", "effect", "discordant"}
        for row in self.matching["task_covariates"]:
            self.assertFalse(forbidden & set(row))

    def test_selector_is_deterministic_one_to_one(self):
        ids = [x["task_id"] for x in self.matching["task_covariates"]]
        d = ids[:3]
        c = ids[3:15]
        a = r80.select_controls_from_frozen_covariates(self.matching, d, c)
        b = r80.select_controls_from_frozen_covariates(self.matching, d, c)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 3)
        self.assertEqual(len({x["matched_control_task_id"] for x in a}), 3)
        with self.assertRaises(RuntimeError):
            r80.select_controls_from_frozen_covariates(self.matching, ids[:5], ids[5:7])

    def test_execution_authority_is_narrow(self):
        a = self.auth["authority"]
        self.assertTrue(a["qwen_execution"])
        self.assertTrue(a["llama_execution"])
        self.assertFalse(a["analysis"])
        self.assertTrue(a["gpu"])
        self.assertFalse(a["PSMG"])
        self.assertFalse(a["L3"])
        self.assertFalse(a["paper_claim_change"])
        self.assertFalse(self.auth["strong_model_scale_execution"])

    def test_path_migration_only(self):
        r = self.auth["execution_realization"]
        self.assertTrue(r["path_migration_only"])
        self.assertFalse(r["scientific_treatment_change"])
        self.assertEqual(r["clean_source_checkout"], "/data/wyt/b1-r77-clean-memrl")


if __name__ == "__main__":
    unittest.main()
