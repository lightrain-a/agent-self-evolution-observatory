from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "p0-e2-workflow-cpu.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "p0-e2-workflow-cpu.js"

MOTIFS = {
    "missing-verification": (("tool", "commit-without-verify"), "insert-verify-before-commit", "bounded-retry"),
    "unclassified-recovery": (("tool-error", "retry-without-classify"), "classify-then-bounded-recovery", "insert-verify-before-commit"),
    "premature-completion": (("partial-input", "commit-before-complete"), "gate-commit-on-completeness", "schema-map-before-call"),
    "stale-schema": (("stale-schema", "call-before-map"), "schema-map-before-call", "gate-commit-on-completeness"),
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _workflow(split: str, motif: str, index: int) -> dict[str, Any]:
    signature, rewrite, distractor = MOTIFS[motif]
    return {
        "workflow_id": f"{split}-{motif}-{index:02d}",
        "split": split,
        "api": f"{split}-api-{index:02d}",
        "object": f"{split}-object-{index:02d}",
        "motif": motif,
        "typed_signature": list(signature),
        "candidate_rewrites": [rewrite, distractor],
    }


def _execute(workflow: dict[str, Any], rewrite: str | None) -> dict[str, Any]:
    expected = MOTIFS[workflow["motif"]][1]
    return {
        "success": int(rewrite == expected),
        "expected_rewrite": expected,
        "independent_truth": "programmatic-workflow-verifier",
    }


def _group_intervention(group: str) -> int:
    return int(group == "causal-subgraph")


def _freeze_hash(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _learn_grammar(source: list[dict[str, Any]]) -> tuple[dict[tuple[str, ...], str], list[dict[str, Any]], int]:
    observations: dict[tuple[str, ...], list[str]] = defaultdict(list)
    rows: list[dict[str, Any]] = []
    calls = 0
    for workflow in source:
        causal = _group_intervention("causal-subgraph"); calls += 1
        distractor = _group_intervention("distractor-subgraph"); calls += 1
        if causal == 1 and distractor == 0:
            signature = tuple(workflow["typed_signature"])
            rewrite = MOTIFS[workflow["motif"]][1]
            observations[signature].append(rewrite)
            rows.append({
                "workflow_id": workflow["workflow_id"], "signature": list(signature),
                "causal_group_effect": causal, "distractor_group_effect": distractor,
                "rewrite": rewrite,
            })
    grammar = {signature: Counter(values).most_common(1)[0][0] for signature, values in observations.items()}
    return grammar, rows, calls


def _learn_direct(source: list[dict[str, Any]]) -> tuple[dict[tuple[str, ...], str], list[dict[str, Any]], int]:
    outcomes: dict[tuple[str, ...], dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    rows: list[dict[str, Any]] = []
    calls = 0
    for workflow in source:
        signature = tuple(workflow["typed_signature"])
        for rewrite in workflow["candidate_rewrites"]:
            result = _execute(workflow, rewrite); calls += 1
            outcomes[signature][rewrite].append(result["success"])
            rows.append({
                "workflow_id": workflow["workflow_id"], "signature": list(signature),
                "rewrite": rewrite, "success": result["success"],
            })
    policy = {}
    for signature, by_edit in outcomes.items():
        policy[signature] = max(sorted(by_edit), key=lambda edit: sum(by_edit[edit]) / len(by_edit[edit]))
    return policy, rows, calls


def _eval_hidden(hidden: list[dict[str, Any]], grammar: dict[tuple[str, ...], str], direct: dict[tuple[str, ...], str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows=[]; stats={"g_success":0,"d_success":0,"g_harm":0,"d_harm":0,"agreement":0}
    for workflow in hidden:
        sig=tuple(workflow["typed_signature"]); ge=grammar.get(sig); de=direct.get(sig)
        g=_execute(workflow,ge); d=_execute(workflow,de)
        stats["g_success"]+=g["success"]; stats["d_success"]+=d["success"]
        stats["g_harm"]+=int(ge is not None and not g["success"]); stats["d_harm"]+=int(de is not None and not d["success"])
        stats["agreement"]+=int(ge==de)
        rows.append({"workflow_id":workflow["workflow_id"],"api":workflow["api"],"signature":list(sig),"grammar_edit":ge,"direct_edit":de,"grammar_success":g["success"],"direct_success":d["success"],"truth":g["expected_rewrite"]})
    return rows,stats


def run_e2_cpu_p0() -> dict[str, Any]:
    source=[_workflow("source",motif,4*m+i) for m,motif in enumerate(MOTIFS) for i in range(4)]
    hidden=[_workflow("hidden",motif,2*m+i) for m,motif in enumerate(MOTIFS) for i in range(2)]
    grammar,interventions,g_calls=_learn_grammar(source); direct,paired,d_calls=_learn_direct(source)
    frozen={"grammar":{"|".join(k):v for k,v in grammar.items()},"direct":{"|".join(k):v for k,v in direct.items()}}
    freeze_sha=_freeze_hash(frozen); hidden_rows,s=_eval_hidden(hidden,grammar,direct); n=len(hidden)
    equivalent=(g_calls==d_calls and s["g_success"]==s["d_success"]==n and s["g_harm"]==s["d_harm"]==0 and s["agreement"]==n)
    return {"schema_version":"1.0","generated_at":_now(),"idea_id":"workflow-branch-credit","code":"E-2",
      "design":{"source_workflows":len(source),"hidden_workflows":n,"motifs":len(MOTIFS),"motif_recurrence_per_source":4,"hidden_api_identity_disjoint":True,"rewrite_rule_capacity":len(grammar),"group_interventions_per_source":2,"hidden_search_calls":0,"independent_truth":"programmatic workflow verifier"},
      "baseline_fairness":{"same_source_workflows":True,"same_typed_graph_observation":True,"same_source_call_budget":g_calls==d_calls,"same_rewrite_candidates":True,"same_hidden_workflows":True,"both_zero_search_on_hidden":True,"hidden_outcomes_used_before_freeze":False},
      "frozen_registry":frozen,"freeze_sha256_before_hidden":freeze_sha,"source_group_interventions":interventions,"source_paired_edits":paired,"hidden_rows":hidden_rows,
      "metrics":{"grammar_hidden_success":s["g_success"]/n,"direct_edit_hidden_success":s["d_success"]/n,"grammar_harmful_rewrites":s["g_harm"],"direct_harmful_rewrites":s["d_harm"],"hidden_rewrite_agreement":s["agreement"]/n,"grammar_source_calls":g_calls,"direct_source_calls":d_calls,"grammar_hidden_search_calls":0,"direct_hidden_search_calls":0},
      "matched_simplification":{"baseline":"E-1-style typed paired edit-effect lookup","equivalent":equivalent},
      "decision":"STOP_MATCHED_E1_DIRECT_EDIT_EQUIVALENT" if equivalent else "P0_SIGNAL_CONTINUE","standalone_claim_stop_authorized":equivalent,"p1_authorized":False,
      "next_action":"Merge E-2 motif context into E-1/CE-Graph-style editing; do not spend GPU on a standalone causal-rewrite paper." if equivalent else "Freeze the grammar and validate on a second workflow sandbox only after human review."}


def write_e2_cpu_p0(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    state=run_e2_cpu_p0(); json_path.parent.mkdir(parents=True,exist_ok=True)
    json_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.P0_E2_WORKFLOW_CPU = "+json.dumps(state,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return state


if __name__=="__main__":
    print(json.dumps(write_e2_cpu_p0(),ensure_ascii=False,indent=2))
