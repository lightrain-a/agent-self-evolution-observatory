from __future__ import annotations

import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_gemma4_development_adjudication import (
    FAILURE_LAYER,
    STATUS,
    STOP_CLASS,
    build_development_stop,
    validate_development_stop,
)


class Gemma4DevelopmentAdjudicationTest(unittest.TestCase):
    def test_current_development_is_interface_realization_stop(self) -> None:
        state = build_development_stop(
            contract_path=Path("generated/agent-safety-r9-gemma4-benign-gate-v3-preregistration-20260819.json"),
            gate0_path=Path("generated/agent-safety-r9-gemma4-gate0-pass-20260819.json"),
            development_root=Path("/data/wyt/agent-safety-discovery-20260818/shadow-agent-safety-20260818-r9/gemma4-backbone-v3-20260819/development"),
        )
        self.assertEqual(validate_development_stop(state), [])
        self.assertEqual(state["status"], STATUS)
        self.assertEqual(state["stop_class"], STOP_CLASS)
        self.assertEqual(state["failure_layer"], FAILURE_LAYER)
        self.assertEqual(state["development"]["call_cap_inconclusive_probe_ids"], [12])
        self.assertEqual(state["development"]["classifier_evaluations"], 0)
        self.assertFalse(state["principle_falsified"])
        self.assertTrue(all(value is False for value in state["authority"].values()))

    def test_validator_rejects_partial_panel_harmbench_promotion(self) -> None:
        state = build_development_stop(
            contract_path=Path("generated/agent-safety-r9-gemma4-benign-gate-v3-preregistration-20260819.json"),
            gate0_path=Path("generated/agent-safety-r9-gemma4-gate0-pass-20260819.json"),
            development_root=Path("/data/wyt/agent-safety-discovery-20260818/shadow-agent-safety-20260818-r9/gemma4-backbone-v3-20260819/development"),
        )
        state["development"]["classifier_evaluations"] = 2
        self.assertIn("Gemma4 development stop evidence drift", validate_development_stop(state))


if __name__ == "__main__":
    unittest.main()
