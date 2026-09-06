from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SUITE_ROOT = Path("/data/wyt/e2-r17-search-projection/state-compiler-bridge-suite-v1-20260903")
SPLIT_PATH = SUITE_ROOT / "bridge_split_manifest.json"
SUITE_MANIFEST_PATH = SUITE_ROOT / "suite_manifest.json"
METADATA_PATH = SUITE_ROOT / "bridge_metadata.json"
PROTOCOL_PATH = ROOT / "generated/e2-r17-state-compiler-bridge-protocol-v4-r2-20260903.md"
REVIEW_PATH = ROOT / "generated/e2-r17-state-compiler-bridge-v4r2-preexecution-rereview-20260904.json"
SUITE_QUALIFICATION_PATH = ROOT / "generated/e2-r17-state-compiler-bridge-suite-qualification-20260903.json"

REQUESTED_MODEL = "deepseek-v4-pro"
REQUIRED_RESOLVED_MODEL = "deepseek-v4-pro-ga-260813"
PLAN_ROUTE = "https://ark.cn-beijing.volces.com/api/plan/v3"
MAX_TURNS = 10
MAX_OUTPUT_TOKENS = 8192
SEARCH_K = 8
HELDOUT_K = 1
PROVIDER_RETRY_LIMIT = 0
UPDATER_MAX_PROVIDER_CALLS = 11
ORDER_SALT = "E2-R17-BRIDGE-V4R2-EXECUTION-ORDER-v1"

SCREEN = "SCREEN"
VALIDATION = "VALIDATION"
STAGES = (SCREEN, VALIDATION)

SCREEN_ARMS = (
    "W_FREE",
    "W_COMP",
    "FF4_FREE_A",
    "FF4_COMP",
    "SCORE_ONLY_GENERIC_MAX",
    "SCOPE_MATCHED_GENERIC_MAX",
)
VALIDATION_ARMS = (
    "W_FREE",
    "W_COMP",
    "FF4_FREE_A",
    "FF4_FREE_B",
    "FF4_COMP",
    "SCORE_ONLY_GENERIC_MAX",
    "SCOPE_MATCHED_GENERIC_MAX",
)
FREE_STATE_ARMS = {
    SCREEN: ("W_FREE", "FF4_FREE_A"),
    VALIDATION: ("W_FREE", "FF4_FREE_A", "FF4_FREE_B"),
}
DETERMINISTIC_STATE_ARMS = {
    SCREEN: ("W_COMP", "FF4_COMP", "SCORE_ONLY_GENERIC_MAX", "SCOPE_MATCHED_GENERIC_MAX"),
    VALIDATION: ("W_COMP", "FF4_COMP", "SCORE_ONLY_GENERIC_MAX", "SCOPE_MATCHED_GENERIC_MAX"),
}
VALIDATION_REPLICATE2_ARMS = ("FF4_FREE_A", "FF4_FREE_B", "FF4_COMP")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _family_from_stream(stream_id: str) -> str:
    parts = stream_id.split("-")
    if len(parts) != 3 or parts[0] != "bridge":
        raise ValueError(f"invalid bridge stream id: {stream_id}")
    return parts[1]


def _family_from_task(task_id: str) -> str:
    parts = task_id.split("-")
    if len(parts) < 4 or parts[0] != "r17":
        raise ValueError(f"invalid bridge task id: {task_id}")
    return parts[2]


