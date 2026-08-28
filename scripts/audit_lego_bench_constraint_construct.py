from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

EXPECTED_METADATA_SHA256 = "c4cab948b923b522b9ba4991e167e1c5c7d503786f2b2e5c11a64dab89113c21"
EXPECTED_INSTRUCTION_COUNT = 130
EXPECTED_CONSTRAINT_COUNT = 1250
EXPECTED_CONDITION_TYPES = {
    "Floor Layout",
    "Material Selection",
    "Object Placement",
    "Object Selection",
}
RAW_COUNT_LENGTH_RHO_REJECT_THRESHOLD = 0.70
TYPE_ENTROPY_LENGTH_RHO_CLEAR_THRESHOLD = 0.35
MATCH_MAX_WORD_DIFF = 10
MATCH_MIN_ENTROPY_DIFF_BITS = 0.35
MIN_STRICT_MATCHED_PAIRS_FOR_F0 = 10


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    j = 0
    while j < len(values):
        k = j
        while k + 1 < len(values) and values[order[k + 1]] == values[order[j]]:
            k += 1
        rank = (j + k) / 2.0 + 1.0
        for t in range(j, k + 1):
            out[order[t]] = rank
        j = k + 1
    return out


def _pearson(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("correlation vectors must be non-empty and equal length")
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    da = [x - ma for x in a]
    db = [y - mb for y in b]
    den = math.sqrt(sum(x * x for x in da) * sum(y * y for y in db))
    if den == 0:
        return float("nan")
    return sum(x * y for x, y in zip(da, db)) / den


def spearman(a: list[float], b: list[float]) -> float:
    return _pearson(_rank(a), _rank(b))


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9'-]+", text))


def ordinal_block(index: int) -> str:
    # A conservative metadata-only nuisance block. This is analyst-defined, not
    # an official LEGO-Bench category. It prevents strict F0 pairs from crossing
    # the conspicuous wording-style blocks in the released ordered metadata.
    if index < 50:
        return "000-049"
    if index < 100:
        return "050-099"
    return "100-129"


def entropy_bits(counts: Counter[str]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def validate_and_extract(data: Any) -> tuple[list[dict[str, Any]], list[str], list[int]]:
    if not isinstance(data, list) or len(data) != EXPECTED_INSTRUCTION_COUNT:
        raise ValueError(f"expected {EXPECTED_INSTRUCTION_COUNT} instructions")
    rows: list[dict[str, Any]] = []
    ignored_label_fields: set[str] = set()
    observed_types: set[str] = set()
    label_order_mismatch_rows: list[int] = []
    total_constraints = 0
    for index, item in enumerate(data):
        if not isinstance(item, dict) or set(item) != {"instruction", "constraints", "labels"}:
            raise ValueError(f"row {index}: unexpected top-level schema")
        instruction = item["instruction"]
        constraints = item["constraints"]
        labels = item["labels"]
        if not isinstance(instruction, str) or not isinstance(constraints, list) or not isinstance(labels, list):
            raise ValueError(f"row {index}: malformed instruction/constraints/labels")
        if len(constraints) != len(labels):
            raise ValueError(f"row {index}: constraint/label cardinality mismatch")
        type_counts: Counter[str] = Counter()
        seen_condition_indices: set[int] = set()
        order_mismatch = False
        for position, label in enumerate(labels):
            if not isinstance(label, dict):
                raise ValueError(f"row {index}: malformed label {position}")
            # Match the official evaluator: condition_idx is the binding key.
            # The released label list is not guaranteed to be in constraint
            # order (e.g. row 121), so list position must not define identity.
            try:
                condition_idx = int(str(label.get("condition_idx")))
            except ValueError as exc:
                raise ValueError(f"row {index}: invalid condition_idx at label {position}") from exc
            if condition_idx < 0 or condition_idx >= len(constraints) or condition_idx in seen_condition_indices:
                raise ValueError(f"row {index}: invalid/duplicate condition_idx {condition_idx}")
            seen_condition_indices.add(condition_idx)
            if condition_idx != position:
                order_mismatch = True
            # Only condition_idx + condition_type are consumed. All other
            # metadata fields are ignored; no score/validity/output field is
            # accepted or inspected by this audit.
            condition_type = str(label.get("condition_type") or "").strip()
            if condition_type not in EXPECTED_CONDITION_TYPES:
                raise ValueError(f"row {index}: unexpected condition type {condition_type!r}")
            observed_types.add(condition_type)
            type_counts[condition_type] += 1
            ignored_label_fields.update(set(label) - {"condition_idx", "condition_type"})
        if seen_condition_indices != set(range(len(constraints))):
            raise ValueError(f"row {index}: incomplete condition_idx coverage")
        if order_mismatch:
            label_order_mismatch_rows.append(index)
        n_constraints = len(constraints)
        total_constraints += n_constraints
        h = entropy_bits(type_counts)
        rows.append(
            {
                "index": index,
                "instruction_words": word_count(instruction),
                "constraint_count": n_constraints,
                "condition_type_counts": dict(sorted(type_counts.items())),
                "condition_type_diversity": len(type_counts),
                "condition_type_entropy_bits": h,
                "condition_type_entropy_normalized": h / 2.0,
                "ordinal_metadata_block": ordinal_block(index),
            }
        )
    if total_constraints != EXPECTED_CONSTRAINT_COUNT:
        raise ValueError(f"expected {EXPECTED_CONSTRAINT_COUNT} constraints, got {total_constraints}")
    if observed_types != EXPECTED_CONDITION_TYPES:
        raise ValueError(f"condition type set drift: {sorted(observed_types)}")
    return rows, sorted(ignored_label_fields), label_order_mismatch_rows


def strict_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    edges: list[tuple[int, float, int, int]] = []
    for i, a in enumerate(rows):
        for b in rows[i + 1 :]:
            if a["constraint_count"] != b["constraint_count"]:
                continue
            if a["ordinal_metadata_block"] != b["ordinal_metadata_block"]:
                continue
            word_diff = abs(a["instruction_words"] - b["instruction_words"])
            entropy_diff = abs(a["condition_type_entropy_bits"] - b["condition_type_entropy_bits"])
            if word_diff > MATCH_MAX_WORD_DIFF or entropy_diff < MATCH_MIN_ENTROPY_DIFF_BITS:
                continue
            edges.append((word_diff, -entropy_diff, a["index"], b["index"]))

    by_index = {row["index"]: row for row in rows}
    used: set[int] = set()
    selected: list[dict[str, Any]] = []
    for word_diff, negative_entropy_diff, i, j in sorted(edges):
        if i in used or j in used:
            continue
        used.update({i, j})
        a = by_index[i]
        b = by_index[j]
        low, high = (
            (a, b)
            if a["condition_type_entropy_bits"] <= b["condition_type_entropy_bits"]
            else (b, a)
        )
        selected.append(
            {
                "low_entropy_index": low["index"],
                "high_entropy_index": high["index"],
                "constraint_count": low["constraint_count"],
                "low_words": low["instruction_words"],
                "high_words": high["instruction_words"],
                "word_difference": word_diff,
                "low_entropy_bits": round(low["condition_type_entropy_bits"], 6),
                "high_entropy_bits": round(high["condition_type_entropy_bits"], 6),
                "entropy_difference_bits": round(-negative_entropy_diff, 6),
                "ordinal_metadata_block": low["ordinal_metadata_block"],
                "low_type_counts": low["condition_type_counts"],
                "high_type_counts": high["condition_type_counts"],
            }
        )
    return selected


def build_audit(metadata_path: Path) -> dict[str, Any]:
    digest = sha256_file(metadata_path)
    if digest != EXPECTED_METADATA_SHA256:
        raise ValueError(f"metadata SHA-256 mismatch: {digest}")
    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    rows, ignored_label_fields, label_order_mismatch_rows = validate_and_extract(data)

    counts = [float(row["constraint_count"]) for row in rows]
    words = [float(row["instruction_words"]) for row in rows]
    entropies = [float(row["condition_type_entropy_bits"]) for row in rows]
    diversity = [float(row["condition_type_diversity"]) for row in rows]
    raw_rho = spearman(counts, words)
    entropy_rho = spearman(entropies, words)
    diversity_rho = spearman(diversity, words)
    pairs = strict_pairs(rows)

    raw_disposition = (
        "REJECT_LENGTH_CONFOUNDED"
        if abs(raw_rho) >= RAW_COUNT_LENGTH_RHO_REJECT_THRESHOLD
        else "NOT_REJECTED_BY_LENGTH_CHECK"
    )
    entropy_disposition = (
        "CLEAR_FOR_ZERO_AUTHORITY_GENERATOR_REVIEW"
        if abs(entropy_rho) < TYPE_ENTROPY_LENGTH_RHO_CLEAR_THRESHOLD
        and len(pairs) >= MIN_STRICT_MATCHED_PAIRS_FOR_F0
        else "HOLD_CONSTRUCT_PREFLIGHT"
    )
    return {
        "schema_version": "lego-bench-outcome-blind-construct-audit-v1",
        "status": entropy_disposition,
        "scientific_authority": False,
        "execution_authority": False,
        "provider_calls_executed": 0,
        "gpu_calls_executed": 0,
        "outcome_exposure": {
            "per_case_generation_outcomes_read": False,
            "per_case_evaluator_validity_read": False,
            "performance_conditioned_selection": False,
            "published_aggregate_baseline_results_may_be_known": True,
            "aggregate_results_used_for_construct_selection": False,
            "consumed_fields": ["instruction", "constraints", "labels.condition_idx", "labels.condition_type"],
            "ignored_label_fields": ignored_label_fields,
            "label_order_mismatch_rows": label_order_mismatch_rows,
            "label_binding_rule": "condition_idx, matching the official evaluator; list position is never treated as constraint identity",
        },
        "source": {
            "dataset": "LEGO-Eval/LEGO_Bench",
            "metadata_file": "data/full_data.json",
            "metadata_sha256": digest,
            "instruction_count": len(rows),
            "constraint_count": int(sum(counts)),
            "condition_types": sorted(EXPECTED_CONDITION_TYPES),
        },
        "constructs": {
            "raw_constraint_count": {
                "definition": "number of released constraints attached to an instruction",
                "spearman_with_instruction_words": round(raw_rho, 6),
                "reject_threshold_abs_rho": RAW_COUNT_LENGTH_RHO_REJECT_THRESHOLD,
                "disposition": raw_disposition,
                "reason": "constraint count is too tightly coupled to instruction length to serve as the primary structural load variable",
            },
            "condition_type_entropy": {
                "definition": "Shannon entropy in bits over the four released LEGO constraint types",
                "max_bits": 2.0,
                "spearman_with_instruction_words": round(entropy_rho, 6),
                "clear_threshold_abs_rho": TYPE_ENTROPY_LENGTH_RHO_CLEAR_THRESHOLD,
                "condition_type_diversity_spearman_with_instruction_words": round(diversity_rho, 6),
                "disposition": entropy_disposition,
                "interpretation": "candidate measure of cross-type integration burden; not itself a causal mechanism or scientific result",
            },
        },
        "strict_matched_f0_feasibility": {
            "selection_uses_outcomes": False,
            "same_constraint_count": True,
            "same_analyst_defined_ordinal_metadata_block": True,
            "max_instruction_word_difference": MATCH_MAX_WORD_DIFF,
            "min_type_entropy_difference_bits": MATCH_MIN_ENTROPY_DIFF_BITS,
            "minimum_pairs_required": MIN_STRICT_MATCHED_PAIRS_FOR_F0,
            "selected_disjoint_pairs": len(pairs),
            "pairs": pairs,
            "role": "robustness/falsifier panel only; full-sample controlled analysis remains the primary future design if independently authorized",
        },
        "full_sample_future_control_set": {
            "rows": len(rows),
            "controls": [
                "constraint_count",
                "instruction_word_count",
                "analyst_defined_ordinal_metadata_block",
                "four per-type constraint counts",
                "generator identity",
            ],
            "strongest_same_information_null": "additive per-type difficulty model with the same observables and no cross-type interaction term",
            "candidate_disagreement": "after controlling total load, text length, metadata block, per-type counts, and generator identity, mixed-type integration exhibits a negative interaction/residual associated with higher type entropy",
        },
        "authority": {
            "canonical_generator": False,
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "provider": False,
            "gpu": False,
            "scientific": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = build_audit(args.metadata)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": audit["status"],
        "raw_count_rho": audit["constructs"]["raw_constraint_count"]["spearman_with_instruction_words"],
        "type_entropy_rho": audit["constructs"]["condition_type_entropy"]["spearman_with_instruction_words"],
        "strict_pairs": audit["strict_matched_f0_feasibility"]["selected_disjoint_pairs"],
        "scientific_authority": audit["scientific_authority"],
    }, indent=2))


if __name__ == "__main__":
    main()
