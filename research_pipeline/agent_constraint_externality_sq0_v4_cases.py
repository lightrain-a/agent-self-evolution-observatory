from __future__ import annotations

import copy
import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_appworld_runtime import materialize_appworld_measurement_state
from research_pipeline.agent_constraint_externality_sq0_build import _row
from research_pipeline.agent_constraint_externality_sq0_v3_cases import (
    choose_content,
    choose_manifest,
    choose_task,
    evaluate_case_from_state,
    fg_case as v3_fg_case,
    kv,
)


def _replace(obj: Any, pairs: list[tuple[str, str]]) -> Any:
    if isinstance(obj, str):
        for old, new in pairs:
            obj = obj.replace(old, new)
        return obj
    if isinstance(obj, list):
        return [_replace(x, pairs) for x in obj]
    if isinstance(obj, dict):
        return {k: _replace(v, pairs) for k, v in obj.items()}
    return obj


def _dump_kv(d: dict[str, Any]) -> str:
    return "\n".join(f"{k}={v}" for k, v in d.items())


def fg_case(i: int) -> dict[str, Any]:
    sid = f"{i:02d}"
    c = _replace(
        copy.deepcopy(v3_fg_case(i)),
        [
            ("SQ0V3-", "SQ0V4-"),
            ("sq0v3-", "sq0v4-"),
            ("V3FG", "V4FG"),
            ("V3R", "V4R"),
            ("v3-qualified-blob-", "v4-qualified-blob-"),
        ],
    )
    c["case_id"] = f"SQ0V4-FG-{sid}"
    c["kind"] = "FG_SEMANTIC_V4"
    for row in c["fixture"]["rows"]:
        values = row["values"]
        if isinstance(values.get("id"), int):
            values["id"] += 2_000_000
        if isinstance(values.get("order_index"), int):
            values["order_index"] += 20_000

    route_row = next(
        r for r in c["fixture"]["rows"]
        if r["app"] == "file_system" and str(r["values"].get("tilde_path", "")).endswith("/dispatch-route.txt")
    )
    policy_rows = [
        r for r in c["fixture"]["rows"]
        if r["app"] == "file_system" and Path(str(r["values"].get("tilde_path", ""))).name.startswith("policy-")
    ]
    manifest_rows = [
        r for r in c["fixture"]["rows"]
        if r["app"] == "file_system" and Path(str(r["values"].get("tilde_path", ""))).name.startswith("manifest-")
    ]
    recipient_rows = [
        r for r in c["fixture"]["rows"]
        if r["app"] == "file_system" and Path(str(r["values"].get("tilde_path", ""))).name.startswith("recipient-")
    ]
    selected_policy_row = next(r for r in policy_rows if Path(str(r["values"]["tilde_path"])).name == "policy-b.txt")
    pd = kv(str(selected_policy_row["values"]["content"]))
    pd["PIVOT"] = str(int(pd["PIVOT"]) + 3 + (i % 2))
    pd["W1"] = str(4 + (i % 4))
    pd["W2"] = str(7 - (i % 3))
    selected_policy_row["values"]["content"] = _dump_kv(pd)

    for j, row in enumerate(manifest_rows):
        d = kv(str(row["values"]["content"]))
        d["SCORE"] = str(int(d["SCORE"]) + ((j * 3 + i) % 5) - 2)
        d["TOKEN"] = str(d["TOKEN"]).replace("K", "Q", 1)
        row["values"]["content"] = _dump_kv(d)
    for j, row in enumerate(recipient_rows):
        d = kv(str(row["values"]["content"]))
        d["PRIORITY"] = str(int(d["PRIORITY"]) + ((j + i) % 3))
        row["values"]["content"] = _dump_kv(d)

    rk = kv(str(route_row["values"]["content"]))
    policies = []
    for row in policy_rows:
        d = kv(str(row["values"]["content"])); d["MIN_SCORE"] = int(d["MIN_SCORE"]); d["PIVOT"] = int(d["PIVOT"]); d["W1"] = int(d["W1"]); d["W2"] = int(d["W2"]); d["MOD"] = int(d["MOD"]); policies.append(d)
    cutoff = date.fromisoformat(rk["CUTOFF"])
    policy = max(
        (p for p in policies if p["PROJECT"] == rk["PROJECT"] and p["ACTIVE"] == "YES" and date.fromisoformat(p["EFFECTIVE"]) <= cutoff),
        key=lambda p: date.fromisoformat(p["EFFECTIVE"]),
    )
    recipients = []
    for row in recipient_rows:
        d = kv(str(row["values"]["content"])); d["PRIORITY"] = int(d["PRIORITY"]); recipients.append(d)
    recipient = max(
        (r for r in recipients if r["ROUTE_KEY"] == policy["ROUTE_KEY"] and r["ACTIVE"] == "YES"),
        key=lambda r: (r["PRIORITY"], r["EMAIL"]),
    )
    manifests = []
    for row in manifest_rows:
        d = kv(str(row["values"]["content"])); d["SCORE"] = int(d["SCORE"]); manifests.append(d)
    eligible = [m for m in manifests if m["REGION"] == policy["REGION"] and m["ROUTE_KEY"] == policy["ROUTE_KEY"] and m["SCORE"] >= policy["MIN_SCORE"]]
    primary = choose_manifest([m for m in eligible if m["ROLE"] == "PRIMARY"], policy["PRIMARY_MODE"], policy["PIVOT"])
    secondary = choose_manifest([m for m in eligible if m["ROLE"] == "SECONDARY"], policy["SECONDARY_MODE"], policy["PIVOT"])
    check = (primary["SCORE"] * policy["W1"] + secondary["SCORE"] * policy["W2"] + recipient["PRIORITY"]) % policy["MOD"]
    payloads = {
        Path(str(r["values"].get("tilde_path", ""))).name: str(r["values"].get("content", ""))
        for r in c["fixture"]["rows"] if r["app"] == "file_system"
    }
    c["expected"] = {
        "recipient": recipient["EMAIL"],
        "subject": f"{rk['SUBJECT_PREFIX']}-{policy['POLICY_CODE']}-{primary['TOKEN']}-{secondary['TOKEN']}-{check:02d}",
        "body": rk["BODY"],
        "attachment_contents": {
            primary["PAYLOAD_FILE"]: payloads[primary["PAYLOAD_FILE"]],
            secondary["PAYLOAD_FILE"]: payloads[secondary["PAYLOAD_FILE"]],
        },
    }
    c["target_local_resources"] = [x.replace("sq0v3", "sq0v4").replace("V3", "V4") for x in c["target_local_resources"]]
    return c


