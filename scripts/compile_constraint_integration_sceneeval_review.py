from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "generated" / "sceneeval500-outcome-blind-constraint-audit-20260828.json"
OUTPUT = ROOT / "generated" / "constraint-integration-sceneeval-independent-review-20260828.json"
RAW_ROOT = Path("/data/wyt/agent-evolution-paper-first-reviews/constraint-integration-sceneeval-20260828")
KIMI = RAW_ROOT / "kimi-review.json"
DEEPSEEK = RAW_ROOT / "deepseek-review-v2.json"
DEEPSEEK_NONVOTING_PARTIAL = RAW_ROOT / "deepseek-review.json"

EXPECTED_AUDIT_SHA = "a3eaaa0571d51928e70f0094de1d0d4542211de165d1a196135be55df1247e45"
EXPECTED_KIMI_SHA = "a37514a511bab5a3d2d5d9fa888f751c900fd484767082993701175fd1458363"
EXPECTED_DEEPSEEK_SHA = "f166ae730054fdaa06b0225d8fc175f29db7cd07c7365cf727d8592ea4b89a08"
EXPECTED_NONVOTING_PARTIAL_SHA = "cf78023fc06ec2002e822c0735635732c4f873bd1feb7ba9404854f0bfdd5a37"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_json_object(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    start, end = candidate.find("{"), candidate.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("review contains no JSON object")
    payload = json.loads(candidate[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("review JSON is not an object")
    return payload


def load_review(path: Path, expected_sha: str, *, requested: str, resolved: str) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"missing reviewer raw artifact: {path}")
    actual_sha = sha256_file(path)
    if actual_sha != expected_sha:
        raise SystemExit(f"review digest drift: {path}: {actual_sha}")
    payload = extract_json_object(path.read_text(encoding="utf-8"))
    if payload.get("verdict") != "REVISE_BEFORE_PREREGISTRATION":
        raise SystemExit(f"unexpected review verdict: {path}: {payload.get('verdict')}")
    if payload.get("scientific_authority") is not False:
        raise SystemExit(f"review leaked scientific authority: {path}")
    return {
        "requested_model": requested,
        "resolved_model": resolved,
        "raw_path": str(path),
        "raw_sha256": actual_sha,
        "verdict": payload.get("verdict"),
        "confidence": payload.get("confidence"),
        "strongest_null": payload.get("strongest_null"),
        "identifiability": payload.get("identifiability"),
        "primary_test": payload.get("primary_test"),
        "p0_scope": payload.get("p0_scope"),
        "strongest_alternative": payload.get("strongest_alternative"),
        "negative_control": payload.get("negative_control"),
        "stop_conditions": payload.get("stop_conditions") or [],
        "forbidden_claim": payload.get("forbidden_claim"),
        "required_revision": payload.get("required_revision"),
        "scientific_authority": False,
    }


def main() -> None:
    if sha256_file(AUDIT) != EXPECTED_AUDIT_SHA:
        raise SystemExit("SceneEval audit digest drifted")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    measurement = audit.get("measurement_dependency_preflight") or {}
    if measurement.get("verified") is not True or measurement.get("raw_matching_observable") is not True:
        raise SystemExit("SceneEval prerequisite/matching observability is not verified")

    kimi = load_review(KIMI, EXPECTED_KIMI_SHA, requested="kimi-k3", resolved="kimi-k3")
    deepseek = load_review(
        DEEPSEEK,
        EXPECTED_DEEPSEEK_SHA,
        requested="deepseek-v4-pro",
        resolved="deepseek-v4-pro-ga-260813",
    )
    if sha256_file(DEEPSEEK_NONVOTING_PARTIAL) != EXPECTED_NONVOTING_PARTIAL_SHA:
        raise SystemExit("nonvoting DeepSeek partial artifact digest drifted")

    artifact = {
        "schema_version": "constraint-integration-sceneeval-independent-review-v1",
        "status": "REVISE_BEFORE_PREREGISTRATION",
        "review_scope": "outcome-blind scientific reduction and measurement-identifiability review only",
        "reviewed_audit_artifact": str(AUDIT.relative_to(ROOT)),
        "reviewed_audit_sha256": EXPECTED_AUDIT_SHA,
        "per_case_generator_outputs_read_before_review": False,
        "per_case_sceneeval_metric_outputs_read_before_review": False,
        "voting_reviews": [deepseek, kimi],
        "consensus": {
            "verdict": "REVISE_BEFORE_PREREGISTRATION",
            "reviewer_count": 2,
            "confidence_range": [0.82, 0.85],
            "strongest_null": "N2 prerequisite-aware conditional independence plus exchangeable scene-level frailty/overdispersion; no type-specific downstream interaction",
            "identifiability": "CONDITIONAL_AFTER_MEASUREMENT_REVISION",
            "measurement_revision": [
                "treat shared ObjMatching / ObjCount adequacy as prerequisite and control state rather than a peer cross-type scientific outcome",
                "restrict primary residual-coupling outcomes to prerequisite-eligible ObjAttr, OORel, and OARel specs",
                "condition explicitly on official raw matching/prerequisite state and preserve it as a content-addressed measurement artifact",
                "include scene-level exchangeable frailty/overdispersion before adding type-specific downstream covariance/interaction",
                "freeze the exact N2-vs-candidate model, held-out criterion, uncertainty calibration, and power/design simulation before reading per-case outcomes",
            ],
            "single_generator_scope": "HSM author-released SceneEval-500 output may support only a bounded single-generator P0 after measurement review and legitimate gated access; it cannot support the paper-level cross-generator claim",
            "paper_level_requirement": "at least one independently qualified second generator lane or external scene set is required before transport/generalization claims",
            "primary_negative_control": "oracle/independently verified object matching or an equivalent verified-matching subset; coupling that disappears after correct matching is evaluator-induced",
            "forbidden_interpretation": "naive co-failure among ObjCount/ObjAttr/OORel/OARel cannot be called generator-side integration failure because the official evaluator creates shared matching/prerequisite dependence",
        },
        "nonvoting_provider_history": [
            {
                "requested_model": "deepseek-v4-pro",
                "resolved_model": "deepseek-v4-pro-ga-260813",
                "disposition": "NONVOTING_INCOMPLETE_REASONING_ONLY",
                "note": "provider response was incomplete before assistant output after exhausting the requested reasoning budget",
                "raw_artifact": None,
            },
            {
                "requested_model": "deepseek-v4-pro",
                "resolved_model": "deepseek-v4-pro-ga-260813",
                "disposition": "NONVOTING_TRUNCATED_INVALID_JSON",
                "raw_path": str(DEEPSEEK_NONVOTING_PARTIAL),
                "raw_sha256": EXPECTED_NONVOTING_PARTIAL_SHA,
            },
            {
                "requested_model": "kimi-k3",
                "resolved_model": "kimi-k3",
                "disposition": "NONVOTING_INCOMPLETE_REASONING_ONLY",
                "note": "provider response was incomplete before assistant output when reasoning was not explicitly disabled",
                "raw_artifact": None,
            },
            {
                "requested_model": "kimi-k3",
                "resolved_model": None,
                "disposition": "NONVOTING_TRANSPORT_INDETERMINATE",
                "note": "one remote invocation returned an upstream/connector 502 before an auditable provider response was available; it is not counted as a scientific review",
                "raw_artifact": None,
            },
        ],
        "provider_accounting": {
            "completed_voting_review_calls": 2,
            "confirmed_nonvoting_provider_calls": 3,
            "connector_indeterminate_invocations": 1,
            "scientific_execution_provider_calls": 0,
            "gpu_calls": 0,
            "review_calls_create_scientific_authority": False,
        },
        "next_gate": {
            "name": "MEASUREMENT_MODEL_REVISION_AND_POWER_PREFLIGHT",
            "requirements": [
                "compile the prerequisite-aware downstream outcome definition",
                "freeze N0/N1/N2 and the candidate interaction/covariance model before per-case outcome read",
                "run outcome-blind power/design simulation using only released SceneEval metadata",
                "obtain legitimate HSM gated access or keep the P0 lane waiting",
                "qualify a second generator lane before any paper-level cross-generator claim",
            ],
        },
        "scientific_authority": False,
        "execution_authority": False,
        "authority": {
            "canonical_generator": False,
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "local_validation": False,
            "p0": False,
            "provider": False,
            "gpu": False,
            "scientific": False,
        },
    }
    OUTPUT.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": artifact["status"],
        "voting_reviews": len(artifact["voting_reviews"]),
        "consensus_null": artifact["consensus"]["strongest_null"],
        "identifiability": artifact["consensus"]["identifiability"],
        "scientific_execution_provider_calls": 0,
        "scientific_authority": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
