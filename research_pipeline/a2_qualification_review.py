from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .p0_alfworld_collect import _task_key


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build(qualification_path: Path, sequences_path: Path, *, minimum_sequences: int = 9) -> dict[str, Any]:
    qualification = _load(qualification_path)
    sequences = _read_jsonl(sequences_path)
    sequence_count = int(qualification.get("sequence_count") or len(sequences))
    complete = sequence_count >= minimum_sequences and len(sequences) >= minimum_sequences
    archetype_pass = bool(qualification.get("archetype_pass"))
    controller_pass = bool(qualification.get("controller_disagreement_pass"))
    tiny_pass = bool((qualification.get("tiny_real_subset") or {}).get("pass"))
    exclusion_keys = sorted({_task_key(str(row.get("task_id") or "")) for row in sequences if row.get("task_id")})
    oracle_success_bearing = sum(
        any(float(round_row.get("success") or 0.0) > 0.0 for round_row in (row.get("rounds") or []))
        for row in sequences
    )
    authorization_effect = "may-unblock" if complete else "may-block-only"
    independent_validation = complete
    check_updates = {
        "target_variation": {
            "pass": bool(complete and archetype_pass),
            "evidence": (
                f"Current ALFWorld A2-R1 qualification used {sequence_count} frozen sequences: "
                f"optimal-round entropy={float(qualification.get('optimal_round_entropy_bits') or 0.0):.3f} bits, "
                f"oracle-success-bearing={oracle_success_bearing}/{sequence_count}, "
                f"non-early={int(qualification.get('non_early_optimal_sequences') or 0)}, "
                f"rollback/harm={int(qualification.get('rollback_or_harm_sequences') or 0)}, "
                f"jackknife-min-entropy={float(qualification.get('jackknife_min_entropy_bits') or 0.0):.3f}."
            ),
        },
        "baseline_disagreement": {
            "pass": bool(complete and controller_pass),
            "evidence": (
                f"LOO continue/stop AUC={float(qualification.get('leave_one_sequence_out_continue_stop_auc') or 0.0):.3f}; "
                f"learned-vs-tuned-rule disagreements={int(qualification.get('controller_baseline_disagreement_sequences') or 0)}/{sequence_count}. "
                "A disagreement only counts as readiness evidence when the frozen controller also clears the preregistered LOO AUC gate."
            ),
        },
        "tiny_overfit": {
            "pass": bool(complete and tiny_pass),
            "evidence": (
                f"Frozen first-five-sequence tiny-fit AUC={float((qualification.get('tiny_real_subset') or {}).get('training_auc') or 0.0):.3f}; "
                "threshold=0.95."
            ),
        },
    }
    remaining = [key for key, row in check_updates.items() if not row["pass"]]
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "artifact_kind": "A2-R1-pre-experiment-evidence-review",
        "evidence_id": "a2-r1-alfworld-sequence-qualification",
        "idea_id": "budgeted-evolution-controller",
        "qualification_complete": complete,
        "minimum_sequences": minimum_sequences,
        "sequence_count": sequence_count,
        "authorization_effect": authorization_effect,
        "independent_validation": independent_validation,
        "same_substrate": True,
        "same_evaluation_batch_as_repair_selection": False,
        "check_updates": check_updates,
        "oracle_success_bearing_sequences": oracle_success_bearing,
        "excluded_qualification_task_keys": exclusion_keys,
        "excluded_qualification_task_count": len(exclusion_keys),
        "remaining_readiness_blockers": remaining,
        "next_action": (
            "Freeze qualification task exclusions in A2 screening/confirmatory configs and recompile the Pre-Experiment Card."
            if complete and not remaining else
            "Repair only the remaining A2 controller representation/tiny-fit blockers; do not rerun the 366-episode screening until the Pre-Experiment Card passes."
            if complete else
            "Complete the preregistered nine-sequence A2-R1 qualification before updating scientific readiness."
        ),
        "scientific_role": "pre-experiment readiness evidence only; never a method result",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert final A2-R1 qualification into a safe Pre-P0 evidence overlay and task-exclusion list.")
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--sequences", type=Path, required=True)
    parser.add_argument("--minimum-sequences", type=int, default=9)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = build(args.qualification, args.sequences, minimum_sequences=args.minimum_sequences)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
