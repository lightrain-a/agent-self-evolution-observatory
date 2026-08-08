from __future__ import annotations
import json
from .ark_provider import ArkResponsesClient, extract_json_object
from .config import PROJECT_ROOT
SOURCE=PROJECT_ROOT/"generated"/"ark-r34-compiler-residual.json"; OUTPUT=PROJECT_ROOT/"generated"/"ark-r34-compiler-residual-audit.json"; MODEL="deepseek-v4-flash"
def main()->int:
 c=json.loads(SOURCE.read_text(encoding="utf-8"))["repair"]
 p=f"""Strictly audit this final repair. ADVANCE only if it now operationalizes all of: immutable SHA-256/versioned frozen M* loaded read-only across variants; independent pre-training hidden execution/assertion truth unavailable to learner/compiler oracle; one preregistered small-pilot go/re-scope/stop identification rule; a shared formal local-delta grammar G and matched non-residual whitelist including operation-effect distribution; three fair residual-typed/non-residual-typed/unrestricted conditions under identical information/capacity/compute; crossed unseen-model×unseen-harness full test; and explicit claim re-scope if non-residual typed matches residual typed. Return JSON only: {{"idea_id":"compiler-residual-contract-editor-v53-r34","verdict":"advance|revise|block","confidence":"high|medium|low","finding":"...","required_action":"...","simplification_resistance":0,"persistent_learning":0,"independent_truth":0,"pilot_identifiability":0}}.\nChild:\n{json.dumps(c,ensure_ascii=False,indent=2)}"""
 r=ArkResponsesClient().respond(p,model=MODEL,max_output_tokens=4000,thinking="disabled"); o=extract_json_object(r["text"]); OUTPUT.write_text(json.dumps({"schema_version":"1.0","judge":MODEL,"audit":o,"usage":r.get("usage") or {}},ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps(o,ensure_ascii=False)); return 0
if __name__=="__main__": raise SystemExit(main())
