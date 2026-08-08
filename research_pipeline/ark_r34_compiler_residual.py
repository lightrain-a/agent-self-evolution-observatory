from __future__ import annotations

import json
from .ark_provider import ArkResponsesClient, extract_json_object
from .config import PROJECT_ROOT

R33=PROJECT_ROOT/"generated"/"ark-r33-compiler-residual.json"
AUDIT=PROJECT_ROOT/"generated"/"ark-r33-compiler-residual-audit.json"
OUTPUT=PROJECT_ROOT/"generated"/"ark-r34-compiler-residual.json"
MODEL="glm-5.2"


def main()->int:
    child=json.loads(R33.read_text(encoding="utf-8"))["repair"]
    audit=json.loads(AUDIT.read_text(encoding="utf-8"))["audit"]
    prompt=f"""Perform one final targeted ICLR repair. Keep the same problem and three-condition residual-vs-non-residual-vs-unrestricted design, but operationalize the four missing contracts exactly.

Required additions:
1. Frozen persistent asset: define one immutable versioned JSON/IR contract state `M*` written once after training, content-addressed by SHA-256, loaded read-only by ALL variants and all audits. No target-time edits/relearning/search of M*.
2. Independent hidden truth: define a held-out execution/assertion suite whose expected outputs are produced before training by either human-validated specifications or a separate reference implementation/compiler with no access to repair training data, residual labels, or model outputs. The repair learner/compiler oracle cannot score this suite.
3. Decisive small pilot rule: preregister a small pilot on a fixed N of residual-required cases. Advance the residual-specific claim only if residual-typed A beats both non-residual-typed B and unrestricted C by a fixed margin/CI while B does not match A; if A≈B, immediately re-scope to generic typed restriction; if A fails C, stop. The pilot is a go/re-scope/stop decision, not a descriptive warm-up.
4. Equal action space/complexity: formally define one local-delta grammar G with primitive edit operators shared by A/B/C. A and B restrict only which typed tokens from G are whitelisted; C can use all G tokens. Construct B's non-residual whitelist to match A on cardinality, arity, token length, and empirical operation-effect distribution on a preregistered neutral calibration set. Same parameter count, optimizer, traces, verifier, calls, tokens, steps, and wall-clock.

Do not weaken the claim or omit the existing crossed unseen-model × unseen-harness full test. Return JSON only, preserving all useful r33 fields, with id=compiler-residual-contract-editor-v53-r34 and r33_id=compiler-residual-contract-editor-v53-r33. Explicitly update persistent_update_object, independent_ground_truth, shared_information_budget, decisive_pilot, method_logic, strongest_matched_baseline, stop_condition, surviving_claim, why_remaining_boundary_is_closed.

R33 child:
{json.dumps(child,ensure_ascii=False,indent=2)}

Audit:
{json.dumps(audit,ensure_ascii=False,indent=2)}
"""
    r=ArkResponsesClient().respond(prompt,model=MODEL,max_output_tokens=8000,thinking="disabled")
    row=extract_json_object(r["text"]); row["generator_model"]=MODEL; row["r33_id"]="compiler-residual-contract-editor-v53-r33"
    if row.get("id")!="compiler-residual-contract-editor-v53-r34": raise ValueError(f"bad id {row.get('id')}")
    OUTPUT.write_text(json.dumps({"schema_version":"1.0","repair":row,"usage":r.get("usage") or {}},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(row["id"]); return 0

if __name__=="__main__": raise SystemExit(main())
