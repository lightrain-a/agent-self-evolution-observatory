from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_m3r4_execution_guard import (
    DRAFT_STATUS,
    FRESH_IDENTITY_STATUS,
    validate_fresh_identity,
    validate_zero_provider_draft,
)


ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "generated/e2-r17-m3r4-execution-draft-contract-20260904.json"


class M3R4ExecutionGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.draft = json.loads(DRAFT.read_text(encoding="utf-8"))

    def test_current_draft_passes_only_zero_provider_validation(self) -> None:
        observed = validate_zero_provider_draft(DRAFT)
        self.assertEqual(observed["status"], DRAFT_STATUS)
        self.assertTrue(all(value is False for value in observed["authority"].values()))

    def test_draft_with_any_provider_authority_fails(self) -> None:
        bad = copy.deepcopy(self.draft)
        bad["authority"]["provider_io"] = True
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "zero authority"):
                validate_zero_provider_draft(p)

    def test_historical_identity_cannot_impersonate_fresh_m3r4_identity(self) -> None:
        historical = json.loads(
            (ROOT / "generated/e2-r17-deepseek-v2-repair2-model-identity-adjudication-20260831.json").read_text(
                encoding="utf-8"
            )
        )
        with self.assertRaisesRegex(RuntimeError, "fresh M3R4 identity status"):
            validate_fresh_identity(historical, self.draft)

    def test_future_identity_schema_is_exact_and_non_scientific(self) -> None:
        good = {
            "status": FRESH_IDENTITY_STATUS,
            "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
            "requested_and_resolved": {
                "deepseek-v4-pro": {
                    "requested": "deepseek-v4-pro",
                    "resolved": "deepseek-v4-pro-ga-260813",
                    "thinking_requested": "disabled",
                }
            },
            "provider_retry_limit": 0,
            "max_output_tokens_smoke": 8192,
            "scientific_tranche": "E2-R17-M3R4",
            "scientific_experiment": False,
        }
        validate_fresh_identity(good, self.draft)
        for mutation, error in (
            (("status", "PASS_CURRENT_REVIEW_TRANCHE"), "fresh M3R4 identity status"),
            (("route", "https://example.invalid"), "route drift"),
            (("scientific_experiment", True), "non-scientific"),
        ):
            bad = copy.deepcopy(good)
            bad[mutation[0]] = mutation[1]
            with self.assertRaisesRegex(RuntimeError, error):
                validate_fresh_identity(bad, self.draft)

    def test_changed_resolved_model_requires_review_not_silent_substitution(self) -> None:
        bad = {
            "status": FRESH_IDENTITY_STATUS,
            "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
            "requested_and_resolved": {
                "deepseek-v4-pro": {
                    "requested": "deepseek-v4-pro",
                    "resolved": "deepseek-v4-pro-some-new-release",
                    "thinking_requested": "disabled",
                }
            },
            "provider_retry_limit": 0,
            "max_output_tokens_smoke": 8192,
            "scientific_tranche": "E2-R17-M3R4",
            "scientific_experiment": False,
        }
        with self.assertRaisesRegex(RuntimeError, "resolved model drift"):
            validate_fresh_identity(bad, self.draft)
        self.assertEqual(
            self.draft["fresh_model_identity_gate"]["if_resolved_identity_changes"],
            "HOLD_REVIEW_REQUIRED_NO_AUTOMATIC_MODEL_SUBSTITUTION",
        )


if __name__ == "__main__":
    unittest.main()
