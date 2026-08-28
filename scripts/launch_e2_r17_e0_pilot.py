#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ACTOR_SCRIPT = ROOT / "scripts/run_e2_r17_actor_pool.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_authorization(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    require(payload.get("status") == "AUTHORIZED_E0", "authorization status is not AUTHORIZED_E0")
    authority = payload.get("authority") or {}
    require(authority.get("scientific_experiment") is True, "authorization lacks E0 scientific authority")
    require(authority.get("e0_pilot") is True, "authorization does not grant E0 pilot")
    require(authority.get("e0_full") is False, "authorization accidentally grants E0 full")
    require(authority.get("e1") is False, "authorization accidentally grants E1")
    require(authority.get("public_externality") is False, "authorization accidentally grants public externality")
    require(authority.get("paper_promotion") is False, "authorization accidentally grants paper promotion")
    require(payload.get("authorized_mode") == "e0", "authorized mode is not e0")
    task_ids = payload.get("authorized_task_ids") or []
    require(len(task_ids) == 12 and len(set(task_ids)) == 12, "authorization must bind exactly 12 unique tasks")
    require(payload.get("k") == 8, "authorization must bind K=8")
    require(payload.get("prefix_ks") == [1, 2, 4, 8], "authorization must bind nested prefixes 1/2/4/8")
    require(payload.get("requested_model") == "deepseek-v4-pro", "unexpected requested actor model")
    require(bool(payload.get("resolved_model")), "resolved actor model missing")
    require(payload.get("provider_retry_limit") == 0, "provider retry must be zero")
    require(payload.get("thinking") == "disabled", "thinking must be disabled")
    require(payload.get("temperature") == 0, "temperature must be zero")
    require(payload.get("resume_missing_units_only") is True, "resume policy must be missing-units-only")
    return payload


def validate_code(payload: dict[str, Any]) -> None:
    bound_commit = str(payload.get("research_git_commit") or "")
    require(len(bound_commit) == 40, "authorization lacks a full research Git commit")
    current = git("rev-parse", "HEAD")
    ancestry = subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", bound_commit, current],
        check=False,
    )
    require(ancestry.returncode == 0, "current HEAD is not descended from the authorized code commit")
    dirty = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--"], check=False)
    require(dirty.returncode == 0, "tracked worktree changes exist after authorization")
    staged = subprocess.run(["git", "-C", str(ROOT), "diff", "--cached", "--quiet", "--"], check=False)
    require(staged.returncode == 0, "staged worktree changes exist after authorization")
    for rel, expected in sorted((payload.get("code_sha256") or {}).items()):
        target = ROOT / rel
        require(target.is_file(), f"authorized code file missing: {rel}")
        require(sha256(target) == expected, f"authorized code drift: {rel}")


def validate_inputs(payload: dict[str, Any], authorization_path: Path) -> None:
    for key in ("suite_root", "mindmemos_root", "identity_path", "skill_source", "runtime_venv", "runtime_freeze_path"):
        require(Path(payload[key]).exists(), f"authorized path missing: {key}={payload[key]}")
    identity = Path(payload["identity_path"])
    require(sha256(identity) == payload["identity_sha256"], "identity artifact hash drift")
    skill_md = Path(payload["skill_source"]) / "SKILL.md"
    require(sha256(skill_md) == payload["skill_pre_sha256"], "initial skill hash drift")
    suite_root = Path(payload["suite_root"])
    require(sha256(suite_root / "suite_manifest.json") == payload["suite_manifest_sha256"], "suite manifest drift")
    require(
        sha256(suite_root / "r17_split_manifest.json") == payload["split_manifest_sha256"],
        "split manifest drift",
    )
    require(sha256(Path(payload["runtime_freeze_path"])) == payload["runtime_freeze_sha256"], "runtime freeze hash drift")
    require(sha256(authorization_path) == payload.get("self_sha256", sha256(authorization_path)), "authorization self hash drift")


