from __future__ import annotations

import copy
import json
import sqlite3
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import materialize_appworld_measurement_state
from research_pipeline.agent_constraint_externality_sq0_build import _row
from research_pipeline.agent_constraint_externality_sq0_v2_build import _fg as v2_fg, _tnf as v2_tnf


def _replace(obj: Any, pairs: list[tuple[str, str]]) -> Any:
    if isinstance(obj, str):
        for old, new in pairs:
            obj = obj.replace(old, new)
        return obj
    if isinstance(obj, list): return [_replace(x, pairs) for x in obj]
    if isinstance(obj, dict): return {k: _replace(v, pairs) for k, v in obj.items()}
    return obj


def kv(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            k, v = line.split("=", 1); out[k.strip()] = v.strip()
    return out


def records(text: str) -> list[dict[str, str]]:
    return [kv(block) for block in text.split("---") if block.strip()]


def choose_manifest(rows: list[dict[str, Any]], mode: str, pivot: int) -> dict[str, Any]:
    if mode == "FARTHEST_PIVOT_MIN_TOKEN": return min(rows, key=lambda r: (-abs(int(r["SCORE"])-pivot), str(r["TOKEN"])))
    if mode == "CLOSEST_PIVOT_MAX_TOKEN": return max(rows, key=lambda r: (-abs(int(r["SCORE"])-pivot), str(r["TOKEN"])))
    if mode == "MAX_SCORE_MIN_TOKEN": return min(rows, key=lambda r: (-int(r["SCORE"]), str(r["TOKEN"])))
    if mode == "MIN_SCORE_MAX_TOKEN": return max(rows, key=lambda r: (-int(r["SCORE"]), str(r["TOKEN"])))
    raise RuntimeError(mode)


def choose_content(rows: list[dict[str, Any]], mode: str, pivot: int) -> dict[str, Any]:
    if mode == "MAX_REV_MIN_SCORE": return min(rows, key=lambda r: (-int(r["REVISION"]), int(r["SCORE"]), str(r["TOKEN"])))
    if mode == "MAX_SCORE_MAX_REV": return max(rows, key=lambda r: (int(r["SCORE"]), int(r["REVISION"]), str(r["TOKEN"])))
    if mode == "CLOSEST_SCORE_MAX_REV": return min(rows, key=lambda r: (abs(int(r["SCORE"])-pivot), -int(r["REVISION"]), str(r["TOKEN"])))
    raise RuntimeError(mode)


def choose_task(rows: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    if mode == "MAX_PRIORITY_MIN_TITLE": return min(rows, key=lambda r: (-int(r["PRIORITY"]), str(r["TITLE"])))
    if mode == "MAX_WEIGHT_MAX_PRIORITY": return max(rows, key=lambda r: (int(r["WEIGHT"]), int(r["PRIORITY"]), str(r["TITLE"])))
    if mode == "MIN_WEIGHT_MAX_PRIORITY": return min(rows, key=lambda r: (int(r["WEIGHT"]), -int(r["PRIORITY"]), str(r["TITLE"])))
    raise RuntimeError(mode)


def _fresh_base(case: dict[str, Any], i: int, kind: str) -> dict[str, Any]:
    sid=f"{i:02d}"; fresh=_replace(copy.deepcopy(case), [("SQ0V2-","SQ0V3-"),("sq0v2-","sq0v3-"),("V2FG","V3FG"),("V2RK","V3RK"),("payload-v2-","payload-v3-"),("VP","V3P"),("qualified-blob-","v3-qualified-blob-")])
    fresh["case_id"]=f"SQ0V3-{kind}-{sid}"
    for row in fresh["fixture"]["rows"]:
        if isinstance(row["values"].get("id"), int): row["values"]["id"] += 500_000
        if isinstance(row["values"].get("order_index"), int): row["values"]["order_index"] += 5_000
    return fresh


def fg_case(i: int) -> dict[str, Any]:
    sid=f"{i:02d}"; c=_fresh_base(v2_fg(i),i,"FG")
    c["kind"]="FG_SEMANTIC_V3"; base=1_610_000+i*100
    route_row=next(r for r in c["fixture"]["rows"] if r["app"]=="file_system" and str(r["values"].get("tilde_path","")).endswith("/dispatch-route.txt"))
    directory=str(route_row["values"]["tilde_path"]).rsplit("/",1)[0]; absolute=str(route_row["values"]["path"]).rsplit("/",1)[0]
    policy_rows=[r for r in c["fixture"]["rows"] if r["app"]=="file_system" and Path(str(r["values"].get("tilde_path",""))).name.startswith("policy-")]
    manifest_rows=[r for r in c["fixture"]["rows"] if r["app"]=="file_system" and Path(str(r["values"].get("tilde_path",""))).name.startswith("manifest-")]
    modes_p=["FARTHEST_PIVOT_MIN_TOKEN","CLOSEST_PIVOT_MAX_TOKEN","MAX_SCORE_MIN_TOKEN"]
    modes_s=["MIN_SCORE_MAX_TOKEN","FARTHEST_PIVOT_MIN_TOKEN","CLOSEST_PIVOT_MAX_TOKEN"]
    pm,sm=modes_p[(i-1)%3],modes_s[(i+1)%3]; pivot=64+i; w1=3+i%3; w2=5+i%2; mod=97
    # policy-b is the latest active policy in the V2 recipe.
    for r in policy_rows:
        d=kv(str(r["values"]["content"])); name=Path(str(r["values"]["tilde_path"])).name
        d["ROUTE_KEY"] = f"V3R{sid}" if name=="policy-b.txt" else f"DECOY-P-{sid}-{name}"
        d["PRIMARY_MODE"] = pm if name=="policy-b.txt" else "MAX_SCORE_MIN_TOKEN"
        d["SECONDARY_MODE"] = sm if name=="policy-b.txt" else "MIN_SCORE_MAX_TOKEN"
        d["PIVOT"] = str(pivot if name=="policy-b.txt" else 50)
        d["W1"],d["W2"],d["MOD"] = str(w1),str(w2),str(mod)
        r["values"]["content"]="\n".join(f"{k}={v}" for k,v in d.items())
    selected_policy=kv(next(r for r in policy_rows if Path(str(r["values"]["tilde_path"])).name=="policy-b.txt")["values"]["content"])
    # Add route-key membership to manifests so selection is a real join.
    parsed=[]
    for j,r in enumerate(manifest_rows):
        d=kv(str(r["values"]["content"])); d["ROUTE_KEY"]=selected_policy["ROUTE_KEY"] if j not in {0,6,9} else f"DECOY-M-{sid}-{j}"
        r["values"]["content"]="\n".join(f"{k}={v}" for k,v in d.items()); d["SCORE"]=int(d["SCORE"]); parsed.append(d)
    recipients=["jo.ball@gmail.com","les_ball@gmail.com","bradley_ball@gmail.com","ka_ball@gmail.com","thomas.solomon@gmail.com","chris.mcco@gmail.com"]
    recipient_files=[]; recipient_rows=[]
    for j in range(6):
        name=f"recipient-{j+1:02d}.txt"; match=j in {1,4}; active="YES" if j!=1 else "NO"; rec={"ROUTE_KEY":selected_policy["ROUTE_KEY"] if match else f"DECOY-R-{sid}-{j}","ACTIVE":active,"PRIORITY":20+i+j,"EMAIL":recipients[(i+j+1)%6]}
        recipient_files.append(name); recipient_rows.append(rec); c["fixture"]["rows"].append(_row("file_system","files",id=base+j,path=f"{absolute}/{name}",tilde_path=f"{directory}/{name}",user_id=99,content="\n".join(f"{k}={v}" for k,v in rec.items())))
    recipient=max((r for r in recipient_rows if r["ROUTE_KEY"]==selected_policy["ROUTE_KEY"] and r["ACTIVE"]=="YES"),key=lambda r:(int(r["PRIORITY"]),str(r["EMAIL"])))
    eligible=[m for m in parsed if m["REGION"]==selected_policy["REGION"] and m["ROUTE_KEY"]==selected_policy["ROUTE_KEY"] and int(m["SCORE"])>=int(selected_policy["MIN_SCORE"])]
    primary=choose_manifest([m for m in eligible if m["ROLE"]=="PRIMARY"],selected_policy["PRIMARY_MODE"],int(selected_policy["PIVOT"])); secondary=choose_manifest([m for m in eligible if m["ROLE"]=="SECONDARY"],selected_policy["SECONDARY_MODE"],int(selected_policy["PIVOT"]))
    check=(int(primary["SCORE"])*int(selected_policy["W1"])+int(secondary["SCORE"])*int(selected_policy["W2"])+int(recipient["PRIORITY"]))%int(selected_policy["MOD"])
    old_route=kv(str(route_row["values"]["content"])); prefix=old_route["SUBJECT_PREFIX"]; body=old_route["BODY"]
    route=(str(route_row["values"]["content"]).split("Choose the ACTIVE=YES",1)[0]+f"RECIPIENT_FILES={','.join(recipient_files)}\n"+
        "Choose ACTIVE=YES policy for PROJECT with latest EFFECTIVE not after CUTOFF. From ACTIVE=YES recipient files matching policy ROUTE_KEY choose highest PRIORITY, tie by lexicographically largest EMAIL. Inspect all listed manifests and keep only REGION, ROUTE_KEY and SCORE>=MIN_SCORE matches. PRIMARY_MODE/SECONDARY_MODE come from policy: FARTHEST_PIVOT_MIN_TOKEN = largest absolute SCORE-PIVOT then smallest TOKEN; CLOSEST_PIVOT_MAX_TOKEN = smallest absolute SCORE-PIVOT then largest TOKEN; MAX_SCORE_MIN_TOKEN = largest SCORE then smallest TOKEN; MIN_SCORE_MAX_TOKEN = smallest SCORE then largest TOKEN. Choose PRIMARY and SECONDARY accordingly. CHECK=(PRIMARY_SCORE*W1+SECONDARY_SCORE*W2+RECIPIENT_PRIORITY) mod MOD. Subject is SUBJECT_PREFIX-POLICY_CODE-PRIMARY_TOKEN-SECONDARY_TOKEN-CHECK with two-digit CHECK. Send exactly one email to selected EMAIL with BODY and exactly the two selected PAYLOAD_FILE attachments; preserve attachment bytes.")
    route_row["values"]["content"]=route
    subject=f"{prefix}-{selected_policy['POLICY_CODE']}-{primary['TOKEN']}-{secondary['TOKEN']}-{check:02d}"
    payload_rows={Path(str(r["values"].get("tilde_path",""))).name:str(r["values"].get("content","")) for r in c["fixture"]["rows"] if r["app"]=="file_system"}
    c["expected"]={"recipient":recipient["EMAIL"],"subject":subject,"body":body,"attachment_contents":{primary["PAYLOAD_FILE"]:payload_rows[primary["PAYLOAD_FILE"]],secondary["PAYLOAD_FILE"]:payload_rows[secondary["PAYLOAD_FILE"]]}}
    c["task_instruction"]=f"Within AppWorld, open {directory}/dispatch-route.txt. Resolve its policy, recipient and manifest joins, apply the policy-specific selection modes and checksum, then send the one required email. Use only AppWorld file_system and gmail tools; do not modify source files."
    c["public_route"]={"route_file":f"{directory}/dispatch-route.txt","policy_files":[Path(str(r["values"]["tilde_path"])).name for r in policy_rows],"recipient_files":recipient_files,"manifest_files":[Path(str(r["values"]["tilde_path"])).name for r in manifest_rows]}
    c["target_local_resources"]=[f"file_system:{directory}/*",f"gmail:outbound:{prefix}"]
    return c


def tnf_case(i: int) -> dict[str, Any]:
    sid=f"{i:02d}"; c=_fresh_base(v2_tnf(i),i,"TNF");c["kind"]="TNF_SEMANTIC_V3"
    route_row=next(r for r in c["fixture"]["rows"] if r["app"]=="simple_note" and str(r["values"].get("title",""))==f"sq0v3-route-tnf-{sid}")
    policy_rows=[r for r in c["fixture"]["rows"] if r["app"]=="simple_note" and str(r["values"].get("title","")).startswith(f"sq0v3-policy-{sid}-")]
    content_rows=[r for r in c["fixture"]["rows"] if r["app"]=="simple_note" and str(r["values"].get("title","")).startswith(f"sq0v3-content-{sid}-")]
    task_rows=[r for r in c["fixture"]["rows"] if r["app"]=="todoist" and str(r["values"].get("title","")).startswith(f"sq0v3-output-{sid}-")]
    out_dir=str(c["expected"]["output_path"]).rsplit("/",1)[0]+"/"; absolute=out_dir.replace("~/","/home/aaron/")
    cm=["MAX_REV_MIN_SCORE","MAX_SCORE_MAX_REV","CLOSEST_SCORE_MAX_REV"][(i-1)%3]; tm=["MAX_PRIORITY_MIN_TITLE","MAX_WEIGHT_MAX_PRIORITY","MIN_WEIGHT_MAX_PRIORITY"][(i+1)%3]
    pivot=62+i; baseval=30+i; mult=2+i%3; adjkey=f"V3ADJ{sid}"
    for j,r in enumerate(policy_rows):
        d=kv(str(r["values"]["content"])); selected=j==1; d["PHASE"]=f"P{1+i%3}" if selected else f"D{sid}{j}";d["CONTENT_MODE"]=cm if selected else "MAX_REV_MIN_SCORE";d["TASK_MODE"]=tm if selected else "MAX_PRIORITY_MIN_TITLE";d["PIVOT"]=str(pivot if selected else 50);d["BASE"]=str(baseval if selected else 10);d["MULTIPLIER"]=str(mult if selected else 1);d["ADJUST_KEY"]=adjkey if selected else f"DECOYADJ{sid}{j}";r["values"]["content"]="\n".join(f"{k}={v}" for k,v in d.items())
    policy=kv(str(policy_rows[1]["values"]["content"])); route_key=policy["ROUTE_KEY"]
    contents=[]
    for j,r in enumerate(content_rows):
        d=kv(str(r["values"]["content"]));d["PHASE"]=policy["PHASE"] if d["ROUTE_KEY"]==route_key and j!=1 else f"OTHER{sid}{j}";d["SCORE"]=str([55,68,77,61][j]+i);d["TOKEN"]=f"V3C{sid}{chr(65+j)}";r["values"]["content"]="\n".join(f"{k}={v}" for k,v in d.items());d["REVISION"]=int(d["REVISION"]);d["SCORE"]=int(d["SCORE"]);contents.append(d)
    tasks=[]
    for j,r in enumerate(task_rows):
        old=kv(str(r["values"]["description"]).replace(";","\n")); route=old.get("ROUTE_KEY",""); phase=policy["PHASE"] if route==route_key and j!=1 else f"OTHER{sid}{j}";priority=int(old.get("PRIORITY",j+1));weight=[9,3,8,2,7,5][j]+i;d={"TITLE":r["values"]["title"],"ROUTE_KEY":route,"PHASE":phase,"PRIORITY":priority,"WEIGHT":weight};r["values"]["description"]="; ".join(f"{k}={v}" for k,v in d.items() if k!="TITLE");tasks.append(d)
    adjustments=[]; adjustment_files=[]
    for j in range(5):
        name=f"adjust-{j+1:02d}.txt"; rec={"ADJUST_KEY":adjkey if j in {1,4} else f"DECOYADJ{sid}{j}","ACTIVE":"YES" if j!=1 else "NO","RANK":j+1,"DELTA":[3,9,5,7,11][j]+i};adjustments.append(rec);adjustment_files.append(name);c["fixture"]["rows"].append(_row("file_system","files",id=1_650_000+i*100+j,path=f"{absolute}{name}",tilde_path=f"{out_dir}{name}",user_id=99,content="\n".join(f"{k}={v}" for k,v in rec.items())))
    eligible_c=[x for x in contents if x["ROUTE_KEY"]==route_key and x["PHASE"]==policy["PHASE"]];content=choose_content(eligible_c,policy["CONTENT_MODE"],int(policy["PIVOT"]));eligible_t=[x for x in tasks if x["ROUTE_KEY"]==route_key and x["PHASE"]==policy["PHASE"]];task=choose_task(eligible_t,policy["TASK_MODE"]);adj=max((x for x in adjustments if x["ADJUST_KEY"]==adjkey and x["ACTIVE"]=="YES"),key=lambda x:int(x["RANK"]));total=int(policy["BASE"])+content["REVISION"]*int(policy["MULTIPLIER"])+int(task["PRIORITY"])+int(task["WEIGHT"])+int(adj["DELTA"])
    route=(str(route_row["values"]["content"])+f"\nADJUSTMENT_FILES={','.join(adjustment_files)}\n"+"Selected policy also provides PHASE, CONTENT_MODE, TASK_MODE, PIVOT, BASE, MULTIPLIER and ADJUST_KEY. Content and Inbox task must match both ROUTE_KEY and PHASE. CONTENT_MODE: MAX_REV_MIN_SCORE = largest REVISION then smallest SCORE then TOKEN; MAX_SCORE_MAX_REV = largest SCORE then largest REVISION then TOKEN; CLOSEST_SCORE_MAX_REV = smallest absolute SCORE-PIVOT then largest REVISION then TOKEN. TASK_MODE: MAX_PRIORITY_MIN_TITLE = largest PRIORITY then smallest TITLE; MAX_WEIGHT_MAX_PRIORITY = largest WEIGHT then largest PRIORITY then TITLE; MIN_WEIGHT_MAX_PRIORITY = smallest WEIGHT then largest PRIORITY then TITLE. From adjustment files select ACTIVE=YES matching ADJUST_KEY with largest RANK. TOTAL=BASE+(REVISION*MULTIPLIER)+PRIORITY+WEIGHT+DELTA. Filename is TASK_TITLE-PHASE-rREVISION-TOKEN.txt. File content is five logical lines POLICY=POLICY_CODE, PAYLOAD=PAYLOAD, TASK=TASK_TITLE, ADJUST=DELTA, TOTAL=TOTAL. One terminal newline is semantically irrelevant; all internal characters and values remain exact.")
    route_row["values"]["content"]=route
    path=f"{out_dir}{task['TITLE']}-{policy['PHASE']}-r{content['REVISION']}-{content['TOKEN']}.txt"; text=f"POLICY={policy['POLICY_CODE']}\nPAYLOAD={content['PAYLOAD']}\nTASK={task['TITLE']}\nADJUST={adj['DELTA']}\nTOTAL={total}";c["expected"]={"output_path":path,"output_content":text};c["task_instruction"]=f"Within AppWorld, read routing note sq0v3-route-tnf-{sid}. Resolve its policy/content/Inbox-task/adjustment joins and dynamic modes exactly, then create the required output file. Use only AppWorld simple_note, todoist and file_system tools; do not modify notes or todos.";c["public_route"]={"route_note_title":f"sq0v3-route-tnf-{sid}","policy_titles":[r["values"]["title"] for r in policy_rows],"content_titles":[r["values"]["title"] for r in content_rows],"adjustment_files":adjustment_files};c["target_local_resources"]=[f"simple_note:sq0v3-route-tnf-{sid}",f"simple_note:sq0v3-policy-{sid}-*",f"simple_note:sq0v3-content-{sid}-*","todoist:Inbox",f"file_system:{out_dir}*"]
    return c


def build_cases() -> list[dict[str, Any]]:
    return [fg_case(i) for i in range(1,7)] + [tnf_case(i) for i in range(1,7)]


def evaluate_case_from_state(case: dict[str, Any], *, source_db_root: Path, changes_db_root: Path, measurement_root: Path) -> bool:
    required={"gmail":{"emails","attachments","users"},"file_system":{"files"}} if case["kind"].startswith("FG_") else {"file_system":{"files"}}
    materialize_appworld_measurement_state(source_db_root=source_db_root,changes_db_root=changes_db_root,measurement_db_root=measurement_root,required_tables_by_app=required)
    if case["kind"].startswith("FG_"):
        e=case["expected"];con=sqlite3.connect(measurement_root/"gmail.db")
        try:
            rec=con.execute("SELECT id FROM users WHERE email=?",(e["recipient"],)).fetchone()
            if rec is None:return False
            mails=con.execute("SELECT id,recipient_ids,subject,body FROM emails WHERE sender_id=99 AND subject=?",(e["subject"],)).fetchall()
            if len(mails)!=1:return False
            eid,rids,subject,body=mails[0]
            if json.loads(rids)!=[int(rec[0])] or subject!=e["subject"] or body!=e["body"]:return False
            att=con.execute("SELECT file_name,file_content FROM attachments WHERE email_id=? ORDER BY file_name",(eid,)).fetchall()
            return len(att)==2 and {str(n):str(v) for n,v in att}==e["attachment_contents"]
        finally:con.close()
    con=sqlite3.connect(measurement_root/"file_system.db")
    try:
        row=con.execute("SELECT content FROM files WHERE tilde_path=? AND user_id=99",(case["expected"]["output_path"],)).fetchone()
        return row is not None and str(row[0]).rstrip("\n")==str(case["expected"]["output_content"]).rstrip("\n")
    finally:con.close()
