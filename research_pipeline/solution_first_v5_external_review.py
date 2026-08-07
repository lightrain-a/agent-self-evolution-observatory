from __future__ import annotations

import argparse, json, math, socket, subprocess, sys, time
from pathlib import Path
from typing import Any, Sequence

from .config import PROJECT_ROOT, StorageSettings
from .iclr_external_review import EXPECTED_HOST, _atomic_json, extract_json, normalize_response, update_store
from .idea_discovery_v5 import DEFAULT_EXTERNAL_JSON, DEFAULT_JSON, build_idea_discovery_v5, write_idea_discovery_v5

REVIEWER = "agent-project-web-gpt-idea-discovery-v5-area-chair"


def load_bank(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else build_idea_discovery_v5()
    if not isinstance(payload.get("finalists"), list): raise ValueError("v5 bank has no finalists")
    return payload


def packet(x: dict[str, Any]) -> dict[str, Any]:
    return {
        "idea_id": x["id"], "title": x["title"]["en"], "internal_status": x["internal_status"],
        "parent_ids": x.get("parent_ids", []), "problem": x["problem"]["en"],
        "exact_mechanism": x["exact_mechanism"]["en"], "update_surface": x["update_surface"],
        "learning_signal": x["learning_signal"]["en"], "independent_ground_truth": x["independent_ground_truth"]["en"],
        "components": x.get("components", []), "necessity_logic": x["necessity_logic"]["en"],
        "strongest_baseline": x["strongest_baseline"]["en"], "decisive_pilot": x["decisive_pilot"]["en"],
        "stop_condition": x["stop_condition"]["en"], "revival_condition": (x.get("revival_condition") or {}).get("en", ""),
        "repository_patterns": x.get("repository_patterns", []), "scores": x.get("scores", {}),
    }


def build_prompt(ideas: Sequence[dict[str, Any]], *, batch_index: int, batch_count: int) -> str:
    schema = {"reviewer": REVIEWER, "review_date": "YYYY-MM-DD", "ideas": [{
        "idea_id":"exact supplied id", "verdict":"pass|revise|block", "confidence":"high|medium|low",
        "finding":"English judgment", "finding_zh":"中文判断", "required_action":"English material action", "required_action_zh":"中文修改要求",
        "simplification_challenge":{"simplest_equivalent_method":"capacity-matched simpler method","reducible":"yes|partial|no","what_must_survive":"non-removable learning object or operator"},
        "combination_audit":{"all_components_necessary":"yes|partial|no","removable_components":["component"],"closed_failure_loop":"one sentence"},
        "direct_collision":{"status":"none|partial|direct|unknown","closest_work":[{"title":"exact title","venue_year":"venue/year","official_url":"official URL","overlap":"problem|mechanism|combination|experiment"}],"surviving_difference":"remaining boundary"},
        "revival_assessment":"material-change|cosmetic-change|not-applicable", "strongest_baseline":"strongest erasing baseline",
        "decisive_pilot":"one matched-budget falsification", "stop_rule":"specific Stop rule", "unknowns":["unverified facts"]
    }]}
    return f"""# Independent ICLR Idea Discovery v5 audit — batch {batch_index}/{batch_count}

Act as a strict ICLR area chair and solution-search auditor. This v5 pool deliberately widens search: real failure evidence is triangulated with literature, structured combinations are allowed, and old REVISE/BLOCK branches may revive after material changes. Do NOT block an idea simply because it combines known components. Do NOT pass an idea merely because the problem is real.

Use web search and only official paper pages/PDFs, OpenReview/proceedings, official project pages, and author-maintained repositories. Check work available through 2026-08-01.

For each idea test:
1. Is the failure real and important enough for an ICLR method thesis?
2. Does the persistent learned object change future behavior after freezing?
3. Are signal and ground truth independently identifiable?
4. Are all listed components necessary to close distinct sensing/credit/update/evaluation paths?
5. Run a simplification challenge: propose the strongest capacity-matched simpler method using the same data, calls, tokens, training and evaluation budget. If it reproduces the claim, REVISE/BLOCK.
6. For revived ideas, verify the changed learning object/supervision is material, not wording.
7. Require held-out model/domain/version/composition transfer where relevant.
8. The pilot must falsify the mechanism, not just show the broad problem exists.

Verdicts:
- PASS: standalone thesis survives simplification and collision audit; mechanism is identifiable and low-resource falsifiable.
- REVISE: real problem with a plausible path, but one material objective/component/supervision/boundary must change.
- BLOCK: not standalone now; retain as component, baseline, or revival source rather than deleting it.

Return exactly one JSON object, no prose outside JSON. Preserve all exact IDs.
Schema:\n```json\n{json.dumps(schema,ensure_ascii=False,indent=2)}\n```\nCandidates:\n```json\n{json.dumps([packet(x) for x in ideas],ensure_ascii=False,indent=2)}\n```\n"""


def normalize_v5(payload: dict[str, Any], ids: Sequence[str], source: str) -> dict[str, dict[str, Any]]:
    reviews = normalize_response(payload, ids, source_artifact=source)
    rows = {str(r.get("idea_id")): r for r in payload.get("ideas", []) if isinstance(r, dict)}
    for i, review in reviews.items():
        row = rows.get(i, {}); review["simplification_challenge"] = row.get("simplification_challenge", {})
        review["combination_audit"] = row.get("combination_audit", {}); review["revival_assessment"] = str(row.get("revival_assessment") or "not-applicable")
    return reviews


def read_store(path: Path = DEFAULT_EXTERNAL_JSON) -> dict[str, Any]:
    if path.exists():
        p = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(p, dict) and isinstance(p.get("reviews"), dict): return p
    return {"schema_version":"1.0","pipeline":"code-oracle -> signed-in ChatGPT web UI -> Agent project","required_host":EXPECTED_HOST,"reviews":{},"status":{"reviewed":0,"pending":32,"complete":False,"failed_batches":0}}


def prepare_batches(bank: dict[str, Any], out: Path, batch_size: int, store: dict[str, Any]) -> dict[str, Any]:
    done = store.get("reviews", {}); ideas = [x for x in bank["finalists"] if not done.get(x["id"])]
    out.mkdir(parents=True, exist_ok=True); count = math.ceil(len(ideas)/batch_size) if ideas else 0; batches=[]
    for n in range(count):
        chunk=ideas[n*batch_size:(n+1)*batch_size]; pp=out/f"batch-{n+1:02d}-of-{count:02d}.md"; rp=out/f"batch-{n+1:02d}-of-{count:02d}.response.md"
        pp.write_text(build_prompt(chunk,batch_index=n+1,batch_count=count),encoding="utf-8"); batches.append({"index":n+1,"idea_ids":[x["id"] for x in chunk],"prompt":str(pp),"response":str(rp)})
    manifest={"schema_version":"1.0","total_finalists":len(bank["finalists"]),"queued_ideas":len(ideas),"batch_size":batch_size,"batches":batches}; _atomic_json(out/"manifest.json",manifest); return manifest


def run_batches(bank: dict[str, Any], manifest: dict[str, Any], store_path: Path, timeout: int) -> dict[str, Any]:
    host=socket.gethostname(); ids=[x["id"] for x in bank["finalists"]]
    if host != EXPECTED_HOST: raise RuntimeError(f"requires {EXPECTED_HOST}; current {host}")
    runner=PROJECT_ROOT/"scripts"/"project_web_gpt.py"; store=read_store(store_path)
    for batch in manifest["batches"]:
        pp=Path(batch["prompt"]); rp=Path(batch["response"]); error=""
        for attempt in range(1,4):
            rp.unlink(missing_ok=True)
            cmd=[sys.executable,str(runner),"Review the attached ICLR Idea Discovery v5 batch. Return only the required JSON object.","--file",str(pp),"--slug",f"idea-discovery-v5-{batch['index']:02d}-attempt-{attempt}","--timeout",str(timeout),"--output",str(rp)]
            done=subprocess.run(cmd,cwd=PROJECT_ROOT,text=True,capture_output=True,check=False,timeout=timeout+60)
            try:
                if done.returncode: raise RuntimeError(done.stderr[-3000:] or done.stdout[-3000:])
                payload=extract_json(rp.read_text(encoding="utf-8")); reviews=normalize_v5(payload,batch["idea_ids"],str(rp))
                store=update_store(store,reviews,all_ids=ids,attempt_result=f"batch_{batch['index']}_completed",attempt_host=host); _atomic_json(store_path,store); write_idea_discovery_v5(); break
            except Exception as exc:
                error=str(exc)
                if attempt<3: time.sleep(45*attempt)
        else: raise RuntimeError(error or f"batch {batch['index']} failed")
    return store


def main(argv: Sequence[str] | None = None) -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--run",action="store_true"); ap.add_argument("--batch-size",type=int,default=6); ap.add_argument("--timeout",type=int,default=900); args=ap.parse_args(argv)
    st=StorageSettings.from_env(); st.ensure(); bank=load_bank(); out=st.run_dir/"reviews"/"idea-discovery-v5-web-gpt"; store=read_store(); manifest=prepare_batches(bank,out,args.batch_size,store)
    if args.run: print(json.dumps(run_batches(bank,manifest,DEFAULT_EXTERNAL_JSON,args.timeout).get("status",{}),ensure_ascii=False))
    else: print(json.dumps({"output_dir":str(out),"queued":manifest["queued_ideas"],"batches":len(manifest["batches"])},ensure_ascii=False))
    return 0

if __name__ == "__main__": raise SystemExit(main())
