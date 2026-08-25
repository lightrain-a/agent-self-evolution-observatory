from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponsesClient, ArkSettings, ArkResponseStateError
from research_pipeline.config import load_env_file

ENV = Path('/home/wyt/code/agent-self-evolution-observatory/.env')
DRAFT = ROOT / 'paper_drafts/stri-r2-mechanism-20260825/body.tex'
STORY = ROOT / 'paper_drafts/stri-r2-mechanism-20260825/STORYBOARD.md'
GATE = ROOT / 'generated/asset-first-stri-r2-manuscript-gate-20260825.json'
SYNTH = ROOT / 'generated/asset-first-stri-r2-paper-design-synthesis-20260825.json'
P0 = ROOT / 'generated/asset-first-stri-r2-credit-fragmentation-result-20260825.json'
P1 = ROOT / 'generated/asset-first-stri-r2-credit-fragmentation-phase-result-20260825.json'
P2 = ROOT / 'generated/asset-first-stri-r2-selection-credit-decomposition-result-20260825.json'
PREV = ROOT / 'generated/asset-first-stri-r2-natural-prevalence-qualification-20260825.json'
SECOND = ROOT / 'generated/asset-first-stri-r2-second-system-credit-partition-20260825.json'
OUT = ROOT / 'generated/stri-r2-mechanism-redesign-debate-20260825/round5-kimi-draft-review.json'


def load(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))


def compact_result(p: Path) -> dict:
    x = load(p)
    return {k: x.get(k) for k in ('decision','status','pass_gate','headline','mechanism_decomposition','claim_boundary','next_gate') if k in x}


def schema():
    props = {
        'summary_score_1_to_10': {'type':'integer','minimum':1,'maximum':10},
        'is_story_materially_deeper_than_r19': {'type':'boolean'},
        'closed_loop_assessment': {'type':'string'},
        'mechanism_depth_assessment': {'type':'string'},
        'strongest_remaining_reduction_attack': {'type':'string'},
        'strongest_remaining_reviewer_objection': {'type':'string'},
        'is_2x2_intervention_actually_decisive': {'type':'boolean'},
        'is_phase_law_scientifically_useful_or_decorative': {'type':'string'},
        'cross_system_evidence_assessment': {'type':'string'},
        'natural_prevalence_risk': {'type':'string'},
        'behavior_boundary_assessment': {'type':'string'},
        'top_three_repairs': {'type':'array','minItems':3,'maxItems':3,'items':{'type':'object','properties':{
            'priority':{'type':'integer','minimum':1,'maximum':3},
            'problem':{'type':'string'},
            'repair':{'type':'string'},
            'requires_new_outcome_experiment':{'type':'boolean'},
        },'required':['priority','problem','repair','requires_new_outcome_experiment'],'additionalProperties':False}},
        'what_to_delete_or_demote': {'type':'array','items':{'type':'string'}},
        'what_to_promote': {'type':'array','items':{'type':'string'}},
        'title_assessment': {'type':'string'},
        'estimated_iclr_position_if_submitted_as_draft': {'type':'string'},
        'advisory_verdict': {'type':'string','enum':['PROMISING_MAJOR_REWRITE','READY_FOR_STRICT_REVIEW','KEEP_R19','STOP_R2']},
    }
    return [{'type':'function','name':'submit_review','description':'Return strict zero-authority paper review.','parameters':{
        'type':'object','properties':{'review':{'type':'object','properties':props,'required':list(props),'additionalProperties':False}},
        'required':['review'],'additionalProperties':False}}]


def main() -> int:
    if OUT.exists():
        raise RuntimeError(f'refuse overwrite: {OUT}')
    packet = {
        'role':'strict ICLR mechanism reviewer, not architect',
        'instructions':[
            'Do not reward added equations, modules, tables, or terminology by themselves.',
            'Attack whether credit fragmentation is truly a new stage-local mechanism rather than generic identity fragmentation or a threshold toy.',
            'Judge whether phenomenon -> mechanism -> phase law -> orthogonal intervention -> cross-system evidence -> boundaries forms a real closed loop.',
            'Preserve the natural-prevalence HOLD and AutoSkill heldout STOP; penalize any hidden overclaim.',
            'Prefer repairs that use existing frozen evidence. Mark any repair that truly requires new outcome-bearing execution.',
            'This review has zero scientific/experiment/GPU/submission authority.'
        ],
        'storyboard': STORY.read_text(encoding='utf-8'),
        'draft_body': DRAFT.read_text(encoding='utf-8'),
        'deterministic_gate': load(GATE),
        'design_synthesis': load(SYNTH),
        'evidence': {
            'p0': compact_result(P0),
            'p1': compact_result(P1),
            'p2': compact_result(P2),
            'natural_prevalence': compact_result(PREV),
            'second_system': compact_result(SECOND),
        },
        'fresh_deepseek_status':'UNAVAILABLE_NONVOTING_INVALID_SUBSCRIPTION',
    }
    prompt = 'Return exactly one submit_review function call.\n\n' + json.dumps(packet, ensure_ascii=False)
    load_env_file(ENV)
    key=os.environ.get('ARK_API_KEY','').strip()
    if not key: raise RuntimeError('ARK_API_KEY missing')
    settings=ArkSettings(api_key=key, base_url=os.environ.get('ARK_BASE_URL','https://ark.cn-beijing.volces.com/api/plan/v3').rstrip('/'), default_model='kimi-k3', timeout_seconds=300.0, max_retries=0)
    client=ArkResponsesClient(settings)
    try:
        resp=client.respond(prompt, model='kimi-k3', max_output_tokens=5000, tools=schema(), thinking='disabled', store=True, allow_thinking_compatibility_fallback=True)
        calls=[c for c in resp.get('function_calls') or [] if c.get('name')=='submit_review']
        if len(calls)!=1: raise RuntimeError(f'expected one review call, got {len(calls)}')
        review=json.loads(calls[0].get('arguments') or '{}')['review']
        row={'schema_version':'1.0','paper_id':'E1.STRI','role':'STRICT_DRAFT_REVIEW','requested_model':'kimi-k3','resolved_model':resp.get('resolved_model'),'response_id':resp.get('response_id'),'status':resp.get('status'),'usage':resp.get('usage') or {},'draft_sha256':hashlib.sha256(DRAFT.read_bytes()).hexdigest(),'gate_sha256':hashlib.sha256(GATE.read_bytes()).hexdigest(),'review':review,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False}
        row['receipt_sha256']=hashlib.sha256(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':'SUCCESS','review':review,'receipt_sha256':row['receipt_sha256']},ensure_ascii=False))
        return 0
    except (ArkResponseStateError, RuntimeError) as exc:
        receipt = exc.receipt() if isinstance(exc, ArkResponseStateError) else {'code':'ARK_AGENTPLAN_INVALID_SUBSCRIPTION' if 'InvalidSubscription' in str(exc) else 'ARK_RUNTIME_ERROR'}
        row={'schema_version':'1.0','paper_id':'E1.STRI','role':'STRICT_DRAFT_REVIEW','status':'NONVOTING_PROVIDER_STATE_FAILURE','provider_receipt':receipt,'scientific_authority':False,'experiment_authority':False,'gpu_authority':False,'submission_authority':False}
        OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row,ensure_ascii=False)); return 2

if __name__=='__main__':
    raise SystemExit(main())
