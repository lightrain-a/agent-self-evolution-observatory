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
CONTRACT = ROOT / "generated/e2-r17-semantic-transfer-v2-stage-a-v5-contract-20260903.json"
PREFLIGHT = ROOT / "generated/e2-r17-semantic-transfer-v2-stage-a-v5-preflight-20260903.json"
AUTHORIZER = ROOT / "scripts/authorize_e2_r17_semantic_transfer_v2_stage_a_v5.py"
ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v2_stage_a_v5.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SemanticTransferV2StageAControlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
        cls.adjudicator = load_module(ADJUDICATOR, "semantic_transfer_v2_adjudicator_test")

    def test_contract_and_preflight_have_zero_execution_authority(self) -> None:
        self.assertEqual("FROZEN_SEMANTIC_TRANSFER_V2_STAGE_A_V5", self.contract["status"])
        self.assertEqual("PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V2_STAGE_A_V5_PREFLIGHT", self.preflight["status"])
        self.assertFalse(self.contract["authority"]["stage_a_provider_execution"])
        self.assertFalse(self.contract["authority"]["stage_b_learning_execution"])
        self.assertFalse(self.preflight["authority"]["stage_a_provider_execution"])
        self.assertFalse(self.preflight["fresh_identity_qualified"])
        self.assertTrue(self.preflight["fresh_identity_required_before_authorization"])
        self.assertEqual(18, self.preflight["stream_count"])
        self.assertEqual(144, self.preflight["task_count"])

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
        split = json.loads(split_path.read_text(encoding="utf-8"))
        streams = split["e1_update_streams"]
        self.assertEqual(self.contract["suite"]["streams"], list(streams.keys()))
        updates = [task for tasks in streams.values() for task in tasks]
        heldout = list(split["e1_common_heldout_probe"])
        self.assertEqual(18, len(streams))
        self.assertTrue(all(len(tasks) == 8 for tasks in streams.values()))
        self.assertEqual(144, len(updates))
        self.assertEqual(144, len(set(updates)))
        self.assertEqual(18, len(heldout))
        self.assertFalse(set(updates) & set(heldout))

    def test_equal_dose_hash_selection_v2_is_order_invariant(self) -> None:
        tasks = [f"task-{index}" for index in range(8)]
        a = self.adjudicator.choose_four("stream-x", tasks)
        b = self.adjudicator.choose_four("stream-x", list(reversed(tasks)))
        self.assertEqual(a, b)
        expected = sorted(
            tasks,
            key=lambda task_id: hashlib.sha256(
                f"semantic-transfer-mrw4-v2|stream-x|{task_id}".encode("utf-8")
            ).hexdigest(),
        )[:4]
        self.assertEqual(expected, a)

    def test_reduction_router_rankings_are_deterministic(self) -> None:
        streams = [f"s{index:02d}" for index in range(18)]
        difficulty = {stream: index // 2 for index, stream in enumerate(streams)}
        mixedness = {stream: 8 - (index // 2) for index, stream in enumerate(streams)}
        hard_a = self.adjudicator.choose_nine_streams(
            streams, difficulty, descending=False, salt="semantic-transfer-difficulty-v2"
        )
        hard_b = self.adjudicator.choose_nine_streams(
            list(reversed(streams)), difficulty, descending=False, salt="semantic-transfer-difficulty-v2"
        )
        mixed_a = self.adjudicator.choose_nine_streams(
            streams, mixedness, descending=True, salt="semantic-transfer-mixedness-v2"
        )
        mixed_b = self.adjudicator.choose_nine_streams(
            list(reversed(streams)), mixedness, descending=True, salt="semantic-transfer-mixedness-v2"
        )
        self.assertEqual(hard_a, hard_b)
        self.assertEqual(mixed_a, mixed_b)
        self.assertEqual(9, len(hard_a))
        self.assertEqual(9, len(mixed_a))

    def _write_review_root(self, root: Path, *, contract_sha: str, dual_pass: bool = True) -> Path:
        review_root = root / "reviews"
        review_root.mkdir()
        summary = {
            "contract_sha256": contract_sha,
            "all_pass_to_separate_stage_a_authorization": dual_pass,
            "stage_b_authority": False,
            "paper_claim_authority": False,
        }
        (review_root / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        for model in ("deepseek-v4-pro", "kimi-k3"):
            row = {
                "status": "COMPLETED" if dual_pass else "FAIL_PROVIDER_PROTOCOL",
                "scientific_authority": False,
                "experiment_authority": False,
                "review": {
                    "contract_sha256_acknowledged": contract_sha,
                    "verdict": "PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION",
                    "execution_recommendation": "ALLOW_SEPARATE_STAGE_A_AUTHORIZATION",
                    "remaining_blockers": [],
                    "stage_b_authority": False,
                    "paper_claim_authority": False,
                } if dual_pass else {},
            }
            (review_root / f"{model}.json").write_text(json.dumps(row), encoding="utf-8")
        return review_root

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

    def _run_authorizer(self, root: Path, review_root: Path, identity: Path) -> tuple[subprocess.CompletedProcess[str], Path]:
        output = root / "authorization.json"
        result = subprocess.run(
            [
                sys.executable,
                str(AUTHORIZER),
                "--contract", str(CONTRACT),
                "--preflight", str(PREFLIGHT),
                "--review-root", str(review_root),
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
            review_root = self._write_review_root(root, contract_sha=contract_sha, dual_pass=True)
            contract_time = datetime.fromisoformat(self.contract["created_at_utc"])
            identity = self._write_identity(root, created_at=contract_time - timedelta(seconds=1))
            result, output = self._run_authorizer(root, review_root, identity)
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())

    def test_authorizer_refuses_nonpassing_dual_review(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract_sha = file_sha(CONTRACT)
            review_root = self._write_review_root(root, contract_sha=contract_sha, dual_pass=False)
            contract_time = datetime.fromisoformat(self.contract["created_at_utc"])
            identity = self._write_identity(root, created_at=contract_time + timedelta(seconds=1))
            result, output = self._run_authorizer(root, review_root, identity)
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())

    def test_authorizer_can_mint_only_with_dual_pass_and_fresh_identity_in_temp(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract_sha = file_sha(CONTRACT)
            review_root = self._write_review_root(root, contract_sha=contract_sha, dual_pass=True)
            contract_time = datetime.fromisoformat(self.contract["created_at_utc"])
            identity = self._write_identity(root, created_at=contract_time + timedelta(seconds=1))
            result, output = self._run_authorizer(root, review_root, identity)
            self.assertEqual(0, result.returncode, msg=result.stderr)
            self.assertTrue(output.is_file())
            auth = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("AUTHORIZED_SEMANTIC_TRANSFER_V2_STAGE_A_V5", auth["status"])
            self.assertEqual(144, len(auth["execution_scope"]["allowed_task_ids"]))
            self.assertEqual(file_sha(identity), auth["fresh_model_identity"]["sha256"])
            self.assertTrue(auth["authority"]["stage_a_provider_execution"])
            self.assertFalse(auth["authority"]["stage_b_learning_execution"])


if __name__ == "__main__":
    unittest.main()
