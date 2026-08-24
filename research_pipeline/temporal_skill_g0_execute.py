from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings
from research_pipeline.experiment_authority import acquire_authority, release_authority

PAPER_ID = "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK"
OWNER_ID = PAPER_ID + ":TEMP-O4-STAGE-A-DEEPSEEK"
DATA_ROOT = Path("/data/wyt/agent-self-evolution-observatory")
REPLAY_ROOT = DATA_ROOT / "paper-acceptance" / "source-native-replay" / PAPER_ID
R3 = REPLAY_ROOT / "20260822-r3"
R4 = REPLAY_ROOT / "20260822-r4-postreview-eia"
DEFAULT_PLAN = PROJECT_ROOT / "generated" / "temporal-skill-g0-fresh-factorial-plan-20260824.json"
DEFAULT_PREFLIGHT = PROJECT_ROOT / "generated" / "temporal-skill-g0-reopen-preflight-20260824.json"
DEFAULT_AUTHORIZATION = PROJECT_ROOT / "generated" / "temporal-skill-g0-human-authorization-20260824.json"
ANALYZER_PATH = PROJECT_ROOT / "research_pipeline" / "temporal_skill_g0_analyze.py"
DEFAULT_OUTPUT = REPLAY_ROOT / "20260824-g0-stage-a-deepseek" / "results.json"

MAX_OUTPUT_TOKENS = 768
POLL_MAX = 3
POLL_INTERVAL_SECONDS = 1.0
G0_SOURCE = "def skill(package, context):\n    return {}\n"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha_bytes(raw)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_assets() -> dict[str, Any]:
    r3_raw = read_json(R3 / "endpoints.json")
    r3_rows = r3_raw.get("endpoints", r3_raw) if isinstance(r3_raw, dict) else r3_raw
    r4_raw = read_json(R4 / "endpoints.json")
    r4_rows = r4_raw.get("endpoints", r4_raw) if isinstance(r4_raw, dict) else r4_raw
    endpoints: dict[str, dict[str, Any]] = {}
    source: dict[str, str] = {}
    for row in r3_rows:
        endpoints[str(row["endpoint_id"])] = row
        source[str(row["endpoint_id"])] = "R3"
    for row in r4_rows:
        endpoints[str(row["endpoint_id"])] = row
        source[str(row["endpoint_id"])] = "R4"

    r3_harness = load_module(R3 / "harness.py", "temporal_g0_r3_harness")
    r3_scorer = load_module(R3 / "scorer.py", "temporal_g0_r3_scorer")
    r4_harness = load_module(R4 / "harness.py", "temporal_g0_r4_harness")
    r4_scorer = load_module(R4 / "scorer.py", "temporal_g0_r4_scorer")
    targeted = {
        ("R3", "temporal_cutoff"): (R3 / "skills/targeted/T1_temporal_cutoff.py", "temporal_g0_t1_r3"),
        ("R3", "release_alignment"): (R3 / "skills/targeted/T2_release_alignment.py", "temporal_g0_t2_r3"),
        ("R3", "exogenous_grounding"): (R3 / "skills/targeted/T3_exogenous_grounding.py", "temporal_g0_t3_r3"),
        ("R4", "temporal_cutoff"): (R4 / "skills/targeted/T1_temporal_cutoff.py", "temporal_g0_t1_r4"),
    }
    targeted_modules: dict[tuple[str, str], Any] = {}
    targeted_hashes: dict[str, str] = {}
    for key, (path, name) in targeted.items():
        targeted_modules[key] = load_module(path, name)
        targeted_hashes[f"{key[0]}:{key[1]}"] = sha_file(path)

    return {
        "endpoints": endpoints,
        "source": source,
        "r3_harness": r3_harness,
        "r3_scorer": r3_scorer,
        "r4_harness": r4_harness,
        "r4_scorer": r4_scorer,
        "targeted_modules": targeted_modules,
        "hashes": {
            "r3_endpoints": sha_file(R3 / "endpoints.json"),
            "r4_endpoints": sha_file(R4 / "endpoints.json"),
            "r3_harness": sha_file(R3 / "harness.py"),
            "r3_scorer": sha_file(R3 / "scorer.py"),
            "r4_harness": sha_file(R4 / "harness.py"),
            "r4_scorer": sha_file(R4 / "scorer.py"),
            "targeted": targeted_hashes,
            "g0_source": sha_bytes(G0_SOURCE.encode("utf-8")),
        },
    }


