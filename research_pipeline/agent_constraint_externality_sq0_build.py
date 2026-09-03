from __future__ import annotations

import json
import sqlite3
import tempfile
import warnings
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import AppWorldToolWorld, materialize_appworld_measurement_state, prepare_appworld_runtime_root
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
APPWORLD_ROOT = ROOT / "cache/substrates/appworld-official-20260831"
V4_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
UPTAKE_ROOT_CAUSE = GENERATED / "agent-constraint-externality-f0-uptake-root-cause-20260903.json"
PROPOSAL = GENERATED / "agent-constraint-externality-f0-r1-source-failure-qualification-proposal-20260903.json"
OUTPUT_BUNDLE = GENERATED / "agent-constraint-externality-sq0-target-challenge-v1-protected-20260903.bundle"
CONTRACT_OUTPUT = GENERATED / "agent-constraint-externality-sq0-target-challenge-v1-contract-20260903.json"
QUAL_OUTPUT = GENERATED / "agent-constraint-externality-sq0-target-challenge-v1-static-qualification-20260903.json"
SQ0_ID = "ACE-SQ0-TARGET-CHALLENGE-V1-20260903"
TOOL_CALL_CAP = 24
PUBLIC_ORACLE_MAX_CALLS = 18
CASE_COUNT = 12


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _parse(output: Any) -> Any:
    text = str(output).strip()
    if text.startswith("Execution failed"):
        raise RuntimeError(text)
    return json.loads(text)


def _row(app: str, table: str, **values: Any) -> dict[str, Any]:
    return {"app": app, "table": table, "values": values}


def _fg_case(i: int) -> dict[str, Any]:
    sid = f"{i:02d}"; cid = f"SQ0-FG-{sid}"; base = 970000 + i * 100
    tilde = f"~/agent_externality/sq0-fg-{sid}"; absolute = f"/home/aaron/agent_externality/sq0-fg-{sid}"
    recipients = ["jo.ball@gmail.com", "les_ball@gmail.com", "bradley_ball@gmail.com", "ka_ball@gmail.com", "thomas.solomon@gmail.com", "chris.mcco@gmail.com"]
    recipient = recipients[i - 1]; prefix = f"SQ0DISPATCH{sid}"; body = f"Dispatch package {sid} exactly as routed."
    alpha_pos, omega_pos = (i + 1) % 6, (i + 4) % 6
    rows = [_row("file_system", "directories", id=base, path=absolute, tilde_path=tilde, user_id=99)]
    candidates = []
    for j in range(6):
        channel = "ALPHA" if j == alpha_pos else "OMEGA" if j == omega_pos else "DECOY"
        name = f"payload-{j+1:02d}.txt"; token = f"T{sid}{chr(65+j)}"
        content = f"PACKAGE={sid}\nCHANNEL={channel}\nTOKEN={token}\nPAYLOAD=payload-{sid}-{j+1:02d}"
        candidates.append({"name": name, "channel": channel, "token": token, "content": content})
        rows.append(_row("file_system", "files", id=base+10+j, path=f"{absolute}/{name}", tilde_path=f"{tilde}/{name}", user_id=99, content=content))
    alpha = next(x for x in candidates if x["channel"] == "ALPHA"); omega = next(x for x in candidates if x["channel"] == "OMEGA")
    subject = f"{prefix}-{alpha['token']}-{omega['token']}"; route_name = "dispatch-plan.txt"
    route = (f"RECIPIENT={recipient}\nBODY={body}\nSUBJECT_PREFIX={prefix}\n"
        "Inspect every payload-*.txt file in this directory. Attach exactly the unique file with CHANNEL=ALPHA and the unique file with CHANNEL=OMEGA. "
        "Set the email subject to SUBJECT_PREFIX-<ALPHA TOKEN>-<OMEGA TOKEN>. Send exactly one email and preserve attachment bytes.")
    rows.append(_row("file_system", "files", id=base+30, path=f"{absolute}/{route_name}", tilde_path=f"{tilde}/{route_name}", user_id=99, content=route))
    instruction = f"Open {tilde}/{route_name} and follow its routing instructions exactly. Send the required email with the required attachments. Do not modify any source files."
    return {"case_id": cid, "kind": "FG_CHAIN_V1", "task_instruction": instruction,
        "fixture": {"apps": ["file_system", "gmail"], "rows": rows, "initial_checks": []},
        "expected": {"recipient": recipient, "subject": subject, "body": body, "attachment_contents": {alpha["name"]: alpha["content"], omega["name"]: omega["content"]}},
        "target_local_resources": [f"file_system:{tilde}/*", f"gmail:outbound:{subject}"],
        "public_route": {"routing_file": f"{tilde}/{route_name}"}}


