from __future__ import annotations

import json
from pathlib import Path

from research_pipeline.ark_provider import ArkResponsesClient, extract_json_object

ROOT = Path(__file__).resolve().parents[1]
PAPER = Path(__file__).resolve().parent
BODY = (PAPER / "stri-20260816-narrow-body.tex").read_text(encoding="utf-8")
FORMAT = json.loads((ROOT / "generated" / "asset-first-stri-iclr2027-format-state-20260816.json").read_text(encoding="utf-8"))
QA = json.loads((ROOT / "generated" / "asset-first-stri-iclr2027-submission-qa-20260816.json").read_text(encoding="utf-8"))
PREMORTEM = json.loads((ROOT / "generated" / "asset-first-stri-narrow-final-review-20260816.json").read_text(encoding="utf-8"))
COLLISION = json.loads((ROOT / "generated" / "asset-first-stri-narrow-collision-review-20260816.json").read_text(encoding="utf-8"))
OUTPUT = ROOT / "generated" / "asset-first-stri-iclr2027-final-review-20260816.json"
RAW = ROOT / "generated" / "asset-first-stri-iclr2027-final-review-raw-20260816.txt"

prompt = f"""You are a strict independent ICLR 2027 reviewer performing the final paper-level premortem on a narrow submission. Review only the scientific claims actually retained in the supplied official 9-page body. Do not reward wording. Do not reopen a claim that the paper explicitly drops.

CURRENT CLAIM SCOPE:
N1: released self-evolving skill control surfaces can be sensitive to skill-package representation.
N2: for a finite frozen context-by-package support matrix A, R*(A)=min t subject to w>=0 and 1<=Aw<=t1 exactly decides package-only additive-exposure equalizability; the singleton-overlap theorem gives an interpretable factor-2 lower bound in its stated case.
N3: across the audited released regimes, non-equalizable support geometry rather than overlap prevalence tracks the static STRI residual.

FORBIDDEN CLAIMS / EVIDENCE BOUNDARY:
- no downstream utility harm claim;
- no dynamic STRI success claim;
- no empirical SQC success claim;
- no LP-algorithm novelty claim;
- the Qwen3-8B dynamic pilot failed its frozen proposer-qualification gate and supplies no scientific evidence for or against dynamic STRI;
- do not recommend lowering that gate, rerunning the same P0-A, adding generations, or changing backbone as a paper repair.

CURRENT FORMAL/FORMAT STATE:
{json.dumps(FORMAT.get('build_validation', {}), ensure_ascii=False)}
Submission QA: {json.dumps(QA, ensure_ascii=False)}
Previous narrow premortem: {PREMORTEM.get('verdict')} confidence={PREMORTEM.get('confidence')}
Narrow collision review: {COLLISION.get('verdict')} confidence={COLLISION.get('confidence')}

OFFICIAL 9-PAGE BODY:
---BEGIN BODY---
{BODY}
---END BODY---

Return exactly one JSON object with these fields:
- verdict: one of READY_TO_SUBMIT, REVISE_BEFORE_SUBMIT, NOT_READY
- confidence: number 0..1
- overall_score_1_to_10
- strongest_contribution
- strongest_reviewer_objection
- theorem_correctness: PASS or ISSUE plus concise reason
- novelty_boundary: PASS or ISSUE plus concise reason
- evidence_closure: PASS or ISSUE plus concise reason
- clarity_story: PASS or ISSUE plus concise reason
- required_revisions: array of only submission-blocking or high-value revisions that can be justified from this claim scope
- optional_revisions: array
- claims_that_must_remain_forbidden: array
- whether_new_gpu_evidence_is_required_for_current_claim_scope: boolean
- recommended_title
- scientific_authority: false

A request for additional dynamic/GPU evidence is valid only if N1-N3 as written literally cannot be supported by the supplied static/released evidence. The absence of a stronger but explicitly dropped claim is not itself a defect. Be conservative and reviewer-like."""

client = ArkResponsesClient()
response = client.respond(prompt, model="doubao-seed-2.0-lite", max_output_tokens=3600, thinking="disabled")
raw = str(response.get("text") or "")
RAW.write_text(raw, encoding="utf-8")
try:
    obj = extract_json_object(raw)
except Exception as exc:
    OUTPUT.write_text(json.dumps({
        "schema_version": "1.0",
        "status": "PROVIDER_INCOMPLETE_ZERO_AUTHORITY",
        "error": f"{type(exc).__name__}: {exc}",
        "requested_model": "doubao-seed-2.0-lite",
        "resolved_model": response.get("resolved_model"),
        "scientific_authority": False,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raise
obj.update({
    "schema_version": "1.0",
    "status": "COMPLETE_ZERO_AUTHORITY_REVIEW",
    "requested_model": "doubao-seed-2.0-lite",
    "resolved_model": response.get("resolved_model"),
    "scientific_authority": False,
})
OUTPUT.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"verdict": obj.get("verdict"), "confidence": obj.get("confidence"), "overall": obj.get("overall_score_1_to_10"), "resolved_model": response.get("resolved_model")}, ensure_ascii=False))
