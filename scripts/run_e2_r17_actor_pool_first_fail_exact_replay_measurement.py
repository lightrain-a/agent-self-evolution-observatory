#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from typing import Any
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts import run_e2_r17_actor_pool_measurement_compat_v1 as base
PREFLIGHT='PREFLIGHT_ONLY_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT'; AUTH='AUTHORIZED_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT_ONLY'
def validate_authority(*,mode:str,authorization:Path|None,task_ids:list[str],split:dict[str,Any],k:int,stop_before_provider_io:bool)->tuple[dict[str,Any],str]:
 if mode!='e1': raise RuntimeError('exact-replay measurement permits e1 only')
 if authorization is None: raise RuntimeError('measurement authorization required')
 p=base.json.loads(authorization.read_text(encoding='utf-8')); cp=Path(str(p.get('contract_path') or ''))
 if not cp.is_file() or base.sha256(cp)!=p.get('contract_sha256'): raise RuntimeError('measurement contract binding drift')
 status=p.get('status');
 if status not in {PREFLIGHT,AUTH}: raise RuntimeError('invalid exact-replay measurement authorization status')
 if status==PREFLIGHT and not stop_before_provider_io: raise RuntimeError('preflight authority cannot reach provider I/O')
 au=p.get('authority') or {}; expected_science=status==AUTH
 if au.get('measurement_only') is not True or au.get('updater') is not False or au.get('analyzer') is not False or au.get('scientific_experiment') is not expected_science: raise RuntimeError('measurement authority bits drift')
 scope=p.get('execution_scope') or {}
 if scope.get('measurement_child')!='E2-R17-FIRST-FAIL-EXACT-REPLAY-MEASUREMENT' or scope.get('allowed_modes')!=['e1']: raise RuntimeError('measurement child/mode drift')
 allowed=list(map(str,scope.get('allowed_task_ids') or []))
 if len(allowed)!=18 or len(task_ids)!=1 or task_ids[0] not in allowed: raise RuntimeError('measurement task scope drift')
 if int(scope.get('exact_k',-1))!=int(k) or int(k)!=1 or scope.get('allow_noninitial_skill') is not True: raise RuntimeError('measurement K/skill scope drift')
 learned=scope.get('learned_states') or []
 if len(learned)!=2 or {str(x.get('arm')) for x in learned}!={'win_c','first_fail'}: raise RuntimeError('measurement learned-state set drift')
 return p,base.sha256(authorization)
base.validate_authority=validate_authority
if __name__=='__main__': raise SystemExit(base.main())