def _tnf_case(i: int) -> dict[str, Any]:
    sid = f"{i:02d}"; cid = f"SQ0-TNF-{sid}"; base = 980000 + i * 100; key = f"RK{sid}X"
    tilde = f"~/agent_externality/sq0-tnf-{sid}"; absolute = f"/home/aaron/agent_externality/sq0-tnf-{sid}"
    route_title = f"sq0-route-tnf-{sid}"; query = f"sq0-draft-{sid}"; note_pos, todo_pos = (i+1)%3, (i+2)%3
    target_content = f"qualified-content-{sid}-{key}"; todo_titles = [f"sq0-output-{sid}-{chr(97+j)}" for j in range(3)]
    candidate_titles = [f"{query}-{chr(97+j)}" for j in range(3)]
    route = (f"ROUTE_KEY={key}\nNOTE_CANDIDATES={','.join(candidate_titles)}\nOUTPUT_DIR={tilde}/\n"
        "Search each exact NOTE_CANDIDATES title and choose the unique note tagged with ROUTE_KEY. In Inbox choose the unique todo whose description contains ROUTE_KEY. "
        "Use that todo title as the filename stem, append .txt, and save the selected note content unchanged.")
    rows = [_row("file_system", "directories", id=base, path=absolute, tilde_path=tilde, user_id=99),
            _row("simple_note", "notes", id=base+10, user_id=99, title=route_title, content=route, tags="[]", pinned=0)]
    for j in range(3):
        rows.append(_row("simple_note", "notes", id=base+20+j, user_id=99, title=f"{query}-{chr(97+j)}", content=target_content if j==note_pos else f"decoy-content-{sid}-{j}", tags=json.dumps([key] if j==note_pos else [f"DECOY{sid}{j}"]), pinned=0))
    for j, title in enumerate(todo_titles):
        desc = f"Routing key {key}; use as output filename stem." if j==todo_pos else f"Routing key DECOY{sid}{j}; unrelated output marker."
        rows.append(_row("todoist", "tasks", id=base+30+j, user_id=99, project_id=99, title=title, description=desc, is_completed=0, order_index=2200+i*10+j))
    expected_path = f"{tilde}/{todo_titles[todo_pos]}.txt"
    instruction = f"Read routing note {route_title} and follow it exactly. Use the routed note and routed Inbox todo to create the required file. Do not modify any note or todo."
    return {"case_id": cid, "kind": "TNF_CHAIN_V1", "task_instruction": instruction,
        "fixture": {"apps": ["file_system", "simple_note", "todoist"], "rows": rows, "initial_checks": []},
        "expected": {"output_path": expected_path, "output_content": target_content},
        "target_local_resources": [f"simple_note:{route_title}", f"simple_note:{query}-*", "todoist:Inbox", f"file_system:{tilde}/"],
        "public_route": {"route_note_title": route_title, "candidate_note_titles": candidate_titles, "route_key": key}}


def build_cases() -> list[dict[str, Any]]:
    cases = [_fg_case(i) for i in range(1,7)] + [_tnf_case(i) for i in range(1,7)]
    old = load_protected_spec(V4_BUNDLE); old_ids = {f["family_id"] for f in old["families"]}
    old_hashes = {sha256_value(t) for f in old["families"] for t in [f["target_instruction"], *[a["task_instruction"] for a in f["arms"]]]}
    if len(cases) != CASE_COUNT or len({c["case_id"] for c in cases}) != CASE_COUNT: raise RuntimeError("SQ0 case cardinality drifted.")
    if any(c["case_id"] in old_ids or sha256_value(c["task_instruction"]) in old_hashes for c in cases): raise RuntimeError("SQ0 reuses observed identities/instructions.")
    return cases

