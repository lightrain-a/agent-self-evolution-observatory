from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import random
import time
from pathlib import Path
from typing import Any


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atom(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _norm_history(value: Any) -> list[list[str]]:
    out: list[list[str]] = []
    for item in list(value or []):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"invalid history item: {item!r}")
        out.append([str(item[0]), str(item[1])])
    return out[-6:]


def analyze(rows: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    contexts = {str(row["context_id"]): row for row in contract["selected_contexts"]}
    by: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        by.setdefault(str(row["context_id"]), {})[str(row["arm"])] = row
    expected_arms = set(contract["arms"])
    complete = [cid for cid in contexts if set(by.get(cid, {})) == expected_arms]
    technical_failures: list[dict[str, Any]] = []
    unit_rows: list[dict[str, Any]] = []
    for cid in complete:
        arms = by[cid]
        for arm_name, arm in arms.items():
            for key in ("replay_context_exact", "teacher_suffix_score_exact", "adapter_sha_exact", "base_rollback_exact"):
                if not bool(arm.get(key, True)):
                    technical_failures.append({"context_id": cid, "arm": arm_name, "key": key})
        if not bool(arms["updated_natural"].get("updated_first_action_exact")):
            technical_failures.append({"context_id": cid, "arm": "updated_natural", "key": "updated_first_action_exact"})
        bf = int(arms["base_forced_teacher_suffix"]["final_score"])
        uf = int(arms["updated_forced_teacher_suffix"]["final_score"])
        bn = int(arms["base_natural"]["final_score"])
        un = int(arms["updated_natural"]["final_score"])
        residual = uf - bf
        unit_rows.append({
            "context_id": cid,
            "unit_id": contexts[cid]["unit_id"],
            "task_family": contexts[cid]["task_family"],
            "update_arm": contexts[cid]["update_arm"],
            "mechanism_fidelity_residual": residual,
            "intended_correction_value": bf - bn,
            "updated_natural_effect": un - bn,
            "natural_vs_equalized_updated_gap": un - uf,
            "scores": {"base_natural": bn, "base_forced": bf, "updated_natural": un, "updated_forced": uf},
        })
    residual_rows = [r for r in unit_rows if r["mechanism_fidelity_residual"] != 0]
    residual_families = sorted({r["task_family"] for r in residual_rows})
    negative_residuals = sum(r["mechanism_fidelity_residual"] < 0 for r in residual_rows)
    positive_residuals = sum(r["mechanism_fidelity_residual"] > 0 for r in residual_rows)
    if technical_failures:
        decision = "HOLD_PROVENANCE_OR_RUNTIME_FIDELITY_FAIL"
    elif len(complete) != len(contexts):
        decision = "INCOMPLETE_NO_SCIENTIFIC_DECISION"
    elif len(residual_rows) <= 1 or len(residual_families) <= 1:
        decision = "STOP_CORRECTION_PROGRAM_EXPLAINS_DOWNSTREAM_UPDATE_EFFECT"
    elif len(residual_rows) == 2:
        decision = "MECHANISM_FIDELITY_RESIDUAL_INCONCLUSIVE"
    else:
        decision = "MECHANISM_FIDELITY_RESIDUAL_GO"
    return {
        "schema_version": "1.0",
        "experiment_id": contract["experiment_id"],
        "decision": decision,
        "complete_contexts": len(complete),
        "total_contexts": len(contexts),
        "technical_failures": technical_failures,
        "nonzero_residual_contexts": len(residual_rows),
        "residual_task_families": residual_families,
        "negative_residual_contexts": negative_residuals,
        "positive_residual_contexts": positive_residuals,
        "strong_risk_flag": negative_residuals >= 1,
        "unit_rows": unit_rows,
        "paper_design_authorized": False,
        "method_authorized": False,
        "p0_authorized": False,
        "second_backbone_authorized": False,
        "next_action": (
            "Run current-source/mature-reduction adjudication before any Paper Design or method work."
            if decision == "MECHANISM_FIDELITY_RESIDUAL_GO"
            else "Stop or hold exactly as frozen; do not rescue with more contexts, threshold changes, or a second backbone."
        ),
    }


def run(
    *,
    contract_path: Path,
    output_dir: Path,
    model_path: Path,
    gpu_uuid: str,
    legacy_source_root: Path,
    wall_hours_cap: float,
    rollout_cap: int,
) -> dict[str, Any]:
    import torch
    from peft import PeftModel

    if os.environ.get("CUDA_VISIBLE_DEVICES", "") != gpu_uuid:
        raise RuntimeError("CUDA_VISIBLE_DEVICES must equal the frozen GPU UUID")
    contract = _load_json(contract_path)
    if contract.get("status") != "FROZEN_PENDING_PREFLIGHT":
        raise RuntimeError("contract must be frozen pending preflight")
    if int(contract["budget"]["new_rollouts_max"]) != rollout_cap:
        raise RuntimeError("rollout cap differs from frozen contract")
    if float(wall_hours_cap) > float(contract["budget"]["wall_hours_cap"]):
        raise RuntimeError("wall cap exceeds frozen contract")
    for item in contract["source_files"].values():
        path = Path(item["path"])
        if not path.exists() or _sha(path) != item["sha256"]:
            raise RuntimeError(f"source SHA mismatch: {path}")
    for item in contract["source_unit_result_files"]:
        path = Path(item["path"])
        if not path.exists() or _sha(path) != item["sha256"]:
            raise RuntimeError(f"unit-result SHA mismatch: {path}")
    for ctx in contract["selected_contexts"]:
        adapter_file = Path(ctx["adapter_dir"]) / "adapter_model.safetensors"
        if not adapter_file.exists() or _sha(adapter_file) != ctx["adapter_model_sha256"]:
            raise RuntimeError(f"adapter SHA mismatch: {ctx['context_id']}")

    # Import the bit-bound legacy ScienceWorld runtime only after source-SHA validation.
    import sys
    legacy = str(legacy_source_root)
    if legacy not in sys.path:
        sys.path.insert(0, legacy)
    from research_pipeline.run_scienceworld_base_headroom_q1_shard import replay
    from research_pipeline.scienceworld_qwen_adapter import ScienceWorldQwenPolicy, normalize_action
    from research_pipeline.scienceworld_sapd_f0_runtime import base_fingerprint
    from scienceworld import ScienceWorldEnv

    random.seed(0)
    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)

    output_dir.mkdir(parents=True, exist_ok=True)
    lock_path = output_dir.parent / (output_dir.name + ".lock")
    lock = lock_path.open("a+")
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    raw_path = output_dir / "raw-arms.jsonl"
    committed_dir = output_dir / "committed-contexts"
    staging_dir = output_dir / "staging-contexts"
    committed_dir.mkdir(parents=True, exist_ok=True)
    staging_dir.mkdir(parents=True, exist_ok=True)

    def _context_receipt_path(root: Path, context_id: str) -> Path:
        key = hashlib.sha256(context_id.encode()).hexdigest()[:20]
        return root / f"{key}.json"

    def _load_committed_rows() -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        seen_contexts: set[str] = set()
        for path in sorted(committed_dir.glob("*.json")):
            payload = _load_json(path)
            cid = str(payload.get("context_id") or "")
            rows = list(payload.get("rows") or [])
            if not cid or cid in seen_contexts or len(rows) != 4:
                raise RuntimeError(f"invalid committed context receipt: {path}")
            if {str(row.get("arm")) for row in rows} != set(contract["arms"]):
                raise RuntimeError(f"committed arm set mismatch: {cid}")
            if any(str(row.get("context_id")) != cid for row in rows):
                raise RuntimeError(f"committed context id mismatch: {cid}")
            seen_contexts.add(cid)
            out.extend(rows)
        return out

    existing = _load_committed_rows()
    completed_contexts = {str(r["context_id"]) for r in existing}
    if len(existing) != 4 * len(completed_contexts):
        raise RuntimeError("committed context receipt shape mismatch")
    if len(existing) > rollout_cap:
        raise RuntimeError("committed receipts exceed frozen rollout cap")
    if raw_path.exists():
        raw_existing = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if raw_existing != existing:
            raise RuntimeError("derived raw-arms.jsonl disagrees with committed context receipts")

    pending_stages = list(staging_dir.glob("*.json"))
    if len(pending_stages) > 1:
        raise RuntimeError("more than one uncommitted staging context exists")
    if pending_stages:
        stage = _load_json(pending_stages[0])
        cid = str(stage.get("context_id") or "")
        if cid in completed_contexts:
            raise RuntimeError("staging context is already committed")
        stage_rows = list(stage.get("rows") or [])
        stage_arms = [str(row.get("arm")) for row in stage_rows]
        if len(stage_arms) != len(set(stage_arms)) or not set(stage_arms).issubset(set(contract["arms"])):
            raise RuntimeError("invalid staging arm receipts")
        if any(str(row.get("context_id")) != cid for row in stage_rows):
            raise RuntimeError("staging context id mismatch")
        if str(stage.get("contract_hash")) != str(contract["contract_hash"]):
            raise RuntimeError("staging contract hash mismatch")

    policy = ScienceWorldQwenPolicy(model_path)
    env = ScienceWorldEnv("", envStepLimit=50)
    base_fp = base_fingerprint(policy.model)
    started = time.monotonic()
    _atom(output_dir / "manifest.json", {
        "schema_version": "1.0",
        "experiment_id": contract["experiment_id"],
        "contract_file_sha256": _sha(contract_path),
        "contract_hash": contract["contract_hash"],
        "runner_sha256": _sha(Path(__file__)),
        "legacy_source_root": str(legacy_source_root),
        "gpu_uuid": gpu_uuid,
        "model_path": str(model_path),
        "base_model_fingerprint": base_fp,
        "rollout_cap": rollout_cap,
        "wall_hours_cap": wall_hours_cap,
        "new_training_steps": 0,
        "gold_or_teacher_access_during_continuation": False,
        "method_authorized": False,
        "p0_authorized": False,
    })

    def reconstruct(ctx: dict[str, Any]) -> tuple[Any, dict[str, Any], list[tuple[str, str]], int]:
        obs, info, attempts = replay(env, ctx)
        if obs is None:
            raise RuntimeError(f"{ctx['context_id']}: initial-state replay failed")
        hist: list[tuple[str, str]] = []
        total_steps = 0
        for action in ctx["replay_prefix_actions"]:
            obs2, _reward, done, info = env.step(str(action))
            hist.append((str(action), str(obs2)))
            obs = str(obs2)
            total_steps += 1
            if done:
                raise RuntimeError(f"{ctx['context_id']}: prefix terminated before correction state")
        task = str(env.taskdescription())
        inventory = str(env.inventory())
        templates = list(env.get_possible_actions())
        objects = list(env.get_possible_objects())
        exact = (
            task == str(ctx["task_desc"])
            and hashlib.sha256(str(obs).encode()).hexdigest() == str(ctx["observation_sha256"])
            and inventory == str(ctx["inventory"])
            and _norm_history(hist) == _norm_history(ctx["history"])
            and templates == list(ctx["templates"])
            and objects == list(ctx["objects"])
        )
        if not exact:
            raise RuntimeError(f"{ctx['context_id']}: exact correction-context replay mismatch")
        return obs, info, hist, total_steps

    def continuation(ctx: dict[str, Any], arm: str, forced_suffix: list[str] | None) -> dict[str, Any]:
        before_calls = int(policy.calls)
        before_in = int(policy.input_tokens)
        before_out = int(policy.output_tokens)
        obs, info, hist, total_steps = reconstruct(ctx)
        trace: list[dict[str, Any]] = []
        teacher_exact = True
        if forced_suffix:
            for action in forced_suffix:
                if total_steps >= 50:
                    break
                obs_before = str(obs)
                obs2, reward, done, info = env.step(str(action))
                trace.append({
                    "kind": "forced_teacher",
                    "step_from_reset": total_steps,
                    "observation_sha256": hashlib.sha256(obs_before.encode()).hexdigest(),
                    "action": str(action),
                    "reward": reward,
                    "score": int(info.get("score", 0) or 0),
                    "done": bool(done),
                })
                hist.append((str(action), str(obs2)))
                obs = str(obs2)
                total_steps += 1
                if done:
                    break
            teacher_exact = int(info.get("score", 0) or 0) == int(ctx["teacher_suffix_expected_final_score"])
            if not teacher_exact:
                raise RuntimeError(f"{ctx['context_id']} {arm}: forced teacher suffix score mismatch")
        first_model_action: str | None = None
        while total_steps < 50:
            task = str(env.taskdescription())
            inventory = str(env.inventory())
            action, raw = policy.choose(task, str(obs), inventory, hist, env.get_possible_actions(), env.get_possible_objects())
            if first_model_action is None:
                first_model_action = str(action)
            obs_before = str(obs)
            obs2, reward, done, info = env.step(str(action))
            trace.append({
                "kind": "policy",
                "step_from_reset": total_steps,
                "observation_sha256": hashlib.sha256(obs_before.encode()).hexdigest(),
                "action": str(action),
                "raw": str(raw),
                "reward": reward,
                "score": int(info.get("score", 0) or 0),
                "done": bool(done),
            })
            hist.append((str(action), str(obs2)))
            obs = str(obs2)
            total_steps += 1
            if done:
                break
        updated_first_exact = True
        if arm == "updated_natural":
            updated_first_exact = first_model_action is not None and normalize_action(first_model_action) == normalize_action(str(ctx["repair_action"]))
            if not updated_first_exact:
                raise RuntimeError(f"{ctx['context_id']}: frozen adapter no longer reproduces learned repair action")
        return {
            "schema_version": "1.0",
            "experiment_id": contract["experiment_id"],
            "context_id": ctx["context_id"],
            "unit_id": ctx["unit_id"],
            "task_family": ctx["task_family"],
            "update_arm": ctx["update_arm"],
            "arm": arm,
            "final_score": int(info.get("score", 0) or 0),
            "total_steps_from_reset": total_steps,
            "continuation_trace": trace,
            "first_model_action": first_model_action,
            "replay_context_exact": True,
            "teacher_suffix_score_exact": teacher_exact,
            "adapter_sha_exact": True,
            "base_rollback_exact": True,
            "updated_first_action_exact": updated_first_exact,
            "usage": {
                "generation_calls": int(policy.calls) - before_calls,
                "input_tokens": int(policy.input_tokens) - before_in,
                "output_tokens": int(policy.output_tokens) - before_out,
            },
        }

    contexts = list(contract["selected_contexts"])
    context_ids = [str(ctx["context_id"]) for ctx in contexts]
    committed_order = [cid for cid in context_ids if cid in completed_contexts]
    if committed_order != context_ids[: len(committed_order)]:
        raise RuntimeError("committed contexts are not a prefix of the frozen context order")
    if pending_stages:
        pending_cid = str(_load_json(pending_stages[0]).get("context_id") or "")
        expected_cid = context_ids[len(committed_order)] if len(committed_order) < len(context_ids) else ""
        if pending_cid != expected_cid:
            raise RuntimeError("staging context is not the next frozen context")

    runner_sha = _sha(Path(__file__))

    def _write_derived_raw(rows: list[dict[str, Any]]) -> None:
        tmp = raw_path.with_suffix(raw_path.suffix + ".tmp")
        text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, raw_path)

    def _save_stage(ctx: dict[str, Any], rows: list[dict[str, Any]]) -> Path:
        path = _context_receipt_path(staging_dir, str(ctx["context_id"]))
        _atom(path, {
            "schema_version": "1.0",
            "context_id": ctx["context_id"],
            "contract_hash": contract["contract_hash"],
            "runner_sha256": runner_sha,
            "rows": rows,
        })
        return path

    def _commit_stage(ctx: dict[str, Any], rows: list[dict[str, Any]], rollback_mode: str) -> None:
        if len(rows) != 4 or {str(row["arm"]) for row in rows} != set(contract["arms"]):
            raise RuntimeError(f"{ctx['context_id']}: cannot commit incomplete context")
        ordered = []
        by_arm = {str(row["arm"]): dict(row) for row in rows}
        for arm in contract["arms"]:
            row = by_arm[str(arm)]
            row["base_rollback_exact"] = True
            ordered.append(row)
        commit_path = _context_receipt_path(committed_dir, str(ctx["context_id"]))
        _atom(commit_path, {
            "schema_version": "1.0",
            "context_id": ctx["context_id"],
            "contract_hash": contract["contract_hash"],
            "runner_sha256": runner_sha,
            "rollback_verification": rollback_mode,
            "rows": ordered,
        })
        stage_path = _context_receipt_path(staging_dir, str(ctx["context_id"]))
        if stage_path.exists():
            stage_path.unlink()
        committed_rows = _load_committed_rows()
        _write_derived_raw(committed_rows)

    try:
        for ctx in contexts:
            cid = str(ctx["context_id"])
            commit_path = _context_receipt_path(committed_dir, cid)
            if commit_path.exists():
                continue
            elapsed_h = (time.monotonic() - started) / 3600.0
            stage_path = _context_receipt_path(staging_dir, cid)
            stage_rows: list[dict[str, Any]] = []
            if stage_path.exists():
                stage_payload = _load_json(stage_path)
                if str(stage_payload.get("context_id")) != cid or str(stage_payload.get("contract_hash")) != str(contract["contract_hash"]):
                    raise RuntimeError(f"{cid}: invalid staging provenance")
                if str(stage_payload.get("runner_sha256")) != runner_sha:
                    raise RuntimeError(f"{cid}: staging runner SHA mismatch")
                stage_rows = [dict(row) for row in list(stage_payload.get("rows") or [])]
            stage_arms = {str(row["arm"]) for row in stage_rows}
            if len(stage_arms) != len(stage_rows) or not stage_arms.issubset(set(contract["arms"])):
                raise RuntimeError(f"{cid}: invalid staged arms")
            if len(existing) + len(stage_rows) >= rollout_cap and len(stage_rows) < 4:
                raise RuntimeError("rollout cap reached")
            if elapsed_h >= wall_hours_cap and len(stage_rows) < 4:
                _atom(output_dir / "execution-hold.json", {
                    "decision": "HOLD_BUDGET_CAP_BEFORE_COMPLETE",
                    "completed_committed_rollouts": len(existing),
                    "staged_rollouts": len(stage_rows),
                    "wall_hours": elapsed_h,
                    "scientific_belief_update_allowed": False,
                })
                raise RuntimeError("wall cap reached before complete")

            # If a prior process produced all four staged arms but crashed before rollback/commit,
            # a fresh clean process can safely commit them because no later context was allowed to run.
            if len(stage_rows) == 4:
                if base_fingerprint(policy.model) != base_fp:
                    raise RuntimeError(f"{cid}: fresh-process base fingerprint mismatch during stage recovery")
                _commit_stage(ctx, stage_rows, "fresh_process_recovery_before_any_later_context")
                existing = _load_committed_rows()
                completed_contexts.add(cid)
                _atom(output_dir / "progress.json", {"status": "running", "completed_rollouts": len(existing), "total_rollouts": rollout_cap, "current_context": cid, "current_arm": "context_commit_recovered"})
                continue

            for arm, suffix in [
                ("base_natural", None),
                ("base_forced_teacher_suffix", list(ctx["teacher_suffix"])),
            ]:
                if arm in stage_arms:
                    continue
                row = continuation(ctx, arm, suffix)
                stage_rows.append(row)
                stage_arms.add(arm)
                _save_stage(ctx, stage_rows)
                _atom(output_dir / "progress.json", {"status": "running", "completed_rollouts": len(existing) + len(stage_rows), "committed_rollouts": len(existing), "staged_rollouts": len(stage_rows), "total_rollouts": rollout_cap, "current_context": cid, "current_arm": arm})

            updated_missing = [arm for arm in ("updated_natural", "updated_forced_teacher_suffix") if arm not in stage_arms]
            if updated_missing:
                if base_fingerprint(policy.model) != base_fp:
                    raise RuntimeError("base fingerprint mismatch before adapter load")
                adapter_dir = Path(ctx["adapter_dir"])
                policy.model = PeftModel.from_pretrained(policy.model, str(adapter_dir), is_trainable=False).to(policy.device).eval()
                try:
                    for arm, suffix in [
                        ("updated_natural", None),
                        ("updated_forced_teacher_suffix", list(ctx["teacher_suffix"])),
                    ]:
                        if arm in stage_arms:
                            continue
                        row = continuation(ctx, arm, suffix)
                        stage_rows.append(row)
                        stage_arms.add(arm)
                        _save_stage(ctx, stage_rows)
                        _atom(output_dir / "progress.json", {"status": "running", "completed_rollouts": len(existing) + len(stage_rows), "committed_rollouts": len(existing), "staged_rollouts": len(stage_rows), "total_rollouts": rollout_cap, "current_context": cid, "current_arm": arm})
                finally:
                    peft_model = policy.model
                    policy.model = peft_model.unload()
                    del peft_model
                    torch.cuda.empty_cache()
                rollback = base_fingerprint(policy.model)
                if rollback != base_fp:
                    raise RuntimeError(f"{cid}: base rollback mismatch")
                rollback_mode = "same_process_unload_fingerprint_exact"
            else:
                if base_fingerprint(policy.model) != base_fp:
                    raise RuntimeError(f"{cid}: clean base mismatch before committing resumed updated arms")
                rollback_mode = "fresh_process_recovery_before_any_later_context"

            _commit_stage(ctx, stage_rows, rollback_mode)
            existing = _load_committed_rows()
            completed_contexts.add(cid)
            _atom(output_dir / "progress.json", {"status": "running", "completed_rollouts": len(existing), "total_rollouts": rollout_cap, "current_context": cid, "current_arm": "context_commit"})

        analysis = analyze(existing, contract)
        _atom(output_dir / "analysis.json", analysis)
        _atom(output_dir / "decision.json", {
            "schema_version": "1.0",
            "experiment_id": contract["experiment_id"],
            "decision": analysis["decision"],
            "complete_contexts": analysis["complete_contexts"],
            "nonzero_residual_contexts": analysis["nonzero_residual_contexts"],
            "residual_task_families": analysis["residual_task_families"],
            "negative_residual_contexts": analysis["negative_residual_contexts"],
            "positive_residual_contexts": analysis["positive_residual_contexts"],
            "strong_risk_flag": analysis["strong_risk_flag"],
            "paper_design_authorized": False,
            "method_authorized": False,
            "p0_authorized": False,
            "next_action": analysis["next_action"],
        })
        _atom(output_dir / "progress.json", {"status": "complete", "completed_rollouts": len(existing), "total_rollouts": rollout_cap, "decision": analysis["decision"]})
        return analysis
    except Exception as exc:
        _atom(output_dir / "execution-error.json", {
            "schema_version": "1.0",
            "experiment_id": contract["experiment_id"],
            "error": repr(exc),
            "completed_rollouts": len(existing),
            "scientific_belief_update_allowed": False,
        })
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--gpu-uuid", required=True)
    parser.add_argument("--legacy-source-root", type=Path, required=True)
    parser.add_argument("--wall-hours-cap", type=float, default=0.85)
    parser.add_argument("--rollout-cap", type=int, default=48)
    args = parser.parse_args()
    result = run(
        contract_path=args.contract,
        output_dir=args.output_dir,
        model_path=args.model_path,
        gpu_uuid=args.gpu_uuid,
        legacy_source_root=args.legacy_source_root,
        wall_hours_cap=args.wall_hours_cap,
        rollout_cap=args.rollout_cap,
    )
    print(json.dumps({k: result[k] for k in ("decision", "complete_contexts", "nonzero_residual_contexts", "residual_task_families", "negative_residual_contexts", "positive_residual_contexts")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