def build_command(payload: dict[str, Any], authorization_path: Path) -> list[str]:
    runtime_python = Path(payload["runtime_venv"]) / "bin/python"
    require(runtime_python.is_file(), f"authorized runtime python missing: {runtime_python}")
    command = [
        str(runtime_python),
        str(ACTOR_SCRIPT),
        "--env-file",
        str(ROOT / ".env"),
        "--suite-root",
        payload["suite_root"],
        "--mindmemos-root",
        payload["mindmemos_root"],
        "--run-root",
        payload["run_root"],
        "--identity",
        payload["identity_path"],
        "--authorization",
        str(authorization_path),
        "--skill-source",
        payload["skill_source"],
        "--mode",
        "e0",
        "--model",
        payload["requested_model"],
        "--k",
        str(payload["k"]),
        "--prefix-ks",
        ",".join(str(value) for value in payload["prefix_ks"]),
        "--max-turns",
        str(payload["max_turns"]),
        "--max-output-tokens",
        str(payload["max_output_tokens"]),
        "--concurrency",
        str(payload["concurrency"]),
        "--output",
        payload["summary_path"],
    ]
    for task_id in payload["authorized_task_ids"]:
        command.extend(["--task-id", task_id])
    return command


def validate_completed_summary(payload: dict[str, Any]) -> None:
    summary_path = Path(payload["summary_path"])
    require(summary_path.is_file(), "actor completed without the authorized summary")
    summary = load_json(summary_path)
    require(summary.get("status") == "COMPLETED", "actor summary is not completed")
    require(summary.get("mode") == "e0", "actor summary mode drift")
    require(summary.get("contract_sha256") == payload["contract_sha256"], "summary contract hash drift")
    require(summary.get("authorization_sha256") == sha256(Path(payload["authorization_path"])), "summary authorization hash drift")
    require(summary.get("requested_model") == payload["requested_model"], "summary requested model drift")
    require(summary.get("resolved_model") == payload["resolved_model"], "summary resolved model drift")
    require(summary.get("provider_retry_limit") == 0, "summary provider retry drift")
    require(summary.get("thinking") == "disabled", "summary thinking drift")
    observed = [str(row["task_id"]) for row in summary.get("tasks") or []]
    require(observed == payload["authorized_task_ids"], "summary task order/allowlist drift")
    require(summary.get("k") == 8 and summary.get("prefix_ks") == [1, 2, 4, 8], "summary K/prefix drift")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorization", type=Path, required=True)
    args = parser.parse_args()
    authorization = args.authorization.resolve()
    payload = validate_authorization(authorization)
    # Store the resolved authorization path only in memory; the signed artifact
    # intentionally remains location-independent.
    payload["authorization_path"] = str(authorization)
    validate_code(payload)
    validate_inputs(payload, authorization)

    summary_path = Path(payload["summary_path"])
    if summary_path.exists():
        validate_completed_summary(payload)
        print(json.dumps({"status": "ALREADY_COMPLETED", "summary_path": str(summary_path)}, ensure_ascii=False))
        return 0

    env = os.environ.copy()
    runtime_venv = Path(payload["runtime_venv"])
    runtime_python = runtime_venv / "bin/python"
    env["VIRTUAL_ENV"] = str(runtime_venv)
    env["PATH"] = str(runtime_venv / "bin") + os.pathsep + env.get("PATH", "")
    import_check = subprocess.run(
        [
            str(runtime_python),
            "-c",
            (
                "import openpyxl,pydantic; "
                "assert openpyxl.__version__ == '3.1.5'; "
                "from mindmemos_eval.skills.agents import ReactAgentFactory; "
                "from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv"
            ),
        ],
        env=env,
        check=False,
    )
    require(import_check.returncode == 0, "frozen full MindMemOS runtime qualification failed")
    command = build_command(payload, authorization)
    result = subprocess.run(command, cwd=ROOT, env=env, check=False)
    require(result.returncode == 0, f"E0 actor runner failed with code {result.returncode}")
    validate_completed_summary(payload)
    print(json.dumps({"status": "COMPLETED", "summary_path": str(summary_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
