from __future__ import annotations
import argparse,ast,hashlib,json,math,os,re,subprocess,sys,time,unicodedata,urllib.parse,urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

CANDIDATE_ID='SHADOW-P06-C01'
CONTRACT_SHA='abab137697817d2716bc2823e6bad7e3e0da16d8654d146dc775443c24f3cd47'
PLAN_SHA='829601282dbf00f11f102a88d3bb64a2487b68c3270fc1c89f7259b671c4b9d2'
SOURCE_SHA='4ffadad60b18cd7ede864155f3e8a366fe4deec2189b3d0a25691b7df4b839e8'
SOURCE_COMMIT='d73f0dc0be7e0a2ff6a403d5fe65fcd96461f384'
RAW_ROOT=f'https://raw.githubusercontent.com/mayubo2333/MMLongBench-Doc/{SOURCE_COMMIT}/data/pdfs'
DEFAULT_MODEL=Path('/root/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct/snapshots/a09a35458c702b33eeacc393d103063234e8bc28')
POLICIES=('negative_evidence_baseline','naive_summary','evidence_gap_aware','coverage_certified')
ACTIONS={'ANSWER','RETRIEVE_MORE','ABSTAIN','CONTINUE'}
MAX_INPUT_TOKENS=4096; MAX_NEW_TOKENS=160; PAGE_CHARS=3600; NOTE_CHARS=1200

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def htext(x:str)->str:return hashlib.sha256(x.encode()).hexdigest()
def load(path:Path):return json.loads(path.read_text(encoding='utf-8'))
def lit(x):
    if isinstance(x,list):return x
    try:y=ast.literal_eval(str(x or '[]'))
    except (ValueError,SyntaxError):return []
    return list(y) if isinstance(y,(list,tuple)) else []

def validate(plan_path:Path,samples_path:Path):
    if sha(plan_path)!=PLAN_SHA:raise ValueError('plan-sha-mismatch')
    if sha(samples_path)!=SOURCE_SHA:raise ValueError('source-sha-mismatch')
    p,s=load(plan_path),load(samples_path)
    if p.get('candidate_id')!=CANDIDATE_ID or p.get('contract_sha256')!=CONTRACT_SHA:raise ValueError('contract-mismatch')
    if len(p.get('units') or [])!=96 or not isinstance(s,list) or len(s)!=1082:raise ValueError('cardinality-mismatch')
    seen=set()
    for u in p['units']:
        i=int(u['sample_index']);r=s[i]
        if i in seen:
            raise ValueError('duplicate-sample')
        seen.add(i)
        if u['doc_id']!=r['doc_id'] or r.get('filename')!=r['doc_id']+'.pdf' or u['question_sha256']!=htext(r['question']) or u['answer_sha256']!=htext(str(r['answer'])):
            raise ValueError('unit-identity-mismatch')
    return p,s

def toks(x:str):return re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKC',x).casefold())
def bm25(q:str,pages:list[str])->list[int]:
    qq=toks(q);docs=[toks(x) for x in pages];n=len(docs);avg=sum(map(len,docs))/max(1,n);df=Counter()
    for d in docs:df.update(set(d))
    scored=[]
    for i,d in enumerate(docs,1):
        tf=Counter(d);dl=len(d);v=0.0
        for t in qq:
            f=tf.get(t,0)
            if f:v+=math.log(1+(n-df[t]+.5)/(df[t]+.5))*f*2.5/(f+1.5*(.25+.75*dl/max(1,avg)))
        scored.append((v,i))
    return [i for _,i in sorted(scored,key=lambda z:(-z[0],z[1]))]

