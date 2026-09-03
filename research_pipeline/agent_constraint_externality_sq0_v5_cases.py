from __future__ import annotations

import copy
from datetime import date
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_sq0_v3_cases import choose_content, choose_manifest, choose_task, kv
from research_pipeline.agent_constraint_externality_sq0_v4_cases import _choose_modifier, fg_case as v4_fg_case, tnf_case as v4_tnf_case, evaluate_case_from_state


def _replace(obj: Any, pairs: list[tuple[str, str]]) -> Any:
    if isinstance(obj, str):
        for old, new in pairs:
            obj = obj.replace(old, new)
        return obj
    if isinstance(obj, list): return [_replace(x, pairs) for x in obj]
    if isinstance(obj, dict): return {k: _replace(v, pairs) for k, v in obj.items()}
    return obj


def _dump(d: dict[str, Any]) -> str:
    return "\n".join(f"{k}={v}" for k, v in d.items())


def _recompute_fg(case: dict[str, Any]) -> None:
    rows = case["fixture"]["rows"]
    route = next(r for r in rows if r["app"] == "file_system" and str(r["values"].get("tilde_path", "")).endswith("/dispatch-route.txt"))
    rk = kv(str(route["values"]["content"]))
    def files(prefix: str) -> list[dict[str, Any]]:
        return [r for r in rows if r["app"] == "file_system" and Path(str(r["values"].get("tilde_path", ""))).name.startswith(prefix)]
    policies=[]
    for r in files("policy-"):
        d=kv(str(r["values"]["content"]));
        for k in ("MIN_SCORE","PIVOT","W1","W2","MOD"): d[k]=int(d[k])
        policies.append(d)
    cutoff=date.fromisoformat(rk["CUTOFF"])
    policy=max((p for p in policies if p["PROJECT"]==rk["PROJECT"] and p["ACTIVE"]=="YES" and date.fromisoformat(p["EFFECTIVE"])<=cutoff),key=lambda p:date.fromisoformat(p["EFFECTIVE"]))
    recipients=[]
    for r in files("recipient-"):
        d=kv(str(r["values"]["content"])); d["PRIORITY"]=int(d["PRIORITY"]); recipients.append(d)
    recipient=max((r for r in recipients if r["ROUTE_KEY"]==policy["ROUTE_KEY"] and r["ACTIVE"]=="YES"),key=lambda r:(r["PRIORITY"],r["EMAIL"]))
    manifests=[]
    for r in files("manifest-"):
        d=kv(str(r["values"]["content"])); d["SCORE"]=int(d["SCORE"]); manifests.append(d)
    eligible=[m for m in manifests if m["REGION"]==policy["REGION"] and m["ROUTE_KEY"]==policy["ROUTE_KEY"] and m["SCORE"]>=policy["MIN_SCORE"]]
    primary=choose_manifest([m for m in eligible if m["ROLE"]=="PRIMARY"],policy["PRIMARY_MODE"],policy["PIVOT"])
    secondary=choose_manifest([m for m in eligible if m["ROLE"]=="SECONDARY"],policy["SECONDARY_MODE"],policy["PIVOT"])
    check=(primary["SCORE"]*policy["W1"]+secondary["SCORE"]*policy["W2"]+recipient["PRIORITY"])%policy["MOD"]
    payloads={Path(str(r["values"].get("tilde_path", ""))).name:str(r["values"].get("content", "")) for r in rows if r["app"]=="file_system"}
    case["expected"]={"recipient":recipient["EMAIL"],"subject":f"{rk['SUBJECT_PREFIX']}-{policy['POLICY_CODE']}-{primary['TOKEN']}-{secondary['TOKEN']}-{check:02d}","body":rk["BODY"],"attachment_contents":{primary["PAYLOAD_FILE"]:payloads[primary["PAYLOAD_FILE"]],secondary["PAYLOAD_FILE"]:payloads[secondary["PAYLOAD_FILE"]]}}


