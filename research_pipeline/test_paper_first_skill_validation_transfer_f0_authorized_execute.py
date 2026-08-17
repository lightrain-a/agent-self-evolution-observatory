from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from .paper_first_skill_validation_transfer_f0 import ARMS, CANDIDATE_ID, SCHEDULE_TASKS_PER_ARM, build_plan
from .paper_first_skill_validation_transfer_f0_authorized_execute import (
    _load_arm_rows,
    build_arm_command,
    claim_permit_once,
)


class SkillValidationTransferAuthorizedExecuteTest(unittest.TestCase):
    def tempdir(self, prefix: str) -> Path:
        root = Path(tempfile.mkdtemp(prefix=prefix))
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def test_arm_command_is_frozen_to_gemini_seed_a_and_explicit_gemini_key_route(self) -> None:
        command = build_arm_command(
            python=Path("/runtime/venv/bin/python"),
            source_root=Path("/runtime/SkillEvolBench"),
            workspace_root=Path("/runtime/runs"),
            arm=ARMS[0],
            run_id="pa05-demo__raw",
            dry_run=False,
        )
        joined = " ".join(command)
        self.assertIn("--baseline-name raw_trajectory_rag", joined)
        self.assertIn("--model-yaml configs/models/gemini-3-flash.yaml", joined)
        self.assertIn("--order-seed A", joined)
        self.assertIn("--api-key-env-var GEMINI_API_KEY", joined)
        self.assertNotIn("--dry-run", command)

    def test_dry_run_flag_is_explicit_and_does_not_change_arm_identity(self) -> None:
        command = build_arm_command(
            python=Path("/runtime/venv/bin/python"),
            source_root=Path("/runtime/SkillEvolBench"),
            workspace_root=Path("/runtime/runs"),
            arm=ARMS[1],
            run_id="pa05-demo__selfgen",
            dry_run=True,
        )
        self.assertEqual("selfgen_experience_always", command[command.index("--baseline-name") + 1])
        self.assertIn("--dry-run", command)

    def test_single_use_human_permit_cannot_be_claimed_twice(self) -> None:
        control = self.tempdir("pa05-controller-claim-")
        human = {
            "artifact_sha256": hashlib.sha256(b"permit").hexdigest(),
            "source_message_sha256": hashlib.sha256(b"explicit approval").hexdigest(),
        }
        first = claim_permit_once(control, human, "pa05-run-a")
        state = json.loads(first.read_text(encoding="utf-8"))
        self.assertEqual(CANDIDATE_ID, state["candidate_id"])
        self.assertEqual(build_plan()["plan_sha256"], state["plan_hash"])
        with self.assertRaisesRegex(RuntimeError, "single-use"):
            claim_permit_once(control, human, "pa05-run-b")

    def test_arm_rows_require_exact_270_record_coverage(self) -> None:
        run_dir = self.tempdir("pa05-arm-rows-")
        records = run_dir / "stores" / "replay" / "records"
        records.mkdir(parents=True)
        for i in range(SCHEDULE_TASKS_PER_ARM):
            (records / f"r{i:03d}.json").write_text(json.dumps({"task_id": f"t{i}"}) + "\n", encoding="utf-8")
        self.assertEqual(SCHEDULE_TASKS_PER_ARM, len(_load_arm_rows(run_dir)))
        (records / "r000.json").unlink()
        with self.assertRaisesRegex(RuntimeError, "exactly 270"):
            _load_arm_rows(run_dir)


if __name__ == "__main__":
    unittest.main()
