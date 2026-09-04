from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ORDER_SALT = "E2-R17-M3R4-EXECUTION-ORDER-v1"
SCIENTIFIC_OBJECT = "E2-R17-M3R4-FROZEN-STATE-ACTOR-LOCALIZATION-20260904"
REQUESTED_MODEL = "deepseek-v4-pro"
REQUIRED_RESOLVED_MODEL = "deepseek-v4-pro-ga-260813"
MAX_TURNS = 10
MAX_OUTPUT_TOKENS = 8192
TEMPERATURE = 0
THINKING = "disabled"
PROVIDER_RETRY_LIMIT = 0
MAX_PROVIDER_CALLS_PER_LOGICAL_UNIT = 10

TASK_IDS: tuple[str, ...] = (
    "r17-b4-agj-p2",
    "r17-b4-agj-p3",
    "r17-b4-agj-p8",
    "r17-b4-fmv-p1",
    "r17-b4-fmv-p2",
    "r17-b4-fmv-p8",
    "r17-b4-ioc-p1",
    "r17-b4-ioc-p4",
    "r17-b4-ioc-p6",
    "r17-b4-msp-p0",
    "r17-b4-msp-p7",
    "r17-b4-msp-p8",
    "r17-b4-ska-p4",
    "r17-b4-ska-p5",
    "r17-b4-ska-p8",
    "r17-b4-tsr-p0",
    "r17-b4-tsr-p6",
    "r17-b4-tsr-p8",
)


@dataclass(frozen=True)
class StateBinding:
    state_id: str
    skill_path: str
    skill_sha256: str
    update_receipt_path: str
    update_receipt_sha256: str
    parent_contract_sha256: str
    parent_authorization_sha256: str


STATE_BINDINGS: tuple[StateBinding, ...] = (
    StateBinding(
        state_id="ff_r1",
        skill_path="/data/wyt/e2-r17-search-projection/runs/single-case-first-fail-exact-replay-20260902/states/e1-tsr-00/replicate_1/first_fail/update/skill_post/SKILL.md",
        skill_sha256="596bd30b49935d16f35d51e9eed36e19567332cd8a9104ae50d832f91ffdf04f",
        update_receipt_path="/data/wyt/e2-r17-search-projection/runs/single-case-first-fail-exact-replay-20260902/states/e1-tsr-00/replicate_1/first_fail/update/update_receipt.json",
        update_receipt_sha256="332fd5d3a265c01c3be5887fa3e8f40c37d1f0e5c5825840a8fddc257b83a5c1",
        parent_contract_sha256="dd508d9cefb3bfba1a439f784f718cb7962f78130b83c18f14e5b0d591478dea",
        parent_authorization_sha256="e5d5a8ac04fe8b924327672e5b4efbe82ab053a6882ec5167d2771f8d06b84e4",
    ),
    StateBinding(
        state_id="ff_r2",
        skill_path="/data/wyt/e2-r17-search-projection/runs/single-case-first-fail-exact-replay-updater-recovery-v2-20260902/states/e1-tsr-00/replicate_2/first_fail/update/skill_post/SKILL.md",
        skill_sha256="fb5454a27faf8182ba1b0d722273c4377d4762815cd1898c3780cc8ff336615e",
        update_receipt_path="/data/wyt/e2-r17-search-projection/runs/single-case-first-fail-exact-replay-updater-recovery-v2-20260902/states/e1-tsr-00/replicate_2/first_fail/update/update_receipt.json",
        update_receipt_sha256="acf25c85f672010ccb0203365c309e53c574ea7840f81808c26a837f6d4e1cfa",
        parent_contract_sha256="9afbcd0d499a7e0a3ea9982975a9538f27033ef07b0e1a9043da7bf6b57c1ca9",
        parent_authorization_sha256="d4553bdddf2a8838b2866b917fe721c37d5510be27a8a21dadb57936c2fec7f2",
    ),
)


