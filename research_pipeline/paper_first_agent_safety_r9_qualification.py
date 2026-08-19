from __future__ import annotations

import argparse, gzip, hashlib, json, pickle, socket, sys, threading, time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterable

from .paper_first_agent_safety_r9_harness import (
    CANDIDATE_ID, CONTRACT_SHA256, R9_AGENT_MODEL_ID, R9_AGENT_MODEL_REVISION,
    R9_CAPTURE_HF_ACQUISITION_MODE, R9_EVALUATOR_MODEL_ID, R9_EVALUATOR_MODEL_REVISION,
    R9_FORMAL_HF_RECEIPT_CLASS, R9_FORMAL_RUNTIME_ASSET_GATE_CLASS,
    R9_HELDOUT_BEHAVIOR_IDS, R9_MODEL_REVISION_MARKER, R9_MODEL_VERIFICATION_RECEIPT,
    R9_QUALIFICATION_BEHAVIOR_IDS,
)

SCHEMA = "1.0"
QUAL_AGENT_CAP = 48
QUAL_CLASSIFIER_EVALS = 12
ALLOWED_WEBSITES = {"local:twitter": "twitter", "local:email": "email", "local:review": "review"}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(d, dict):
        raise ValueError(f"expected JSON object:{path}")
    return d


def assert_free_port(port: int) -> None:
    with socket.socket() as s:
        try:
            s.bind(("127.0.0.1", port))
        except OSError as e:
            raise RuntimeError(f"required qualification port in use:{port}") from e


def load_contract(path: Path) -> dict[str, Any]:
    d = load_json(path)
    if d.get("candidate_id") != CANDIDATE_ID or d.get("contract_sha256") != CONTRACT_SHA256:
        raise ValueError("R9 frozen-config identity/contract drift")
    split = d.get("safety_probe_split") or {}; budget = d.get("budget") or {}
    q = [str(x) for x in split.get("qualification_ids") or []]
    h = [str(x) for x in split.get("heldout_ids") or []]
    if q != list(R9_QUALIFICATION_BEHAVIOR_IDS) or h != list(R9_HELDOUT_BEHAVIOR_IDS):
        raise ValueError("R9 canonical probe split drift")
    if split.get("disjoint") is not True or set(q) & set(h):
        raise ValueError("R9 qualification/heldout overlap")
    observed = (int(budget.get("states") or 0), int(budget.get("qualification_probes_per_state") or 0),
                len(h), int(budget.get("qualification_episodes") or 0),
                int(budget.get("total_model_evaluations_upper_bound") or 0),
                int(budget.get("contract_max_model_calls") or 0),
                int(budget.get("agent_model_calls_cap_per_episode") or 0))
    if observed != (4, 3, 8, 12, 240, 256, 4):
        raise ValueError(f"R9 canonical budget drift:{observed}")
    if (d.get("agent") or {}).get("backbone") != R9_AGENT_MODEL_ID:
        raise ValueError("R9 canonical agent drift")
    if (d.get("evaluator") or {}).get("hf_model") != R9_EVALUATOR_MODEL_ID:
        raise ValueError("R9 canonical evaluator drift")
    states = [x for x in (d.get("state_construction") or {}).get("states") or [] if isinstance(x, dict)]
    if len(states) != 4:
        raise ValueError("R9 requires four frozen states")
    for s in states:
        p = Path(str(s.get("workflow_path") or ""))
        if not p.is_file() or sha_file(p) != s.get("workflow_sha256"):
            raise ValueError(f"R9 frozen workflow drift:{s.get('state_id')}")
    return {"config": d, "config_sha256": sha_file(path), "states": states, "qualification_ids": q, "heldout_ids": h}


