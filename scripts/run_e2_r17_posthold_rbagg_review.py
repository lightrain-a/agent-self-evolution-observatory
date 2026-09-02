#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_e2_r17_v3_1_review as base

PREF0 = ROOT / "generated/e2-r17-posthold-rbagg-diagnostic-pref0-adjudication-20260902.json"
IDENTITY = ROOT / "generated/e2-r17-deepseek-v2-repair2-model-identity-adjudication-20260831.json"
OUT_ROOT = ROOT / "generated/e2-r17-posthold-rbagg-review-20260902"
MODELS = ("deepseek-v4-pro", "kimi-k3")
MINDMEMOS_ROOT = Path("/data/wyt/evidence-substrates/MindMemOS-20260817")
REASONINGBANK_ROOT = Path("/data/wyt/e2-r17-search-projection/baselines/published/reasoning-bank")


def schema() -> dict[str, Any]:
    return {
        "pref0_sha256_acknowledged": "",
        "verdict": "PASS_TO_SEPARATE_SINGLE_STREAM_SEMANTIC_PILOT|REVISE_RBAGG_BEFORE_PROVIDER|STOP_RBAGG_DIAGNOSTIC",
        "parent_hold_boundary_assessment": "",
        "predeclared_diagnostic_role_assessment": "",
        "reasoningbank_semantic_boundary_assessment": "",
        "session_score_semantics_assessment": "",
        "win_score_equivalence_assessment": "",
        "add_record_summary_provenance_assessment": "",
        "mindmemos_scored_path_assessment": "",
        "summary_stage_substitution_assessment": "",
        "fresh_win_d_control_assessment": "",
        "aggregation_reuse_across_replicates_assessment": "",
        "provider_budget_and_compute_assessment": "",
        "secondary_inference_assessment": "",
        "semantic_pilot_scope_assessment": "",
        "remaining_blockers": [
            {"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_repair": ""}
        ],
        "nonblocking_notes": [""],
        "semantic_pilot_recommendation": "ALLOW_SEPARATE_SINGLE_STREAM_SEMANTIC_PILOT_AUTHORIZATION|HOLD|STOP",
        "full_diagnostic_recommendation": "HOLD|STOP",
        "parent_scientific_status_must_remain": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, pref0_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent adversarial protocol reviewer for a POST-HOLD secondary diagnostic in E2-R17 Search-Projection Censoring. You are a reviewer only. You receive no new RB-AGG scientific effectiveness outcome. This consultation has zero experiment, updater, heldout, paper-promotion, public-benchmark, or submission authority.

Reviewer endpoint: {model}
Exact RB-AGG Pre-F0 adjudication SHA-256: {pref0_sha}

Historical fact that MUST remain immutable: the complete DeepSeek parent result is `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`. RB-AGG is not allowed to rescue it, append samples to it, or recompute the parent p-value.

The pre-outcome V3 design had already named `RB_AGG` as a ReasoningBank collision diagnostic that could run regardless of MRW GO/HOLD after a semantic runtime pilot. However the final closeout correctly disabled any AUTOMATIC RB-AGG rescue. This new child is therefore independently preregistered and may at most diagnose whether richer same-pool aggregation collides with the minimal failed-witness story.

Audit the ACTUAL bound code and first-party source. Be especially hostile to semantic spoofing.

1. PARENT BOUNDARY: Does the new protocol unambiguously preserve the parent HOLD for every possible RB result? Is this truly a secondary collision diagnostic rather than disguised sample-size rescue?

2. PREDECLARED ROLE: Given the old V3 plan, is it legitimate to revisit RB-AGG now as a separately preregistered post-HOLD diagnostic, provided it never changes the parent decision? Or should post-outcome timing alone STOP the diagnostic?

3. REASONINGBANK SEMANTICS: The pinned ReasoningBank `PARALLEL_SI` output is a set of Memory Items directly used as memory in the source system. The child explicitly labels itself `ReasoningBank-style`, NOT source-faithful. Is the proposed use of literal PARALLEL_SI over all eight frozen trajectories with 512-token/source cap, success/failure labels, temperature .7, strict 1–5 item parser and exact source provenance a defensible semantic adapter? Flag any material deviation that makes the label misleading.

4. SESSION SCORE: MindMemOS scored patch prompts say each summary has a trajectory evaluation score and higher score means the session went better. The child does NOT score the generated Memory Items. Instead it defines the originating record as the complete frozen K=8 search session and sets score=`acting_success`, the actual best-of-K user-facing session outcome. Is that truthful or is it still a semantic misrepresentation requiring STOP/repair?

5. SCORE EQUIVALENCE: Zero-provider preflight proved on 96/96 pools that the RB session score equals WIN's selected winner trajectory score under the frozen binary selector. Does this remove score-label confounding for RB-vs-WIN-D? Explain whether any residual score semantics asymmetry remains.

6. 1:1 PROVENANCE: First-party `SkillTraceSummary` is documented as 1:1 with an originating add trace. The adapter creates one explicit synthetic K=8 SEARCH-SESSION add record and one matching precomputed summary. It proves the summary exists before `SkillEvolver.evolve`, and forbids direct trajectory summarization of that synthetic source. Actual-path preflight on in-memory Qdrant confirms 8 precomputed summaries, 0 new trajectory-summary calls, exactly one evolved version. Is this a scientifically honest boundary substitution, or does it spoof first-party MindMemOS semantics enough to invalidate the diagnostic?

7. SAME PATCH PATH: After precomputed summaries exist, RB uses the same first-party `PROPOSE_PATCH_SCORED_SYSTEM`, same patch parser, same config, initial skill, batch size 8, temperature 0, correction rule and no rewrite. Is the diagnostic adequately isolated at the summary/evidence stage?

8. SUMMARY-STAGE SUBSTITUTION: Parent WIN nominally makes 8 first-party trajectory-summary calls then propose+apply. RB substitutes 8 PARALLEL_SI calls for those summary calls, then the same propose+apply. Nominal provider call count therefore remains 10 per one updater realization, though RB input/token content is richer and aggregation temperature differs. Is this acceptable for a METHOD/COLLISION diagnostic if token/compute differences are reported, or is a matched-token control mandatory before any result is interpretable?

9. CONTEMPORANEOUS CONTROL: The child refuses to compare new RB only against historical WIN-C and instead preregisters a fresh concurrent WIN-D, with same pools, initial skill, heldout, 4 updater replicates, model identity, and interleaved execution. Does this adequately close wall-clock/provider drift?

10. AGGREGATION STOCHASTICITY: The proposed full diagnostic generates one RB aggregate per task exactly once, freezes it, and reuses the same eight aggregate summaries across four updater replicates. This isolates updater stochasticity but not aggregation stochasticity. Is that the right scientific unit for this secondary method diagnostic, or must aggregation also be replicated? If repair is required, specify it BEFORE provider pilot.

11. INFERENCE: Full diagnostic would compare fresh RB-AGG vs fresh WIN-D at the same 12 stream units, four replicates/stream and same 18 heldout tasks. One exact stream-level sign-flip contrast plus paired bootstrap and TOST is predeclared. Historical MRW/WIN outcomes do not enter the child primary statistic. Is this statistically and causally acceptable as secondary collision evidence?

12. PILOT SCOPE: Review may at most allow a separately authorized fixed-stream `e1-agj-00` semantic provider pilot: 8 aggregation calls + one updater realization (2 nominal, hard max 3) = 10 nominal / 11 hard max, zero heldout, no effectiveness inference, pilot skill permanently excluded. Is that scope minimal and sufficient?

13. FAILURE DISCIPLINE: Aggregator parse is strict, retry=0, malformed output fail-closes, model identity is exact, no hidden retry, no provider ambiguity tolerated. Pilot failure cannot be automatically retried. Does the code/protocol preserve this?

PASS only if there are no P0/P1 blockers and `remaining_blockers` is exactly []. Even PASS MUST set `full_diagnostic_recommendation=HOLD`, `paper_claim_authority=false`, and only recommend a SEPARATE single-stream semantic-pilot authorization. Do not authorize that pilot directly.

Return exactly one JSON object and no markdown using this schema:
{spec}
Set `pref0_sha256_acknowledged` exactly to the SHA above.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


base.REPAIR = PREF0
base.IDENTITY = IDENTITY
base.OUT_ROOT = OUT_ROOT
base.MODELS = MODELS
base.DOSSIER = (
    ("pref0_adjudication", PREF0),
    ("protocol", ROOT / "consultations/e2-r17-posthold-rbagg-diagnostic-protocol-20260902.md"),
    ("semantic_preflight", ROOT / "generated/e2-r17-posthold-rbagg-zero-provider-semantic-adapter-preflight-20260902.json"),
    ("actual_path_preflight", ROOT / "generated/e2-r17-posthold-rbagg-zero-provider-actual-path-preflight-v2-20260902.json"),
    ("actual_path_v1_blocker", ROOT / "generated/e2-r17-posthold-rbagg-zero-provider-actual-path-v1-assertion-blocker-20260902.json"),
    ("semantic_adapter", ROOT / "research_pipeline/e2_r17_rbagg_posthold.py"),
    ("mindmemos_adapter", ROOT / "research_pipeline/e2_r17_rbagg_mindmemos_updater.py"),
    ("adapter_tests", ROOT / "research_pipeline/test_e2_r17_rbagg_posthold.py"),
    ("rb_style_renderer", ROOT / "research_pipeline/e2_r17_reasoningbank_style.py"),
    ("parent_closeout", ROOT / "generated/e2-r17-deepseek-v2-final-scientific-closeout-20260902.json"),
    ("old_v3_plan", ROOT / "generated/e2-r17-experiment-plan-v3-20260828.json"),
    ("parent_repair2_contract", ROOT / "generated/e2-r17-deepseek-v2-repair2-contract-20260831.json"),
    ("mindmemos_evolution_first_party", MINDMEMOS_ROOT / "src/mindmemos/mindmemos/pipelines/skill/evolution.py"),
    ("mindmemos_skill_typing_first_party", MINDMEMOS_ROOT / "src/mindmemos/mindmemos/typing/skill.py"),
    ("mindmemos_skill_patch_prompt_first_party", MINDMEMOS_ROOT / "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py"),
    ("reasoningbank_memory_instruction", REASONINGBANK_ROOT / "WebArena/prompts/memory_instruction.py"),
    ("reasoningbank_induce_scaling", REASONINGBANK_ROOT / "WebArena/induce_scaling.py"),
)
base.schema = schema
base.prompt_for = prompt_for


def identity_map() -> dict[str, str]:
    payload = json.loads(IDENTITY.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS_CURRENT_REVIEW_TRANCHE":
        raise RuntimeError("RB-AGG reviewer identity adjudication is not PASS_CURRENT_REVIEW_TRANCHE")
    rows = payload.get("requested_and_resolved") or {}
    resolved = {model: str(rows[model]["resolved"]) for model in MODELS}
    if len(set(resolved.values())) != len(MODELS):
        raise RuntimeError("RB-AGG reviewer identities are not distinct")
    return resolved


base.identity_map = identity_map


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-file", type=Path, required=True)
    ap.add_argument("--max-output-tokens", type=int, default=5000)
    args = ap.parse_args()
    expected = base.identity_map()
    bound, hashes = base.dossier()
    pref0_sha = base.sha_file(PREF0)
    base.load_env_file(args.env_file)
    source = base.ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != base.PLAN_BASE_URL:
        raise RuntimeError("RB-AGG review refuses non-Ark-Plan route")
    settings = base.ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    client = base.ArkResponsesClient(settings)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for model in MODELS:
        row = base.call(
            client,
            model=model,
            expected_resolved=expected[model],
            bound=bound,
            hashes=hashes,
            repair_sha=pref0_sha,
            max_output_tokens=args.max_output_tokens,
        )
        base.atomic_json(OUT_ROOT / f"{base.slug(model)}.json", row)
        rows.append(row)
    completed = [row for row in rows if row.get("status") == "COMPLETED"]
    allow = len(completed) == len(rows) and all(
        row.get("review", {}).get("pref0_sha256_acknowledged") == pref0_sha
        and row.get("review", {}).get("verdict") == "PASS_TO_SEPARATE_SINGLE_STREAM_SEMANTIC_PILOT"
        and row.get("review", {}).get("semantic_pilot_recommendation") == "ALLOW_SEPARATE_SINGLE_STREAM_SEMANTIC_PILOT_AUTHORIZATION"
        and row.get("review", {}).get("full_diagnostic_recommendation") == "HOLD"
        and row.get("review", {}).get("parent_scientific_status_must_remain") == "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS"
        and row.get("review", {}).get("paper_claim_authority") is False
        and not row.get("review", {}).get("remaining_blockers")
        for row in completed
    )
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-posthold-rbagg-dual-protocol-review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pref0_sha256": pref0_sha,
        "statuses": {row["requested_model"]: row.get("status") for row in rows},
        "resolved_models": {row["requested_model"]: row.get("resolved_model") for row in rows},
        "verdicts": {row["requested_model"]: row.get("review", {}).get("verdict") for row in completed},
        "remaining_blockers": {row["requested_model"]: row.get("review", {}).get("remaining_blockers") for row in completed},
        "all_pass_to_separate_single_stream_semantic_pilot": allow,
        "parent_primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
        "parent_status_changed": False,
        "semantic_pilot_authority": False,
        "full_diagnostic_authority": False,
        "paper_claim_authority": False,
    }
    base.atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if len(completed) == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
