from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from research_pipeline.e2_r17_evidence_window_v2 import (
    BLOCK_BOUNDARY,
    BLOCK_FOOTER,
    BLOCK_HEADER,
    ExactMatchedEvidenceBlockRenderer,
    MIN_SELECTED_SOURCE_TOKENS,
    canonical_trajectory_text,
)
from research_pipeline.e2_r17_mindmemos_updater import BlindedEvidenceUnit
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef, canonical_sha256

ARMS = (
    "win_c",
    "first_fail",
    "progress_fail",
    "progress_contrast",
)
FORBIDDEN_VISIBLE_MARKERS = (
    "win_c",
    "first_fail",
    "progress_fail",
    "progress_contrast",
    "rollout_index",
    "trajectory_sha256",
    "pool_id",
)


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _tool_call_name_sequence(trajectory: TrajectoryRef) -> tuple[str, ...]:
    payload = load_json(Path(trajectory.trajectory_path))
    names: list[str] = []
    for message in payload.get("messages") or []:
        if not isinstance(message, dict) or str(message.get("role") or "") != "assistant":
            continue
        for call in message.get("tool_calls") or []:
            name = (call.get("function") or {}).get("name")
            if name:
                names.append(str(name))
    return tuple(names)


def _provider_call_count(trajectory: TrajectoryRef) -> int:
    payload = load_json(Path(trajectory.trajectory_path))
    return len(payload.get("adapter_receipts") or [])


def _common_prefix_length(left: Sequence[str], right: Sequence[str]) -> int:
    count = 0
    for lvalue, rvalue in zip(left, right):
        if lvalue != rvalue:
            break
        count += 1
    return count


def progress_matched_failed_nonwinner(pool: SearchPool) -> TrajectoryRef:
    """Frozen diagnostic-witness selector used only by the new single-case pilot.

    Rule: minimize absolute tool-call count gap to the served winner, then absolute
    provider-call count gap, then maximize tool-name longest common prefix, then
    lowest rollout index. No held-out or future-skill outcome enters the selector.
    """
    pool.validate()
    if not pool.mixed_pool:
        raise ValueError("progress-matched failed witness exists only on mixed pools")
    winner = pool.winner
    winner_tools = _tool_call_name_sequence(winner)
    winner_provider_calls = _provider_call_count(winner)
    failures = [row for row in pool.trajectories if row.score == 0.0 and row.rollout_index != winner.rollout_index]
    if not failures:
        raise ValueError("mixed pool contains no failed non-winner")

    def key(row: TrajectoryRef) -> tuple[int, int, int, int]:
        tools = _tool_call_name_sequence(row)
        provider_calls = _provider_call_count(row)
        return (
            abs(len(tools) - len(winner_tools)),
            abs(provider_calls - winner_provider_calls),
            -_common_prefix_length(tools, winner_tools),
            row.rollout_index,
        )

    return min(failures, key=key)


def _safe_decode(encoding: Any, tokens: Sequence[int]) -> str:
    if hasattr(encoding, "decode_bytes"):
        return encoding.decode_bytes(list(tokens)).decode("utf-8", errors="ignore")
    return encoding.decode(list(tokens))


