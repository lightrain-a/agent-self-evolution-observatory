#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponsesClient, ArkSettings, ArkResponseStateError
from research_pipeline.config import load_env_file

PAPER = ROOT / "paper_drafts/d2-temporal-skill-bottleneck-iclr2027/main.pdf"
CLAIMS = ROOT / "generated/d2-temporal-skill-bottleneck-claim-ledger.json"
PROBES = ROOT / "generated/d2-temporal-skill-independent-probes-20260822.json"
QA = ROOT / "generated/d2-temporal-skill-bottleneck-paper-qa-post-f11.json"
SEMANTIC = ROOT / "generated/d2-temporal-skill-f11-semantic-audit-20260823.json"
STRONG = ROOT / "generated/d2-temporal-skill-f9f10-strong-control-20260823.json"
OUT = ROOT / "generated/d2-temporal-skill-post-f11-semantic-mock-pc-20260823"
OUT.mkdir(parents=True, exist_ok=True)
MODELS = {"BLIND_MANUSCRIPT": "deepseek-v4-pro", "ARTIFACT_AWARE": "kimi-k3"}


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def schema() -> list[dict[str, Any]]:
    objection = {
        "type": "object",
        "properties": {
            "objection_id": {"type": "string"},
            "category": {"type": "string"},
            "text": {"type": "string"},
            "decision_critical": {"type": "boolean"},
            "claim_ids": {"type": "array", "items": {"type": "string"}},
            "repair_type": {"type": "string", "enum": ["manuscript", "analysis", "new_experiment", "support_access", "none"]},
        },
        "required": ["objection_id", "category", "text", "decision_critical", "claim_ids", "repair_type"],
        "additionalProperties": False,
    }
    review = {
        "type": "object",
        "properties": {
            "recommendation": {"type": "string", "enum": ["strong_reject", "reject", "weak_reject", "borderline", "weak_accept", "accept", "strong_accept"]},
            "score_1_to_10": {"type": "integer", "minimum": 1, "maximum": 10},
            "confidence_1_to_5": {"type": "integer", "minimum": 1, "maximum": 5},
            "novelty_1_to_5": {"type": "integer", "minimum": 1, "maximum": 5},
            "significance_1_to_5": {"type": "integer", "minimum": 1, "maximum": 5},
            "technical_quality_1_to_5": {"type": "integer", "minimum": 1, "maximum": 5},
            "empirical_sufficiency_1_to_5": {"type": "integer", "minimum": 1, "maximum": 5},
            "clarity_1_to_5": {"type": "integer", "minimum": 1, "maximum": 5},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "weaknesses": {"type": "array", "items": {"type": "string"}},
            "decision_critical_objections": {"type": "array", "items": objection},
            "strongest_reject_reason": {"type": "string"},
            "highest_value_next_action": {"type": "string"},
            "extra_experiment_needed_before_submission": {"type": "boolean"},
            "submission_advice": {"type": "string", "enum": ["freeze", "minor_revision", "major_revision", "new_experiment", "hold_support"]},
        },
        "required": ["recommendation", "score_1_to_10", "confidence_1_to_5", "novelty_1_to_5", "significance_1_to_5", "technical_quality_1_to_5", "empirical_sufficiency_1_to_5", "clarity_1_to_5", "strengths", "weaknesses", "decision_critical_objections", "strongest_reject_reason", "highest_value_next_action", "extra_experiment_needed_before_submission", "submission_advice"],
        "additionalProperties": False,
    }
    return [{"type": "function", "name": "submit_mock_pc_review", "description": "Return the independent ICLR-style review.", "parameters": {"type": "object", "properties": {"review": review}, "required": ["review"], "additionalProperties": False}}]