@dataclass(frozen=True)
class LogicalUnit:
    order_index: int
    round_index: int
    task_id: str
    state_id: str
    actor_replicate: int
    unit_id: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _hash_rank(values: Iterable[str], *, salt: str) -> list[str]:
    return sorted(
        (str(value) for value in values),
        key=lambda value: hashlib.sha256(f"{salt}|{value}".encode("utf-8")).hexdigest(),
    )


def logical_units() -> tuple[LogicalUnit, ...]:
    """Freeze a 72-unit hash-interleaved four-round actor schedule.

    Every task appears exactly once in each round.  A task's four state/replicate
    combinations are assigned to the four rounds by a content-hash-ranked Latin
    rotation.  The rank modulo four is deliberately used instead of hash modulo
    four so round-level treatment counts are deterministically balanced (5/5/4/4
    across the four combinations for 18 tasks), while each round's task traversal
    order is independently hash-ranked.

    This keeps actor replicates for the same task separated in time, prevents a
    state or replicate from occupying a contiguous execution block, and freezes
    all ordering before outcomes.  It does not make provider calls statistically
    independent; M3R4 retains separate runtime/iid/factorization qualifications.
    """

    combos: tuple[tuple[str, int], ...] = (
        ("ff_r1", 1),
        ("ff_r2", 1),
        ("ff_r1", 2),
        ("ff_r2", 2),
    )
    task_rank = _hash_rank(TASK_IDS, salt=f"{ORDER_SALT}|offset-rank")
    offsets = {task_id: rank % 4 for rank, task_id in enumerate(task_rank)}

    rows: list[LogicalUnit] = []
    order_index = 0
    for round_index in range(4):
        round_tasks = _hash_rank(TASK_IDS, salt=f"{ORDER_SALT}|round-{round_index}|task-order")
        for task_id in round_tasks:
            state_id, actor_replicate = combos[(round_index + offsets[task_id]) % 4]
            unit_id = f"round_{round_index}/{task_id}/{state_id}/actor_rep_{actor_replicate}"
            rows.append(
                LogicalUnit(
                    order_index=order_index,
                    round_index=round_index,
                    task_id=task_id,
                    state_id=state_id,
                    actor_replicate=actor_replicate,
                    unit_id=unit_id,
                )
            )
            order_index += 1
    validate_logical_units(rows)
    return tuple(rows)


def validate_logical_units(rows: Sequence[LogicalUnit]) -> None:
    if len(rows) != 72:
        raise ValueError(f"M3R4 requires exactly 72 logical units, got {len(rows)}")
    if [row.order_index for row in rows] != list(range(72)):
        raise ValueError("M3R4 order_index must be exact 0..71")
    if len({row.unit_id for row in rows}) != 72:
        raise ValueError("M3R4 logical unit IDs must be unique")
    if {row.task_id for row in rows} != set(TASK_IDS):
        raise ValueError("M3R4 task set drift")
    if {row.state_id for row in rows} != {"ff_r1", "ff_r2"}:
        raise ValueError("M3R4 state set drift")
    if {row.actor_replicate for row in rows} != {1, 2}:
        raise ValueError("M3R4 actor replicate set drift")
    for task_id in TASK_IDS:
        observed = {
            (row.state_id, row.actor_replicate)
            for row in rows
            if row.task_id == task_id
        }
        if observed != {("ff_r1", 1), ("ff_r1", 2), ("ff_r2", 1), ("ff_r2", 2)}:
            raise ValueError(f"M3R4 task combination drift: {task_id} -> {sorted(observed)}")
        rounds = {row.round_index for row in rows if row.task_id == task_id}
        if rounds != {0, 1, 2, 3}:
            raise ValueError(f"M3R4 task must appear exactly once per round: {task_id}")
    for round_index in range(4):
        round_rows = [row for row in rows if row.round_index == round_index]
        if len(round_rows) != 18 or len({row.task_id for row in round_rows}) != 18:
            raise ValueError(f"M3R4 round {round_index} task balance drift")
        counts = {
            combo: sum((row.state_id, row.actor_replicate) == combo for row in round_rows)
            for combo in (("ff_r1", 1), ("ff_r1", 2), ("ff_r2", 1), ("ff_r2", 2))
        }
        if sorted(counts.values()) != [4, 4, 5, 5]:
            raise ValueError(f"M3R4 round {round_index} treatment balance drift: {counts}")


