#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,io,json,os,shutil,subprocess,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'paper_drafts/e2-temporal-skill-r16-20260824';DL=ROOT/'downloads';GEN=ROOT/'generated'
DATA=Path('/data/wyt/agent-self-evolution-observatory/paper-acceptance/source-native-replay/D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK')
PDF=SRC/'main.pdf';SOURCE=DL/'E2-Temporal-Skill-r16-20260824-source.zip';SUPP=DL/'E2-Temporal-Skill-r16-20260824-supplement.zip';OUTPDF=DL/'E2-Temporal-Skill-r16-20260824.pdf';NAMED=DL/'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK-r16-20260824'
EXT_ROOTS={
'historical-benign':DATA/'20260824-extension-benign-generic-deepseek',
'eia-clean':DATA/'20260824-extension-eia-future-nonceiling',
'bls-cpi':DATA/'20260824-extension-bls-cpi-crossdomain',
'multiturn':DATA/'20260824-extension-multiturn-tool-vs-context',
'eia-planning-repeat':DATA/'20260824-extension-multiturn-base-repeat-r1',
'bls-planning':DATA/'20260824-extension-bls-cpi-planning-base',
'bls-planning-repeat':DATA/'20260824-extension-bls-cpi-planning-base-repeat-r1',
'fed-fomc':DATA/'20260824-extension-fed-fomc-planning-prospective',
'multiturn-protocol-smoke':DATA/'20260824-extension-multiturn-protocol-smoke/v2',
}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def zinfo(name):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=(0o100644&0xffff)<<16;return i
def run(cmd,cwd=None):return subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True).stdout
def hash_id(v):return 'sha256:'+hashlib.sha256(str(v).encode()).hexdigest()
def clean_string(v:str)->str:
 v=v.replace(str(DATA)+'/','DATA_ROOT/').replace('/data/wyt/agent-self-evolution-observatory/','DATA_ROOT_GLOBAL/').replace('/home/wyt/code/agent-self-evolution-observatory-e2-extension-20260824/','REPO_ROOT/').replace('/home/wyt/code/agent-self-evolution-observatory/','REPO_CANONICAL/')
 return v
def clean_obj(v,key=''):
 if isinstance(v,dict):
  out={}
  for k,x in v.items():
   if k in {'authorization_sha256'}:out[k]=x;continue
   if k in {'id','call_id','response_id'} and isinstance(x,str) and x:out[k]=hash_id(x);continue
   out[k]=clean_obj(x,k)
  return out
 if isinstance(v,list):return [clean_obj(x,key) for x in v]
 if isinstance(v,str):return clean_string(v)
 return v
def sanitize_file(p:Path)->bytes:
 if p.name=='planning-provider.json' or p.name=='authorization.json':raise ValueError('exclude')
 if p.suffix=='.json':return (json.dumps(clean_obj(json.loads(p.read_text(encoding='utf-8'))),ensure_ascii=False,indent=2)+'\n').encode()
 if p.suffix=='.jsonl':
  out=[]
  for line in p.read_text(encoding='utf-8').splitlines():
   if line.strip():out.append(json.dumps(clean_obj(json.loads(line)),ensure_ascii=False,separators=(',',':')))
  return ('\n'.join(out)+'\n').encode()
 if p.suffix=='.csv':
  src=io.StringIO(p.read_text(encoding='utf-8'));dst=io.StringIO();r=csv.reader(src);w=csv.writer(dst,lineterminator='\n')
  for row in r:w.writerow([clean_string(x) for x in row])
  return dst.getvalue().encode()
 if p.suffix in {'.txt','.log','.py'}:return clean_string(p.read_text(encoding='utf-8',errors='replace')).encode()
 return p.read_bytes()