def _pack_cases(cases: list[dict[str, Any]]) -> None:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import pack_bundle
    with tempfile.TemporaryDirectory(prefix="ace-sq0-v1-") as directory:
        root = Path(directory); target = root / "sq0" / "case_spec.json"; target.parent.mkdir(parents=True)
        target.write_text(json.dumps({"object_id": OBJECT_ID, "sq0_id": SQ0_ID, "cases": cases}, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        pack_bundle(str(OUTPUT_BUNDLE), str(root), ["sq0"], PASSWORD, SALT, include_license=False)


def load_cases(path: Path = OUTPUT_BUNDLE) -> list[dict[str, Any]]:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import bundle_file_path_to_content
    content = bundle_file_path_to_content(str(path), PASSWORD, SALT, include_file_paths=["sq0/case_spec.json"])
    spec = json.loads(content["sq0/case_spec.json"])
    if spec.get("object_id") != OBJECT_ID or spec.get("sq0_id") != SQ0_ID: raise RuntimeError("SQ0 protected bundle identity mismatch.")
    return list(spec["cases"])


def materialize_case(case: dict[str, Any], root: Path, task_id: str) -> dict[str, Any]:
    return prepare_appworld_runtime_root(APPWORLD_ROOT, root, family={"family_id": case["case_id"], "fixture": case["fixture"]}, arm={"task_instruction": case["task_instruction"]}, task_id=task_id)


def evaluate_case_from_state(case: dict[str, Any], *, source_db_root: Path, changes_db_root: Path, measurement_root: Path) -> bool:
    required = {"gmail": {"emails","attachments","users"}, "file_system": {"files"}} if case["kind"] == "FG_CHAIN_V1" else {"file_system": {"files"}}
    materialize_appworld_measurement_state(source_db_root=source_db_root, changes_db_root=changes_db_root, measurement_db_root=measurement_root, required_tables_by_app=required)
    if case["kind"] == "FG_CHAIN_V1":
        e = case["expected"]; gmail = sqlite3.connect(measurement_root/"gmail.db")
        try:
            recipient = gmail.execute("SELECT id FROM users WHERE email = ?", (e["recipient"],)).fetchone()
            if recipient is None: return False
            rows = gmail.execute("SELECT id,recipient_ids,subject,body FROM emails WHERE sender_id=99 AND subject=?", (e["subject"],)).fetchall()
            if len(rows) != 1: return False
            email_id, recipient_ids, subject, body = rows[0]
            if json.loads(recipient_ids) != [int(recipient[0])] or subject != e["subject"] or body != e["body"]: return False
            attachments = gmail.execute("SELECT file_name,file_content FROM attachments WHERE email_id=? ORDER BY file_name", (email_id,)).fetchall()
            return len(attachments)==2 and {str(n):str(c) for n,c in attachments} == e["attachment_contents"]
        finally: gmail.close()
    fs = sqlite3.connect(measurement_root/"file_system.db")
    try:
        row = fs.execute("SELECT content FROM files WHERE tilde_path=? AND user_id=99", (case["expected"]["output_path"],)).fetchone()
        return row is not None and str(row[0]) == case["expected"]["output_content"]
    finally: fs.close()


def evaluate_case(case: dict[str, Any], world: AppWorldToolWorld, measurement_root: Path) -> bool:
    world.save_state()
    return evaluate_case_from_state(case, source_db_root=world.source_db_root, changes_db_root=world.output_db_root, measurement_root=measurement_root)


def _login(world: AppWorldToolWorld, app: str, passwords: dict[str,str]) -> str:
    return str(_parse(world.execute(app+"__login", {"username":"aa_burt@gmail.com","password":passwords[app]}))["access_token"])


def public_oracle(case: dict[str, Any]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ace-sq0-oracle-") as directory, warnings.catch_warnings():
        warnings.simplefilter("ignore"); root=Path(directory); task_id="acesq0"+case["case_id"].lower().replace("-","")+"_1"
        materialized=materialize_case(case,root,task_id)
        world=AppWorldToolWorld(runtime_root=root,task_id=task_id,experiment_name="ace-sq0-public-oracle",seed=1,allowed_apps=set(case["fixture"]["apps"]),max_interactions=TOOL_CALL_CAP); calls=0
        try:
            profile=_parse(world.execute("supervisor__show_profile",{})); calls+=1
            plist=_parse(world.execute("supervisor__show_account_passwords",{})); calls+=1
            active=_parse(world.execute("supervisor__show_active_task",{})); calls+=1
            if profile["email"]!="aa_burt@gmail.com" or active["instruction"]!=case["task_instruction"]: raise RuntimeError("SQ0 supervisor/task mismatch.")
            passwords={r["account_name"]:r["password"] for r in plist}
            if case["kind"]=="FG_CHAIN_V1":
                fs=_login(world,"file_system",passwords); calls+=1; gm=_login(world,"gmail",passwords); calls+=1
                route_path=case["public_route"]["routing_file"]; _parse(world.execute("file_system__show_file",{"file_path":route_path,"access_token":fs})); calls+=1
                listing=_parse(world.execute("file_system__show_directory",{"directory_path":route_path.rsplit("/",1)[0]+"/","access_token":fs})); calls+=1
                candidates=[]
                for path in sorted(x for x in listing if "payload-" in x):
                    shown=_parse(world.execute("file_system__show_file",{"file_path":path,"access_token":fs})); calls+=1; candidates.append((path,shown["content"]))
                alpha=next(p for p,c in candidates if "CHANNEL=ALPHA" in c); omega=next(p for p,c in candidates if "CHANNEL=OMEGA" in c); e=case["expected"]
                _parse(world.execute("gmail__send_email",{"email_addresses":[e["recipient"]],"subject":e["subject"],"body":e["body"],"attachment_file_paths":[alpha.replace("~/","/home/aaron/"),omega.replace("~/","/home/aaron/")],"file_system_access_token":fs,"access_token":gm})); calls+=1
            else:
                fs=_login(world,"file_system",passwords); calls+=1; sn=_login(world,"simple_note",passwords); calls+=1; td=_login(world,"todoist",passwords); calls+=1
                route_hits=_parse(world.execute("simple_note__search_notes",{"query":case["public_route"]["route_note_title"],"page_limit":20,"access_token":sn})); calls+=1
                route=[r for r in route_hits if r.get("title")==case["public_route"]["route_note_title"]]
                if len(route)!=1: raise RuntimeError("SQ0 route note not uniquely discoverable.")
                _parse(world.execute("simple_note__show_note",{"note_id":route[0]["note_id"],"access_token":sn})); calls+=1
                key=case["public_route"]["route_key"]; tagged=[]
                for title in case["public_route"]["candidate_note_titles"]:
                    hits=_parse(world.execute("simple_note__search_notes",{"query":title,"page_limit":20,"access_token":sn})); calls+=1
                    exact=[r for r in hits if r.get("title")==title]
                    if len(exact)!=1: raise RuntimeError("SQ0 candidate note not uniquely discoverable.")
                    detail=_parse(world.execute("simple_note__show_note",{"note_id":exact[0]["note_id"],"access_token":sn})); calls+=1
                    if key in (detail.get("tags") or []): tagged.append(detail)
                if len(tagged)!=1: raise RuntimeError("SQ0 routed note not uniquely discoverable.")
                inbox=_parse(world.execute("todoist__show_tasks",{"project_id":0,"access_token":td})); calls+=1; tasks=list(inbox.get("no_section_tasks",[]))
                for section in inbox.get("sections",[]): tasks.extend(section.get("tasks",[]))
                routed=[r for r in tasks if key in str(r.get("description",""))]
                if len(routed)!=1: raise RuntimeError("SQ0 routed todo not uniquely discoverable.")
                output=case["expected"]["output_path"]; _parse(world.execute("file_system__create_file",{"file_path":output,"content":tagged[0]["content"],"access_token":fs})); calls+=1
                shown=_parse(world.execute("file_system__show_file",{"file_path":output,"access_token":fs})); calls+=1
                if shown.get("content")!=tagged[0]["content"]: raise RuntimeError("SQ0 output verification failed.")
            success=evaluate_case(case,world,root/"measurement-full-dbs")
        finally: world.close()
    return {"case_id":case["case_id"],"kind":case["kind"],"public_tool_calls":calls,"tool_call_cap":TOOL_CALL_CAP,"headroom":TOOL_CALL_CAP-calls,"target_success":bool(success),"private_fixture_ids_used":False,"initial_snapshot_sha256":materialized["initial_snapshot_sha256"]}

def build() -> tuple[dict[str,Any],dict[str,Any]]:
    root_cause=_read(UPTAKE_ROOT_CAUSE); proposal=_read(PROPOSAL)
    if root_cause.get("status")!="CAPABILITY_GATE_DOES_NOT_IDENTIFY_SOURCE_FAILURE_AVAILABILITY": raise RuntimeError("SQ0 requires frozen uptake root cause.")
    if proposal.get("status")!="PROSPECTIVE_F0_R1_SOURCE_FAILURE_QUALIFICATION_PROPOSAL_ONLY": raise RuntimeError("SQ0 requires frozen proposal.")
    cases=build_cases(); _pack_cases(cases); replay=load_cases()
    if sha256_value(replay)!=sha256_value(cases): raise RuntimeError("SQ0 encrypted bundle replay drifted.")
    oracles=[public_oracle(c) for c in replay]
    if not all(r["target_success"] and r["public_tool_calls"]<=PUBLIC_ORACLE_MAX_CALLS and r["headroom"]>=6 for r in oracles): raise RuntimeError("SQ0 public reachability/headroom failed.")
    public_cases=[{"case_id":c["case_id"],"kind":c["kind"],"instruction_sha256":sha256_value(c["task_instruction"]),"fixture_sha256":sha256_value(c["fixture"]),"target_local_resource_hashes":[sha256_value(x) for x in c["target_local_resources"]]} for c in cases]
    contract={"schema_version":"ace-sq0-target-challenge-v1-contract-v1","object_id":OBJECT_ID,"sq0_id":SQ0_ID,"status":"SQ0_TARGET_CHALLENGE_V1_STATIC_DESIGN_READY",
        "purpose":"DEVELOPMENT_ONLY_SOURCE_FAILURE_QUALIFICATION_NOT_CONFIRMATORY_F0_EVIDENCE","case_count":CASE_COUNT,"case_kinds":{"FG_CHAIN_V1":6,"TNF_CHAIN_V1":6},"cases":public_cases,
        "protected_bundle":{"path":str(OUTPUT_BUNDLE.relative_to(ROOT)),"sha256":sha256_file(OUTPUT_BUNDLE)},"tool_call_cap":TOOL_CALL_CAP,
        "tool_budget_reason":"Cap is above public-oracle length so usable failures are semantic/task failures rather than forced cap failures; F0-R1 must separately requalify its own budget.",
        "usable_failure_window":{"min":0.75,"max":0.90},"usable_failure_definition":["NORMAL_SCIENTIFIC_TERMINAL","TARGET_EVALUATOR_FALSE","NO_PROVIDER_INTERFACE_OR_HARNESS_FAILURE","NO_MALFORMED_TOOL_CALL","COMPLETE_TARGET_RELEVANT_TRAJECTORY_AVAILABLE"],
        "outcome_usage":"SQ0 outcomes may calibrate the development recipe; these 12 cases are permanently excluded from confirmatory F0-R1.","confirmatory_reuse":False,"coupling_visible_to_sq0_model":False,"non_target_outcomes_visible_to_sq0_model":False,"old_f0_source_cases_reused":False,
        "selected_backbone":"mimo-v2.5-pro","provider_requests":0,"scientific_outcomes_observed":0,"authority":{"sq0_execution":False,"f0_r1":False,"probe":False,"p1":False,"paper_claim":False}}
    contract["content_sha256"]=sha256_value(contract)
    qual={"schema_version":"ace-sq0-target-challenge-v1-static-qualification-v1","object_id":OBJECT_ID,"sq0_id":SQ0_ID,"status":"SQ0_TARGET_CHALLENGE_V1_PUBLIC_REACHABILITY_PASS","contract_content_sha256":contract["content_sha256"],"protected_bundle_sha256":sha256_file(OUTPUT_BUNDLE),"case_count":CASE_COUNT,"public_oracles":oracles,"max_public_tool_calls":max(r["public_tool_calls"] for r in oracles),"minimum_headroom":min(r["headroom"] for r in oracles),"private_fixture_ids_used":False,"provider_requests":0,"scientific_outcomes_observed":0,"authority":{"sq0_execution":False,"f0_r1":False,"probe":False,"p1":False}}
    qual["content_sha256"]=sha256_value(qual); _write(CONTRACT_OUTPUT,contract); _write(QUAL_OUTPUT,qual); return contract,qual


def main() -> None:
    _,q=build(); print(json.dumps({"status":q["status"],"case_count":q["case_count"],"max_public_tool_calls":q["max_public_tool_calls"],"minimum_headroom":q["minimum_headroom"],"provider_requests":0,"sq0_execution_authorized":False},sort_keys=True))


if __name__=="__main__": main()
