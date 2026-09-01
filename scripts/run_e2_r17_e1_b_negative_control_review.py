#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import scripts.run_e2_r17_v3_1_review as base

DRAFT=ROOT/"generated/e2-r17-e1-b-negative-control-full-draft-contract-20260829.json"
IDENTITY=ROOT/"generated/e2-r17-e1-b-negative-control-model-identity-qualification-20260829.json"
OUT_ROOT=ROOT/"generated/e2-r17-e1-b-negative-control-review-20260829"


def schema()->dict[str,Any]:
    return {
        "draft_contract_sha256_acknowledged":"",
        "verdict":"PASS_TO_SEPARATELY_AUTHORIZED_NEGATIVE_CONTROL_FULL|REVISE_NEGATIVE_CONTROL_BEFORE_EXECUTION|STOP_NEGATIVE_CONTROL",
        "scientific_units_and_split_assessment":"",
        "identical_treatment_assessment":"",
        "arm_order_and_temporal_bias_assessment":"",
        "runtime_and_receipt_handoff_assessment":"",
        "provider_budget_and_resume_assessment":"",
        "heldout_evaluation_assessment":"",
        "statistics_and_equivalence_assessment":"",
        "outcome_selection_and_failure_policy_assessment":"",
        "mrw_separation_assessment":"",
        "remaining_blockers":[{"priority":"P0|P1","issue":"","why_blocking":"","exact_repair":""}],
        "nonblocking_notes":[""],
        "negative_control_execution_recommendation":"ALLOW_SEPARATE_FROZEN_NEGATIVE_CONTROL_AUTHORIZATION|HOLD|STOP",
        "mrw_execution_recommendation":"HOLD|STOP",
        "paper_claim_authority":False,
        "single_sentence_verdict":""
    }