def fg_case(i: int) -> dict[str, Any]:
    sid=f"{i:02d}"
    c=_replace(copy.deepcopy(v4_fg_case(i)),[("SQ0V4-","SQ0V5-"),("sq0v4-","sq0v5-"),("V4FG","V5FG"),("V4R","V5R"),("V4C","V5C"),("V4P","V5P"),("v4-qualified-blob-","v5-qualified-blob-")])
    c["case_id"]=f"SQ0V5-FG-{sid}"; c["kind"]="FG_SEMANTIC_V5"
    for r in c["fixture"]["rows"]:
        v=r["values"]
        if isinstance(v.get("id"),int): v["id"] += 3_000_000
        if isinstance(v.get("order_index"),int): v["order_index"] += 30_000
        path=Path(str(v.get("tilde_path", ""))).name
        if path=="policy-b.txt":
            d=kv(str(v["content"])); d["PIVOT"]=str(int(d["PIVOT"])+2+(i%3)); d["W1"]=str(int(d["W1"])+1); v["content"]=_dump(d)
        elif path.startswith("manifest-"):
            d=kv(str(v["content"])); d["SCORE"]=str(int(d["SCORE"])+((i+int(v["id"]))%3)-1); v["content"]=_dump(d)
        elif path.startswith("recipient-"):
            d=kv(str(v["content"])); d["PRIORITY"]=str(int(d["PRIORITY"])+(i%2)); v["content"]=_dump(d)
    _recompute_fg(c)
    return c


def _recompute_tnf(case: dict[str, Any]) -> None:
    rows=case["fixture"]["rows"]
    route=next(r for r in rows if r["app"]=="simple_note" and str(r["values"].get("title","")).startswith("sq0v5-route-tnf-"))
    rk=kv(str(route["values"]["content"]))
    policies=[]
    for r in rows:
        if r["app"]=="simple_note" and str(r["values"].get("title","")).startswith("sq0v5-policy-"):
            d=kv(str(r["values"]["content"])); d["title"]=r["values"]["title"]
            for k in ("EPOCH","POLICY_PRIORITY","PIVOT","MODIFIER_PIVOT","BASE","WA","WB","MOD"): d[k]=int(d[k])
            policies.append(d)
    cutoff=int(rk["CUTOFF_EPOCH"])
    policy=max((p for p in policies if p["ACTIVE"]=="YES" and p["TIER"]==rk["REQUIRED_TIER"] and p["EPOCH"]<=cutoff),key=lambda p:(p["EPOCH"],p["POLICY_PRIORITY"],p["title"]))
    contents=[]
    for r in rows:
        if r["app"]=="simple_note" and str(r["values"].get("title","")).startswith("sq0v5-content-"):
            d=kv(str(r["values"]["content"])); d["title"]=r["values"]["title"]; d["SCORE"]=int(d["SCORE"]);d["REVISION"]=int(d["REVISION"]);contents.append(d)
    eligible=[c for c in contents if c["ROUTE_KEY"]==policy["ROUTE_KEY"] and c["PHASE"]==policy["PHASE"]]
    primary=choose_content([c for c in eligible if c["ROLE"]=="PRIMARY"],policy["PRIMARY_CONTENT_MODE"],policy["PIVOT"])
    secondary=choose_content([c for c in eligible if c["ROLE"]=="SECONDARY"],policy["SECONDARY_CONTENT_MODE"],policy["PIVOT"])
    tasks=[]
    for r in rows:
        if r["app"]=="todoist" and str(r["values"].get("title","")).startswith("sq0v5-output-"):
            d=kv(str(r["values"].get("description","")).replace(";","\n")); tasks.append({"TITLE":r["values"]["title"],"ROUTE_KEY":d["ROUTE_KEY"],"PHASE":d["PHASE"],"PRIORITY":int(d["PRIORITY"]),"WEIGHT":int(d["WEIGHT"])})
    task=choose_task([t for t in tasks if t["ROUTE_KEY"]==policy["ROUTE_KEY"] and t["PHASE"]==policy["PHASE"]],policy["TASK_MODE"])
    adjustments=[]; modifiers=[]
    for r in rows:
        if r["app"]!="file_system" or "content" not in r["values"]: continue
        name=Path(str(r["values"].get("tilde_path", ""))).name
        if name.startswith("adjust-"):
            d=kv(str(r["values"]["content"]));d["name"]=name;d["RANK"]=int(d["RANK"]);d["DELTA"]=int(d["DELTA"]);adjustments.append(d)
        elif name.startswith("modifier-"):
            d=kv(str(r["values"]["content"]));d["name"]=name;d["RANK"]=int(d["RANK"]);d["VALUE"]=int(d["VALUE"]);modifiers.append(d)
    adj=max((a for a in adjustments if a["ADJUST_KEY"]==policy["ADJUST_KEY"] and a["ACTIVE"]=="YES"),key=lambda a:a["RANK"])
    modifier=_choose_modifier([m for m in modifiers if m["MOD_KEY"]==policy["MOD_KEY"] and m["ACTIVE"]=="YES"],policy["MODIFIER_MODE"],policy["MODIFIER_PIVOT"])
    total=(policy["BASE"]+primary["REVISION"]*policy["WA"]+secondary["SCORE"]*policy["WB"]+task["PRIORITY"]+task["WEIGHT"]+adj["DELTA"]+modifier["VALUE"])%policy["MOD"]
    out=f"{rk['OUTPUT_DIR']}{task['TITLE']}-{policy['PHASE']}-{primary['TOKEN']}-{secondary['TOKEN']}-{modifier['TOKEN']}.txt"
    text=f"POLICY={policy['POLICY_CODE']}\nPRIMARY={primary['TOKEN']}:{primary['PAYLOAD']}\nSECONDARY={secondary['TOKEN']}:{secondary['PAYLOAD']}\nTASK={task['TITLE']}\nADJUST={adj['DELTA']}\nMODIFIER={modifier['TOKEN']}:{modifier['VALUE']}\nTOTAL={total}"
    case["expected"]={"output_path":out,"output_content":text}