def order_manifest() -> dict[str, Any]:
    rows = logical_units()
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-m3r4-logical-unit-order-manifest",
        "scientific_object": SCIENTIFIC_OBJECT,
        "order_salt": ORDER_SALT,
        "ordering_rule": "four_round_content_hash_ranked_latin_rotation_v1",
        "logical_units": [asdict(row) for row in rows],
        "unit_count": len(rows),
        "task_count": len(TASK_IDS),
        "state_count": 2,
        "actor_replicates_per_state_task": 2,
        "round_count": 4,
        "outcome_conditioned": False,
    }
    payload["logical_units_sha256"] = canonical_sha256(payload["logical_units"])
    return payload


def state_binding_map() -> dict[str, StateBinding]:
    return {row.state_id: row for row in STATE_BINDINGS}


def validate_state_bindings() -> None:
    if len(STATE_BINDINGS) != 2 or set(state_binding_map()) != {"ff_r1", "ff_r2"}:
        raise ValueError("M3R4 state bindings must contain exactly FF_R1 and FF_R2")
    for row in STATE_BINDINGS:
        skill = Path(row.skill_path)
        receipt = Path(row.update_receipt_path)
        if not skill.is_file() or sha256_file(skill) != row.skill_sha256:
            raise ValueError(f"M3R4 state skill drift: {row.state_id}")
        if not receipt.is_file() or sha256_file(receipt) != row.update_receipt_sha256:
            raise ValueError(f"M3R4 updater receipt drift: {row.state_id}")
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        if payload.get("status") != "COMPLETED":
            raise ValueError(f"M3R4 updater receipt is not completed: {row.state_id}")
        if payload.get("skill_post_sha256") != row.skill_sha256:
            raise ValueError(f"M3R4 updater receipt skill SHA drift: {row.state_id}")
        if Path(str(payload.get("skill_post_path") or "")).resolve() != skill.resolve():
            raise ValueError(f"M3R4 updater receipt skill path drift: {row.state_id}")
        if payload.get("contract_sha256") != row.parent_contract_sha256:
            raise ValueError(f"M3R4 parent contract provenance drift: {row.state_id}")
        if payload.get("authorization_sha256") != row.parent_authorization_sha256:
            raise ValueError(f"M3R4 parent authorization provenance drift: {row.state_id}")
        if int(payload.get("provider_retry_limit", -1)) != 0:
            raise ValueError(f"M3R4 parent updater receipt retry drift: {row.state_id}")


def structural_provider_budget() -> dict[str, Any]:
    total_units = len(logical_units())
    total_limit = total_units * MAX_PROVIDER_CALLS_PER_LOGICAL_UNIT
    return {
        "provider_retry_limit": PROVIDER_RETRY_LIMIT,
        "max_provider_calls_per_logical_unit": MAX_PROVIDER_CALLS_PER_LOGICAL_UNIT,
        "logical_units": total_units,
        "hard_max_provider_calls_structural": total_limit,
        "max_turns": MAX_TURNS,
        "derivation": "72 actor logical units x 10 max actor turns/calls; no updater calls",
        "claims_before_io": True,
        "claims_never_released": True,
        "automatic_retry": False,
        "unused_budget_reallocation": False,
    }


__all__ = [
    "ORDER_SALT",
    "SCIENTIFIC_OBJECT",
    "REQUESTED_MODEL",
    "REQUIRED_RESOLVED_MODEL",
    "MAX_TURNS",
    "MAX_OUTPUT_TOKENS",
    "TEMPERATURE",
    "THINKING",
    "PROVIDER_RETRY_LIMIT",
    "MAX_PROVIDER_CALLS_PER_LOGICAL_UNIT",
    "TASK_IDS",
    "STATE_BINDINGS",
    "StateBinding",
    "LogicalUnit",
    "canonical_sha256",
    "logical_units",
    "validate_logical_units",
    "order_manifest",
    "state_binding_map",
    "validate_state_bindings",
    "structural_provider_budget",
]
