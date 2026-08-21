from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .api_research_memory import record_parsed_api_output, record_raw_api_output
from .p12_recency_bias_execute import _call_once, _close_parse_failure
from .p12_recency_bias_harness import (
    CANDIDATE_ID,
    CONTRACT_SHA256,
    EXECUTOR_MODEL,
    retrieval_text,
    sha_json,
    skill_calibration_bundles,
    skill_compilation_prompt,
    skill_tool,
)
from .p12_recency_bias_protocol import (
    client,
    load_json,
    lock_output,
    parse_skills,
    provider_archive_payload,
    sha_bytes,
    sha_text,
    write_json,
)
from .paper_first_evidence_acquisition import compile_harness_runtime_repair_receipts, validate_evidence_plan

FAILURE_V3_FILENAME = "runtime-failure-manifest-v3.json"
REVOKED_V3_FILENAME = "authorization-revoked-plan-v3.json"
OLD_MANIFEST_V3_FILENAME = "harness-implementation-manifest-v3.json"
REPAIR_PLAN_V4_FILENAME = "runtime-repair-plan-v4.json"
OFFLINE_PROBE_V4_FILENAME = "runtime-repair-offline-probe-v4.json"
PROTOCOL_REVIEW_V4_FILENAME = "runtime-protocol-review-v4.json"
TRANSPORT_PROBE_V4_FILENAME = "runtime-transport-probe-v4.json"
MANIFEST_V4_FILENAME = "harness-implementation-manifest-v4.json"
REPAIR_RECEIPT_V4_FILENAME = "runtime-repair-receipt-v4.json"
AUTHORIZATION_V4_FILENAME = "authorization-repaired-plan-v4.json"
OLD_RETURN_SENTENCE = "Return only through the supplied function."
FAILED_BUNDLE = "SKILL-BUNDLE-QUADRATIC"
REUSE_BUNDLE = "SKILL-BUNDLE-LINEAR"
UNSTARTED_BUNDLES = ("SKILL-BUNDLE-ALTERNATING2", "SKILL-BUNDLE-CYCLIC3")
MAX_OUTPUT_TOKENS = 700
FROZEN_MAX_MODEL_CALLS = 192
REPLACEMENT_PROVIDER_CALL_CAP = 99
PROTOCOL_VERSION = "P12_SKILL_JSON_FIRST_V4"


def _bundle(bundle_id: str) -> dict[str, Any]:
    return next(row for row in skill_calibration_bundles() if row["bundle_id"] == bundle_id)


def skill_prompt_v4(bundle: dict[str, Any]) -> str:
    base = skill_compilation_prompt(bundle)
    if not base.endswith(OLD_RETURN_SENTENCE):
        raise RuntimeError("frozen skill prompt return sentence drift")
    replacement = (
        'Response protocol only: before any reasoning, emit one first line containing exact JSON '
        '{"older_skill_text":"...","newer_skill_text":"..."}. The supplied function may also be called and takes priority. '
        'Keep both procedures under the original length limit; do not change the calibration task or procedure content criteria.'
    )
    return base[: -len(OLD_RETURN_SENTENCE)] + replacement


def scientific_prompt_body(prompt: str) -> str:
    if OLD_RETURN_SENTENCE in prompt:
        return prompt.split(OLD_RETURN_SENTENCE, 1)[0]
    marker = "Response protocol only: before any reasoning"
    if marker in prompt:
        return prompt.split(marker, 1)[0]
    raise ValueError("unrecognized P12 skill prompt protocol")


def parse_skills_v4(archive: dict[str, Any]) -> tuple[dict[str, str], str]:
    try:
        return parse_skills(archive)
    except Exception:
        pass
    first = next((line.strip() for line in str(archive.get("text") or "").splitlines() if line.strip()), "")
    if not first:
        raise ValueError("v4 skill fallback requires first-line JSON")
    try:
        payload = json.loads(first)
    except json.JSONDecodeError as error:
        raise ValueError("v4 skill fallback requires exact first-line JSON") from error
    clean = {"function_calls": [], "text": json.dumps(payload, ensure_ascii=False, separators=(",", ":"))}
    values, _ = parse_skills(clean)
    return values, "JSON_FIRST_TEXT"


