from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated/e2-r17-semantic-transfer-v1-stage-a-r2-contract-20260902.json"
PREFLIGHT = ROOT / "generated/e2-r17-semantic-transfer-v1-stage-a-r2-preflight-20260902.json"
AUTHORIZER = ROOT / "scripts/authorize_e2_r17_semantic_transfer_stage_a_r2.py"
ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_stage_a_v1.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SemanticTransferStageAControlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.adjudicator = load_module(ADJUDICATOR, "semantic_transfer_adjudicator_test")

    def test_r2_contract_has_zero_execution_authority(self) -> None:
        self.assertEqual("FROZEN_SEMANTIC_TRANSFER_V1_STAGE_A_R2", self.contract["status"])
        authority = self.contract["authority"]
        self.assertFalse(authority["stage_a_provider_execution"])
        self.assertFalse(authority["stage_b_learning_execution"])
        self.assertFalse(authority["updater"])
        self.assertFalse(authority["heldout_evaluation"])
        self.assertFalse(authority["analyzer"])
        self.assertTrue(self.contract["equal_dose_support"]["all_96_pools_must_be_sealed_before_support_read"])
        self.assertEqual(4, self.contract["equal_dose_support"]["required_mixed_pools_per_stream"])
        self.assertEqual(4, self.contract["equal_dose_support"]["treated_mixed_pools_per_stream"])

    def test_bound_code_hashes_match_contract(self) -> None:
        for label, item in self.contract["bound_code"].items():
            with self.subTest(label=label):
                path = ROOT / item["path"]
                self.assertTrue(path.is_file())
                observed = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(item["sha256"], observed)

    def test_bound_split_is_96_updates_and_18_disjoint_heldout(self) -> None:
        suite_root = Path(self.contract["suite"]["root"])
        split_path = suite_root / "r17_split_manifest.json"
        observed_sha = hashlib.sha256(split_path.read_bytes()).hexdigest()
        self.assertEqual(self.contract["suite"]["split_manifest_sha256"], observed_sha)
        split = json.loads(split_path.read_text(encoding="utf-8"))
        streams = split["e1_update_streams"]
        self.assertEqual(self.contract["suite"]["streams"], list(streams.keys()))
        updates = [task for tasks in streams.values() for task in tasks]
        heldout = list(split["e1_common_heldout_probe"])
        self.assertEqual(96, len(updates))
        self.assertEqual(96, len(set(updates)))
        self.assertEqual(18, len(heldout))
        self.assertEqual(18, len(set(heldout)))
        self.assertFalse(set(updates) & set(heldout))

    def test_equal_dose_hash_selection_is_order_invariant_and_exactly_four(self) -> None:
        tasks = [f"task-{index}" for index in range(8)]
        selected_a = self.adjudicator.choose_four("stream-x", tasks)
        selected_b = self.adjudicator.choose_four("stream-x", list(reversed(tasks)))
        self.assertEqual(selected_a, selected_b)
        self.assertEqual(4, len(selected_a))
        expected = sorted(
            tasks,
            key=lambda task_id: hashlib.sha256(
                f"semantic-transfer-mrw4-v1|stream-x|{task_id}".encode("utf-8")
            ).hexdigest(),
        )[:4]
        self.assertEqual(expected, selected_a)

    def test_equal_dose_selection_rejects_fewer_than_four_mixed(self) -> None:
        with self.assertRaises(RuntimeError):
            self.adjudicator.choose_four("stream-x", ["a", "b", "c"])

    def test_authorizer_refuses_nonpassing_review_without_writing_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            review_root = root / "reviews"
            review_root.mkdir()
            contract_sha = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
            summary = {
                "contract_sha256": contract_sha,
                "all_pass_to_separate_stage_a_authorization": False,
                "stage_b_authority": False,
                "paper_claim_authority": False,
            }
            (review_root / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
            for model in ("deepseek-v4-pro", "kimi-k3"):
                row = {
                    "status": "FAIL_PROVIDER_PROTOCOL",
                    "scientific_authority": False,
                    "experiment_authority": False,
                    "review": {},
                }
                (review_root / f"{model}.json").write_text(json.dumps(row), encoding="utf-8")
            output = root / "authorization.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(AUTHORIZER),
                    "--contract",
                    str(CONTRACT),
                    "--preflight",
                    str(PREFLIGHT),
                    "--review-root",
                    str(review_root),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())

    def test_authorizer_refuses_single_reviewer_or_drifted_review(self) -> None:
        contract_sha = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
        base_review = {
            "status": "COMPLETED",
            "scientific_authority": False,
            "experiment_authority": False,
            "review": {
                "contract_sha256_acknowledged": contract_sha,
                "verdict": "PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION",
                "execution_recommendation": "ALLOW_SEPARATE_STAGE_A_AUTHORIZATION",
                "remaining_blockers": [],
                "stage_b_authority": False,
                "paper_claim_authority": False,
            },
        }
        scenarios = {
            "single_reviewer_only": {
                "deepseek-v4-pro": base_review,
                "kimi-k3": {
                    "status": "FAIL_PROVIDER_PROTOCOL",
                    "scientific_authority": False,
                    "experiment_authority": False,
                    "review": {},
                },
            },
            "wrong_contract_ack": {
                "deepseek-v4-pro": base_review,
                "kimi-k3": {
                    **base_review,
                    "review": {**base_review["review"], "contract_sha256_acknowledged": "0" * 64},
                },
            },
            "overbroad_stage_b": {
                "deepseek-v4-pro": base_review,
                "kimi-k3": {
                    **base_review,
                    "review": {**base_review["review"], "stage_b_authority": True},
                },
            },
        }
        for name, rows in scenarios.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                review_root = root / "reviews"
                review_root.mkdir()
                summary = {
                    "contract_sha256": contract_sha,
                    "all_pass_to_separate_stage_a_authorization": True,
                    "stage_b_authority": False,
                    "paper_claim_authority": False,
                }
                (review_root / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
                for model, row in rows.items():
                    (review_root / f"{model}.json").write_text(json.dumps(row), encoding="utf-8")
                output = root / "authorization.json"
                result = subprocess.run(
                    [
                        sys.executable,
                        str(AUTHORIZER),
                        "--contract",
                        str(CONTRACT),
                        "--preflight",
                        str(PREFLIGHT),
                        "--review-root",
                        str(review_root),
                        "--output",
                        str(output),
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
