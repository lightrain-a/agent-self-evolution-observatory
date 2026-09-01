#!/usr/bin/env python3
"""Strict R47 preflight for R45-M1.

Scientific arms/schedule/outcome rule are unchanged.  Before opening any of the
8 utilization treatments, require the strict R46M2 receipt and ensure every
utilization representative can realize U1 from a top frozen eligible retrieval.
"""
from __future__ import annotations

try:
    from . import failure_memory_memrl_utilization_r47m1 as base
except ImportError:
    import failure_memory_memrl_utilization_r47m1 as base  # type: ignore

STRICT_R46_ROLE = "R46M2_STRICT_PRIMARY_SUPPORT_ADJUDICATION_ZERO_VALIDATION_OUTCOME"
_original_preflight = base.preflight


def preflight(manifest, auth, qual, frozen, source_receipt):
    _original_preflight(manifest, auth, qual, frozen, source_receipt)
    if qual.get("role") != STRICT_R46_ROLE or qual.get("all_32_primary_clusters_supported") is not True:
        raise RuntimeError("strict-r46m2-primary-support-not-qualified")
    rows = [r for r in frozen.get("rows") or [] if r.get("cohort") == "utilization"]
    if len(rows) != 8:
        raise RuntimeError("utilization-row-count-drift")
    for row in rows:
        selected = list(row.get("selected") or [])
        if not selected:
            raise RuntimeError(f"utilization-U1-support-missing:{row.get('validation_task_id')}")
        top = selected[0]
        if top.get("eligible") is not True or not top.get("content") or type(top.get("source_outcome_success")) is not bool:
            raise RuntimeError(f"utilization-top-retrieval-not-eligible:{row.get('validation_task_id')}")


# r47m1.main() delegates into its imported original-r47 module. Rebind both
# layers so command-line execution cannot bypass this strict M2 preflight.
base.preflight = preflight
base.base.preflight = preflight

ARMS = base.ARMS
arm_order = base.arm_order
u4_map = base.u4_map
plan = base.plan
reverse_blocks = base.reverse_blocks
memctx = base.memctx
analyze = base.analyze


def main() -> None:
    base.main()


if __name__ == "__main__":
    main()
