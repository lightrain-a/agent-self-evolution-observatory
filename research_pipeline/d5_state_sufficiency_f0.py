from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from .p0_alfworld_adapter import ALFWorldGameRunner, HFAdmissiblePolicy, load_config
from .p0_mem_xfer_support_enriched import _token_matched_placebo

EXPERIMENT_ID = "D5-STATE-SUFFICIENCY-F0-v1"
SOURCE_FAMILY = "pick_heat_then_place_in_recep"
MEMORY_IDS = (
    "se-m-pick_heat_then_place_in_recep-1",
    "se-m-pick_heat_then_place_in_recep-2",
    "se-m-pick_heat_then_place_in_recep-3",
)
TARGET_FAMILIES = (
    "pick_and_place_simple",
    "pick_cool_then_place_in_recep",
    "pick_heat_then_place_in_recep",
)
TASKS_PER_FAMILY = 2
ARMS = ("no-memory", "placebo", "retrieved")


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _stable_hash(value: Any) -> str:
    return _sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _task_rel_id(path: str | Path) -> str:
    text = str(path).replace("\\", "/")
    marker = "json_2.1.1/valid_unseen/"
    if marker in text:
        return marker + text.split(marker, 1)[1]
    return text


def _family_from_task(path: str | Path) -> str:
    p = Path(_task_rel_id(path))
    name = p.parent.parent.name
    return name.split("-", 1)[0]


def historical_task_exposure(runs_root: Path, *, max_file_bytes: int = 32 << 20) -> set[str]:
    """Collect actually executed/source tasks, excluding mere plan-pool mentions.

    Only execution-bearing artifacts are eligible. A task that appeared in a plan but was
    never executed remains fresh for this prospective F0.
    """
    import re
    pattern = re.compile(r"json_2\.1\.1/valid_unseen/[^\"'\s,}]+/game\.tw-pddl")
    evidence_tokens = (
        "raw-trace", "raw_outcome", "raw-outcome", "stage-a-raw", "stage-b-raw",
        "stage_a_raw", "stage_b_raw", "main_table", "main-table", "outcomes",
        "source-memor", "action-replay",
    )
    exposed: set[str] = set()
    for path in runs_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".json", ".jsonl", ".csv"}:
            continue
        name = path.name.lower()
        if not any(token in name for token in evidence_tokens):
            continue
        try:
            if path.stat().st_size > max_file_bytes:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        exposed.update(match.group(0) for match in pattern.finditer(text))
    return exposed


def model_fingerprint(model_path: Path, *, full_weights: bool = False) -> dict[str, Any]:
    required = ("config.json", "model.safetensors.index.json", "tokenizer_config.json", "tokenizer.json")
    files: dict[str, Any] = {}
    for name in required:
        p = model_path / name
        if not p.is_file():
            raise FileNotFoundError(p)
        files[name] = {"size": p.stat().st_size, "sha256": _sha_file(p)}
    weights = sorted(model_path.glob("model-*-of-*.safetensors"))
    if not weights:
        raise FileNotFoundError(f"no sharded safetensors in {model_path}")
    files["weights"] = [
        {
            "name": p.name,
            "size": p.stat().st_size,
            **({"sha256": _sha_file(p)} if full_weights else {}),
        }
        for p in weights
    ]
    result = {"path": str(model_path), "files": files, "full_weight_hashes": bool(full_weights)}
    result["fingerprint_sha256"] = _stable_hash(files)
    return result


def _development_score_signature(main_rows: list[dict[str, str]], memory_id: str) -> tuple[tuple[Any, ...], ...]:
    rows = sorted(
        (r for r in main_rows if r["memory_id"] == memory_id and r["evaluation_role"] == "probe_development"),
        key=lambda r: (r["target_family"], _task_rel_id(r["target_task_id"])),
    )
    if len(rows) != 3:
        raise ValueError(f"{memory_id}: expected 3 development probes, found {len(rows)}")
    return tuple(
        (
            r["target_family"],
            _task_rel_id(r["target_task_id"]),
            int(r["retrieved_success"]),
            int(r["placebo_success"]),
            int(r["no_memory_success"]),
        )
        for r in rows
    )


