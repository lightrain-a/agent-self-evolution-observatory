from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from research_pipeline import temporal_skill_g0_execute as execute
from research_pipeline import temporal_skill_g0_reopen_preflight as preflight


class TemporalSkillG0ExecuteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt, cls.plan = preflight.build_receipt()
        cls.request = preflight.build_authorization_request(cls.receipt, cls.plan)

    def valid_authorization(self) -> dict:
        auth = {
            "schema_version": "1.0",
            "status": "HUMAN_EXECUTION_AUTHORITY_RECORDED",
            "authority_source": "unit-test",
            "directive": "test-only",
            "scope": list(self.request["requested_scope"]),
            "bound_plan_body_sha256": self.plan["plan_body_sha256"],
            "bound_runner_sha256": self.request["bound_runner_sha256"],
            "bound_analyzer_sha256": self.request["bound_analyzer_sha256"],
            "scientific_reopen_authorized": True,
            "execution_authorized": True,
            "provider_spend_authorized": True,
            "ark_plan_target_confirmed_and_propagated": True,
            "ark_plan_target_model": self.plan["model_identity"]["required_plan_target_model"],
            "ark_plan_base_url": self.plan["model_identity"]["required_plan_base_url"],
            "bounded_budget": {
                "model_calls_upper_bound": self.plan["summary"]["planned_model_calls"],
                "reruns_allowed": False,
            },
            "outcome_driven_selection_authorized": False,
            "model_identity": dict(self.plan["model_identity"]),
        }
        auth["authorization_sha256"] = execute.canonical_sha(auth)
        return auth

    def test_valid_authorization_binds_plan_code_and_plan_route(self) -> None:
        self.assertEqual(execute.validate_authorization(self.valid_authorization(), self.plan), [])

    def test_direct_or_unconfirmed_route_is_rejected(self) -> None:
        auth = self.valid_authorization()
        auth.pop("authorization_sha256")
        auth["ark_plan_target_confirmed_and_propagated"] = False
        auth["ark_plan_base_url"] = "https://ark.cn-beijing.volces.com/api/v3"
        auth["authorization_sha256"] = execute.canonical_sha(auth)
        errors = execute.validate_authorization(auth, self.plan)
        self.assertIn("ark-plan-target-not-confirmed", errors)
        self.assertIn("ark-plan-base-url-mismatch", errors)

    def test_code_hash_change_is_rejected(self) -> None:
        auth = self.valid_authorization()
        auth.pop("authorization_sha256")
        auth["bound_runner_sha256"] = "0" * 64
        auth["authorization_sha256"] = execute.canonical_sha(auth)
        self.assertIn("authorization-runner-hash-mismatch", execute.validate_authorization(auth, self.plan))

    def test_missing_authorization_fails_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing-auth.json"
            output = Path(tmp) / "results.json"
            with self.assertRaisesRegex(RuntimeError, "human authorization artifact missing"):
                execute.execute(
                    preflight.DEFAULT_PLAN if hasattr(preflight, "DEFAULT_PLAN") else Path("generated/temporal-skill-g0-fresh-factorial-plan-20260824.json"),
                    Path("generated/temporal-skill-g0-reopen-preflight-20260824.json"),
                    missing,
                    output,
                )
            self.assertFalse(output.exists())

    def test_runner_is_single_post_no_retry(self) -> None:
        source = Path(execute.__file__).read_text(encoding="utf-8")
        self.assertIn("max_retries=0", source)
        self.assertIn("allow_thinking_compatibility_fallback=False", source)
        self.assertIn("generation_post_attempts_per_planned_unit", source)
        self.assertNotIn("requests.post", source)

    def test_g0_source_matches_frozen_plan(self) -> None:
        self.assertEqual(self.plan["g0"]["source"], execute.G0_SOURCE)
        self.assertEqual(self.plan["g0"]["source_sha256"], execute.sha_bytes(execute.G0_SOURCE.encode("utf-8")))


if __name__ == "__main__":
    unittest.main()