def _balanced_contrast_candidate(renderer: ExactMatchedEvidenceBlockRenderer, winner_tokens: Sequence[int], failure_tokens: Sequence[int], source_budget: int) -> tuple[str, int, int, int]:
    if source_budget < 4:
        raise ValueError("contrast source budget must be at least four tokens")
    winner_budget = max(2, source_budget // 2)
    failure_budget = max(2, source_budget - winner_budget)
    winner_budget = min(winner_budget, len(winner_tokens))
    failure_budget = min(failure_budget, len(failure_tokens))
    # If one branch is shorter than half, transfer only the unusable remainder to
    # the other branch.  With the frozen S1 trajectories both branches are long
    # enough, so the realized source allocation remains exactly 50/50 up to one token.
    unused = source_budget - winner_budget - failure_budget
    if unused > 0:
        add_w = min(unused, len(winner_tokens) - winner_budget)
        winner_budget += add_w
        unused -= add_w
    if unused > 0:
        failure_budget += min(unused, len(failure_tokens) - failure_budget)
    winner_text = _safe_decode(renderer.encoding, winner_tokens[:winner_budget])
    # Preserve the terminal diagnostic portion of the failed branch.
    failure_text = _safe_decode(renderer.encoding, failure_tokens[-failure_budget:])
    block = BLOCK_HEADER + winner_text + BLOCK_BOUNDARY + failure_text + BLOCK_FOOTER
    return block, len(renderer.encoding.encode(block)), winner_budget, failure_budget


def _contrast_reachable(renderer: ExactMatchedEvidenceBlockRenderer, winner_tokens: Sequence[int], failure_tokens: Sequence[int], *, start_budget: int, lower_bound: int) -> dict[int, tuple[int, str, int, int]]:
    reachable: dict[int, tuple[int, str, int, int]] = {}
    for budget in range(start_budget, lower_bound - 1, -1):
        block, actual, winner_budget, failure_budget = _balanced_contrast_candidate(renderer, winner_tokens, failure_tokens, budget)
        if actual > renderer.final_block_cap_tokens:
            continue
        reachable.setdefault(actual, (budget, block, winner_budget, failure_budget))
    return reachable


def render_four_arm_exact(
    renderer: ExactMatchedEvidenceBlockRenderer,
    *,
    win_text: str,
    first_fail_text: str,
    progress_fail_text: str,
) -> tuple[dict[str, str], dict[str, Any]]:
    singles = {
        "win_c": renderer.encoding.encode(win_text),
        "first_fail": renderer.encoding.encode(first_fail_text),
        "progress_fail": renderer.encoding.encode(progress_fail_text),
    }
    winner_tokens = renderer.encoding.encode(win_text)
    progress_tokens = renderer.encoding.encode(progress_fail_text)
    if any(len(tokens) < MIN_SELECTED_SOURCE_TOKENS for tokens in singles.values()) or len(progress_tokens) < MIN_SELECTED_SOURCE_TOKENS:
        raise ValueError("all S1 source evidences must contain at least 64 tokens")
    contrast_capacity = len(winner_tokens) + len(progress_tokens)
    start = min(min(len(tokens) for tokens in singles.values()), contrast_capacity, renderer.final_block_cap_tokens)
    lower_bounds: list[int] = []
    for width in (32, 128, 512, 1024, start):
        lower = max(MIN_SELECTED_SOURCE_TOKENS, start - int(width))
        if not lower_bounds or lower != lower_bounds[-1]:
            lower_bounds.append(lower)
    if lower_bounds[-1] != MIN_SELECTED_SOURCE_TOKENS:
        lower_bounds.append(MIN_SELECTED_SOURCE_TOKENS)

    for lower in lower_bounds:
        reachable = {name: renderer._reachable(tokens, start_budget=start, lower_bound=lower) for name, tokens in singles.items()}
        contrast_map = _contrast_reachable(renderer, winner_tokens, progress_tokens, start_budget=start, lower_bound=lower)
        common = set(contrast_map)
        for mapping in reachable.values():
            common.intersection_update(mapping)
        if not common:
            continue
        matched = max(common)
        blocks = {name: reachable[name][matched][1] for name in singles}
        contrast_budget, contrast_block, winner_budget, failure_budget = contrast_map[matched]
        blocks["progress_contrast"] = contrast_block
        actual = {name: len(renderer.encoding.encode(block)) for name, block in blocks.items()}
        if set(actual.values()) != {matched}:
            raise AssertionError(f"four-arm re-tokenized parity invariant failed: {actual}")
        if abs(winner_budget - failure_budget) > 1:
            raise AssertionError("contrast branch source allocation is not 50/50")
        return blocks, {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-diagnostic-witness-exact-matched-four-arm-block",
            "matched_final_block_tokens": matched,
            "final_block_cap_tokens": renderer.final_block_cap_tokens,
            "search_lower_bound": lower,
            "padding_used": False,
            "arm_metadata_visible": False,
            "single_selected_source_tokens": {name: int(reachable[name][matched][0]) for name in singles},
            "contrast_selected_source_tokens": contrast_budget,
            "contrast_winner_source_tokens": winner_budget,
            "contrast_failure_source_tokens": failure_budget,
            "contrast_source_allocation": "50/50",
            "search_candidate_counts": {**{name: len(reachable[name]) for name in singles}, "progress_contrast": len(contrast_map)},
            "block_sha256": {name: sha_text(blocks[name]) for name in ARMS},
        }
    raise RuntimeError("no exact common re-tokenized evidence length exists across four S1 arms")


@dataclass(frozen=True)
class DiagnosticStreamProjection:
    stream_id: str
    initial_skill_sha256: str
    pools: tuple[SearchPool, ...]
    projection: str
    packet_sha256s: tuple[str, ...]

    @property
    def packets(self) -> tuple[str, ...]:
        # run_projection_update only requires exact cardinality in the blinded path.
        return self.packet_sha256s

    @property
    def stream_sha256(self) -> str:
        return canonical_sha256(
            {
                "stream_id": self.stream_id,
                "initial_skill_sha256": self.initial_skill_sha256,
                "pool_ids": [pool.pool_id for pool in self.pools],
                "packet_sha256s": list(self.packet_sha256s),
                "projection": self.projection,
                "rule_version": "E2-R17-DIAGNOSTIC-WITNESS-S1-V1",
            }
        )


def make_diagnostic_stream(*, stream_id: str, initial_skill_sha256: str, pools: Sequence[SearchPool], arm: str, units: Sequence[BlindedEvidenceUnit]) -> DiagnosticStreamProjection:
    if arm not in ARMS:
        raise ValueError(f"unsupported diagnostic arm: {arm}")
    if len(pools) != 8 or len(units) != 8:
        raise ValueError("single-case diagnostic update requires eight pools/evidence units")
    if [pool.pool_id for pool in pools] != [unit.pool_id for unit in units]:
        raise ValueError("diagnostic stream evidence/pool order drift")
    return DiagnosticStreamProjection(
        stream_id=stream_id,
        initial_skill_sha256=initial_skill_sha256,
        pools=tuple(pools),
        projection=f"diagnostic_{arm}",
        packet_sha256s=tuple(unit.evidence_sha256 for unit in units),
    )


def validate_selector_freeze(pools: list[SearchPool], freeze: dict[str, Any]) -> None:
    if freeze.get("status") != "S0_SELECTOR_FREEZE_PASS_ZERO_PROVIDER":
        raise RuntimeError("single-case selector freeze is not passing")
    if freeze.get("case_stream") != "e1-tsr-00":
        raise RuntimeError("single-case selector freeze stream drift")
    rows = freeze.get("units") or []
    if len(rows) != 8 or len(pools) != 8:
        raise RuntimeError("selector-freeze/pool cardinality drift")
    by_task = {str(row["task_id"]): row for row in rows}
    if set(by_task) != {pool.task_id for pool in pools}:
        raise RuntimeError("selector freeze task set drift")
    changed = 0
    mixed = 0
    for pool in pools:
        row = by_task[pool.task_id]
        if row["pool_id"] != pool.pool_id or bool(row["mixed"]) != pool.mixed_pool:
            raise RuntimeError(f"selector-freeze pool identity drift: {pool.task_id}")
        if int(row["winner_rollout"]) != pool.winner.rollout_index:
            raise RuntimeError(f"selector-freeze winner drift: {pool.task_id}")
        if pool.mixed_pool:
            mixed += 1
            first = pool.first_failed_nonwinner
            progress = progress_matched_failed_nonwinner(pool)
            if int(row["first_fail_rollout"]) != first.rollout_index:
                raise RuntimeError(f"selector-freeze first-fail drift: {pool.task_id}")
            if int(row["progress_fail_rollout"]) != progress.rollout_index:
                raise RuntimeError(f"selector-freeze progress-fail drift: {pool.task_id}")
            observed_changed = first.rollout_index != progress.rollout_index
            if bool(row["selector_changed"]) != observed_changed:
                raise RuntimeError(f"selector-freeze change flag drift: {pool.task_id}")
            changed += int(observed_changed)
    if mixed != int(freeze.get("mixed_pool_count", -1)) or changed != int(freeze.get("selector_changed_mixed_pools", -1)):
        raise RuntimeError("selector-freeze aggregate drift")


def build_four_arm_evidence(
    pools: list[SearchPool],
    *,
    selector_freeze: dict[str, Any],
    final_block_cap_tokens: int,
    transcript_max_chars: int,
) -> tuple[dict[str, list[BlindedEvidenceUnit]], list[dict[str, Any]]]:
    if len(pools) != 8:
        raise ValueError("single-case updater requires exactly eight frozen pools")
    validate_selector_freeze(pools, selector_freeze)
    renderer = ExactMatchedEvidenceBlockRenderer(final_block_cap_tokens=final_block_cap_tokens)
    units: dict[str, list[BlindedEvidenceUnit]] = {arm: [] for arm in ARMS}
    receipts: list[dict[str, Any]] = []

    for pool in pools:
        win_ref = pool.winner
        first_ref = pool.first_failed_nonwinner if pool.mixed_pool else win_ref
        progress_ref = progress_matched_failed_nonwinner(pool) if pool.mixed_pool else win_ref
        refs = {
            "win_c": win_ref,
            "first_fail": first_ref,
            "progress_fail": progress_ref,
            "progress_contrast": progress_ref,
        }
        payloads = {name: load_json(Path(ref.trajectory_path)) for name, ref in refs.items()}
        for name, ref in refs.items():
            path = Path(ref.trajectory_path)
            if not path.is_file() or sha_file(path) != ref.trajectory_sha256:
                raise RuntimeError(f"trajectory SHA drift: {pool.task_id}/{name}")

        if pool.mixed_pool:
            rendered, parity = render_four_arm_exact(
                renderer,
                win_text=canonical_trajectory_text(payloads["win_c"]),
                first_fail_text=canonical_trajectory_text(payloads["first_fail"]),
                progress_fail_text=canonical_trajectory_text(payloads["progress_fail"]),
            )
        else:
            winner_text = canonical_trajectory_text(payloads["win_c"])
            rendered = {}
            # Pair rendering is sufficient here because all four raw sources are
            # exactly the same; copy the same byte-identical block into every arm.
            block, _, pair_receipt = renderer.render_pair(winner_text, winner_text)
            rendered = {arm: block for arm in ARMS}
            parity = {
                "schema_version": "1.0",
                "artifact_type": "e2-r17-diagnostic-witness-nonmixed-identical-block",
                "matched_final_block_tokens": pair_receipt.matched_final_block_tokens,
                "padding_used": False,
                "arm_metadata_visible": False,
                "block_sha256": {arm: sha_text(block) for arm in ARMS},
            }
        token_counts = {arm: len(renderer.encoding.encode(rendered[arm])) for arm in ARMS}
        if len(set(token_counts.values())) != 1:
            raise RuntimeError(f"four-arm token parity drift: {pool.task_id}: {token_counts}")
        for arm in ARMS:
            if len(f"[user] {rendered[arm]}") > transcript_max_chars:
                raise RuntimeError(f"{pool.task_id}/{arm} evidence would be downstream-truncated")
            for marker in FORBIDDEN_VISIBLE_MARKERS:
                if marker in rendered[arm]:
                    raise RuntimeError(f"arm/provenance marker leaked: {pool.task_id}/{arm}/{marker}")
        if not pool.mixed_pool and len({rendered[arm] for arm in ARMS}) != 1:
            raise RuntimeError(f"nonmixed four-arm evidence must be byte-identical: {pool.task_id}")

        for arm in ARMS:
            ref = refs[arm]
            source_score = 0.0 if arm == "progress_contrast" and pool.mixed_pool else float(ref.score)
            unit = BlindedEvidenceUnit(
                task_id=pool.task_id,
                pool_id=pool.pool_id,
                acting_winner_sha256=pool.winner.trajectory_sha256,
                source_rollout_index=ref.rollout_index,
                source_trajectory_sha256=ref.trajectory_sha256,
                source_score=source_score,
                evidence_text=rendered[arm],
                evidence_sha256=sha_text(rendered[arm]),
                evidence_tokens=token_counts[arm],
            )
            unit.validate()
            units[arm].append(unit)

        receipts.append(
            {
                "task_id": pool.task_id,
                "pool_id": pool.pool_id,
                "mixed_pool": pool.mixed_pool,
                "winner_rollout": win_ref.rollout_index,
                "first_fail_rollout": first_ref.rollout_index,
                "progress_fail_rollout": progress_ref.rollout_index,
                "selector_changed": first_ref.rollout_index != progress_ref.rollout_index,
                "matched_final_tokens": token_counts["win_c"],
                "evidence_sha256": {arm: sha_text(rendered[arm]) for arm in ARMS},
                "source_score": {arm: units[arm][-1].source_score for arm in ARMS},
                "parity": parity,
                "contrast_reference_winner_sha256": win_ref.trajectory_sha256,
                "contrast_failed_witness_sha256": progress_ref.trajectory_sha256,
            }
        )
    return units, receipts
