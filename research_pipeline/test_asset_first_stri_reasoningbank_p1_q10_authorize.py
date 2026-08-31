from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_pipeline.asset_first_stri_reasoningbank_p1_core import write_json
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_authorize import (
    generate_authority,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_fault_gate import (
    OUTPUT as FAULT_GATE,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_smoke import SMOKE
from research_pipeline.asset_first_stri_reasoningbank_p1_q5_prepare import (
    load_payload,
)


class ReasoningBankP1Q10AuthorityTest(unittest.TestCase):
    def test_real_frozen_gates_open_q10_replay_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "authority.json"
            result = generate_authority(SMOKE, FAULT_GATE, output)
            payload = load_payload(output)
        self.assertTrue(result["q10_replay_execution_authorized"])
        self.assertEqual(
            payload["decision"],
            "P1_Q10_RUNTIME_RECONCILIATION_QUALIFIED_Q10_REPLAY_AUTHORIZED",
        )
        self.assertTrue(all(payload["checks"].values()))
        self.assertFalse(payload["full_p1_execution_authorized"])
        self.assertFalse(payload["full_p1_preregistration_authorized"])
        self.assertEqual(payload["model_calls"], payload["provider_calls"])
        self.assertEqual(payload["model_calls"], 0)

    def test_failed_smoke_keeps_q10_authority_closed(self) -> None:
        real_smoke = load_payload(SMOKE)
        real_smoke["pass"] = False
        real_smoke["decision"] = "Q10_DAEMON_STATE_RECONCILIATION_SMOKE_HOLD"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            smoke = root / "smoke.json"
            output = root / "authority.json"
            write_json(smoke, {
                key: value for key, value in real_smoke.items()
                if key != "payload_sha256"
            })
            result = generate_authority(smoke, FAULT_GATE, output)
            payload = load_payload(output)
        self.assertFalse(result["q10_replay_execution_authorized"])
        self.assertEqual(
            payload["decision"],
            "P1_Q10_RUNTIME_RECONCILIATION_HOLD_Q10_REPLAY_UNAUTHORIZED",
        )
        self.assertFalse(payload["full_p1_execution_authorized"])


if __name__ == "__main__":
    unittest.main()
