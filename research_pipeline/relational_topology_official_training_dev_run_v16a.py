from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

import research_pipeline.relational_topology_official_training_dev_run_v15a as base
from research_pipeline.relational_topology_official_training_dev_v15a import (
    OBJECT_ID, BATCH, STEPS, CKPT_EVERY, SEED,
    atom, build_config, file_sha, load,
)

ROOT = Path(__file__).resolve().parents[1]


def _git_head(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return None


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


def _prepare_root_evidence(*, component: str, run_root: Path, authority: Path,
                           proposal: Path, source: Path, bedroom: Path,
                           split: Path, code_sha: str) -> Path:
    root = run_root / component
    pre = load(root / "resource_preflight.json")
    claim = load(root / "claim.json")
    cfg = build_config(source, component, bedroom)
    authority_obj = load(authority)
    proposal_obj = load(proposal)

    atom(root / "manifest.json", {
        "object_id": OBJECT_ID,
        "component_id": component,
        "state": "TRAINING_READY",
        "classification": "DEVELOPMENTAL_OFFICIAL_TRAINING_NO_SCIENTIFIC_OUTCOME_ADMISSION",
        "training_seed": SEED,
        "batch_size": BATCH,
        "gradient_accumulation": 1,
        "logical_optimizer_steps": STEPS,
        "checkpoint_every_steps": CKPT_EVERY,
        "training_code_sha": code_sha,
        "resource_preflight_sha256": file_sha(root / "resource_preflight.json"),
        "scientific_outcomes": 0,
        "outcomes_enter_p1": False,
    })
    atom(root / "authority.json", {
        "authority_receipt_sha256": file_sha(authority),
        "proposal_sha256": file_sha(proposal),
        "normalized_authority": authority_obj["grant"]["normalized_authority"],
        "authority_state": authority_obj["state"],
        "proposal_state": proposal_obj["state"],
        "reproduction_evaluation": False,
        "p1": False,
        "scientific_outcomes": 0,
    })
    atom(root / "environment.json", pre["environment"] | {
        "resource_preflight_sha256": file_sha(root / "resource_preflight.json"),
        "training_code_sha": code_sha,
    })
    atom(root / "git_state.json", {
        "observatory_head": _git_head(ROOT),
        "instructscene_head": _git_head(source),
        "training_code_sha": code_sha,
        "authority_receipt_sha256": file_sha(authority),
        "proposal_sha256": file_sha(proposal),
    })
    atom(root / "dataset_manifest.json", {
        "split_path": str(split),
        "split_sha256": file_sha(split),
        "content_sha256": pre["content_sha256"],
        "batch_size": BATCH,
        "scientific_outcomes": 0,
    })
    atom(root / "corpus_manifest.json", {
        "component_id": component,
        "content_sha256": pre["content_sha256"],
        "config_sha256": pre["config_sha256"],
        "first_batch_keys_sha256": pre["first_batch_keys_sha256"],
        "claim_key": claim["claim_key"],
    })
    atom(root / "model_manifest.json", {
        "component_id": component,
        "initial_model_state_sha256": pre["initial_model_state_sha256"],
        "parameter_count": pre["parameter_count"],
        "training_code_sha": code_sha,
        "scientific_outcomes": 0,
    })
    (root / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=True))
    for name in (
        "training_events.jsonl", "loss.jsonl", "checkpoint_manifest.jsonl",
        "failures.jsonl", "stdout.log", "stderr.log",
    ):
        _touch(root / name)
    atom(root / "heartbeat.json", {
        "object_id": OBJECT_ID,
        "component_id": component,
        "state": "TRAINING_READY",
        "global_step": 0,
        "scientific_outcomes": 0,
    })
    atom(root / "final_training_summary.json", {
        "object_id": OBJECT_ID,
        "component_id": component,
        "state": "PENDING",
        "scientific_outcomes": 0,
        "outcomes_enter_p1": False,
    })
    return root


def train(*, component: str, run_root: Path, authority: Path, proposal: Path,
          source: Path, bedroom: Path, split: Path, corpus_dir: Path, clip: Path,
          fvq: Path, bounds: Path, code_sha: str, device_index: int = 0,
          resume: Path | None = None):
    root = _prepare_root_evidence(
        component=component, run_root=run_root, authority=authority,
        proposal=proposal, source=source, bedroom=bedroom, split=split,
        code_sha=code_sha,
    )
    original_append = base.append

    def mirrored_append(path: Path, obj) -> None:
        original_append(path, obj)
        if path.parent.parent == root / "segments" and path.name in {
            "training_events.jsonl", "loss.jsonl", "failures.jsonl"
        }:
            original_append(root / path.name, obj)

    base.append = mirrored_append
    try:
        atom(root / "manifest.json", load(root / "manifest.json") | {"state": "TRAINING_RUNNING"})
        out = base.train(
            component=component, run_root=run_root, authority=authority,
            proposal=proposal, source=source, bedroom=bedroom, split=split,
            corpus_dir=corpus_dir, clip=clip, fvq=fvq, bounds=bounds,
            code_sha=code_sha, device_index=device_index, resume=resume,
        )
        atom(root / "manifest.json", load(root / "manifest.json") | {
            "state": "TRAINING_COMPLETE",
            "final_checkpoint_sha256": out["final_checkpoint_sha256"],
        })
        return out
    except Exception as exc:
        original_append(root / "failures.jsonl", {
            "object_id": OBJECT_ID,
            "component_id": component,
            "state": "FAIL_CLOSED_WRAPPER",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "scientific_outcomes": 0,
        })
        atom(root / "manifest.json", load(root / "manifest.json") | {"state": "FAIL_CLOSED"})
        raise
    finally:
        base.append = original_append
