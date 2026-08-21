from __future__ import annotations

import ast
import hashlib
import itertools
import json
import subprocess
import sys
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

CANDIDATE_ID = "SHADOW-P15-C01"
CONTRACT_SHA256 = "e41c05f823661dda273f63fbedf5ab01528c96c1512eff3d16a42a0e6beb80fa"
HARNESS_PLAN_SHA256 = "87a0fece5d1df4369b6f1eb045a5b863882f82994624f6a0eff69a5ed8de3b75"
EXECUTOR_MODEL = "kimi-k3"
MAX_UNITS = 80
MAX_MODEL_CALLS = 160

SKILLS: dict[str, str] = {
    "S1_NORMALIZE": "Normalize every task label with unicodedata.normalize('NFKC', value).strip().casefold(). Use that exact normalization and do not invent synonym maps.",
    "S2_PARSE_NUMERIC": "Parse numeric strings with decimal.Decimal inside try/except InvalidOperation. Reject missing, invalid, or non-finite numeric values before using them.",
    "S3_GROUP_SUM": "For grouped sums, use collections.defaultdict and add each valid numeric value to the group selected by the task. Preserve exact arithmetic type when practical.",
    "S4_STABLE_SORT": "Produce deterministic ordered output with sorted(..., key=...), including the explicit task tie-break instead of relying on incidental dictionary order.",
    "S5_DEDUP_FIRST": "Deduplicate by the task's composite key with a set named seen_keys. Preserve the first valid record and call seen_keys.add(key) when admitting it.",
}

TASKS: dict[str, dict[str, Any]] = {
    "T1": {
        "title": "normalize-group-sort",
        "skills": ["S1_NORMALIZE", "S3_GROUP_SUM", "S4_STABLE_SORT"],
        "instruction": "Implement solve(records). Normalize team labels, sum integer score per normalized team, and return a list of {'team': str, 'score': int} sorted by descending score then ascending team.",
        "cases": [
            {
                "input": [{"team": " Alpha ", "score": 3}, {"team": "ＡＬＰＨＡ", "score": 5}, {"team": "Beta", "score": 4}],
                "expected": [{"team": "alpha", "score": 8}, {"team": "beta", "score": 4}],
            },
            {
                "input": [{"team": "Z", "score": 2}, {"team": " y ", "score": 2}, {"team": "Y", "score": 1}],
                "expected": [{"team": "y", "score": 3}, {"team": "z", "score": 2}],
            },
        ],
    },
    "T2": {
        "title": "parse-group-sort",
        "skills": ["S2_PARSE_NUMERIC", "S3_GROUP_SUM", "S4_STABLE_SORT"],
        "instruction": "Implement solve(records). Parse amount strings exactly with Decimal; skip invalid/non-finite amounts; sum by the already-canonical category; return [{'category': str, 'amount': str}] with amount formatted to two decimals, sorted descending numeric amount then category.",
        "cases": [
            {
                "input": [{"category": "a", "amount": "1.20"}, {"category": "b", "amount": "bad"}, {"category": "a", "amount": "2.30"}, {"category": "b", "amount": "3.50"}],
                "expected": [{"category": "a", "amount": "3.50"}, {"category": "b", "amount": "3.50"}],
            },
            {
                "input": [{"category": "x", "amount": "NaN"}, {"category": "y", "amount": "4"}, {"category": "z", "amount": "4.00"}],
                "expected": [{"category": "y", "amount": "4.00"}, {"category": "z", "amount": "4.00"}],
            },
        ],
    },
    "T3": {
        "title": "normalize-parse-dedup",
        "skills": ["S1_NORMALIZE", "S2_PARSE_NUMERIC", "S5_DEDUP_FIRST"],
        "instruction": "Implement solve(records). Normalize sku labels, parse price with Decimal, skip invalid/non-finite prices, and keep only the first valid record for each normalized sku using first-occurrence order. Return [{'sku': str, 'price': str}] with two-decimal price strings.",
        "cases": [
            {
                "input": [{"sku": " A-1 ", "price": "2.00"}, {"sku": "Ａ-１", "price": "3.00"}, {"sku": "b", "price": "bad"}, {"sku": "B", "price": "4"}],
                "expected": [{"sku": "a-1", "price": "2.00"}, {"sku": "b", "price": "4.00"}],
            },
            {
                "input": [{"sku": " X ", "price": "NaN"}, {"sku": "x", "price": "1.25"}, {"sku": "Y", "price": "5"}],
                "expected": [{"sku": "x", "price": "1.25"}, {"sku": "y", "price": "5.00"}],
            },
        ],
    },
    "T4": {
        "title": "normalize-dedup-sort",
        "skills": ["S1_NORMALIZE", "S5_DEDUP_FIRST", "S4_STABLE_SORT"],
        "instruction": "Implement solve(records). Normalize name and tag, deduplicate by the normalized (name, tag) pair preserving first occurrence, then return [{'name': str, 'tag': str}] sorted by name then tag.",
        "cases": [
            {
                "input": [{"name": " Alice ", "tag": " X "}, {"name": "ＡＬＩＣＥ", "tag": "x"}, {"name": "Bob", "tag": "A"}],
                "expected": [{"name": "alice", "tag": "x"}, {"name": "bob", "tag": "a"}],
            },
            {
                "input": [{"name": "z", "tag": "b"}, {"name": "Y", "tag": "c"}, {"name": " y ", "tag": " C "}],
                "expected": [{"name": "y", "tag": "c"}, {"name": "z", "tag": "b"}],
            },
        ],
    },
    "T5": {
        "title": "parse-dedup-group",
        "skills": ["S2_PARSE_NUMERIC", "S5_DEDUP_FIRST", "S3_GROUP_SUM"],
        "instruction": "Implement solve(records). Parse value using Decimal, skip invalid/non-finite values, deduplicate by event_id preserving the first valid event, then sum by canonical group. Return a dictionary mapping each group to a two-decimal string.",
        "cases": [
            {
                "input": [{"event_id": "e1", "group": "a", "value": "1.5"}, {"event_id": "e1", "group": "a", "value": "9"}, {"event_id": "e2", "group": "b", "value": "2"}, {"event_id": "e3", "group": "a", "value": "bad"}],
                "expected": {"a": "1.50", "b": "2.00"},
            },
            {
                "input": [{"event_id": "e1", "group": "x", "value": "NaN"}, {"event_id": "e1", "group": "x", "value": "4"}, {"event_id": "e2", "group": "x", "value": "1"}],
                "expected": {"x": "5.00"},
            },
        ],
    },
}

