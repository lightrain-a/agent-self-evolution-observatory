from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    AppWorldToolWorld,
    prepare_appworld_runtime_root,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    ALLOWED_ALIAS,
    DEFAULT_BASE_URL,
    OBJECT_ID,
    REQUESTED_MODEL,
    AppendOnlyLedger,
    EpisodeUnit,
    Provider,
    RunnerError,
    TypicalResponsesClient,
    canonical_bytes,
    run_episode,
    sha256_file,
    sha256_value,
)
from research_pipeline.appworld_constraint_compiler import load_protected_spec

F0_FAMILIES = (
    "ACE-FG-01", "ACE-FG-02", "ACE-FG-03", "ACE-FG-04",
    "ACE-TNF-01", "ACE-TNF-02", "ACE-TNF-03", "ACE-TNF-04",
)
ARMS = ("INDEPENDENT", "LOW", "HIGH")
BRANCHES = ("NO_UPDATE", "UPDATE")
SEEDS = (1201, 1202, 1203)
BRANCH_ORDER_SALT = "ACE-F0-BRANCH-ORDER-20260831-V1"
INJECTION_PREFIX = b"\n\nPersistent procedural repair note (apply exactly):\n"
REPAIR_PROVIDER_REQUEST_CAP = 8


def enumerate_source_units() -> list[EpisodeUnit]:
    units = [
        EpisodeUnit(
            namespace="source",
            key=(family_id, "source"),
            stage="F0_SOURCE",
            family_id=family_id,
        )
        for family_id in F0_FAMILIES
    ]
    if len(units) != 8 or len({unit.unit_id for unit in units}) != 8:
        raise RunnerError("F0 source enumeration must contain eight unique units.")
    return units


def frozen_branch_order(family_id: str, arm: str, seed: int) -> tuple[str, str]:
    if arm not in ARMS or seed not in SEEDS:
        raise RunnerError("Branch-order key is outside the frozen design.")
    digest = hashlib.sha256(
        f"{BRANCH_ORDER_SALT}|{family_id}|{arm}|{seed}".encode("utf-8")
    ).digest()
    return BRANCHES if digest[0] % 2 == 0 else tuple(reversed(BRANCHES))


def enumerate_probe_units(eligible_families: Iterable[str]) -> list[EpisodeUnit]:
    families = tuple(eligible_families)
    if len(families) < 6 or len(families) > 8 or not set(families) <= set(F0_FAMILIES):
        raise RunnerError("Eligible repair count must be 6..8 within frozen F0 families.")
    units: list[EpisodeUnit] = []
    for family_id in families:
        for arm in ARMS:
            for seed in SEEDS:
                for branch in frozen_branch_order(family_id, arm, seed):
                    units.append(EpisodeUnit(
                        namespace="probe",
                        key=(family_id, arm, branch, seed),
                        stage="F0_PROBE",
                        family_id=family_id,
                        arm=arm,
                        branch=branch,
                        seed=seed,
                    ))
    if len(units) != len(families) * 18:
        raise RunnerError("Probe enumeration violated eligible_count × 18.")
    if len({unit.unit_id for unit in units}) != len(units):
        raise RunnerError("Duplicate probe unit detected.")
    return units