def client(model: str) -> ArkResponsesClient:
    env_path = os.environ.get("C06_CANON_ENV", "").strip()
    if not env_path:
        raise RuntimeError("C06_CANON_ENV must point to the authorized provider environment file")
    load_env_file(Path(env_path))
    key = os.environ.get("ARK_API_KEY", "").strip()
    if not key:
        raise RuntimeError("ARK_API_KEY missing")
    base = ArkSettings.from_env()
    return ArkResponsesClient(ArkSettings(api_key=key, base_url=base.base_url, default_model=model, timeout_seconds=300.0, max_retries=0))


def manuscript_text() -> str:
    return subprocess.run(["pdftotext", str(PAPER), "-"], check=True, text=True, capture_output=True).stdout


def prompt(mode: str) -> str:
    text = manuscript_text()
    base = f"""Act as a strict independent ICLR program-committee reviewer. Judge this manuscript as it exists now. Distinguish a valid negative/boundary result from an unsupported positive claim. Do not reward a manipulation check as downstream evidence. Do not require the authors to hide a preregistered negative result. Support or infrastructure failure has no scientific authority, although missing decisive evidence may still affect acceptance readiness. Focus on novelty, causal identification, empirical sufficiency, clarity, and whether the claimed contribution is competitive for ICLR. Return exactly one submit_mock_pc_review tool call.\n\nMANUSCRIPT:\n{text}\n"""
    if mode == "BLIND_MANUSCRIPT":
        return base + "\nBLIND_MANUSCRIPT mode: use only the manuscript. Do not assume hidden artifacts."
    packet = {
        "claim_ledger": json.loads(CLAIMS.read_text()),
        "independent_probe_summary": json.loads(PROBES.read_text()),
        "manuscript_qa": json.loads(QA.read_text()),
        "semantic_measurement_audit": json.loads(SEMANTIC.read_text()),
        "paper_pdf_sha256": sha_bytes(PAPER.read_bytes()),
        "nonstl_strong_control_crossmodel": json.loads(STRONG.read_text()),
    }
    return base + "\nARTIFACT_AWARE mode: audit the manuscript against this frozen evidence packet. Check that the deterministic STL gate and the semantic measurement audit are not conflated: the frozen deterministic 5/7 vs 0/7 result remains recorded, while the one valid blinded semantic reviewer gives 6/7 vs 2/7 with p=0.109375 and semantic robustness is explicitly unresolved. The second predeclared semantic reviewer is nonvoting after a parse failure and is not replaced. Judge whether this disclosure resolves the verifier-validity concern or instead materially weakens the empirical claim. The title asks what makes a skill causal and the paper is framed as an evaluation standard. Verify F1 is only a reachability manipulation check and F2 remains the prospective negative output-injection result. Audit F3 as the Qwen executable hidden-implementation swap: 6/19 versus 2/19, +21.1 points, p=0.109375. Audit F4 on the same endpoints with DeepSeek-v4-Pro: 5/19 versus 3/19, p=0.3125, never pooled with F3. Audit F5 as the original fresh Qwen population: 3/7 versus 2/7, p=0.50. Preserve the legacy five-endpoint F5-R2 support tranche as 1/5 versus 0/5 with p=0.50. Most importantly, audit F8 using the deduplicated first-time support-recovered endpoints from the original pre-outcome F5 candidate population. Twelve endpoints were executed in the latest support extension, but five had already appeared in legacy F5-R2 and therefore have zero new scientific authority. Only seven first-time endpoints count for F8. They give 5/7 targeted versus 0/7 matched-generic successes, +71.4 points, exact one-sided p=0.03125, and pass the frozen +20-point/p<=0.05 gate. All seven are STL-decomposition endpoints, so F8 supports executable procedure state within that family while broader procedure-family generality remains open. The full 12-endpoint rerun is diagnostic only. Audit F6 separately as a post-hoc stronger-control diagnostic: 6/19 correct procedure versus 1/19 substantive off-target procedure, +26.3 points with p=0.0625, and no primary-closure authority. Also audit the later first-observation completion of the same pre-outcome frozen F5 population. It uses exactly one first valid observation per execution-qualified endpoint, including one newly recovered first-time endpoint, and contains 20 endpoints total: targeted 10/20, matched generic 2/20, and no skill 2/20. The targeted-minus-generic descriptive difference is +40.0 points with eight targeted-only discordances, zero generic-only discordances, and exact one-sided p=0.00390625. This aggregate is robustness evidence only: support completion occurred after partial F5 outcomes, so formal_closure_authority is explicitly false and the F8 seven-endpoint tranche remains the closure-bearing independent result. The current frozen population has one support hold and three reference execution/replay failures; no failed candidate is replaced. Audit the new independent L2 strong-control tests as the main broader-family evidence. The L2 source population contains 60 task IDs frozen before F9 outcomes; 58 task JSONs were retrieved, 12 met the deterministic metadata candidate rule, and 9 passed execution qualification with no replacement. The target procedures span five non-STL families: linear interpolation, model comparison, residual diagnostics, ROCKET classification, and time-series forest regression. In F9/Qwen, one endpoint is invalid because the substantive off-target arm issued a frozen-protocol-forbidden second tool call; it was not retried. On the remaining 8 paired endpoints, targeted succeeds 5/8 and the task-local substantive off-target procedure 1/8, +50.0 points with four targeted-only discordances, zero control-only discordances, and exact p=0.0625. This reaches the magnitude floor but not alpha. F10 repeats the exact 9-endpoint contract with DeepSeek-v4-Pro: targeted 5/9, substantive off-target 2/9, +33.3 points, p=0.125, with all 27 records valid. No-skill is 0/9 and its secondary p=0.03125. F9 and F10 are adjudicated independently; their p-values are never pooled. The primary direction is positive on both models, while neither broad non-STL gate closes. Judge whether this materially answers the earlier concerns that the effect was STL-only and that neutral schema validation was too weak a control. Check that C3 retains the distinction between formal STL support and directional broader-family evidence; C4 remains active and requires longitudinal TimeSage-EV evidence; repeated endpoints carry zero new authority, and no cross-probe p-values are pooled.\n\nARTIFACT PACKET:\n" + json.dumps(packet, ensure_ascii=False)