def build_repair_plan(run_root: Path) -> dict[str, Any]:
    failure = load_json(run_root / FAILURE_V3_FILENAME)
    old = load_json(run_root / OLD_MANIFEST_V3_FILENAME)
    bodies = {}
    for bundle_id in (FAILED_BUNDLE, *UNSTARTED_BUNDLES):
        base = skill_compilation_prompt(_bundle(bundle_id))
        new = skill_prompt_v4(_bundle(bundle_id))
        bodies[bundle_id] = {
            "old_prompt_sha256": sha_text(base),
            "new_prompt_sha256": sha_text(new),
            "scientific_prompt_body_sha256": sha_text(scientific_prompt_body(base)),
            "scientific_prompt_body_unchanged": scientific_prompt_body(base) == scientific_prompt_body(new),
        }
    core = {
        "schema_version": "1.0",
        "status": "P12_SKILL_RUNTIME_REPAIR_PLAN_V4",
        "candidate_id": CANDIDATE_ID,
        "contract_sha256": CONTRACT_SHA256,
        "failure_manifest_sha256": failure["failure_manifest_sha256"],
        "replaces_harness_manifest_sha256": old["harness_manifest_sha256"],
        "protocol_version": PROTOCOL_VERSION,
        "protocol_only_change": True,
        "scientific_object_unchanged": True,
        "reuse_completed_skill_bundles": [REUSE_BUNDLE],
        "retry_failed_skill_bundle": {"bundle_id": FAILED_BUNDLE, "max_attempts": 1},
        "unstarted_skill_bundles": list(UNSTARTED_BUNDLES),
        "prompt_bindings": bodies,
        "model_unchanged": True,
        "temperature_unchanged": True,
        "tool_schema_unchanged": True,
        "skill_length_limits_unchanged": True,
        "remaining_scientific_work": {"skill_calls": 3, "evaluation_calls": 96},
        "provider_calls_already_charged": int(failure["provider_calls_charged"]),
        "remaining_model_call_budget_before_repair": int(failure["remaining_model_call_budget"]),
        "replacement_provider_call_cap": REPLACEMENT_PROVIDER_CALL_CAP,
        "scientific_authority": False,
        "belief_authority": False,
    }
    core["replacement_harness_plan_sha256"] = sha_json(core)
    return core


