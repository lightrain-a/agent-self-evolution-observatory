"""Freeze and execute zero-model evaluator qualification for Qwen STRI D0."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from research_pipeline import asset_first_stri_swebench_aria2_acquire as aria
from research_pipeline import asset_first_stri_swebench_oci_import as oci
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT,
    canonical_json,
    sha256_file,
    sha256_text,
    utcnow,
    write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    DaemonReconciledDockerRun,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_d0 import (
    DATASET,
    DATASET_SHA256,
    EXPERIMENT_ID,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_d0_rootful_runtime import (
    CONTRACT as ROOTFUL_REPAIR_CONTRACT,
    CONTRACT_SHA256 as ROOTFUL_REPAIR_CONTRACT_SHA256,
    ROOTFUL_DOCKER_HOST,
    activate as activate_rootful_runtime,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_evaluator import (
    OFFICIAL_PYTHON_PARSER_SHA256,
    PARSERS,
    SWEBENCH_VERSION,
    SWEBENCH_WHEEL_SHA256,
    grade_status_map,
    parse_status_map,
)

D0 = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-feasibility-20260901.json"
D0_SHA256 = "7ba0264dc410380c1f910d17eaeb1275789c06b8c3d8694cc87e01fd7e1e36fa"
CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-evaluator-contract-20260901.json"
INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-evaluator-index-20260901.json"
RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-evaluator-receipts-20260901"
MANIFEST_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-image-manifests-20260901"
RAW_LOG_DIR = Path("/data/wyt/e1-stri-reasoningbank-runtime/qwen-distribution-v3/d0-evaluator-raw-logs")
LAYOUT_ROOT = Path("/data/wyt/e1-stri-reasoningbank-runtime/qwen-distribution-v3/d0-oci-layouts")
MIRROR_ORDER = ("https://docker.1ms.run", "https://docker.1panel.live")
MIN_QUALIFIED_PER_REPO = 21
PRIMARY_REPOSITORY_COUNT = 4
FALLBACK_REPOSITORY_COUNT = 3
EVALUATOR_TIMEOUT_SECONDS = 1800
EXPECTED_CONTRACT_SHA256 = "c7cebba078363825668fd846d6599d291ae0bb1613b7494fdfceb1b1e51eb1f5"


class OperationalBlocker(RuntimeError):
    """An external/substrate failure that must not change task eligibility."""


class QualificationDockerRun(DaemonReconciledDockerRun):
    def __init__(self, image: str, base_commit: str, run_id: str) -> None:
        if "@sha256:" not in image:
            raise RuntimeError("qualification image is not digest-bound")
        super().__init__(
            image=image,
            base_commit=base_commit,
            run_id=run_id,
            expected_image_digest=image.rsplit("@", 1)[1],
            exact_base=True,
        )


def load_d0() -> dict[str, Any]:
    if sha256_file(D0) != D0_SHA256:
        raise RuntimeError("Qwen D0 artifact SHA drift")
    document = json.loads(D0.read_text(encoding="utf-8"))
    if document["decision"] != "D0_RAW_FEASIBILITY_FROZEN_EVALUATOR_QUALIFICATION_REQUIRED":
        raise RuntimeError("Qwen D0 decision drift")
    return document


def candidate_schedule() -> list[dict[str, Any]]:
    document = load_d0()
    raw_capacity = set(document["raw_capacity_repository_order"])
    rows = [
        {
            "ordinal": ordinal,
            "repo_hash_rank": row["repo_hash_rank"],
            "task_hash_rank_within_repo": row["task_hash_rank_within_repo"],
            "repo": row["repo"],
            "instance_id": row["instance_id"],
            "instance_id_sha256": row["instance_id_sha256"],
            "base_commit": row["base_commit"],
            "image_tag": row["image_tag"],
            "model_visible_task_sha256": row["model_visible_task_sha256"],
            "evaluator_contract_sha256": row["evaluator_contract_sha256"],
            "gold_patch_sha256": row["gold_patch_sha256"],
            "qualification_attempt_count": 1,
        }
        for ordinal, row in enumerate(
            (row for row in document["candidate_pool"] if row["repo"] in raw_capacity),
            start=1,
        )
    ]
    if len(rows) != 446:
        raise RuntimeError("D0 qualification candidate schedule count drift")
    return rows


def contract_payload() -> dict[str, Any]:
    schedule = candidate_schedule()
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "D0_ZERO_MODEL_EVALUATOR_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": "D0_ZERO_MODEL_EVALUATOR_QUALIFICATION_AUTHORIZED",
        "d0_artifact": str(D0.relative_to(ROOT)),
        "d0_artifact_sha256": D0_SHA256,
        "candidate_schedule": schedule,
        "candidate_schedule_sha256": sha256_text(canonical_json(schedule)),
        "repository_rule": {
            "minimum_zero_model_qualified_fresh_tasks": MIN_QUALIFIED_PER_REPO,
            "primary_repository_count": PRIMARY_REPOSITORY_COUNT,
            "fallback_repository_count": FALLBACK_REPOSITORY_COUNT,
            "order": "ascending SHA256(repo_name), then ascending SHA256(instance_id)",
            "stop_repo_after_qualified_capacity_proven": True,
            "stop_global_after_first_four_eligible_repositories": True,
            "uses_behavioral_outcomes": False,
            "uses_provider_calls": False,
        },
        "qualification_checks": [
            "exact task identity",
            "exact base commit",
            "exact linux/amd64 image manifest digest",
            "test patch availability",
            "evaluator script hash",
            "official parser family",
            "gold patch applies to exact base",
            "gold-patch evaluator raw returncode zero",
            "valid marker-bounded nonempty status map",
            "all FAIL_TO_PASS passed",
            "all PASS_TO_PASS maintained",
            "post-evaluator diff/status exactly equal pre-evaluator gold state",
            "container cleanup accepted",
        ],
        "gold_patch_boundary": {
            "allowed_use": "infrastructure/evaluator qualification only",
            "model_visible": False,
            "memory_visible": False,
            "prompt_visible": False,
            "task_selection_by_expected_model_result": False,
            "raw_log_persisted_outside_git": True,
            "raw_log_never_consumed_by_model_pipeline": True,
        },
        "official_evaluator": {
            "package": f"swebench=={SWEBENCH_VERSION}",
            "wheel_sha256": SWEBENCH_WHEEL_SHA256,
            "python_log_parser_sha256": OFFICIAL_PYTHON_PARSER_SHA256,
            "parser_semantics": "exact pinned compatibility implementation",
        },
        "transport_policy": {
            "manifest_and_blob_mirror_order": list(MIRROR_ORDER),
            "SHA256_verification_required": True,
            "operational_failure_changes_task_eligibility": False,
            "operational_failure_action": "pause same untouched qualification unit",
            "task_replacement_by_model_outcome": False,
        },
        "scientific_boundary": {
            "model_calls_authorized": False,
            "provider_calls_authorized": False,
            "behavioral_outcomes_observed": False,
            "source_generation_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }


def freeze_contract(output: Path = CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable D0 evaluator contract")
    payload = contract_payload()
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "candidate_count": len(payload["candidate_schedule"]),
        "model_calls": 0,
    }


def dataset_rows() -> dict[str, dict[str, Any]]:
    if sha256_file(DATASET) != DATASET_SHA256:
        raise RuntimeError("D0 evaluator dataset SHA drift")
    return {str(row["instance_id"]): row for row in pq.read_table(DATASET).to_pylist()}


def _run(command: list[str], timeout: int, *, docker: bool = False) -> dict[str, Any]:
    env = os.environ.copy()
    if docker:
        env["DOCKER_HOST"] = ROOTFUL_DOCKER_HOST
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            env=env,
            check=False,
        )
        return {"returncode": completed.returncode, "timed_out": False, "output": completed.stdout or ""}
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return {"returncode": None, "timed_out": True, "output": output}


def fetch_manifest(unit: dict[str, Any]) -> dict[str, Any]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    safe = unit["instance_id"].replace("__", "-").replace("_", "-")
    target = MANIFEST_DIR / f"{unit['ordinal']:03d}-{safe}-amd64.json"
    metadata_path = target.with_suffix(".receipt.json")
    if target.exists() and metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if "sha256:" + sha256_file(target) != metadata["manifest_digest"]:
            raise RuntimeError("persisted D0 manifest digest drift")
        return metadata
    errors = []
    for base in MIRROR_ORDER:
        host = base.removeprefix("https://")
        mirror_tag = host + "/" + unit["image_tag"]
        result = _run(["docker", "manifest", "inspect", "--verbose", mirror_tag], 300)
        if result["returncode"] != 0 or result["timed_out"]:
            errors.append({"mirror": base, "returncode": result["returncode"], "timed_out": result["timed_out"], "output_tail": result["output"][-500:]})
            continue
        try:
            records = json.loads(result["output"])
            if isinstance(records, dict):
                records = [records]
            matches = [
                row for row in records
                if (row.get("Descriptor") or {}).get("platform", {}).get("architecture") == "amd64"
                and (row.get("Descriptor") or {}).get("platform", {}).get("os") == "linux"
            ]
            if len(matches) != 1:
                raise ValueError("expected exactly one linux/amd64 manifest")
            selected = matches[0]
            raw = base64.b64decode(selected["Raw"])
            digest = "sha256:" + hashlib.sha256(raw).hexdigest()
            if digest != selected["Descriptor"]["digest"]:
                raise ValueError("manifest descriptor digest mismatch")
            manifest = json.loads(raw)
            if manifest.get("schemaVersion") != 2:
                raise ValueError("unexpected manifest schema")
        except Exception as error:
            errors.append({"mirror": base, "error_type": type(error).__name__, "message": str(error)})
            continue
        target.write_bytes(raw)
        metadata = {
            "instance_id": unit["instance_id"],
            "mirror_base": base,
            "mirror_repo": mirror_tag.removesuffix(":latest"),
            "download_repo": unit["image_tag"].removesuffix(":latest"),
            "manifest_path": str(target.relative_to(ROOT)),
            "manifest_digest": digest,
            "manifest_file_sha256": sha256_file(target),
            "manifest_media_type": selected["Descriptor"]["mediaType"],
            "manifest_size": selected["Descriptor"]["size"],
            "config_digest": manifest["config"]["digest"],
            "layer_count": len(manifest["layers"]),
            "layer_bytes": sum(int(row["size"]) for row in manifest["layers"]),
            "image_pull_reference": mirror_tag.removesuffix(":latest") + "@" + digest,
            "architecture": "amd64",
            "os": "linux",
            "credential_material_present": False,
        }
        write_json(metadata_path, metadata)
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    raise OperationalBlocker("all predeclared manifest mirrors unavailable: " + json.dumps(errors, sort_keys=True))


def acquire_and_import(unit: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    manifest_path = ROOT / metadata["manifest_path"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    descriptors = {str(item["digest"]): int(item["size"]) for item in [manifest["config"], *manifest["layers"]]}
    aria.CACHE.mkdir(parents=True, exist_ok=True)
    acquisition_rows, errors = [], []
    pending = dict(descriptors)
    for base in MIRROR_ORDER:
        if not pending:
            break
        aria.BASE = base
        current, pending = pending, {}
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {
                pool.submit(aria.acquire_one, digest, size, metadata["download_repo"]): (digest, size)
                for digest, size in current.items()
            }
            for future in as_completed(futures):
                digest, size = futures[future]
                try:
                    row = future.result()
                    acquisition_rows.append({"digest": digest, "size": size, "mirror_base": base, "status": row["status"], "sha256_verified": True})
                except Exception as error:
                    pending[digest] = size
                    errors.append({"digest": digest, "mirror_base": base, "error_type": type(error).__name__, "message": str(error)})
    if pending:
        raise OperationalBlocker("predeclared blob mirrors exhausted: " + json.dumps(errors, sort_keys=True))
    oci.LAYOUT_ROOT = LAYOUT_ROOT
    digest = metadata["manifest_digest"].removeprefix("sha256:")
    spec = {
        "label": f"d0-{unit['ordinal']:03d}-{unit['instance_id'].replace('__', '-')}",
        "repo": metadata["mirror_repo"],
        "tag": f"qwend0-{digest[:12]}",
        "manifest": manifest_path,
        "digest": digest,
    }
    try:
        imported = oci.import_one(spec)
    except Exception as error:
        raise OperationalBlocker(f"exact OCI import failed: {type(error).__name__}: {error}") from error
    inspect_output = ((imported.get("inspect") or {}).get("output") or "")
    if imported.get("pass") is not True or metadata["manifest_digest"] not in inspect_output or "amd64" not in inspect_output:
        raise OperationalBlocker("imported image lacks exact digest/architecture proof")
    archive, archive_sha = imported.get("archive"), imported.get("archive_sha256")
    archive_removed = False
    if archive and Path(archive).is_file():
        Path(archive).unlink()
        archive_removed = True
    return {
        "image_pull_reference": imported["digest_ref"],
        "manifest_digest": metadata["manifest_digest"],
        "architecture": "amd64",
        "download_rows": sorted(acquisition_rows, key=lambda row: row["digest"]),
        "all_blobs_sha256_verified": len(acquisition_rows) == len(descriptors),
        "import_status": imported["status"],
        "import_archive_sha256": archive_sha,
        "temporary_import_archive_removed": archive_removed,
        "exact_digest_visible": metadata["manifest_digest"] in inspect_output,
        "architecture_amd64_visible": "amd64" in inspect_output,
    }

def _docker_copy(source: Path, container_name: str, target: str) -> dict[str, Any]:
    return _run(["docker", "cp", str(source), f"{container_name}:{target}"], 120, docker=True)


def qualification_failure(
    unit: dict[str, Any],
    error: Exception,
    *,
    runtime_receipt: dict[str, Any] | None,
    started_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "D0_ZERO_MODEL_EVALUATOR_QUALIFICATION",
        "created_at_utc": started_at,
        "finished_at_utc": utcnow(),
        "ordinal": unit["ordinal"],
        "repo": unit["repo"],
        "repo_hash_rank": unit["repo_hash_rank"],
        "task_hash_rank_within_repo": unit["task_hash_rank_within_repo"],
        "instance_id": unit["instance_id"],
        "qualification_attempt_count": 1,
        "qualification_status": "UNQUALIFIED",
        "qualified": False,
        "failure": {
            "failure_layer": "evaluator_or_task_infrastructure",
            "error_type": type(error).__name__,
            "message": str(error),
        },
        "runtime_receipt": runtime_receipt,
        "model_calls": 0,
        "provider_calls": 0,
        "behavioral_outcomes_observed": False,
        "gold_patch_model_visible": False,
        "credential_material_present": False,
    }


def qualify_task(
    unit: dict[str, Any],
    row: dict[str, Any],
    manifest_meta: dict[str, Any],
    image_receipt: dict[str, Any],
) -> dict[str, Any]:
    container = QualificationDockerRun(
        image=image_receipt["image_pull_reference"],
        base_commit=str(row["base_commit"]),
        run_id=f"qwen-d0-{unit['ordinal']:03d}-{unit['instance_id']}",
    )
    runtime_receipt: dict[str, Any] | None = None
    started_at = utcnow()
    try:
        runtime_receipt = container.start()
    except Exception as error:
        cleanup = container.close()
        message = str(error)
        if "normalization" not in message and "base commit" not in message:
            raise OperationalBlocker(
                f"container substrate failed before task qualification: {type(error).__name__}: {error}"
            ) from error
        receipt = qualification_failure(
            unit, error, runtime_receipt=runtime_receipt, started_at=started_at
        )
        receipt["container_cleanup_receipt"] = cleanup
        return receipt

    receipt: dict[str, Any]
    raw_log_path = RAW_LOG_DIR / f"{unit['ordinal']:03d}-{unit['instance_id'].replace('__', '-')}.log"
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix="e1-qwen-d0-gold-",
            suffix=".patch",
            delete=False,
        ) as stream:
            stream.write(str(row["patch"]))
            host_patch = Path(stream.name)
        try:
            copied = _docker_copy(host_patch, container.name, "/tmp/e1-qwen-d0-gold.patch")
        finally:
            host_patch.unlink(missing_ok=True)
        if copied["returncode"] != 0 or copied["timed_out"]:
            raise RuntimeError("gold patch transfer failed")
        apply_check = container.exec("git apply --check /tmp/e1-qwen-d0-gold.patch", timeout=120)
        applied = container.exec("git apply /tmp/e1-qwen-d0-gold.patch", timeout=120)
        removed = container.exec("rm -f /tmp/e1-qwen-d0-gold.patch", timeout=30)
        if any(
            result["returncode"] != 0 or result["timed_out"]
            for result in (apply_check, applied, removed)
        ):
            raise RuntimeError("gold patch did not apply cleanly to frozen base")
        state_command = (
            f"git -c core.fileMode=false diff --binary {row['base_commit']} && "
            "printf '\\n__STATUS__\\n' && "
            "git status --porcelain=v1 --untracked-files=all"
        )
        pre = container.exec(state_command, timeout=120)
        if pre["returncode"] != 0 or pre["timed_out"]:
            raise RuntimeError("unable to capture gold-patch pre-evaluator state")
        pre_state_sha = sha256_text(pre["output"])
        evaluation = container.exec(str(row["eval_script"]), timeout=EVALUATOR_TIMEOUT_SECONDS)
        RAW_LOG_DIR.mkdir(parents=True, exist_ok=True)
        raw_log_path.write_text(evaluation["output"], encoding="utf-8")
        raw_log_sha = sha256_file(raw_log_path)
        status_map = parse_status_map(str(row["log_parser"]), evaluation["output"])
        grade = grade_status_map(
            status_map,
            list(row["FAIL_TO_PASS"]),
            list(row["PASS_TO_PASS"]),
        )
        post = container.exec(state_command, timeout=120)
        post_state_sha = sha256_text(post["output"])
        markers_valid = (
            ">>>>> Start Test Output" in evaluation["output"]
            and ">>>>> End Test Output" in evaluation["output"]
        )
        checks = {
            "task_identity_exact": str(row["instance_id"]) == unit["instance_id"],
            "base_commit_exact": (
                runtime_receipt["base_commit_receipt"]["observed_head"].strip()
                == str(row["base_commit"])
            ),
            "image_digest_exact": image_receipt["exact_digest_visible"],
            "architecture_amd64": image_receipt["architecture_amd64_visible"],
            "test_patch_available": bool(str(row["test_patch"]).strip()),
            "eval_script_available": bool(str(row["eval_script"]).strip()),
            "official_parser_family_supported": str(row["log_parser"]) in PARSERS,
            "gold_patch_sha_exact": sha256_text(str(row["patch"])) == unit["gold_patch_sha256"],
            "gold_patch_applied": applied["returncode"] == 0 and not applied["timed_out"],
            "evaluator_not_timed_out": not evaluation["timed_out"],
            "evaluator_returncode_zero": evaluation["returncode"] == 0,
            "test_output_markers_valid": markers_valid,
            "status_map_nonempty": bool(status_map),
            "all_fail_to_pass": bool(grade["all_fail_to_pass"]),
            "all_pass_to_pass": bool(grade["all_pass_to_pass"]),
            "gold_state_observable_before_eval": bool(pre["output"]),
            "post_eval_state_observable": post["returncode"] == 0 and not post["timed_out"],
            "evaluator_cleanup_diff_exact": pre_state_sha == post_state_sha,
        }
        receipt = {
            "schema_version": 1,
            "experiment_id": EXPERIMENT_ID,
            "stage": "D0_ZERO_MODEL_EVALUATOR_QUALIFICATION",
            "created_at_utc": started_at,
            "finished_at_utc": utcnow(),
            "ordinal": unit["ordinal"],
            "repo": unit["repo"],
            "repo_hash_rank": unit["repo_hash_rank"],
            "task_hash_rank_within_repo": unit["task_hash_rank_within_repo"],
            "instance_id": unit["instance_id"],
            "qualification_attempt_count": 1,
            "task_receipt": {
                "model_visible_task_sha256": unit["model_visible_task_sha256"],
                "base_commit": str(row["base_commit"]),
                "image_tag": str(row["image"]),
                "image_manifest": manifest_meta,
                "image_runtime": image_receipt,
                "eval_type": str(row["eval_type"]),
                "eval_script_sha256": sha256_text(str(row["eval_script"])),
                "test_patch_sha256": sha256_text(str(row["test_patch"])),
                "test_patch_available": bool(str(row["test_patch"]).strip()),
                "log_parser": str(row["log_parser"]),
                "FAIL_TO_PASS": grade["FAIL_TO_PASS"],
                "PASS_TO_PASS": grade["PASS_TO_PASS"],
                "status_map": status_map,
                "gold_patch_sha256": unit["gold_patch_sha256"],
                "gold_patch_content_persisted_in_receipt": False,
                "raw_evaluator_log_path": str(raw_log_path),
                "raw_evaluator_log_sha256": raw_log_sha,
                "raw_evaluator_log_model_visible": False,
                "evaluator_returncode": evaluation["returncode"],
                "evaluator_timed_out": evaluation["timed_out"],
                "pre_evaluator_gold_state_sha256": pre_state_sha,
                "post_evaluator_state_sha256": post_state_sha,
            },
            "runtime_receipt": runtime_receipt,
            "checks": checks,
            "model_calls": 0,
            "provider_calls": 0,
            "behavioral_outcomes_observed": False,
            "gold_patch_model_visible": False,
            "credential_material_present": False,
        }
    except Exception as error:
        receipt = qualification_failure(
            unit, error, runtime_receipt=runtime_receipt, started_at=started_at
        )
    cleanup = container.close()
    receipt["container_cleanup_receipt"] = cleanup
    if "checks" in receipt:
        receipt["checks"]["container_cleanup_accepted"] = bool(cleanup["accepted"])
        receipt["qualified"] = all(receipt["checks"].values())
        receipt["qualification_status"] = (
            "QUALIFIED" if receipt["qualified"] else "UNQUALIFIED"
        )
    return receipt


def receipt_path(unit: dict[str, Any]) -> Path:
    safe = unit["instance_id"].replace("__", "-").replace("_", "-")
    return RECEIPT_DIR / f"{unit['ordinal']:03d}-{safe}.json"


def existing_receipts(schedule: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    by_ordinal = {row["ordinal"]: row for row in schedule}
    if not RECEIPT_DIR.exists():
        return result
    for path in sorted(RECEIPT_DIR.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        ordinal = int(document["ordinal"])
        if ordinal not in by_ordinal:
            raise RuntimeError("D0 evaluator receipt ordinal outside frozen schedule")
        unit = by_ordinal[ordinal]
        if document["instance_id"] != unit["instance_id"]:
            raise RuntimeError("D0 evaluator receipt identity drift")
        if document["qualification_attempt_count"] != 1:
            raise RuntimeError("D0 evaluator qualification attempt-count drift")
        result[ordinal] = document
    return result

def repository_state(
    schedule: list[dict[str, Any]],
    completed: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    repos = []
    for repo in dict.fromkeys(row["repo"] for row in schedule):
        units = [row for row in schedule if row["repo"] == repo]
        receipts = [completed[row["ordinal"]] for row in units if row["ordinal"] in completed]
        qualified = [row for row in receipts if row["qualified"]]
        remaining = len(units) - len(receipts)
        repos.append(
            {
                "repo": repo,
                "repo_hash_rank": units[0]["repo_hash_rank"],
                "candidate_count": len(units),
                "completed_count": len(receipts),
                "qualified_count": len(qualified),
                "unqualified_count": len(receipts) - len(qualified),
                "remaining_count": remaining,
                "eligibility": (
                    "ELIGIBLE"
                    if len(qualified) >= MIN_QUALIFIED_PER_REPO
                    else (
                        "INELIGIBLE"
                        if len(qualified) + remaining < MIN_QUALIFIED_PER_REPO
                        else "PENDING"
                    )
                ),
                "qualified_task_ids": [row["instance_id"] for row in qualified],
            }
        )
    return repos


def next_unit(
    schedule: list[dict[str, Any]],
    completed: dict[int, dict[str, Any]],
) -> dict[str, Any] | None:
    state = repository_state(schedule, completed)
    if sum(row["eligibility"] == "ELIGIBLE" for row in state) >= PRIMARY_REPOSITORY_COUNT:
        return None
    for repo_state in state:
        if repo_state["eligibility"] != "PENDING":
            continue
        for unit in (row for row in schedule if row["repo"] == repo_state["repo"]):
            if unit["ordinal"] not in completed:
                return unit
    return None


def index_payload(
    schedule: list[dict[str, Any]],
    completed: dict[int, dict[str, Any]],
    *,
    operational_blocker: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = repository_state(schedule, completed)
    eligible = [row for row in state if row["eligibility"] == "ELIGIBLE"]
    execution_complete = len(eligible) >= PRIMARY_REPOSITORY_COUNT or all(
        row["eligibility"] != "PENDING" for row in state
    )
    if len(eligible) >= PRIMARY_REPOSITORY_COUNT:
        decision = "D0_PRIMARY_FOUR_REPOSITORY_EVALUATOR_FEASIBILITY_PASS"
        selected = eligible[:PRIMARY_REPOSITORY_COUNT]
        design = "PRIMARY_4_REPOSITORY"
    elif execution_complete and len(eligible) >= FALLBACK_REPOSITORY_COUNT:
        decision = "D0_FALLBACK_THREE_REPOSITORY_EVALUATOR_FEASIBILITY_PASS"
        selected = eligible[:FALLBACK_REPOSITORY_COUNT]
        design = "FALLBACK_3_REPOSITORY"
    elif execution_complete:
        decision = "HOLD_NO_QUALIFIED_MULTI_REPOSITORY_DATASET"
        selected = []
        design = None
    else:
        decision = "D0_EVALUATOR_QUALIFICATION_IN_PROGRESS"
        selected = []
        design = None
    journal = []
    for ordinal in sorted(completed):
        document = completed[ordinal]
        unit = {"ordinal": ordinal, "instance_id": document["instance_id"]}
        path = receipt_path(unit)
        journal.append(
            {
                "ordinal": ordinal,
                "instance_id": document["instance_id"],
                "repo": document["repo"],
                "qualification_status": document["qualification_status"],
                "qualified": document["qualified"],
                "qualification_attempt_count": document["qualification_attempt_count"],
                "receipt_path": str(path.relative_to(ROOT)),
                "receipt_sha256": sha256_file(path),
                "persisted": True,
            }
        )
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "D0_ZERO_MODEL_EVALUATOR_QUALIFICATION",
        "updated_at_utc": utcnow(),
        "decision": decision,
        "execution_complete": execution_complete,
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": sha256_file(CONTRACT),
        "candidate_schedule_sha256": sha256_text(canonical_json(schedule)),
        "repository_state": state,
        "selected_design": design,
        "selected_repositories": [row["repo"] for row in selected],
        "selected_qualified_task_ids": {
            row["repo"]: row["qualified_task_ids"][:MIN_QUALIFIED_PER_REPO]
            for row in selected
        },
        "completed_qualification_count": len(completed),
        "journal_record_count": len(journal),
        "journal": journal,
        "operational_blocker": operational_blocker,
        "runtime_repair": {
            "contract_path": str(ROOTFUL_REPAIR_CONTRACT.relative_to(ROOT)),
            "contract_sha256": ROOTFUL_REPAIR_CONTRACT_SHA256,
            "docker_host_for_new_units": ROOTFUL_DOCKER_HOST,
            "completed_pre_repair_receipts_remain_immutable": True,
        },
        "checks": {
            "journal_count_matches_completed": len(journal) == len(completed),
            "every_attempt_count_one": all(row["qualification_attempt_count"] == 1 for row in journal),
            "every_receipt_persisted": all(row["persisted"] for row in journal),
            "no_provider_calls": True,
            "no_model_calls": True,
            "no_behavioral_outcomes_observed": True,
            "credential_material_absent": True,
        },
        "scientific_boundary": {
            "provider_calls_authorized": False,
            "source_generation_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }


def run(index_path: Path = INDEX) -> dict[str, Any]:
    if EXPECTED_CONTRACT_SHA256 == "PENDING":
        raise RuntimeError("D0 evaluator contract SHA has not been pinned")
    if sha256_file(CONTRACT) != EXPECTED_CONTRACT_SHA256:
        raise RuntimeError("D0 evaluator contract SHA drift")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["decision"] != "D0_ZERO_MODEL_EVALUATOR_QUALIFICATION_AUTHORIZED":
        raise RuntimeError("D0 evaluator qualification unauthorized")
    activate_rootful_runtime()
    schedule = candidate_schedule()
    if sha256_text(canonical_json(schedule)) != contract["candidate_schedule_sha256"]:
        raise RuntimeError("D0 evaluator schedule drift")
    rows = dataset_rows()
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    completed = existing_receipts(schedule)
    write_json(index_path, index_payload(schedule, completed))
    while True:
        unit = next_unit(schedule, completed)
        if unit is None:
            final = index_payload(schedule, completed)
            write_json(index_path, final)
            return {
                "decision": final["decision"],
                "execution_complete": final["execution_complete"],
                "completed_qualification_count": len(completed),
                "selected_repositories": final["selected_repositories"],
                "index_sha256": sha256_file(index_path),
            }
        try:
            manifest = fetch_manifest(unit)
            image = acquire_and_import(unit, manifest)
            receipt = qualify_task(unit, rows[unit["instance_id"]], manifest, image)
        except OperationalBlocker as error:
            blocker = {
                "instance_id": unit["instance_id"],
                "ordinal": unit["ordinal"],
                "failure_layer": "environment_or_transport",
                "error_type": type(error).__name__,
                "message": str(error),
                "changes_task_eligibility": False,
                "authorized_next_action": "resume same untouched qualification unit",
            }
            write_json(index_path, index_payload(schedule, completed, operational_blocker=blocker))
            raise
        target = receipt_path(unit)
        if target.exists():
            raise RuntimeError("refusing to overwrite D0 evaluator task receipt")
        write_json(target, receipt)
        completed[unit["ordinal"]] = json.loads(target.read_text(encoding="utf-8"))
        write_json(index_path, index_payload(schedule, completed))
        print(
            json.dumps(
                {
                    "ordinal": unit["ordinal"],
                    "instance_id": unit["instance_id"],
                    "repo": unit["repo"],
                    "qualified": receipt["qualified"],
                    "completed": len(completed),
                },
                sort_keys=True,
            ),
            flush=True,
        )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    args = parser.parse_args()
    result = freeze_contract() if args.freeze_contract else run()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
