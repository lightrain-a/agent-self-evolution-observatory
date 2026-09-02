#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FAMILIES = ("agj", "fmv", "ioc", "msp", "ska", "tsr")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def pearson(xs: list[float], ys: list[float]) -> float:
    require(len(xs) == len(ys) and len(xs) >= 2, "invalid correlation inputs")
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else float("nan")


def tool_call_count(trajectory: dict[str, Any]) -> int:
    return sum(
        len(message.get("tool_calls") or [])
        for message in trajectory.get("messages") or []
        if isinstance(message, dict)
    )


def task_family(task_id: str) -> str:
    return task_id.split("-")[2]


def stream_family(stream_id: str) -> str:
    return stream_id.split("-")[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--valid-manifest", type=Path, required=True)
    parser.add_argument("--support-adjudication", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--pool-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    require(not args.output.exists(), "mechanism development artifact already exists")
    adjudication = load_json(args.adjudication)
    support = load_json(args.support_adjudication)
    split = load_json(args.split_manifest)
    require(adjudication.get("status") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS", "unexpected V2 verdict")
    require(support.get("status") == "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT", "support artifact not passing")

    stream_effects = {
        str(row["stream_id"]): float(row["mean_difference_mrw_minus_win_c"])
        for row in adjudication["per_stream"]
    }
    require(set(stream_effects) == set(split["e1_update_streams"]), "stream set drift")
    mixed_counts = {str(k): int(v) for k, v in support["primary_support"]["per_stream_mixed_recomputed"].items()}

    valid_rows = {}
    for line in args.valid_manifest.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            valid_rows[str(row["unit_id"])] = row
    require(len(valid_rows) == 48, "expected full 48-pair V2 manifest")

    per_stream: list[dict[str, Any]] = []
    for stream_id, tasks in split["e1_update_streams"].items():
        D = stream_effects[stream_id]
        mixed_pool_count = 0
        failed_mass = 0
        rescue_count = 0
        selected_ratios: list[float] = []
        selected_token_gaps: list[int] = []
        selected_call_ratios: list[float] = []
        selected_call_gaps: list[int] = []
        selected_tool_call_gaps: list[int] = []
        selected_message_gaps: list[int] = []

        for task_id in tasks:
            pool_path = args.pool_root / str(task_id) / "pool_k8.json"
            require(pool_path.is_file(), f"missing pool: {task_id}")
            pool = load_json(pool_path)
            trajectories = pool["trajectories"]
            scores = [float(row["score"]) for row in trajectories]
            failures = [index for index, score in enumerate(scores) if score == 0.0]
            successes = [index for index, score in enumerate(scores) if score == 1.0]
            failed_mass += len(failures)
            rescue_count += int(bool(pool["rescue_event"]))
            if not failures or not successes:
                continue
            mixed_pool_count += 1
            winner_index = int(pool["acting_winner_index"])
            require(winner_index in successes, f"winner is not successful: {task_id}")
            failed_index = next(index for index in failures if index != winner_index)
            failed = trajectories[failed_index]
            winner = trajectories[winner_index]
            failed_tokens = int(failed["evidence_tokens"])
            winner_tokens = int(winner["evidence_tokens"])
            selected_ratios.append(failed_tokens / winner_tokens if winner_tokens else 0.0)
            selected_token_gaps.append(failed_tokens - winner_tokens)
            failed_trace = load_json(Path(failed["trajectory_path"]))
            winner_trace = load_json(Path(winner["trajectory_path"]))
            failed_calls = len(failed_trace.get("adapter_receipts") or [])
            winner_calls = len(winner_trace.get("adapter_receipts") or [])
            selected_call_ratios.append(failed_calls / winner_calls if winner_calls else 0.0)
            selected_call_gaps.append(failed_calls - winner_calls)
            selected_tool_call_gaps.append(tool_call_count(failed_trace) - tool_call_count(winner_trace))
            selected_message_gaps.append(len(failed_trace.get("messages") or []) - len(winner_trace.get("messages") or []))

        require(mixed_pool_count == mixed_counts[stream_id], f"mixed count drift: {stream_id}")

        # Existing V2 held-out outcomes are used only as development diagnostics.
        heldout_by_family: dict[str, list[float]] = {family: [] for family in FAMILIES}
        skill_char_deltas: list[int] = []
        skill_word_deltas: list[int] = []
        skill_line_deltas: list[int] = []
        for replicate in range(4):
            valid = valid_rows[f"{stream_id}/rep{replicate}"]
            arm_scores: dict[str, dict[str, float]] = {}
            for arm in ("mrw", "win_c"):
                binding = valid["arms"][arm]
                scores: dict[str, float] = {}
                for line in Path(binding["eval_manifest_path"]).read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    ref = load_json(Path(row["trajectory_ref_path"]))
                    scores[str(row["task_id"])] = float(ref["score"])
                arm_scores[arm] = scores
                skill_path = Path(binding["state_root"]) / "update/skill_post/SKILL.md"
                require(skill_path.is_file(), f"missing skill: {stream_id}/rep{replicate}/{arm}")
            for task_id, score in arm_scores["mrw"].items():
                heldout_by_family[task_family(task_id)].append(score - arm_scores["win_c"][task_id])

            mrw_text = (Path(valid["arms"]["mrw"]["state_root"]) / "update/skill_post/SKILL.md").read_text(encoding="utf-8")
            win_text = (Path(valid["arms"]["win_c"]["state_root"]) / "update/skill_post/SKILL.md").read_text(encoding="utf-8")
            skill_char_deltas.append(len(mrw_text) - len(win_text))
            skill_word_deltas.append(len(mrw_text.split()) - len(win_text.split()))
            skill_line_deltas.append(len(mrw_text.splitlines()) - len(win_text.splitlines()))

        heldout_family_means = {family: statistics.fmean(values) for family, values in heldout_by_family.items()}
        same_family = heldout_family_means[stream_family(stream_id)]
        off_family = statistics.fmean(value for family, value in heldout_family_means.items() if family != stream_family(stream_id))

        per_stream.append(
            {
                "stream_id": stream_id,
                "family": stream_family(stream_id),
                "v2_stream_effect": D,
                "mixed_pool_fraction": mixed_pool_count / 8.0,
                "failed_trajectory_fraction": failed_mass / 64.0,
                "rescue_event_fraction": rescue_count / 8.0,
                "selected_failure_to_winner_evidence_token_ratio": statistics.fmean(selected_ratios),
                "selected_failure_minus_winner_evidence_tokens": statistics.fmean(selected_token_gaps),
                "selected_failure_to_winner_provider_call_ratio": statistics.fmean(selected_call_ratios),
                "selected_failure_minus_winner_provider_calls": statistics.fmean(selected_call_gaps),
                "selected_failure_minus_winner_tool_calls": statistics.fmean(selected_tool_call_gaps),
                "selected_failure_minus_winner_messages": statistics.fmean(selected_message_gaps),
                "mean_mrw_minus_win_skill_chars": statistics.fmean(skill_char_deltas),
                "mean_mrw_minus_win_skill_words": statistics.fmean(skill_word_deltas),
                "mean_mrw_minus_win_skill_lines": statistics.fmean(skill_line_deltas),
                "heldout_effect_by_family": heldout_family_means,
                "same_family_heldout_effect": same_family,
                "off_family_heldout_effect": off_family,
                "same_minus_off_family_effect": same_family - off_family,
            }
        )

    keys = [
        "mixed_pool_fraction",
        "failed_trajectory_fraction",
        "rescue_event_fraction",
        "selected_failure_to_winner_evidence_token_ratio",
        "selected_failure_minus_winner_evidence_tokens",
        "selected_failure_to_winner_provider_call_ratio",
        "selected_failure_minus_winner_provider_calls",
        "selected_failure_minus_winner_tool_calls",
        "selected_failure_minus_winner_messages",
        "mean_mrw_minus_win_skill_chars",
        "mean_mrw_minus_win_skill_words",
        "mean_mrw_minus_win_skill_lines",
    ]
    correlations = {
        key: pearson([float(row[key]) for row in per_stream], [float(row["v2_stream_effect"]) for row in per_stream])
        for key in keys
    }

    family_effects: dict[str, list[float]] = defaultdict(list)
    for row in per_stream:
        family_effects[row["family"]].append(float(row["v2_stream_effect"]))
    family_summary = {
        family: {
            "stream_effects": values,
            "mean_effect": statistics.fmean(values),
        }
        for family, values in family_effects.items()
    }

    ordered_by_progress = sorted(per_stream, key=lambda row: row["selected_failure_to_winner_evidence_token_ratio"])
    low = ordered_by_progress[:6]
    high = ordered_by_progress[6:]

    same_family_mean = statistics.fmean(float(row["same_family_heldout_effect"]) for row in per_stream)
    off_family_mean = statistics.fmean(float(row["off_family_heldout_effect"]) for row in per_stream)

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v2-posthoc-mechanism-development-analysis",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "EXPLORATORY_DEVELOPMENT_ONLY_NO_CONFIRMATORY_AUTHORITY",
        "source_bindings": {
            "adjudication_path": str(args.adjudication),
            "adjudication_sha256": sha_file(args.adjudication),
            "valid_manifest_path": str(args.valid_manifest),
            "valid_manifest_sha256": sha_file(args.valid_manifest),
            "support_adjudication_path": str(args.support_adjudication),
            "support_adjudication_sha256": sha_file(args.support_adjudication),
            "split_manifest_path": str(args.split_manifest),
            "split_manifest_sha256": sha_file(args.split_manifest),
        },
        "v2_global_verdict_preserved": adjudication["status"],
        "n_streams": 12,
        "per_stream": per_stream,
        "exploratory_correlations_with_v2_stream_effect": correlations,
        "family_summary": family_summary,
        "progress_proxy_halves": {
            "lower_six_mean_progress_ratio": statistics.fmean(float(row["selected_failure_to_winner_evidence_token_ratio"]) for row in low),
            "lower_six_mean_v2_effect": statistics.fmean(float(row["v2_stream_effect"]) for row in low),
            "upper_six_mean_progress_ratio": statistics.fmean(float(row["selected_failure_to_winner_evidence_token_ratio"]) for row in high),
            "upper_six_mean_v2_effect": statistics.fmean(float(row["v2_stream_effect"]) for row in high),
        },
        "transfer_specificity": {
            "mean_same_family_heldout_effect": same_family_mean,
            "mean_off_family_heldout_effect": off_family_mean,
            "mean_same_minus_off_family_effect": statistics.fmean(float(row["same_minus_off_family_effect"]) for row in per_stream),
        },
        "development_interpretation": [
            "Mixed-pool availability is not a useful stand-alone predictor of V2 effect in the 12 completed streams.",
            "Failure-family identity is not sufficient to explain transfer: same-family heldout benefit is not larger than off-family benefit in this development sample.",
            "Coarse progress/proximity features of the actually selected rejected witness are more associated with V2 effect than mixed-pool count, motivating a prospective diagnostic-witness-quality intervention.",
            "These associations are post-hoc, n=12, and may not be reported as confirmatory evidence or used to claim a causal mediator without a new independent experiment.",
        ],
        "authority": {
            "provider_io": False,
            "new_scientific_execution": False,
            "confirmatory_claim": False,
            "paper_promotion": False,
            "submission": False,
        },
    }
    atomic_json(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "mixed_pool_r": correlations["mixed_pool_fraction"],
        "selected_failure_provider_call_gap_r": correlations["selected_failure_minus_winner_provider_calls"],
        "selected_failure_tool_call_gap_r": correlations["selected_failure_minus_winner_tool_calls"],
        "same_family_mean": same_family_mean,
        "off_family_mean": off_family_mean,
        "low_progress_mean_effect": payload["progress_proxy_halves"]["lower_six_mean_v2_effect"],
        "high_progress_mean_effect": payload["progress_proxy_halves"]["upper_six_mean_v2_effect"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