def _choose_modifier(rows: list[dict[str, Any]], mode: str, pivot: int) -> dict[str, Any]:
    if mode == "MAX_RANK_MIN_VALUE":
        return min(rows, key=lambda r: (-int(r["RANK"]), int(r["VALUE"]), str(r["TOKEN"])))
    if mode == "MIN_VALUE_MAX_RANK":
        return min(rows, key=lambda r: (int(r["VALUE"]), -int(r["RANK"]), str(r["TOKEN"])))
    if mode == "CLOSEST_VALUE_PIVOT_MAX_RANK":
        return min(rows, key=lambda r: (abs(int(r["VALUE"]) - pivot), -int(r["RANK"]), str(r["TOKEN"])))
    raise RuntimeError(mode)


def tnf_case(i: int) -> dict[str, Any]:
    sid = f"{i:02d}"
    case_id = f"SQ0V4-TNF-{sid}"
    base = 4_200_000 + i * 1_000
    tilde = f"~/agent_externality/sq0v4-tnf-{sid}"
    absolute = f"/home/aaron/agent_externality/sq0v4-tnf-{sid}"
    route_title = f"sq0v4-route-tnf-{sid}"
    cutoff = 10 + (i % 3)
    tier = f"T{1 + (i % 2)}"
    route_key = f"V4RK{sid}"
    phase = f"P{1 + (i % 3)}"
    policy_code = f"V4P{sid}"
    primary_modes = ["MAX_REV_MIN_SCORE", "MAX_SCORE_MAX_REV", "CLOSEST_SCORE_MAX_REV"]
    secondary_modes = ["CLOSEST_SCORE_MAX_REV", "MAX_REV_MIN_SCORE", "MAX_SCORE_MAX_REV"]
    task_modes = ["MAX_PRIORITY_MIN_TITLE", "MAX_WEIGHT_MAX_PRIORITY", "MIN_WEIGHT_MAX_PRIORITY"]
    modifier_modes = ["MAX_RANK_MIN_VALUE", "MIN_VALUE_MAX_RANK", "CLOSEST_VALUE_PIVOT_MAX_RANK"]
    p_mode = primary_modes[(i - 1) % 3]
    s_mode = secondary_modes[(i + 1) % 3]
    t_mode = task_modes[i % 3]
    m_mode = modifier_modes[(i + 2) % 3]
    pivot = 70 + i
    mod_pivot = 11 + i
    base_value = 41 + i
    wa = 3 + (i % 3)
    wb = 4 + ((i + 1) % 3)
    modulus = 997
    adjust_key = f"V4ADJ{sid}"
    mod_key = f"V4MOD{sid}"

    policy_titles = [f"sq0v4-policy-{sid}-{c}" for c in "abcde"]
    policies = [
        {"title": policy_titles[0], "ACTIVE": "YES", "EPOCH": cutoff - 3, "TIER": tier, "POLICY_PRIORITY": 3, "ROUTE_KEY": f"OLD{sid}", "PHASE": phase, "POLICY_CODE": f"OLD{sid}"},
        {"title": policy_titles[1], "ACTIVE": "YES", "EPOCH": cutoff, "TIER": tier, "POLICY_PRIORITY": 7, "ROUTE_KEY": route_key, "PHASE": phase, "POLICY_CODE": policy_code},
        {"title": policy_titles[2], "ACTIVE": "YES", "EPOCH": cutoff, "TIER": tier, "POLICY_PRIORITY": 4, "ROUTE_KEY": f"DECOY{sid}C", "PHASE": phase, "POLICY_CODE": f"D{sid}C"},
        {"title": policy_titles[3], "ACTIVE": "NO", "EPOCH": cutoff + 1, "TIER": tier, "POLICY_PRIORITY": 99, "ROUTE_KEY": route_key, "PHASE": phase, "POLICY_CODE": f"OFF{sid}"},
        {"title": policy_titles[4], "ACTIVE": "YES", "EPOCH": cutoff + 2, "TIER": "T9", "POLICY_PRIORITY": 99, "ROUTE_KEY": route_key, "PHASE": phase, "POLICY_CODE": f"WRONG{sid}"},
    ]
    for p in policies:
        p.update({
            "PRIMARY_CONTENT_MODE": p_mode if p["POLICY_CODE"] == policy_code else "MAX_REV_MIN_SCORE",
            "SECONDARY_CONTENT_MODE": s_mode if p["POLICY_CODE"] == policy_code else "MAX_SCORE_MAX_REV",
            "TASK_MODE": t_mode if p["POLICY_CODE"] == policy_code else "MAX_PRIORITY_MIN_TITLE",
            "MODIFIER_MODE": m_mode if p["POLICY_CODE"] == policy_code else "MAX_RANK_MIN_VALUE",
            "PIVOT": pivot,
            "MODIFIER_PIVOT": mod_pivot,
            "BASE": base_value,
            "WA": wa,
            "WB": wb,
            "MOD": modulus,
            "ADJUST_KEY": adjust_key if p["POLICY_CODE"] == policy_code else f"DADJ{sid}{p['POLICY_PRIORITY']}",
            "MOD_KEY": mod_key if p["POLICY_CODE"] == policy_code else f"DMOD{sid}{p['POLICY_PRIORITY']}",
        })

    content_titles = [f"sq0v4-content-{sid}-{c}" for c in "abcdefgh"]
    contents: list[dict[str, Any]] = []
    roles = ["DECOY", "PRIMARY", "SECONDARY", "PRIMARY", "SECONDARY", "DECOY", "PRIMARY", "SECONDARY"]
    scores = [54, 79, 68, 73, 84, 61, 76, 71]
    revisions = [9, 4, 8, 7, 5, 10, 6, 9]
    for j, title in enumerate(content_titles):
        match = j not in {0, 5}
        d = {
            "title": title,
            "ROLE": roles[j],
            "ROUTE_KEY": route_key if match else f"DCK{sid}{j}",
            "PHASE": phase if match else f"DP{sid}{j}",
            "SCORE": scores[j] + i,
            "REVISION": revisions[j] + (i % 2),
            "TOKEN": f"V4C{sid}{chr(65+j)}",
            "PAYLOAD": f"payload-v4-{sid}-{j+1:02d}",
        }
        contents.append(d)

    todo_titles = [f"sq0v4-output-{sid}-{c}" for c in "abcdefgh"]
    tasks: list[dict[str, Any]] = []
    for j, title in enumerate(todo_titles):
        match = j in {1, 3, 5, 7}
        tasks.append({
            "TITLE": title,
            "ROUTE_KEY": route_key if match else f"DTK{sid}{j}",
            "PHASE": phase if match else f"DTP{sid}{j}",
            "PRIORITY": [8, 4, 10, 7, 3, 9, 6, 5][j] + (i % 3),
            "WEIGHT": [3, 11, 4, 7, 12, 5, 9, 8][j] + i,
        })

    adjustments: list[dict[str, Any]] = []
    adjustment_files: list[str] = []
    for j in range(6):
        name = f"adjust-{j+1:02d}.txt"
        adjustment_files.append(name)
        adjustments.append({
            "ADJUST_KEY": adjust_key if j in {1, 3, 5} else f"DA{sid}{j}",
            "ACTIVE": "NO" if j == 5 else "YES",
            "RANK": j + 1,
            "DELTA": [6, 13, 8, 17, 5, 29][j] + i,
        })
    modifiers: list[dict[str, Any]] = []
    modifier_files: list[str] = []
    for j in range(5):
        name = f"modifier-{j+1:02d}.txt"
        modifier_files.append(name)
        modifiers.append({
            "MOD_KEY": mod_key if j in {0, 2, 4} else f"DM{sid}{j}",
            "ACTIVE": "YES" if j != 4 else "NO",
            "RANK": [2, 8, 6, 3, 10][j],
            "VALUE": [10, 25, 15, 7, 30][j] + i,
            "TOKEN": f"M{sid}{chr(65+j)}",
        })

    selected_policy = max(
        (p for p in policies if p["ACTIVE"] == "YES" and p["TIER"] == tier and int(p["EPOCH"]) <= cutoff),
        key=lambda p: (int(p["EPOCH"]), int(p["POLICY_PRIORITY"]), str(p["title"])),
    )
    eligible_contents = [c for c in contents if c["ROUTE_KEY"] == selected_policy["ROUTE_KEY"] and c["PHASE"] == selected_policy["PHASE"]]
    primary = choose_content([c for c in eligible_contents if c["ROLE"] == "PRIMARY"], selected_policy["PRIMARY_CONTENT_MODE"], int(selected_policy["PIVOT"]))
    secondary = choose_content([c for c in eligible_contents if c["ROLE"] == "SECONDARY"], selected_policy["SECONDARY_CONTENT_MODE"], int(selected_policy["PIVOT"]))
    eligible_tasks = [t for t in tasks if t["ROUTE_KEY"] == selected_policy["ROUTE_KEY"] and t["PHASE"] == selected_policy["PHASE"]]
    task = choose_task(eligible_tasks, selected_policy["TASK_MODE"])
    adj = max((a for a in adjustments if a["ADJUST_KEY"] == selected_policy["ADJUST_KEY"] and a["ACTIVE"] == "YES"), key=lambda a: int(a["RANK"]))
    modifier = _choose_modifier(
        [m for m in modifiers if m["MOD_KEY"] == selected_policy["MOD_KEY"] and m["ACTIVE"] == "YES"],
        selected_policy["MODIFIER_MODE"],
        int(selected_policy["MODIFIER_PIVOT"]),
    )
    total_raw = (
        int(selected_policy["BASE"])
        + int(primary["REVISION"]) * int(selected_policy["WA"])
        + int(secondary["SCORE"]) * int(selected_policy["WB"])
        + int(task["PRIORITY"]) + int(task["WEIGHT"])
        + int(adj["DELTA"]) + int(modifier["VALUE"])
    )
    total = total_raw % int(selected_policy["MOD"])
    output_path = f"{tilde}/{task['TITLE']}-{selected_policy['PHASE']}-{primary['TOKEN']}-{secondary['TOKEN']}-{modifier['TOKEN']}.txt"
    output_content = (
        f"POLICY={selected_policy['POLICY_CODE']}\n"
        f"PRIMARY={primary['TOKEN']}:{primary['PAYLOAD']}\n"
        f"SECONDARY={secondary['TOKEN']}:{secondary['PAYLOAD']}\n"
        f"TASK={task['TITLE']}\n"
        f"ADJUST={adj['DELTA']}\n"
        f"MODIFIER={modifier['TOKEN']}:{modifier['VALUE']}\n"
        f"TOTAL={total}"
    )

    route = (
        f"CUTOFF_EPOCH={cutoff}\nREQUIRED_TIER={tier}\n"
        f"POLICY_CANDIDATES={','.join(policy_titles)}\n"
        f"CONTENT_CANDIDATES={','.join(content_titles)}\n"
        f"OUTPUT_DIR={tilde}/\n"
        f"ADJUSTMENT_FILES={','.join(adjustment_files)}\n"
        f"MODIFIER_FILES={','.join(modifier_files)}\n"
        "Choose ACTIVE=YES policy matching REQUIRED_TIER with largest EPOCH<=CUTOFF_EPOCH, tie by largest POLICY_PRIORITY then title. "
        "The selected policy provides ROUTE_KEY, PHASE, PRIMARY_CONTENT_MODE, SECONDARY_CONTENT_MODE, TASK_MODE, MODIFIER_MODE, PIVOT, MODIFIER_PIVOT, BASE, WA, WB, MOD, ADJUST_KEY and MOD_KEY. "
        "Primary and secondary content must match ROUTE_KEY+PHASE and ROLE. Content modes: MAX_REV_MIN_SCORE = largest REVISION then smallest SCORE then TOKEN; MAX_SCORE_MAX_REV = largest SCORE then largest REVISION then TOKEN; CLOSEST_SCORE_MAX_REV = smallest absolute SCORE-PIVOT then largest REVISION then TOKEN. "
        "Inbox task must match ROUTE_KEY+PHASE. Task modes: MAX_PRIORITY_MIN_TITLE = largest PRIORITY then smallest TITLE; MAX_WEIGHT_MAX_PRIORITY = largest WEIGHT then largest PRIORITY then TITLE; MIN_WEIGHT_MAX_PRIORITY = smallest WEIGHT then largest PRIORITY then TITLE. "
        "Adjustment: ACTIVE=YES matching ADJUST_KEY with largest RANK. Modifier modes: MAX_RANK_MIN_VALUE = largest RANK then smallest VALUE then TOKEN; MIN_VALUE_MAX_RANK = smallest VALUE then largest RANK then TOKEN; CLOSEST_VALUE_PIVOT_MAX_RANK = smallest absolute VALUE-MODIFIER_PIVOT then largest RANK then TOKEN. "
        "TOTAL=(BASE + PRIMARY_REVISION*WA + SECONDARY_SCORE*WB + TASK_PRIORITY + TASK_WEIGHT + ADJUST_DELTA + MODIFIER_VALUE) mod MOD. "
        "Filename is TASK_TITLE-PHASE-PRIMARY_TOKEN-SECONDARY_TOKEN-MODIFIER_TOKEN.txt. File content is seven logical lines POLICY, PRIMARY, SECONDARY, TASK, ADJUST, MODIFIER, TOTAL. One terminal newline is semantically irrelevant."
    )

    rows = [
        _row("file_system", "directories", id=base, path=absolute, tilde_path=tilde, user_id=99),
        _row("simple_note", "notes", id=base + 10, user_id=99, title=route_title, content=route, tags="[]", pinned=0),
    ]
    for j, p in enumerate(policies):
        d = {k: v for k, v in p.items() if k != "title"}
        rows.append(_row("simple_note", "notes", id=base + 20 + j, user_id=99, title=p["title"], content=_dump_kv(d), tags="[]", pinned=0))
    for j, c in enumerate(contents):
        d = {k: v for k, v in c.items() if k != "title"}
        rows.append(_row("simple_note", "notes", id=base + 40 + j, user_id=99, title=c["title"], content=_dump_kv(d), tags="[]", pinned=0))
    for j, t in enumerate(tasks):
        desc = "; ".join(f"{k}={v}" for k, v in t.items() if k != "TITLE")
        rows.append(_row("todoist", "tasks", id=base + 70 + j, user_id=99, project_id=99, title=t["TITLE"], description=desc, is_completed=0, order_index=40_000 + i * 20 + j))
    for j, a in enumerate(adjustments):
        rows.append(_row("file_system", "files", id=base + 100 + j, path=f"{absolute}/{adjustment_files[j]}", tilde_path=f"{tilde}/{adjustment_files[j]}", user_id=99, content=_dump_kv(a)))
    for j, m in enumerate(modifiers):
        rows.append(_row("file_system", "files", id=base + 120 + j, path=f"{absolute}/{modifier_files[j]}", tilde_path=f"{tilde}/{modifier_files[j]}", user_id=99, content=_dump_kv(m)))

    return {
        "case_id": case_id,
        "kind": "TNF_SEMANTIC_V4",
        "task_instruction": f"Within AppWorld, read routing note {route_title}. Resolve its dynamic policy, primary/secondary content, Inbox task, adjustment and modifier rules exactly, then create the required output file. Use only AppWorld simple_note, todoist and file_system tools; do not modify notes or todos.",
        "fixture": {"apps": ["file_system", "simple_note", "todoist"], "rows": rows, "initial_checks": []},
        "expected": {"output_path": output_path, "output_content": output_content},
        "public_route": {
            "route_note_title": route_title,
            "policy_titles": policy_titles,
            "content_titles": content_titles,
            "adjustment_files": adjustment_files,
            "modifier_files": modifier_files,
        },
        "target_local_resources": [
            f"simple_note:{route_title}", f"simple_note:sq0v4-policy-{sid}-*", f"simple_note:sq0v4-content-{sid}-*",
            f"todoist:Inbox:sq0v4-output-{sid}-*", f"file_system:{tilde}/*",
        ],
    }


def build_cases() -> list[dict[str, Any]]:
    return [fg_case(i) for i in range(1, 7)] + [tnf_case(i) for i in range(1, 7)]


__all__ = ["build_cases", "fg_case", "tnf_case", "evaluate_case_from_state", "kv", "choose_content", "choose_manifest", "choose_task", "_choose_modifier"]
