#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings, extract_json_object
from research_pipeline.config import load_env_file
PDF=ROOT/'downloads/E2-Temporal-Skill-r13-20260824.pdf'
OUT=ROOT/'generated/temporal-skill-r13-internal-review-20260824'
MODELS=('deepseek-v4-pro','kimi-k3','minimax-m3')
BASE='https://ark.cn-beijing.volces.com/api/plan/v3'
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def prompt(text:str,model:str)->str:
 return f'''Act as an independent, strict ICLR 2027 reviewer. This is an INTERNAL review, not Stanford Agentic Reviewer and not an external human review. Do not reward wording polish. Judge only the supplied manuscript and do not pretend to have searched the web.

The previous external review objected to: (1) generic-helper degradation masquerading as targeted benefit, (2) absence of a behavior-neutral generic control, (3) absence of an operation-matched retrieval-side baseline, (4) small/ceiling/cross-domain generality, and (5) confusion between temporal operation value and callable skill-container value.

R13 now reports fresh G0 no-op controls, a Kimi grounding downgrade, and a T-vs-operation-matched-retrieval comparison. Audit whether these actually close the identification gaps. Attack the strongest version of the paper, especially:
- whether G0 is genuinely behavior-neutral and whether A1/A2 staging avoids sequential-selection bias;
- whether R is truly same-information / operation-matched, rather than a weaker retrieval baseline;
- whether T≈R should force a narrower contribution than the manuscript currently claims;
- whether the DeepSeek/Kimi endpoint counts and bootstrap/sign tests support the exact stated claims;
- whether Kimi grounding is correctly downgraded everywhere;
- whether exact TimeSage-EV replication debt is represented honestly;
- novelty after conceding temporal retrieval and reusable-skill prior work;
- whether any decision-critical claim lacks an experiment that would change acceptance.

Return exactly one JSON object with this schema:
{{
 "reviewer_model":"{model}",
 "overall_score_1_to_10":0,
 "recommendation":"accept|weak_accept|borderline|weak_reject|reject",
 "confidence_1_to_5":0,
 "dimensions":{{"originality":0,"importance":0,"claim_support":0,"experimental_soundness":0,"clarity":0,"community_value":0,"prior_work_context":0}},
 "one_sentence_verdict":"",
 "decision_critical_concerns":[{{"id":"","severity":"critical|major","claim_or_section":"","problem":"","why_it_matters":"","cheapest_decisive_repair":"paper-only|analysis-only|new-experiment|external-replication","acceptance_effect_if_repaired":""}}],
 "noncritical_repairs":[""],
 "claims_to_downgrade_or_delete":[""],
 "evidence_that_is_now_convincing":[""],
 "novelty_boundary":"",
 "would_new_experiment_change_verdict":true,
 "single_highest_value_next_action":""
}}
Scores must be integers. Keep at most 4 decision-critical concerns and at most 5 noncritical repairs.

MANUSCRIPT START
{text}
MANUSCRIPT END'''
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--models',nargs='*',default=list(MODELS)); a=ap.parse_args()
 if not PDF.exists(): raise SystemExit(f'missing {PDF}')
 text=subprocess.check_output(['pdftotext','-f','1','-l','15',str(PDF),'-'],text=True)
 for env_path in (ROOT/'.env', ROOT.parent/'agent-self-evolution-observatory'/'.env'):
  load_env_file(env_path)
 settings0=ArkSettings.from_env(required=True)
 if settings0.base_url.rstrip('/')!=BASE: raise RuntimeError('Ark Plan base URL required')
 settings=ArkSettings(api_key=settings0.api_key,base_url=settings0.base_url,default_model=settings0.default_model,timeout_seconds=240,max_retries=0)
 OUT.mkdir(parents=True,exist_ok=True); client=ArkResponsesClient(settings); summary=[]
 for model in a.models:
  p=prompt(text,model); row={'schema_version':'1.0','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','revision':'r13','review_kind':'INTERNAL_ICLR_PANEL_ZERO_AUTHORITY','requested_model':model,'paper_pdf_sha256':sha(PDF.read_bytes()),'prompt_sha256':sha(p.encode()),'created_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),'scientific_authority':False,'submission_authority':False}
  try:
   try:r=client.respond(p,model=model,max_output_tokens=5000,temperature=0,thinking='disabled',allow_thinking_compatibility_fallback=False)
   except ArkResponseStateError as e:
    if not e.response_id: raise
    q=client.poll_response(e.response_id,max_polls=4,interval_seconds=1.0)
    if not q.get('text'): raise RuntimeError('poll recovered no text')
    r=q|{'requested_model':model,'response_id':q.get('response_id') or e.response_id}
   raw=str(r.get('text') or ''); row.update({'status':'completed','resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'response_id_sha256':sha(str(r.get('response_id') or '').encode()),'raw_text':raw,'raw_text_sha256':sha(raw.encode())})
   try:row['review']=extract_json_object(raw); row['parse_valid']=True
   except Exception as e:row['parse_valid']=False; row['parse_error']=f'{type(e).__name__}:{e}'
  except Exception as e:row.update({'status':'failed','error':f'{type(e).__name__}:{e}','parse_valid':False})
  path=OUT/f'{model}.json'; path.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); summary.append({'model':model,'status':row['status'],'resolved_model':row.get('resolved_model'),'parse_valid':row.get('parse_valid'),'score':(row.get('review') or {}).get('overall_score_1_to_10'),'recommendation':(row.get('review') or {}).get('recommendation'),'file':str(path.relative_to(ROOT)),'file_sha256':sha(path.read_bytes())}); print(json.dumps(summary[-1],ensure_ascii=False))
 out={'schema_version':'1.0','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','revision':'r13','review_kind':'INTERNAL_ICLR_PANEL_ZERO_AUTHORITY','paper_pdf_sha256':sha(PDF.read_bytes()),'reviews':summary,'scientific_authority':False,'submission_authority':False}; (OUT/'summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
