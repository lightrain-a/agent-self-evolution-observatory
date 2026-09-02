from __future__ import annotations
import argparse, json, sys, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research_pipeline.relational_topology_gpu_qualification_runner import QualificationError,run_component

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--component',required=True,choices=['BEDROOM-SG2SC-SHARED','SGP-12','SGP-14'])
    p.add_argument('--run-root',type=Path,required=True); p.add_argument('--instructscene-root',type=Path,required=True)
    p.add_argument('--bedroom-root',type=Path,required=True); p.add_argument('--corpus-dir',type=Path,required=True)
    p.add_argument('--clip-root',type=Path,required=True); p.add_argument('--fvqvae-checkpoint',type=Path,required=True)
    p.add_argument('--objfeat-bounds',type=Path,required=True); p.add_argument('--device',type=int,default=0)
    a=p.parse_args()
    try:
        out=run_component(component=a.component,run_root=a.run_root,instructscene=a.instructscene_root,bedroom=a.bedroom_root,corpus_dir=a.corpus_dir,clip=a.clip_root,fvq=a.fvqvae_checkpoint,bounds=a.objfeat_bounds,device_index=a.device)
    except Exception as e:
        fail=a.run_root/(a.component+'.failure.json'); fail.parent.mkdir(parents=True,exist_ok=True)
        fail.write_text(json.dumps({'component':a.component,'error_type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc(),'scientific_outcome':False},ensure_ascii=False,indent=2)+'\n')
        raise
    print(json.dumps({'component':a.component,'status':out['status'],'logical_steps':out['logical_optimizer_steps'],'resume':out['gates']['resume_stability']['status']},sort_keys=True))
if __name__=='__main__': main()