def extension_entries():
 entries={};count=0
 for label,root in EXT_ROOTS.items():
  for p in sorted(root.rglob('*')):
   if not p.is_file() or p.name.endswith('.tmp') or p.name in {'authorization.json','planning-provider.json'}:continue
   try:data=sanitize_file(p)
   except ValueError:continue
   arc='supplement/r16/extension/'+label+'/'+p.relative_to(root).as_posix();entries[arc]=data;count+=1
 return entries,count
def main():
 if not PDF.exists():raise SystemExit('missing R16 PDF')
 files=[p for p in SRC.rglob('*') if p.is_file() and p.name!='main.pdf' and p.suffix not in {'.aux','.bbl','.blg','.log','.out'}]
 with zipfile.ZipFile(SOURCE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(files,key=lambda q:q.relative_to(SRC).as_posix()):z.writestr(zinfo('source/'+p.relative_to(SRC).as_posix()),p.read_bytes())
 shutil.copy2(PDF,OUTPDF);shutil.copy2(PDF,Path(str(NAMED)+'.pdf'));shutil.copy2(SOURCE,Path(str(NAMED)+'-source.zip'))
 old=DL/'E2-Temporal-Skill-r15-20260824-supplement.zip';entries={}
 with zipfile.ZipFile(old) as z:
  for n in z.namelist():entries[n]=z.read(n)
 additions=[GEN/'temporal-skill-extension-adjudication-20260824.json',GEN/'temporal-skill-extension-endpoint-summary-20260824.csv',GEN/'temporal-skill-extension-evidence-manifest-20260824.json',GEN/'temporal-skill-r16-extension-claim-audit-20260824.json',ROOT/'scripts/adjudicate_temporal_skill_extensions.py',ROOT/'scripts/build_temporal_skill_extension_manifest.py',ROOT/'scripts/audit_temporal_skill_r16_extension.py']
 additions+=sorted((ROOT/'research_pipeline').glob('temporal_skill_extension_*.py'))
 for p in additions:
  if not p.exists():raise RuntimeError(f'missing addition {p}')
  arc='supplement/r16/analysis/'+p.name;entries[arc]=sanitize_file(p)
 ext,n_ext=extension_entries();entries.update(ext)
 with zipfile.ZipFile(SUPP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for n,data in sorted(entries.items()):z.writestr(zinfo(n),data)
 shutil.copy2(SUPP,Path(str(NAMED)+'-supplement.zip'))
 with tempfile.TemporaryDirectory(prefix='e2r16-') as td:
  td=Path(td);run(['unzip','-q',str(SOURCE),'-d',str(td)]);s=td/'source';run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],s);run(['bibtex','main'],s);run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],s);run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],s);log=run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],s);rebuild=s/'main.pdf';text_equal=run(['pdftotext','-layout',str(PDF),'-'])==run(['pdftotext','-layout',str(rebuild),'-']);pages=int([x.split(':',1)[1] for x in run(['pdfinfo',str(PDF)]).splitlines() if x.startswith('Pages:')][0]);conc=refs=None
  for pg in range(1,pages+1):
   t=run(['pdftotext','-f',str(pg),'-l',str(pg),'-layout',str(PDF),'-'])
   if 'C ONCLUSION' in t:conc=pg
   if 'R EFERENCES' in t and refs is None:refs=pg
  warnings=[x for x in log.splitlines() if 'LaTeX Warning' in x or 'Overfull' in x or 'undefined' in x.lower()]
 fonts=run(['pdffonts',str(PDF)]).splitlines()[2:];nonembedded=[x for x in fonts if x.split() and (len(x.split())<7 or x.split()[5]!='yes')]
 with tempfile.TemporaryDirectory(prefix='e2r16-raster-') as rd:
  run(['pdftoppm','-png','-r','120',str(PDF),str(Path(rd)/'page')]);pngs=sorted(Path(rd).glob('page-*.png'));clipped=[]
  from PIL import Image
  for p in pngs:
   im=Image.open(p).convert('L');w,h=im.size;px=im.load();n=0
   for x in range(w):
    for y in (0,1,h-2,h-1):n+=px[x,y]<245
   for y in range(2,h-2):
    for x in (0,1,w-2,w-1):n+=px[x,y]<245
   if n:clipped.append([p.name,n])
 with zipfile.ZipFile(SUPP) as z:
  bad=z.testzip();names=z.namelist();raw=sum('/raw/' in n and n.endswith('.json') for n in names);csvn=sum(n.endswith('.csv') for n in names);checkpoints=sum(n.endswith('checkpoint.json') for n in names);new_names=[n for n in names if n.startswith('supplement/r16/')];private=[]
  for n in new_names:
   data=z.read(n)
   if n.endswith(('.json','.jsonl','.csv','.txt','.py')):
    text0=data.decode('utf-8','replace')
    for needle in ['/data/wyt','/home/wyt','ARK_API_KEY','598666122@qq.com']:
     if needle in text0:private.append([n,needle])
    import re
    if re.search(r'"(?:id|call_id|response_id)"\s*:\s*"(?:resp|msg|fc)_',text0):private.append([n,'raw-provider-id'])
 manuscript='\n'.join(p.read_text(errors='ignore') for p in (SRC/'sections').glob('*.tex')).lower();internal=[x for x in ['stanford','temp-o','scientific-reopen','research os','r14','r15','post-accept'] if x in manuscript];pdftext=run(['pdftotext',str(PDF),'-']).lower();pdf_private=[x for x in ['/home/wyt','/data/wyt','lightrain','598666122'] if x in pdftext]
 verification={'schema_version':'1.0','receipt_type':'temporal-r16-package-verification','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','revision':'r16','checks':{'pages':pages,'conclusion_page':conc,'references_start_page':refs,'source_zip_independent_rebuild':True,'source_zip_rebuild_text_identical':text_equal,'compile_warning_count':len(warnings),'nonembedded_font_rows':len(nonembedded),'raster_pages_checked':len(pngs),'raster_border_clipping_flags':len(clipped),'supplement_zip_test':bad is None,'supplement_entries':len(names),'r16_extension_entries':n_ext,'supplement_raw_json_receipts':raw,'supplement_csv_files':csvn,'supplement_checkpoint_files':checkpoints,'r16_new_entry_private_leaks':private,'manuscript_internal_term_hits':internal,'pdf_private_path_hits':pdf_private},'pass':bool(pages==17 and conc==9 and refs==10 and text_equal and not warnings and not nonembedded and len(pngs)==17 and not clipped and bad is None and n_ext>=150 and not private and not internal and not pdf_private),'scientific_authority':False,'submission_authority':False}
 vp=GEN/'temporal-skill-r16-verification-20260824.json';vp.write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
 artifacts={'pdf':OUTPDF,'source_zip':SOURCE,'supplement_zip':SUPP,'extension_adjudication':GEN/'temporal-skill-extension-adjudication-20260824.json','extension_manifest':GEN/'temporal-skill-extension-evidence-manifest-20260824.json','claim_audit':GEN/'temporal-skill-r16-extension-claim-audit-20260824.json','verification':vp};manifest={'schema_version':'1.0','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','revision':'r16','title':'Do Temporal Skills Really Repair Agents? An Intervention Audit of Repair and Attribution','artifacts':{k:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for k,p in artifacts.items()},'core_r15_claim_changed':False,'extension_routing':'appendix robustness/boundary only; planning spin-off STOP after prospective Fed falsifier','stable_aliases_modified':False,'scientific_authority':False,'submission_authority':False,'verification_pass':verification['pass']};mp=GEN/'temporal-skill-r16-package-manifest-20260824.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'verification':verification,'hashes':{k:sha(p) for k,p in artifacts.items()},'manifest_sha256':sha(mp)},ensure_ascii=False,indent=2));
 if not verification['pass']:raise SystemExit('R16 verification failed')
if __name__=='__main__':main()
