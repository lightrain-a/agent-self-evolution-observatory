from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
OUT = HERE / "c1-prerequisite-diagnostic-completeness-20260828.json"
COORDS = ("W", "E", "U", "O", "F")
NATIVE = ("W", "E", "U", "O")


def state(prefix_depth: int, forced_capacity: int) -> dict[str, int]:
    if prefix_depth not in range(5):
        raise ValueError(prefix_depth)
    if forced_capacity not in (0, 1):
        raise ValueError(forced_capacity)
    return {
        "W": int(prefix_depth >= 1),
        "E": int(prefix_depth >= 2),
        "U": int(prefix_depth >= 3),
        "O": int(prefix_depth >= 4),
        "F": forced_capacity,
    }


def projection(row: dict[str, int], observed: Iterable[str]) -> tuple[int, ...]:
    return tuple(row[key] for key in observed)


def main() -> int:
    states = []
    for prefix_depth in range(5):
        for forced_capacity in (0, 1):
            values = state(prefix_depth, forced_capacity)
            states.append(
                {
                    "state_id": f"p{prefix_depth}-f{forced_capacity}",
                    "prefix_depth": prefix_depth,
                    "forced_capacity": forced_capacity,
                    "values": values,
                }
            )

    subsets = []
    injective_subsets = []
    for r in range(len(COORDS) + 1):
        for observed in itertools.combinations(COORDS, r):
            buckets: dict[tuple[int, ...], list[str]] = {}
            for row in states:
                key = projection(row["values"], observed)
                buckets.setdefault(key, []).append(row["state_id"])
            ambiguous_groups = [group for group in buckets.values() if len(group) > 1]
            ambiguous_pair_count = sum(len(group) * (len(group) - 1) // 2 for group in ambiguous_groups)
            injective = not ambiguous_groups
            if injective:
                injective_subsets.append(list(observed))
            subsets.append(
                {
                    "observed": list(observed),
                    "size": len(observed),
                    "injective": injective,
                    "distinct_projections": len(buckets),
                    "ambiguous_group_count": len(ambiguous_groups),
                    "ambiguous_pair_count": ambiguous_pair_count,
                    "ambiguous_groups": ambiguous_groups,
                }
            )

    omit_one = {}
    for omitted in COORDS:
        observed = [coord for coord in COORDS if coord != omitted]
        row = next(item for item in subsets if item["observed"] == observed)
        omit_one[omitted] = {
            "observed": observed,
            "ambiguous_pair_count": row["ambiguous_pair_count"],
            "ambiguous_groups": row["ambiguous_groups"],
        }

    expected_native_pairs = {
        "W": [["p0-f0", "p1-f0"], ["p0-f1", "p1-f1"]],
        "E": [["p1-f0", "p2-f0"], ["p1-f1", "p2-f1"]],
        "U": [["p2-f0", "p3-f0"], ["p2-f1", "p3-f1"]],
        "O": [["p3-f0", "p4-f0"], ["p3-f1", "p4-f1"]],
    }
    for coord in NATIVE:
        actual = sorted(sorted(group) for group in omit_one[coord]["ambiguous_groups"])
        expected = sorted(sorted(group) for group in expected_native_pairs[coord])
        if actual != expected:
            raise RuntimeError(f"unexpected {coord}-omission aliases: {actual}")
        if omit_one[coord]["ambiguous_pair_count"] != 2:
            raise RuntimeError(f"unexpected {coord}-omission pair count")
    if omit_one["F"]["ambiguous_pair_count"] != 5:
        raise RuntimeError("omitting F must alias both capacity states at every prefix depth")
    if injective_subsets != [list(COORDS)]:
        raise RuntimeError(f"full basis is not the unique injective subset: {injective_subsets}")
    if len(states) != 10 or len(subsets) != 32:
        raise RuntimeError("state/subset geometry drift")

    canonical_state_table = [
        {
            "prefix_depth": p,
            "interpretation": (
                "no native branch-specific state",
                "write only",
                "written and exposed",
                "first-action uptake",
                "terminal transport",
            )[p],
            "W": int(p >= 1),
            "E": int(p >= 2),
            "U": int(p >= 3),
            "O": int(p >= 4),
            "forced_capacity_variants": [0, 1],
        }
        for p in range(5)
    ]

    payload = {
        "schema_version": "1.0",
        "artifact_kind": "C1_PREREQUISITE_DIAGNOSTIC_COMPLETENESS",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "generated_at": "2026-08-28",
        "scientific_object": "diagnostic distinguishability induced by the paper's native prerequisite order plus an independent forced-capacity bit",
        "model": {
            "coordinates": list(COORDS),
            "native_prerequisite_order": "O => U => E => W",
            "prefix_depths": 5,
            "forced_capacity_values": [0, 1],
            "diagnostic_states": 10,
            "observed_surface_subsets": 32,
        },
        "state_table": canonical_state_table,
        "result": {
            "injective_subsets": injective_subsets,
            "unique_minimal_separating_basis": list(COORDS),
            "full_basis_is_unique_injective_subset": True,
            "omit_one": omit_one,
            "all_subsets": subsets,
        },
        "lemma": "For the complete 10-state class induced by native prefix depth p in {0,1,2,3,4} and independent forced-capacity F in {0,1}, projection onto observed surfaces A subseteq {W,E,U,O,F} is injective if and only if A is the full five-surface basis.",
        "proof_sketch": "The full signature is injective. Omitting native coordinate j aliases adjacent prefix depths j-1 and j separately for F=0 and F=1, while omitting F aliases the two capacity states at every prefix depth. Exhaustive enumeration independently verifies all 32 subsets.",
        "claim_boundary": "This is a paper-specific exact diagnostic-completeness result for the stated binary prerequisite class. It is not a universal taxonomy of stochastic memory mechanisms, and empirical NOT-SUPPORTED evidence is not coerced into literal zero.",
        "execution": {
            "provider_calls": 0,
            "gpu_runs": 0,
            "model_actions": 0,
            "scientific_empirical_outcomes_read": 0,
        },
        "authority": {
            "scientific": False,
            "experiment": False,
            "provider": False,
            "gpu": False,
            "submission": False,
        },
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["content_sha256_without_self"] = hashlib.sha256(encoded).hexdigest()
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"states": 10, "subsets": 32, "injective_subsets": injective_subsets, "provider_calls": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
