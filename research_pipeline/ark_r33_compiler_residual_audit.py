from __future__ import annotations

import json

from .ark_provider import ArkResponsesClient, extract_json_object
from .config import PROJECT_ROOT

SOURCE=PROJECT_ROOT/"generated"/"ark-r33-compiler-residual.json"
OUTPUT=PROJECT_ROOT/"generated"/"ark-r33-compiler-residual-audit.json"
MODEL="deepseek-v4-flash"


def main()->int:
    child=json.loads(SOURCE.read_text(encoding="utf-8"))["repair"]
    prompt=f"""Act as a strict independent ICLR repair auditor. This is the third repair of one idea. The only previous boundary was that residual-specific typed editing was confounded with generic output-space restriction.

ADVANCE only if the child now operationalizes THREE fair conditions in the body: (1) residual-typed whitelist, (2) matched-cardinality/matched-syntactic-complexity non-residual typed whitelist, and (3) unrestricted local-delta editor; all receive identical compiled state, supervision, traces, verifier access, capacity, calls, tokens, optimization, and wall-clock; evaluation uses a preregistered residual-required held-out set crossed with unseen-model × unseen-harness; and the claim is killed/re-scoped if the non-residual typed control matches the residual-specific one. Frozen persistent asset and independent hidden execution truth are required.

Return JSON only: {{"idea_id":"compiler-residual-contract-editor-v53-r33","verdict":"advance|revise|block","confidence":"high|medium|low","finding":"...","required_action":"...","simplification_resistance":0,"persistent_learning":0,"independent_truth":0,"pilot_identifiability":0}}.

Child:
{json.dumps(child,ensure_ascii=False,indent=2)}
"""
    r=ArkResponsesClient().respond(prompt,model=MODEL,max_output_tokens=4000,thinking="disabled")
    obj=extract_json_object(r["text"])
    OUTPUT.write_text(json.dumps({"schema_version":"1.0","judge":MODEL,"audit":obj,"usage":r.get("usage") or {}},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(obj,ensure_ascii=False))
    return 0

if __name__=="__main__": raise SystemExit(main())