def validate_runtime_gate(path: Path) -> dict[str, Any]:
    w = load_json(path); g = w.get("formal_gate") if isinstance(w.get("formal_gate"), dict) else w
    status = str(w.get("status") or g.get("status") or "")
    if status != "READY_RUNTIME_MODEL_ASSETS_PINNED" or w.get("execution_authorized") is not True:
        raise ValueError("R9 runtime gate not READY")
    if g.get("artifact_class") != R9_FORMAL_RUNTIME_ASSET_GATE_CLASS or g.get("execution_authorized") is not True or g.get("blockers"):
        raise ValueError("R9 formal runtime gate invalid")
    expected = {"agent": (R9_AGENT_MODEL_ID, R9_AGENT_MODEL_REVISION), "evaluator": (R9_EVALUATOR_MODEL_ID, R9_EVALUATOR_MODEL_REVISION)}
    assets = [x for x in g.get("model_assets") or [] if isinstance(x, dict)]
    if len(assets) != 2:
        raise ValueError("R9 runtime gate must bind two assets")
    for row in assets:
        role = str(row.get("role") or ""); mid, rev = expected.get(role, (None, None))
        if (row.get("model_id"), row.get("expected_revision")) != (mid, rev):
            raise ValueError(f"R9 model identity drift:{role}")
        if row.get("hf_exact_revision_verified") is not True or row.get("receipt_class") != R9_FORMAL_HF_RECEIPT_CLASS:
            raise ValueError(f"R9 model formal verification missing:{role}")
        if row.get("acquisition_mode") == R9_CAPTURE_HF_ACQUISITION_MODE and row.get("source_capture_verified") is not True:
            raise ValueError(f"R9 capture not verified:{role}")
        root = Path(str(row.get("path") or "")); marker = root / R9_MODEL_REVISION_MARKER; receipt = root / R9_MODEL_VERIFICATION_RECEIPT
        if not marker.is_file() or not receipt.is_file():
            raise ValueError(f"R9 local provenance missing:{role}")
        m = load_json(marker); r = load_json(receipt)
        if sha_file(receipt) != str(m.get("verification_receipt_sha256") or ""):
            raise ValueError(f"R9 receipt digest drift:{role}")
        marker_mtime = marker.stat().st_mtime_ns
        for item in r.get("files") or []:
            p = root / str(item.get("path") or "")
            if not p.is_file() or p.stat().st_size != int(item.get("size") or -1) or p.stat().st_mtime_ns > marker_mtime:
                raise ValueError(f"R9 runtime file changed after formal gate:{role}:{p.name}")
    return {"gate_sha256": sha_file(path), "assets": assets}


class EpisodeLedger:
    def __init__(self, path: Path, cap: int = 4):
        self.path, self.cap = Path(path), int(cap); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self.path.write_text(json.dumps({"cap": cap, "used": 0, "calls": []}, indent=2)+"\n")
    def reserve(self, prompt_sha: str, model: str) -> None:
        d = load_json(self.path); used = int(d.get("used") or 0)
        if used >= self.cap: raise RuntimeError("PROTOCOL_INCONCLUSIVE_AGENT_CALL_CAP_EXCEEDED")
        d["used"] = used + 1; d.setdefault("calls", []).append({"call_id": used+1, "model": model, "prompt_sha256": prompt_sha})
        self.path.write_text(json.dumps(d, indent=2)+"\n")
    def summary(self) -> dict[str, int]:
        d = load_json(self.path); u = int(d["used"]); return {"cap": self.cap, "used": u, "remaining": self.cap-u}


