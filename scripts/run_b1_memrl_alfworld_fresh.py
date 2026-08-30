#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.b1_memrl_alfworld_adjudication import adjudicate_confirmatory
from research_pipeline.b1_memrl_alfworld_target_execution import run_target_phase
from research_pipeline.b1_memrl_alfworld_target_plan import write_target_execution_plan

DEFAULT_RUN = Path('/data/wyt/agent-self-evolution-observatory/runs/b1-memrl-alfworld-fresh-20260830')
DEFAULT_PREFLIGHT = ROOT / 'generated/b1-memrl-alfworld-fresh-preflight-20260830.json'


def main() -> None:
    p=argparse.ArgumentParser(description='Run the frozen B1 MemRL/ALFWorld fresh target pipeline')
    p.add_argument('command',choices=('plan','pilot','confirmatory','adjudicate'))
    p.add_argument('--run-dir',type=Path,default=DEFAULT_RUN)
    p.add_argument('--preflight',type=Path,default=DEFAULT_PREFLIGHT)
    p.add_argument('--config',type=Path,default=ROOT/'research_pipeline/p0_alfworld_config.yaml')
    p.add_argument('--model-path',type=Path,default=Path('/data/wyt/models/indept/Qwen2.5-7B'))
    p.add_argument('--alfworld-data',type=Path,default=Path('/data/wyt/agent-self-evolution-observatory/alfworld'))
    p.add_argument('--device',default='cuda:0')
    a=p.parse_args(); plan=a.run_dir/'target-execution-plan.json'
    if a.command=='plan':
        result=write_target_execution_plan(preflight_path=a.preflight,source_support_path=a.run_dir/'source-support.json',output_dir=a.run_dir,plan_path=plan)
        out={'status':result['status'],'plan_sha256':result['plan_sha256'],'pilot_n':len(result['assignments']['pilot']),'confirmatory_n':len(result['assignments']['confirmatory'])}
    elif a.command in {'pilot','confirmatory'}:
        result=run_target_phase(phase=a.command,preflight_path=a.preflight,plan_path=plan,output_dir=a.run_dir,config_path=a.config,model_path=a.model_path,alfworld_data=a.alfworld_data,device=a.device)
        out={'status':result['status'],'receipt_sha256':result['receipt_sha256'],'target_count_complete':result['target_count_complete'],'memory_utilization_target_count':result['memory_utilization_target_count'],'confirmatory_execution_authorized':result['confirmatory_execution_authorized']}
    else:
        result=adjudicate_confirmatory(preflight_path=a.preflight,plan_path=plan,output_dir=a.run_dir)
        out={'status':result['status'],'receipt_sha256':result['receipt_sha256'],'primary':result['primary'],'secondary':result['secondary']}
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))

if __name__=='__main__':
    main()
