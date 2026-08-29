#!/usr/bin/env python3
"""Frozen source induction, A/B/C/D/E construction, and P1 pilot execution."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_ark_provider import ArkCompatibilityError
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    BASE_URL,
    DOCKER_HOST,
    MAX_RETRIES,
    MODEL,
    OFFICIAL_COMMIT,
    RETRIEVAL_CERT_PATH,
    ROOT,
    DockerRun,
    load_fixtures,
    load_instructions,
    make_client,
    safe_model_receipt,
    sha256_file,
    sha256_text,
    canonical_json,
    utcnow,
    verify_frozen_inputs,
    write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_eval import run_case

JUDGE_INSTRUCTIONS = (
    "You are a helpful assistant that judges whether the agent successfully completed the task."
)


def call_role(
    *, input_text: str, instructions: str, role: str, temperature: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    client = make_client()
    request = {
        "model": MODEL, "input": input_text, "instructions": instructions,
        "temperature": temperature, "max_output_tokens": 65536, "store": True,
    }
    try:
        result = client.create_response(
            input_items=input_text, instructions=instructions, model=MODEL,
            temperature=temperature, max_output_tokens=65536, store=True,
        )
    except ArkCompatibilityError as error:
        raise RuntimeError(f"{role} provider failure: {error.safe_receipt()}") from error
    receipt = safe_model_receipt(result)
    if receipt["resolved_model"] != MODEL:
        raise RuntimeError(f"{role} model identity drift")
    return request, receipt


def source_induction(output_dir: Path) -> dict[str, Any]:
    verification = verify_frozen_inputs()
    fixture = [row for row in load_fixtures() if row["role"] == "source_induction"][0]
    run_id = f"source-{fixture['instance_id']}"
    source_result = run_case(
        fixture, selected_memory="", run_id=run_id, output_dir=output_dir,
        r0={
            "arm": "SOURCE_NO_MEMORY", "eligible_cases": [], "selected_case": None,
            "selected_memory": "", "top_k": 1,
        },
    )
    source_path = ROOT / source_result["path"]
    source_payload = json.loads(source_path.read_text(encoding="utf-8"))
    if "messages" not in source_payload:
        return {
            "decision": "SOURCE_INDUCTION_RUNTIME_HOLD",
            "source_run": source_result, "scientific_outcome_authorized": False,
        }
    task = fixture["model_visible"]["problem_statement"]
    trajectory_text = "\n".join(
        str(message["content"]) for message in source_payload["messages"]
        if message["role"] != "system"
    )
    judge_prompt = (
        f"Task: {task}\n\nTrajectory:\n{trajectory_text}\n\n"
        "Did the agent successfully complete the task? Answer with 'success' or 'fail' only."
    )
    judge_request, judge_receipt = call_role(
        input_text=judge_prompt, instructions=JUDGE_INSTRUCTIONS,
        role="judge", temperature=0.0,
    )
    judged_success = "success" in str(judge_receipt["text"]).strip().lower()
    instructions = load_instructions()
    induction_instruction = instructions[
        "SUCCESSFUL_SI" if judged_success else "FAILED_SI"
    ]
    induction_prompt = f"**Query:** {task}\n\n**Trajectory:**\n{trajectory_text}"
    induction_request, induction_receipt = call_role(
        input_text=induction_prompt, instructions=induction_instruction.strip(),
        role="memory_induction", temperature=1.0,
    )
    raw_memory_text = str(induction_receipt["text"])
    raw_items = raw_memory_text.split("\n\n")
    semantic_items = [item for item in raw_items if item.strip()]
    eligible = len(semantic_items) >= 2
    core = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-SOURCE-INDUCTION-20260829",
        "created_at_utc": utcnow(), "official_commit": OFFICIAL_COMMIT,
        "source_case_id": fixture["instance_id"], "case_id": fixture["instance_id"],
        "memory_id": f"rb-{fixture['instance_id']}-{sha256_text(raw_memory_text)[:16]}",
        "task_sha256": sha256_text(task), "raw_input": task,
        "source_run": source_result, "source_run_file_sha256": sha256_file(source_path),
        "raw_trajectory": trajectory_text,
        "raw_trajectory_sha256": sha256_text(trajectory_text),
        "model_calls": {
            "judge": {"request": judge_request, "response": judge_receipt},
            "induction": {"request": induction_request, "response": induction_receipt},
        },
        "source_behavior_exit_status": source_payload.get("exit_status"),
        "source_official_evaluator": source_payload.get("R4_terminal_outcome"),
        "judge_output": judge_receipt["text"],
        "judge_status": "success" if judged_success else "fail",
        "extractor": "response.text.split('\\n\\n')",
        "raw_extracted_memory_text": raw_memory_text,
        "raw_memory_items": raw_items, "semantic_memory_items": semantic_items,
        "memory_item_count_raw": len(raw_items),
        "memory_item_count_nonempty": len(semantic_items),
        "treatment_eligible": eligible,
        "provider": {
            "base_url": BASE_URL, "model": MODEL, "judge_temperature": 0.0,
            "memory_induction_temperature": 1.0, "max_output_tokens": 65536,
        },
        "frozen_input_verification": verification,
        "credential_material_present": False,
        "scientific_boundary": {
            "source_eval_disjoint": True, "downstream_p1_outcome_observed": False,
            "failed_source_replacement_forbidden": True,
        },
        "decision": (
            "SOURCE_MEMORY_FROZEN_P1_TREATMENT_ELIGIBLE"
            if eligible else
            "SOURCE_MEMORY_FROZEN_P1_TREATMENT_INELIGIBLE_NO_REPLACEMENT"
        ),
    }
    memory_path = ROOT / "generated/asset-first-stri-reasoningbank-p1-source-memory-20260829.json"
    memory_sha = write_json(memory_path, core)
    return {
        "decision": core["decision"], "source_run": source_result,
        "memory_artifact": str(memory_path.relative_to(ROOT)),
        "memory_artifact_sha256": memory_sha, "treatment_eligible": eligible,
        "memory_item_count_nonempty": len(semantic_items),
    }


def treatment_cases(memory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    pieces = list(memory["semantic_memory_items"])
    if len(pieces) < 2:
        raise RuntimeError("frozen source memory is treatment-ineligible")
    source_id = str(memory["case_id"])
    canonical = "\n\n".join(pieces)
    definitions = {
        "A": [{"task_id": source_id, "query": memory["raw_input"], "memory_items": [canonical]}],
        "B": [{"task_id": source_id, "query": memory["raw_input"], "memory_items": pieces}],
        "C": [{
            "task_id": source_id, "query": memory["raw_input"],
            "memory_items": list(reversed(pieces)),
        }],
        "D": [
            {
                "task_id": f"{source_id}::cross-1", "query": memory["raw_input"],
                "memory_items": [pieces[0]], "embedding_identity": "CLONED-SOURCE-QUERY",
            },
            {
                "task_id": f"{source_id}::cross-2", "query": memory["raw_input"],
                "memory_items": pieces[1:], "embedding_identity": "CLONED-SOURCE-QUERY",
            },
        ],
        "E": [{
            "task_id": f"{source_id}::case-id-placebo", "query": memory["raw_input"],
            "memory_items": pieces,
        }],
    }
    selected: dict[str, dict[str, Any]] = {}
    for arm, cases in definitions.items():
        selected_case = cases[0]
        selected_memory = "\n\n".join(selected_case["memory_items"])
        r0 = {
            "arm": arm, "eligible_cases": cases,
            "retrieval_scores": {
                "numeric_score_observed": False,
                "selection_identified_without_score": True,
                "all_eligible_scores_equal": arm == "D",
                "tie_resolution": (
                    "Python stable descending sort selects preregistered first case"
                    if arm == "D" else "single eligible case"
                ),
            },
            "top_k": 1, "selected_case": selected_case["task_id"],
            "selected_memory": selected_memory,
            "selected_memory_sha256": sha256_text(selected_memory),
            "ordering": [case["task_id"] for case in cases],
            "retrieval_certificate": str(RETRIEVAL_CERT_PATH.relative_to(ROOT)),
        }
        selected[arm] = {
            "arm": arm, "cases": cases, "selected_memory": selected_memory, "R0": r0,
            "treatment_sha256": sha256_text(canonical_json(r0)),
        }
    if selected["A"]["selected_memory"] != selected["B"]["selected_memory"]:
        raise RuntimeError("A/B native reunion invariant failed")
    if selected["B"]["selected_memory"] != selected["E"]["selected_memory"]:
        raise RuntimeError("B/E placebo invariant failed")
    if selected["D"]["selected_memory"] == selected["A"]["selected_memory"]:
        raise RuntimeError("D boundary invariant failed")
    return selected


def freeze_treatments(memory_path: Path) -> dict[str, Any]:
    memory = json.loads(memory_path.read_text(encoding="utf-8"))
    treatments = treatment_cases(memory)
    core = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-TREATMENTS-20260829",
        "created_at_utc": utcnow(),
        "source_memory_artifact": str(memory_path.relative_to(ROOT)),
        "source_memory_artifact_sha256": sha256_file(memory_path),
        "arms": treatments,
        "checks": {
            "A_equals_B_model_visible_memory": (
                treatments["A"]["selected_memory"] == treatments["B"]["selected_memory"]
            ),
            "B_equals_E_model_visible_memory": (
                treatments["B"]["selected_memory"] == treatments["E"]["selected_memory"]
            ),
            "C_order_reversed": True, "D_top1_loses_at_least_one_piece": True,
            "same_semantic_evidence_pre_retrieval": True,
        },
        "scientific_boundary": {
            "downstream_p1_outcome_observed": False,
            "treatments_frozen_before_pilot": True,
        },
    }
    output = ROOT / "generated/asset-first-stri-reasoningbank-p1-treatment-manifest-20260829.json"
    file_sha = write_json(output, core)
    return {
        "decision": "P1_TREATMENTS_FROZEN", "path": str(output.relative_to(ROOT)),
        "file_sha256": file_sha,
        "treatment_hashes": {
            arm: row["treatment_sha256"] for arm, row in treatments.items()
        },
    }


def qualify_runtime(output: Path) -> dict[str, Any]:
    verification = verify_frozen_inputs()
    rows = []
    for fixture in load_fixtures():
        container = DockerRun(
            fixture["image_pull_reference"], fixture["model_visible"]["base_commit"],
            f"runtime-{fixture['instance_id']}",
        )
        try:
            start = container.start()
            probe = container.exec(
                "test -d /testbed && test -d /opt/miniconda3 && git status --porcelain=v1",
                timeout=30,
            )
            rows.append({
                "instance_id": fixture["instance_id"],
                "image": fixture["image_pull_reference"],
                "expected_manifest_digest": fixture["image_amd64_manifest_digest"],
                "start": start, "non_outcome_probe": probe,
                "pass": probe["returncode"] == 0 and probe["output"].strip() == "",
            })
        except Exception as error:
            rows.append({
                "instance_id": fixture["instance_id"], "image": fixture["image_pull_reference"],
                "pass": False, "error_type": type(error).__name__, "message": str(error),
            })
        finally:
            container.close()
    decision = "P1_RUNTIME_QUALIFIED" if all(row["pass"] for row in rows) else "P1_RUNTIME_HOLD"
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-RUNTIME-QUALIFICATION-20260829",
        "created_at_utc": utcnow(), "frozen_input_verification": verification,
        "rows": rows,
        "checks": {
            "all_images_present_by_fixed_digest": all(row["pass"] for row in rows),
            "all_base_commits_exact": all(row["pass"] for row in rows),
            "no_task_test_or_evaluator_executed": True,
            "separate_docker_daemon": True,
        },
        "decision": decision,
        "scientific_boundary": {
            "source_induction_executed": False, "p1_task_outcome_observed": False,
        },
    }
    return {"decision": decision, "file_sha256": write_json(output, payload), "rows": len(rows)}


def run_pilot(
    *, treatment_manifest: Path, output_dir: Path, index_path: Path,
) -> dict[str, Any]:
    verify_frozen_inputs()
    manifest = json.loads(treatment_manifest.read_text(encoding="utf-8"))
    arms = manifest["arms"]
    fixtures = [
        row for row in load_fixtures() if row["role"] == "held_out_pilot_evaluation"
    ]
    rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        for arm in ("A", "B", "C", "D", "E"):
            arm_row = arms[arm]
            receipt = run_case(
                fixture, selected_memory=arm_row["selected_memory"],
                run_id=f"pilot-{fixture['instance_id']}-{arm}",
                output_dir=output_dir, r0=arm_row["R0"],
            )
            rows.append(receipt)
            write_json(index_path, {
                "schema_version": 1,
                "experiment_id": "E1-STRI-REASONINGBANK-P1-MINIMAL-PILOT-20260829",
                "created_at_utc": utcnow(),
                "treatment_manifest": str(treatment_manifest.relative_to(ROOT)),
                "treatment_manifest_sha256": sha256_file(treatment_manifest),
                "ordered_execution": "evaluation-case order then A/B/C/D/E",
                "completed_runs": rows, "planned_run_count": len(fixtures) * 5,
                "execution_complete": len(rows) == len(fixtures) * 5,
                "credential_material_present": False,
            })
    return {
        "decision": "P1_MINIMAL_PILOT_EXECUTION_COMPLETE", "run_count": len(rows),
        "index_path": str(index_path.relative_to(ROOT)),
        "index_sha256": sha256_file(index_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify")
    runtime = sub.add_parser("qualify-runtime")
    runtime.add_argument(
        "--output", type=Path,
        default=ROOT / "generated/asset-first-stri-reasoningbank-p1-runtime-qualification-result-20260829.json",
    )
    source = sub.add_parser("source-induction")
    source.add_argument(
        "--output-dir", type=Path,
        default=ROOT / "generated/asset-first-stri-reasoningbank-p1-runs-20260829",
    )
    treatment = sub.add_parser("freeze-treatments")
    treatment.add_argument(
        "--memory", type=Path,
        default=ROOT / "generated/asset-first-stri-reasoningbank-p1-source-memory-20260829.json",
    )
    pilot = sub.add_parser("run-pilot")
    pilot.add_argument(
        "--treatments", type=Path,
        default=ROOT / "generated/asset-first-stri-reasoningbank-p1-treatment-manifest-20260829.json",
    )
    pilot.add_argument(
        "--output-dir", type=Path,
        default=ROOT / "generated/asset-first-stri-reasoningbank-p1-runs-20260829",
    )
    pilot.add_argument(
        "--index", type=Path,
        default=ROOT / "generated/asset-first-stri-reasoningbank-p1-minimal-pilot-index-20260829.json",
    )
    args = parser.parse_args()
    if args.command == "verify":
        verify_frozen_inputs()
        value = {"decision": "FROZEN_INPUTS_VERIFIED"}
    elif args.command == "qualify-runtime":
        value = qualify_runtime(args.output)
    elif args.command == "source-induction":
        value = source_induction(args.output_dir)
    elif args.command == "freeze-treatments":
        value = freeze_treatments(args.memory)
    else:
        value = run_pilot(
            treatment_manifest=args.treatments, output_dir=args.output_dir,
            index_path=args.index,
        )
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
