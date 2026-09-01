#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_e2_r17_experiment_plan_v2_review as base

base.PLAN_PATH = ROOT / "generated/e2-r17-experiment-plan-v3-20260828.json"
base.IDENTITY_PATH = ROOT / "generated/e2-r17-experiment-plan-v3-model-identity-qualification-20260828.json"
base.OUT_ROOT = ROOT / "generated/e2-r17-experiment-plan-v3-review-20260828"
base.DOSSIER_PATHS = (
    base.PLAN_PATH,
    ROOT / "consultations/e2-r17-experiment-plan-v3-20260828.md",
    ROOT / "consultations/e2-r17-v2-review-adjudication-20260828.md",
    ROOT / "generated/e2-r17-experiment-plan-v2-review-20260828/deepseek-v4-pro.json",
    ROOT / "generated/e2-r17-experiment-plan-v2-review-20260828/kimi-k3.json",
    ROOT / "generated/e2-r17-theory-correction-mixed-pool-20260828.json",
    ROOT / "consultations/e2-r17-published-baseline-audit-v2-20260828.md",
    ROOT / "generated/e2-r17-published-baseline-audit-v2-20260828.json",
    ROOT / "research_pipeline/e2_r17_evidence_window.py",
    ROOT / "research_pipeline/e2_r17_search_projection_theory.py",
    ROOT / "research_pipeline/e2_r17_search_projection_runner.py",
    ROOT / "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
    base.IDENTITY_PATH,
)


def schema() -> dict[str, Any]:
    return {
        "plan_sha256_acknowledged": "",
        "verdict": "PASS_TO_OUTCOME_BLIND_RUNTIME_PILOT|REVISE_V3_BEFORE_PILOT|STOP_PROGRAM",
        "v2_p0_repairs_complete": False,
        "mixed_support_gate_assessment": "",
        "matched_window_renderer_assessment": "",
        "updater_stochasticity_control_assessment": "",
        "primary_statistics_and_power_assessment": "",
        "reasoningbank_collision_assessment": "",
        "published_baseline_and_two_lane_assessment": "",
        "claim_scope_assessment": "",
        "runtime_pilot_scope_assessment": "",
        "checkpoint_and_budget_assessment": "",
        "remaining_blockers": [
            {"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_repair": ""}
        ],
        "nonblocking_notes": [""],
        "runtime_pilot_recommendation": "ALLOW_OUTCOME_BLIND_RUNTIME_PILOT|HOLD|STOP",
        "e1_a_recommendation": "HOLD_UNTIL_SEPARATE_IMMUTABLE_CONTRACT|STOP",
        "e1_b_recommendation": "HOLD_UNTIL_SUPPORT_GATE_AND_SEPARATE_CONTRACT|STOP",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, plan_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent final pre-Pilot design reviewer for E2-R17 / Compute Shielding. You are blind to the other reviewer. This consultation has zero scientific-experiment, GPU, paper-promotion, frontend, or submission authority.

Requested reviewer endpoint: {model}
Exact Experiment Plan V3 SHA-256: {plan_sha}

V2 was independently reviewed by DeepSeek and Kimi and both returned REVISE before Pilot. V3 claims to repair the verdict-changing issues before any E1 updater outcome. Audit the actual bound artifacts and code, not the authors' assertion that they are fixed.

Published novelty threat: ReasoningBank/MaTTS (ICLR 2026) already learns memory from successful and failed trajectories generated with test-time scaling. E2-R17 survives only if exact-same-pool projection censoring and its causal/regime consequences are genuinely more specific than that known result.

The proposed V3 chain is:
1. theory distinguishes rescue censoring from mixed-pool treatment support;
2. E1-A freezes 96 exact K=8 pools before any updater call;
3. hard support gate is >=24/96 mixed AND >=8/12 streams with >=2 mixed each, with no waivers/replacement;
4. family coverage is now a separate generalization qualification, not a pooled-identifiability requirement;
5. WIN/MRW source evidence is token matched with a frozen tiktoken==0.11.0 cl100k_base renderer, cap 3072, pair budget=min(cap,left,right), 1/3 head + 2/3 tail;
6. WIN-A vs byte-identical WIN-B is an updater stochasticity negative control; unspecified first-party updater temperature is forced to 0.0;
7. MRW vs WIN-A is primary; ReasoningBank-style same-pool aggregation is a predeclared secondary collision arm that runs regardless of MRW GO/HOLD after semantic Pilot;
8. equivalence uses paired TOST alpha=.05 and +/-1/18 margin; nonsignificant superiority without equivalence is HOLD, not STOP;
9. source-faithful baseline reproduction and unified rerun stay separate;
10. this review can at most permit an outcome-blind runtime/mechanical Pilot. It cannot authorize E1-A pool generation or E1-B updater outcomes.

Audit these exact questions:
- Did V3 fully repair the V2 >=1-vs->=2 stream inconsistency, and are all support thresholds hard/non-waivable before outcomes?
- Is separating >=4/6 family coverage from pooled identifiability scientifically correct?
- Does the frozen matched-window renderer eliminate the evidence-length confound without creating a new arm-specific budget advantage? Is fixing the dependency/version before Pilot sufficient?
- Is the 1/3 head + 2/3 tail rule acceptable as a precommitted renderer, or is there a P0 semantic problem that makes the primary treatment uninterpretable?
- Does WIN-A/WIN-B plus forced temperature=0 adequately handle hosted-updater stochasticity? Is the equivalence gate operational?
- Are paired TOST, exact 2^12 sign-flip, paired bootstrap, n=12 unit definition, and explicit d~0.766 power limitation coherent?
- Does the always-predeclared RB-AGG collision arm prevent the simple claim from collapsing into ReasoningBank? Is labeling it 'ReasoningBank-style' rather than source-faithful correct?
- Is the interpretation table safe against post-hoc story rescue if MRW is null but RB-AGG is positive?
- Is the two-lane published-baseline design honest under the current credential blocker?
- Are WebArena/AppWorld deferred until E1 GO and are source-faithful scores prohibited from entering unified rankings?
- Does V3 prevent an E1-only result from being promoted into a prospective compute-shielding regime law before E3?
- Is the proposed runtime Pilot genuinely outcome-blind and mechanical? Name any specific check that would leak scientific effectiveness into method/model selection.
- Are SHA revalidation, missing-unit resume, retry=0, and pre-Full budget measurement sufficient?

Return exactly one JSON object and no markdown using this schema:
{spec}

Set plan_sha256_acknowledged exactly to the SHA above. Keep paper_claim_authority false. A PASS only means a separate zero-effect-selection runtime Pilot may be contracted; E1-A and E1-B remain HOLD pending their own contracts.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


base.schema = schema
base.prompt_for = prompt_for

if __name__ == "__main__":
    raise SystemExit(base.main())
