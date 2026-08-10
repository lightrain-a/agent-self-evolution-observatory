from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build(qualification_traces: Path, *, panel_size: int = 6) -> dict[str, Any]:
    rows = [json.loads(line) for line in qualification_traces.read_text(encoding="utf-8").splitlines() if line.strip()]
    mastered: list[dict[str, Any]] = []
    for row in rows:
        trace = row.get("trace") or {}
        if int(trace.get("success") or 0) != 1:
            continue
        mastered.append({
            "task_id": str(trace.get("task_id") or trace.get("gamefile") or ""),
            "task_family": str(trace.get("task_family") or row.get("family") or "unknown"),
            "baseline_success": 1,
            "baseline_steps": int(trace.get("steps") or 0),
            "qualification_index": int(row.get("index") or 0),
        })
    if len(mastered) < panel_size:
        return {
            "schema_version": "1.0",
            "generated_at": _now(),
            "pass": False,
            "reason": "insufficient-mastered-id-tasks",
            "panel_size": panel_size,
            "mastered_candidates": len(mastered),
            "selected": [],
            "scientific_role": "probe-panel construction only; no method conclusion",
        }

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in mastered:
        groups[row["task_family"]].append(row)
    for family in groups:
        groups[family].sort(key=lambda row: (row["baseline_steps"], row["task_id"]))

    selected: list[dict[str, Any]] = []
    families = sorted(groups, key=lambda family: (len(groups[family]), family))
    while len(selected) < panel_size:
        advanced = False
        for family in families:
            if groups[family] and len(selected) < panel_size:
                selected.append(groups[family].pop(0))
                advanced = True
        if not advanced:
            break
    coverage = sorted({row["task_family"] for row in selected})
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "artifact_kind": "mastered-probe-panel",
        "source": str(qualification_traces),
        "selection_rule": "baseline-success-only; maximize family coverage by deterministic family round-robin; within family prefer shorter successful baseline trajectories",
        "panel_size": panel_size,
        "mastered_candidates": len(mastered),
        "task_family_coverage": len(coverage),
        "task_families": coverage,
        "selected": selected,
        "pass": len(selected) == panel_size and all(row["baseline_success"] == 1 for row in selected),
        "next_gate": "replay frozen development candidate patches on this panel; if development fidelity improves, freeze the panel/selection policy and validate on a fresh candidate batch before formal P0",
        "scientific_role": "development panel construction only; the same screening batch may not validate a panel selected using its hidden labels",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Select a deterministic regression-probe panel from mastered ID qualification tasks.")
    parser.add_argument("--qualification-traces", type=Path, required=True)
    parser.add_argument("--panel-size", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = build(args.qualification_traces, panel_size=args.panel_size)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
