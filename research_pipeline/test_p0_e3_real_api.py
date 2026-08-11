from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT
from .p0_e3_real_api import TARGETS, _prediction_hash


class P0E3RealApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state=json.loads((PROJECT_ROOT/"generated"/"p0-e3-real-api.json").read_text(encoding="utf-8"))

    def test_hidden_truth_is_not_available_to_predictor(self) -> None:
        self.assertTrue(all(len(row)==3 for target in TARGETS.values() for row in target["hidden"]))
        self.assertTrue(self.state["design"]["hidden_outcomes_sealed_until_prediction_hash"])
        self.assertEqual(_prediction_hash(self.state["deterministic_pex_predictions"]),self.state["prediction_sha256_before_hidden"])
        self.assertEqual(self.state["source_rule_quality"]["passed"],5)
        self.assertTrue(self.state["source_rule_quality"]["pass"])
        self.assertTrue(all(row["pass"] for row in self.state["probe_contracts"].values()))

    def test_real_read_only_substrate_is_reducible_without_overclaiming_stop(self) -> None:
        m=self.state["metrics"]
        self.assertEqual(m["logical_target_probes"],12)
        self.assertEqual((m["correct_hidden"],m["total_hidden"]),(12,12))
        self.assertEqual(m["family_accuracy"],{"gitlab":1.0,"codeberg":1.0})
        self.assertEqual(self.state["decision"],"READ_ONLY_SUBSTRATE_REDUCIBLE")
        self.assertTrue(self.state["deterministic_baseline_ceiling"])
        self.assertFalse(self.state["learned_arm_run"])
        self.assertFalse(self.state["standalone_claim_stop_authorized"])
        self.assertTrue(self.state["design"]["read_only_public_api_scope"])
        self.assertIn("stateful",self.state["next_action"].lower())


if __name__=="__main__": unittest.main()