def tnf_case(i: int) -> dict[str, Any]:
    sid=f"{i:02d}"
    c=_replace(copy.deepcopy(v4_tnf_case(i)),[("SQ0V4-","SQ0V5-"),("sq0v4-","sq0v5-"),("V4ADJ","V5ADJ"),("V4MOD","V5MOD"),("V4C","V5C"),("V4P","V5P"),("V4RK","V5RK")])
    c["case_id"]=f"SQ0V5-TNF-{sid}";c["kind"]="TNF_SEMANTIC_V5"
    for r in c["fixture"]["rows"]:
        v=r["values"]
        if isinstance(v.get("id"),int): v["id"] += 3_500_000
        if isinstance(v.get("order_index"),int): v["order_index"] += 35_000
        if r["app"]=="simple_note" and str(v.get("title","")).startswith("sq0v5-route-tnf-"):
            v["content"] = str(v["content"]) + (
                "\nEXACT_OUTPUT_MAPPING: the seven output lines MUST use these selected attributes exactly: "
                "POLICY=<POLICY_CODE>; PRIMARY=<PRIMARY TOKEN>:<PRIMARY PAYLOAD>; "
                "SECONDARY=<SECONDARY TOKEN>:<SECONDARY PAYLOAD>; TASK=<TASK TITLE>; "
                "ADJUST=<selected adjustment DELTA>; MODIFIER=<selected modifier TOKEN>:<selected modifier VALUE>; TOTAL=<computed TOTAL>. "
                "Do not substitute note titles, source filenames, adjustment filenames, or modifier filenames for those attribute values."
            )
        elif r["app"]=="simple_note" and str(v.get("title","")).startswith("sq0v5-policy-"):
            d=kv(str(v["content"]));d["BASE"]=str(int(d["BASE"])+2+i);d["PIVOT"]=str(int(d["PIVOT"])+1+(i%2));v["content"]=_dump(d)
        elif r["app"]=="simple_note" and str(v.get("title","")).startswith("sq0v5-content-"):
            d=kv(str(v["content"]));d["SCORE"]=str(int(d["SCORE"])+((i+int(v["id"]))%3)-1);d["REVISION"]=str(int(d["REVISION"])+(i%2));v["content"]=_dump(d)
        elif r["app"]=="todoist" and str(v.get("title","")).startswith("sq0v5-output-"):
            d=kv(str(v.get("description","")).replace(";","\n"));d["PRIORITY"]=str(int(d["PRIORITY"])+(i%2));d["WEIGHT"]=str(int(d["WEIGHT"])+((i+1)%3));v["description"]="; ".join(f"{k}={val}" for k,val in d.items())
        elif r["app"]=="file_system" and Path(str(v.get("tilde_path", ""))).name.startswith("adjust-"):
            d=kv(str(v["content"]));d["DELTA"]=str(int(d["DELTA"])+(i%3));v["content"]=_dump(d)
        elif r["app"]=="file_system" and Path(str(v.get("tilde_path", ""))).name.startswith("modifier-"):
            d=kv(str(v["content"]));d["VALUE"]=str(int(d["VALUE"])+((i+1)%2));v["content"]=_dump(d)
    c["target_local_resources"]=[x.replace("sq0v4","sq0v5").replace("V4","V5") for x in c["target_local_resources"]]
    c["task_instruction"]=c["task_instruction"].replace("routing note", "routing note").replace("exactly, then create", "exactly, including the note's explicit output-field mapping, then create")
    _recompute_tnf(c)
    return c


def build_cases() -> list[dict[str, Any]]:
    return [fg_case(i) for i in range(1,7)] + [tnf_case(i) for i in range(1,7)]


__all__=["build_cases","fg_case","tnf_case","evaluate_case_from_state"]