def _rank_key(kind: str, unit_id: str) -> str:
    return hashlib.sha256(f"{ORDER_SALT}|{kind}|{unit_id}".encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SearchUnit:
    stage: str
    stream_id: str
    task_id: str
    candidate_index: int
    unit_id: str
    max_provider_calls: int = MAX_TURNS


@dataclass(frozen=True)
class StateUnit:
    stage: str
    stream_id: str
    arm: str
    provider_required: bool
    unit_id: str
    max_provider_calls: int


@dataclass(frozen=True)
class ActorUnit:
    stage: str
    stream_id: str
    task_id: str
    arm: str
    actor_replicate: int
    unit_id: str
    exact_k: int = HELDOUT_K
    max_provider_calls: int = MAX_TURNS


def split_manifest() -> dict[str, Any]:
    return load_json(SPLIT_PATH)


def stage_stream_ids(stage: str) -> tuple[str, ...]:
    split = split_manifest()
    key = "screen_stream_ids" if stage == SCREEN else "validation_stream_ids" if stage == VALIDATION else None
    if key is None:
        raise ValueError(f"invalid stage: {stage}")
    return tuple(split[key])


def update_tasks(stream_id: str) -> tuple[str, ...]:
    rows = split_manifest()["update_streams"][stream_id]
    if len(rows) != 8 or len(set(rows)) != 8:
        raise RuntimeError(f"bridge update stream cardinality drift: {stream_id}")
    return tuple(rows)


def stage_heldout(stage: str) -> tuple[str, ...]:
    split = split_manifest()
    key = "screen_heldout" if stage == SCREEN else "validation_heldout" if stage == VALIDATION else None
    if key is None:
        raise ValueError(f"invalid stage: {stage}")
    return tuple(split[key])


def heldout_for_stream(stage: str, stream_id: str) -> tuple[str, ...]:
    family = _family_from_stream(stream_id)
    rows = tuple(task for task in stage_heldout(stage) if _family_from_task(task) == family)
    if len(rows) != 2:
        raise RuntimeError(f"bridge heldout family cardinality drift: {stage}/{stream_id}: {rows}")
    return rows


def search_units(stage: str) -> tuple[SearchUnit, ...]:
    units: list[SearchUnit] = []
    for stream_id in stage_stream_ids(stage):
        for task_id in update_tasks(stream_id):
            for candidate_index in range(1, SEARCH_K + 1):
                unit_id = f"{stage}/search/{stream_id}/{task_id}/k{candidate_index}"
                units.append(SearchUnit(stage, stream_id, task_id, candidate_index, unit_id))
    units.sort(key=lambda row: _rank_key("search", row.unit_id))
    return tuple(units)


def state_units(stage: str) -> tuple[StateUnit, ...]:
    units: list[StateUnit] = []
    for stream_id in stage_stream_ids(stage):
        for arm in FREE_STATE_ARMS[stage]:
            unit_id = f"{stage}/state/{stream_id}/{arm}"
            units.append(StateUnit(stage, stream_id, arm, True, unit_id, UPDATER_MAX_PROVIDER_CALLS))
        for arm in DETERMINISTIC_STATE_ARMS[stage]:
            unit_id = f"{stage}/state/{stream_id}/{arm}"
            units.append(StateUnit(stage, stream_id, arm, False, unit_id, 0))
    units.sort(key=lambda row: _rank_key("state", row.unit_id))
    return tuple(units)


def actor_units(stage: str) -> tuple[ActorUnit, ...]:
    arms = SCREEN_ARMS if stage == SCREEN else VALIDATION_ARMS if stage == VALIDATION else None
    if arms is None:
        raise ValueError(f"invalid stage: {stage}")
    units: list[ActorUnit] = []
    for stream_id in stage_stream_ids(stage):
        for task_id in heldout_for_stream(stage, stream_id):
            for arm in arms:
                unit_id = f"{stage}/actor/{stream_id}/{task_id}/{arm}/rep1"
                units.append(ActorUnit(stage, stream_id, task_id, arm, 1, unit_id))
            if stage == VALIDATION:
                for arm in VALIDATION_REPLICATE2_ARMS:
                    unit_id = f"{stage}/actor/{stream_id}/{task_id}/{arm}/rep2"
                    units.append(ActorUnit(stage, stream_id, task_id, arm, 2, unit_id))
    units.sort(key=lambda row: _rank_key("actor", row.unit_id))
    return tuple(units)


def stage_budget(stage: str) -> dict[str, int | bool | str]:
    searches = search_units(stage)
    states = state_units(stage)
    actors = actor_units(stage)
    search_calls = sum(row.max_provider_calls for row in searches)
    updater_calls = sum(row.max_provider_calls for row in states)
    actor_calls = sum(row.max_provider_calls for row in actors)
    actor_rep1_calls = sum(row.max_provider_calls for row in actors if row.actor_replicate == 1)
    actor_rep2_calls = sum(row.max_provider_calls for row in actors if row.actor_replicate == 2)
    return {
        "stage": stage,
        "search_rollout_units": len(searches),
        "search_k": SEARCH_K,
        "free_state_units": sum(row.provider_required for row in states),
        "deterministic_state_units": sum(not row.provider_required for row in states),
        "actor_logical_units_pre_alias": len(actors),
        "heldout_k": HELDOUT_K,
        "search_hard_max_provider_calls": search_calls,
        "free_updater_hard_max_provider_calls": updater_calls,
        "deterministic_compiler_provider_calls": 0,
        "heldout_actor_rep1_hard_max_provider_calls_pre_alias": actor_rep1_calls,
        "heldout_actor_rep2_hard_max_provider_calls_pre_alias": actor_rep2_calls,
        "heldout_actor_hard_max_provider_calls_pre_alias": actor_calls,
        "stage_hard_max_provider_calls_pre_alias": search_calls + updater_calls + actor_calls,
        "all_call_counts_are_structural_pre_alias_ceilings_not_expected_spend": True,
        "aliasing_can_only_reduce_actor_calls": True,
        "removed_alias_calls_reallocatable": False,
    }


def full_plan_payload() -> dict[str, Any]:
    split = split_manifest()
    suite = load_json(SUITE_MANIFEST_PATH)
    qualification = load_json(SUITE_QUALIFICATION_PATH)
    review = load_json(REVIEW_PATH)
    payload = {
        "schema_version": "1.0",
        "scientific_object": "E2-R17-STATE-COMPILER-BRIDGE-V4R2",
        "status": "ZERO_PROVIDER_EXECUTION_PLAN_ONLY",
        "order_salt": ORDER_SALT,
        "provider": {
            "route": PLAN_ROUTE,
            "requested_model": REQUESTED_MODEL,
            "required_resolved_model": REQUIRED_RESOLVED_MODEL,
            "thinking": "disabled",
            "temperature": 0,
            "provider_retry_limit": PROVIDER_RETRY_LIMIT,
            "max_turns": MAX_TURNS,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "search_k": SEARCH_K,
            "heldout_k": HELDOUT_K,
            "updater_max_provider_calls_per_state": UPDATER_MAX_PROVIDER_CALLS,
        },
        "bindings": {
            "protocol_path": str(PROTOCOL_PATH.relative_to(ROOT)),
            "protocol_sha256": sha256_file(PROTOCOL_PATH),
            "review_path": str(REVIEW_PATH.relative_to(ROOT)),
            "review_sha256": sha256_file(REVIEW_PATH),
            "suite_qualification_path": str(SUITE_QUALIFICATION_PATH.relative_to(ROOT)),
            "suite_qualification_sha256": sha256_file(SUITE_QUALIFICATION_PATH),
            "suite_root": str(SUITE_ROOT),
            "suite_manifest_sha256": sha256_file(SUITE_MANIFEST_PATH),
            "split_manifest_sha256": sha256_file(SPLIT_PATH),
            "metadata_sha256": sha256_file(METADATA_PATH),
        },
        "stage_rule": {
            "screen_executes_first": True,
            "validation_provider_io_before_raw_screen_pass": False,
            "validation_order_prefrozen_before_screen_outcomes": True,
            "screen_stream_ids": list(stage_stream_ids(SCREEN)),
            "validation_stream_ids": list(stage_stream_ids(VALIDATION)),
            "screen_heldout": list(stage_heldout(SCREEN)),
            "validation_heldout": list(stage_heldout(VALIDATION)),
        },
        "stages": {},
        "authority": {
            "provider_io": False,
            "search_pool_acquisition": False,
            "updater_execution": False,
            "actor_evaluation": False,
            "screen_opening": False,
            "validation_opening": False,
            "analysis": False,
            "e3": False,
            "public_benchmark": False,
            "second_backbone": False,
            "paper_promotion": False,
            "submission": False,
        },
        "scientific_outcomes_read": False,
    }
    for stage in STAGES:
        payload["stages"][stage] = {
            "stream_ids": list(stage_stream_ids(stage)),
            "update_tasks": {s: list(update_tasks(s)) for s in stage_stream_ids(stage)},
            "heldout_by_stream": {s: list(heldout_for_stream(stage, s)) for s in stage_stream_ids(stage)},
            "search_units": [asdict(row) for row in search_units(stage)],
            "state_units": [asdict(row) for row in state_units(stage)],
            "actor_units_pre_alias": [asdict(row) for row in actor_units(stage)],
            "budget": stage_budget(stage),
        }
    payload["sanity"] = {
        "suite_formal_tasks": suite["formal_task_count"],
        "split_outcome_blind": split["selection_is_outcome_blind"],
        "suite_qualification_status": qualification["status"],
        "independent_review_verdict": review["verdict"],
    }
    return payload


def canonical_sha256(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_plan() -> dict[str, Any]:
    payload = full_plan_payload()
    if payload["sanity"]["suite_formal_tasks"] != 120:
        raise RuntimeError("bridge formal task count drift")
    if payload["sanity"]["split_outcome_blind"] is not True:
        raise RuntimeError("bridge split no longer outcome-blind")
    if payload["sanity"]["suite_qualification_status"] != "PASS_ZERO_PROVIDER_FRESH_BRIDGE_SUITE_QUALIFICATION":
        raise RuntimeError("bridge suite qualification drift")
    if payload["sanity"]["independent_review_verdict"] != "PASS_PREEXECUTION_DESIGN":
        raise RuntimeError("bridge independent review verdict drift")
    if len(search_units(SCREEN)) != 384 or len(search_units(VALIDATION)) != 384:
        raise RuntimeError("bridge K=8 search cardinality drift")
    if len(state_units(SCREEN)) != 36 or len(state_units(VALIDATION)) != 42:
        raise RuntimeError("bridge state cardinality drift")
    if len(actor_units(SCREEN)) != 72 or len(actor_units(VALIDATION)) != 120:
        raise RuntimeError("bridge actor schedule cardinality drift")
    if stage_budget(SCREEN)["stage_hard_max_provider_calls_pre_alias"] != 4692:
        raise RuntimeError("bridge SCREEN budget derivation drift")
    if stage_budget(SCREEN)["heldout_actor_rep1_hard_max_provider_calls_pre_alias"] != 720:
        raise RuntimeError("bridge SCREEN heldout K=1/rep1 budget drift")
    if stage_budget(SCREEN)["heldout_actor_rep2_hard_max_provider_calls_pre_alias"] != 0:
        raise RuntimeError("bridge SCREEN must not have actor replicate2")
    if stage_budget(VALIDATION)["stage_hard_max_provider_calls_pre_alias"] != 5238:
        raise RuntimeError("bridge VALIDATION budget derivation drift")
    if stage_budget(VALIDATION)["heldout_actor_rep1_hard_max_provider_calls_pre_alias"] != 840:
        raise RuntimeError("bridge VALIDATION rep1 budget drift")
    if stage_budget(VALIDATION)["heldout_actor_rep2_hard_max_provider_calls_pre_alias"] != 360:
        raise RuntimeError("bridge VALIDATION Q3 rep2 budget drift")
    if set(stage_stream_ids(SCREEN)) & set(stage_stream_ids(VALIDATION)):
        raise RuntimeError("bridge stream stage overlap")
    if set(stage_heldout(SCREEN)) & set(stage_heldout(VALIDATION)):
        raise RuntimeError("bridge heldout stage overlap")
    return payload


__all__ = [
    "SCREEN", "VALIDATION", "STAGES", "SCREEN_ARMS", "VALIDATION_ARMS",
    "FREE_STATE_ARMS", "DETERMINISTIC_STATE_ARMS", "VALIDATION_REPLICATE2_ARMS",
    "SearchUnit", "StateUnit", "ActorUnit", "search_units", "state_units", "actor_units",
    "stage_stream_ids", "update_tasks", "stage_heldout", "heldout_for_stream", "stage_budget",
    "full_plan_payload", "canonical_sha256", "validate_plan", "sha256_file",
]