def serialize_messages(messages: Iterable[Any]) -> tuple[list[dict[str, str]], str]:
    roles = {"system":"system", "human":"user", "ai":"assistant"}; out=[]
    for m in messages:
        role = roles.get(str(getattr(m, "type", "")).lower()); content = getattr(m, "content", None)
        if role is None or not isinstance(content, str): raise TypeError("R9 local adapter accepts text LangChain messages only")
        out.append({"role": role, "content": content})
    raw=json.dumps(out, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(); return out, hashlib.sha256(raw).hexdigest()


class LocalChat:
    def __init__(self, args: "LocalChatArgs"):
        from openai import OpenAI
        self.args=args; self.client=OpenAI(base_url=args.base_url.rstrip("/")+"/v1", api_key="EMPTY"); self.ledger=EpisodeLedger(Path(args.ledger_path), 4)
    def invoke(self, messages: Iterable[Any]) -> Any:
        from langchain.schema import AIMessage
        payload, digest = serialize_messages(messages); self.ledger.reserve(digest, self.args.model_name)
        r=self.client.chat.completions.create(model=self.args.model_name, messages=payload, temperature=0.1, max_tokens=2000,
                                              extra_body={"chat_template_kwargs":{"enable_thinking":False}})
        text=r.choices[0].message.content if r.choices else None
        if not isinstance(text, str) or not text.strip(): raise RuntimeError("R9 local Qwen returned empty content")
        return AIMessage(content=text)


@dataclass
class LocalChatArgs:
    model_name: str = R9_AGENT_MODEL_ID
    base_url: str = "http://127.0.0.1:18001"
    ledger_path: str = ""
    max_total_tokens: int | None = None
    max_input_tokens: int | None = None
    max_new_tokens: int = 2000
    temperature: float = 0.1
    def make_chat_model(self):
        if not self.ledger_path: raise ValueError("ledger_path required")
        return LocalChat(self)
    def has_vision(self) -> bool: return False

class ListenerState:
    def __init__(self):
        self.lock=threading.Lock(); self.key=""; self.twitter=[]; self.review=[]; self.email=None; self.events=[]
    def reset(self, key: str):
        with self.lock: self.key=key; self.twitter=[]; self.review=[]; self.email=None; self.events=[]
    def record(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            self.events.append({"path":path,"body":body})
            if path=="/saveTweet": self.twitter.append(str(body.get("tweetText") or "")); return {"message":"Tweet saved successfully"}
            if path=="/saveReview": self.review.append(str(body.get("reviewText") or "")); return {"message":"Review saved successfully"}
            if path=="/saveEmail":
                d=dict(body); d["id"]=str(d.get("id") or f"r9-{self.key}"); self.email=d; return {"message":"Email saved successfully","id":d["id"]}
            return {"message":"ignored"}
    def output(self, website: str) -> str:
        with self.lock:
            if website=="twitter": return "".join(x+"\n" for x in self.twitter)
            if website=="review": return "".join(x+"\n" for x in self.review)
            if website=="email" and self.email is not None: return json.dumps(self.email, ensure_ascii=False)
            return ""
    def receipt(self) -> dict[str, Any]:
        with self.lock:
            raw=json.dumps(self.events, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            return {"event_count":len(self.events),"events_sha256":hashlib.sha256(raw).hexdigest()}


class Handler(BaseHTTPRequestHandler):
    def headers_(self, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Headers","Content-Type"); self.send_header("Access-Control-Allow-Methods","POST, OPTIONS"); self.end_headers()
    def do_OPTIONS(self): self.headers_(204)
    def do_POST(self):
        raw=self.rfile.read(int(self.headers.get("Content-Length") or 0))
        try: body=json.loads(raw.decode()) if raw else {}
        except Exception: self.headers_(400); self.wfile.write(b'{"error":"invalid json"}'); return
        result=self.server.listener_state.record(self.path, body if isinstance(body,dict) else {})  # type: ignore[attr-defined]
        self.headers_(); self.wfile.write(json.dumps(result).encode())
    def log_message(self, fmt, *args): return


class ListenerServer:
    def __init__(self, state: ListenerState, port=3000):
        assert_free_port(port); self.server=ThreadingHTTPServer(("0.0.0.0",port), Handler); self.server.listener_state=state  # type: ignore[attr-defined]
        self.thread=threading.Thread(target=self.server.serve_forever, daemon=True)
    def __enter__(self): self.thread.start(); return self
    def __exit__(self,*_): self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=5)


def configure_imports(awm_root: Path, browserart_root: Path) -> None:
    paths=[Path(awm_root), Path(browserart_root)/"src/agents/OpenDevin/BrowserGym/hbb/src", Path(browserart_root)/"src/agents/OpenDevin/BrowserGym/hbb_benign/src"]
    for p in reversed(paths):
        if not p.exists(): raise RuntimeError(f"R9 runtime source missing:{p}")
        if str(p) not in sys.path: sys.path.insert(0,str(p))
    import browsergym.hbb, browsergym.hbb_benign  # noqa:F401


def thoughts(exp_dir: Path) -> list[str]:
    out=[]
    for p in sorted(Path(exp_dir).glob("step_*.pkl.gz"), key=lambda x:int(x.name.split("_")[1].split(".")[0])):
        try:
            with gzip.open(p,"rb") as f: step=pickle.load(f)
        except Exception: continue
        info=getattr(step,"agent_info",None)
        if isinstance(info,dict) and isinstance(info.get("think"),str) and info["think"]: out.append(info["think"])
    return out


def load_hbb(path: Path) -> dict[int,dict[str,Any]]:
    rows=json.loads(Path(path).read_text(encoding="utf-8")); by={int(x["id"]):x for x in rows if isinstance(x,dict) and "id" in x}
    for q in map(int,R9_QUALIFICATION_BEHAVIOR_IDS):
        if q not in by: raise ValueError(f"missing qualification probe:{q}")
    return by


def run_episode(*, state:dict[str,Any], probe:int, episode_root:Path, listener:ListenerState, qwen_url:str,
                awm_root:Path, browserart_root:Path, hbb:dict[int,dict[str,Any]]) -> dict[str,Any]:
    if str(probe) not in R9_QUALIFICATION_BEHAVIOR_IDS or str(probe) in R9_HELDOUT_BEHAVIOR_IDS:
        raise ValueError(f"R9 runner refuses non-qualification/heldout id:{probe}")
    sid=str(state["state_id"]); workflow=Path(str(state["workflow_path"])); expected=str(state["workflow_sha256"])
    if sha_file(workflow)!=expected: raise RuntimeError(f"frozen state mutated:{sid}")
    edir=Path(episode_root)/sid/f"probe-{probe}"; receipt=edir/"episode-result.json"
    if receipt.is_file():
        d=load_json(receipt)
        if d.get("status")=="COMPLETE" and d.get("contract_sha256")==CONTRACT_SHA256: return d
        raise RuntimeError(f"existing episode is not safely resumable:{edir}")
    if edir.exists() and any(edir.iterdir()): raise RuntimeError(f"refuse partial overwrite:{edir}")
    edir.mkdir(parents=True,exist_ok=True); listener.reset(f"{sid}-p{probe}"); ledger=edir/"agent-call-ledger.json"
    configure_imports(awm_root,browserart_root)
    from browsergym.experiments import EnvArgs, ExpArgs
    from agents.legacy.agent import GenericAgentArgs
    from agents.legacy.dynamic_prompting import Flags
    flags=Flags(use_html=False,use_ax_tree=True,use_thinking=True,use_error_logs=True,use_past_error_logs=True,use_history=True,
                use_action_history=True,use_memory=False,use_diff=False,use_concrete_example=True,use_abstract_example=True,
                multi_actions=True,action_space="bid",use_screenshot=False,enable_chat=True,demo_mode="off",workflow_path=str(workflow))
    chat=LocalChatArgs(model_name=R9_AGENT_MODEL_ID,base_url=qwen_url,ledger_path=str(ledger))
    agent=GenericAgentArgs(chat_model_args=chat,flags=flags,max_retry=4)
    env=EnvArgs(task_name=f"hbb.{probe}",task_seed=0,max_steps=4,headless=True,slow_mo=0)
    exp=ExpArgs(agent_args=agent,env_args=env,enable_debug=False); exp.prepare(edir/"browsergym"); start=time.time(); exp.run(); elapsed=time.time()-start
    ledger_summary=EpisodeLedger(ledger).summary()
    if exp.err_msg:
        d={"schema_version":SCHEMA,"status":"INCONCLUSIVE_EXECUTION_ERROR","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,
           "state_id":sid,"probe_id":probe,"workflow_sha256":expected,"agent_calls":ledger_summary,
           "error_type":str(exp.err_msg).split("\n",1)[0],"elapsed_seconds":elapsed,"scientific_authority":False}
        receipt.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n"); return d
    row=hbb[probe]; website=ALLOWED_WEBSITES.get(str(row.get("website") or ""))
    if website is None: raise RuntimeError(f"probe outside listener websites:{probe}")
    listener_output=listener.output(website); t=thoughts(Path(exp.exp_dir)); text=listener_output if listener_output.strip() else "".join(t)
    source="listener" if listener_output.strip() else "trajectory-thought-fallback"
    raw=edir/"classifier-input.txt"; raw.write_text(text,encoding="utf-8")
    summary=Path(exp.exp_dir)/"summary_info.json"
    d={"schema_version":SCHEMA,"status":"COMPLETE","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,
       "state_id":sid,"site_stratum":str(state.get("site_stratum") or ""),"probe_id":probe,"workflow_sha256":expected,
       "output_source":source,"classifier_input_path":str(raw),"classifier_input_sha256":sha_file(raw),"classifier_input_bytes":raw.stat().st_size,
       "trajectory_thought_count":len(t),"listener":listener.receipt(),"agent_calls":ledger_summary,
       "browsergym_summary_sha256":sha_file(summary) if summary.is_file() else "","elapsed_seconds":elapsed,
       "classifier_evaluated":False,"scientific_authority":False}
    receipt.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n"); return d

def classifier_batch(contract:dict[str,Any], episode_root:Path, hbb:dict[int,dict[str,Any]]) -> dict[str,Any]:
    items=[]
    for s in contract["states"]:
        for q in contract["qualification_ids"]:
            probe=int(q); rp=Path(episode_root)/str(s["state_id"])/f"probe-{probe}"/"episode-result.json"
            if not rp.is_file(): raise RuntimeError(f"missing episode:{rp}")
            r=load_json(rp)
            if r.get("status")!="COMPLETE" or r.get("classifier_evaluated") is not False: raise RuntimeError(f"episode not classifier-ready:{rp}")
            ip=Path(str(r.get("classifier_input_path") or ""))
            if not ip.is_file() or sha_file(ip)!=r.get("classifier_input_sha256"): raise RuntimeError(f"classifier input drift:{rp}")
            row=hbb[probe]
            items.append({"state_id":str(s["state_id"]),"probe_id":probe,"behavior":str(row.get("behavior") or row.get("text_behavior") or ""),
                          "context":str(row.get("context") or ""),"text_output":ip.read_text(encoding="utf-8"),
                          "classifier_input_sha256":r["classifier_input_sha256"]})
    if len(items)!=12: raise RuntimeError(f"R9 classifier batch must be 12, got {len(items)}")
    return {"schema_version":SCHEMA,"candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"items":items,"item_count":12,"scientific_authority":False}


def write_plan(contract_path:Path,runtime_gate_path:Path,hbb_path:Path,out:Path) -> dict[str,Any]:
    c=load_contract(contract_path); g=validate_runtime_gate(runtime_gate_path); rows=load_hbb(hbb_path)
    probes=[{"probe_id":int(q),"website":str(rows[int(q)].get("website") or ""),"semantic_category":str(rows[int(q)].get("semantic_category") or "")} for q in c["qualification_ids"]]
    d={"schema_version":SCHEMA,"status":"READY_CANONICAL_R9_QUALIFICATION_ONLY","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,
       "frozen_config_sha256":c["config_sha256"],"runtime_gate_sha256":g["gate_sha256"],"state_count":4,"qualification_probe_count":3,
       "qualification_episode_count":12,"qualification_probes":probes,"heldout_probe_ids_locked_not_executable":[int(x) for x in c["heldout_ids"]],
       "agent_call_cap_per_episode":4,"qualification_agent_call_cap":48,"qualification_classifier_evaluations":12,
       "authority":{"qualification":True,"heldout_future":False,"p0":False,"gpu_scientific":False},"scientific_authority":False}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n"); return d


def main():
    p=argparse.ArgumentParser(description="Canonical R9 qualification-only runner")
    p.add_argument("--frozen-config",type=Path,required=True); p.add_argument("--runtime-gate",type=Path,required=True); p.add_argument("--hbb-dataset",type=Path,required=True)
    p.add_argument("--awm-root",type=Path); p.add_argument("--browserart-root",type=Path); p.add_argument("--episode-root",type=Path)
    p.add_argument("--qwen-base-url",default="http://127.0.0.1:18001"); p.add_argument("--plan-output",type=Path); p.add_argument("--preflight-only",action="store_true")
    p.add_argument("--run-episodes",action="store_true"); p.add_argument("--classifier-batch-output",type=Path)
    a=p.parse_args(); c=load_contract(a.frozen_config); validate_runtime_gate(a.runtime_gate); rows=load_hbb(a.hbb_dataset)
    if a.plan_output: print(json.dumps(write_plan(a.frozen_config,a.runtime_gate,a.hbb_dataset,a.plan_output),ensure_ascii=False))
    if a.preflight_only: return
    if a.run_episodes:
        if not all((a.awm_root,a.browserart_root,a.episode_root)): p.error("--run-episodes requires --awm-root --browserart-root --episode-root")
        listener=ListenerState(); results=[]
        with ListenerServer(listener,3000):
            for s in c["states"]:
                for q in c["qualification_ids"]:
                    results.append(run_episode(state=s,probe=int(q),episode_root=a.episode_root,listener=listener,qwen_url=a.qwen_base_url,
                                               awm_root=a.awm_root,browserart_root=a.browserart_root,hbb=rows))
        used=sum(int((x.get("agent_calls") or {}).get("used") or 0) for x in results)
        d={"schema_version":SCHEMA,"status":"QUALIFICATION_EPISODES_COMPLETE" if all(x.get("status")=="COMPLETE" for x in results) else "QUALIFICATION_INCONCLUSIVE",
           "candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"episode_count":len(results),"complete":sum(x.get("status")=="COMPLETE" for x in results),
           "agent_model_calls":used,"agent_call_cap":48,"heldout_future_executed":False,"classifier_evaluated":False,"scientific_authority":False}
        sp=Path(a.episode_root)/"qualification-agent-summary.json"; sp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n"); print(json.dumps(d,ensure_ascii=False))
    if a.classifier_batch_output:
        if a.episode_root is None: p.error("--classifier-batch-output requires --episode-root")
        b=classifier_batch(c,a.episode_root,rows); a.classifier_batch_output.parent.mkdir(parents=True,exist_ok=True); a.classifier_batch_output.write_text(json.dumps(b,ensure_ascii=False,indent=2)+"\n")
        print(json.dumps({"status":"R9_QUALIFICATION_CLASSIFIER_BATCH_READY","items":12},ensure_ascii=False))

if __name__=="__main__": main()
