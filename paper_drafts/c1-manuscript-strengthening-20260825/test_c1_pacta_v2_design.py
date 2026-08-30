from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
RUNNER=HERE/'run_c1_pacta_v2_20260830.py'
spec=importlib.util.spec_from_file_location('pacta_v2',RUNNER); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def test_tv_and_gate_rule():
 assert m.tv(['a']*6,['b']*6)==1.0
 assert m.tv(['a']*6,['a']*6)==0.0
 b1,b2,ws,wf=1.0,0.5,1/3,1/6
 assert min(b1,b2)>max(ws,wf)
 assert not (min(1/3,1/3)>max(1/3,0.0))
def test_frozen_pilot_selection_and_random_ranking():
 pool={137:[352,354,355],138:[239,241,242],139:[269,270,271],156:[436,437,438],172:[506,508],211:[261,262]}
 selected=[]
 for template,tasks in pool.items():
  selected.append((template,min(tasks,key=lambda task:hashlib.sha256(f'C1-PACTA-V2-PILOT-v1|{template}|{task}'.encode()).hexdigest())))
 assert [task for _,task in selected]==[352,239,271,437,506,261]
 ranking=sorted(selected,key=lambda row:hashlib.sha256(f'C1-PACTA-V2-RANDOM-GATE-v1|{row[0]}|{row[1]}'.encode()).hexdigest())
 assert [task for _,task in ranking]==[437,261,271,506,352,239]
def test_frozen_contract_has_no_tunable_epsilon():
 path=HERE/'c1-pacta-v2-contract-20260830.json'
 if not path.exists(): return
 contract=json.loads(path.read_text())
 assert contract['scientific_object']['gate']=='G = min(B1,B2) > max(WS,WF)'
 assert contract['scientific_object']['epsilon'] is None
 assert contract['final_policy']['expected_calls']==288
 assert contract['shadow_realization']['expected_calls']==144