def run(mode: str) -> dict[str, Any]:
    target = OUT / f"{mode}.json"
    if target.exists():
        return json.loads(target.read_text())
    model = MODELS[mode]
    pr = prompt(mode)
    packet_sha = sha_bytes(pr.encode())
    try:
        resp = client(model).respond(pr, model=model, max_output_tokens=6500, tools=schema(), thinking="disabled", store=True, allow_thinking_compatibility_fallback=True)
        calls = [x for x in resp.get("function_calls") or [] if x.get("name") == "submit_mock_pc_review"]
        if len(calls) != 1:
            raise RuntimeError(f"expected one review call, got {len(calls)}")
        args = json.loads(calls[0].get("arguments") or "{}")
        rid = str(resp.get("response_id") or "")
        out = {
            "schema_version": "1.0",
            "paper_id": "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",
            "revision": "POST_F11_SEMANTIC_MEASUREMENT_REVISION",
            "mode": mode,
            "requested_model": model,
            "resolved_model": resp.get("resolved_model"),
            "status": resp.get("status"),
            "usage": resp.get("usage") or {},
            "packet_sha256": packet_sha,
            "paper_pdf_sha256": sha_bytes(PAPER.read_bytes()),
            "review": args["review"],
            "provider_response_id_archived_privately": bool(rid),
            "provider_response_id_sha256": sha_bytes(rid.encode()) if rid else "",
            "scientific_authority": False,
            "experiment_authority": False,
            "submission_authority": False,
        }
    except ArkResponseStateError as exc:
        out = {
            "schema_version": "1.0", "paper_id": "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK", "revision": "POST_F11_SEMANTIC_MEASUREMENT_REVISION",
            "mode": mode, "requested_model": model, "status": "NONVOTING_PROVIDER_STATE_FAILURE", "packet_sha256": packet_sha,
            "provider_receipt": exc.receipt(), "scientific_authority": False, "experiment_authority": False, "submission_authority": False,
        }
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    return out