def fetch_pdfs(plan:dict,pdf_dir:Path):
    pdf_dir.mkdir(parents=True,exist_ok=True);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
    for doc in sorted({u['doc_id'] for u in plan['units']}):
        dst=pdf_dir/(doc+'.pdf')
        if not(dst.is_file() and dst.stat().st_size>1024):
            url=RAW_ROOT+'/'+urllib.parse.quote(doc+'.pdf');last=None
            for k in range(2):
                try:
                    with opener.open(urllib.request.Request(url,headers={'User-Agent':'agent-self-evolution-observatory'}),timeout=30) as r:data=r.read()
                    if len(data)<=1024 or not data.startswith(b'%PDF'):raise ValueError('not-pdf')
                    tmp=Path(str(dst)+'.tmp');tmp.write_bytes(data);os.replace(tmp,dst);last=None;break
                except Exception as e:last=e;time.sleep(1 if k==0 else 0)
            if last:raise RuntimeError(f'pdf-fetch:{doc}:{last}')
        rows.append({'doc_id':doc,'bytes':dst.stat().st_size,'sha256':sha(dst)})
    return rows

def pages_of(pdf:Path,cache_dir:Path)->list[str]:
    cache_dir.mkdir(parents=True,exist_ok=True);psha=sha(pdf);cache=cache_dir/(psha+'.json')
    if cache.is_file():
        d=load(cache)
        if d.get('pdf_sha256')==psha:return [str(x) for x in d['pages']]
    r=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True)
    if r.returncode:raise RuntimeError('pdftotext:'+r.stderr.decode('utf-8','ignore')[:300])
    pages=[x.replace('\x00','').strip() for x in r.stdout.decode('utf-8','ignore').split('\f')]
    if pages and not pages[-1]:pages.pop()
    if not pages:raise RuntimeError('empty-pdf-text:'+pdf.name)
    cache.write_text(json.dumps({'pdf_sha256':psha,'pages':pages},ensure_ascii=False)+'\n');return pages

def raw_block(pages:list[str],ids:list[int])->str:
    return '\n\n'.join(f'[PAGE {i}]\n{pages[i-1][:PAGE_CHARS]}' for i in ids)
