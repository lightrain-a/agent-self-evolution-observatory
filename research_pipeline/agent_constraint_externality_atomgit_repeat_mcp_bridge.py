from __future__ import annotations

import argparse, copy, sys
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repeat_common as c
from research_pipeline import agent_constraint_externality_atomgit_repeat_dev_source_mcp_bridge as base
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_reserve_build import OUTPUT_BUNDLE, load_reserve_spec
from research_pipeline.agent_constraint_externality_runner_core import sha256_file


def transformed_spec(family_id:str,arm_level:str,branch:str)->dict[str,Any]:
    spec=copy.deepcopy(load_reserve_spec()); rows=[x for x in spec['families'] if x['family_id']==family_id]
    if len(rows)!=1: raise c.RepeatStop(f'unknown repeat family: {family_id}')
    family=rows[0]; arms=[x for x in family['arms'] if x['coupling_level']==arm_level]
    if len(arms)!=1: raise c.RepeatStop(f'unknown arm: {arm_level}')
    case=copy.deepcopy(family['source_case']); case['fixture']=copy.deepcopy(family['fixture']); case['task_instruction']=c.visible_instruction(family_id,arm_level,branch); case['case_id']=f'{family_id}-{arm_level}-{branch}'
    family['source_case']=case; spec['families']=[family]; return spec

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument('--bundle',type=Path,required=True); p.add_argument('--family-id',required=True); p.add_argument('--arm',choices=c.ARMS,required=True); p.add_argument('--branch',choices=c.BRANCHES,required=True); p.add_argument('--repeat',type=int,choices=c.REPEATS,required=True); p.add_argument('--runtime-root',type=Path,required=True); p.add_argument('--task-id',required=True); p.add_argument('--experiment-name',required=True); p.add_argument('--progress',type=Path,required=True); p.add_argument('--trajectory',type=Path,required=True); p.add_argument('--tool-call-cap',type=int,required=True); a=p.parse_args()
    if sha256_file(a.bundle)!=sha256_file(OUTPUT_BUNDLE): raise c.RepeatStop('reserve bundle SHA drift')
    spec=transformed_spec(a.family_id,a.arm,a.branch)
    base.FROZEN_BUNDLE=OUTPUT_BUNDLE; base.load_dev_spec=lambda: spec
    base.SCHEMA_VERSION='ace-atomgit-repeat-r2-mcp-progress-v1'; base.TRAJECTORY_SCHEMA='ace-atomgit-repeat-r2-trajectory-v1'
    original_world=base.AppWorldToolWorld
    def world_factory(**kwargs:Any):
        kwargs['seed']=c.REPEAT_SEEDS[a.repeat]; return original_world(**kwargs)
    base.AppWorldToolWorld=world_factory
    sys.argv=[sys.argv[0],'--bundle',str(a.bundle),'--family-id',a.family_id,'--runtime-root',str(a.runtime_root),'--task-id',a.task_id,'--experiment-name',a.experiment_name,'--progress',str(a.progress),'--trajectory',str(a.trajectory),'--tool-call-cap',str(a.tool_call_cap)]
    base.main()

if __name__=='__main__': main()
