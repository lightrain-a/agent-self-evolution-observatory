from __future__ import annotations

import gc
import os
import subprocess
from pathlib import Path

import torch

import research_pipeline.relational_topology_official_training_dev_run_v15a as base
import research_pipeline.relational_topology_official_training_dev_run_v16a as persist
from research_pipeline.relational_topology_official_training_dev_v15a import (
    BATCH, OBJECT_ID, TrainingGateError, append, atom, build_config, file_sha,
    init_component, jsha, load, make_dataset, prepare, set_rng, verify_assets,
    verify_authority,
)


def _other_training_process_exists(run_root: Path, component: str) -> bool:
    me = os.getpid()
    out = subprocess.check_output(["ps", "-eo", "pid=,args="], text=True)
    root = str(run_root)
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        pid_text, _, args = line.partition(" ")
        try:
            pid = int(pid_text)
        except ValueError:
            continue
        if pid == me:
            continue
        if root in args and component in args and "official_training_developmental" in args:
            return True
    return False


def _create_or_reuse_step0_anchor(*, component: str, run_root: Path,
                                   authority: Path, proposal: Path, source: Path,
                                   bedroom: Path, split: Path, corpus_dir: Path,
                                   clip: Path, fvq: Path, bounds: Path,
                                   code_sha: str, device_index: int) -> Path:
    root = run_root / component
    anchor_meta = root / "initial_resume_anchor.json"
    if anchor_meta.is_file():
        meta = load(anchor_meta)
        path = Path(meta["checkpoint_path"])
        if not path.is_file() or file_sha(path) != meta["checkpoint_sha256"]:
            raise TrainingGateError("step0 resume anchor content-address drift")
        return path

    has_segments = (root / "segments").exists()
    has_checkpoints = (root / "checkpoints").exists() and any((root / "checkpoints").glob("*.pt"))
    if has_segments or has_checkpoints:
        raise TrainingGateError("cannot create step0 anchor after training artifacts exist")

    verify_authority(authority, proposal)
    verify_assets(source, clip, fvq, bounds)
    if not torch.cuda.is_available():
        raise TrainingGateError("CUDA unavailable for step0 anchor")
    set_rng()
    device = torch.device(f"cuda:{device_index}")
    cfg = build_config(source, component, bedroom)
    cfg_sha = jsha(cfg)
    ds = make_dataset(source, cfg)
    data = prepare(component, ds, split, corpus_dir)
    model, opt, ema, text, vq, init, params = init_component(
        source, component, cfg, ds, device, clip, fvq, bounds
    )
    ckdir = root / "checkpoints"
    ckdir.mkdir(exist_ok=True)
    row = base.save_checkpoint(
        root=ckdir, component=component, model=model, opt=opt, ema=ema,
        step=0, cursor=0, order=data["order"], content_sha=data["sha"],
        cfg_sha=cfg_sha, code_sha=code_sha, segment_id="initial-resume-anchor",
    )
    append(root / "checkpoint_manifest.jsonl", row)
    meta = {
        "object_id": OBJECT_ID,
        "component_id": component,
        "state": "STEP0_RESUME_ANCHOR_COMMITTED",
        "optimizer_steps": 0,
        "checkpoint_path": row["checkpoint_path"],
        "checkpoint_sha256": row["checkpoint_sha256"],
        "model_state_sha256": row["model_state_sha256"],
        "optimizer_state_sha256": row["optimizer_state_sha256"],
        "ema_state_sha256": row["ema_state_sha256"],
        "rng_state_sha256": row["rng_state_sha256"],
        "sampler_state_sha256": row["sampler_state_sha256"],
        "initial_model_state_sha256": init,
        "parameter_count": params,
        "training_code_sha": code_sha,
        "scientific_outcomes": 0,
        "outcomes_enter_p1": False,
    }
    atom(anchor_meta, meta)
    claim_path = root / "claim.json"
    claim = load(claim_path)
    if claim.get("state") != "RESOURCE_PREFLIGHT_PASS":
        raise TrainingGateError("claim state changed before step0 anchor commit")
    claim.update(
        optimizer_steps_committed=0,
        latest_checkpoint_path=row["checkpoint_path"],
        latest_checkpoint_sha256=row["checkpoint_sha256"],
        initial_resume_anchor_sha256=row["checkpoint_sha256"],
    )
    atom(claim_path, claim)
    del model, opt, ema, text, vq, ds, data
    gc.collect()
    torch.cuda.empty_cache()
    return Path(row["checkpoint_path"])


def _authorize_explicit_resume(*, component: str, run_root: Path,
                               resume: Path) -> None:
    root = run_root / component
    claim_path = root / "claim.json"
    claim = load(claim_path)
    state = claim.get("state")
    if state == "RESOURCE_PREFLIGHT_PASS":
        return
    if state not in {"TRAINING_RUNNING", "CHECKPOINT_COMMITTED", "FAIL_CLOSED"}:
        raise TrainingGateError(f"claim state not resumable: {state}")
    if _other_training_process_exists(run_root, component):
        raise TrainingGateError("another matching training process is still alive")
    expected_path = claim.get("latest_checkpoint_path")
    expected_sha = claim.get("latest_checkpoint_sha256")
    if not expected_path or not expected_sha:
        raise TrainingGateError("claim has no committed resume checkpoint")
    if Path(expected_path).resolve() != resume.resolve():
        raise TrainingGateError("resume path is not claim latest checkpoint")
    if not resume.is_file() or file_sha(resume) != expected_sha:
        raise TrainingGateError("resume checkpoint hash drift")
    claim.update(
        state="RESOURCE_PREFLIGHT_PASS",
        resume_transition_from=state,
        resume_checkpoint_sha256=expected_sha,
    )
    atom(claim_path, claim)


def train(*, component: str, run_root: Path, authority: Path, proposal: Path,
          source: Path, bedroom: Path, split: Path, corpus_dir: Path, clip: Path,
          fvq: Path, bounds: Path, code_sha: str, device_index: int = 0,
          resume: Path | None = None):
    persist._prepare_root_evidence(
        component=component, run_root=run_root, authority=authority,
        proposal=proposal, source=source, bedroom=bedroom, split=split,
        code_sha=code_sha,
    )
    if resume is None:
        resume = _create_or_reuse_step0_anchor(
            component=component, run_root=run_root, authority=authority,
            proposal=proposal, source=source, bedroom=bedroom, split=split,
            corpus_dir=corpus_dir, clip=clip, fvq=fvq, bounds=bounds,
            code_sha=code_sha, device_index=device_index,
        )
    _authorize_explicit_resume(component=component, run_root=run_root, resume=resume)
    return persist.train(
        component=component, run_root=run_root, authority=authority,
        proposal=proposal, source=source, bedroom=bedroom, split=split,
        corpus_dir=corpus_dir, clip=clip, fvq=fvq, bounds=bounds,
        code_sha=code_sha, device_index=device_index, resume=resume,
    )
