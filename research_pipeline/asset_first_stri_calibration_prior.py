from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

FIVE_ATOMS = ("skill_003", "skill_004", "skill_015", "skill_003+skill_015", "skill_004+skill_015")


def load_json(path: Path) -> dict[str, Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"{path} must contain an object")
    return value

def load_jsonl(path: Path) -> list[dict[str,Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def atom(row: dict[str,Any]) -> str:
    values=sorted(str(x) for x in row.get("accepted_skill_ids") or [])
    return "+".join(values) if values else "NONE"

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def build_prior(rows:list[dict[str,Any]],split:dict[str,Any])->dict[str,Any]:
    cal_tools=set(split["partitions"]["calibration"]["tools"])
    held_tools=set(split["partitions"]["heldout"]["tools"])
    if cal_tools & held_tools: raise ValueError("tool leakage")
    cal=[r for r in rows if int(r.get("level") or 0)==1 and str(r.get("tool")) in cal_tools]
    held=[r for r in rows if int(r.get("level") or 0)==1 and str(r.get("tool")) in held_tools]
    def counts(part):
        out={a:0 for a in FIVE_ATOMS}; other=0
        for r in part:
            a=atom(r)
            if a in out: out[a]+=1
            elif a!="NONE": other+=1
        return out,other
    cc,co=counts(cal);hc,ho=counts(held)
    denom=sum(cc.values())
    if denom<=0 or any(cc[a]<=0 for a in FIVE_ATOMS): raise ValueError("calibration lacks five atoms")
    prior={a:cc[a]/denom for a in FIVE_ATOMS}
    core={"atoms":list(FIVE_ATOMS),"calibration_counts":cc,"calibration_non_none_rows":denom,"prior":prior}
    return {
      "schema_version":"1.0","candidate_id":"skill-taxonomy-representation-invariance",
      "split_id":split["split_id"],"calibration_tools":sorted(cal_tools),"heldout_tools":sorted(held_tools),
      "atoms":list(FIVE_ATOMS),"calibration_counts":cc,"calibration_non_none_rows":denom,
      "empirical_calibration_prior":prior,"prior_sha256":digest(core),
      "heldout_frequency_audit_only":{"counts":hc,"non_none_rows":sum(hc.values()),"other_patterns":ho,"may_change_prior_or_structure":False},
      "calibration_other_patterns":co,
      "lock":{"prior_uses_heldout_rows":False,"heldout_frequency_cannot_update_prior":True,"heldout_frequency_cannot_update_atoms":True,"validator_outputs_are_support_labels_not_task_utility":True},
      "scientific_authority":False,
    }


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--membership',type=Path,required=True);ap.add_argument('--split',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    split=load_json(a.split);result=build_prior(load_jsonl(a.membership),split)
    result["membership_sha256"]=sha256(a.membership);result["split_sha256"]=sha256(a.split)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({"prior":result['empirical_calibration_prior'],"prior_sha256":result['prior_sha256']},ensure_ascii=False))
if __name__=='__main__':main()
