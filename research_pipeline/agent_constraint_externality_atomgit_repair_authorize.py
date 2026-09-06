from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from research_pipeline import agent_constraint_externality_atomgit_repair_common as c
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

RUNNER=c.ROOT/'research_pipeline/agent_constraint_externality_atomgit_repair_execute.py'
AUTH_BASIS="User message '继续' at 2026-09-06 20:27+08:00 after the assistant explicitly scoped the next provider action to target-evidence projection followed by repair-generation only, with repeat/topology execution remaining closed."

def freeze()->dict[str,Any]:
    if c.AUTH.exists() or c.CONTRACT.exists(): raise c.RepairStop('repair authority artifacts already exist')
    pf=c.verified(c.PREFLIGHT,'ATOMGIT_REPEAT_DEV_REPAIR_PREFLIGHT_PASS_AWAITING_HUMAN_AUTHORITY'); proj=c.projection()
    if pf['projection_content_sha256']!=proj['content_sha256'] or pf['runner_sha256']!=sha256_file(RUNNER) or pf['common_sha256']!=sha256_file(Path(c.__file__)):
        raise c.RepairStop('preflight execution binding drift')
    if pf['g1_quota_release_file_sha256']!=sha256_file(c.G1_RELEASE): raise c.RepairStop('G1 quota release drift')
    auth={'schema_version':'ace-repeat-dev-repair-human-authorization-v1','object_id':OBJECT_ID,'status':'USER_AUTHORIZED_ATOMGIT_REPEAT_DEV_REPAIR_GENERATION_ONLY','authorized_at':'2026-09-06T20:27:00+08:00','authorization_basis':AUTH_BASIS,'scope':'Exactly one target-only repair-writer request for each of the six frozen development families, using TARGET_EVIDENCE_PROJECTION_V1. No source replay, topology arm, repeat panel, RQ1/RQ2, RQ3, RQ4, or paper-claim authority.','projection_content_sha256':proj['content_sha256'],'preflight_content_sha256':pf['content_sha256'],'authority':{'repair_generation':True,'development_repeat_qualification':False,'target_only_verification':False,'rq1_rq2':False,'rq3':False,'rq4':False,'paper_claim':False},'scientific_externality_outcomes_observed':0}
    auth['content_sha256']=sha256_value(auth); c.writej(c.AUTH,auth)
    contract={'schema_version':'ace-repeat-dev-repair-execution-contract-v1','object_id':OBJECT_ID,'status':'ATOMGIT_REPEAT_DEV_REPAIR_GENERATION_EXECUTION_AUTHORIZED','execution_id':c.EXECUTION_ID,'human_authorization_content_sha256':auth['content_sha256'],'projection_content_sha256':proj['content_sha256'],'preflight_content_sha256':pf['content_sha256'],'g1_quota_release_file_sha256':sha256_file(c.G1_RELEASE),'runner_sha256':sha256_file(RUNNER),'common_sha256':sha256_file(Path(c.__file__)),'model':{'provider':c.PROVIDER,'profile':c.MODEL_PROFILE,'id':c.MODEL_ID},'writer':{'family_ids':c.selected_ids(proj),'one_request_per_family':True,'request_cap':6,'model_round_cap_per_family':1,'retry_after_dispatch':False,'tools_allowed':False,'raw_source_trajectory_visible':False,'human_edit_after_generation':False},'quota':{'g1_reserve':0,'release_basis_file_sha256':sha256_file(c.G1_RELEASE),'stage_request_cap':6,'operational_margin':5,'predispatch_remaining_rule':'remaining >= number_of_not_yet_dispatched_repairs + 5'},'authority':auth['authority'],'scientific_externality_outcomes_observed':0}
    contract['content_sha256']=sha256_value(contract); c.writej(c.CONTRACT,contract)
    return {'authorization':auth,'contract':contract}

def main()->None: print(json.dumps(freeze(),ensure_ascii=False,sort_keys=True))
if __name__=='__main__': main()
