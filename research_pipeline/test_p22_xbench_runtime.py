from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .p22_xbench_runtime import (
    CANDIDATE_ID,
    CONTRACT_SHA256,
    HARNESS_PLAN_SHA256,
    execute_unit,
    prediction_manifest_valid,
)


class P22XBenchRuntimeTest(unittest.TestCase):
    def test_evaluation_is_locked_without_prediction_manifest(self):
        with self.assertRaisesRegex(RuntimeError, "evaluation-locked"):
            execute_unit(
                phase="evaluation",
                task_id="40",
                kval=1,
                memevolve_root=Path("/does/not/matter"),
                xbench_root=Path("/does/not/matter"),
                prediction_manifest=None,
            )

    def test_prediction_manifest_digest_is_verified(self):
        core = {
            "schema_version": "1.0",
            "status": "P22_EVALUATION_PREDICTIONS_COMMITTED",
            "candidate_id": CANDIDATE_ID,
            "contract_sha256": CONTRACT_SHA256,
            "harness_plan_sha256": HARNESS_PLAN_SHA256,
            "evaluation_predictions": [],
            "scientific_authority": False,
        }
        core["prediction_manifest_sha256"] = hashlib.sha256(
            json.dumps(core, ensure_ascii=False, sort_keys=True, separators=(",", ":"), skipkeys=False).encode()
        ).hexdigest()
        # Digest is defined over the object before adding its digest field.
        no_digest = dict(core); no_digest.pop("prediction_manifest_sha256")
        core["prediction_manifest_sha256"] = hashlib.sha256(
            json.dumps(no_digest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "prediction.json"
            path.write_text(json.dumps(core), encoding="utf-8")
            ok, digest = prediction_manifest_valid(path)
            self.assertTrue(ok)
            self.assertEqual(digest, core["prediction_manifest_sha256"])
            core["candidate_id"] = "OTHER"
            path.write_text(json.dumps(core), encoding="utf-8")
            ok, reason = prediction_manifest_valid(path)
            self.assertFalse(ok)
            self.assertEqual(reason, "prediction-manifest-contract")


if __name__ == "__main__":
    unittest.main()