ALLOWED_IMPORTS = {"unicodedata", "decimal", "collections", "math", "re", "json"}
FORBIDDEN_CALLS = {"open", "exec", "eval", "compile", "__import__", "input", "breakpoint", "globals", "locals", "vars"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def conditions_for_task(task_id: str) -> list[dict[str, Any]]:
    skills = list(TASKS[task_id]["skills"])
    rows: list[dict[str, Any]] = []
    for index, order in enumerate(itertools.permutations(skills), 1):
        rows.append({"condition_id": f"PERM-{index}", "kind": "PERMUTATION", "skills": list(order)})
    rows.append({"condition_id": "NO-SKILL", "kind": "NO_SKILL", "skills": []})
    for index, skill in enumerate(skills, 1):
        rows.append({"condition_id": f"SINGLE-{index}", "kind": "SINGLE_SKILL", "skills": [skill]})
    return rows


def all_units() -> list[dict[str, Any]]:
    rows = []
    for task_id in sorted(TASKS):
        for condition in conditions_for_task(task_id):
            rows.append({
                "unit_id": f"{task_id}-{condition['condition_id']}",
                "task_id": task_id,
                **deepcopy(condition),
            })
    return rows


def solution_tool() -> list[dict[str, Any]]:
    return [{
        "type": "function",
        "name": "submit_solution",
        "description": "Submit the complete Python solution for the frozen benign task.",
        "parameters": {
            "type": "object",
            "properties": {
                "python_code": {"type": "string", "minLength": 20},
            },
            "required": ["python_code"],
            "additionalProperties": False,
        },
    }]


def prompt_for_unit(unit: dict[str, Any]) -> str:
    task = TASKS[unit["task_id"]]
    skills = unit["skills"]
    skill_text = "\n".join(f"{i+1}. {skill_id}: {SKILLS[skill_id]}" for i, skill_id in enumerate(skills)) or "(no procedural skill supplied)"
    cases_public = [{"input": row["input"], "expected_schema_example": row["expected"]} for row in task["cases"][:1]]
    return f'''You are a frozen executor in a controlled agent-skill order experiment. Solve one benign local Python transformation task.

TASK_ID={unit['task_id']}
CONDITION_ID={unit['condition_id']}
TASK={task['instruction']}

PROCEDURAL_SKILLS_IN_PRESENTATION_ORDER:
{skill_text}

The task itself never changes across conditions. Skills are optional procedural guidance, not extra task facts. Write deterministic Python 3 code defining exactly one public function solve(records). No file/network/process access, no top-level execution, no dynamic imports. Allowed imports: {sorted(ALLOWED_IMPORTS)}.
One public example is provided only to clarify schema, not as the full test set:
{json.dumps(cases_public,ensure_ascii=False)}

Call submit_solution exactly once with the complete source code. Do not return prose.'''


def validate_solution_ast(code: str) -> dict[str, Any]:
    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        return {"valid": False, "errors": [f"syntax:{error.msg}"]}
    errors: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        errors.append(f"forbidden-top-level:{type(node).__name__}")
    solve_defs = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "solve"]
    if len(solve_defs) != 1:
        errors.append("solve-definition-count")
    elif len(solve_defs[0].args.args) != 1:
        errors.append("solve-arity")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    errors.append(f"forbidden-import:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = str(node.module or "").split(".")[0]
            if module not in ALLOWED_IMPORTS:
                errors.append(f"forbidden-import:{node.module}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            errors.append(f"forbidden-call:{node.func.id}")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            errors.append(f"forbidden-dunder:{node.attr}")
    return {"valid": not errors, "errors": sorted(set(errors)), "ast_sha256": hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()}


def uptake_signatures(code: str) -> dict[str, bool]:
    lowered = code.lower()
    return {
        "S1_NORMALIZE": "unicodedata.normalize" in lowered and ".casefold" in lowered,
        "S2_PARSE_NUMERIC": "decimal" in lowered and "invalidoperation" in lowered,
        "S3_GROUP_SUM": "defaultdict" in lowered,
        "S4_STABLE_SORT": "sorted(" in lowered or ".sort(" in lowered,
        "S5_DEDUP_FIRST": "seen_keys" in lowered and ".add(" in lowered,
    }

_RUNNER = r'''
import json,sys
payload=json.loads(sys.stdin.read())
code=payload["code"]
ns={}
exec(compile(code,"<candidate>","exec"),ns,ns)
solve=ns.get("solve")
if not callable(solve): raise RuntimeError("missing solve")
out=[]
for case in payload["cases"]:
    try:
        got=solve(case["input"])
        out.append({"ok":got==case["expected"],"got":got,"expected":case["expected"]})
    except Exception as e:
        out.append({"ok":False,"error":type(e).__name__+":"+str(e),"expected":case["expected"]})
print(json.dumps(out,ensure_ascii=False,sort_keys=True,default=str))
'''


def evaluate_solution(task_id: str, code: str, *, timeout_seconds: float = 5.0) -> dict[str, Any]:
    audit = validate_solution_ast(code)
    if not audit["valid"]:
        return {"valid_execution": False, "task_success": False, "ast_audit": audit, "cases": [], "uptake": uptake_signatures(code)}
    payload = {"code": code, "cases": TASKS[task_id]["cases"]}
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", _RUNNER],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return {"valid_execution": False, "task_success": False, "ast_audit": audit, "cases": [], "uptake": uptake_signatures(code), "error": "timeout"}
    if proc.returncode != 0:
        return {"valid_execution": False, "task_success": False, "ast_audit": audit, "cases": [], "uptake": uptake_signatures(code), "error": proc.stderr[-1000:]}
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"valid_execution": False, "task_success": False, "ast_audit": audit, "cases": [], "uptake": uptake_signatures(code), "error": "invalid-runner-json"}
    success = bool(rows) and all(bool(row.get("ok")) for row in rows)
    return {"valid_execution": True, "task_success": success, "ast_audit": audit, "cases": rows, "uptake": uptake_signatures(code)}


def offline_probe() -> dict[str, Any]:
    units = all_units()
    errors: list[str] = []
    if len(units) != 50:
        errors.append("unit-count")
    if len({row["unit_id"] for row in units}) != 50:
        errors.append("unit-id-duplicate")
    for task_id in TASKS:
        conditions = conditions_for_task(task_id)
        perms = [row for row in conditions if row["kind"] == "PERMUTATION"]
        if len(perms) != 6:
            errors.append(f"perm-count:{task_id}")
        expected_set = sorted(TASKS[task_id]["skills"])
        if any(sorted(row["skills"]) != expected_set for row in perms):
            errors.append(f"perm-skill-set-drift:{task_id}")
        prompts = [prompt_for_unit({"task_id": task_id, **row}) for row in perms]
        visible_skill_lengths = [sum(len(SKILLS[s]) for s in row["skills"]) for row in perms]
        if len(set(visible_skill_lengths)) != 1:
            errors.append(f"perm-visible-skill-length-drift:{task_id}")
        if len({hashlib.sha256(p.encode()).hexdigest() for p in prompts}) != 6:
            errors.append(f"perm-prompt-not-distinct:{task_id}")
    reference_code = """\ndef solve(records):\n    return records\n"""
    if not validate_solution_ast(reference_code)["valid"]:
        errors.append("ast-validator-self-check")
    core = {
        "schema_version": "1.0",
        "status": "P15_OFFLINE_HARNESS_PROBE_PASS" if not errors else "P15_OFFLINE_HARNESS_PROBE_FAIL",
        "candidate_id": CANDIDATE_ID,
        "contract_sha256": CONTRACT_SHA256,
        "harness_plan_sha256": HARNESS_PLAN_SHA256,
        "task_count": len(TASKS),
        "unit_count": len(units),
        "per_task_conditions": 10,
        "permutation_conditions": 6,
        "provider_call_upper_bound": len(units),
        "unit_cap": MAX_UNITS,
        "model_call_cap": MAX_MODEL_CALLS,
        "errors": errors,
        "scientific_authority": False,
        "belief_authority": False,
    }
    core["offline_probe_sha256"] = sha_json(core)
    return core


def adjudicate(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    by_unit = {str(row.get("unit_id") or ""): row for row in receipts if isinstance(row, dict)}
    expected = {row["unit_id"] for row in all_units()}
    missing = sorted(expected - set(by_unit))
    extra = sorted(set(by_unit) - expected)
    invalid = [uid for uid in expected & set(by_unit) if not by_unit[uid].get("valid_execution")]
    task_rows: dict[str, dict[str, Any]] = {}
    divergent_tasks = 0
    uptake_divergent_tasks = 0
    for task_id in sorted(TASKS):
        perm = [by_unit[f"{task_id}-PERM-{i}"] for i in range(1, 7) if f"{task_id}-PERM-{i}" in by_unit]
        successes = [bool(row.get("task_success")) for row in perm]
        success_divergent = len(set(successes)) > 1 if len(successes) == 6 else False
        if success_divergent:
            divergent_tasks += 1
        uptake_vectors = [tuple(sorted((row.get("uptake") or {}).items())) for row in perm]
        uptake_divergent = len(set(uptake_vectors)) > 1 if len(uptake_vectors) == 6 else False
        if uptake_divergent:
            uptake_divergent_tasks += 1
        task_rows[task_id] = {
            "permutation_successes": successes,
            "success_divergent": success_divergent,
            "uptake_divergent": uptake_divergent,
            "no_skill_success": bool(by_unit.get(f"{task_id}-NO-SKILL", {}).get("task_success")),
            "single_skill_successes": [bool(by_unit.get(f"{task_id}-SINGLE-{i}", {}).get("task_success")) for i in range(1, 4)],
        }
    if missing or extra or invalid:
        outcome = "INCONCLUSIVE"
        reason = "missing/extra/invalid execution receipts"
    elif divergent_tasks >= 2 and uptake_divergent_tasks >= 1:
        outcome = "RESIDUAL_SURVIVES"
        reason = "at least two preregistered tasks change success across identical-skill permutations and uptake also changes on at least one task"
    elif divergent_tasks == 0:
        outcome = "REDUCTION_SUPPORTED"
        reason = "all preregistered tasks are success-invariant across all six identical-skill permutations"
    else:
        outcome = "INCONCLUSIVE"
        reason = "only one task shows success divergence or uptake evidence is insufficient for directional consistency"
    core = {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "contract_sha256": CONTRACT_SHA256,
        "harness_plan_sha256": HARNESS_PLAN_SHA256,
        "outcome": outcome,
        "reason": reason,
        "missing_units": missing,
        "extra_units": extra,
        "invalid_units": invalid,
        "divergent_tasks": divergent_tasks,
        "uptake_divergent_tasks": uptake_divergent_tasks,
        "task_results": task_rows,
        "scientific_authority": False,
        "belief_authority": False,
    }
    core["adjudication_sha256"] = sha_json(core)
    return core
