from __future__ import annotations

import argparse, contextlib, copy, csv, hashlib, importlib.util, io, json, subprocess, sys, tempfile, types
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "generated/asset-first-skillrl-representation-invariance-contract.json"
DEFAULT_JSON = ROOT / "generated/asset-first-stri-skillrl-budget-baselines-20260824.json"
DEFAULT_CSV = ROOT / "generated/asset-first-stri-skillrl-budget-baselines-20260824.csv"
TOP_K_VALUES = (1, 2, 3, 4, 6, 8, 12, 13)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_key(skill: dict[str, Any]) -> tuple[str, str, str]:
    return (str(skill.get("title") or ""), str(skill.get("principle") or ""), str(skill.get("when_to_apply") or ""))


def memory_class(repo: Path):
    memory_dir = repo / "agent_system/memory"
    pkg_name = "_skillrl_budget_probe"
    pkg = types.ModuleType(pkg_name); pkg.__path__ = [str(memory_dir)]; sys.modules[pkg_name] = pkg
    for name in ("base", "skills_only_memory"):
        spec = importlib.util.spec_from_file_location(f"{pkg_name}.{name}", memory_dir / f"{name}.py")
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load SkillRL module {name}")
        module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    return sys.modules[f"{pkg_name}.skills_only_memory"].SkillsOnlyMemory


def new_memory(cls, bank: dict[str, Any]):
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as tmp:
        json.dump(bank, tmp); path = Path(tmp.name)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return cls(str(path), retrieval_mode="template")
    finally:
        path.unlink(missing_ok=True)


def signatures(mem, tasks: list[str], top_k: int) -> list[dict[str, Any]]:
    out = []
    for task in tasks:
        r = mem.retrieve(task, top_k=top_k)
        seq = [semantic_key(s) for s in r["general_skills"]]
        out.append({"prompt": mem.format_for_prompt(r), "semantic_set": set(seq), "unique_count": len(set(seq)), "general_count": len(seq)})
    return out


