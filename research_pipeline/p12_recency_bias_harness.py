from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

CANDIDATE_ID = "SHADOW-P12-C01"
CONTRACT_SHA256 = "216f48652df9c08727a030730aafbf0564c485cf7a3fc2a694ba6c2d53d7a1bb"
HARNESS_PLAN_SHA256 = "c053fd7ccc8429fb1da46eecfa6ea9e47bcd39f6f21ce4ac86ffa386e35165f2"
EXECUTOR_MODEL = "kimi-k3"
TEMPERATURE = 0.0
FAMILIES = ("LINEAR", "QUADRATIC", "ALTERNATING2", "CYCLIC3")
PHASES = ("BACKWARD_LOOKING", "FORWARD_LOOKING")
LIBRARY_STAGES = (4, 8)
RECENCY_POLICIES = ("UNIFORM", "EXPONENTIAL_HALF_LIFE_2_SKILLS")
TOP_K = 3
RECENCY_BONUS = 0.15
PROVIDER_CALL_CAP = 104
EVALUATION_UNIT_CAP = 96
DIFFICULTY_CALIBRATION_CALLS = 4
SKILL_COMPILATION_CALLS = 4
RIDGE = 1.0

ANALYSIS_PROTOCOL = {
    "scenario_split": "ascending sha256('p12-analysis:' + scenario_id): first 8 fit, last 4 heldout",
    "difficulty_gate": "four disjoint paired no-skill calibration scenarios; both phase accuracies must be <1.0 and absolute phase-accuracy gap <=0.25",
    "baseline_features": ["intercept", "phase_forward", "recency_policy", "stage8", "selected_static_similarity_mean", "selected_static_similarity_min", "phase_no_skill_accuracy"],
    "candidate_extra_feature": "phase_forward_x_recency_policy",
    "fit": "ridge linear-probability model, lambda=1.0, intercept unpenalized, fit on 8 scenarios only",
    "primary_metric": "heldout Brier/MSE improvement of candidate interaction model over additive same-information baseline",
    "direct_interaction": "mean[(success_uniform-success_recency)_forward - (success_uniform-success_recency)_backward] over heldout scenario-stage pairs",
    "residual_survives": "fit direct harm interaction >0; heldout direct interaction >=0.25; heldout Brier improvement >=0.02; stage8 direct interaction >= stage4 direct interaction; regression interaction coefficient is diagnostic only because success-model sign is opposite the harm definition",
    "reduction_supported": "abs(heldout direct interaction) <=0.125 and heldout Brier improvement <=0.005",
    "otherwise": "INCONCLUSIVE",
    "scientific_authority": False,
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _family_series(family: str, variant: int) -> dict[str, Any]:
    if family not in FAMILIES:
        raise ValueError(family)
    sign = -1 if variant % 2 == 0 else 1
    if family == "LINEAR":
        base, slope = 17 + 3 * variant, sign * (2 + variant % 3)
        clean = [base + slope * t for t in range(1, 10)]
    elif family == "QUADRATIC":
        base, a, q = 11 + 2 * variant, sign * (2 + variant % 2), sign
        clean = [base + a * t + q * t * t for t in range(1, 10)]
    elif family == "ALTERNATING2":
        base, slope, amp = 31 + variant, sign * (1 + variant % 2), 3 + variant % 3
        clean = [base + slope * t + (amp if t % 2 == 0 else -amp) for t in range(1, 10)]
    else:
        base, slope, amp = 43 + variant, sign * (1 + variant % 2), 2 + variant % 4
        cyc = (-amp, 0, amp)
        clean = [base + slope * t + cyc[(t - 1) % 3] for t in range(1, 10)]
    recent_step = clean[7] - clean[6]
    if recent_step == 0:
        recent_step = 3 * sign
    observed = list(clean)
    observed[7] = clean[7] - 4 * recent_step
    return {"clean": clean, "observed": observed, "recent_step": recent_step}


def _task_from_scenario(scenario_id: str, family: str, variant: int, phase: str, split: str) -> dict[str, Any]:
    series = _family_series(family, variant)
    if phase == "BACKWARD_LOOKING":
        times = list(range(2, 8))
        values = series["observed"][1:7]
        answer = series["clean"][0]
        direction = "immediately before"
    elif phase == "FORWARD_LOOKING":
        times = list(range(3, 9))
        values = series["observed"][2:8]
        answer = series["clean"][8]
        direction = "immediately after"
    else:
        raise ValueError(phase)
    task_id = f"{scenario_id}-{phase[:1]}"
    retrieval_query = f"{family.lower()} temporal numeric sequence endpoint extrapolation robust pattern analysis"
    return {
        "task_id": task_id,
        "scenario_id": scenario_id,
        "family": family,
        "variant": variant,
        "phase": phase,
        "split": split,
        "times": times,
        "values": values,
        "answer": int(answer),
        "retrieval_query": retrieval_query,
        "retrieval_query_sha256": sha_text(retrieval_query),
        "difficulty_signature": {"observations": 6, "answer_type": "integer", "endpoint_distance": 1},
        "prompt_core": (
            f"Temporal family token: {family}. Observed integer sequence: "
            + ", ".join(f"t{t}={v}" for t, v in zip(times, values))
            + f". Infer the latent clean integer value {direction} this window. "
              "A transient endpoint measurement shock may be present."
        ),
        "scientific_authority": False,
    }


def evaluation_tasks() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family_index, family in enumerate(FAMILIES):
        for local in range(3):
            variant = 10 + family_index * 7 + local
            sid = f"E-{family}-{local+1}"
            rows.extend(_task_from_scenario(sid, family, variant, phase, "EVALUATION") for phase in PHASES)
    return rows


def difficulty_calibration_pairs() -> list[dict[str, Any]]:
    rows = []
    for index, family in enumerate(FAMILIES):
        variant = 70 + index * 5
        sid = f"D-{family}-1"
        rows.append({
            "pair_id": sid,
            "family": family,
            "backward": _task_from_scenario(sid, family, variant, "BACKWARD_LOOKING", "DIFFICULTY_CALIBRATION"),
            "forward": _task_from_scenario(sid, family, variant, "FORWARD_LOOKING", "DIFFICULTY_CALIBRATION"),
            "scientific_authority": False,
        })
    return rows


def skill_calibration_bundles() -> list[dict[str, Any]]:
    bundles = []
    for index, family in enumerate(FAMILIES):
        examples = []
        for j, variant in enumerate((100 + index * 11, 101 + index * 11), 1):
            sid = f"S-{family}-{j}"
            # Phase-neutral solved endpoint examples: one clean backward and one shocked forward example.
            phase = "BACKWARD_LOOKING" if j == 1 else "FORWARD_LOOKING"
            task = _task_from_scenario(sid, family, variant, phase, "SKILL_CALIBRATION")
            examples.append({"example_id":sid,"family":family,"prompt_core":task["prompt_core"],"answer":task["answer"]})
        bundles.append({
            "bundle_id": f"SKILL-BUNDLE-{family}",
            "family": family,
            "older_skill_id": f"S{index+1:02d}",
            "newer_skill_id": f"S{index+5:02d}",
            "older_timestamp": index + 1,
            "newer_timestamp": index + 5,
            "examples": examples,
            "scientific_authority": False,
        })
    return bundles


def retrieval_text(family: str) -> str:
    return f"{family.lower()} temporal numeric sequence endpoint extrapolation robust pattern analysis"


def mock_skills() -> list[dict[str, Any]]:
    rows=[]
    for bundle in skill_calibration_bundles():
        for which in ("older", "newer"):
            sid=bundle[f"{which}_skill_id"]
            rows.append({
                "skill_id":sid,"family":bundle["family"],"timestamp":bundle[f"{which}_timestamp"],
                "text":f"Frozen mock procedure {sid} for {bundle['family']} endpoint extrapolation.",
                "retrieval_text":retrieval_text(bundle["family"]),"origin":"DISJOINT_SKILL_CALIBRATION",
                "scientific_authority":False,
            })
    return sorted(rows,key=lambda x:x["timestamp"])


def validate_frozen_skills(skills: list[dict[str, Any]]) -> list[str]:
    errors=[]
    if len(skills)!=8: errors.append("skill-count-not-8")
    ids=[str(x.get("skill_id") or "") for x in skills];timestamps=[int(x.get("timestamp") or 0) for x in skills]
    if len(set(ids))!=8 or sorted(ids)!=[f"S{i:02d}" for i in range(1,9)]: errors.append("skill-id-set")
    if sorted(timestamps)!=list(range(1,9)): errors.append("skill-timestamps")
    counts=Counter(str(x.get("family") or "") for x in skills)
    if counts!={family:2 for family in FAMILIES}: errors.append("skill-family-balance")
    eval_ids={x["task_id"] for x in evaluation_tasks()}
    for row in skills:
        if not str(row.get("text") or "").strip(): errors.append(f"empty-skill:{row.get('skill_id')}")
        if str(row.get("retrieval_text") or "")!=retrieval_text(str(row.get("family") or "")): errors.append(f"retrieval-text-drift:{row.get('skill_id')}")
        if any(eid in str(row.get("text") or "") for eid in eval_ids): errors.append(f"evaluation-id-leak:{row.get('skill_id')}")
    return sorted(set(errors))


def _tokens(text: str) -> list[str]:
    return [x for x in re.findall(r"[a-z0-9]+", text.lower()) if len(x)>1]


def bm25_scores(query: str, documents: list[str]) -> list[float]:
    tokenized=[_tokens(x) for x in documents];q=_tokens(query);n=len(tokenized)
    avg=sum(len(x) for x in tokenized)/max(1,n);dfs=Counter()
    for doc in tokenized:
        for token in set(doc): dfs[token]+=1
    out=[];k1=1.2;b=0.75
    for doc in tokenized:
        tf=Counter(doc);score=0.0
        for token in q:
            if token not in tf: continue
            idf=math.log(1+(n-dfs[token]+0.5)/(dfs[token]+0.5));freq=tf[token]
            score+=idf*(freq*(k1+1))/(freq+k1*(1-b+b*len(doc)/max(avg,1e-9)))
        out.append(score)
    return out


def rank_skills(skills: list[dict[str, Any]], task: dict[str, Any], stage: int, policy: str) -> list[dict[str, Any]]:
    active=[row for row in skills if int(row["timestamp"])<=stage]
    static=bm25_scores(task["retrieval_query"],[str(row["retrieval_text"]) for row in active])
    rows=[]
    for row,score in zip(active,static):
        age=stage-int(row["timestamp"]);weight=2.0**(-age/2.0)
        final=score if policy=="UNIFORM" else score+RECENCY_BONUS*weight
        rows.append({"skill_id":row["skill_id"],"family":row["family"],"timestamp":row["timestamp"],"static_similarity":score,"recency_weight":weight,"final_score":final,"text":row["text"]})
    rows.sort(key=lambda x:(-x["final_score"],x["skill_id"]))
    for i,row in enumerate(rows,1): row["rank"]=i
    return rows


def rollout_units(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    errors=validate_frozen_skills(skills)
    if errors: raise ValueError(f"invalid frozen skills:{errors}")
    units=[]
    for task in evaluation_tasks():
        for stage in LIBRARY_STAGES:
            for policy in RECENCY_POLICIES:
                ranking=rank_skills(skills,task,stage,policy);selected=ranking[:TOP_K]
                uid=f"{task['task_id']}-L{stage}-{'U' if policy=='UNIFORM' else 'R'}"
                units.append({
                    "unit_id":uid,"task_id":task["task_id"],"scenario_id":task["scenario_id"],"family":task["family"],"phase":task["phase"],
                    "library_stage":stage,"recency_policy":policy,"answer":task["answer"],"prompt_core":task["prompt_core"],
                    "retrieval_query_sha256":task["retrieval_query_sha256"],"selected_skill_ids":[x["skill_id"] for x in selected],
                    "selected_static_similarities":[round(float(x["static_similarity"]),9) for x in selected],
                    "selected_skill_texts":[x["text"] for x in selected],"ranking":[{k:x[k] for k in ("skill_id","rank","static_similarity","recency_weight","final_score")} for x in ranking],
                    "scientific_authority":False,
                })
    return sorted(units,key=lambda x:hashlib.sha256(("p12-rollout-order:"+x["unit_id"]).encode()).hexdigest())


def retrieval_pairing_checks(skills: list[dict[str, Any]]) -> dict[str, Any]:
    tasks={x["task_id"]:x for x in evaluation_tasks()};errors=[];pairs=[]
    for scenario in sorted({x["scenario_id"] for x in tasks.values()}):
        back=next(x for x in tasks.values() if x["scenario_id"]==scenario and x["phase"]=="BACKWARD_LOOKING")
        forward=next(x for x in tasks.values() if x["scenario_id"]==scenario and x["phase"]=="FORWARD_LOOKING")
        if back["retrieval_query_sha256"]!=forward["retrieval_query_sha256"]: errors.append(f"query-mismatch:{scenario}")
        for stage in LIBRARY_STAGES:
            for policy in RECENCY_POLICIES:
                br=rank_skills(skills,back,stage,policy);fr=rank_skills(skills,forward,stage,policy)
                bs=[(x["skill_id"],round(x["static_similarity"],9),round(x["final_score"],9)) for x in br]
                fs=[(x["skill_id"],round(x["static_similarity"],9),round(x["final_score"],9)) for x in fr]
                if bs!=fs: errors.append(f"retrieval-pair-drift:{scenario}:L{stage}:{policy}")
        pairs.append({"scenario_id":scenario,"retrieval_query_sha256":back["retrieval_query_sha256"]})
    return {"passed":not errors,"errors":errors,"pairs":pairs,"scientific_authority":False}


def analysis_split() -> dict[str, list[str]]:
    scenarios=sorted({x["scenario_id"] for x in evaluation_tasks()},key=lambda x:hashlib.sha256(("p12-analysis:"+x).encode()).hexdigest())
    return {"fit":scenarios[:8],"heldout":scenarios[8:]}


def offline_probe() -> dict[str, Any]:
    tasks=evaluation_tasks();difficulty=difficulty_calibration_pairs();bundles=skill_calibration_bundles();skills=mock_skills();units=rollout_units(skills);pairing=retrieval_pairing_checks(skills);split=analysis_split()
    checks={
        "evaluation_tasks_24":len(tasks)==24,
        "matched_scenarios_12":len({x["scenario_id"] for x in tasks})==12,
        "phase_balance_12_12":Counter(x["phase"] for x in tasks)=={"BACKWARD_LOOKING":12,"FORWARD_LOOKING":12},
        "difficulty_calls_4":len(difficulty)==4,
        "skill_compilation_calls_4":len(bundles)==4,
        "frozen_skills_8":validate_frozen_skills(skills)==[],
        "rollout_units_96":len(units)==96,
        "provider_upper_bound_104":len(units)+len(difficulty)+len(bundles)==PROVIDER_CALL_CAP,
        "retrieval_pairing_exact":pairing["passed"] is True,
        "same_prompt_complexity_within_pair":all(pair["backward"]["difficulty_signature"]==pair["forward"]["difficulty_signature"] for pair in difficulty),
        "analysis_split_8_4":len(split["fit"])==8 and len(split["heldout"])==4 and not(set(split["fit"])&set(split["heldout"])),
        "no_evaluation_task_in_skill_calibration":not({x["task_id"] for x in tasks}&{f"{e['example_id']}-{p[:1]}" for b in bundles for e in b["examples"] for p in PHASES}),
    }
    core={
        "schema_version":"1.0","status":"P12_OFFLINE_HARNESS_PROBE_PASS" if all(checks.values()) else "P12_OFFLINE_HARNESS_PROBE_FAIL",
        "candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"harness_plan_sha256":HARNESS_PLAN_SHA256,
        "checks":checks,"task_manifest_sha256":sha_json(tasks),"difficulty_calibration_manifest_sha256":sha_json(difficulty),
        "skill_calibration_manifest_sha256":sha_json(bundles),"mock_ranking_manifest_sha256":sha_json(units),"analysis_split":split,
        "analysis_protocol":ANALYSIS_PROTOCOL,"retrieval_pairing":pairing,"provider_call_upper_bound":PROVIDER_CALL_CAP,
        "scientific_authority":False,"belief_authority":False,
    }
    core["offline_probe_sha256"]=sha_json(core);return core


def difficulty_summary(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    by={str(row.get("pair_id") or ""):row for row in receipts if isinstance(row,dict)}
    expected={row["pair_id"] for row in difficulty_calibration_pairs()}
    if set(by)!=expected:
        return {"passed":False,"reason":"difficulty-calibration-coverage","phase_accuracy":{},"scientific_authority":False}
    backward=sum(bool(by[pid].get("backward_success")) for pid in expected)/len(expected)
    forward=sum(bool(by[pid].get("forward_success")) for pid in expected)/len(expected)
    passed=backward<1.0 and forward<1.0 and abs(backward-forward)<=0.25
    return {"passed":passed,"reason":"PASS" if passed else "no-skill-headroom-or-phase-match-failed","phase_accuracy":{"BACKWARD_LOOKING":backward,"FORWARD_LOOKING":forward},"absolute_phase_gap":abs(backward-forward),"scientific_authority":False}


def _solve(a: list[list[float]], b: list[float]) -> list[float]:
    n=len(b);m=[a[i][:]+[b[i]] for i in range(n)]
    for c in range(n):
        pivot=max(range(c,n),key=lambda r:abs(m[r][c]));m[c],m[pivot]=m[pivot],m[c]
        if abs(m[c][c])<1e-10: raise ValueError("singular P12 ridge system")
        scale=m[c][c];m[c]=[x/scale for x in m[c]]
        for r in range(n):
            if r==c: continue
            factor=m[r][c];m[r]=[m[r][j]-factor*m[c][j] for j in range(n+1)]
    return [m[i][-1] for i in range(n)]


def _ridge_fit(rows: list[dict[str, Any]], *, interaction: bool) -> list[float]:
    vectors=[];ys=[]
    for row in rows:
        phase=1.0 if row["phase"]=="FORWARD_LOOKING" else 0.0
        recency=1.0 if row["recency_policy"]=="EXPONENTIAL_HALF_LIFE_2_SKILLS" else 0.0
        stage8=1.0 if int(row["library_stage"])==8 else 0.0
        sims=[float(x) for x in row["selected_static_similarities"]]
        vector=[1.0,phase,recency,stage8,sum(sims)/len(sims),min(sims),float(row["phase_no_skill_accuracy"])]
        if interaction: vector.append(phase*recency)
        vectors.append(vector);ys.append(float(bool(row["task_success"])))
    d=len(vectors[0]);xtx=[[0.0]*d for _ in range(d)];xty=[0.0]*d
    for x,y in zip(vectors,ys):
        for i in range(d):
            xty[i]+=x[i]*y
            for j in range(d): xtx[i][j]+=x[i]*x[j]
    for i in range(1,d): xtx[i][i]+=RIDGE
    return _solve(xtx,xty)


def _prediction(row: dict[str, Any], weights: list[float], *, interaction: bool) -> float:
    phase=1.0 if row["phase"]=="FORWARD_LOOKING" else 0.0
    recency=1.0 if row["recency_policy"]=="EXPONENTIAL_HALF_LIFE_2_SKILLS" else 0.0
    stage8=1.0 if int(row["library_stage"])==8 else 0.0
    sims=[float(x) for x in row["selected_static_similarities"]]
    vector=[1.0,phase,recency,stage8,sum(sims)/len(sims),min(sims),float(row["phase_no_skill_accuracy"])]
    if interaction: vector.append(phase*recency)
    return max(0.0,min(1.0,sum(w*x for w,x in zip(weights,vector))))


def _direct_interaction(rows: list[dict[str, Any]], scenario_ids: set[str], stage: int | None=None) -> float:
    by={(row["scenario_id"],row["phase"],int(row["library_stage"]),row["recency_policy"]):int(bool(row["task_success"])) for row in rows if row["scenario_id"] in scenario_ids and (stage is None or int(row["library_stage"])==stage)}
    deltas=[]
    stages=(stage,) if stage is not None else LIBRARY_STAGES
    for sid in sorted(scenario_ids):
        for st in stages:
            try:
                fu=by[(sid,"FORWARD_LOOKING",st,"UNIFORM")];fr=by[(sid,"FORWARD_LOOKING",st,"EXPONENTIAL_HALF_LIFE_2_SKILLS")]
                bu=by[(sid,"BACKWARD_LOOKING",st,"UNIFORM")];br=by[(sid,"BACKWARD_LOOKING",st,"EXPONENTIAL_HALF_LIFE_2_SKILLS")]
            except KeyError as error: raise ValueError(f"missing P12 interaction cell:{error}") from error
            deltas.append((fu-fr)-(bu-br))
    return sum(deltas)/len(deltas)


def adjudicate_rollouts(receipts: list[dict[str, Any]], difficulty: dict[str, Any]) -> dict[str, Any]:
    if difficulty.get("passed") is not True:
        return {"schema_version":"1.0","status":"P12_INCONCLUSIVE_DIFFICULTY_GATE","outcome":"INCONCLUSIVE","reason":difficulty.get("reason"),"scientific_authority":False,"belief_authority":False}
    valid=[row for row in receipts if isinstance(row,dict) and row.get("status")=="UNIT_COMPLETE" and row.get("valid_execution") is True]
    ids={row.get("unit_id") for row in valid};expected={row["unit_id"] for row in rollout_units(mock_skills())}
    if len(valid)!=96 or ids!=expected:
        return {"schema_version":"1.0","status":"P12_INCONCLUSIVE_PROTOCOL","outcome":"INCONCLUSIVE","reason":"requires exactly 96 valid frozen units","valid_units":len(valid),"scientific_authority":False,"belief_authority":False}
    phase_acc=difficulty["phase_accuracy"]
    rows=[]
    for row in valid:
        copy=dict(row);copy["phase_no_skill_accuracy"]=phase_acc[copy["phase"]];rows.append(copy)
    split=analysis_split();fit_ids=set(split["fit"]);heldout_ids=set(split["heldout"])
    fit=[row for row in rows if row["scenario_id"] in fit_ids];heldout=[row for row in rows if row["scenario_id"] in heldout_ids]
    baseline_w=_ridge_fit(fit,interaction=False);candidate_w=_ridge_fit(fit,interaction=True)
    baseline_brier=sum((_prediction(row,baseline_w,interaction=False)-float(bool(row["task_success"])))**2 for row in heldout)/len(heldout)
    candidate_brier=sum((_prediction(row,candidate_w,interaction=True)-float(bool(row["task_success"])))**2 for row in heldout)/len(heldout)
    improvement=baseline_brier-candidate_brier;train_interaction=_direct_interaction(rows,fit_ids);heldout_interaction=_direct_interaction(rows,heldout_ids);stage4=_direct_interaction(rows,heldout_ids,4);stage8=_direct_interaction(rows,heldout_ids,8);coef=candidate_w[-1]
    residual=train_interaction>0 and heldout_interaction>=0.25 and improvement>=0.02 and stage8>=stage4
    reduction=abs(heldout_interaction)<=0.125 and improvement<=0.005
    outcome="RESIDUAL_SURVIVES" if residual else "REDUCTION_SUPPORTED" if reduction else "INCONCLUSIVE"
    result={"schema_version":"1.0","status":"P12_EVIDENCE_ADJUDICATED","outcome":outcome,"qualified_units":96,"analysis_split":split,"difficulty_summary":difficulty,"baseline":{"weights":baseline_w,"heldout_brier":baseline_brier},"candidate":{"weights":candidate_w,"interaction_coefficient":coef,"heldout_brier":candidate_brier,"heldout_brier_improvement":improvement},"direct_interaction":{"fit":train_interaction,"heldout":heldout_interaction,"heldout_stage4":stage4,"heldout_stage8":stage8},"decision_thresholds":ANALYSIS_PROTOCOL,"scientific_authority":False,"belief_authority":False}
    result["adjudication_sha256"]=sha_json(result);return result


def difficulty_prompt(pair: dict[str, Any]) -> str:
    b,f=pair["backward"],pair["forward"]
    return f'''This is a frozen no-skill temporal difficulty calibration. Do not create or use any skill memory. Solve both independent integer endpoint tasks.
BACKWARD: {b["prompt_core"]}
FORWARD: {f["prompt_core"]}
Return the two integer answers only through the supplied function.'''


def skill_compilation_prompt(bundle: dict[str, Any]) -> str:
    return f'''This is a disjoint calibration-to-skill compilation step before evaluation. The examples and answers below are calibration-only and never appear in evaluation.
Family={bundle["family"]}
EXAMPLES={canonical_json(bundle["examples"])}
Distill exactly two concise reusable procedural skills for solving future endpoint-extrapolation tasks in this family. Do not copy example numbers or answers. Do not mention timestamps, recency policy, library stage, evaluation IDs, or expected experimental effects. Each procedure must be <=500 characters. Return only through the supplied function.'''


def rollout_prompt(unit: dict[str, Any]) -> str:
    skill_block="\n\n".join(f"[Retrieved skill {i}]\n{text}" for i,text in enumerate(unit["selected_skill_texts"],1))
    return f'''You are a frozen temporal-task executor. Retrieved skills are advisory procedures and may conflict; use the task data to decide. Do not infer any hidden retrieval policy or experiment condition.
TASK: {unit["prompt_core"]}
RETRIEVED_SKILLS_START
{skill_block}
RETRIEVED_SKILLS_END
Return exactly one integer answer through the supplied function.'''


def difficulty_tool() -> list[dict[str, Any]]:
    return [{"type":"function","name":"submit_p12_difficulty_answers","description":"Submit the two no-skill calibration answers.","parameters":{"type":"object","properties":{"backward_answer":{"type":"integer"},"forward_answer":{"type":"integer"}},"required":["backward_answer","forward_answer"],"additionalProperties":False}}]


def skill_tool() -> list[dict[str, Any]]:
    return [{"type":"function","name":"submit_p12_skills","description":"Submit exactly two calibration-derived procedures.","parameters":{"type":"object","properties":{"older_skill_text":{"type":"string","maxLength":700},"newer_skill_text":{"type":"string","maxLength":700}},"required":["older_skill_text","newer_skill_text"],"additionalProperties":False}}]


def answer_tool() -> list[dict[str, Any]]:
    return [{"type":"function","name":"submit_p12_answer","description":"Submit the integer task answer.","parameters":{"type":"object","properties":{"answer":{"type":"integer"}},"required":["answer"],"additionalProperties":False}}]
