from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-contract-20260903.json"
PREFLIGHT = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-preflight-20260903.json"
ACTOR = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_actor_pool.py"
RUNNER = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a.py"
AUTHORIZER = ROOT / "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a.py"
ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SemanticTransferV3StageAControlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
        cls.adjudicator = load_module(ADJUDICATOR, "semantic_transfer_v3_adjudicator_test")
        cls.actor = load_module(ACTOR, "semantic_transfer_v3_actor_test")
        cls.runner = load_module(RUNNER, "semantic_transfer_v3_runner_test")
        suite_root = Path(cls.contract["suite"]["root"])
        cls.split = json.loads((suite_root / "r17_split_manifest.json").read_text(encoding="utf-8"))
        cls.streams = {str(k): [str(x) for x in v] for k, v in cls.split["e1_update_streams"].items()}
        cls.update_tasks = [task for stream in cls.streams.values() for task in stream]
        cls.heldout = [str(x) for x in cls.split["e1_common_heldout_probe"]]

    def test_contract_and_preflight_have_zero_execution_authority(self) -> None:
        self.assertEqual("FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A", self.contract["status"])
        self.assertEqual("PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_PREFLIGHT", self.preflight["status"])
        self.assertFalse(self.contract["authority"]["stage_a_provider_execution"])
        self.assertFalse(self.contract["authority"]["stage_b_learning_execution"])
        self.assertFalse(self.preflight["authority"]["stage_a_provider_execution"])
        self.assertFalse(self.preflight["fresh_identity_qualified"])
        self.assertTrue(self.preflight["fresh_identity_required_before_authorization"])
        self.assertEqual(20, self.preflight["stream_count"])
        self.assertEqual(160, self.preflight["task_count"])
        self.assertEqual(0, self.preflight["provider_calls"])
        self.assertFalse(self.preflight["scientific_execution"])

    def test_bound_code_hashes_match_contract(self) -> None:
        for label, item in self.contract["bound_code"].items():
            with self.subTest(label=label):
                path = ROOT / item["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(item["sha256"], file_sha(path))

    def test_bound_split_shape_and_heldout_separation(self) -> None:
        suite_root = Path(self.contract["suite"]["root"])
        split_path = suite_root / "r17_split_manifest.json"
        self.assertEqual(self.contract["suite"]["split_manifest_sha256"], file_sha(split_path))
        self.assertEqual(self.contract["suite"]["streams"], list(self.streams))
        self.assertEqual(20, len(self.streams))
        self.assertTrue(all(len(tasks) == 8 for tasks in self.streams.values()))
        self.assertEqual(160, len(self.update_tasks))
        self.assertEqual(160, len(set(self.update_tasks)))
        self.assertEqual(20, len(self.heldout))
        self.assertFalse(set(self.update_tasks) & set(self.heldout))

    def test_actor_has_no_legacy_or_hidden_family_metadata_dependency(self) -> None:
        source = ACTOR.read_text(encoding="utf-8")
        self.assertNotIn("primary_failure_family", source)
        self.assertNotIn('metadata[task_id]["semantic_type"]', source)
        self.assertNotIn('metadata[task_id]["matched_skeleton"]', source)

    def test_equal_dose_hash_selection_v3_is_order_invariant(self) -> None:
        tasks = [f"task-{index}" for index in range(8)]
        a = self.adjudicator.choose_four("stream-x", tasks)
        b = self.adjudicator.choose_four("stream-x", list(reversed(tasks)))
        self.assertEqual(a, b)
        expected = sorted(
            tasks,
            key=lambda task_id: hashlib.sha256(
                f"semantic-transfer-mrw4-v3|stream-x|{task_id}".encode("utf-8")
            ).hexdigest(),
        )[:4]
        self.assertEqual(expected, a)

    def test_failed_witness_selector_is_lowest_index_failed_nonwinner(self) -> None:
        rows = [
            {"rollout_index": 5, "score": 0.0, "trajectory_path": "/tmp/r5", "trajectory_sha256": "5" * 64},
            {"rollout_index": 1, "score": 1.0, "trajectory_path": "/tmp/r1", "trajectory_sha256": "1" * 64},
            {"rollout_index": 2, "score": 0.0, "trajectory_path": "/tmp/r2", "trajectory_sha256": "2" * 64},
            {"rollout_index": 7, "score": 1.0, "trajectory_path": "/tmp/r7", "trajectory_sha256": "7" * 64},
        ]
        witness = self.adjudicator.select_failed_witness(rows, acting_winner_index=1)
        self.assertEqual(2, witness["rollout_index"])
        self.assertEqual(0.0, witness["score"])
        self.assertEqual(
            "lowest original rollout index among verifier-failure nonwinner trajectories",
            witness["selector"],
        )

    def test_reduction_router_rankings_are_deterministic(self) -> None:
        streams = [f"s{index:02d}" for index in range(20)]
        difficulty = {stream: index // 2 for index, stream in enumerate(streams)}
        mixedness = {stream: 10 - (index // 2) for index, stream in enumerate(streams)}
        hard_a = self.adjudicator.choose_ten_streams(
            streams, difficulty, descending=False, salt="semantic-transfer-difficulty-v3"
        )
        hard_b = self.adjudicator.choose_ten_streams(
            list(reversed(streams)), difficulty, descending=False, salt="semantic-transfer-difficulty-v3"
        )
        mixed_a = self.adjudicator.choose_ten_streams(
            streams, mixedness, descending=True, salt="semantic-transfer-mixedness-v3"
        )
        mixed_b = self.adjudicator.choose_ten_streams(
            list(reversed(streams)), mixedness, descending=True, salt="semantic-transfer-mixedness-v3"
        )
        self.assertEqual(hard_a, hard_b)
        self.assertEqual(mixed_a, mixed_b)
        self.assertEqual(10, len(hard_a))
        self.assertEqual(10, len(mixed_a))

    def _write_review(
        self,
        root: Path,
        *,
        contract_sha: str,
        passing: bool = True,
        created_at: datetime | None = None,
    ) -> Path:
        path = root / "review.json"
        if created_at is None:
            created_at = datetime.fromisoformat(self.contract["created_at_utc"]) + timedelta(seconds=1)
        payload = {
            "status": "COMPLETED",
            "created_at_utc": created_at.isoformat(),
            "conversation_url": "https://chatgpt.com/c/synthetic-v3-stage-a-review",
            "surface": "ChatGPT web",
            "model": "GPT-5.6 Sol",
            "thinking_level": "极高",
            "prompt_submissions": 1,
            "contract_sha256_acknowledged": contract_sha,
            "verdict": "PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION" if passing else "REVISE_BEFORE_STAGE_A",
            "execution_recommendation": "ALLOW_SEPARATE_STAGE_A_AUTHORIZATION" if passing else "HOLD_STAGE_A",
            "remaining_blockers": [] if passing else ["synthetic blocker"],
            "stage_b_authority": False,
            "paper_claim_authority": False,
            "scientific_authority": False,
            "experiment_authority": False,
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _write_identity(self, root: Path, *, created_at: datetime) -> Path:
        path = root / "identity.json"
        payload = {
            "status": "PASS_CURRENT_REVIEW_TRANCHE",
            "created_at_utc": created_at.isoformat(),
            "requested_and_resolved": {
                "deepseek-v4-pro": {
                    "requested": "deepseek-v4-pro",
                    "resolved": "deepseek-v4-pro-ga-260813",
                    "thinking": "disabled",
                    "provider_retry_limit": 0,
                }
            },
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _run_authorizer(self, root: Path, review: Path, identity: Path) -> tuple[subprocess.CompletedProcess[str], Path]:
        output = root / "authorization.json"
        result = subprocess.run(
            [
                sys.executable,
                str(AUTHORIZER),
                "--contract", str(CONTRACT),
                "--preflight", str(PREFLIGHT),
                "--review", str(review),
                "--fresh-identity", str(identity),
                "--output", str(output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return result, output

    def test_authorizer_refuses_stale_identity(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract_sha = file_sha(CONTRACT)
            review = self._write_review(root, contract_sha=contract_sha, passing=True)
            contract_time = datetime.fromisoformat(self.contract["created_at_utc"])
            identity = self._write_identity(root, created_at=contract_time - timedelta(seconds=1))
            result, output = self._run_authorizer(root, review, identity)
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())

    def test_authorizer_refuses_stale_web_review(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract_sha = file_sha(CONTRACT)
            contract_time = datetime.fromisoformat(self.contract["created_at_utc"])
            review = self._write_review(
                root,
                contract_sha=contract_sha,
                passing=True,
                created_at=contract_time - timedelta(seconds=1),
            )
            identity = self._write_identity(root, created_at=contract_time + timedelta(seconds=1))
            result, output = self._run_authorizer(root, review, identity)
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())

    def test_authorizer_refuses_nonpassing_web_review(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract_sha = file_sha(CONTRACT)
            review = self._write_review(root, contract_sha=contract_sha, passing=False)
            contract_time = datetime.fromisoformat(self.contract["created_at_utc"])
            identity = self._write_identity(root, created_at=contract_time + timedelta(seconds=1))
            result, output = self._run_authorizer(root, review, identity)
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())

    def test_authorizer_can_mint_only_exact_v3_stage_a_scope_in_temp(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract_sha = file_sha(CONTRACT)
            review = self._write_review(root, contract_sha=contract_sha, passing=True)
            contract_time = datetime.fromisoformat(self.contract["created_at_utc"])
            identity = self._write_identity(root, created_at=contract_time + timedelta(seconds=1))
            result, output = self._run_authorizer(root, review, identity)
            self.assertEqual(0, result.returncode, msg=result.stderr)
            self.assertTrue(output.is_file())
            auth = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A", auth["status"])
            self.assertEqual(160, len(auth["execution_scope"]["allowed_task_ids"]))
            self.assertEqual(file_sha(identity), auth["fresh_model_identity"]["sha256"])
            self.assertTrue(auth["authority"]["stage_a_provider_execution"])
            scope = auth["execution_scope"]
            self.assertEqual([1, 2, 4, 8], scope["exact_prefix_ks"])
            self.assertEqual(self.contract["actor"]["concurrency"], scope["exact_concurrency"])
            self.assertEqual(self.contract["run_root"], scope["required_run_root"])
            self.assertTrue(scope["runner_lease_required"])
            for key in (
                "stage_b_learning_execution",
                "updater",
                "heldout_evaluation",
                "analyzer",
                "second_backbone",
                "public_benchmark",
                "paper_promotion",
            ):
                self.assertFalse(auth["authority"][key])
            self.actor.validate_authority(
                mode="e1",
                authorization=output,
                task_ids=self.update_tasks[:8],
                split=self.split,
                k=8,
            )
            self.runner.verify_authorization_scope(self.contract, auth, self.update_tasks, self.heldout)


    def test_actor_runner_context_requires_active_bound_lease(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_root = root / "run"
            lease_path = root / "lease.json"
            contract_sha = "c" * 64
            authorization_sha = "a" * 64
            authorization = {
                "contract_sha256": contract_sha,
                "execution_scope": {
                    "required_run_root": str(run_root),
                    "exact_prefix_ks": [1, 2, 4, 8],
                    "exact_concurrency": 1,
                    "runner_lease_required": True,
                    "global_lease_path": str(lease_path),
                },
            }
            with self.assertRaises(RuntimeError):
                self.actor.validate_stage_a_runner_context(
                    authorization_payload=authorization,
                    authorization_sha=authorization_sha,
                    run_root=run_root,
                    prefix_ks=(1, 2, 4, 8),
                    concurrency=1,
                )
            lease_path.write_text(json.dumps({
                "status": "RUNNING_STAGE_A_V3",
                "contract_sha256": contract_sha,
                "authorization_sha256": authorization_sha,
                "run_root": str(run_root),
            }), encoding="utf-8")
            lease = self.actor.validate_stage_a_runner_context(
                authorization_payload=authorization,
                authorization_sha=authorization_sha,
                run_root=run_root,
                prefix_ks=(1, 2, 4, 8),
                concurrency=1,
            )
            self.assertEqual("RUNNING_STAGE_A_V3", lease["status"])
            with self.assertRaises(RuntimeError):
                self.actor.validate_stage_a_runner_context(
                    authorization_payload=authorization,
                    authorization_sha=authorization_sha,
                    run_root=run_root,
                    prefix_ks=(1, 8),
                    concurrency=1,
                )

    def test_actor_scientific_scope_forbids_noninitial_skill(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            default_skill = root / "default"
            alternate_skill = root / "alternate"
            authorization = {"execution_scope": {"allow_noninitial_skill": False}}
            self.actor.validate_initial_skill_scope(
                authorization_payload=authorization,
                skill_source=default_skill,
                default_skill_source=default_skill,
            )
            with self.assertRaises(RuntimeError):
                self.actor.validate_initial_skill_scope(
                    authorization_payload=authorization,
                    skill_source=alternate_skill,
                    default_skill_source=default_skill,
                )


if __name__ == "__main__":
    unittest.main()
