#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def terminal_record(adjudication: dict[str, Any], *, adjudication_path: Path, adjudication_sha: str) -> tuple[str, dict[str, Any]]:
    status = str(adjudication.get("status") or "")
    evidence = {"path": str(adjudication_path), "sha256": adjudication_sha}
    if status == "PASS_NEGATIVE_CONTROL_EQUIVALENCE_READY_FOR_MRW_CONTRACT":
        return "success", {
            "success_id": "R17-S004-E1B-NC-EQUIVALENCE",
            "stage": "E1-B identical-treatment WIN-A/WIN-B full negative control",
            "status": status,
            "evidence": evidence,
            "scientific_endpoint_reached": True,
            "central_mechanism_adjudicated": False,
            "lesson": (
                "Under the preregistered 12-pair stream-level TOST margin of 1/18, byte-identical WIN-A/WIN-B "
                "hosted updater+evaluator treatments are practically equivalent. This qualifies the nuisance floor "
                "for a separately authorized MRW same-pool causal experiment; it is not evidence that MRW is effective."
            ),
            "authority_after_success": {
                "prepare_mrw_contract": True,
                "execute_mrw": False,
                "paper_promotion": False,
            },
        }
    if status == "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY":
        return "failure", {
            "failure_id": "R17-F012-E1B-NC-NONEQUIVALENCE",
            "stage": "E1-B identical-treatment WIN-A/WIN-B full negative control",
            "terminal_status": status,
            "classification": ["SCIENTIFIC_IDENTIFIABILITY"],
            "scientific_endpoint_reached": True,
            "scientific_data_observed_for_effectiveness": False,
            "contamination": "NONE; protocol-valid nuisance-control endpoint.",
            "provider_calls": "as recorded by the frozen run summary/adjudication",
            "root_cause": (
                "Preregistered identical-treatment WIN-A/WIN-B variability was not demonstrated practically equivalent "
                "within the fixed 1/18 stream-success margin. This may reflect hosted updater and/or evaluator stochasticity; "
                "the negative control does not identify which component dominates."
            ),
            "scientific_belief_update": (
                "The sign/value of the central Search-Projection mechanism remains UNKNOWN. The current hosted stack is "
                "not qualified for MRW causal interpretation under the frozen nuisance-control criterion."
            ),
            "repair_or_stop": (
                "HOLD MRW. Do not rerun, widen the equivalence margin, change probes/model, or average favorable subsets under "
                "the current protocol. A future redesign is scientifically permissible only as a new nuisance-control protocol "
                "with an independently justified measurement/stochasticity intervention, not as a rescue of this result."
            ),
            "rerun_policy": "NO_AUTOMATIC_RERUN_OR_MARGIN_RELAXATION; NEW_PROTOCOL_REQUIRED_FOR_ANY_FUTURE_IDENTIFIABILITY_ATTEMPT",
            "reusable_rule": (
                "A protocol-valid negative control that fails equivalence is a scientific identifiability result. It cannot be "
                "laundered into an implementation failure merely because it blocks the desired causal experiment."
            ),
            "preserved_artifacts": [evidence],
        }
    raise RuntimeError(f"unsupported negative-control adjudication status: {status}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    adjudication = json.loads(args.adjudication.read_text(encoding="utf-8"))
    require(registry.get("artifact_type") == "e2-r17-failure-differential-registry", "unexpected registry type")
    require(adjudication.get("artifact_type") == "e2-r17-e1-b-negative-control-adjudication", "unexpected adjudication type")
    require(adjudication.get("central_mechanism_adjudicated") is False, "negative control must not adjudicate central mechanism")

    kind, record = terminal_record(adjudication, adjudication_path=args.adjudication, adjudication_sha=sha_file(args.adjudication))
    out = copy.deepcopy(registry)
    out["schema_version"] = "1.5"
    out["date"] = datetime.now(timezone.utc).date().isoformat()
    out["supersedes"] = {"path": str(args.registry), "sha256": sha_file(args.registry)}
    state = out.setdefault("current_scientific_state", {})
    if kind == "success":
        existing = {row.get("success_id") for row in out.setdefault("qualified_successes", [])}
        if record["success_id"] not in existing:
            out["qualified_successes"].append(record)
        state["e1_b_negative_control"] = "PASS_EQUIVALENCE_READY_FOR_SEPARATE_MRW_CONTRACT"
        state["e1_b_mrw_causal_effect"] = "UNKNOWN_MRW_CONTRACT_PREPARATION_ALLOWED_EXECUTION_UNAUTHORIZED"
    else:
        existing = {row.get("failure_id") for row in out.setdefault("entries", [])}
        if record["failure_id"] not in existing:
            out["entries"].append(record)
        state["e1_b_negative_control"] = "HOLD_IDENTIFIABILITY_HOSTED_STOCHASTICITY_NOT_EQUIVALENT"
        state["e1_b_mrw_causal_effect"] = "UNKNOWN_AND_BLOCKED_BY_NEGATIVE_CONTROL"
    state["central_mechanism"] = "OPEN_NOT_YET_ADJUDICATED"
    out["status"] = "ACTIVE_CANONICAL_FAILURE_LEDGER_FOR_R17_WORKTREE"
    atomic_json(args.output, out)
    print(json.dumps({
        "status": "REGISTERED",
        "kind": kind,
        "record_id": record.get("success_id") or record.get("failure_id"),
        "output": str(args.output),
        "output_sha256": sha_file(args.output),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
