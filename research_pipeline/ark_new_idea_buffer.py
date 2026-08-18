from __future__ import annotations

import argparse, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient
from .config import PROJECT_ROOT

DEFAULT_JSON=PROJECT_ROOT/"generated"/"ark-new-idea-buffer.json"
MODELS=("deepseek-v4-pro","glm-5.2","doubao-seed-evolving")
CURRENT_TITLES=[
"Contradiction-Preserving Consolidation","Compositional Update Compatibility","Agent Update Trust Region","Correction-Action Causal Compiler","Memory Interaction Clause Learner","Probe Mutation and Retirement Policy","Update-Composition Repair Compiler","Monotone Applicability-Set Specializer","API Error-Semantics Adapter","Workflow Repair Grammar","Restoration-Clause Induction","Rubric Intervention Sparse Solver","Update-History Semantic Compactor","Bounded-Probe API Transition Operator","Interventional Reauthorization Triage Under a Fixed Ceiling","Nested-Pathway Memory Repair","Constraint-Complete Typed Memory-Order Logic","Certified Out-of-Span Interaction Inverter","Compiler-Residual Contract Editor","Filtered Longitudinal Evaluator-State Extrapolation"]


def _tool(n:int)->list[dict[str,Any]]:
 bi={"type":"object","properties":{"en":{"type":"string"},"zh":{"type":"string"}},"required":["en","zh"],"additionalProperties":False}
 props={"id":{"type":"string"},"title":bi,"problem":bi,"importance":bi,"core_idea":bi,"why_not_current_portfolio":bi,"persistent_update_object":{"type":"string"},"learning_signal":bi,"independent_ground_truth":bi,"strongest_matched_baseline":bi,"shared_information_budget":bi,"mechanism_irreducibility":bi,"decisive_pilot":bi,"stop_condition":bi,"collision_search_queries":{"type":"array","minItems":3,"maxItems":6,"items":{"type":"string"}},"low_resource_assets":{"type":"array","minItems":2,"maxItems":6,"items":{"type":"string"}},"remaining_risk":bi}
 return [{"type":"function","name":"submit_ideas","description":"Submit novel ICLR agent self-evolution ideas.","parameters":{"type":"object","properties":{"ideas":{"type":"array","minItems":n,"maxItems":n,"items":{"type":"object","properties":props,"required":list(props),"additionalProperties":False}}},"required":["ideas"],"additionalProperties":False}}]


def prompt(model:str,n:int)->str:
 return f"""Generate {n} materially distinct ICLR-level research ideas for persistent agent self-evolution. You are a creative mechanism designer, not the final reviewer.

Existing portfolio to AVOID duplicating or trivially renaming:
{json.dumps(CURRENT_TITLES,ensure_ascii=False)}

Target scientific scope: agents that learn persistently from failures/experience/version changes by updating memory, prompts, workflows, tool semantics, small modules, policies, evaluators, curricula, world models, or other explicit persistent state. The first paper must remain low-resource: frozen 7B/8B backbones where possible, <=2 GPUs / <=48 GPU-hours for a decisive pilot.

Hard design constraints:
1. Start from a REAL failure mode, not a method combination looking for a problem.
2. Exact learned object must persist after evolution context is removed and change future behavior without hidden target-time relearning.
3. Do not propose 'a learned gate/scorer/router' unless the learned representation/state itself is scientifically necessary and cannot be replaced by the same-information fixed rule or direct predictor.
4. Strongest simplification receives identical observations, features, labels, intervention outcomes, traces, verifier access, model capacity, calls, tokens, optimizer steps, and wall-clock wherever applicable. Never win by starving the baseline.
5. Independent final truth must not be produced by the learner or the model/judge that supplies training labels.
6. Each idea needs one decisive crossed/factorial pilot and a stop rule that kills the thesis.
7. Prefer underexplored mechanism questions such as persistent credit across evolution rounds, failure localization before reflection, learned update-surface choice with counterfactual necessity, self-evolution under tool/environment nonstationarity, causal internalization of inference-time corrections, temporal dependency/obsolescence of learned assets, self-evolving world-model abstractions, or other genuinely different problems. These are hints, not required templates.
8. Combination ideas are allowed only when each component is logically necessary to close a real failure loop; explain why the result is not a simple union of existing components.
9. Do NOT invent literature citations. Instead provide 3-6 precise collision_search_queries that an independent reviewer can use against official/primary sources.
10. Prefer ideas whose decisive P0 can distinguish the exact mechanism from the strongest same-information simplification before a large experiment.
11. ids must be unique lowercase slugs ending in -buffer-{model.replace('.','-').replace('_','-')}.
12. Call submit_ideas exactly once, bilingual English/Chinese.

Model label: {model}
"""


def generate(model:str,n:int)->dict[str,Any]:
 r=ArkResponsesClient().respond(prompt(model,n),model=model,max_output_tokens=15000,tools=_tool(n),thinking="disabled")
 calls=[x for x in r.get("function_calls",[]) if x.get("name")=="submit_ideas"]
 if len(calls)!=1: raise ValueError(f"expected one submit_ideas call, got {len(calls)}")
 rows=(json.loads(calls[0].get("arguments") or "{}")).get("ideas") or []
 if len(rows)!=n: raise ValueError(f"expected {n} ideas, got {len(rows)}")
 return {"model":model,"usage":r.get("usage") or {},"ideas":[{"generator_model":model,**x} for x in rows]}


def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("--model",choices=MODELS,required=True); p.add_argument("--count",type=int,default=6); p.add_argument("--json",type=Path,default=DEFAULT_JSON); a=p.parse_args()
 result=generate(a.model,a.count); existing={"schema_version":"1.0","generated_at":"","models":[],"ideas":[],"runs":[]}
 if a.json.exists():
  try: existing=json.loads(a.json.read_text(encoding="utf-8"))
  except Exception: pass
 existing["generated_at"]=datetime.now(timezone.utc).replace(microsecond=0).isoformat(); existing["models"]=list(dict.fromkeys([*(existing.get("models") or []),a.model])); existing["runs"]=[r for r in existing.get("runs") or [] if r.get("model")!=a.model]+[{"model":a.model,"usage":result["usage"],"count":len(result["ideas"])}]; existing["ideas"]=[x for x in existing.get("ideas") or [] if x.get("generator_model")!=a.model]+result["ideas"]
 a.json.write_text(json.dumps(existing,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(a.model,len(result["ideas"])); [print(x["id"],x["title"]["en"]) for x in result["ideas"]]; return 0
if __name__=="__main__": raise SystemExit(main())
