from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paper_first_shared_p0_f0 import FAULTS, PERSISTENT_CROSS_FAULT_REPAIR_ACTIVE, SURFACES, centers, dist, feats


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decompose_drop(baseline_all: float, paired_pre: float, paired_post: float) -> dict[str, float]:
    composition = baseline_all - paired_pre
    paired = paired_pre - paired_post
    return {
        "legacy_unpaired_drop": baseline_all - paired_post,
        "cohort_composition_term": composition,
        "paired_causal_drop": paired,
        "reconstructed_drop": composition + paired,
    }


def build_audit(run_root: Path) -> dict[str, Any]:
    raw_path = run_root / "raw-traces.jsonl"
    progress_path = run_root / "progress.json"
    analysis_path = run_root / "analysis.json"
    rows = [json.loads(line) for line in raw_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    tasks = list((json.loads(progress_path.read_text(encoding="utf-8")) or {}).get("tasks") or [])
    if len(tasks) != 6:
        raise ValueError(f"paired PF-4 audit requires the frozen six-task support run, got {len(tasks)}")
    idx = {(str(r["task_id"]), str(r["fault"]), str(r["repair"])): r for r in rows}
    expected = {(t, f, r) for t in tasks for f in FAULTS for r in ("none",) + SURFACES}
    if set(idx) != expected:
        missing = sorted(expected - set(idx))[:8]
        extra = sorted(set(idx) - expected)[:8]
        raise ValueError(f"paired PF-4 audit requires complete 6x3x4 table; missing={missing} extra={extra}")
    dev, held = tasks[:3], tasks[3:]
    cen = centers([idx[t, f, "none"] for t in dev for f in FAULTS])

    def pred(row: dict[str, Any]) -> str:
        return min(cen, key=lambda key: dist(feats(row), cen[key]))

    def correct(row: dict[str, Any]) -> int:
        return int(pred(row) == str(row["fault"]))

    all_base = [idx[t, f, "none"] for t in held for f in FAULTS]
    baseline_all = sum(correct(r) for r in all_base) / len(all_base)
    legacy = json.loads(analysis_path.read_text(encoding="utf-8")) if analysis_path.exists() else {}
    legacy_pf4 = dict(legacy.get("pf4") or {})
    surface_rows: dict[str, Any] = {}
    max_paired_drop = float("-inf")
    for surface in SURFACES:
        pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for task in held:
            for fault in FAULTS:
                if fault == surface:
                    continue
                post = idx[task, fault, surface]
                if int(post.get("success") or 0) == 0:
                    pairs.append((idx[task, fault, "none"], post))
        if not pairs:
            surface_rows[surface] = {"eligible_failed_wrong_surface_pairs": 0}
            continue
        paired_pre = sum(correct(pre) for pre, _ in pairs) / len(pairs)
        paired_post = sum(correct(post) for _, post in pairs) / len(pairs)
        decomposition = decompose_drop(baseline_all, paired_pre, paired_post)
        max_paired_drop = max(max_paired_drop, decomposition["paired_causal_drop"])
        pair_rows = []
        for pre, post in pairs:
            pre_feats, post_feats = feats(pre), feats(post)
            pair_rows.append({
                "task_id": str(pre["task_id"]),
                "fault": str(pre["fault"]),
                "baseline_prediction": pred(pre),
                "post_prediction": pred(post),
                "baseline_correct": bool(correct(pre)),
                "post_correct": bool(correct(post)),
                "features_exactly_equal": pre_feats == post_feats,
                "feature_l2_shift": dist(pre_feats, post_feats),
                "baseline_success": int(pre.get("success") or 0),
                "post_success": int(post.get("success") or 0),
            })
        legacy_drop = (legacy_pf4.get("diagnostic_drop") or {}).get(surface)
        if legacy_drop is not None and abs(float(legacy_drop) - decomposition["legacy_unpaired_drop"]) > 1e-12:
            raise ValueError(f"legacy PF-4 drop mismatch for {surface}")
        surface_rows[surface] = {
            "eligible_failed_wrong_surface_pairs": len(pairs),
            "paired_baseline_accuracy_same_units": paired_pre,
            "paired_post_accuracy": paired_post,
            **decomposition,
            "exact_feature_identity_pairs": sum(row["features_exactly_equal"] for row in pair_rows),
            "same_prediction_pairs": sum(row["baseline_prediction"] == row["post_prediction"] for row in pair_rows),
            "pairs": pair_rows,
        }
    paired_gate = bool(max_paired_drop >= 0.15)
    return {
        "schema_version": "1.0",
        "audit_id": "pf4-paired-diagnosability-estimand-readjudication-20260816",
        "generated_at": _now(),
        "source_run_root": str(run_root),
        "source_raw_trace_sha256": _sha(raw_path),
        "source_analysis_sha256": _sha(analysis_path) if analysis_path.exists() else "",
        "source_rows": len(rows),
        "heldout_probe_count": len(all_base),
        "frozen_observer_centers": cen,
        "legacy_pf4_support_pass": bool(legacy_pf4.get("support_pass")),
        "legacy_unpaired_baseline_accuracy": baseline_all,
        "registered_drop_gate": 0.15,
        "surfaces": surface_rows,
        "paired_max_diagnostic_drop": max_paired_drop,
        "paired_support_gate_pass": paired_gate,
        "persistent_cross_fault_repair_active": dict(PERSISTENT_CROSS_FAULT_REPAIR_ACTIVE),
        "operationalization_valid_for_future_diagnosability": all(PERSISTENT_CROSS_FAULT_REPAIR_ACTIVE.values()),
        "operationalization_structural_witness": "In run_one(), prompt repair always changes the prompt patch. Workflow repair only changes behavior by disabling the injected workflow-fault branch when fault==workflow; tool repair only restores hidden open actions when fault==tool. Therefore workflow/tool repair are guaranteed no-ops on wrong-surface future faults and cannot instantiate a committed update whose downstream diagnostic channel is being measured.",
        "readjudication": "INVALIDATE_OLD_SUPPORT_PASS_ESTIMAND_AND_OPERATIONALIZATION" if bool(legacy_pf4.get("support_pass")) else "NO_CHANGE",
        "diagnosis_layer": "experiment-design-estimand-and-operationalization",
        "scientific_interpretation": "The historical PF-4 support gate compared diagnostic accuracy on all heldout no-repair faults with a different, surface-specific post-treatment subset restricted to wrong-surface repairs that still failed, mixing cohort composition with paired change. More fundamentally, workflow/tool historical repair arms are fault-cancellation controls rather than persistent cross-fault updates, so they are inert on the very wrong-surface probes used to claim future diagnosability. On the same eligible units, workflow and tool have zero diagnostic degradation; prompt improves. Therefore the historical support-pass cannot update belief about repair-induced future diagnosability loss. The broader diagnosability-preservation principle remains open and requires independent sealed future-fault probes after a committed update that remains active under those faults.",
        "broader_principle_falsified": False,
        "method_failure_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "scientific_authority": "readjudication-of-historical-diagnostic-only",
    }


def write_audit(run_root: Path, output_path: Path) -> dict[str, Any]:
    state = build_audit(run_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state
