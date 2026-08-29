from __future__ import annotations
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.ark_provider import ArkResponseStateError,ArkResponsesClient,ArkSettings
from research_pipeline.config import load_env_file
AUTH=HERE/'c1-scmb-human-authorization-20260829.json'; OUT=HERE/'c1-scmb-provider-support-20260829.json'; ENV=Path('/home/wyt/code/agent-self-evolution-observatory/.env')
MODEL='doubao-seed-2.0-mini'; RESOLVED='doubao-seed-2-0-mini-260215'; PROMPT='Non-scientific service probe. Reply exactly: SCMB READY'
def shat(s):return hashlib.sha256(s.encode()).hexdigest()
def dump(o):OUT.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def main():
 a=json.load(open(AUTH)); assert a['authorized']['one_provider_model_support_requalification']; load_env_file(ENV);raw=ArkSettings.from_env(); settings=ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=180,max_retries=0); client=ArkResponsesClient(settings)
 base={'schema_version':'1.0','artifact_kind':'C1_SCMB_PROVIDER_SUPPORT','paper_id':a['paper_id'],'experiment_id':a['experiment_id'],'generated_at':datetime.now(timezone.utc).isoformat(),'execution_base':subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip(),'git_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'probe_is_scientific':False,'prompt_sha256':shat(PROMPT),'requested_model':MODEL,'expected_resolved':RESOLVED,'provider':settings.safe_summary()}
 try:
  r=client.respond(PROMPT,model=MODEL,max_output_tokens=32,temperature=0.0,thinking='disabled',store=True,allow_thinking_compatibility_fallback=False);t=str(r.get('text') or '')
  checks={'text':bool(t.strip()),'requested':r.get('requested_model')==MODEL,'resolved':r.get('resolved_model')==RESOLVED,'no_fallback':r.get('thinking_compatibility_fallback') is False,'status':bool(r.get('status'))}
  o={**base,'status':'SUPPORT_PASS' if all(checks.values()) else 'SUPPORT_HOLD','checks':checks,'response':{'response_id':r.get('response_id'),'status':r.get('status'),'resolved_model':r.get('resolved_model'),'text_sha256':shat(t),'usage':r.get('usage') or {}},'provider_posts':1,'scientific_outcomes':0}
 except Exception as e:o={**base,'status':'SUPPORT_HOLD','failure':{'type':type(e).__name__,'message':str(e)[:1200]},'provider_posts':1,'scientific_outcomes':0}
 dump(o);print(json.dumps({'status':o['status'],'resolved':(o.get('response') or {}).get('resolved_model'),'provider_posts':o['provider_posts']}));return 0 if o['status']=='SUPPORT_PASS' else 2
if __name__=='__main__':raise SystemExit(main())