def extractive(pages:list[str],ids:list[int])->str:
    n=max(220,NOTE_CHARS//max(1,len(ids)))
    return ' | '.join(' '.join(pages[i-1].split())[:n] for i in ids)[:NOTE_CHARS]
def note(policy:str,pages:list[str],ids:list[int])->str:
    base=extractive(pages,ids);total=len(pages);unchecked=max(0,total-len(set(ids)));sid=','.join(map(str,ids))
    if policy=='negative_evidence_baseline':return 'Visible evidence may be incomplete. Use only visible pages. If insufficient, request more evidence or abstain.'
    if policy=='naive_summary':return 'Extractive note from visible text: '+base
    if policy=='evidence_gap_aware':return f'Extractive note: {base}\nVisible page ids: {sid}. Document length: {total}. Unchecked pages: {unchecked}. Do not assume unchecked pages contain the answer.'
    ratio=len(set(ids))/max(1,total);cert='FULL' if unchecked==0 else 'PARTIAL'
    return f'Extractive note: {base}\nVisible page ids: {sid}. Document length: {total}. Coverage: {len(set(ids))}/{total}={ratio:.3f}. Unchecked pages: {unchecked}. Coverage certificate: {cert}. Certificate is page coverage only, never answerability.'

def prompt(question:str,pages:list[str],ids:list[int],policy:str,step:int):
    raw=raw_block(pages,ids)
    common=f'You are a document agent under selective page access. Use no outside knowledge. The document has {len(pages)} pages.\n\nQUESTION:\n{question}\n\nRAW VISIBLE PAGES:\n{raw}\n'
    tail='\n\nPERSISTENT NOTE REPRESENTATION:\n'+note(policy,pages,ids)+f'\n\nChoose exactly one action: ANSWER, RETRIEVE_MORE, ABSTAIN, CONTINUE. Return one JSON object only with keys action and answer. For non-ANSWER set answer to empty string. Decision step {step} of 2.'
    return common+tail,htext(common)

def parse(text:str):
    m=re.search(r'\{.*?\}',text,re.S)
    try:o=json.loads(m.group(0) if m else '')
    except Exception:
        a=re.search(r'\b(ANSWER|RETRIEVE_MORE|ABSTAIN|CONTINUE)\b',text.upper())
        return {'valid':bool(a),'action':a.group(1) if a else '','answer':'','raw':text,'salvaged':bool(a)}
    a=str(o.get('action') or '').strip().upper();ans=str(o.get('answer') or '').strip()[:500]
    return {'valid':a in ACTIONS,'action':a,'answer':ans if a=='ANSWER' else '','raw':text,'salvaged':False}
def norm(x):return ' '.join(re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKC',str(x or '')).casefold()))
def exact(pred,gold):return bool(pred.strip()) and norm(pred)==norm(gold)
def mcnemar(left,right):
    b=sum(a==0 and c==1 for a,c in zip(left,right));c=sum(a==1 and c==0 for a,c in zip(left,right));n=b+c
    if not n:return 1.0,b,c
    return min(1.0,2*sum(math.comb(n,k) for k in range(min(b,c)+1))/(2**n)),b,c

def probe(plan_path:Path,samples_path:Path,model_path:Path):
    plan,_=validate(plan_path,samples_path)
    synthetic_pages=[
        "alpha unrelated context",
        "target fact cobalt supporting text",
        "appendix numbers",
        "administrative end",
    ]
    ranking=bm25("what is target fact cobalt",synthetic_pages)
    raw_hashes=[]
    rendered={}
    for policy in POLICIES:
        rendered_prompt,raw_hash=prompt("what is target fact cobalt",synthetic_pages,ranking[:3],policy,1)
        rendered[policy]=rendered_prompt
        raw_hashes.append(raw_hash)
    forbidden_hits={}
    for policy,rendered_prompt in rendered.items():
        lowered=rendered_prompt.lower()
        hits=[]
        for literal in ("not answerable","evidence_pages"):
            if literal in lowered:
                hits.append(literal)
        forbidden_hits[policy]=hits
    parser_cases=[
        parse('{"action":"RETRIEVE_MORE","answer":""}'),
        parse('{"action":"ANSWER","answer":"cobalt"}'),
        parse("ABSTAIN"),
    ]
    shards=len(list(model_path.glob("model-*.safetensors"))) if model_path.is_dir() else 0
    budget=plan["budget"]
    checks={
        "plan_hash":sha(plan_path)==PLAN_SHA,
        "source_hash":sha(samples_path)==SOURCE_SHA,
        "bm25_no_truth_dependency":ranking[0]==2,
        "raw_lock":len(set(raw_hashes))==1,
        "no_truth_literal_leak":not any(forbidden_hits.values()),
        "parser":all(case["valid"] for case in parser_cases),
        "model_snapshot":model_path.is_dir() and shards>=4 and (model_path/"config.json").is_file(),
        "pdftotext":subprocess.run(["sh","-lc","command -v pdftotext >/dev/null"]).returncode==0,
        "units_budget":plan["scope"]["units"]<=budget["max_units"],
        "batch_budget":budget["planned_worst_case_total_batches"]<=budget["max_model_calls"],
    }
    return {
        "candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA,
        "plan_sha256":sha(plan_path),"source_sha256":sha(samples_path),
        "model_path":str(model_path),"model_shards":shards,
        "truth_literal_hits":forbidden_hits,"checks":checks,
        "passed":all(checks.values()),"scientific_authority":False,
    }
def manifest(plan_path:Path,samples_path:Path,model_path:Path,out:Path):
    pr=probe(plan_path,samples_path,model_path);payload={'schema_version':'1.0-private','candidate_id':CANDIDATE_ID,'contract_sha256':CONTRACT_SHA,'plan_sha256':sha(plan_path),'source_sha256':sha(samples_path),'source_commit':SOURCE_COMMIT,'runtime_code_sha256':sha(Path(__file__).resolve()),'python_runtime':sys.version,'model_path':str(model_path),'probe':pr,'sandboxed':True,'budget_feasible':pr['checks']['units_budget'] and pr['checks']['batch_budget'],'scientific_authority':False}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');return {**payload,'harness_manifest_sha256':sha(out)}

def load_model(path:Path):
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    tok=AutoTokenizer.from_pretrained(str(path),local_files_only=True,trust_remote_code=True);tok.pad_token_id=tok.pad_token_id or tok.eos_token_id;tok.padding_side='left'
    model=AutoModelForCausalLM.from_pretrained(str(path),local_files_only=True,trust_remote_code=True,torch_dtype=torch.bfloat16,low_cpu_mem_usage=True).cuda().eval();return torch,tok,model

def gen(torch,tok,model,prompts):
    enc=tok(prompts,return_tensors='pt',padding=True,truncation=True,max_length=MAX_INPUT_TOKENS);enc={k:v.cuda() for k,v in enc.items()};w=enc['input_ids'].shape[1]
    with torch.inference_mode():out=model.generate(**enc,do_sample=False,max_new_tokens=MAX_NEW_TOKENS,use_cache=True,pad_token_id=tok.pad_token_id)
    return [tok.decode(x[w:],skip_special_tokens=True) for x in out]

def run(plan_path:Path,samples_path:Path,pdf_dir:Path,cache_dir:Path,model_path:Path,out:Path,max_units:int|None=None):
    plan,samples=validate(plan_path,samples_path);pdf_manifest=fetch_pdfs(plan,pdf_dir);torch,tok,model=load_model(model_path);start=time.monotonic();gpu=0.0;calls=0;rows=[];docs={};units=plan['units'][:max_units or len(plan['units'])];raw=out.with_suffix('.jsonl');out.parent.mkdir(parents=True,exist_ok=True)
    maxwall=plan['budget']['max_wall_minutes']*60;maxgpu=plan['budget']['max_gpu_hours']*3600;maxcalls=plan['budget']['max_model_calls']
    with raw.open('w',encoding='utf-8') as fh:
      for ordinal,u in enumerate(units,1):
        if time.monotonic()-start>maxwall or gpu>=maxgpu or calls>=maxcalls:break
        src=samples[u['sample_index']];doc=u['doc_id'];pages=docs.get(doc)
        if pages is None:pages=pages_of(pdf_dir/doc,cache_dir);docs[doc]=pages
        ranking=bm25(src['question'],pages);ids=ranking[:min(3,len(ranking))];prompts=[];rhs=[]
        for pol in POLICIES:q,rh=prompt(src['question'],pages,ids,pol,1);prompts.append(q);rhs.append(rh)
        if len(set(rhs))!=1:raise RuntimeError('raw-lock-violation')
        t=time.monotonic();texts=gen(torch,tok,model,prompts);torch.cuda.synchronize();gpu+=time.monotonic()-t;calls+=1;first={p:parse(x) for p,x in zip(POLICIES,texts)}
        active=[p for p in POLICIES if first[p]['valid'] and first[p]['action'] in {'RETRIEVE_MORE','CONTINUE'}];second={}
        if active and calls<maxcalls and gpu<maxgpu and time.monotonic()-start<=maxwall:
            ids2=ranking[:min(6,len(ranking))];p2=[prompt(src['question'],pages,ids2,p,2)[0] for p in active];t=time.monotonic();txt2=gen(torch,tok,model,p2);torch.cuda.synchronize();gpu+=time.monotonic()-t;calls+=1;second={p:parse(x) for p,x in zip(active,txt2)}
        ep=[int(x) for x in lit(src.get('evidence_pages')) if isinstance(x,int) or str(x).isdigit()];gap=u['class']=='answerable' and not set(ep).issubset(ids);covered=u['class']=='answerable' and set(ep).issubset(ids)
        for pol in POLICIES:
            a=first[pol];b=second.get(pol);final=b if b and b['valid'] else a
            row={'unit_id':u['unit_id'],'sample_index':u['sample_index'],'class':u['class'],'doc_id':doc,'doc_type':u['doc_type'],'policy':pol,'question_sha256':u['question_sha256'],'raw_observation_sha256':rhs[0],'initial_page_ids':ids,'document_pages':len(pages),'gap_stratum':gap,'covered_stratum':covered,'first_valid':a['valid'],'first_action':a['action'],'first_answer':a['answer'],'second_valid':None if b is None else b['valid'],'second_action':'' if b is None else b['action'],'final_action':final['action'],'final_answer':final['answer'],'primary_state':int(a['valid'] and a['action'] in {'RETRIEVE_MORE','ABSTAIN'}),'exact_correct':bool(final['valid'] and final['action']=='ANSWER' and exact(final['answer'],src['answer'])),'false_answer_unanswerable':bool(u['class']=='unanswerable' and final['valid'] and final['action']=='ANSWER'),'parser_valid':bool(a['valid'] and (b is None or b['valid']))}
            fh.write(json.dumps(row,ensure_ascii=False)+'\n');rows.append(row)
        fh.flush()
        if ordinal%8==0:print(json.dumps({'completed_units':ordinal,'batch_calls':calls,'gpu_seconds':round(gpu,2)}),flush=True)
    cost={'planned_units':len(units),'completed_units':len({r['unit_id'] for r in rows}),'batch_calls':calls,'gpu_seconds':round(gpu,3),'gpu_hours':round(gpu/3600,6),'wall_seconds':round(time.monotonic()-start,3)};cost['within_budget']=calls<=maxcalls and gpu<=maxgpu and cost['wall_seconds']<=maxwall
    result={'candidate_id':CANDIDATE_ID,'contract_sha256':CONTRACT_SHA,'plan_sha256':sha(plan_path),'pdf_manifest':pdf_manifest,'cost':cost,'raw_rows_path':str(raw),'scientific_authority':False};out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result

def rate(rows,key):return sum(bool(r[key]) for r in rows)/len(rows) if rows else float('nan')

def analyze(plan_path:Path,samples_path:Path,run_path:Path,out:Path):
    validate(plan_path,samples_path);runj=load(run_path);raw=Path(runj['raw_rows_path']);rows=[json.loads(x) for x in raw.read_text(encoding='utf-8').splitlines() if x.strip()]
    units=sorted({r['unit_id'] for r in rows});valid={u for u in units if len([r for r in rows if r['unit_id']==u])==4 and all(r['parser_valid'] for r in rows if r['unit_id']==u)};rows=[r for r in rows if r['unit_id'] in valid]
    by={p:[r for r in rows if r['policy']==p] for p in POLICIES};gap=sorted({r['unit_id'] for r in rows if r['gap_stratum']});covered=sorted({r['unit_id'] for r in rows if r['covered_stratum']});un=sorted({r['unit_id'] for r in rows if r['class']=='unanswerable'})
    def sub(p,ids):s=set(ids);return [r for r in by[p] if r['unit_id'] in s]
    base='negative_evidence_baseline';cov='coverage_certified';bg=sub(base,gap);cg=sub(cov,gap);bc=sub(base,covered);cc=sub(cov,covered);bu=sub(base,un);cu=sub(cov,un)
    sg=rate(cg,'primary_state')-rate(bg,'primary_state') if gap else float('nan');sc=rate(cc,'primary_state')-rate(bc,'primary_state') if covered else float('nan');dd=sg-sc if gap and covered else float('nan')
    bm={r['unit_id']:r['primary_state'] for r in bg};cm={r['unit_id']:r['primary_state'] for r in cg};pair=[u for u in gap if u in bm and u in cm];pv,b01,b10=mcnemar([bm[u] for u in pair],[cm[u] for u in pair]) if pair else (1.0,0,0)
    false_gain=rate(bu,'false_answer_unanswerable')-rate(cu,'false_answer_unanswerable') if un else float('nan');acc_drop=rate(bc,'exact_correct')-rate(cc,'exact_correct') if covered else float('nan')
    adequate=len(valid)>=96 and len(gap)>=15 and len(covered)>=15 and bool(runj['cost'].get('within_budget'));residual=bool(adequate and dd>=.10 and pv<.05 and false_gain>=.10 and acc_drop<=.05)
    rates={p:{'gap_primary_state':rate(sub(p,gap),'primary_state') if gap else None,'covered_primary_state':rate(sub(p,covered),'primary_state') if covered else None,'unanswerable_primary_state':rate(sub(p,un),'primary_state') if un else None,'unanswerable_false_answer':rate(sub(p,un),'false_answer_unanswerable') if un else None,'covered_exact_accuracy':rate(sub(p,covered),'exact_correct') if covered else None} for p in POLICIES}
    deltas=[]
    for ids in (gap,covered,un):
        if ids:deltas.append(abs(rate(sub(cov,ids),'primary_state')-rate(sub(base,ids),'primary_state')))
    metrics={'valid_units':len(valid),'gap_answerable':len(gap),'covered_answerable':len(covered),'unanswerable':len(un),'shift_gap':sg,'shift_covered':sc,'difference_in_differences':dd,'paired_gap_mcnemar_p':pv,'discord_base0_cov1':b01,'discord_base1_cov0':b10,'false_answer_improvement_unanswerable':false_gain,'covered_exact_accuracy_drop':acc_drop,'baseline_within_0_05_all_available_strata':bool(deltas and max(deltas)<=.05),'rates':rates}
    outcome='INCONCLUSIVE' if not adequate else ('RESIDUAL_SURVIVES' if residual else 'REDUCTION_SUPPORTED');material={'contract':CONTRACT_SHA,'plan':sha(plan_path),'run':sha(run_path),'raw':sha(raw),'metrics':metrics,'outcome':outcome};msha=hashlib.sha256(json.dumps(material,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    result={'candidate_id':CANDIDATE_ID,'contract_sha256':CONTRACT_SHA,'outcome':outcome,'qualified_units':len(valid),'protocol_valid':bool(len(valid)>0 and runj['cost'].get('within_budget')),'metrics':metrics,'cost':runj['cost'],'evidence_manifest_sha256':msha,'decision_rule_frozen_before_execution':True,'scientific_authority':False};out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('probe','manifest','prepare','run','analyze'));ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--samples',type=Path,required=True);ap.add_argument('--model',type=Path,default=DEFAULT_MODEL);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--pdf-dir',type=Path);ap.add_argument('--page-cache',type=Path);ap.add_argument('--max-units',type=int);ap.add_argument('--run-json',type=Path);a=ap.parse_args()
    if a.command=='probe':r=probe(a.plan,a.samples,a.model);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    elif a.command=='manifest':r=manifest(a.plan,a.samples,a.model,a.output)
    elif a.command=='prepare':
        p,_=validate(a.plan,a.samples)
        if not a.pdf_dir:raise SystemExit('--pdf-dir required')
        r={'pdfs':fetch_pdfs(p,a.pdf_dir),'scientific_authority':False};a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    elif a.command=='run':
        if not a.pdf_dir or not a.page_cache:raise SystemExit('--pdf-dir/--page-cache required')
        r=run(a.plan,a.samples,a.pdf_dir,a.page_cache,a.model,a.output,a.max_units)
    else:
        if not a.run_json:raise SystemExit('--run-json required')
        r=analyze(a.plan,a.samples,a.run_json,a.output)
    print(json.dumps(r,ensure_ascii=False))
if __name__=='__main__':main()
