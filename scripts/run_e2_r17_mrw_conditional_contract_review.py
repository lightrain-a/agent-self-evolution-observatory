#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.ark_provider import ArkResponsesClient,ArkSettings,extract_json_object
from research_pipeline.config import load_env_file

PLAN_BASE_URL='https://ark.cn-beijing.volces.com/api/plan/v3'
MODELS=('deepseek-v4-pro','kimi-k3')
DRAFT=ROOT/'generated/e2-r17-e1-b-mrw-contemporaneous-draft-contract-20260829.json'
IDENTITY=ROOT/'generated/e2-r17-e1-b-negative-control-model-identity-adjudication-20260829.json'
OUT_ROOT=ROOT/'generated/e2-r17-mrw-conditional-contract-review-20260829'
DOSSIER=(
 ('conditional_contract',DRAFT),
 ('runner',ROOT/'scripts/run_e2_r17_e1_b_mrw_contemporaneous_full.py'),
 ('analysis',ROOT/'scripts/analyze_e2_r17_e1_b_mrw_contemporaneous.py'),
 ('preoutcome_design_review',ROOT/'generated/e2-r17-mrw-control-design-review-20260829/summary.json'),
 ('negative_control_contract',ROOT/'generated/e2-r17-e1-b-negative-control-full-contract-20260829.json'),
 ('failure_registry',ROOT/'generated/e2-r17-failure-differential-registry-v6-20260829.json'),
)

def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:return sha_bytes(p.read_bytes())
def sha_text(t:str)->str:return sha_bytes(t.encode())
def slug(v:str)->str:return re.sub(r'[^A-Za-z0-9_.-]+','-',v)
def atomic_json(p:Path,x:dict[str,Any])->None:
 p.parent.mkdir(parents=True,exist_ok=True); q=p.with_suffix(p.suffix+'.tmp'); q.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); q.replace(p)

def schema()->dict[str,Any]:
 return {
  'draft_contract_sha256_acknowledged':'',
  'verdict':'PASS_TO_CONDITIONAL_FREEZE_AFTER_NEGATIVE_CONTROL_PASS|REVISE_PREOUTCOME_CONTRACT|STOP_MRW_DESIGN',
  'contemporaneous_control_assessment':'',
  'hash_balanced_schedule_assessment':'',
  'same_pool_treatment_purity_assessment':'',
  'statistical_decision_logic_assessment':'',
  'practical_null_precedence_assessment':'',
  'missing_invalid_unit_assessment':'',
  'negative_control_gate_sequencing_assessment':'',
  'historical_win_ab_role_assessment':'',
  'runtime_budget_checkpoint_assessment':'',
  'remaining_blockers':[{'priority':'P0|P1','issue':'','exact_repair':''}],
  'nonblocking_notes':[''],
  'conditional_freeze_recommendation':'ALLOW_CONDITIONAL_DRAFT_FREEZE_ONLY|HOLD|STOP',
  'negative_control_fail_policy':'MRW_REMAINS_UNAUTHORIZED',
  'mrw_execution_authority':False,
  'paper_claim_authority':False,
  'single_sentence_verdict':''
 }

def dossier()->str:
 chunks=[]
 for label,p in DOSSIER:
  raw=p.read_text(encoding='utf-8'); chunks.append(f'\n===== {label} | {p} | sha256={sha_file(p)} =====\n{raw}\n')
 return ''.join(chunks)

