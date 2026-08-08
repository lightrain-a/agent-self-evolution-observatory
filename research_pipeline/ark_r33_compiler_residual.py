from __future__ import annotations

import json
from pathlib import Path

from .ark_provider import ArkResponsesClient
from .config import PROJECT_ROOT

R32 = PROJECT_ROOT / "generated" / "ark-r32-repair-candidates.json"
AUDIT = PROJECT_ROOT / "generated" / "ark-r32-internal-audit.json"
OUTPUT = PROJECT_ROOT / "generated" / "ark-r33-compiler-residual.json"
MODEL = "deepseek-v4-pro"


def main() -> int:
    children=json.loads(R32.read_text(encoding="utf-8"))["repairs"]
    child=next(x for x in children if x["parent_id"]=="compiler-residual-contract-editor-v53")
    audits=json.loads(AUDIT.read_text(encoding="utf-8"))["ideas"]
    audit=next(x for x in audits if x["idea_id"]=="compiler-residual-contract-editor-v53-r32")
    prompt=f"""Repair one ICLR idea for the THIRD and final internal iteration.

The only remaining objection is precise: the current child claims a residual-specific typed whitelist, but its comparison only shows generic output-space restriction helps. You MUST operationalize a third matched control, not just mention it in a title:
- Residual-typed editor: whitelist = dependency-edge / semantic-predicate / temporal-relation residual vocabulary.
- Non-residual typed editor: whitelist has MATCHED cardinality and MATCHED syntactic complexity but is drawn from an equally typed, non-residual edit vocabulary.
- Unrestricted local-delta editor: no whitelist.
All three receive identical compiled state, residual supervision, target traces, labels, verifier access, parameter count, calls, tokens, optimizer steps, and wall-clock.
The decisive test is on the preregistered residual-required held-out set with a crossed unseen-model × unseen-harness swap. The residual-structure claim survives only if residual-typed > non-residual-typed > or != unrestricted as preregistered; if non-residual typed matches residual typed, re-scope to generic output-space restriction and stop claiming residual specificity.

Do not change the research problem. Keep the frozen persistent migrated contract asset. Independent truth is hidden target execution/assertion truth.

Original r32 child:
{json.dumps(child,ensure_ascii=False,indent=2)}

Flash audit finding:
{json.dumps(audit,ensure_ascii=False,indent=2)}

Return JSON only with all fields from the original child, but id must be compiler-residual-contract-editor-v53-r33 and r32_id must be compiler-residual-contract-editor-v53-r32. Add/modify the method, strongest_matched_baseline, shared_information_budget, decisive_pilot, stop_condition, surviving_claim, and why_remaining_boundary_is_closed so the three-condition comparison is fully operationalized in the body.
"""
    response=ArkResponsesClient().respond(prompt,model=MODEL,max_output_tokens=8000,thinking="disabled")
    text=response["text"].strip(); start=text.find("{"); end=text.rfind("}")
    if start<0 or end<=start: raise ValueError("no JSON object")
    row=json.loads(text[start:end+1])
    row["generator_model"]=MODEL
    if row.get("id")!="compiler-residual-contract-editor-v53-r33": raise ValueError(f"bad id {row.get('id')}")
    row["r32_id"]="compiler-residual-contract-editor-v53-r32"
    OUTPUT.write_text(json.dumps({"schema_version":"1.0","repair":row,"usage":response.get("usage") or {}},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(row["id"])
    return 0

if __name__=="__main__": raise SystemExit(main())
