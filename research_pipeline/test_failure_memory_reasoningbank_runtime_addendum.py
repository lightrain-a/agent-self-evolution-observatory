from __future__ import annotations

import copy
import unittest

from research_pipeline.failure_memory_reasoningbank_runtime_addendum import build_addendum


def parent() -> dict:
    return {
        "status": "IDENTIFICATION_COHORT_AND_STATISTICAL_DIRECTION_FROZEN_RUNTIME_EXECUTOR_BUDGET_UNBOUND",
        "cohort": {
            "independent_units": 36,
            "downstream_task_ids": [str(i) for i in range(36)],
        },
    }


def audit() -> dict:
    return {
        "status": "DECLARED_PY313_RUNTIME_NOT_DIRECTLY_MATERIALIZABLE_PY312_WEBARENA_COMPATIBILITY_PATH_VERIFIED",
        "first_party_runtime": {"commit": "ed80611788292ea739f1effd31f16c53823b8a0d"},
        "python312_compatibility_runtime": {
            "python": "3.12.13",
            "versions": {
                "browsergym-core": "0.14.1",
                "browsergym-experiments": "0.14.1",
                "browsergym-webarena": "0.14.1",
                "playwright": "1.44.0",
                "greenlet": "3.0.3",
                "libwebarena": "0.0.4",
            },
            "webarena_import_completed": True,
            "webarena_registered_task_ids": 812,
            "playwright_chromium_revision": "1117",
            "matching_default_chromium_cache_found": False,
            "webarena_site_env_configured": {
                "REDDIT": "",
                "SHOPPING": "",
                "SHOPPING_ADMIN": "",
                "GITLAB": "",
                "WIKIPEDIA": "",
                "MAP": "",
                "HOMEPAGE": "",
            },
            "webarena_all_required_site_envs_present": False,
            "live_webarena_deployment_detected": False,
        },
        "adjudication": {
            "exact_declared_python313_runtime_materialized": False,
            "python312_browsergym0141_component_path_materialized": True,
            "python312_webarena_import_verified": True,
        },
    }


class TestReasoningBankRuntimeAddendum(unittest.TestCase):
    def test_selects_explicit_py312_compatibility_without_execution(self) -> None:
        payload = build_addendum(parent(), audit(), parent_sha="parent", audit_sha="audit")
        self.assertEqual(
            payload["runtime_policy"]["selected_l2b_runtime_label"],
            "PY312_BG0141_EXPLICIT_COMPATIBILITY_DEVIATION",
        )
        self.assertEqual(payload["runtime_policy"]["browsergym_webarena"], "0.14.1")
        self.assertEqual(payload["runtime_policy"]["playwright"], "1.44.0")
        self.assertFalse(payload["execution_gate"]["execution_permitted"])
        self.assertFalse(payload["execution_gate"]["exact_chromium_revision_available"])
        self.assertFalse(payload["execution_gate"]["webarena_sites_configured_and_deployed"])
        self.assertFalse(payload["authority"]["model_calls"])
        self.assertFalse(payload["authority"]["browser_tasks"])

    def test_scope_never_unlocks_l3_or_exact_runtime_claim(self) -> None:
        payload = build_addendum(parent(), audit(), parent_sha="parent", audit_sha="audit")
        self.assertFalse(payload["identification_scope"]["o6_l3_unblocked"])
        forbidden = payload["identification_scope"]["forbidden_claims"]
        self.assertIn("exact-as-declared ReasoningBank runtime replication", forbidden)
        self.assertIn("source-faithful financial AgentDojo transport", forbidden)
        self.assertEqual(
            payload["identification_scope"]["strongest_allowed_positive_claim"],
            "A provenance-status metadata effect on the frozen ReasoningBank/WebArena compatibility substrate.",
        )

    def test_wrong_parent_or_runtime_audit_fails_closed(self) -> None:
        bad_parent = copy.deepcopy(parent())
        bad_parent["status"] = "WRONG"
        with self.assertRaises(ValueError):
            build_addendum(bad_parent, audit(), parent_sha="parent", audit_sha="audit")

        bad_audit = copy.deepcopy(audit())
        bad_audit["status"] = "WRONG"
        with self.assertRaises(ValueError):
            build_addendum(parent(), bad_audit, parent_sha="parent", audit_sha="audit")

    def test_runtime_audit_must_have_verified_compatibility_import(self) -> None:
        bad = copy.deepcopy(audit())
        bad["adjudication"]["python312_webarena_import_verified"] = False
        with self.assertRaises(ValueError):
            build_addendum(parent(), bad, parent_sha="parent", audit_sha="audit")


if __name__ == "__main__":
    unittest.main()