def prompt(model:str,bound:str,draft_sha:str)->str:
 spec=json.dumps(schema(),ensure_ascii=False,indent=2)
 return f'''You are an independent pre-outcome causal/statistical reviewer for E2-R17. You are blind to the other reviewer. The WIN-A/WIN-B negative-control full run is still executing and its outcome is not available to this review. This review has zero MRW execution, paper, frontend, or submission authority.

Reviewer endpoint: {model}
Conditional MRW draft SHA-256: {draft_sha}

Audit the exact conditional contract, runner, analysis, prior pre-outcome control-design review, and failure-registry rules. The design is allowed to become executable only if the separate preregistered negative-control equivalence adjudication later returns PASS. If the negative control fails, MRW must remain unauthorized.

Key intended design:
- fresh contemporaneous WIN-C vs MRW, 12 paired streams;
- same initial skill, same exact 8 E1-A pools per stream, same served acting winner, same updater/executor/probes/runtimes/budgets;
- V3.1 arm-blinded exact matched evidence; on nonmixed pools MRW evidence equals WIN; on mixed pools MRW exposes deterministic first failed nonwinner;
- hash-balanced update order and per-probe evaluation order with fixed salts;
- historical WIN-A/WIN-B secondary bridge/stability evidence only, excluded from primary estimand;
- primary D_s=J_s(MRW)-J_s(WIN-C), exact one-sided sign-flip alpha=.05 plus 95% paired bootstrap lower>0;
- practical-null TOST epsilon=1/18 has precedence: a TOST-equivalent small positive effect is STOP_PRACTICALLY_NULL, not GO;
- harmful exact negative sign-flip -> STOP; otherwise HOLD;
- no stream/task dropping, imputation, replacement, or auto-rerun after ambiguous calls.

Check especially whether the runner actually implements the treatment pairing and whether the analysis decision rules are internally coherent on small-but-significant effects. Check that the conditional freeze policy permits only gate SHA, fresh model identity, review metadata, and status changes after the negative-control outcome, not scientific redesign.

Return exactly one JSON object and no markdown using this schema:
{spec}
Set draft_contract_sha256_acknowledged exactly. Keep negative_control_fail_policy=MRW_REMAINS_UNAUTHORIZED, mrw_execution_authority=false, paper_claim_authority=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
'''

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('--env-file',type=Path,required=True); ap.add_argument('--max-output-tokens',type=int,default=4500); args=ap.parse_args()
 ident=json.loads(IDENTITY.read_text(encoding='utf-8'))
 if ident.get('status')!='PASS_CURRENT_REVIEW_TRANCHE': raise RuntimeError('review identity not passing')
 expected={k:str(v['resolved']) for k,v in ident['requested_and_resolved'].items() if k in MODELS}
 load_env_file(args.env_file); src=ArkSettings.from_env(required=True)
 if src.base_url.rstrip('/')!=PLAN_BASE_URL: raise RuntimeError('review refuses non-Ark-Plan route')
 client=ArkResponsesClient(ArkSettings(api_key=src.api_key,base_url=src.base_url,default_model=src.default_model,timeout_seconds=300.0,max_retries=0))
 bound=dossier(); draft_sha=sha_file(DRAFT); required=set(schema()); OUT_ROOT.mkdir(parents=True,exist_ok=True); rows=[]
 for model in MODELS:
  pr=prompt(model,bound,draft_sha); res=client.respond(pr,model=model,max_output_tokens=args.max_output_tokens,temperature=0,thinking='disabled',allow_thinking_compatibility_fallback=False)
  raw=str(res.get('text') or ''); review=extract_json_object(raw); resolved=str(res.get('resolved_model') or '')
  missing=sorted(required-set(review))
  if review.get('draft_contract_sha256_acknowledged')!=draft_sha: missing.append('draft_contract_sha256_acknowledged_exact')
  if review.get('negative_control_fail_policy')!='MRW_REMAINS_UNAUTHORIZED': missing.append('negative_control_fail_policy')
  if review.get('mrw_execution_authority') is not False: missing.append('mrw_execution_authority_false')
  if review.get('paper_claim_authority') is not False: missing.append('paper_claim_authority_false')
  row={'schema_version':'1.0','artifact_type':'e2-r17-mrw-conditional-contract-independent-review','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'requested_model':model,'resolved_model':resolved,'expected_resolved_model':expected[model],'resolved_model_matches_qualification':resolved==expected[model],'draft_contract_sha256':draft_sha,'provider_retry_limit':0,'thinking_requested':'disabled','raw_text_sha256':sha_text(raw),'response_id_sha256':sha_text(str(res.get('response_id') or '')),'usage':res.get('usage') or {},'review':review,'missing_required_fields':missing,'status':'COMPLETED' if not missing and resolved==expected[model] else 'FAIL_SCHEMA_OR_IDENTITY','independent':True,'exposed_to_other_review':False,'scientific_authority':False,'mrw_execution_authority':False,'paper_claim_authority':False}
  atomic_json(OUT_ROOT/f'{slug(model)}.json',row); rows.append(row)
 completed=[r for r in rows if r['status']=='COMPLETED']
 allow=len(completed)==2 and all(r['review'].get('verdict')=='PASS_TO_CONDITIONAL_FREEZE_AFTER_NEGATIVE_CONTROL_PASS' and r['review'].get('conditional_freeze_recommendation')=='ALLOW_CONDITIONAL_DRAFT_FREEZE_ONLY' and not r['review'].get('remaining_blockers') for r in completed)
 summary={'schema_version':'1.0','artifact_type':'e2-r17-mrw-conditional-contract-dual-review','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'draft_contract_sha256':draft_sha,'statuses':{r['requested_model']:r['status'] for r in rows},'verdicts':{r['requested_model']:r.get('review',{}).get('verdict') for r in completed},'conditional_freeze_recommendations':{r['requested_model']:r.get('review',{}).get('conditional_freeze_recommendation') for r in completed},'all_allow_conditional_freeze_after_negative_control_pass':allow,'negative_control_outcome_used':False,'mrw_execution_authority':False,'paper_claim_authority':False}
 atomic_json(OUT_ROOT/'summary.json',summary); print(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if len(completed)==2 else 2
if __name__=='__main__': raise SystemExit(main())
