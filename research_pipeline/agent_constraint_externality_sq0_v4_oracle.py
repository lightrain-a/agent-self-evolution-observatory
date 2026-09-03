from __future__ import annotations

import tempfile
import warnings
from datetime import date
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import AppWorldToolWorld
from research_pipeline.agent_constraint_externality_sq0_build import _login, _parse, materialize_case
from research_pipeline.agent_constraint_externality_sq0_v4_cases import (
    _choose_modifier,
    choose_content,
    choose_manifest,
    choose_task,
    evaluate_case_from_state,
    kv,
)

TOOL_CALL_CAP = 80


def _show_note(world: AppWorldToolWorld, title: str, token: str) -> tuple[dict[str, Any], int]:
    hits = _parse(world.execute("simple_note__search_notes", {"query": title, "page_limit": 20, "access_token": token}))
    exact = [r for r in hits if r.get("title") == title]
    if len(exact) != 1:
        raise RuntimeError(f"V4 note not uniquely discoverable: {title}")
    return _parse(world.execute("simple_note__show_note", {"note_id": exact[0]["note_id"], "access_token": token})), 2


def public_oracle(case: dict[str, Any]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ace-sq0-v4-oracle-") as directory, warnings.catch_warnings():
        warnings.simplefilter("ignore")
        root = Path(directory)
        task_id = "acesq0v4" + case["case_id"].lower().replace("-", "") + "_1"
        materialized = materialize_case(case, root, task_id)
        world = AppWorldToolWorld(
            runtime_root=root,
            task_id=task_id,
            experiment_name="ace-sq0-v4-public-oracle",
            seed=1,
            allowed_apps=set(case["fixture"]["apps"]),
            max_interactions=TOOL_CALL_CAP,
        )
        calls = 0
        try:
            profile = _parse(world.execute("supervisor__show_profile", {})); calls += 1
            plist = _parse(world.execute("supervisor__show_account_passwords", {})); calls += 1
            active = _parse(world.execute("supervisor__show_active_task", {})); calls += 1
            if profile["email"] != "aa_burt@gmail.com" or active["instruction"] != case["task_instruction"]:
                raise RuntimeError("V4 supervisor/task mismatch.")
            passwords = {r["account_name"]: r["password"] for r in plist}
            if case["kind"].startswith("FG_"):
                fs = _login(world, "file_system", passwords); calls += 1
                gm = _login(world, "gmail", passwords); calls += 1
                base = case["public_route"]["route_file"].rsplit("/", 1)[0] + "/"
                route = _parse(world.execute("file_system__show_file", {"file_path": case["public_route"]["route_file"], "access_token": fs})); calls += 1
                rk = kv(route["content"])
                policies = []
                for name in case["public_route"]["policy_files"]:
                    x = _parse(world.execute("file_system__show_file", {"file_path": base + name, "access_token": fs})); calls += 1
                    p = kv(x["content"]); p["MIN_SCORE"] = int(p["MIN_SCORE"]); p["PIVOT"] = int(p["PIVOT"]); p["W1"] = int(p["W1"]); p["W2"] = int(p["W2"]); p["MOD"] = int(p["MOD"]); policies.append(p)
                cutoff = date.fromisoformat(rk["CUTOFF"])
                policy = max((p for p in policies if p["PROJECT"] == rk["PROJECT"] and p["ACTIVE"] == "YES" and date.fromisoformat(p["EFFECTIVE"]) <= cutoff), key=lambda p: date.fromisoformat(p["EFFECTIVE"]))
                recipients = []
                for name in case["public_route"]["recipient_files"]:
                    x = _parse(world.execute("file_system__show_file", {"file_path": base + name, "access_token": fs})); calls += 1
                    r = kv(x["content"]); r["PRIORITY"] = int(r["PRIORITY"]); recipients.append(r)
                recipient = max((r for r in recipients if r["ROUTE_KEY"] == policy["ROUTE_KEY"] and r["ACTIVE"] == "YES"), key=lambda r: (r["PRIORITY"], r["EMAIL"]))
                manifests = []
                for name in case["public_route"]["manifest_files"]:
                    x = _parse(world.execute("file_system__show_file", {"file_path": base + name, "access_token": fs})); calls += 1
                    m = kv(x["content"]); m["SCORE"] = int(m["SCORE"]); manifests.append(m)
                valid = [m for m in manifests if m["REGION"] == policy["REGION"] and m["ROUTE_KEY"] == policy["ROUTE_KEY"] and m["SCORE"] >= policy["MIN_SCORE"]]
                primary = choose_manifest([m for m in valid if m["ROLE"] == "PRIMARY"], policy["PRIMARY_MODE"], policy["PIVOT"])
                secondary = choose_manifest([m for m in valid if m["ROLE"] == "SECONDARY"], policy["SECONDARY_MODE"], policy["PIVOT"])
                check = (primary["SCORE"] * policy["W1"] + secondary["SCORE"] * policy["W2"] + recipient["PRIORITY"]) % policy["MOD"]
                subject = f"{rk['SUBJECT_PREFIX']}-{policy['POLICY_CODE']}-{primary['TOKEN']}-{secondary['TOKEN']}-{check:02d}"
                _parse(world.execute("gmail__send_email", {
                    "email_addresses": [recipient["EMAIL"]], "subject": subject, "body": rk["BODY"],
                    "attachment_file_paths": [(base + primary["PAYLOAD_FILE"]).replace("~/", "/home/aaron/"), (base + secondary["PAYLOAD_FILE"]).replace("~/", "/home/aaron/")],
                    "file_system_access_token": fs, "access_token": gm,
                })); calls += 1
            else:
                fs = _login(world, "file_system", passwords); calls += 1
                sn = _login(world, "simple_note", passwords); calls += 1
                td = _login(world, "todoist", passwords); calls += 1
                route, n = _show_note(world, case["public_route"]["route_note_title"], sn); calls += n
                rk = kv(route["content"])
                policies = []
                for title in case["public_route"]["policy_titles"]:
                    x, n = _show_note(world, title, sn); calls += n
                    p = kv(x["content"])
                    for key in ("EPOCH", "POLICY_PRIORITY", "PIVOT", "MODIFIER_PIVOT", "BASE", "WA", "WB", "MOD"):
                        p[key] = int(p[key])
                    policies.append(p)
                cutoff = int(rk["CUTOFF_EPOCH"])
                policy = max(
                    (p for p in policies if p["ACTIVE"] == "YES" and p["TIER"] == rk["REQUIRED_TIER"] and p["EPOCH"] <= cutoff),
                    key=lambda p: (p["EPOCH"], p["POLICY_PRIORITY"], p["POLICY_CODE"]),
                )
                contents = []
                for title in case["public_route"]["content_titles"]:
                    x, n = _show_note(world, title, sn); calls += n
                    c = kv(x["content"]); c["REVISION"] = int(c["REVISION"]); c["SCORE"] = int(c["SCORE"]); contents.append(c)
                eligible = [c for c in contents if c["ROUTE_KEY"] == policy["ROUTE_KEY"] and c["PHASE"] == policy["PHASE"]]
                primary = choose_content([c for c in eligible if c["ROLE"] == "PRIMARY"], policy["PRIMARY_CONTENT_MODE"], policy["PIVOT"])
                secondary = choose_content([c for c in eligible if c["ROLE"] == "SECONDARY"], policy["SECONDARY_CONTENT_MODE"], policy["PIVOT"])
                inbox = _parse(world.execute("todoist__show_tasks", {"project_id": 0, "access_token": td})); calls += 1
                all_tasks = list(inbox.get("no_section_tasks", []))
                for sec in inbox.get("sections", []): all_tasks.extend(sec.get("tasks", []))
                tasks = []
                for task in all_tasks:
                    d = kv(str(task.get("description", "")).replace(";", "\n"))
                    if d.get("ROUTE_KEY") == policy["ROUTE_KEY"] and d.get("PHASE") == policy["PHASE"]:
                        tasks.append({"TITLE": task["title"], "ROUTE_KEY": d["ROUTE_KEY"], "PHASE": d["PHASE"], "PRIORITY": int(d["PRIORITY"]), "WEIGHT": int(d["WEIGHT"])})
                task = choose_task(tasks, policy["TASK_MODE"])
                adjustments = []
                for name in case["public_route"]["adjustment_files"]:
                    x = _parse(world.execute("file_system__show_file", {"file_path": rk["OUTPUT_DIR"] + name, "access_token": fs})); calls += 1
                    a = kv(x["content"]); a["RANK"] = int(a["RANK"]); a["DELTA"] = int(a["DELTA"]); adjustments.append(a)
                adj = max((a for a in adjustments if a["ADJUST_KEY"] == policy["ADJUST_KEY"] and a["ACTIVE"] == "YES"), key=lambda a: a["RANK"])
                modifiers = []
                for name in case["public_route"]["modifier_files"]:
                    x = _parse(world.execute("file_system__show_file", {"file_path": rk["OUTPUT_DIR"] + name, "access_token": fs})); calls += 1
                    m = kv(x["content"]); m["RANK"] = int(m["RANK"]); m["VALUE"] = int(m["VALUE"]); modifiers.append(m)
                modifier = _choose_modifier([m for m in modifiers if m["MOD_KEY"] == policy["MOD_KEY"] and m["ACTIVE"] == "YES"], policy["MODIFIER_MODE"], policy["MODIFIER_PIVOT"])
                total = (policy["BASE"] + primary["REVISION"] * policy["WA"] + secondary["SCORE"] * policy["WB"] + task["PRIORITY"] + task["WEIGHT"] + adj["DELTA"] + modifier["VALUE"]) % policy["MOD"]
                path = f"{rk['OUTPUT_DIR']}{task['TITLE']}-{policy['PHASE']}-{primary['TOKEN']}-{secondary['TOKEN']}-{modifier['TOKEN']}.txt"
                text = f"POLICY={policy['POLICY_CODE']}\nPRIMARY={primary['TOKEN']}:{primary['PAYLOAD']}\nSECONDARY={secondary['TOKEN']}:{secondary['PAYLOAD']}\nTASK={task['TITLE']}\nADJUST={adj['DELTA']}\nMODIFIER={modifier['TOKEN']}:{modifier['VALUE']}\nTOTAL={total}"
                _parse(world.execute("file_system__create_file", {"file_path": path, "content": text, "access_token": fs})); calls += 1
                shown = _parse(world.execute("file_system__show_file", {"file_path": path, "access_token": fs})); calls += 1
                if str(shown.get("content", "")).rstrip("\n") != text.rstrip("\n"):
                    raise RuntimeError("V4 oracle output verification failed.")
            world.save_state()
            success = evaluate_case_from_state(case, source_db_root=world.source_db_root, changes_db_root=world.output_db_root, measurement_root=root / "measurement-full-dbs")
        finally:
            world.close()
    return {
        "case_id": case["case_id"], "kind": case["kind"], "public_tool_calls": calls,
        "tool_call_cap": TOOL_CALL_CAP, "headroom": TOOL_CALL_CAP - calls,
        "target_success": bool(success), "private_fixture_ids_used": False,
        "initial_snapshot_sha256": materialized["initial_snapshot_sha256"],
    }
