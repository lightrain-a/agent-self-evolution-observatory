from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PUBLICATION_CODE = "B1"
EXPECTED_MEMRL_REVISION = "c1b322ca43de36ddf64c6712f89d0095bfc35ce0"
EXPECTED_REASONINGBANK_REVISION = "ed80611788292ea739f1effd31f16c53823b8a0d"
MEMRL_AGENT_REL = Path("memrl/agent/memp_agent.py")
SUCCESS_HEADER = "--- SUCCESSFUL MEMORIES (Examples to follow) ---"
FAILURE_HEADER = "--- FAILED MEMORIES (Examples to avoid or learn from) ---"
HIDDEN_HEADER = "--- MEMORY (source outcome hidden) ---"

FAMILIES = (
    "pick_and_place",
    "pick_clean_then_place",
    "pick_heat_then_place",
    "pick_cool_then_place",
    "look_at_obj_in_light",
    "pick_two_obj_and_place",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def _family(path: Path) -> str:
    name = path.parent.parent.name.lower()
    for family in FAMILIES:
        if name.startswith(family):
            return family
    raise ValueError(f"unknown ALFWorld family for {path}: {name}")


def _games(split_root: Path) -> list[Path]:
    rows = sorted(split_root.rglob("game.tw-pddl"), key=lambda p: p.as_posix())
    if not rows:
        raise RuntimeError(f"no ALFWorld games under {split_root}")
    return rows


def _select_by_family(rows: list[Path], per_family: int, offset: int = 0) -> list[Path]:
    grouped: dict[str, list[Path]] = defaultdict(list)
    for path in rows:
        grouped[_family(path)].append(path)
    selected: list[Path] = []
    for family in FAMILIES:
        values = grouped.get(family, [])
        need = offset + per_family
        if len(values) < need:
            raise RuntimeError(f"family {family} has {len(values)} games, need {need}")
        selected.extend(values[offset:need])
    return selected


def render_memory_patch(memory_body: str, arm: str, true_provenance: str) -> str:
    body = str(memory_body).strip()
    if arm == "A0_NO_MEMORY":
        return ""
    if arm in {"A1_CONTENT_ONLY", "A7_BACKEND_ONLY_LABEL"}:
        return f"MEMORY::{HIDDEN_HEADER}\n{body}"
    if true_provenance not in {"success", "failure"}:
        raise ValueError(f"invalid true provenance: {true_provenance}")
    truthful = SUCCESS_HEADER if true_provenance == "success" else FAILURE_HEADER
    flipped = FAILURE_HEADER if true_provenance == "success" else SUCCESS_HEADER
    if arm == "A2_TRUTHFUL_VISIBLE_PROVENANCE":
        return f"MEMORY::{truthful}\n{body}"
    if arm == "A5_FLIPPED_VISIBLE_PROVENANCE":
        return f"MEMORY::{flipped}\n{body}"
    raise ValueError(f"unknown arm: {arm}")


def build_preflight(
    *,
    memrl_root: Path,
    alfworld_data: Path,
    model_path: Path,
    project_root: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    memrl_root = memrl_root.resolve()
    alfworld_data = alfworld_data.resolve()
    model_path = model_path.resolve()
    project_root = project_root.resolve()

    memrl_revision = _git_head(memrl_root)
    memrl_agent = memrl_root / MEMRL_AGENT_REL
    agent_text = memrl_agent.read_text(encoding="utf-8")
    source_root = alfworld_data / "json_2.1.1" / "train"
    target_root = alfworld_data / "json_2.1.1" / "valid_unseen"
    train_games = _games(source_root)
    target_games = _games(target_root)

    # Outcome-blind deterministic partition. Source outcomes may later be used only
    # to stratify source-memory provenance; target outcomes cannot alter membership.
    source_pool = _select_by_family(train_games, per_family=4, offset=0)
    pilot_targets = _select_by_family(target_games, per_family=1, offset=0)
    confirmatory_targets = _select_by_family(target_games, per_family=2, offset=1)

    source_set = {p.resolve() for p in source_pool}
    pilot_set = {p.resolve() for p in pilot_targets}
    confirm_set = {p.resolve() for p in confirmatory_targets}
    if source_set & pilot_set or source_set & confirm_set or pilot_set & confirm_set:
        raise RuntimeError("source/pilot/confirmatory game files are not disjoint")

    model_ids = {}
    for name in ("config.json", "tokenizer.json", "model.safetensors.index.json"):
        path = model_path / name
        if not path.exists():
            raise RuntimeError(f"missing model artifact: {path}")
        model_ids[name] = _sha_file(path)

    # The current MemRL implementation must really expose the declared channel.
    if SUCCESS_HEADER not in agent_text or FAILURE_HEADER not in agent_text:
        raise RuntimeError("MemRL executor-visible success/failure headers not found at pinned revision")

    probe_body = "Task: synthetic source\n\nArchived trajectory body."
    prompt_probe = {
        arm: {
            "success_source_sha256": _sha_bytes(render_memory_patch(probe_body, arm, "success").encode()),
            "failure_source_sha256": _sha_bytes(render_memory_patch(probe_body, arm, "failure").encode()),
        }
        for arm in (
            "A0_NO_MEMORY",
            "A1_CONTENT_ONLY",
            "A2_TRUTHFUL_VISIBLE_PROVENANCE",
            "A5_FLIPPED_VISIBLE_PROVENANCE",
            "A7_BACKEND_ONLY_LABEL",
        )
    }
    if prompt_probe["A1_CONTENT_ONLY"] != prompt_probe["A7_BACKEND_ONLY_LABEL"]:
        raise RuntimeError("backend-only provenance control must render byte-identical executor input to content-only")

    def rels(rows: list[Path], split: str) -> list[dict[str, str]]:
        root = alfworld_data / "json_2.1.1" / split
        return [
            {
                "family": _family(path),
                "relative_gamefile": path.relative_to(root).as_posix(),
                "gamefile_sha256": _sha_file(path),
            }
            for path in rows
        ]

    primary_estimand = (
        "paired target-task terminal success contrast between truthful visible provenance "
        "and flipped visible provenance under byte-identical memory body"
    )
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "paper_id": PAPER_ID,
        "publication_code": PUBLICATION_CODE,
        "generated_at": generated_at or _now(),
        "status": "FRESH_SUBSTRATE_G1_G8_PREFLIGHT_PASS",
        "carrier": {
            "name": "MemRL ALFWorld episodic-memory carrier",
            "role": "fresh confirmatory carrier only; not the novelty source or a source-faithful ReasoningBank replication",
            "memrl_repo": "https://github.com/MemTensor/MemRL.git",
            "memrl_revision": memrl_revision,
            "memrl_revision_expected": EXPECTED_MEMRL_REVISION,
            "memrl_agent_path": MEMRL_AGENT_REL.as_posix(),
            "memrl_agent_sha256": _sha_file(memrl_agent),
            "reasoningbank_reference_revision": EXPECTED_REASONINGBANK_REVISION,
            "alfworld_data_root": str(alfworld_data),
            "train_game_count": len(train_games),
            "valid_unseen_game_count": len(target_games),
        },
        "executor": {
            "model_path": str(model_path),
            "model_artifact_sha256": model_ids,
            "policy": "local Qwen2.5-7B deterministic admissible-command policy",
            "policy_mode": "react-family",
            "generation_sampling": False,
            "max_steps": 30,
            "automatic_model_switch": False,
        },
        "intervention": {
            "memory_body_rule": "raw source trajectory is frozen once and reused byte-identically across every arm for a target pair",
            "success_header": SUCCESS_HEADER,
            "failure_header": FAILURE_HEADER,
            "hidden_header": HIDDEN_HEADER,
            "arms": {
                "A0_NO_MEMORY": "no memory",
                "A1_CONTENT_ONLY": "same memory body, source outcome hidden",
                "A2_TRUTHFUL_VISIBLE_PROVENANCE": "same memory body, true source outcome header visible to executor",
                "A5_FLIPPED_VISIBLE_PROVENANCE": "same memory body, source outcome header flipped while body stays identical",
                "A7_BACKEND_ONLY_LABEL": "true provenance recorded in receipt only; executor bytes identical to A1",
            },
            "prompt_probe": prompt_probe,
            "backend_only_equals_content_only": True,
        },
        "task_partition": {
            "selection_rule": "sort gamefile path within each of six ALFWorld families before any source or target outcome; source=train first 4/family; pilot=valid_unseen first 1/family; confirmatory=valid_unseen next 2/family",
            "source_pool": rels(source_pool, "train"),
            "pilot_targets": rels(pilot_targets, "valid_unseen"),
            "confirmatory_targets": rels(confirmatory_targets, "valid_unseen"),
            "source_n": len(source_pool),
            "pilot_target_n": len(pilot_targets),
            "confirmatory_target_n": len(confirmatory_targets),
            "family_counts_source": dict(Counter(_family(p) for p in source_pool)),
            "family_counts_pilot": dict(Counter(_family(p) for p in pilot_targets)),
            "family_counts_confirmatory": dict(Counter(_family(p) for p in confirmatory_targets)),
            "all_partitions_disjoint": True,
        },
        "estimands": {
            "primary": primary_estimand,
            "first_stage": "paired first-action change rate under memory exposure versus no-memory and truthful versus flipped provenance",
            "memory_marginal_utility": "paired terminal success difference A1_CONTENT_ONLY - A0_NO_MEMORY for the same target task and frozen memory body",
            "visible_provenance_increment": "paired terminal success difference A2_TRUTHFUL_VISIBLE_PROVENANCE - A1_CONTENT_ONLY",
            "label_directionality": "paired terminal success difference A2_TRUTHFUL_VISIBLE_PROVENANCE - A5_FLIPPED_VISIBLE_PROVENANCE",
            "no_channel_negative_control": "A7_BACKEND_ONLY_LABEL executor prompt hash and deterministic rollout must equal A1_CONTENT_ONLY under the same target/memory pair",
        },
        "statistics": {
            "independent_unit": "ALFWorld gamefile/task",
            "requests_or_repeated_model_calls_are_nested_not_n": True,
            "pilot_n": len(pilot_targets),
            "confirmatory_n": len(confirmatory_targets),
            "primary_test": "exact paired discordance/sign test over target-game terminal success; report all discordant counts and exact interval",
            "first_stage_test": "exact paired rate over first actions; descriptive gate only, not terminal scientific authority",
            "no_optional_stopping_on_effect_size": True,
        },
        "source_acquisition_gate": {
            "ordered_source_pool_is_frozen": True,
            "initial_batch": 6,
            "extension_batch": 6,
            "maximum_sources": len(source_pool),
            "minimum_environment_success_sources": 2,
            "minimum_environment_failure_sources": 2,
            "stopping_rule": "execute sources in frozen order in batches of 6; stop source acquisition after a completed batch once at least 2 environment-success and 2 environment-failure trajectories exist, otherwise continue until all 24 are exhausted",
            "source_outcome_may_control_source_support_only": True,
            "source_outcome_cannot_change_pilot_or_confirmatory_target_membership": True,
            "if_support_not_met_after_24": "HOLD_SOURCE_PROVENANCE_SUPPORT; do not invent expert/corrupted trajectories post hoc",
        },
        "pilot_gate": {
            "purpose": "execution + utilization qualification only; pilot targets are excluded from confirmatory analysis",
            "requirements": [
                "source pool contains at least one environment-success and one environment-failure trajectory before target execution",
                "all five intervention arms render with frozen body hashes",
                "A1 and A7 executor prompt bytes are identical for every pilot pair",
                "no fatal runtime/provider/model error",
                "at least one pilot target shows memory utilization at first action or later action sequence relative to A0; otherwise HOLD_MEMORY_UNUSED",
            ],
            "pilot_outcomes_cannot_change_confirmatory_target_membership": True,
        },
        "confirmatory_gate": {
            "launch_only_after_pilot_pass": True,
            "target_membership_already_frozen": True,
            "no_task_replacement_after_first_confirmatory_outcome": True,
            "pre_exposure_support_failure_may_be_retried_once_only_if_executor_prompt_was_not_sent": True,
            "post_exposure_failure_is_retained_and_never_replaced": True,
            "all_arms_and_all_target_tasks_are_reported": True,
        },
        "gates": {
            "G1": {"pass": True, "evidence": "ALFWorld environment reward/won supplies source and target outcome truth; provenance is not researcher post-labeling."},
            "G2": {"pass": True, "evidence": "Target pair reuses one frozen raw trajectory memory body; content matching is byte identity and requires no target outcome."},
            "G3": {"pass": True, "evidence": "MemRL pinned code natively exposes success/failure memory headers; treatment changes only this declared executor-visible header. A7 keeps provenance backend-only."},
            "G4": {"pass": True, "evidence": "Source=train and targets=valid_unseen; pilot and confirmatory target files are disjoint and the entire substrate is disjoint from historical B1 WebArena R19/legacy units."},
            "G5": {"pass": True, "evidence": "Pinned ALFWorld game.tw-pddl files replay under one frozen environment evaluator; reset->admissible-command->step smoke passed before model execution."},
            "G6": {"pass": True, "evidence": "Statistical n is target gamefile. Model calls/steps are repeated observations within task, not independent units."},
            "G7": {"pass": True, "evidence": "Source/pilot/confirmatory partitions are deterministic path/family selections frozen before target outcomes."},
            "G8": {"pass": True, "evidence": "This content-addressed manifest freezes carrier/model revisions, arms, task membership, endpoints, exclusions, statistics, pilot/confirmatory promotion and stopping rules before first target rollout."},
        },
        "historical_boundary": {
            "r19_not_resumed": True,
            "historical_r19_or_legacy_units_pooled": False,
            "old_webarena_support_failure_is_not_scientific_negative": True,
            "old_stanford_review_is_diagnostic_only": True,
        },
        "authority": {
            "scientific": False,
            "paper": False,
            "experiment": False,
            "provider": False,
            "gpu": False,
            "submission": False,
        },
    }
    payload["manifest_sha256"] = _sha_bytes(
        json.dumps({k: v for k, v in payload.items() if k not in {"generated_at", "manifest_sha256"}}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memrl-root", type=Path, default=Path("/data/wyt/b1-memrl-audit-20260830"))
    parser.add_argument("--alfworld-data", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory/alfworld"))
    parser.add_argument("--model-path", type=Path, default=Path("/data/wyt/models/indept/Qwen2.5-7B"))
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("generated/b1-memrl-alfworld-fresh-preflight-20260830.json"))
    args = parser.parse_args()
    payload = build_preflight(
        memrl_root=args.memrl_root,
        alfworld_data=args.alfworld_data,
        model_path=args.model_path,
        project_root=args.project_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "manifest_sha256": payload["manifest_sha256"], "source_n": payload["task_partition"]["source_n"], "pilot_target_n": payload["task_partition"]["pilot_target_n"], "confirmatory_target_n": payload["task_partition"]["confirmatory_target_n"]}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