def validate_authorization(auth: dict[str, Any], plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_scope = {
        "TEMP-O4_STAGE_A_DEEPSEEK_PRIMARY",
        "G0_NOOP_BEHAVIOR_NEUTRALITY",
        "FRESH_N_T_REPLICATION_FOR_SAME_UNITS",
    }
    if auth.get("status") != "HUMAN_EXECUTION_AUTHORITY_RECORDED":
        errors.append("human-authorization-status-missing")
    if not bool(auth.get("scientific_reopen_authorized")):
        errors.append("scientific-reopen-not-authorized")
    if not bool(auth.get("execution_authorized")):
        errors.append("execution-not-authorized")
    if not bool(auth.get("provider_spend_authorized")):
        errors.append("provider-spend-not-authorized")
    if str(auth.get("bound_plan_body_sha256") or "") != str(plan["plan_body_sha256"]):
        errors.append("authorization-plan-hash-mismatch")
    if not required_scope.issubset(set(auth.get("scope") or [])):
        errors.append("authorization-scope-incomplete")
    budget = auth.get("bounded_budget") or {}
    if int(budget.get("model_calls_upper_bound") or -1) != int(plan["summary"]["planned_model_calls"]):
        errors.append("authorization-call-budget-mismatch")
    if bool(budget.get("reruns_allowed")):
        errors.append("reruns-must-be-forbidden")
    if bool(auth.get("outcome_driven_selection_authorized")):
        errors.append("outcome-driven-selection-must-be-forbidden")
    model = auth.get("model_identity") or {}
    if str(model.get("requested_model") or "") != str(plan["model_identity"]["requested_model"]):
        errors.append("authorization-requested-model-mismatch")
    if str(model.get("required_resolved_model") or "") != str(plan["model_identity"]["required_resolved_model"]):
        errors.append("authorization-resolved-model-mismatch")
    if not bool(auth.get("ark_plan_target_confirmed_and_propagated")):
        errors.append("ark-plan-target-not-confirmed")
    if str(auth.get("ark_plan_target_model") or "") != str(plan["model_identity"]["required_plan_target_model"]):
        errors.append("ark-plan-target-model-mismatch")
    if str(auth.get("ark_plan_base_url") or "") != str(plan["model_identity"]["required_plan_base_url"]):
        errors.append("ark-plan-base-url-mismatch")
    if str(auth.get("bound_runner_sha256") or "") != sha_file(Path(__file__)):
        errors.append("authorization-runner-hash-mismatch")
    if str(auth.get("bound_analyzer_sha256") or "") != sha_file(ANALYZER_PATH):
        errors.append("authorization-analyzer-hash-mismatch")
    supplied_sha = str(auth.get("authorization_sha256") or "")
    if supplied_sha:
        body = {k: v for k, v in auth.items() if k != "authorization_sha256"}
        if supplied_sha != canonical_sha(body):
            errors.append("authorization-self-hash-mismatch")
    return errors


def helper_output(assets: dict[str, Any], endpoint: dict[str, Any], arm: str) -> tuple[dict[str, Any] | None, str | None]:
    if arm == "N_FRESH":
        return None, None
    if arm == "G0_NOOP":
        return {}, sha_bytes(G0_SOURCE.encode("utf-8"))
    eid = str(endpoint["endpoint_id"])
    source = assets["source"][eid]
    family = str(endpoint["failure_family"])
    module = assets["targeted_modules"][(source, family)]
    output = module.skill(endpoint["package"], endpoint.get("skill_context") or {})
    return output, assets["hashes"]["targeted"][f"{source}:{family}"]


def render_prompt(assets: dict[str, Any], endpoint: dict[str, Any], helper: dict[str, Any] | None) -> str:
    source = assets["source"][str(endpoint["endpoint_id"])]
    harness = assets["r3_harness"] if source == "R3" else assets["r4_harness"]
    return harness.render_prompt(endpoint, helper)


def parse_and_score(assets: dict[str, Any], endpoint: dict[str, Any], text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    source = assets["source"][str(endpoint["endpoint_id"])]
    harness = assets["r3_harness"] if source == "R3" else assets["r4_harness"]
    prediction = harness.extract_json(text)
    if source == "R3":
        score = assets["r3_scorer"].score(endpoint, prediction)
    else:
        score = assets["r4_scorer"].family_score(endpoint, prediction)
    return prediction, score


def run_one(client: ArkResponsesClient, assets: dict[str, Any], plan_row: dict[str, Any]) -> dict[str, Any]:
    endpoint = assets["endpoints"][str(plan_row["endpoint_id"])]
    helper, helper_sha = helper_output(assets, endpoint, str(plan_row["arm"]))
    prompt = render_prompt(assets, endpoint, helper)
    base = {
        **plan_row,
        "helper_output": helper,
        "helper_source_sha256": helper_sha,
        "prompt_sha256": sha_bytes(prompt.encode("utf-8")),
        "runtime_valid": False,
        "family_success": False,
        "generation_post_attempts": 1,
        "get_recovery_attempts": 0,
    }
    started = time.time()
    try:
        response = client.respond(
            prompt,
            model=str(plan_row["requested_model"]),
            max_output_tokens=MAX_OUTPUT_TOKENS,
            temperature=0,
            thinking="disabled",
            allow_thinking_compatibility_fallback=False,
        )
        text = str(response.get("text") or "")
        recovered = False
    except ArkResponseStateError as exc:
        if not exc.response_id:
            return {**base, "failure_kind": "provider-response-state-no-id", "error": str(exc), "runtime_seconds": round(time.time() - started, 3)}
        polled = client.poll_response(exc.response_id, max_polls=POLL_MAX, interval_seconds=POLL_INTERVAL_SECONDS)
        text = str(polled.get("text") or "")
        response = {
            "response_id": polled.get("response_id") or exc.response_id,
            "status": polled.get("status"),
            "resolved_model": polled.get("resolved_model") or exc.resolved_model,
            "usage": polled.get("usage") or {},
        }
        base["get_recovery_attempts"] = int(polled.get("poll_count") or 0)
        recovered = True
        if not text:
            return {
                **base,
                "provider_response_id_sha256": sha_bytes(str(response.get("response_id") or "").encode("utf-8")),
                "resolved_model": str(response.get("resolved_model") or ""),
                "failure_kind": "provider-get-recovery-no-text",
                "error": str(exc),
                "runtime_seconds": round(time.time() - started, 3),
            }
    except Exception as exc:
        return {**base, "failure_kind": "provider-post-failure", "error_type": type(exc).__name__, "error": str(exc)[:1200], "runtime_seconds": round(time.time() - started, 3)}

    resolved = str(response.get("resolved_model") or "")
    response_id = str(response.get("response_id") or "")
    raw_sha = sha_bytes(text.encode("utf-8"))
    common = {
        **base,
        "resolved_model": resolved,
        "provider_response_id_sha256": sha_bytes(response_id.encode("utf-8")),
        "provider_status": response.get("status"),
        "usage": response.get("usage") or {},
        "raw_text": text,
        "raw_text_sha256": raw_sha,
        "get_recovered": recovered,
        "runtime_seconds": round(time.time() - started, 3),
    }
    if resolved != str(plan_row["required_resolved_model"]):
        return {**common, "failure_kind": "resolved-model-drift"}
    try:
        prediction, score = parse_and_score(assets, endpoint, text)
    except Exception as exc:
        return {**common, "failure_kind": "protocol-parse-or-score-failure", "error_type": type(exc).__name__, "error": str(exc)[:1200]}
    return {
        **common,
        "prediction": prediction,
        "family_score": score,
        "family_success": bool(score["success"]),
        "runtime_valid": True,
    }


def build_initial_payload(plan: dict[str, Any], preflight: dict[str, Any], auth: dict[str, Any], assets: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "run_id": "TEMP-O4-G0-STAGE-A-DEEPSEEK-20260824",
        "plan_body_sha256": plan["plan_body_sha256"],
        "preflight_receipt_body_sha256": preflight["receipt_body_sha256"],
        "authorization_sha256": auth.get("authorization_sha256") or canonical_sha(auth),
        "runner_sha256": sha_file(Path(__file__)),
        "asset_hashes": assets["hashes"],
        "model_identity": plan["model_identity"],
        "provider_policy": {
            "generation_post_attempts_per_planned_unit": 1,
            "ark_client_max_retries": 0,
            "thinking_compatibility_repost": False,
            "existing_response_get_recovery_only": True,
            "poll_max": POLL_MAX,
            "poll_interval_seconds": POLL_INTERVAL_SECONDS,
            "stop_on_first_runtime_invalid": True,
            "stop_on_resolved_model_drift": True,
        },
        "rows": [],
        "status": "registered",
        "scientific_result_available": False,
    }


def execute(plan_path: Path, preflight_path: Path, auth_path: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"refuse to overwrite existing execution output: {output}")
    plan = read_json(plan_path)
    preflight = read_json(preflight_path)
    if not auth_path.exists():
        raise RuntimeError(f"human authorization artifact missing: {auth_path}")
    auth = read_json(auth_path)
    auth_errors = validate_authorization(auth, plan)
    if auth_errors:
        raise RuntimeError("authorization invalid: " + ",".join(auth_errors))
    if str(preflight.get("status")) != "HOLD_EXPLICIT_SCIENTIFIC_REOPEN_AND_EXPERIMENT_AUTHORITY":
        raise RuntimeError("unexpected preflight state")
    if str(preflight["fresh_execution_contract"]["plan_body_sha256"]) != str(plan["plan_body_sha256"]):
        raise RuntimeError("preflight/plan hash mismatch")
    if str(preflight["frozen_execution_code"]["runner_sha256"]) != sha_file(Path(__file__)):
        raise RuntimeError("runner changed after preflight freeze")
    if str(preflight["frozen_execution_code"]["analyzer_sha256"]) != sha_file(ANALYZER_PATH):
        raise RuntimeError("analyzer changed after preflight freeze")
    if str(plan["g0"]["source"]) != G0_SOURCE or str(plan["g0"]["source_sha256"]) != sha_bytes(G0_SOURCE.encode("utf-8")):
        raise RuntimeError("G0 source changed after plan freeze")
    assets = load_assets()
    if set(assets["endpoints"]) != set(row["endpoint_id"] for row in plan["rows"]):
        raise RuntimeError("plan endpoint inventory does not match frozen assets")

    raw_settings = ArkSettings.from_env(required=True)
    if raw_settings.base_url.rstrip("/") != str(plan["model_identity"]["required_plan_base_url"]).rstrip("/"):
        raise RuntimeError("Ark base URL is not the frozen Plan billing route; refuse execution")
    settings = ArkSettings(
        api_key=raw_settings.api_key,
        base_url=raw_settings.base_url,
        default_model=raw_settings.default_model,
        timeout_seconds=180.0,
        max_retries=0,
    )
    client = ArkResponsesClient(settings)

    authority = acquire_authority(
        DATA_ROOT,
        OWNER_ID,
        str(plan["plan_body_sha256"]),
        "temporal-skill-g0-executor",
        "TEMP-O4-STAGE-A",
        "TEMP-O4-G0-STAGE-A-DEEPSEEK-20260824",
    )
    release_outcome = "startup-failure"
    payload: dict[str, Any] | None = None
    try:
        payload = build_initial_payload(plan, preflight, auth, assets)
        payload["runtime_authority"] = authority
        payload["status"] = "running"
        atomic_json(output, payload)
        release_outcome = "completed"
        for index, plan_row in enumerate(plan["rows"]):
            row = run_one(client, assets, plan_row)
            payload["rows"].append(row)
            payload["attempted_rows"] = index + 1
            atomic_json(output, payload)
            if not row.get("runtime_valid"):
                payload["status"] = "stopped"
                payload["stopped_reason"] = str(row.get("failure_kind") or "runtime-invalid")
                payload["scientific_result_available"] = False
                release_outcome = payload["stopped_reason"]
                atomic_json(output, payload)
                return payload
        payload["status"] = "completed"
        payload["scientific_result_available"] = True
        payload["rows_total"] = len(payload["rows"])
        payload["runtime_valid_rows"] = sum(bool(row.get("runtime_valid")) for row in payload["rows"])
        payload["result_body_sha256"] = canonical_sha({k: v for k, v in payload.items() if k != "result_body_sha256"})
        atomic_json(output, payload)
        return payload
    except Exception as exc:
        release_outcome = f"runner-exception:{type(exc).__name__}"
        if payload is not None:
            payload["status"] = "stopped"
            payload["stopped_reason"] = release_outcome
            payload["scientific_result_available"] = False
            payload["runner_exception"] = str(exc)[:1200]
            atomic_json(output, payload)
        raise
    finally:
        release_authority(DATA_ROOT, OWNER_ID, str(authority["authority_id"]), release_outcome)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute the pre-authorized TEMP-O4 Stage-A fresh N/G0/T plan.")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--authorization", type=Path, default=DEFAULT_AUTHORIZATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    plan = read_json(args.plan)
    assets = load_assets()
    summary = {
        "plan_body_sha256": plan["plan_body_sha256"],
        "planned_model_calls": plan["summary"]["planned_model_calls"],
        "runner_sha256": sha_file(Path(__file__)),
        "asset_hashes": assets["hashes"],
        "authorization_present": args.authorization.exists(),
        "output_exists": args.output.exists(),
    }
    if args.validate_only:
        if args.authorization.exists():
            summary["authorization_errors"] = validate_authorization(read_json(args.authorization), plan)
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
        return

    result = execute(args.plan, args.preflight, args.authorization, args.output)
    print(json.dumps({
        "status": result["status"],
        "attempted_rows": result.get("attempted_rows", 0),
        "scientific_result_available": result.get("scientific_result_available", False),
        "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