def compile_contract(
    *,
    source_memories_path: Path,
    historical_main_table_path: Path,
    alfworld_root: Path,
    model_path: Path,
    config_path: Path,
    historical_runs_root: Path | None = None,
    full_weight_hashes: bool = False,
) -> dict[str, Any]:
    memories = {str(r["memory_id"]): r for r in _read_jsonl(source_memories_path)}
    missing = [m for m in MEMORY_IDS if m not in memories]
    if missing:
        raise ValueError(f"missing frozen memories: {missing}")
    if any(str(memories[m].get("source_family") or "") != SOURCE_FAMILY for m in MEMORY_IDS):
        raise ValueError("frozen memory source-family mismatch")

    with historical_main_table_path.open(newline="", encoding="utf-8") as f:
        main_rows = list(csv.DictReader(f))
    signatures = {m: _development_score_signature(main_rows, m) for m in MEMORY_IDS}
    panels = {m: tuple((row[0], row[1]) for row in sig) for m, sig in signatures.items()}
    if len(set(panels.values())) != 1:
        raise ValueError(f"frozen memories were not evaluated on one common development panel: {panels}")
    outcome_signatures = {m: tuple((row[0], row[2], row[3], row[4]) for row in sig) for m, sig in signatures.items()}
    if len(set(outcome_signatures.values())) != 1:
        raise ValueError(f"frozen memories are not score-equivalent on the common development panel: {outcome_signatures}")
    expected_signature = next(iter(outcome_signatures.values()))
    common_panel = next(iter(panels.values()))
    flat_outcomes = [value for row in expected_signature for value in row[-3:]]
    if all(value == 0 for value in flat_outcomes) or all(value == 1 for value in flat_outcomes):
        raise ValueError(f"common development signature is degenerate at a complete floor/ceiling: {expected_signature}")

    excluded = {_task_rel_id(r["target_task_id"]) for r in main_rows}
    excluded.update(_task_rel_id(str(row.get("source_task_id") or "")) for row in memories.values())
    global_exposed: set[str] = set()
    if historical_runs_root is not None:
        global_exposed = historical_task_exposure(historical_runs_root)
        excluded.update(global_exposed)
    task_root = alfworld_root / "json_2.1.1" / "valid_unseen"
    selected: list[dict[str, str]] = []
    for family in TARGET_FAMILIES:
        candidates = sorted(
            str(p)
            for p in task_root.glob(f"{family}-*/**/game.tw-pddl")
            if _task_rel_id(p) not in excluded
        )
        if len(candidates) < TASKS_PER_FAMILY:
            raise ValueError(f"insufficient fresh tasks for {family}: {len(candidates)}")
        for path in candidates[:TASKS_PER_FAMILY]:
            selected.append({
                "target_family": family,
                "task_path": path,
                "task_relpath": _task_rel_id(path),
            })

    mem_rows = []
    for m in MEMORY_IDS:
        row = memories[m]
        text = str(row.get("text") or "")
        mem_rows.append({
            "memory_id": m,
            "source_family": str(row.get("source_family") or ""),
            "source_task_id": str(row.get("source_task_id") or ""),
            "source_task_sha256": _sha_bytes(str(row.get("source_task_id") or "").encode()),
            "memory_text_sha256": _sha_bytes(text.encode()),
            "candidate_index": int(row.get("candidate_index") or 0),
            "candidate_role": str(row.get("candidate_role") or ""),
        })

    material = {
        "schema_version": "1.0",
        "experiment_id": EXPERIMENT_ID,
        "scientific_question": (
            "Are development-score-equivalent persistent memories future-effect equivalent on a common, disjoint task set?"
        ),
        "claim_boundary": (
            "This F0 tests sufficiency of a frozen current evaluation signature, not causal history effects after full internal-state equality."
        ),
        "source_family": SOURCE_FAMILY,
        "frozen_memory_ids": list(MEMORY_IDS),
        "development_equivalence": {
            "definition": "exact equality on one common ordered 3-probe panel of the (retrieved_success, placebo_success, no_memory_success) vector",
            "common_panel": [list(x) for x in common_panel],
            "signature": [list(x) for x in expected_signature],
            "nondegenerate_required": True,
            "selected_without_future_outcomes": True,
            "historical_evaluation_role": "probe_development",
        },
        "target_families": list(TARGET_FAMILIES),
        "tasks_per_family": TASKS_PER_FAMILY,
        "task_selection": {
            "rule": "lexicographically first valid_unseen game.tw-pddl after canonical-path exclusion of every known historical task exposure",
            "outcome_independent": True,
            "historical_runs_root": str(historical_runs_root) if historical_runs_root else "",
            "historical_exposed_task_count": len(global_exposed),
            "historical_exposure_sha256": _stable_hash(sorted(global_exposed)),
            "selected_tasks": selected,
        },
        "arms": list(ARMS),
        "arm_order": list(ARMS),
        "episodes": len(MEMORY_IDS) * len(selected) * len(ARMS),
        "max_steps": 50,
        "outcome_truth": "ALFWorld environment won/success; no LLM judge",
        "frozen_memories": mem_rows,
        "source_artifacts": {
            "source_memories": {"path": str(source_memories_path), "sha256": _sha_file(source_memories_path)},
            "historical_main_table": {"path": str(historical_main_table_path), "sha256": _sha_file(historical_main_table_path)},
            "historical_runs_exposure": {"root": str(historical_runs_root) if historical_runs_root else "", "task_count": len(global_exposed), "sha256": _stable_hash(sorted(global_exposed))},
            "alfworld_config": {"path": str(config_path), "sha256": _sha_file(config_path)},
        },
        "model": model_fingerprint(model_path, full_weights=full_weight_hashes),
        "analysis": {
            "unit_effect": "controlled_delta = retrieved_success - placebo_success",
            "future_divergent_task": "the three frozen memories do not all have identical controlled_delta on the same task",
            "go_min_divergent_tasks": 2,
            "go_min_divergent_target_families": 2,
            "go_requires_no_memory_reproducible": True,
            "go_requires_all_episodes_complete": True,
            "no_threshold_retuning_after_outcomes": True,
            "interpretation_if_go": "current 3-probe score equivalence is insufficient for future transfer equivalence; advance to prospective confirmation, not directly to a broad history-causality claim",
            "interpretation_if_stop": "this frozen F0 does not support a standalone state-sufficiency paper on the selected substrate",
        },
        "authority": {
            "canonical_problem_gate": False,
            "canonical_p0": False,
            "canonical_gpu": False,
            "isolated_user_requested_f0": True,
        },
    }
    contract = dict(material)
    contract["contract_sha256"] = _stable_hash(material)
    contract["created_at"] = _now()
    contract["scientific_authority"] = False
    return contract


