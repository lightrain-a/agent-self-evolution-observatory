"""Persist the targeted non-scientific Full-P1/Q10 test gate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT,
    utcnow,
    write_json,
)

OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-full-p1-targeted-test-gate-20260831.json"
MODULES = [
    "research_pipeline/test_asset_first_stri_reasoningbank_full_p1.py",
    "research_pipeline/test_asset_first_stri_reasoningbank_p1_q10_runtime.py",
    "research_pipeline/test_asset_first_stri_reasoningbank_p1_q10_stack.py",
]


def run(output: Path = OUTPUT) -> dict[str, object]:
    if output.exists():
        raise RuntimeError("refusing duplicate Full-P1 targeted test gate")
    command = [sys.executable, "-m", "pytest", "-q", *MODULES]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=180,
        check=False,
    )
    passed = completed.returncode == 0
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-FULL-P1-TARGETED-TEST-GATE-20260831",
        "created_at_utc": utcnow(),
        "decision": (
            "FULL_P1_TARGETED_TEST_GATE_PASS"
            if passed
            else "FULL_P1_TARGETED_TEST_GATE_HOLD"
        ),
        "command": command,
        "modules": MODULES,
        "returncode": completed.returncode,
        "output": completed.stdout,
        "pass": passed,
        "model_calls": 0,
        "evaluator_calls": 0,
        "task_outcomes_observed": False,
        "credential_material_present": False,
    }
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "pass": passed,
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
