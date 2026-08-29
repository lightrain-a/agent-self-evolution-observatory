from __future__ import annotations
import hashlib,json,os,shutil,subprocess,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;SRC=HERE/'source-r9';PDF=HERE/'C1-stage-resolved-r9-state-binding.pdf';ZIP=HERE/'C1-stage-resolved-r9-state-binding-source.zip';MAN=HERE/'c1-r9-scmb-package-manifest-20260829.json';VER=HERE/'c1-scmb-independent-verification-20260829.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(a,cwd=None):
 p=subprocess.run(a,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if p.returncode:
  raise RuntimeError(p.stdout[-4000:])
 return p.stdout
def main():
 for cmd in [['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],['bibtex','main'],['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex']]:run(cmd,SRC)
 shutil.copy2(SRC/'main.pdf',PDF)
 if ZIP.exists():ZIP.unlink()
 with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(SRC.rglob('*')):
   if not p.is_file() or p.name in {'main.pdf','main.aux','main.log','main.out','main.blg'}:continue
   info=zipfile.ZipInfo(str(p.relative_to(SRC)).replace(os.sep,'/'),(2026,8,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 info=run(['pdfinfo',str(PDF)]);pages=int([x.split(':',1)[1] for x in info.splitlines() if x.startswith('Pages:')][0]);log=(SRC/'main.log').read_text(errors='ignore');blg=(SRC/'main.blg').read_text(errors='ignore');p9=run(['pdftotext','-f','9','-l','9','-layout',str(PDF),'-']).replace(' ','').upper();p10=run(['pdftotext','-f','10','-l','10','-layout',str(PDF),'-']).replace(' ','').upper();fonts=run(['pdffonts',str(PDF)]).splitlines()[2:];embedded=all(len(line.split())>=5 and line.split()[4]=='yes' for line in fonts if line.strip())
 v=json.loads(VER.read_text())
 m={'schema_version':'1.0','artifact_kind':'C1_R9_SCMB_PACKAGE','revision':'R9-state-binding','status':'READY_HETEROGENEOUS_PROOF_OF_CONCEPT_NOT_GENERAL_REPAIR','scientific_results_changed':True,'result_boundary':'State-conditioned binding raises mean first-action uptake on a fresh 12-state pilot relative to native and memory-only controls, but the preregistered cross-state consistency gate fails; treat as heterogeneous proof-of-concept, not universal repair or method novelty.','paper_qa':{'pages':pages,'conclusion_on_page9':'CONCLUSION' in p9,'references_on_page9':'REFERENCES' in p9,'appendix_on_page10':'F0REPRODUCTIONDETAILS' in p10,'undefined_or_overfull_warnings':sum(1 for l in log.splitlines() if 'Undefined' in l or 'Overfull' in l),'bibtex_warnings':sum(1 for l in blg.splitlines() if 'Warning' in l),'fonts_embedded':embedded,'scmb_independent_verification':v['status']},'files':{'pdf':{'path':str(PDF.relative_to(HERE.parents[1])),'sha256':sha(PDF)},'source_zip':{'path':str(ZIP.relative_to(HERE.parents[1])),'sha256':sha(ZIP)},'scmb_verification':{'path':str(VER.relative_to(HERE.parents[1])),'sha256':sha(VER)}},'authority':{'confirmatory':False,'terminal_outcome':False,'submission':False}}
 MAN.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
if __name__=='__main__':main()
