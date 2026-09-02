#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.e2_r18_heldout_probe_suite import build_suite,self_check

def sha(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output-root',type=Path,required=True); ap.add_argument('--receipt',type=Path,required=True); ap.add_argument('--overwrite',action='store_true'); a=ap.parse_args()
 m=build_suite(a.output_root,overwrite=a.overwrite); check=self_check(a.output_root)
 payload={'schema_version':'1.0','artifact_type':'e2-r18-heldout-probe-suite-build-receipt','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'status':'PASS_ZERO_PROVIDER','output_root':str(a.output_root),'suite_manifest_sha256':sha(a.output_root/'suite_manifest.json'),'split_manifest_sha256':sha(a.output_root/'r18_split_manifest.json'),'dataset_sha256':m['dataset_sha256'],'self_check':check,'provider_calls':0,'scientific_outcomes_accessed':False,'authority':{'scientific_execution':False,'provider_io':False,'updater':False,'evaluation':False}}
 a.receipt.parent.mkdir(parents=True,exist_ok=True); a.receipt.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print(json.dumps(payload,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