def run_offline_probe(run_root: Path) -> dict[str, Any]:
    output = run_root / OFFLINE_PROBE_V4_FILENAME
    lock = lock_output(output, {"stage": "p12-skill-repair-offline-v4"})
    try:
        plan = build_repair_plan(run_root)
        function_archive = {"function_calls": [{"name": "submit_p12_skills", "arguments": json.dumps({"older_skill_text": "Use a robust global pattern.", "newer_skill_text": "Use a recent-window cross-check."})}], "text": ""}
        text_archive = {"function_calls": [], "text": '{"older_skill_text":"Use a stable arithmetic rule.","newer_skill_text":"Check endpoint shocks first."}\nreasoning may follow'}
        checks = {
            "all_skill_bodies_unchanged": all(row["scientific_prompt_body_unchanged"] for row in plan["prompt_bindings"].values()),
            "reuse_one_retry_one_unstarted_two": plan["reuse_completed_skill_bundles"] == [REUSE_BUNDLE] and plan["retry_failed_skill_bundle"]["bundle_id"] == FAILED_BUNDLE and len(plan["unstarted_skill_bundles"]) == 2,
            "function_call_preferred": parse_skills_v4(function_archive)[1] == "FUNCTION_CALL",
            "json_first_fallback": parse_skills_v4(text_archive)[1] == "JSON_FIRST_TEXT",
            "total_calls_107_within_192": plan["provider_calls_already_charged"] + plan["replacement_provider_call_cap"] == 107 <= FROZEN_MAX_MODEL_CALLS,
        }
        result = {"schema_version": "1.0", "status": "P12_SKILL_RUNTIME_REPAIR_OFFLINE_V4_PASS" if all(checks.values()) else "P12_SKILL_RUNTIME_REPAIR_OFFLINE_V4_FAIL", "checks": checks, "replacement_harness_plan_sha256": plan["replacement_harness_plan_sha256"], "scientific_authority": False, "belief_authority": False}
        result["offline_probe_sha256"] = sha_json(result)
        write_json(run_root / REPAIR_PLAN_V4_FILENAME, plan)
        write_json(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def run_neutral_transport_probe(run_root: Path, persistent_root: Path) -> dict[str, Any]:
    output = run_root / TRANSPORT_PROBE_V4_FILENAME
    lock = lock_output(output, {"stage": "p12-skill-transport-v4"})
    try:
        prompt = 'Neutral response-protocol probe. Before any reasoning, first line must be exact JSON {"older_skill_text":"Use rule A.","newer_skill_text":"Use rule B."}. No scientific task or evaluation data is present.'
        provider_root = persistent_root / "runs" / f"p12-neutral-skill-json-{sha_text(PROTOCOL_VERSION)[:10]}"
        provider_root.mkdir(parents=True, exist_ok=True)
        response = client().respond(prompt, model=EXECUTOR_MODEL, max_output_tokens=180, temperature=0.0, thinking="disabled", store=True)
        archive = provider_archive_payload(response)
        raw = provider_root / "raw-skill-json-first.json"
        raw.write_text(json.dumps(archive, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
        psha = sha_text(prompt)
        archived = record_raw_api_output(run_root=provider_root, stage="p12-skill-json-transport-v4", raw_path=raw, requested_model=EXECUTOR_MODEL, resolved_model=archive["resolved_model"], request_fingerprint=sha_json({"stage": "p12-skill-json-transport-v4", "prompt_sha256": psha}), prompt_sha256=psha, root=persistent_root)
        skills, source = parse_skills_v4(archive)
        passed = skills == {"older_skill_text": "Use rule A.", "newer_skill_text": "Use rule B."} and source == "JSON_FIRST_TEXT"
        result = {"schema_version": "1.0", "status": "P12_SKILL_RUNTIME_TRANSPORT_V4_PASS" if passed else "P12_SKILL_RUNTIME_TRANSPORT_V4_FAIL", "raw_sha256": archived["raw_sha256"], "response_id_archived": bool(archive.get("response_id")), "answer_source": source, "scientific_authority": False, "belief_authority": False}
        result["transport_probe_sha256"] = sha_json(result)
        record_parsed_api_output(run_root=provider_root, stage="p12-skill-json-transport-v4", raw_sha256=archived["raw_sha256"], structured_payload=result, requested_model=EXECUTOR_MODEL, resolved_model=archive["resolved_model"], research_objects=[], root=persistent_root)
        write_json(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def authorize_v4(run_root: Path) -> dict[str, Any]:
    output = run_root / AUTHORIZATION_V4_FILENAME
    lock = lock_output(output, {"stage": "p12-skill-authorize-v4"})
    try:
        revoked = load_json(run_root / REVOKED_V3_FILENAME)
        failure = load_json(run_root / FAILURE_V3_FILENAME)
        old = load_json(run_root / OLD_MANIFEST_V3_FILENAME)
        plan = load_json(run_root / REPAIR_PLAN_V4_FILENAME)
        offline = load_json(run_root / OFFLINE_PROBE_V4_FILENAME)
        transport = load_json(run_root / TRANSPORT_PROBE_V4_FILENAME)
        review = load_json(run_root / PROTOCOL_REVIEW_V4_FILENAME)
        if offline.get("status") != "P12_SKILL_RUNTIME_REPAIR_OFFLINE_V4_PASS" or transport.get("status") != "P12_SKILL_RUNTIME_TRANSPORT_V4_PASS":
            raise RuntimeError("P12 skill v4 probes not PASS")
        if review.get("verdict") != "CLEAR_PROTOCOL_EQUIVALENCE" or review.get("reviewer_independent") is not True:
            raise RuntimeError("P12 skill v4 independent review not CLEAR")
        base = Path(__file__).parent
        names = ("p12_recency_bias_harness.py", "p12_recency_bias_protocol.py", "p12_recency_bias_execute.py", "p12_recency_bias_skill_repair_v4.py")
        manifest = {"schema_version": "1.0", "status": "P12_SKILL_RUNTIME_REPAIR_HARNESS_V4_PASS", "candidate_id": CANDIDATE_ID, "contract_sha256": CONTRACT_SHA256, "failure_manifest_sha256": failure["failure_manifest_sha256"], "replaces_harness_manifest_sha256": old["harness_manifest_sha256"], "replacement_harness_plan_sha256": plan["replacement_harness_plan_sha256"], "offline_probe_sha256": offline["offline_probe_sha256"], "transport_probe_sha256": transport["transport_probe_sha256"], "protocol_review_sha256": review["review_sha256"], "code_sha256": {name: sha_bytes((base / name).read_bytes()) for name in names}, "replacement_provider_call_cap": REPLACEMENT_PROVIDER_CALL_CAP, "sandboxed": True, "probe_passed": True, "budget_feasible": True, "scientific_object_unchanged": True, "protocol_only_change": True, "scientific_authority": False, "belief_authority": False}
        manifest["harness_manifest_sha256"] = sha_json(manifest)
        write_json(run_root / MANIFEST_V4_FILENAME, manifest)
        receipt = {"schema_version": "1.0", "scientific_authority": False, "receipts": [{"candidate_id": CANDIDATE_ID, "contract_sha256": CONTRACT_SHA256, "failure_manifest_sha256": failure["failure_manifest_sha256"], "replaces_harness_manifest_sha256": old["harness_manifest_sha256"], "replacement_harness_plan_sha256": plan["replacement_harness_plan_sha256"], "harness_manifest_sha256": manifest["harness_manifest_sha256"], "implementation_summary": "P12 v4 skill-response protocol only: frozen calibration examples/truth/Kimi/temperature/two-skill content contract and length limits unchanged; emit exact older/newer JSON on the first line before optional reasoning, function call remains preferred; reuse LINEAR, retry QUADRATIC once, run the two never-started skill bundles, then unchanged evaluation.", "sandboxed": True, "probe_passed": True, "budget_feasible": True, "scientific_object_unchanged": True, "protocol_only_change": True, "replacement_provider_call_cap": REPLACEMENT_PROVIDER_CALL_CAP}]}
        write_json(run_root / REPAIR_RECEIPT_V4_FILENAME, receipt)
        repaired = compile_harness_runtime_repair_receipts(revoked, receipt)
        errors = validate_evidence_plan(repaired)
        if errors:
            raise ValueError(f"P12 v4 authorization invalid:{errors}")
        write_json(output, repaired)
        row = next(x for x in repaired["entries"] if x.get("candidate_id") == CANDIDATE_ID)
        return {"status": "P12_SKILL_RUNTIME_REPAIR_V4_AUTHORIZED", "execution_authorized": row["execution_authorized"], "harness_manifest_sha256": manifest["harness_manifest_sha256"], "replacement_harness_plan_sha256": plan["replacement_harness_plan_sha256"], "scientific_authority": False}
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def execute_skill_v4(run_root: Path, persistent_root: Path, bundle_id: str) -> dict[str, Any]:
    from .p12_recency_bias_protocol import authorization_ok

    authorization_ok(run_root)
    allowed = {FAILED_BUNDLE, *UNSTARTED_BUNDLES}
    if bundle_id not in allowed:
        raise ValueError(f"P12 v4 skill execution not authorized for {bundle_id}")
    output = run_root / "skill-compilation-v4" / f"{bundle_id}.json"
    lock = lock_output(output, {"stage": "p12-skill-v4", "bundle_id": bundle_id})
    try:
        bundle = _bundle(bundle_id)
        manifest = load_json(run_root / MANIFEST_V4_FILENAME)
        run_id = f"p12-recency-{manifest['harness_manifest_sha256'][:10]}-skill-{bundle_id.lower()}"
        archive, failure = _call_once(persistent_root=persistent_root, run_id=run_id, stage="p12-skill-compilation-v4", prompt=skill_prompt_v4(bundle), tools=skill_tool(), max_output_tokens=MAX_OUTPUT_TOKENS)
        if archive is None:
            result = {"schema_version": "1.0", "status": "SKILL_PROVIDER_FAILURE", "bundle_id": bundle_id, **failure}
            write_json(output, result)
            return result
        try:
            texts, source = parse_skills_v4(archive)
        except Exception as error:
            _close_parse_failure(persistent_root=persistent_root, archive=archive, stage="p12-skill-compilation-v4", error=error)
            result = {"schema_version": "1.0", "status": "SKILL_PROTOCOL_FAILURE", "bundle_id": bundle_id, "raw_sha256": archive["raw_sha256"], "error": f"{type(error).__name__}:{error}", "scientific_authority": False, "belief_authority": False}
            write_json(output, result)
            return result
        skills = [
            {"skill_id": bundle["older_skill_id"], "family": bundle["family"], "timestamp": bundle["older_timestamp"], "text": texts["older_skill_text"], "retrieval_text": retrieval_text(bundle["family"]), "origin": "DISJOINT_SKILL_CALIBRATION", "source_bundle_id": bundle_id, "scientific_authority": False},
            {"skill_id": bundle["newer_skill_id"], "family": bundle["family"], "timestamp": bundle["newer_timestamp"], "text": texts["newer_skill_text"], "retrieval_text": retrieval_text(bundle["family"]), "origin": "DISJOINT_SKILL_CALIBRATION", "source_bundle_id": bundle_id, "scientific_authority": False},
        ]
        result = {"schema_version": "1.0", "status": "SKILL_COMPILATION_COMPLETE", "bundle_id": bundle_id, "family": bundle["family"], "raw_sha256": archive["raw_sha256"], "resolved_model": archive["resolved_model"], "skill_source": source, "skills": skills, "usage": archive["usage"], "runtime_repair_v4": True, "scientific_authority": False, "belief_authority": False}
        result["receipt_sha256"] = sha_json(result)
        record_parsed_api_output(run_root=persistent_root / "runs" / run_id, stage="p12-skill-compilation-v4", raw_sha256=archive["raw_sha256"], structured_payload=result, requested_model=EXECUTOR_MODEL, resolved_model=archive["resolved_model"], research_objects=[], root=persistent_root)
        write_json(output, result)
        return result
    finally:
        if output.exists():
            lock.unlink(missing_ok=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=("offline-probe", "transport-probe", "authorize", "skill"))
    p.add_argument("--run-root", type=Path, required=True)
    p.add_argument("--persistent-root", type=Path)
    p.add_argument("--bundle-id")
    a = p.parse_args()
    if a.cmd == "offline-probe":
        out = run_offline_probe(a.run_root)
    elif a.cmd == "transport-probe":
        if a.persistent_root is None: raise SystemExit("--persistent-root required")
        out = run_neutral_transport_probe(a.run_root, a.persistent_root)
    elif a.cmd == "authorize":
        out = authorize_v4(a.run_root)
    else:
        if a.persistent_root is None or not a.bundle_id: raise SystemExit("--persistent-root and --bundle-id required")
        out = execute_skill_v4(a.run_root, a.persistent_root, a.bundle_id)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
