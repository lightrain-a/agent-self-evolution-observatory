#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, tempfile, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PID="D2-PAPER-FAILURE-MEMORY-PROVENANCE"
SRC=ROOT/"paper/b1-r58-full350-l2-20260902/source"
SUP=ROOT/"paper/b1-r62-public-supplement-20260903"
DL=ROOT/"downloads"; GEN=ROOT/"generated"
TITLE="Does Memory Provenance Matter? Explicit Source-Outcome Cues Shift Agent Actions but Rarely Change Terminal Outcomes"
EXCLUDE={"main.aux","main.blg","main.fdb_latexmk","main.fls","main.log","main.out","main.pdf","main.synctex.gz"}


def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def run(*cmd,cwd=None)->str:return subprocess.check_output(cmd,cwd=cwd,text=True,stderr=subprocess.STDOUT)
def zadd(z:zipfile.ZipFile,arc:str,data:bytes,mode:int=0o644):
 i=zipfile.ZipInfo(arc,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=(mode&0xFFFF)<<16;z.writestr(i,data)
def zip_tree(out:Path,root:Path,prefix:str,exclude:set[str]=set()):
 with zipfile.ZipFile(out,"w") as z:
  for p in sorted(x for x in root.rglob("*") if x.is_file() and x.name not in exclude):
   rel=p.relative_to(root).as_posix();mode=0o755 if p.name in {"reproduce.sh","recompute.py"} else 0o644;zadd(z,f"{prefix}/{rel}",p.read_bytes(),mode)
def pdf_qa(pdf:Path,log:Path)->dict:
 info=run("pdfinfo",str(pdf));pages=int(next(x.split(":",1)[1] for x in info.splitlines() if x.startswith("Pages:")).strip())
 size=next(x.split(":",1)[1] for x in info.splitlines() if x.startswith("Page size:")).strip()
 fonts=run("pdffonts",str(pdf)).splitlines()[2:];embedded=all(len(x.split())>=5 and x.split()[4]=="yes" for x in fonts if x.strip())
 text=log.read_text(errors="replace")
 return {"pdf_pages":pages,"page_size":size,"all_fonts_embedded":embedded,"overfull_boxes":text.count("Overfull"),"undefined_citations":text.count("Citation `") if "undefined" in text else 0,"undefined_references":text.count("Reference `") if "undefined" in text else 0}
def raster_hashes(pdf:Path,outdir:Path)->list[str]:
 outdir.mkdir(parents=True,exist_ok=True);run("pdftoppm","-r","120","-png",str(pdf),str(outdir/"page"))
 return [sha(p) for p in sorted(outdir.glob("page-*.png"))]

def main():
 a=argparse.ArgumentParser();a.add_argument("--skip-build",action="store_true");args=a.parse_args()
 if not args.skip_build: subprocess.check_call(["bash","reproduce.sh"],cwd=SRC,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
 pdf=SRC/"main.pdf";log=SRC/"main.log";qa=pdf_qa(pdf,log)
 if qa["pdf_pages"]!=16 or qa["page_size"]!="612 x 792 pts (letter)" or not qa["all_fonts_embedded"] or qa["overfull_boxes"] or qa["undefined_citations"] or qa["undefined_references"]:raise RuntimeError(f"B1 R66 PDF QA failed:{qa}")
 rpdf=DL/f"{PID}-r66-20260903.pdf";rsrc=DL/f"{PID}-r66-20260903-source.zip";rsup=DL/f"{PID}-r66-20260903-supplement.zip"
 shutil.copy2(pdf,rpdf);zip_tree(rsrc,SRC,"source",EXCLUDE)
 stats=GEN/f"d2-failure-memory-provenance-r66-sparse-discordance-statistical-audit.json";iso=GEN/f"d2-failure-memory-provenance-r66-osinteraction-arm-isolation-audit.json"
 with zipfile.ZipFile(rsup,"w") as z:
  files=[]
  for p in sorted(x for x in SUP.rglob("*") if x.is_file() and x.name not in {"MANIFEST.json","README.md"}):
   rel=p.relative_to(SUP).as_posix();arc=f"supplement/{rel}";data=p.read_bytes();zadd(z,arc,data,0o755 if p.name=="recompute.py" else 0o644);files.append((arc,hashlib.sha256(data).hexdigest()))
  for p,name in [(stats,"evidence/r66_sparse_discordance_statistical_audit.json"),(iso,"evidence/r66_osinteraction_arm_isolation_audit.json"),(ROOT/"research_pipeline/failure_memory_provenance_r66_sparse_discordance_stats.py","r66_sparse_discordance_stats.py")]:
   arc=f"supplement/{name}";data=p.read_bytes();zadd(z,arc,data,0o755 if p.suffix==".py" else 0o644);files.append((arc,hashlib.sha256(data).hexdigest()))
  readme=(SUP/"README.md").read_text()+"\n\n## R66 post-confirmatory addendum\nR66 changes no scientific outcome or preregistered threshold. It adds a conservative sparse-discordance paired-risk-difference audit and a code-bound OSInteraction fresh-container isolation audit. Run `python r66_sparse_discordance_stats.py --qwen evidence/qwen_ab.json --llama evidence/llama_ab.json` from the supplement directory to recompute the conservative intervals.\n"
  zadd(z,"supplement/README.md",readme.encode());files.append(("supplement/README.md",hashlib.sha256(readme.encode()).hexdigest()))
  manifest={"schema_version":"1.0","paper_id":PID,"revision":"R66","scientific_outcomes_changed":False,"preregistered_analysis_changed":False,"files":[{"path":p,"sha256":h} for p,h in sorted(files)]};manifest["manifest_sha256"]=digest(manifest);zadd(z,"supplement/MANIFEST.json",(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n").encode())
 for target,src in [(DL/f"{PID}.pdf",rpdf),(DL/"B1-Failure-Memory.pdf",rpdf),(DL/f"{PID}-source.zip",rsrc),(DL/f"{PID}-supplement.zip",rsup)]:shutil.copy2(src,target)
 with tempfile.TemporaryDirectory(prefix="b1-r66-rebuild-") as td:
  td=Path(td);zipfile.ZipFile(rsrc).extractall(td);subprocess.check_call(["bash","reproduce.sh"],cwd=td/"source",stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
  h1=raster_hashes(rpdf,td/"r1");h2=raster_hashes(td/"source/main.pdf",td/"r2");rebuild={"rebuilt_pages":len(h2),"rendered_pages_identical_to_release_pdf":h1==h2}
 if not rebuild["rendered_pages_identical_to_release_pdf"]:raise RuntimeError("source rebuild render mismatch")
 review=GEN/"d2-failure-memory-provenance-r66-oracle-review-summary.json"
 release={"schema_version":"1.0","paper_id":PID,"receipt_id":"D2-FAILURE-MEMORY-PROVENANCE-R66-POSTORACLE-MANUSCRIPT-RELEASE","recorded_date":"2026-09-03","status":"R66_POSTORACLE_MANUSCRIPT_RELEASE_PASS","role":"PAPER_ONLY_REPAIR_ZERO_NEW_SCIENTIFIC_EXECUTION","title":TITLE,"parent_scientific_adjudication":{"path":"generated/d2-failure-memory-provenance-r62-cross-backbone-l2-adjudication.json","sha256":sha(GEN/"d2-failure-memory-provenance-r62-cross-backbone-l2-adjudication.json")},"review_binding":{"path":str(review.relative_to(ROOT)),"sha256":sha(review)},"statistical_audit":{"path":str(stats.relative_to(ROOT)),"sha256":sha(stats)},"isolation_audit":{"path":str(iso.relative_to(ROOT)),"sha256":sha(iso)},"release_artifacts":{"pdf":{"path":str(rpdf.relative_to(ROOT)),"bytes":rpdf.stat().st_size,"sha256":sha(rpdf)},"source_zip":{"path":str(rsrc.relative_to(ROOT)),"bytes":rsrc.stat().st_size,"sha256":sha(rsrc)},"supplement_zip":{"path":str(rsup.relative_to(ROOT)),"bytes":rsup.stat().st_size,"sha256":sha(rsup)}},"stable_hashes":{"pdf":sha(DL/f"{PID}.pdf"),"b1_pdf":sha(DL/"B1-Failure-Memory.pdf"),"source_zip":sha(DL/f"{PID}-source.zip"),"supplement_zip":sha(DL/f"{PID}-supplement.zip")},"manuscript_qa":qa,"source_rebuild_qa":rebuild,"claim_boundary":{"scientific_values_changed":False,"new_agent_execution":False,"new_provider_calls":0,"preregistered_15pp_threshold_changed":False,"preregistered_bootstrap_changed":False,"semantic_provenance_reasoning_claimed":False,"plus_minus_15pp_equivalence_claimed":False,"PSMG_efficacy_identified":False,"L3_complete":False},"scientific_authority":False,"experiment_authority":False,"gpu_authority":False,"submission_authority":False};release["receipt_sha256"]=digest(release)
 out=GEN/"d2-failure-memory-provenance-r66-postoracle-manuscript-release.json";out.write_text(json.dumps(release,ensure_ascii=False,indent=2)+"\n");print(json.dumps(release,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
