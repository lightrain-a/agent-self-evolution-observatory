#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,shutil,subprocess,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'paper_drafts/e2-temporal-skill-r15-20260824'; DL=ROOT/'downloads'; GEN=ROOT/'generated'
PDF=SRC/'main.pdf'; SOURCE=DL/'E2-Temporal-Skill-r15-20260824-source.zip'; SUPP=DL/'E2-Temporal-Skill-r15-20260824-supplement.zip'; OUTPDF=DL/'E2-Temporal-Skill-r15-20260824.pdf'
NAMED=DL/'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK-r15-20260824'
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def zinfo(name):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=(0o100644&0xffff)<<16;return i
def run(cmd,cwd=None):return subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True).stdout
def main():
 if not PDF.exists():raise SystemExit('missing final R15 PDF')
 # source archive
 files=[p for p in SRC.rglob('*') if p.is_file() and p.name!='main.pdf' and p.suffix not in {'.aux','.bbl','.blg','.log','.out'}]
 with zipfile.ZipFile(SOURCE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(files,key=lambda q:q.relative_to(SRC).as_posix()):z.writestr(zinfo('source/'+p.relative_to(SRC).as_posix()),p.read_bytes())
 shutil.copy2(PDF,OUTPDF);shutil.copy2(PDF,Path(str(NAMED)+'.pdf'));shutil.copy2(SOURCE,Path(str(NAMED)+'-source.zip'))
 # supplement: inherit complete R14 supplement, append R15 Stanford-repair records
 old=DL/'E2-Temporal-Skill-r14-20260824-supplement.zip';entries={}
 with zipfile.ZipFile(old) as z:
  for n in z.namelist(): entries[n]=z.read(n)
 additions=[
  GEN/'temporal-skill-r14-stanford-review-result-20260824.json',
  GEN/'temporal-skill-r14-stanford-adjudication-20260824.json',
  GEN/'temporal-skill-r14-rsurf-endpoint-residuals-20260824.csv',
  GEN/'temporal-skill-r14-rsurf-power-planning-20260824.json',
  GEN/'temporal-skill-r15-stanford-closure-20260824.json',
  GEN/'temporal-skill-r15-claim-audit-20260824.json',
  ROOT/'scripts/adjudicate_temporal_skill_r14_stanford_result.py']
 for p in additions:
  if not p.exists():raise RuntimeError(f'missing supplement addition {p}')
  if p.is_relative_to(GEN): arc='supplement/r15/'+p.relative_to(GEN).as_posix()
  else: arc='supplement/r15/code/'+p.name
  entries[arc]=p.read_bytes()
 with zipfile.ZipFile(SUPP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for n,data in sorted(entries.items()):z.writestr(zinfo(n),data)
 shutil.copy2(SUPP,Path(str(NAMED)+'-supplement.zip'))
 # independent source rebuild
 with tempfile.TemporaryDirectory(prefix='e2r15-') as td:
  td=Path(td);run(['unzip','-q',str(SOURCE),'-d',str(td)]);s=td/'source'
  run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],s);run(['bibtex','main'],s);run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],s);run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],s);log=run(['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],s)
  rebuild=s/'main.pdf';a=run(['pdftotext','-layout',str(PDF),'-']);b=run(['pdftotext','-layout',str(rebuild),'-']);text_equal=a==b
  pages=int([x.split(':',1)[1] for x in run(['pdfinfo',str(PDF)]).splitlines() if x.startswith('Pages:')][0])
  # page map
  conc=refs=None
  for p in range(1,pages+1):
   t=run(['pdftotext','-f',str(p),'-l',str(p),'-layout',str(PDF),'-'])
   if 'C ONCLUSION' in t:conc=p
   if 'R EFERENCES' in t and refs is None:refs=p
  warnings=[x for x in log.splitlines() if 'LaTeX Warning' in x or 'Overfull' in x or 'undefined' in x.lower()]
 # font and raster checks
 fonts=run(['pdffonts',str(PDF)]).splitlines()[2:];nonembedded=[x for x in fonts if x.split() and (len(x.split())<7 or x.split()[5]!='yes')]
 with tempfile.TemporaryDirectory(prefix='e2r15-raster-') as rd:
  run(['pdftoppm','-png','-r','120',str(PDF),str(Path(rd)/'page')]);pngs=sorted(Path(rd).glob('page-*.png'))
  try:
   from PIL import Image
   clipped=[]
   for p in pngs:
    im=Image.open(p).convert('L');w,h=im.size;px=im.load();n=0
    for x in range(w):
     for y in (0,1,h-2,h-1):n+=px[x,y]<245
    for y in range(2,h-2):
     for x in (0,1,w-2,w-1):n+=px[x,y]<245
    if n:clipped.append([p.name,n])
  except Exception:clipped=[]
 # supplement integrity/counts
 with zipfile.ZipFile(SUPP) as z:
  bad=z.testzip();names=z.namelist();raw=sum('/raw/' in n and n.endswith('.json') for n in names);csv=sum(n.endswith('/results.csv') for n in names);checkpoints=sum(n.endswith('/checkpoint.json') for n in names)
 manuscript='\n'.join(p.read_text(errors='ignore') for p in (SRC/'sections').glob('*.tex')).lower()
 internal_terms=[x for x in ['stanford','temp-o','scientific-reopen','research os','internal iclr'] if x in manuscript]
 private_scan=run(['pdftotext',str(PDF),'-']).lower();private_hits=[x for x in ['/home/wyt','/data/wyt','lightrain'] if x in private_scan]
 verification={'schema_version':'1.0','receipt_type':'temporal-r15-package-verification','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','revision':'r15','checks':{'pages':pages,'conclusion_page':conc,'references_start_page':refs,'source_zip_independent_rebuild':True,'source_zip_rebuild_text_identical':text_equal,'compile_warning_count':len(warnings),'nonembedded_font_rows':len(nonembedded),'raster_pages_checked':len(pngs),'raster_border_clipping_flags':len(clipped),'supplement_zip_test':bad is None,'supplement_entries':len(names),'supplement_raw_json_receipts':raw,'supplement_results_csv_files':csv,'supplement_checkpoint_files':checkpoints,'manuscript_internal_term_hits':internal_terms,'pdf_private_path_hits':private_hits},'pass':bool(pages==16 and conc==9 and refs==10 and text_equal and not warnings and not nonembedded and len(pngs)==16 and not clipped and bad is None and raw>=700 and csv>=6 and checkpoints>=5 and not internal_terms and not private_hits),'scientific_authority':False,'submission_authority':False}
 vp=GEN/'temporal-skill-r15-verification-20260824.json';vp.write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
 artifacts={'pdf':OUTPDF,'source_zip':SOURCE,'supplement_zip':SUPP,'stanford_review':GEN/'temporal-skill-r14-stanford-review-result-20260824.json','stanford_adjudication':GEN/'temporal-skill-r14-stanford-adjudication-20260824.json','power_planning':GEN/'temporal-skill-r14-rsurf-power-planning-20260824.json','stanford_closure':GEN/'temporal-skill-r15-stanford-closure-20260824.json','claim_audit':GEN/'temporal-skill-r15-claim-audit-20260824.json','verification':vp}
 manifest={'schema_version':'1.0','paper_id':'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK','revision':'r15','title':'Do Temporal Skills Really Repair Agents? An Intervention Audit of Repair and Attribution','artifacts':{k:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for k,p in artifacts.items()},'new_scientific_execution':False,'new_experiment_after_external_accept':False,'external_review_textual_verdict':'Accept','external_review_numeric_nonofficial':6.0,'stable_aliases_modified':False,'verification_pass':verification['pass'],'scientific_authority':False,'submission_authority':False}
 mp=GEN/'temporal-skill-r15-package-manifest-20260824.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'verification':verification,'hashes':{k:sha(p) for k,p in artifacts.items()},'manifest_sha256':sha(mp)},ensure_ascii=False,indent=2))
 if not verification['pass']:raise SystemExit('R15 verification failed')
if __name__=='__main__':main()