def verify_contract(contract: dict[str, Any], *, model_path: Path, source_memories_path: Path) -> None:
    development = contract.get("development_equivalence") or {}
    if not development.get("common_panel") or development.get("nondegenerate_required") is not True:
        raise ValueError("legacy state-sufficiency contract lacks common-panel, nondegenerate qualification and is superseded")
    material = {k: v for k, v in contract.items() if k not in {"contract_sha256", "created_at", "scientific_authority"}}
    actual = _stable_hash(material)
    if actual != str(contract.get("contract_sha256") or ""):
        raise ValueError(f"contract hash mismatch: {actual} != {contract.get('contract_sha256')}")
    src = contract["source_artifacts"]["source_memories"]
    if _sha_file(source_memories_path) != src["sha256"]:
        raise ValueError("source-memory artifact changed after contract freeze")
    current = model_fingerprint(model_path, full_weights=bool(contract["model"].get("full_weight_hashes")))
    if current["fingerprint_sha256"] != contract["model"]["fingerprint_sha256"]:
        raise ValueError("model fingerprint changed after contract freeze")


def analyze_rows(rows: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    expected = len(MEMORY_IDS) * len(contract["task_selection"]["selected_tasks"]) * len(ARMS)
    keys = {(r["memory_id"], r["task_relpath"], r["arm"]) for r in rows}
    if len(rows) != expected or len(keys) != expected:
        return {
            "status": "INCOMPLETE",
            "complete_rows": len(rows),
            "expected_rows": expected,
            "scientific_authority": False,
        }
    by_unit: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_unit[(row["memory_id"], row["task_relpath"])][row["arm"]] = row
    task_effects: dict[str, dict[str, int]] = defaultdict(dict)
    no_memory_by_task: dict[str, list[tuple[int, tuple[str, ...]]]] = defaultdict(list)
    for (memory_id, task), arms in by_unit.items():
        if set(arms) != set(ARMS):
            raise ValueError(f"incomplete arms for {memory_id}/{task}")
        task_effects[task][memory_id] = int(arms["retrieved"]["success"]) - int(arms["placebo"]["success"])
        no_memory_by_task[task].append((int(arms["no-memory"]["success"]), tuple(arms["no-memory"].get("actions") or [])))
    no_memory_reproducible = all(len(set(vals)) == 1 for vals in no_memory_by_task.values())
    selected_map = {r["task_relpath"]: r["target_family"] for r in contract["task_selection"]["selected_tasks"]}
    divergent = []
    for task, values in sorted(task_effects.items()):
        v = [values[m] for m in MEMORY_IDS]
        if len(set(v)) > 1:
            divergent.append({"task_relpath": task, "target_family": selected_map[task], "controlled_deltas": dict(values)})
    divergent_families = sorted({r["target_family"] for r in divergent})
    rule = contract["analysis"]
    go = (
        no_memory_reproducible
        and len(divergent) >= int(rule["go_min_divergent_tasks"])
        and len(divergent_families) >= int(rule["go_min_divergent_target_families"])
    )
    return {
        "schema_version": "1.0",
        "experiment_id": EXPERIMENT_ID,
        "status": "COMPLETE",
        "contract_sha256": contract["contract_sha256"],
        "complete_rows": len(rows),
        "expected_rows": expected,
        "no_memory_reproducible": no_memory_reproducible,
        "divergent_tasks": divergent,
        "divergent_task_count": len(divergent),
        "divergent_target_families": divergent_families,
        "divergent_target_family_count": len(divergent_families),
        "decision": "GO_PROSPECTIVE_CONFIRMATION" if go else "STOP_CURRENT_STATE_SUFFICIENCY_PAPER",
        "claim_update": (
            "Development-score equivalence is insufficient for future transfer equivalence on this frozen F0; this is prospective-F0 support only."
            if go else
            "The frozen F0 does not establish a reusable future-effect divergence among development-score-equivalent memories."
        ),
        "paper_authorized": False,
        "scientific_authority": False,
    }


def run_contract(
    *,
    contract_path: Path,
    source_memories_path: Path,
    alfworld_config: Path,
    alfworld_root: Path,
    model_path: Path,
    output_dir: Path,
    device: str = "cuda",
) -> dict[str, Any]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    verify_contract(contract, model_path=model_path, source_memories_path=source_memories_path)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError(f"refusing to overwrite non-empty output dir {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    memories = {str(r["memory_id"]): r for r in _read_jsonl(source_memories_path)}
    os.environ["ALFWORLD_DATA"] = str(alfworld_root)
    runner = ALFWorldGameRunner(load_config(alfworld_config))
    policy = HFAdmissiblePolicy(model_path, device=device, policy_mode="react-family")
    placebo_cache: dict[str, str] = {}
    for memory_id in MEMORY_IDS:
        memory = str(memories[memory_id]["text"])
        placebo_cache[memory_id] = _token_matched_placebo(policy, memory)[0]
    raw_path = output_dir / "raw-traces.jsonl"
    started = time.monotonic()
    rows: list[dict[str, Any]] = []
    for task_index, task in enumerate(contract["task_selection"]["selected_tasks"], 1):
        task_path = Path(task["task_path"])
        if not task_path.exists():
            relocated = alfworld_root / task["task_relpath"]
            if not relocated.exists():
                raise FileNotFoundError(task_path)
            task_path = relocated
        for memory_id in MEMORY_IDS:
            memory = str(memories[memory_id]["text"])
            for arm in ARMS:
                patch = "" if arm == "no-memory" else "MEMORY::" + (memory if arm == "retrieved" else placebo_cache[memory_id])
                trace = runner.run_game_file("eval_out_of_distribution", str(task_path), policy, patch, max_steps=int(contract["max_steps"]))
                row = {
                    "schema_version": "1.0",
                    "experiment_id": EXPERIMENT_ID,
                    "contract_sha256": contract["contract_sha256"],
                    "task_index": task_index,
                    "task_relpath": task["task_relpath"],
                    "target_family": task["target_family"],
                    "memory_id": memory_id,
                    "arm": arm,
                    "success": int(trace.get("success") or 0),
                    "score": float(trace.get("score") or 0),
                    "steps": int(trace.get("steps") or 0),
                    "invalid_actions": int(trace.get("invalid_actions") or 0),
                    "actions": trace.get("actions") or [],
                    "model_calls": int(trace.get("model_calls") or 0),
                    "recorded_at": _now(),
                }
                rows.append(row)
                with raw_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                (output_dir / "progress.json").write_text(json.dumps({
                    "status": "RUNNING",
                    "contract_sha256": contract["contract_sha256"],
                    "completed_rows": len(rows),
                    "expected_rows": contract["episodes"],
                    "elapsed_hours": (time.monotonic() - started) / 3600,
                    "updated_at": _now(),
                }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    analysis = analyze_rows(rows, contract)
    (output_dir / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "manifest.json").write_text(json.dumps({
        "schema_version": "1.0",
        "experiment_id": EXPERIMENT_ID,
        "contract_path": str(contract_path),
        "contract_sha256": contract["contract_sha256"],
        "model": contract["model"],
        "source_memories_sha256": contract["source_artifacts"]["source_memories"]["sha256"],
        "raw_sha256": _sha_file(raw_path),
        "analysis_sha256": _sha_file(output_dir / "analysis.json"),
        "episodes": len(rows),
        "elapsed_hours": (time.monotonic() - started) / 3600,
        "scientific_authority": False,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return analysis


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("compile", "run", "analyze"))
    p.add_argument("--source-memories", type=Path, required=True)
    p.add_argument("--historical-main-table", type=Path)
    p.add_argument("--alfworld-root", type=Path, required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--historical-runs-root", type=Path)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--output-dir", type=Path)
    p.add_argument("--device", default="cuda")
    p.add_argument("--full-weight-hashes", action="store_true")
    args = p.parse_args()
    if args.phase == "compile":
        if args.historical_main_table is None:
            p.error("--historical-main-table required for compile")
        c = compile_contract(
            source_memories_path=args.source_memories,
            historical_main_table_path=args.historical_main_table,
            alfworld_root=args.alfworld_root,
            model_path=args.model,
            config_path=args.config,
            historical_runs_root=args.historical_runs_root,
            full_weight_hashes=args.full_weight_hashes,
        )
        args.contract.parent.mkdir(parents=True, exist_ok=True)
        args.contract.write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "FROZEN", "contract_sha256": c["contract_sha256"], "episodes": c["episodes"], "tasks": c["task_selection"]["selected_tasks"]}, ensure_ascii=False, indent=2))
    elif args.phase == "run":
        if args.output_dir is None:
            p.error("--output-dir required for run")
        result = run_contract(
            contract_path=args.contract,
            source_memories_path=args.source_memories,
            alfworld_config=args.config,
            alfworld_root=args.alfworld_root,
            model_path=args.model,
            output_dir=args.output_dir,
            device=args.device,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.output_dir is None:
            p.error("--output-dir required for analyze")
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        rows = _read_jsonl(args.output_dir / "raw-traces.jsonl")
        result = analyze_rows(rows, contract)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
