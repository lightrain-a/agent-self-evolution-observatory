from __future__ import annotations

import unittest
from unittest.mock import patch

from .experiment_orchestrator import (
    GPUState,
    ServerProfile,
    active_idea_locations,
    build_launch_plan,
    choose_slot,
)


class ExperimentOrchestratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.profiles = [
            ServerProfile(
                id="60",
                ssh="60",
                repo="/repo60",
                python="/py60",
                data_root="/data60",
                model_path="/model60",
                extra_pythonpath="/site60",
                alfworld_data="/alf60",
                priority=10,
            ),
            ServerProfile(
                id="69",
                ssh="69",
                repo="/repo69",
                python="/py69",
                data_root="/data69",
                model_path="/model69",
                extra_pythonpath="/site69",
                alfworld_data="/alf69",
                priority=20,
            ),
        ]

    def test_choose_slot_prefers_idle_high_priority_server(self) -> None:
        cluster = [
            {
                "server_id": "60",
                "priority": 10,
                "reachable": True,
                "preflight": {"launch_ready": True},
                "gpus": [GPUState(0, "GPU-60-0", "3090", 24576, 24000, 0).__dict__],
            },
            {
                "server_id": "69",
                "priority": 20,
                "reachable": True,
                "preflight": {"launch_ready": True},
                "gpus": [GPUState(0, "GPU-69-0", "A100", 81920, 28000, 80).__dict__],
            },
        ]
        server, gpu = choose_slot(cluster, min_free_memory_mib=18000, max_gpu_utilization_pct=25)
        self.assertEqual(server["server_id"], "60")
        self.assertEqual(gpu["index"], 0)

    def test_active_execution_blocks_duplicate_idea_across_servers(self) -> None:
        cluster = [
            {
                "server_id": "69",
                "priority": 20,
                "reachable": True,
                "preflight": {"launch_ready": True},
                "gpus": [GPUState(0, "GPU-69-0", "A100", 81920, 28000, 0).__dict__],
                "execution_states": [{"idea_id": "update-trust-region", "status": "running"}],
            }
        ]
        self.assertEqual(len(active_idea_locations(cluster, "update-trust-region")), 1)
        with self.assertRaisesRegex(RuntimeError, "unresolved execution"):
            build_launch_plan("update-trust-region", self.profiles, cluster, {})

    def test_registered_result_requires_explicit_repeat(self) -> None:
        cluster = [
            {
                "server_id": "60",
                "priority": 10,
                "reachable": True,
                "preflight": {"launch_ready": True, "runtime_contract_hash": "abc"},
                "gpus": [GPUState(1, "GPU-60-1", "3090", 24576, 24000, 0).__dict__],
                "execution_states": [
                    {"idea_id": "budgeted-evolution-controller", "status": "registered", "result": "fail"}
                ],
            }
        ]
        with self.assertRaisesRegex(RuntimeError, "already has a registered P0"):
            build_launch_plan("budgeted-evolution-controller", self.profiles, cluster, {})
        with patch("research_pipeline.experiment_orchestrator.local_economy_preflight", return_value={"execution_compilation_authorized": True, "passed_gates": 5, "gate_count": 5, "gates": []}), patch("research_pipeline.experiment_orchestrator.remote_pre_experiment_card", return_value={"execution_authorized": True, "passed_gates": 8, "gate_count": 8, "blockers": []}):
            plan = build_launch_plan(
                "budgeted-evolution-controller",
                self.profiles,
                cluster,
                {},
                allow_repeat=True,
                run_label="a2-repair",
                config_name="p0_a2_screening_config.json",
            )
        self.assertEqual(plan["server_id"], "60")
        self.assertEqual(plan["gpu_index"], 1)
        self.assertEqual(plan["run_id"], "a2-repair")
        self.assertIn("CUDA_VISIBLE_DEVICES=GPU-60-1", plan["remote_command"])
        self.assertIn("tmux new-session -d", plan["remote_command"])
        self.assertEqual(plan["pre_experiment_status"], "8/8")

    def test_launch_plan_blocks_when_pre_experiment_card_fails(self) -> None:
        cluster = [{
            "server_id": "60", "priority": 10, "reachable": True,
            "preflight": {"launch_ready": True, "runtime_contract_hash": "abc"},
            "gpus": [GPUState(1, "GPU-60-1", "3090", 24576, 24000, 0).__dict__],
            "execution_states": [],
        }]
        with patch("research_pipeline.experiment_orchestrator.local_economy_preflight", return_value={"execution_compilation_authorized": True, "passed_gates": 5, "gate_count": 5, "gates": []}), patch("research_pipeline.experiment_orchestrator.remote_pre_experiment_card", return_value={"execution_authorized": False, "passed_gates": 7, "gate_count": 8, "blockers": ["statistical-resolution"]}):
            with self.assertRaisesRegex(RuntimeError, "Pre-Experiment Compiler"):
                build_launch_plan(
                    "update-trust-region", self.profiles, cluster, {},
                    run_label="blocked", config_name="p0_a1_screening_config.json",
                )

    def test_launch_plan_blocks_before_remote_compile_when_economy_fails(self) -> None:
        cluster = [{"server_id":"60","priority":10,"reachable":True,"preflight":{"launch_ready":True},"gpus":[GPUState(1,"GPU-60-1","3090",24576,24000,0).__dict__],"execution_states":[]}]
        economy={"execution_compilation_authorized":False,"gates":[{"key":"matched_simplification","pass":False}]}
        with patch("research_pipeline.experiment_orchestrator.local_economy_preflight", return_value=economy), patch("research_pipeline.experiment_orchestrator.remote_pre_experiment_card") as remote:
            with self.assertRaisesRegex(RuntimeError, "P0 Economy Gate"):
                build_launch_plan("update-trust-region",self.profiles,cluster,{},run_label="blocked-economy",config_name="p0_a1_screening_config.json")
            remote.assert_not_called()


if __name__ == "__main__":
    unittest.main()