def prompt_for(model:str,bound:str,repair_sha:str)->str:
    spec=json.dumps(schema(),ensure_ascii=False,indent=2)
    return f"""You are an independent adversarial pre-execution reviewer for E2-R17 E1-B WIN-A/WIN-B negative-control FULL. You are blind to the other reviewer. This is a nuisance-control scientific tranche, not the MRW mechanism experiment. Even PASS cannot authorize MRW, paper claims, frontend promotion, or submission.

Reviewer endpoint: {model}
Exact draft SHA-256: {repair_sha}

Context: E1-A has frozen 96 exact K=8 pools and passed strong treatment-support (78/96 mixed, 12/12 exposed streams). A hosted updater runtime Pilot and a receipt-bound update->noninitial-skill->actor transition Pilot both passed. Before MRW can be interpreted causally, we must empirically show that two independent hosted executions of the exact same WIN learning treatment produce practically equivalent future frozen-skill performance.

The proposed full nuisance-control experiment has 12 independent paired stream units. Each stream contains the exact same eight E1-A K=8 pools and frozen initial skill. WIN-A and WIN-B receive the same pre-rendered V3.1 winner evidence bytes and selected-evidence scores but use independent provider calls and cloned persistent states. Each learned state is evaluated on the same 18 never-fed E1 common heldout probes at K=1. The 18 probes are repeated measurements; the independent inferential units are 12 stream pairs.

Audit the actual draft, runner and predeclared analysis. Answer:

1. UNITS/SPLIT: Does the runner bind exactly the 12 frozen e1_update_streams, eight exact content-addressed E1-A pools per stream, and exactly the 18 e1_common_heldout_probe tasks? Is there any task replacement/drop/subset path based on observed A/B outcomes?

2. IDENTICAL TREATMENT: Are WIN-A and WIN-B generated from the same initial SKILL.md, same exact pools, same winner StreamProjection and same deterministic V3.1 matched-window winner BlindedEvidenceUnits? They must differ only in hosted provider stochasticity and resulting learned state. Note the renderer computes WIN/MRW matched windows even though MRW is not executed; judge whether this compromises A/B identity or is a legitimate prospective freeze for the later MRW comparison.

3. ARM ORDER: Update and heldout A/B order are deterministic SHA-based functions of stream/task/arm, frozen before outcomes. Is this a reasonable way to avoid systematic A-first/B-second temporal bias without outcome-dependent randomization? Flag any hidden order-selection path.

4. RUNTIME/HANDOFF: Are updater and actor runtimes separately qualified, model identity freshly bound, update receipt/skill content-addressed, and noninitial skill accepted only when path/SHA/contract/auth receipt checks pass? Does the full runner preserve the V3.1 arm-blinded selected-evidence score semantics?

5. BUDGET/RESUME: Each learned state has its own contract/auth-bound SQLite ledger capped at 190 calls: exact 10 updater calls plus 18 evaluation units each capped at 10. Across exactly 24 states the structural hard maximum is 4560; the ~2621 planning estimate must not relax it. Are completed updates/probes immediately checkpointed and SHA-revalidated on resume? Does any partial ambiguous update/evaluation fail closed and leave the global lock rather than auto-rerun? Could separate per-state ledgers permit an accidental extra state outside the frozen 24-state structure?

6. HELDOUT EVALUATION: Does each state evaluate all the same 18 probes at K=1 with the same actor/verifier/model settings? Is treating the 18 probes as repeated observations and the 12 stream pairs as independent units correct? Does the execution code avoid scientific inference until a separate analysis step?

7. STATISTICS: The predeclared nuisance endpoint is N_s=J_s(WIN-B)-J_s(WIN-A), epsilon=1/18, alpha=.05. Primary equivalence is paired TOST, implemented equivalently as the 90% paired-mean t CI lying strictly inside [-epsilon,+epsilon], with fixed t_0.95,11=1.7958848187. A deterministic 100000-resample paired-stream bootstrap (seed 1717) gives a 90% robustness CI but does not control the gate. Is this statistically correct? With n=12 and a narrow margin it is intentionally strict; state whether failure should be HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY rather than a mechanism negative. Check that nonsignificance is never treated as equivalence.

8. OUTCOME SELECTION / FAILURE POLICY: The nuisance gate was frozen before these outcomes. If equivalence fails, MRW is held because the causal contrast is not interpretable; this is not evidence against R17. Is that legitimate, or does it create an outcome-selective escape hatch? Conversely, if equivalence passes, does it merely allow a separately contracted MRW experiment rather than prove the mechanism?

9. MRW SEPARATION: Confirm zero MRW provider execution, zero RB-AGG, and zero method-effect inference in this full negative-control tranche. Any MRW execution path is P0.

10. DECISION: PASS only if there is no P0/P1 blocker. Keep `mrw_execution_recommendation=HOLD` and paper_claim_authority=false even on PASS.

Return exactly one JSON object and no markdown using this schema:
{spec}
Set `draft_contract_sha256_acknowledged` exactly to the SHA above. For PASS use verdict `PASS_TO_SEPARATELY_AUTHORIZED_NEGATIVE_CONTROL_FULL` and recommendation `ALLOW_SEPARATE_FROZEN_NEGATIVE_CONTROL_AUTHORIZATION`. Keep MRW HOLD and paper authority false.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""

base.REPAIR=DRAFT;base.IDENTITY=IDENTITY;base.OUT_ROOT=OUT_ROOT
base.DOSSIER=(
 ("negative_control_draft",DRAFT),("negative_control_runner",ROOT/"scripts/run_e2_r17_e1_b_negative_control_full.py"),("negative_control_analysis",ROOT/"scripts/analyze_e2_r17_e1_b_negative_control.py"),
 ("actor_runner",ROOT/"scripts/run_e2_r17_actor_pool.py"),("updater_wrapper",ROOT/"research_pipeline/e2_r17_mindmemos_updater.py"),("updater_adapter",ROOT/"research_pipeline/e2_r17_mindmemos_ark_adapter.py"),("renderer",ROOT/"research_pipeline/e2_r17_evidence_window_v2.py"),("provider_budget",ROOT/"research_pipeline/e2_r17_provider_budget.py"),
 ("e1_a_support",ROOT/"generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json"),("provider_runtime_adjudication",ROOT/"generated/e2-r17-v31-provider-runtime-pilot-v2-adjudication-20260829.json"),("transition_adjudication",ROOT/"generated/e2-r17-e1-b-transition-runtime-pilot-adjudication-20260829.json"),("failure_registry",ROOT/"generated/e2-r17-failure-differential-registry-v3-20260829.json"),
 ("fresh_identity_adjudication",ROOT/"generated/e2-r17-e1-b-negative-control-model-identity-adjudication-20260829.json"),("fresh_identity_qualification",IDENTITY),("split_manifest",Path("/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/r17_split_manifest.json"))
)
base.schema=schema;base.prompt_for=prompt_for


def main()->int:
    parser=argparse.ArgumentParser();parser.add_argument("--env-file",type=Path,required=True);parser.add_argument("--max-output-tokens",type=int,default=6500);args=parser.parse_args()
    expected=base.identity_map();bound,hashes=base.dossier();draft_sha=base.sha_file(DRAFT);base.load_env_file(args.env_file);source=base.ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/")!=base.PLAN_BASE_URL: raise RuntimeError("negative-control review refuses non-Ark-Plan route")
    client=base.ArkResponsesClient(base.ArkSettings(api_key=source.api_key,base_url=source.base_url,default_model=source.default_model,timeout_seconds=300.0,max_retries=0));OUT_ROOT.mkdir(parents=True,exist_ok=True);rows=[]
    for model in base.MODELS:
        row=base.call(client,model=model,expected_resolved=expected[model],bound=bound,hashes=hashes,repair_sha=draft_sha,max_output_tokens=args.max_output_tokens);base.atomic_json(OUT_ROOT/f"{base.slug(model)}.json",row);rows.append(row)
    completed=[r for r in rows if r.get("status")=="COMPLETED"]
    allow=len(completed)==len(rows) and all(r.get("review",{}).get("verdict")=="PASS_TO_SEPARATELY_AUTHORIZED_NEGATIVE_CONTROL_FULL" and r.get("review",{}).get("negative_control_execution_recommendation")=="ALLOW_SEPARATE_FROZEN_NEGATIVE_CONTROL_AUTHORIZATION" and r.get("review",{}).get("mrw_execution_recommendation")=="HOLD" and r.get("review",{}).get("paper_claim_authority") is False and not r.get("review",{}).get("remaining_blockers") for r in completed)
    summary={"schema_version":"1.0","artifact_type":"e2-r17-e1-b-negative-control-dual-review","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"draft_contract_sha256":draft_sha,"statuses":{r['requested_model']:r.get('status') for r in rows},"resolved_models":{r['requested_model']:r.get('resolved_model') for r in rows},"verdicts":{r['requested_model']:r.get('review',{}).get('verdict') for r in completed},"all_allow_separate_negative_control_authorization":allow,"independent":True,"exposed_to_other_review":False,"scientific_authority":False,"mrw_authority":False,"paper_claim_authority":False}
    base.atomic_json(OUT_ROOT/"summary.json",summary);print(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True));return 0 if len(completed)==len(rows) else 2

if __name__=="__main__": raise SystemExit(main())