def main() -> None:
    pdf_sha = sha_bytes(PAPER.read_bytes())
    qa = json.loads(QA.read_text())
    probes = json.loads(PROBES.read_text())
    strong = json.loads(STRONG.read_text())
    if qa.get("summary", {}).get("pdf_sha256") != pdf_sha:
        raise RuntimeError("final C06 QA/PDF hash mismatch")
    if "f6_strong_offtarget_control_diagnostic" not in probes:
        raise RuntimeError("F6 missing from probe artifact")
    if probes["f6_strong_offtarget_control_diagnostic"].get("primary_closure_authority") is not False:
        raise RuntimeError("F6 closure boundary drift")
    f8 = probes.get("f8_frozen_population_support_recovery_extension") or {}
    pop = probes.get("f5_first_observation_population_completion_r5") or {}
    if f8.get("requested_endpoints") != 7 or f8.get("repeated_endpoint_count") != 5:
        raise RuntimeError("F8 dedup boundary drift")
    if f8.get("repeated_endpoints_scientific_authority") is not False or (f8.get("frozen_gate") or {}).get("pass") is not True:
        raise RuntimeError("F8 authority/gate drift")
    if pop.get("available_endpoints") != 20 or abs(float(pop.get("one_sided_exact_p") or -1) - 0.00390625) > 1e-12:
        raise RuntimeError("20-endpoint completion drift")
    if pop.get("formal_closure_authority") is not False or pop.get("repeated_r5_endpoint_calls_scientific_authority") is not False:
        raise RuntimeError("completion authority drift")
    if abs(float((strong.get("f9_qwen") or {}).get("primary", {}).get("one_sided_exact_p", -1)) - 0.0625) > 1e-12:
        raise RuntimeError("F9 strong-control drift")
    if abs(float((strong.get("f10_deepseek") or {}).get("primary", {}).get("one_sided_exact_p", -1)) - 0.125) > 1e-12:
        raise RuntimeError("F10 strong-control drift")
    if (strong.get("crossmodel_adjudication") or {}).get("pvalue_pooling") is not False or (strong.get("crossmodel_adjudication") or {}).get("primary_direction_positive_both_models") is not True:
        raise RuntimeError("F9/F10 cross-model adjudication drift")
    sem = json.loads(SEMANTIC.read_text())
    if sem.get("reviewers_voting") != 1:
        raise RuntimeError("F11 voting count drift")
    if (sem.get("adjudication") or {}).get("semantic_robustness_established") is not False:
        raise RuntimeError("F11 semantic authority drift")
    if abs(float((((sem.get("reviewers") or {}).get("deepseek-v4-pro-260425") or {}).get("targeted_vs_generic") or {}).get("one_sided_exact_p") or -1) - 0.109375) > 1e-12:
        raise RuntimeError("F11 semantic p-value drift")
    rows = [run("BLIND_MANUSCRIPT"), run("ARTIFACT_AWARE")]
    summary = {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK",
        "revision": "POST_F11_SEMANTIC_MEASUREMENT_REVISION",
        "paper_pdf_sha256": sha_bytes(PAPER.read_bytes()),
        "reviews": [{"mode": r["mode"], "status": r.get("status"), "recommendation": (r.get("review") or {}).get("recommendation"), "score": (r.get("review") or {}).get("score_1_to_10"), "empirical_sufficiency": (r.get("review") or {}).get("empirical_sufficiency_1_to_5"), "submission_advice": (r.get("review") or {}).get("submission_advice"), "extra_experiment": (r.get("review") or {}).get("extra_experiment_needed_before_submission")} for r in rows],
        "scientific_authority": False,
        "experiment_authority": False,
        "submission_authority": False,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
