from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research_pipeline import temporal_skill_g0_execute as core
from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings
from research_pipeline.experiment_authority import acquire_authority, release_authority
from research_pipeline.temporal_skill_retrieval_surface import materialize_retrieval_surface, parity_receipt

PAPER_ID = core.PAPER_ID
DATA_ROOT = core.DATA_ROOT
OWNER_ID = PAPER_ID + ":TEMP-O5-DEEPSEEK-T-R"
PLAN = PROJECT_ROOT / "generated/temporal-skill-temp-o5-deepseek-plan-20260824.json"
STAGE = PROJECT_ROOT / "generated/temporal-skill-temp-o5-deepseek-stage-contract-20260824.json"
PREFLIGHT = PROJECT_ROOT / "generated/temporal-skill-temp-o5-deepseek-preflight-20260824.json"
AUTH = PROJECT_ROOT / "generated/temporal-skill-temp-o5-deepseek-human-authorization-20260824.json"
OUTPUT = core.REPLAY_ROOT / "20260824-temp-o5-deepseek-t-vs-r" / "results.json"
RETRIEVAL_SURFACE = PROJECT_ROOT / "research_pipeline/temporal_skill_retrieval_surface.py"
ANALYZER = PROJECT_ROOT / "research_pipeline/temporal_skill_temp_o5_analyze.py"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_auth(auth: dict[str, Any], plan: dict[str, Any], stage: dict[str, Any], preflight: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    checks = [
        (auth.get("status") == "HUMAN_EXECUTION_AUTHORITY_RECORDED", "status"),
        (bool(auth.get("scientific_reopen_authorized")), "scientific-reopen"),
        (bool(auth.get("execution_authorized")), "execution"),
        (bool(auth.get("provider_spend_authorized")), "provider-spend"),
        (auth.get("bound_plan_body_sha256") == plan["plan_body_sha256"], "plan-hash"),
        (auth.get("bound_stage_contract_sha256") == stage["stage_contract_sha256"], "stage-hash"),
        (auth.get("bound_preflight_sha256") == preflight["receipt_sha256"], "preflight-hash"),
        (auth.get("bound_executor_sha256") == sha_file(Path(__file__)), "executor-hash"),
        (auth.get("bound_retrieval_surface_sha256") == sha_file(RETRIEVAL_SURFACE), "retrieval-surface-hash"),
        (auth.get("bound_analyzer_sha256") == sha_file(ANALYZER), "analyzer-hash"),
        (auth.get("bound_core_runner_sha256") == sha_file(Path(core.__file__)), "core-runner-hash"),
        (not bool(auth.get("outcome_driven_stopping_authorized")), "outcome-stopping"),
        (bool((auth.get("bounded_budget") or {}).get("resume_missing_only")), "resume-missing-only"),
        (not bool((auth.get("bounded_budget") or {}).get("reruns_allowed")), "reruns-forbidden"),
        (int((auth.get("bounded_budget") or {}).get("model_calls_upper_bound") or -1) == len(plan["rows"]), "budget"),
        (bool(preflight.get("zero_call_parity", {}).get("pass")), "zero-call-parity"),
        (int(preflight.get("zero_call_parity", {}).get("passed") or 0) == 18, "zero-call-parity-count"),
    ]
    for ok, name in checks:
        if not ok:
            errors.append(name)
    supplied = auth.get("authorization_sha256")
    if supplied:
        body = {k: v for k, v in auth.items() if k != "authorization_sha256"}
        if supplied != core.canonical_sha(body):
            errors.append("self-hash")
    return errors


def surface_prompt(assets: dict[str, Any], endpoint: dict[str, Any], arm: str) -> tuple[str, dict[str, Any], dict[str, Any]]:
    operation_output, operation_sha = core.helper_output(assets, endpoint, "T_FROZEN")
    if operation_output is None or operation_sha is None:
        raise RuntimeError("targeted operation output missing")
    if arm == "T_CALLABLE":
        prompt = core.render_prompt(assets, endpoint, operation_output)
        receipt = {
            "integration_surface": "callable_skill_output",
            "operation_output": operation_output,
            "operation_source_sha256": operation_sha,
            "retrieval_parity": None,
        }
        return prompt, operation_output, receipt
    if arm != "R_RETRIEVAL":
        raise ValueError(f"unknown TEMP-O5 arm {arm}")
    retrieval_endpoint = materialize_retrieval_surface(endpoint, operation_output)
    parity = parity_receipt(endpoint, operation_output, retrieval_endpoint)
    if not (parity["candidate_evidence_preserved"] and parity["operation_output_content_equal"] and parity["only_added_field"]):
        raise RuntimeError("operation/retrieval parity failed before model call")
    prompt = core.render_prompt(assets, retrieval_endpoint, None)
    receipt = {
        "integration_surface": "retrieved_context_materialization",
        "operation_output": operation_output,
        "operation_source_sha256": operation_sha,
        "retrieval_parity": parity,
    }
    return prompt, operation_output, receipt


def run_one(client: ArkResponsesClient, assets: dict[str, Any], plan_row: dict[str, Any]) -> dict[str, Any]:
    endpoint = assets["endpoints"][str(plan_row["endpoint_id"])]
    prompt, operation_output, surface = surface_prompt(assets, endpoint, str(plan_row["arm"]))
    base = {
        **plan_row,
        "unit_key": core.row_key(plan_row),
        "runtime_valid": False,
        "family_success": False,
        "generation_post_attempts": 1,
        "get_recovery_attempts": 0,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        **surface,
    }
    started = time.time()
    try:
        response = client.respond(
            prompt,
            model=str(plan_row["requested_model"]),
            max_output_tokens=core.MAX_OUTPUT_TOKENS,
            temperature=0,
            thinking="disabled",
            allow_thinking_compatibility_fallback=False,
        )
        text = str(response.get("text") or "")
        recovered = False
    except ArkResponseStateError as exc:
        if not exc.response_id:
            return {**base, "failure_kind": "provider-response-state-no-id", "error": str(exc), "runtime_seconds": round(time.time() - started, 3)}
        polled = client.poll_response(exc.response_id, max_polls=core.POLL_MAX, interval_seconds=core.POLL_INTERVAL_SECONDS)
        text = str(polled.get("text") or "")
        recovered = True
        base["get_recovery_attempts"] = int(polled.get("poll_count") or 0)
        response = {
            "response_id": polled.get("response_id") or exc.response_id,
            "status": polled.get("status"),
            "resolved_model": polled.get("resolved_model") or exc.resolved_model,
            "usage": polled.get("usage") or {},
        }
        if not text:
            return {**base, "resolved_model": str(response.get("resolved_model") or ""), "failure_kind": "provider-get-recovery-no-text", "error": str(exc), "runtime_seconds": round(time.time() - started, 3)}
    except Exception as exc:
        return {**base, "failure_kind": "provider-post-failure", "error_type": type(exc).__name__, "error": str(exc)[:1200], "runtime_seconds": round(time.time() - started, 3)}
    resolved = str(response.get("resolved_model") or "")
    response_id = str(response.get("response_id") or "")
    common = {
        **base,
        "resolved_model": resolved,
        "provider_response_id_sha256": hashlib.sha256(response_id.encode()).hexdigest(),
        "provider_status": response.get("status"),
        "usage": response.get("usage") or {},
        "raw_text": text,
        "raw_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "get_recovered": recovered,
        "runtime_seconds": round(time.time() - started, 3),
    }
    if resolved != str(plan_row["required_resolved_model"]):
        return {**common, "failure_kind": "resolved-model-drift"}
    try:
        prediction, score = core.parse_and_score(assets, endpoint, text)
    except Exception as exc:
        return {**common, "failure_kind": "protocol-parse-or-score-failure", "error_type": type(exc).__name__, "error": str(exc)[:1200]}
    return {
        **common,
        "prediction": prediction,
        "family_score": score,
        "family_success": bool(score["success"]),
        "runtime_valid": True,
    }


def progress(output: Path, plan: dict[str, Any], stage_name: str, status: str, note: str = "") -> dict[str, Any]:
    rows = core.load_csv_rows(output.parent / "results.csv")
    payload = {
        "schema_version": "1.0", "paper_id": PAPER_ID, "plan_body_sha256": plan["plan_body_sha256"],
        "stage": stage_name, "status": status, "checkpoint_rows": len(rows), "planned_rows": len(plan["rows"]),
        "remaining_rows": len(plan["rows"]) - len(rows), "note": note,
        "results_csv": str(output.parent / "results.csv"), "results_jsonl": str(output.parent / "results.jsonl"),
        "raw_dir": str(output.parent / "raw"),
    }
    core.atomic_json(output.parent / "checkpoint.json", payload)
    return payload


def pilot_gate(output: Path, stage: dict[str, Any]) -> dict[str, Any]:
    rows = core.load_csv_rows(output.parent / "results.csv")
    required = stage["pilot"]["row_keys"]
    missing = [k for k in required if k not in rows]
    invalid = [k for k in required if k in rows and rows[k].get("runtime_valid") != "True"]
    drift = [k for k in required if k in rows and rows[k].get("resolved_model") != rows[k].get("required_resolved_model")]
    raw_missing = [k for k in required if k in rows and not Path(rows[k].get("raw_receipt_path") or "").exists()]
    raw_parity_failure = []
    for key in required:
        if key not in rows:
            continue
        raw_path = Path(rows[key].get("raw_receipt_path") or "")
        if raw_path.exists():
            raw = read_json(raw_path)
            if raw.get("arm") == "R_RETRIEVAL":
                p = raw.get("retrieval_parity") or {}
                if not (p.get("candidate_evidence_preserved") and p.get("operation_output_content_equal") and p.get("only_added_field")):
                    raw_parity_failure.append(key)
    result = {
        "schema_version": "1.0", "gate": "TEMP-O5-DEEPSEEK-PILOT-RUNTIME-PARITY",
        "pass": not (missing or invalid or drift or raw_missing or raw_parity_failure), "pilot_calls": len(required),
        "missing": missing, "runtime_invalid": invalid, "model_drift": drift, "raw_missing": raw_missing,
        "retrieval_parity_failure": raw_parity_failure, "scientific_outcomes_inspected_for_promotion": False,
    }
    core.atomic_json(output.parent / "pilot-gate.json", result)
    return result


def build_results(output: Path, plan: dict[str, Any], auth: dict[str, Any], assets: dict[str, Any]) -> dict[str, Any]:
    raw_by_key = {}
    for path in (output.parent / "raw").glob("*.json"):
        row = read_json(path)
        raw_by_key[core.row_key(row)] = row
    ordered = [raw_by_key[core.row_key(r)] for r in plan["rows"] if core.row_key(r) in raw_by_key]
    result = {
        "schema_version": "1.0", "paper_id": PAPER_ID, "run_id": "TEMP-O5-DEEPSEEK-T-VS-R-20260824",
        "plan_body_sha256": plan["plan_body_sha256"], "authorization_sha256": auth["authorization_sha256"],
        "executor_sha256": sha_file(Path(__file__)), "retrieval_surface_sha256": sha_file(RETRIEVAL_SURFACE),
        "asset_hashes": assets["hashes"], "rows": ordered, "rows_total": len(ordered),
        "runtime_valid_rows": sum(bool(r.get("runtime_valid")) for r in ordered),
        "status": "completed" if len(ordered) == len(plan["rows"]) else "partial",
    }
    result["scientific_result_available"] = result["status"] == "completed" and result["runtime_valid_rows"] == len(ordered)
    result["result_body_sha256"] = core.canonical_sha({k: v for k, v in result.items() if k != "result_body_sha256"})
    core.atomic_json(output, result)
    return result


def execute(stage_name: str) -> dict[str, Any]:
    plan = read_json(PLAN); stage = read_json(STAGE); preflight = read_json(PREFLIGHT); auth = read_json(AUTH)
    errors = validate_auth(auth, plan, stage, preflight)
    if errors:
        raise RuntimeError("authorization invalid: " + ",".join(errors))
    assets = core.load_assets()
    if set(plan["endpoint_selection"]["endpoints"]) != {r["endpoint_id"] for r in plan["rows"]}:
        raise RuntimeError("plan endpoint selection mismatch")
    core.recover_orphan_raw(OUTPUT, plan)
    existing = core.load_csv_rows(OUTPUT.parent / "results.csv")
    bad = [k for k, r in existing.items() if r.get("runtime_valid") != "True"]
    if bad:
        raise RuntimeError("runtime-invalid checkpoint requires adjudication: " + bad[0])
    if stage_name == "full":
        gate_path = OUTPUT.parent / "pilot-gate.json"
        if not gate_path.exists() or not read_json(gate_path).get("pass"):
            raise RuntimeError("pilot gate not passed")
        target = {core.row_key(r) for r in plan["rows"]}
    else:
        target = set(stage["pilot"]["row_keys"])
    raw_settings = ArkSettings.from_env(required=True)
    if raw_settings.base_url.rstrip("/") != plan["model_identity"]["required_plan_base_url"].rstrip("/"):
        raise RuntimeError("not on frozen Ark Plan route")
    client = ArkResponsesClient(ArkSettings(api_key=raw_settings.api_key, base_url=raw_settings.base_url, default_model=raw_settings.default_model, timeout_seconds=180.0, max_retries=0))
    run_id = f"TEMP-O5-DEEPSEEK-{stage_name.upper()}-20260824"
    authority = acquire_authority(DATA_ROOT, OWNER_ID, plan["plan_body_sha256"], "temporal-skill-temp-o5-executor", f"TEMP-O5-{stage_name}", run_id)
    outcome = "runner-exception"
    try:
        progress(OUTPUT, plan, stage_name, "running")
        index = {core.row_key(r): i for i, r in enumerate(plan["rows"])}
        for plan_row in plan["rows"]:
            key = core.row_key(plan_row)
            if key not in target or key in core.load_csv_rows(OUTPUT.parent / "results.csv"):
                continue
            row = run_one(client, assets, plan_row)
            core.persist_checkpoint(OUTPUT, row, index[key])
            progress(OUTPUT, plan, stage_name, "running", "last=" + key)
            if not row.get("runtime_valid"):
                outcome = row.get("failure_kind") or "runtime-invalid"
                progress(OUTPUT, plan, stage_name, "stopped", str(outcome))
                return {"status": "stopped", "reason": outcome, "unit_key": key}
        if stage_name == "pilot":
            gate = pilot_gate(OUTPUT, stage); outcome = "pilot-pass" if gate["pass"] else "pilot-fail"
            progress(OUTPUT, plan, stage_name, outcome)
            return {"status": outcome, "pilot_gate": gate}
        result = build_results(OUTPUT, plan, auth, assets); outcome = "completed" if result["scientific_result_available"] else "partial"
        progress(OUTPUT, plan, stage_name, outcome)
        return {"status": outcome, "rows_total": result["rows_total"], "output": str(OUTPUT)}
    finally:
        release_authority(DATA_ROOT, OWNER_ID, authority["authority_id"], str(outcome))


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", choices=["pilot", "full"], default="pilot"); ap.add_argument("--validate-only", action="store_true"); args = ap.parse_args()
    plan = read_json(PLAN); stage = read_json(STAGE); preflight = read_json(PREFLIGHT); auth = read_json(AUTH) if AUTH.exists() else {}
    if args.validate_only:
        print(json.dumps({"plan_sha": plan["plan_body_sha256"], "stage_sha": stage["stage_contract_sha256"], "preflight_sha": preflight["receipt_sha256"], "executor_sha": sha_file(Path(__file__)), "retrieval_surface_sha": sha_file(RETRIEVAL_SURFACE), "authorization_errors": validate_auth(auth, plan, stage, preflight) if auth else ["missing-auth"], "checkpoint_rows": len(core.load_csv_rows(OUTPUT.parent / "results.csv"))}, indent=2)); return
    print(json.dumps(execute(args.stage), ensure_ascii=False, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