def compare(candidate: list[dict[str, Any]], baseline: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(baseline)
    prompt = sum(c["prompt"] != b["prompt"] for c, b in zip(candidate, baseline, strict=True))
    sem = sum(c["semantic_set"] != b["semantic_set"] for c, b in zip(candidate, baseline, strict=True))
    reduced = sum(c["unique_count"] < b["unique_count"] for c, b in zip(candidate, baseline, strict=True))
    return {"rows": n, "prompt_changed_rows": prompt, "prompt_changed_fraction": prompt/n,
            "semantic_set_changed_rows": sem, "semantic_set_changed_fraction": sem/n,
            "unique_semantic_count_reduced_rows": reduced, "unique_semantic_count_reduced_fraction": reduced/n}


def dedup_general(mem) -> None:
    seen, rows = set(), []
    for skill in mem.skills.get("general_skills", []):
        key = semantic_key(skill)
        if key in seen: continue
        seen.add(key); rows.append(skill)
    mem.skills["general_skills"] = rows


def preflight(contract: dict[str, Any]):
    repo = Path(contract["author_asset"]["repo"])
    checks = {
        "commit": subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip() == contract["author_asset"]["commit"],
        "skills_only_memory_sha": sha(repo/"agent_system/memory/skills_only_memory.py") == contract["author_asset"]["skills_only_memory_sha256"],
        "skill_updater_sha": sha(repo/"agent_system/memory/skill_updater.py") == contract["author_asset"]["skill_updater_sha256"],
        "skillbank_sha": sha(repo/"memory_data/alfworld/claude_style_skills.json") == contract["author_asset"]["alfworld_skillbank_sha256"],
        "released_memories_sha": sha(repo/"memory_data/alfworld/generated_memories_alfworld_total.json") == contract["author_asset"]["alfworld_released_memories_sha256"],
    }
    if not all(checks.values()): raise RuntimeError(f"preflight failed: {checks}")
    bank = load(repo/"memory_data/alfworld/claude_style_skills.json")
    tasks = [str(x["contextual_description"]) for x in load(repo/"memory_data/alfworld/generated_memories_alfworld_total.json")]
    return repo, bank, tasks, memory_class(repo), checks


def build(contract_path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    contract = load(contract_path); repo, bank, tasks, cls, checks = preflight(contract)
    general = bank.get("general_skills", [])
    if (len(general), len(tasks)) != (12, 223): raise RuntimeError("SkillRL frozen inventory drift")
    budgets = []
    for k in TOP_K_VALUES:
        base_mem = new_memory(cls, copy.deepcopy(bank)); base = signatures(base_mem, tasks, k)
        targets = []
        for i, target in enumerate(general):
            dyn = copy.deepcopy(target); dyn["skill_id"] = f"dyn_{900+i:03d}"
            alias = copy.deepcopy(target); alias["skill_id"] = f"alias_{900+i:03d}"
            official = new_memory(cls, copy.deepcopy(bank))
            with contextlib.redirect_stdout(io.StringIO()): off_added = official.add_skills([dyn], category="general")
            off_rows = signatures(official, tasks, k)
            placebo = new_memory(cls, copy.deepcopy(bank))
            with contextlib.redirect_stdout(io.StringIO()): alias_added = placebo.add_skills([alias], category="general")
            placebo_rows = signatures(placebo, tasks, k)
            quotient = new_memory(cls, copy.deepcopy(bank))
            with contextlib.redirect_stdout(io.StringIO()): quotient.add_skills([dyn], category="general")
            dedup_general(quotient); quotient_rows = signatures(quotient, tasks, k)
            capacity_rows = signatures(official, tasks, k+1)
            targets.append({"target_skill_id": target.get("skill_id"), "target_title": target.get("title"),
                "dynamic_clone_admitted": off_added == 1, "non_dynamic_clone_admitted": alias_added == 1,
                "official_dynamic_priority": compare(off_rows, base), "non_dynamic_clone_placebo": compare(placebo_rows, base),
                "exact_semantic_quotient": compare(quotient_rows, base), "capacity_plus_one": compare(capacity_rows, base)})
        def summary(control: str) -> dict[str, Any]:
            total = 12*len(tasks); vals = [row[control] for row in targets]
            p = sum(v["prompt_changed_rows"] for v in vals); s = sum(v["semantic_set_changed_rows"] for v in vals); r = sum(v["unique_semantic_count_reduced_rows"] for v in vals)
            return {"comparisons": total, "prompt_changed": p, "prompt_changed_fraction": p/total,
                    "semantic_set_changed": s, "semantic_set_changed_fraction": s/total,
                    "unique_count_reduced": r, "unique_count_reduced_fraction": r/total,
                    "targets_with_semantic_set_change": sum(v["semantic_set_changed_rows"]>0 for v in vals),
                    "targets_with_unique_count_reduction": sum(v["unique_semantic_count_reduced_rows"]>0 for v in vals)}
        budgets.append({"top_k": k, "baseline_general_count": base[0]["general_count"], "controls": {c:summary(c) for c in ("official_dynamic_priority","non_dynamic_clone_placebo","exact_semantic_quotient","capacity_plus_one")}, "target_results": targets})
    by = {row["top_k"]:row for row in budgets}
    return {"schema_version":"1.0","paper_id":"STRI","analysis":"skillrl-retrieval-budget-baselines","author_repo":str(repo),"author_commit":contract["author_asset"]["commit"],"preflight":checks,"tasks":len(tasks),"general_skill_targets":len(general),"top_k_values":list(TOP_K_VALUES),"new_model_calls":0,"new_gpu_runs":0,"claim_expansion":False,"budgets":budgets,
        "headline":{"top_k_6_official_targets_changed":by[6]["controls"]["official_dynamic_priority"]["targets_with_semantic_set_change"],"top_k_6_official_targets_reduced":by[6]["controls"]["official_dynamic_priority"]["targets_with_unique_count_reduction"],"top_k_6_non_dynamic_placebo_semantic_changes":by[6]["controls"]["non_dynamic_clone_placebo"]["semantic_set_changed"],"top_k_6_quotient_semantic_changes":by[6]["controls"]["exact_semantic_quotient"]["semantic_set_changed"],"top_k_13_official_semantic_changes":by[13]["controls"]["official_dynamic_priority"]["semantic_set_changed"],"interpretation":"The released SkillRL phenotype is a fixed-budget provenance-priority effect: a fresh dynamic identity changes semantic retrieval under constrained top-k, while an equally duplicated non-dynamic ID and exact semantic quotient do not. The semantic-set effect closes when the budget can hold all 12 static contents plus the clone."},
        "scientific_boundary":"SkillRL exposes no independent semantic support matrix, so this is a retrieval phenotype/budget-boundary experiment only; it is not an R* certificate, task-utility result, or prevalence estimate."}


def write_outputs(payload: dict[str, Any], jp: Path = DEFAULT_JSON, cp: Path = DEFAULT_CSV) -> None:
    jp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    fields=("top_k","control","comparisons","prompt_changed_fraction","semantic_set_changed_fraction","unique_count_reduced_fraction","targets_with_semantic_set_change","targets_with_unique_count_reduction")
    with cp.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for row in payload["budgets"]:
            for control,v in row["controls"].items(): w.writerow({"top_k":row["top_k"],"control":control,**{x:v[x] for x in fields[2:]}})


def main() -> None:
    p=argparse.ArgumentParser();p.add_argument("--contract",type=Path,default=DEFAULT_CONTRACT);p.add_argument("--json",type=Path,default=DEFAULT_JSON);p.add_argument("--csv",type=Path,default=DEFAULT_CSV);a=p.parse_args();x=build(a.contract);write_outputs(x,a.json,a.csv);print(json.dumps({"headline":x["headline"],"json":str(a.json),"csv":str(a.csv)},ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
