from __future__ import annotations

import hashlib, json
from typing import Any

SCHEMA_VERSION="1.0"
TEMPLATE_ID="ICLR-AGENT-SELF-EVOLUTION-MANUSCRIPT-V1"
TEMPLATE_VERSION="1.0"

REFERENCES=(
 {"key":"aflow","title":"AFlow: Automating Agentic Workflow Generation","venue":"ICLR 2025","url":"https://proceedings.iclr.cc/paper_files/paper/2025/hash/5492ecbce4439401798dcd2c90be94cd-Abstract-Conference.html","lesson":"problem→challenge→search formulation; early overview figure; broad baselines + cost Pareto + ablation + evolution case study"},
 {"key":"agentsquare","title":"AgentSquare: Automatic LLM Agent Search in Modular Design Space","venue":"ICLR 2025","url":"https://proceedings.iclr.cc/paper_files/paper/2025/hash/0ae94013da7cd459402fd77874e09ee3-Abstract-Conference.html","lesson":"define the scientific problem/design space first; page-two overview; six-domain main results + component ablation + predictor validation + case study"},
 {"key":"amemgym","title":"AMemGym: Interactive Memory Benchmarking for Assistants in Long-Horizon Conversations","venue":"ICLR 2026","url":"https://proceedings.iclr.cc/paper_files/paper/2026/hash/0856bc553d3e3b9827e5140d0ad3bf8d-Abstract-Conference.html","lesson":"make evaluation defect visible with an early comparison table; validate evaluator before ranking systems; diagnose write/read/utilization and robustness"},
 {"key":"reward","title":"Reward Is Enough: LLMs Are In-Context Reinforcement Learners","venue":"ICLR 2026","url":"https://proceedings.iclr.cc/paper_files/paper/2026/hash/b7511dfe2e7a1fa45e093cc75389abc2-Abstract-Conference.html","lesson":"simple conceptual dichotomy; related work organized by scientific distinction; strong self-improvement baselines and mechanism ablations"},
 {"key":"selfrag","title":"Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection","venue":"ICLR 2024","url":"https://proceedings.iclr.cc/paper_files/paper/2024/file/25f7be9694d7b32d5cc670927b8091e1-Paper-Conference.pdf","lesson":"concrete baseline failure + side-by-side method figure; procedural method exposition; training/inference ablations and efficiency-quality tradeoff"},
 {"key":"reasoningbank","title":"ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory","venue":"ICLR 2026","url":"https://iclr.cc/virtual/2026/poster/10007887","lesson":"narrow against raw/success-only memory; connect memory and scaling as one mechanism; test effectiveness and interaction efficiency on multiple agent domains"},
 {"key":"ace","title":"Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models","venue":"ICLR 2026","url":"https://iclr.cc/virtual/2026/poster/10008343","lesson":"name memorable failure modes before method; small number of clear roles; offline+online, quality+latency/cost, held-out hard split"},
 {"key":"dgm","title":"Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents","venue":"ICLR 2026","url":"https://iclr.cc/virtual/2026/poster/10007327","lesson":"theoretical ideal→practical obstacle→empirical substitute; simple archive/self-modify/validate loop; remove self-improvement/open-endedness in baselines"},
)

PAGE_BUDGET=(
 ("Abstract + Introduction",1.5,"necessity, challenge, missing object, intuition, method, decisive evidence, bounded contributions"),
 ("Problem Setup + Related Work",1.0,"define the object and prove closest approaches do not already cover it"),
 ("Method / Protocol",2.0,"intuition→requirements→overview→components→algorithm→assumptions/cost/failure"),
 ("Experimental Setup",0.8,"RQs, data, models, strongest baselines, units, metrics, statistics, parity"),
 ("Main Results",1.3,"answer headline RQs with load-bearing tables/figures"),
 ("Analysis",1.6,"ablation, mechanism, robustness/transfer, failure, efficiency"),
 ("Discussion + Limitations + Conclusion",0.8,"scientific lesson, non-claims, evidence debt, practical implication"),
)

INTRO_JOBS=(
 ("I1","Concrete setting and stake","Name the agent/task and consequence of failure."),
 ("I2","Current paradigm","Explain how the dominant approach works and concede what it already solves."),
 ("I3","Failure and challenge","Give a concrete failure, then 2–3 observable reasons it is hard."),
 ("I4","Missing object + intuition","Name the missing variable/estimand/invariant/control and the simplest intuition."),
 ("I5","Method overview","Explain input→operation→persistent object/state→output in 4–7 sentences."),
 ("I6","Evidence preview","Give the decisive main comparison plus one mechanism/boundary result."),
 ("I7","Contributions","Use 2–4 bullets: object/problem, method/protocol, evidence/analysis."),
)

METHOD_COMPONENT_QUESTIONS=(
 "What exact input is received?","What operation is performed?","What state/object is read or changed?",
 "Why is it necessary for the scientific claim?","What measurable signature changes if removed/replaced?",
 "What is the simplest alternative implementation and what part of the claim is container-independent?",
)

EXPERIMENT_LANES=(
 ("E1","Main comparison","Does the claim beat the strongest fair baseline?",True),
 ("E2","Component / simplification ablation","Which component matters and can a simpler same-information method match it?",True),
 ("E3","Mechanism-aligned analysis","Does the effect occur where the mechanism predicts?",True),
 ("E4","Robustness / transfer / boundary","Where does it persist, vanish, hit ceiling, or reverse?",True),
 ("E5","Negative and failure cases","What fails and what non-claim follows?",True),
 ("E6","Efficiency / cost / scale","What calls/tokens/time/memory/search budget are added?",True),
 ("E7","Case study / trajectory","Can one trace make the mechanism understandable without replacing statistics?",False),
)

