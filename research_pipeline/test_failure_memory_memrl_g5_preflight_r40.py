import unittest
from pathlib import Path
from unittest.mock import patch

from research_pipeline.failure_memory_memrl_g5_preflight_r40 import build, probe_runtime, PINNED_MEMRL_SHA


class MemRLG5PreflightR40Test(unittest.TestCase):
    def _runtime(self, docker: bool) -> dict:
        return {
            "memrl_repo": "/tmp/frozen-memrl",
            "repo_present": True,
            "pinned_commit_expected": PINNED_MEMRL_SHA,
            "commit_observed": PINNED_MEMRL_SHA,
            "commit_matches": True,
            "checkout_clean": True,
            "required_files_present": {"x": True},
            "all_required_files_present": True,
            "docker_server_available": docker,
            "docker_probe_exit_code": 0 if docker else 1,
            "docker_probe_output": "27.0" if docker else "unavailable",
            "model_calls": 0,
            "environment_actions": 0,
            "evaluator_calls": 0,
            "treatment_outcomes_observed": 0,
        }

    def test_contract_never_grants_g6(self):
        d = build(self._runtime(True))
        self.assertTrue(d["G5_adjudication"]["preregistration_contract_frozen"])
        self.assertFalse(d["G5_adjudication"]["passed_now"])
        self.assertFalse(d["gate_adjudication"]["G6_AUTHORITY"])
        self.assertFalse(d["authority"]["experiment"])
        self.assertEqual(set(d["frozen_confirmatory_contract"]["arms"]), {
            "A_content_only", "B_raw_provenance", "C_PSMG", "D_nonprovenance_controller"
        })

    def test_docker_unavailable_fails_closed(self):
        d = build(self._runtime(False))
        self.assertEqual(d["G5_adjudication"]["state"], "BLOCKED_CURRENT_HOST_DOCKER_DAEMON_UNAVAILABLE")
        self.assertEqual(d["gate_adjudication"]["next_blocking_stage"], "G5_RUNTIME_SUPPORT")
        self.assertFalse(d["claim_policy"]["confirmatory_execution_authorized"])

    def test_old_assets_forbidden(self):
        d = build(self._runtime(False))
        c = d["frozen_confirmatory_contract"]
        self.assertFalse(c["R19_partial_outcomes_used_for_design"])
        self.assertFalse(c["same_asset_27_used"])
        self.assertTrue(c["no_interim_inference"])
        self.assertTrue(c["no_optional_stopping_on_effect"])

    def test_probe_requires_pinned_clean_repo_and_files(self):
        with patch("research_pipeline.failure_memory_memrl_g5_preflight_r40._run") as run:
            run.side_effect = [
                (0, PINNED_MEMRL_SHA),
                (0, ""),
                (1, "docker unavailable"),
            ]
            with patch.object(Path, "exists", return_value=True), patch.object(Path, "is_file", return_value=True):
                d = probe_runtime(Path("/tmp/frozen-memrl"))
        self.assertTrue(d["commit_matches"])
        self.assertTrue(d["checkout_clean"])
        self.assertTrue(d["all_required_files_present"])
        self.assertFalse(d["docker_server_available"])
        self.assertEqual(d["model_calls"], 0)
        self.assertEqual(d["environment_actions"], 0)


if __name__ == "__main__":
    unittest.main()
