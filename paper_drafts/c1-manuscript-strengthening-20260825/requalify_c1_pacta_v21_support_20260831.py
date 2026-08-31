from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import run_c1_pacta_20260830 as legacy
from c1_pacta_v21_measurement import atomic_dump, journal_provider_response, parse_journaled_response

RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v21-p0-measurement-repair-20260831-v1")
QUAL_RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-v21-q0-measurement-20260831-v1")
MODEL = "doubao-seed-2.0-mini"
RESOLVED = "doubao-seed-2-0-mini-260215"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    if git("status", "--porcelain"):
        raise RuntimeError("support probe worktree must be clean and committed")
    qualification = json.loads((QUAL_RUN / "qualification.json").read_text(encoding="utf-8"))
    if qualification.get("status") != "PASS_MEASUREMENT_QUALIFICATION":
        raise RuntimeError("measurement qualification must pass before support probe")

    prompt = (
        "NON-SCIENTIFIC PROVIDER SUPPORT PROBE. Return exactly this JSON object and no prose:\n"
        '{"current_state":{"next_goal":"Wait for the synthetic page."},"action":[{"wait":{"seconds":1}}]}'
    )
    path = RUN / "model-support.json"
    request = {
        "case_id": "non-scientific-model-support-attempt-2",
        "artifact_kind": "C1_PACTA_V21_NON_SCIENTIFIC_MODEL_SUPPORT",
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
    }
    client, summary = legacy.client()
    response, raw = legacy.provider_call(client, prompt, 120, 0.2)
    journal_provider_response(path, request, response, raw)
    row = parse_journaled_response(path)
    passed = (
        row.get("status") == "complete"
        and row.get("requested_model") == MODEL
        and row.get("resolved_model") == RESOLVED
        and row.get("thinking_compatibility_fallback") is False
        and row.get("action_signature") == "wait"
    )
    row.update({
        "status": "SUPPORT_PASS" if passed else "STOP_SUPPORT",
        "scientific_state_used": False,
        "thinking": "disabled",
        "temperature": 0.2,
        "max_output_tokens": 120,
        "provider_retries": 0,
        "substitution": False,
        "schema_parse_pass": row.get("action_signature") == "wait",
        "provider_summary": summary,
        "execution_git_sha": git("rev-parse", "HEAD"),
        "completed_at": now(),
    })
    atomic_dump(path, row)
    manifest_path = RUN / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update({"status": row["status"], "support_probe_completed_at": row["completed_at"]})
    atomic_dump(manifest_path, manifest)
    print(json.dumps({
        "status": row["status"],
        "requested": row.get("requested_model"),
        "resolved": row.get("resolved_model"),
        "schema_parse_pass": row["schema_parse_pass"],
    }))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