ARCHETYPES={
 "theory_certificate":"exact theorem/certificate + positive/negative regimes + bounded system witness; do not force a leaderboard claim",
 "evaluation_protocol":"meta-evaluate reliability first, then old-vs-new disagreement, diagnostic decomposition, robustness, optimization proof-of-concept",
 "causal_identification":"treatment/control + information parity + independent unit + power/resolution + placebo/confound sensitivity",
 "causal_mechanism":"intervention→intermediate witness→downstream outcome + alternative-explanation controls",
 "mechanism_intervention":"targeted must beat original and strong generic control in predicted non-ceiling regimes; keep transfer/ceiling/null visible",
}

WRITING_RULES={
 "result_paragraph":"answer → evidence → interpretation → boundary",
 "result_evidence_definition":"evidence means the minimum decisive numbers, strongest comparison, independent unit, and uncertainty/statistical test needed to support the answer",
 "must":["open each section with what it establishes","define new terms once in ordinary language","use concrete subjects and active verbs","one sentence carries one main logical job","say what every number counts and the independent unit","use find/show/observe for evidence and hypothesize/predict for unresolved mechanisms","say explicitly when an experiment was not run"],
 "avoid":["chronological project narration","noun stacks and novelty-sounding labels for standard operations","claiming effect and mechanism from one aggregate score","hiding nulls/support failures/opposite signs/costs that bound the claim","repeated vague adjectives such as comprehensive/significant without concrete scope"],
 "reader_test":"A technically literate reader with no Research OS history can restate the problem, challenge, intuition, method flow, decisive experiment, and claim boundary after one read.",
}

CHECKLIST=(
 "first page contains a concrete problem and real challenge","Related Work explains mechanisms and concedes overlap","an early figure/table makes the gap or method visible","method starts from intuition/design requirements before module names","every component answers the six-question contract","setup freezes strongest baseline, units, metrics, statistics and budget parity","E1–E6 are planned/completed or archetype-justified N/A","at least one analysis directly tests a mechanism prediction","negative/failure/ceiling regimes remain in the main story","efficiency/cost is reported when the method adds resources","results use answer→evidence→interpretation→boundary","discussion states explicit non-claims/evidence debt","reader simulation passes without internal project context",
)

POLICY={"template_is_development_guidance_not_scientific_truth":True,"template_cannot_expand_claims":True,"template_cannot_authorize_experiments":True,"experiment_lane_planning_is_not_execution":True,"historical_manuscripts_are_not_retroactively_demoted":True,"new_material_revision_should_bind_template":True}

def _sha(x:Any)->str:return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def template_payload()->dict[str,Any]:
 p={"schema_version":SCHEMA_VERSION,"template_id":TEMPLATE_ID,"template_version":TEMPLATE_VERSION,"name_zh":"ICLR Agent 自进化论文固定写作与实验模板 v1","name_en":"ICLR Agent Self-Evolution Manuscript & Experiment Template v1","derived_from":[dict(x) for x in REFERENCES],"page_budget_main_body":[{"section":a,"pages":b,"job":c} for a,b,c in PAGE_BUDGET],"abstract_jobs":["setting/stake","specific gap/failure","core intuition + method","decisive result","bounded conclusion"],"introduction_paragraphs":[{"id":a,"job":b,"rule":c} for a,b,c in INTRO_JOBS],"related_work":{"minimum_families":3,"family_fields":["how it works","what it solves","overlap","missing object","claim boundary"],"closest_work_fields":["work","mechanism","already covered","irreducible difference","our non-claim"],"final_job":"end by restating the residual scientific object"},"method":{"order":["object/notation if needed","plain-language intuition","design requirements","overview figure","components in execution order","algorithm/update rule","assumptions/held-fixed/cost/failure"],"component_questions":list(METHOD_COMPONENT_QUESTIONS),"figure_rule":"reader can narrate the full flow from the overview figure/caption","equation_rule":"every equation gets a plain-language quantity/decision/scientific-role sentence"},"experiment_lanes":[{"id":a,"name":b,"question":c,"required":d} for a,b,c,d in EXPERIMENT_LANES],"archetype_adapters":dict(ARCHETYPES),"writing_rules":dict(WRITING_RULES),"final_checklist":list(CHECKLIST),"policy":dict(POLICY),"authority":{"scientific":False,"method":False,"experiment":False,"gpu":False,"submission":False}}
 p["template_sha256"]=_sha(p);return p

def audit_template_binding(value:Any,*,required:bool)->dict[str,Any]:
 row=value if isinstance(value,dict) else {}; blockers=[]
 if required:
  if row.get("template_id")!=TEMPLATE_ID:blockers.append("iclr-template-id-missing-or-stale")
  if str(row.get("template_version") or "")!=TEMPLATE_VERSION:blockers.append("iclr-template-version-missing-or-stale")
  lanes=row.get("experiment_lane_plan") if isinstance(row.get("experiment_lane_plan"),dict) else {}
  for lid,_,_,req in EXPERIMENT_LANES:
   r=lanes.get(lid) if isinstance(lanes.get(lid),dict) else {}
   if req and r.get("status") not in {"PLANNED","COMPLETED","NOT_APPLICABLE_WITH_ARCHETYPE_REASON"}:blockers.append(f"iclr-template-experiment-lane-unbound:{lid}")
 return {"schema_version":SCHEMA_VERSION,"required":required,"passed":not blockers,"status":"ICLR_TEMPLATE_BOUND" if not blockers else "ICLR_TEMPLATE_BINDING_REQUIRED","blockers":blockers,"template_id":TEMPLATE_ID,"template_version":TEMPLATE_VERSION,"scientific_authority":False,"experiment_authority":False}
