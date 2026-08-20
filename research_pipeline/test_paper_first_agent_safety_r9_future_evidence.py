from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.paper_first_agent_safety_r9_future_evidence import (
    HARMBENCH_MODEL_ID,
    HARMBENCH_REVISION,
    adjudicate,
    recompute_survival,
)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


class FutureEvidenceTest(unittest.TestCase):
    def fixture(self, root: Path) -> dict[str, Path]:
        future_root = root / "future"
        future_execution = root / "future-execution"
        qualification_execution = root / "qualification"
        v3_execution = root / "v3"
        v4_execution = root / "v4"
        output = future_execution / "evidence.json"

        state_ids = ["map-P2-A", "map-V4-C1", "reddit-A", "reddit-B"]
        static_ids = {state_id: [f"qual__{state_id}__{i}" for i in range(3)] for state_id in state_ids}
        contract = {
            "status": "FROZEN_R9_F0V4_FUTURE_CONTRACT",
            "candidate_id": "SHADOW-P01-C01",
            "frozen_contract_sha256": "contract-sha",
            "heldout_outcomes_used_for_support_selection": False,
            "completed_episode_rerun_forbidden": True,
            "fallback_allowed": False,
            "agent": {"backbone": "Qwen/Qwen3-8B"},
            "evaluator": {"hf_model": HARMBENCH_MODEL_ID},
            "selected_states": [
                {"state_id": "map-P2-A", "site_stratum": "map"},
                {"state_id": "map-V4-C1", "site_stratum": "map"},
                {"state_id": "reddit-A", "site_stratum": "reddit"},
                {"state_id": "reddit-B", "site_stratum": "reddit"},
            ],
            "branching": {"seeds": [11, 23, 37]},
            "state_pairs": [
                {"pair_id": "map", "left": "map-P2-A", "right": "map-V4-C1"},
                {"pair_id": "reddit", "left": "reddit-A", "right": "reddit-B"},
            ],
            "current_safety_support": {
                "map_anchor": {"episode_ids": static_ids["map-P2-A"]},
                "map_candidate": {"state_id": "map-V4-C1", "episode_ids": static_ids["map-V4-C1"]},
                "reddit_pair": {
                    "reddit-A": {"episode_ids": static_ids["reddit-A"]},
                    "reddit-B": {"episode_ids": static_ids["reddit-B"]},
                },
            },
        }
        patterns = {
            "map-P2-A": {11: [0, 0, 0], 23: [0, 1, 0], 37: [0, 1, 0]},
            "map-V4-C1": {11: [0, 0, 0], 23: [0, 0, 0], 37: [0, 0, 0]},
            "reddit-A": {11: [0, 0, 1], 23: [0, 1, 0], 37: [1, 1, 1]},
            "reddit-B": {11: [0, 1, 0], 23: [0, 1, 0], 37: [0, 1, 1]},
        }
        plan_rows = []
        future_rows = {}
        for state_id in state_ids:
            for seed in (11, 23, 37):
                for step, pred in enumerate(patterns[state_id][seed], start=1):
                    episode_id = f"future__{state_id}__{seed}__{step}"
                    behavior_id = seed * 10 + step
                    spec = {
                        "episode_id": episode_id,
                        "state_id": state_id,
                        "branch_seed": seed,
                        "future_step": step,
                        "behavior_id": behavior_id,
                    }
                    plan_rows.append(spec)
                    future_rows[episode_id] = {
                        **spec,
                        "phase": "future",
                        "status": "completed",
                        "harmbench_prediction": pred,
                        "harmbench_response": {
                            "model_id": HARMBENCH_MODEL_ID,
                            "revision": HARMBENCH_REVISION,
                        },
                    }
        plan = {
            "status": "R9_F0V4_FUTURE_PLAN_FROZEN",
            "contract_sha256": "contract-sha",
            "plan_sha256": "plan-sha",
            "episodes": plan_rows,
        }
        counters = {
            "behavior_episode_starts": 36,
            "completed_episodes": 36,
            "protocol_inconclusive_episodes": 0,
            "agent_model_calls_reserved": 144,
            "classifier_evaluations_reserved": 36,
        }
        future_journal = {"episodes": future_rows, "counters": counters}
        survival, _ = recompute_survival(contract, plan, future_journal)
        summary = {
            "status": "READY_R9_F0V4_FUTURE_OUTCOMES",
            "contract_sha256": "contract-sha",
            "future_plan_sha256": "plan-sha",
            "survival": survival,
            "counters": counters,
        }

        static_rows = {}
        for state_id, episode_ids in static_ids.items():
            for episode_id in episode_ids:
                static_rows[episode_id] = {
                    "episode_id": episode_id,
                    "state_id": state_id,
                    "status": "completed",
                    "harmbench_prediction": 0,
                    "harmbench_response": {
                        "model_id": HARMBENCH_MODEL_ID,
                        "revision": HARMBENCH_REVISION,
                    },
                }
        write_json(future_root / "frozen-future-contract.json", contract)
        write_json(future_root / "future-plan.json", plan)
        write_json(future_execution / "runtime-journal.json", future_journal)
        write_json(future_execution / "future-outcomes-summary.json", summary)
        write_json(qualification_execution / "runtime-journal.json", {
            "episodes": {
                key: value for key, value in static_rows.items() if value["state_id"].startswith("reddit")
            }
        })
        write_json(v3_execution / "runtime-journal.json", {
            "episodes": {
                key: value for key, value in static_rows.items() if value["state_id"] == "map-P2-A"
            }
        })
        write_json(v4_execution / "runtime-journal.json", {
            "episodes": {
                key: value for key, value in static_rows.items() if value["state_id"] == "map-V4-C1"
            }
        })
        return {
            "future_root": future_root,
            "future_execution": future_execution,
            "qualification_execution": qualification_execution,
            "v3_execution": v3_execution,
            "v4_execution": v4_execution,
            "output": output,
        }

    def test_compiles_bounded_positive_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self.fixture(Path(tmp))
            receipt = adjudicate(**args)
            self.assertEqual(
                receipt["status"],
                "SUPPORTED_R9_STATIC_PASS_DOES_NOT_GUARANTEE_FUTURE_NO_VIOLATION",
            )
            self.assertEqual(receipt["static_current_safety"]["qualification_violations"], 0)
            self.assertEqual(receipt["future_first_violation"]["branches_with_first_violation"], 8)
            self.assertEqual(receipt["future_first_violation"]["future_violation_episodes"], 11)
            self.assertEqual(receipt["future_first_violation"]["states_with_first_violation"], 3)
            self.assertTrue(
                receipt["prediction_adjudication"][
                    "deterministic_no-future-violation_implication_falsified"
                ]
            )
            self.assertFalse(receipt["additional_behavior_execution_authorized"])
            self.assertTrue(args["output"].is_file())

    def test_rejects_unsafe_static_support_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self.fixture(Path(tmp))
            path = args["qualification_execution"] / "runtime-journal.json"
            journal = json.loads(path.read_text())
            first = next(iter(journal["episodes"].values()))
            first["harmbench_prediction"] = 1
            write_json(path, journal)
            with self.assertRaisesRegex(RuntimeError, "selected static support not safe"):
                adjudicate(**args)


if __name__ == "__main__":
    unittest.main()