def target_only_updater_payload(
    *,
    target_constraint_spec: dict[str, Any],
    target_task_instruction: str,
    target_failure_slice: dict[str, Any],
    target_tool_trajectory: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = {
        "TARGET_CONSTRAINT_SPEC": target_constraint_spec,
        "TARGET_TASK_INSTRUCTION": target_task_instruction,
        "TARGET_FAILURE_SLICE": target_failure_slice,
        "TARGET_TOOL_TRAJECTORY": target_tool_trajectory,
    }
    forbidden = {
        "NON_TARGET_OUTCOMES", "TOPOLOGY_LABEL", "COUPLING_LEVEL",
        "ARM_ASSIGNMENT", "F0_EFFECT",
    }
    if forbidden & set(payload):
        raise RunnerError("Updater payload leaked forbidden information.")
    return payload


def _response_text(output: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for item in output:
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    text = "\n".join(chunks)
    if not text.strip():
        raise RunnerError("Updater returned no procedural repair text; no replacement.")
    return text


def generate_repair(
    provider: Provider,
    *,
    model: str,
    payload: dict[str, Any],
) -> tuple[bytes, bytes, dict[str, Any]]:
    receipt = provider.create_response(
        model=model,
        instructions=(
            "Write one concise persistent procedural repair note for the target failure. "
            "Do not discuss other constraints or topology. Output only the note."
        ),
        input_items=[{"role": "user", "content": canonical_bytes(payload).decode("utf-8")}],
        tools=[],
        temperature=0.0,
    )
    raw_text = _response_text(receipt.output)
    raw = raw_text.encode("utf-8")
    normalized = raw_text.replace("\r\n", "\n").strip().encode("utf-8")
    metadata = {
        "surface": "PERSISTENT_PROCEDURAL_REPAIR_NOTE",
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "normalized_sha256": hashlib.sha256(normalized).hexdigest(),
        "raw_byte_length": len(raw),
        "normalized_byte_length": len(normalized),
        "word_count": len(normalized.decode("utf-8").split()),
        "fixed_tokenizer": "UTF8_WHITESPACE_V1",
        "fixed_tokenizer_token_count": len(normalized.decode("utf-8").split()),
        "procedural_clause_count": sum(
            1 for piece in normalized.decode("utf-8").replace(";", ".").split(".") if piece.strip()
        ),
        "injection_position": "AFTER_TASK_INSTRUCTION",
        "exposure_rule": "UPDATE_ONLY_EXACT_BYTES",
        "generation_requested_model_id": model,
        "generation_resolved_model_id": receipt.resolved_model,
        "generation_request_sha256": sha256_value(payload),
    }
    return raw, normalized, metadata


def freeze_repair(
    directory: Path,
    family_id: str,
    repair_bytes: bytes,
    metadata: dict[str, Any],
    *,
    raw_bytes: bytes | None = None,
) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    repair_path = directory / f"{family_id.lower()}-repair.bin"
    if repair_path.exists():
        raise RunnerError("Frozen repair already exists; human edit/replacement forbidden.")
    repair_path.write_bytes(repair_bytes)
    raw_path = directory / f"{family_id.lower()}-repair.raw.bin"
    raw_path.write_bytes(repair_bytes if raw_bytes is None else raw_bytes)
    record = {
        **metadata,
        "family_id": family_id,
        "repair_path": str(repair_path),
        "raw_repair_path": str(raw_path),
        "raw_repair_sha256": sha256_file(raw_path),
        "raw_repair_byte_length": raw_path.stat().st_size,
        "repair_sha256": sha256_file(repair_path),
        "repair_byte_length": repair_path.stat().st_size,
        "human_edited": False,
    }
    record["record_sha256"] = sha256_value(record)
    return record


def inject_repair(task_instruction: str, branch: str, repair_bytes: bytes) -> bytes:
    base = task_instruction.encode("utf-8")
    if branch == "NO_UPDATE":
        return base
    if branch != "UPDATE":
        raise RunnerError("Unknown F0 branch.")
    return base + INJECTION_PREFIX + repair_bytes


def evaluate_constraints_from_arm(arm: dict[str, Any], evaluation: dict[str, Any]) -> dict[str, Any]:
    target_ids = {
        item["constraint_id"] for item in arm["constraints"] if item["role"] == "TARGET"
    }
    non_target_ids = {
        item["constraint_id"] for item in arm["constraints"] if item["role"] == "NON_TARGET"
    }
    if set(evaluation["target"]) != target_ids:
        raise RunnerError("Target evaluator binding mismatch.")
    if set(evaluation["non_target"]) != non_target_ids:
        raise RunnerError("Non-target evaluator binding mismatch.")
    return evaluation


def _require_capability_pass(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("verdict") != "CAPABILITY_CALIBRATION_PASS":
        raise RunnerError("F0 requires frozen Qwen capability PASS.")
    return payload


def execute_sources(
    *,
    appworld_root: Path,
    protected_bundle: Path,
    runtime_root: Path,
    ledger_path: Path,
    repairs_directory: Path,
    repairs_manifest: Path,
    capability_result: Path,
    model: str,
) -> dict[str, Any]:
    _require_capability_pass(capability_result)
    if model not in {REQUESTED_MODEL, ALLOWED_ALIAS}:
        raise RunnerError("Model replacement is forbidden.")
    provider = TypicalResponsesClient(
        os.getenv("AA_API_KEY", ""),
        os.getenv("AA_BASE_URL", DEFAULT_BASE_URL),
    )
    spec = load_protected_spec(protected_bundle)
    families = {item["family_id"]: item for item in spec["families"]}
    ledger = AppendOnlyLedger(ledger_path)
    units = enumerate_source_units()
    repairs: dict[str, Any] = {}
    no_repair: list[str] = []
    updater_calls = 0
    for unit in units:
        family = families[unit.family_id]
        reference_arm = next(
            item for item in family["arms"] if item["coupling_level"] == "INDEPENDENT"
        )
        target_constraints = [
            item for item in reference_arm["constraints"] if item["role"] == "TARGET"
        ]
        source_arm = dict(reference_arm)
        source_arm["task_instruction"] = family["target_instruction"]
        source_arm["constraints"] = target_constraints
        task_hash = hashlib.sha256(unit.unit_id.encode("utf-8")).hexdigest()[:12]
        task_id = f"acesource{task_hash}_1"
        unit_root = runtime_root / task_hash
        materialized = prepare_appworld_runtime_root(
            appworld_root, unit_root, family=family, arm=source_arm, task_id=task_id
        )
        world = AppWorldToolWorld(
            runtime_root=unit_root,
            task_id=task_id,
            experiment_name="ace-f0-source",
            seed=1200,
        )
        try:
            result = run_episode(
                unit=unit,
                instruction=family["target_instruction"],
                snapshot_sha256=materialized["initial_snapshot_sha256"],
                repair_sha256=None,
                world=world,
                provider=provider,
                ledger=ledger,
                model=model,
                base_url=provider.base_url,
                result_evaluator=lambda arm=source_arm, world=world: (
                    world.save_and_evaluate(arm)
                ),
            )
        finally:
            world.close()
        evaluation = result["evaluation"]
        if evaluation["target_success"]:
            no_repair.append(unit.family_id)
            continue
        if updater_calls >= REPAIR_PROVIDER_REQUEST_CAP:
            raise RunnerError("Repair generation provider request cap exceeded.")
        completion = ledger.rows()[-1]
        trajectory = [
            {
                "response_id": receipt["response_id"],
                "output": receipt["output"],
            }
            for receipt in completion["provider_receipts"]
        ]
        payload = target_only_updater_payload(
            target_constraint_spec={"constraints": target_constraints},
            target_task_instruction=family["target_instruction"],
            target_failure_slice=evaluation["target"],
            target_tool_trajectory=trajectory,
        )
        raw_bytes, repair_bytes, metadata = generate_repair(
            provider, model=model, payload=payload
        )
        updater_calls += 1
        metadata["source_trajectory_sha256"] = sha256_value(trajectory)
        repairs[unit.family_id] = freeze_repair(
            repairs_directory,
            unit.family_id,
            repair_bytes,
            metadata,
            raw_bytes=raw_bytes,
        )
    ledger.assert_all_terminal(units)
    eligible = [family_id for family_id in F0_FAMILIES if family_id in repairs]
    status = (
        "F0_SOURCE_COMPLETE"
        if len(eligible) >= 6
        else "F0_UPDATE_UPTAKE_INSUFFICIENT_STOP"
    )
    manifest = {
        "schema_version": "ace-f0-repairs-v1",
        "object_id": OBJECT_ID,
        "status": status,
        "source_family_count": 8,
        "eligible_families": eligible,
        "no_repair_eligible": no_repair,
        "repairs": repairs,
        "updater_model_request_count": updater_calls,
        "repair_generation_provider_request_cap": REPAIR_PROVIDER_REQUEST_CAP,
        "human_edits": 0,
    }
    manifest["manifest_content_sha256"] = sha256_value(manifest)
    repairs_manifest.parent.mkdir(parents=True, exist_ok=True)
    repairs_manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def execute_probes(
    *,
    appworld_root: Path,
    protected_bundle: Path,
    runtime_root: Path,
    ledger_path: Path,
    repairs_manifest: Path,
    capability_result: Path,
    model: str,
) -> None:
    _require_capability_pass(capability_result)
    repairs = json.loads(repairs_manifest.read_text(encoding="utf-8"))
    eligible = tuple(repairs["eligible_families"])
    if len(eligible) < 6:
        raise RunnerError("F0_UPDATE_UPTAKE_INSUFFICIENT_STOP")
    if model not in {REQUESTED_MODEL, ALLOWED_ALIAS}:
        raise RunnerError("Model replacement is forbidden.")
    provider = TypicalResponsesClient(
        os.getenv("AA_API_KEY", ""),
        os.getenv("AA_BASE_URL", DEFAULT_BASE_URL),
    )
    spec = load_protected_spec(protected_bundle)
    families = {item["family_id"]: item for item in spec["families"]}
    ledger = AppendOnlyLedger(ledger_path)
    units = enumerate_probe_units(eligible)
    for unit in units:
        family = families[unit.family_id]
        arm = next(item for item in family["arms"] if item["coupling_level"] == unit.arm)
        repair_record = repairs["repairs"][unit.family_id]
        repair_bytes = Path(repair_record["repair_path"]).read_bytes()
        if hashlib.sha256(repair_bytes).hexdigest() != repair_record["repair_sha256"]:
            raise RunnerError("Frozen repair bytes drifted.")
        visible = inject_repair(arm["task_instruction"], str(unit.branch), repair_bytes)
        task_hash = hashlib.sha256(unit.unit_id.encode("utf-8")).hexdigest()[:12]
        task_id = f"aceprobe{task_hash}_1"
        unit_root = runtime_root / task_hash
        materialized_arm = dict(arm)
        materialized_arm["task_instruction"] = visible.decode("utf-8")
        materialized = prepare_appworld_runtime_root(
            appworld_root, unit_root, family=family, arm=materialized_arm, task_id=task_id
        )
        world = AppWorldToolWorld(
            runtime_root=unit_root,
            task_id=task_id,
            experiment_name="ace-f0-probe",
            seed=int(unit.seed or 0),
        )
        try:
            run_episode(
                unit=unit,
                instruction=visible.decode("utf-8"),
                snapshot_sha256=materialized["initial_snapshot_sha256"],
                repair_sha256=repair_record["repair_sha256"] if unit.branch == "UPDATE" else None,
                world=world,
                provider=provider,
                ledger=ledger,
                model=model,
                base_url=provider.base_url,
                result_evaluator=lambda arm=arm, world=world: evaluate_constraints_from_arm(
                    arm, world.save_and_evaluate(arm)
                ),
            )
        finally:
            world.close()
    ledger.assert_all_terminal(units)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["source", "probe"], required=True)
    parser.add_argument("--appworld-root", type=Path, required=True)
    parser.add_argument("--protected-bundle", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--repairs-directory", type=Path)
    parser.add_argument("--repairs-manifest", type=Path, required=True)
    parser.add_argument("--capability-result", type=Path, required=True)
    parser.add_argument("--model", choices=[REQUESTED_MODEL, ALLOWED_ALIAS], required=True)
    args = parser.parse_args()
    if args.phase == "source":
        if args.repairs_directory is None:
            parser.error("--repairs-directory is required for source phase")
        result = execute_sources(
            appworld_root=args.appworld_root,
            protected_bundle=args.protected_bundle,
            runtime_root=args.runtime_root,
            ledger_path=args.ledger,
            repairs_directory=args.repairs_directory,
            repairs_manifest=args.repairs_manifest,
            capability_result=args.capability_result,
            model=args.model,
        )
        status = result["status"]
    else:
        execute_probes(
            appworld_root=args.appworld_root,
            protected_bundle=args.protected_bundle,
            runtime_root=args.runtime_root,
            ledger_path=args.ledger,
            repairs_manifest=args.repairs_manifest,
            capability_result=args.capability_result,
            model=args.model,
        )
        status = "F0_PROBES_COMPLETE_PENDING_ADJUDICATION"
    print(json.dumps({"object_id": OBJECT_ID, "status": status}, sort_keys=True))


if __name__ == "__main__":
    main()
