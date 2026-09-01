from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from research_pipeline.e2_r17_repair2_manifest import ARMS, REPLICATES, require

ALLOWED_SOURCES = {
    "repair1_inherited",
    "repair2_m1_recovered",
    "repair2_v3_fresh",
    "repair2_v3_pair29_recovered",
    "repair2_continuation_v2_fresh",
}
EXPECTED_SOURCE_PAIRS = Counter(
    {
        "repair1_inherited": 14,
        "repair2_m1_recovered": 1,
        "repair2_v3_fresh": 13,
        "repair2_v3_pair29_recovered": 1,
        "repair2_continuation_v2_fresh": 19,
    }
)
EXPECTED_SOURCE_STATES = {
    "repair1_inherited": 28,
    "repair2_m1_recovered": 2,
    "repair2_v3_fresh": 26,
    "repair2_v3_pair29_recovered": 2,
    "repair2_continuation_v2_fresh": 38,
}
PAIR29_UNIT = "e1-msp-01/rep0"


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        value = str(row[key])
        require(value not in rows, f"duplicate {key}: {value}")
        rows[value] = row
    return rows


def validate_valid_rows_v2(
    rows: list[dict[str, Any]],
    *,
    streams: Iterable[str],
    quarantine: dict[str, Any],
    require_complete: bool,
) -> None:
    expected_streams = list(map(str, streams))
    expected_order = [f"{stream}/rep{rep}" for stream in expected_streams for rep in REPLICATES]
    seen: set[str] = set()
    per_stream: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    quarantine_unit = f"{quarantine['stream_id']}/rep{int(quarantine['replicate_id'])}"
    quarantine_root = str(quarantine["state_root"])

    for row in rows:
        unit_id = str(row["unit_id"])
        require(unit_id not in seen, f"duplicate valid pair: {unit_id}")
        seen.add(unit_id)
        stream = str(row["stream_id"])
        replicate = int(row["replicate_id"])
        source = str(row.get("source"))
        require(stream in expected_streams and replicate in REPLICATES, f"out-of-design pair: {unit_id}")
        require(unit_id == f"{stream}/rep{replicate}", f"unit id mismatch: {unit_id}")
        require(source in ALLOWED_SOURCES, f"invalid Continuation V2 source: {unit_id}")

        if unit_id == quarantine_unit:
            require(source == "repair2_m1_recovered", "quarantined Repair1 unit may enter only through audited M1 recovery")
        elif source == "repair2_m1_recovered":
            raise RuntimeError("M1 recovery source attached to wrong unit")

        if unit_id == PAIR29_UNIT:
            require(source == "repair2_v3_pair29_recovered", "pair29 must enter through the audited measurement-only recovery")
        elif source == "repair2_v3_pair29_recovered":
            raise RuntimeError("pair29 recovery source attached to wrong unit")

        arms = row.get("arms") or {}
        require(set(arms) == set(ARMS), f"incomplete pair: {unit_id}")
        for arm in ARMS:
            binding = arms[arm]
            require(str(binding.get("state_root")) != quarantine_root, "quarantined Repair1 state cannot enter Continuation V2")
            require(
                all(binding.get(key) for key in ("skill_sha256", "update_receipt_sha256", "eval_manifest_path", "eval_manifest_sha256")),
                f"incomplete arm binding: {unit_id}/{arm}",
            )
        source_counts[source] += 1
        per_stream[stream] += 1

    ordered_prefix = expected_order[: len(rows)]
    require([str(row["unit_id"]) for row in rows] == ordered_prefix, "Continuation V2 valid manifest is not the frozen design prefix")

    if require_complete:
        require(len(rows) == 48 and seen == set(expected_order), "Continuation V2 valid manifest must contain exactly 48 design pairs")
        require(all(per_stream[stream] == 4 for stream in expected_streams), "Continuation V2 must contain four pairs per stream")
        require(source_counts == EXPECTED_SOURCE_PAIRS, "Continuation V2 source counts drift")
