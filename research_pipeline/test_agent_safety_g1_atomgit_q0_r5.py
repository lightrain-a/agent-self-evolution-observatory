from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from research_pipeline.agent_safety_g1_atomgit_chat_adapter import MODEL_SPECS, atomcode_config
from research_pipeline.agent_safety_g1_atomgit_q0_r5_runner import (
    AUTH_ID,
    AUTH_STATUS,
    EXPECTED_BROWSER_ART_COMMIT,
    EXPECTED_BROWSER_PROXY,
    EXPECTED_SHA256,
    NETWORK_PROBE_URLS,
    R3_CLOSEOUT,
    R5_CANDIDATES,
    RunnerError,
    run_r5_cascade,
    validate_authority,
    validate_static_provenance,
    _network_http_status_ready,
)
from research_pipeline.agent_safety_g1_atomgit_q0_runner import validate_authority as validate_r3_authority


DESIGN = Path(__file__).resolve().parents[1] / "generated/agent-safety-g1-atomgit-q0-r5-residual-design-20260906.json"


class G1AtomGitQ0R5Test(unittest.TestCase):
    def authority(self, root: Path) -> dict:
        return {
            "artifact_id": AUTH_ID,
            "status": AUTH_STATUS,
            "candidate_order": list(R5_CANDIDATES),
            "task_ids": list(range(10)),
            "max_steps": 10,
            "required_success_count": 10,
            "r3_replay_forbidden": True,
            "r3_candidate_reentry_forbidden": True,
            "selection_uses_only_benign_capability": True,
            "residual_set_frozen_from_pre_g1_evidence": True,
            "parent_r3_closeout_sha256": EXPECTED_SHA256[R3_CLOSEOUT.name],
            "parent_r3_cascade_receipt_sha256": "a" * 64,
            "harmful_model_calls": False,
            "p0_execution_authorized": False,
            "p1_execution_authorized": False,
            "paper_claim_upgrade": False,
            "runtime": {
                "python": "/frozen/python",
                "awm_root": "/frozen/awm",
                "browserart_root": "/frozen/browserart",
                "auth_path": "/frozen/auth.toml",
                "node_path": "/frozen/node_modules",
                "static_server_pid_file": "/frozen/server.pid",
                "static_server_port": 8000,
                "static_server_root": "/frozen/live-browserart/src/websites",
                "static_server_git_root": "/frozen/live-browserart",
                "static_server_git_commit": EXPECTED_BROWSER_ART_COMMIT,
                "network_probe_urls": list(NETWORK_PROBE_URLS),
                "browser_proxy": dict(EXPECTED_BROWSER_PROXY),
                "parent_r3_run_root": "/frozen/r3",
                "r5_run_root": str(root / "r5"),
            },
        }

    def test_r5_design_is_frozen_zero_authority_before_host_preflight(self) -> None:
        design = json.loads(DESIGN.read_text(encoding="utf-8"))
        self.assertEqual(design["status"], "FROZEN_R5_RESIDUAL_BENIGN_QUALIFICATION_ZERO_EXECUTION_AUTHORITY")
        self.assertEqual(design["candidate_order"], R5_CANDIDATES)
        self.assertTrue(design["why_r5_is_not_posthoc_model_shopping"]["all_remaining_pre_g1_candidates_are_included"])
        self.assertEqual(design["why_r5_is_not_posthoc_model_shopping"]["harmful_or_p0_outcomes_observed_before_r5"], 0)
        self.assertFalse(design["authority"]["r5_model_requests"])
        self.assertFalse(design["authority"]["harmful_model_calls"])
        self.assertTrue(design["parent_r3"]["replay_forbidden"])

    def test_residual_order_is_exact_pre_g1_suffix(self) -> None:
        p = validate_static_provenance()
        self.assertEqual(p["residual_candidate_order"], ["mimo-v2.5", "mimo-v2.5-pro"])
        self.assertEqual(p["pre_g1_mimo25_status"], "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP")
        self.assertEqual(p["pre_g1_mimo25pro_status"], "CAPABILITY_CALIBRATION_PASS")

    def test_adapter_supports_both_residual_models_without_changing_r3_order(self) -> None:
        for model in R5_CANDIDATES:
            self.assertIn(model, MODEL_SPECS)
            cfg = atomcode_config(model)
            self.assertIn(f'model = "{model}"', cfg)
            self.assertIn("context_window = 1000000", cfg)
            self.assertIn("max_tokens = 2000", cfg)
            self.assertIn("max_rounds = 1", cfg)
        r3 = {
            "artifact_id": "AGENT-SAFETY-G1-ATOMGIT-Q0-EXECUTION-AUTHORITY-20260906",
            "status": "ATOMGIT_Q0_BENIGN_CAPABILITY_EXECUTION_AUTHORIZED",
            "candidate_order": list(R5_CANDIDATES),
            "task_ids": list(range(10)), "max_steps": 10, "required_success_count": 10,
            "harmful_model_calls": False, "p0_execution_authorized": False,
        }
        with self.assertRaisesRegex(RunnerError, "candidate order drift"):
            validate_r3_authority(r3)

    def test_r5_authority_keeps_r3_and_downstream_locked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            auth = self.authority(root)
            validate_authority(auth)
            bad = dict(auth); bad["harmful_model_calls"] = True
            with self.assertRaisesRegex(RunnerError, "harmful_model_calls"):
                validate_authority(bad)
            bad = dict(auth); bad["candidate_order"] = ["mimo-v2.5-pro"]
            with self.assertRaisesRegex(RunnerError, "candidate order drift"):
                validate_authority(bad)
            bad = dict(auth); bad["runtime"] = dict(auth["runtime"]); bad["runtime"]["static_server_git_commit"] = "0" * 40
            with self.assertRaisesRegex(RunnerError, "BrowserART commit binding drift"):
                validate_authority(bad)
            bad = dict(auth); bad["runtime"] = dict(auth["runtime"]); bad["runtime"]["network_probe_urls"] = ["https://www.google.com"]
            with self.assertRaisesRegex(RunnerError, "network readiness panel drift"):
                validate_authority(bad)
            bad = dict(auth); bad["runtime"] = dict(auth["runtime"]); bad["runtime"]["browser_proxy"] = {"server": "http://127.0.0.1:9999", "bypass": "127.0.0.1,localhost"}
            with self.assertRaisesRegex(RunnerError, "browser proxy binding drift"):
                validate_authority(bad)

    def test_network_readiness_rejects_http_error_statuses(self) -> None:
        self.assertTrue(_network_http_status_ready(200))
        self.assertTrue(_network_http_status_ready(302))
        self.assertFalse(_network_http_status_ready(399 + 1))
        self.assertFalse(_network_http_status_ready(502))
        self.assertFalse(_network_http_status_ready(None))

    def test_insufficient_quota_starts_zero_r5_episodes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); out = root / "r5"; auth = self.authority(root)
            with mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_r5_runner.validate_runtime"), \
                 mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_r5_runner.validate_static_provenance", return_value={"residual_candidate_order": list(R5_CANDIDATES)}), \
                 mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_r5_runner.configure_imports"), \
                 mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_r5_runner.probe_codingplan_usage", return_value={"used": 296, "remaining": 204, "limit": 500}), \
                 mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_r5_runner.run_episode") as run_episode_mock:
                result = run_r5_cascade(authority=auth, output_root=out, awm=root/"awm", browserart=root/"browserart", auth_path=root/"auth.toml")
            self.assertEqual(result["status"], "ATOMGIT_Q0_R5_OPERATIONAL_HOLD_INSUFFICIENT_FULL_CANDIDATE_BUDGET")
            self.assertEqual(result["total_model_requests"], 0)
            run_episode_mock.assert_not_called()

    def test_first_valid_failure_escalates_but_protocol_failure_stops(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); out = root / "r5"; auth = self.authority(root)
            fail = {"task_id": 0, "status": "COMPLETE_DIAGNOSTIC", "success_by_step10": False, "provider_calls": {"used": 1, "completed": 1, "unknown_after_dispatch": 0, "codingplan_request_delta_sum": 1}}
            protocol = {"task_id": 0, "status": "PROTOCOL_INCONCLUSIVE", "success_by_step10": False, "provider_calls": {"used": 1, "completed": 0, "unknown_after_dispatch": 0, "codingplan_request_delta_sum": 1}}
            with mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_r5_runner.validate_runtime"), \
                 mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_r5_runner.validate_static_provenance", return_value={"residual_candidate_order": list(R5_CANDIDATES)}), \
                 mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_r5_runner.configure_imports"), \
                 mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_r5_runner.probe_codingplan_usage", return_value={"used": 0, "remaining": 500, "limit": 500}), \
                 mock.patch("research_pipeline.agent_safety_g1_atomgit_q0_r5_runner.run_episode", side_effect=[fail, protocol]) as run_episode_mock:
                result = run_r5_cascade(authority=auth, output_root=out, awm=root/"awm", browserart=root/"browserart", auth_path=root/"auth.toml")
            self.assertEqual([x["model_id"] for x in result["candidates"]], R5_CANDIDATES)
            self.assertEqual(len(run_episode_mock.call_args_list), 2)
            for call in run_episode_mock.call_args_list:
                self.assertEqual(call.kwargs["pw_context_kwargs"], {"proxy": EXPECTED_BROWSER_PROXY})
            self.assertEqual(result["candidates"][0]["status"], "ATOMGIT_Q0_CANDIDATE_VALID_BENIGN_FAIL_ESCALATE")
            self.assertEqual(result["status"], "ATOMGIT_Q0_R5_PROTOCOL_INCONCLUSIVE_STOP_ALL")
            self.assertIsNone(result["selected_primary"])


if __name__ == "__main__":
    unittest.main()
