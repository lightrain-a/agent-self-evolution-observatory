#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings, extract_json_object
from research_pipeline.config import load_env_file
PDF=ROOT/'paper_drafts/e2-temporal-skill-r14-20260824/main.pdf'; OUT=ROOT/'generated/temporal-skill-r14-internal-review-v3-20260824'; MODELS=('deepseek-v4-pro','kimi-k3','minimax-m3'); BASE='https://ark.cn-beijing.volces.com/api/plan/v3'
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def prompt(text:str,model:str)->str:return f'''Act as an independent, strict ICLR 2027 reviewer. This is an INTERNAL zero-authority review, not Stanford Agentic Reviewer and not an external human review. Do not reward wording polish and do not pretend to search the web.

The manuscript is a causal/evaluation audit of reusable temporal skills. A prior internal panel criticized: pooled G0 neutrality being transported to small load-bearing strata; R being described too much like an independent temporal retriever although it deliberately reuses the exact T output; possible T-R parity driven by ceiling; EIA being compatibility-selected post-review; small endpoint counts; and novelty becoming self-defeating once callable-container advantage disappears.

The final R14 claim is narrower still. T-N alone carries the net-repair claim. T-G0 is only a same-surface operation-output contrast, and G0-N is a separate surface/placebo perturbation; the manuscript explicitly uses T-N=(T-G0)+(G0-N) and does NOT call T-G0 a pure operation effect when G0-N is nonzero. EIA is classified as net repair with surface interaction and as a compatibility-selected mechanism replication, not prospective cross-domain confirmation. R_surf is an exact-output context-materialization surface control, not a temporal-retrieval algorithm. The manuscript now reports a TOST at the prospectively frozen +/-10pp portfolio margin (both one-sided p=0.0121), paired-t/bootstrapped 95% intervals, a ~53% parametric equivalence sensitivity estimate, and explicitly leaves the n=4 strictly non-ceiling subset unresolved.

Audit whether this final logic is valid and whether the remaining evidence is sufficient for the CURRENT narrow ICLR methodological/evaluation claim. The manuscript now calls G a mechanism-misaligned stress helper rather than a fair generic baseline; treats EIA primarily as a surface-interaction/mechanism-replication case rather than confirmatory evidence; describes the TOST result only as data consistent with portfolio-average equivalence at the frozen margin under ~53% sensitivity and a ceiling-heavy portfolio; and scopes R_surf to integration-surface placement under a forced one-answer harness, not adaptive callable use. Focus on: (1) whether any attribution error remains; (2) whether any sentence still exceeds the statistics; (3) whether the methodological verdict-reversal contribution is coherent despite modest endpoint scale; and (4) whether a NEW EXPERIMENT is decision-critical to the CURRENT narrow claim. Do not demand experiments merely to support broader cross-domain, non-ceiling, multi-turn, or temporal-retrieval claims that the paper explicitly disclaims.

Return exactly one JSON object:
{{"reviewer_model":"{model}","overall_score_1_to_10":0,"recommendation":"accept|weak_accept|borderline|weak_reject|reject","confidence_1_to_5":0,"dimensions":{{"originality":0,"importance":0,"claim_support":0,"experimental_soundness":0,"clarity":0,"community_value":0,"prior_work_context":0}},"one_sentence_verdict":"","decision_critical_concerns":[{{"id":"","severity":"critical|major","claim_or_section":"","problem":"","why_it_matters":"","cheapest_decisive_repair":"paper-only|analysis-only|new-experiment|external-replication","acceptance_effect_if_repaired":""}}],"noncritical_repairs":[""],"claims_to_downgrade_or_delete":[""],"evidence_that_is_now_convincing":[""],"novelty_boundary":"","would_new_experiment_change_verdict":true,"single_highest_value_next_action":""}}
Use integer scores. At most 4 decision-critical concerns. If a concern only matters for a broader claim the manuscript explicitly disclaims, do not call it decision-critical.

MANUSCRIPT START
{text}
MANUSCRIPT END'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--models',nargs='*',default=list(MODELS));a=ap.parse_args()
 if not PDF.exists():raise SystemExit('missing R14 PDF')
 text=subprocess.check_output(['pdftotext','-f','1','-l','14',str(PDF),'-'],text=True)
 for ep in (ROOT/'.env',ROOT.parent/'agent-self-evolution-observatory'/'.env'):load_env_file(ep)
 s0=ArkSettings.from_env(required=True)
 if s0.base_url.rstrip('/')!=BASE:raise RuntimeError('Ark Plan base URL required')
 settings=ArkSettings(api_key=s0.api_key,base_url=s0.base_url,default_model=s0.default_model,timeout_seconds=240,max_retries=0);client=ArkResponsesClient(settings);OUT.mkdir(parents=True,exist_ok=True);summary=[]
 for model in a.models:
  p=prompt(text,model);row={'schema_version':'1.0','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','revision':'r14','review_kind':'INTERNAL_ICLR_PANEL_ZERO_AUTHORITY','requested_model':model,'paper_pdf_sha256':sha(PDF.read_bytes()),'prompt_sha256':sha(p.encode()),'created_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),'scientific_authority':False,'submission_authority':False}
  try:
   try:r=client.respond(p,model=model,max_output_tokens=5000,temperature=0,thinking='disabled',allow_thinking_compatibility_fallback=False)
   except ArkResponseStateError as e:
    if not e.response_id:raise
    q=client.poll_response(e.response_id,max_polls=4,interval_seconds=1.0)
    if not q.get('text'):raise RuntimeError('poll recovered no text')
    r=q|{'requested_model':model,'response_id':q.get('response_id') or e.response_id}
   raw=str(r.get('text') or '');row.update({'status':'completed','resolved_model':r.get('resolved_model'),'usage':r.get('usage') or {},'response_id_sha256':sha(str(r.get('response_id') or '').encode()),'raw_text':raw,'raw_text_sha256':sha(raw.encode())})
   try:row['review']=extract_json_object(raw);row['parse_valid']=True
   except Exception as e:row['parse_valid']=False;row['parse_error']=f'{type(e).__name__}:{e}'
  except Exception as e:row.update({'status':'failed','error':f'{type(e).__name__}:{e}','parse_valid':False})
  path=OUT/f'{model}.json';path.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');summary.append({'model':model,'status':row['status'],'resolved_model':row.get('resolved_model'),'parse_valid':row.get('parse_valid'),'score':(row.get('review') or {}).get('overall_score_1_to_10'),'recommendation':(row.get('review') or {}).get('recommendation'),'file':str(path.relative_to(ROOT)),'file_sha256':sha(path.read_bytes())});print(json.dumps(summary[-1],ensure_ascii=False))
 out={'schema_version':'1.0','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','revision':'r14','review_kind':'INTERNAL_ICLR_PANEL_ZERO_AUTHORITY','paper_pdf_sha256':sha(PDF.read_bytes()),'reviews':summary,'scientific_authority':False,'submission_authority':False};(OUT/'summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
