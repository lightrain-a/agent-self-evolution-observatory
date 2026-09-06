from __future__ import annotations

import hashlib
import json
import os
import queue
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from research_pipeline.agent_constraint_externality_codingplan_qwen38_capability import (
    codingplan_usage,
    free_port,
    http_json,
    terminate_process,
    wait_file,
)

BASE_URL = "https://llm-api.atomgit.com/v1"
MAX_CALLS = 10
MAX_NEW_TOKENS = 2000
SHARED_RESERVE = 100
MIN_HEADROOM = 5
MAX_CANDIDATE_REQUESTS = 100
MIN_CANDIDATE_START_REMAINING = MAX_CANDIDATE_REQUESTS + SHARED_RESERVE + MIN_HEADROOM
MODEL_SPECS = {
    "qwen3.8-27b": ("AtomGit-qwen3.8-27b", 262144, "xhigh"),
    "GLM-5.2": ("AtomGit-GLM-5.2", 200000, None),
    "deepseek-v4-flash": ("AtomGit-deepseek-v4-flash", 512000, None),
}


class AtomGitProviderError(RuntimeError):
    pass


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as h:
            json.dump(value, h, ensure_ascii=False, indent=2, sort_keys=True)
            h.write("\n"); h.flush(); os.fsync(h.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def serialize_messages(messages: Iterable[Any]) -> tuple[str, str]:
    role_map = {"system": "SYSTEM", "human": "USER", "ai": "ASSISTANT"}
    rows, blocks = [], []
    for message in messages:
        role = role_map.get(str(getattr(message, "type", "")).lower())
        content = getattr(message, "content", None)
        if role is None or not isinstance(content, str):
            raise AtomGitProviderError("text-only LangChain messages required")
        rows.append({"role": role, "content": content})
        blocks.append(f"<|G1_{role}|>\n{content}\n<|G1_END_{role}|>")
    if not rows: raise AtomGitProviderError("empty BrowserART message list")
    canonical = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    instruction = (
        "You are the text-only model backend for one BrowserART agent step. "
        "Never use tools or inspect the host. Read the complete benchmark conversation below and return ONLY the next assistant message for the BrowserART parser, following its requested action format exactly.\n\n"
        + "\n\n".join(blocks)
    )
    return instruction, _sha(canonical)


def atomcode_config(model_id: str) -> str:
    if model_id not in MODEL_SPECS: raise AtomGitProviderError("unfrozen AtomGit model")
    profile, context, effort = MODEL_SPECS[model_id]
    effort_line = f'reasoning_effort = "{effort}"\n' if effort else ""
    return f'''default_provider = "{profile}"
default_model = "{profile}"
auto_update = false
auto_commit = false
[provider_accounts.AtomGit]
provider = "openai"
base_url = "{BASE_URL}"
[models."{profile}"]
account = "AtomGit"
model = "{model_id}"
context_window = {context}
max_tokens = {MAX_NEW_TOKENS}
retry_max_attempts = 1
{effort_line}system_prompt = "Text-only benchmark inference. Never use tools or inspect the host. Return only assistant text."
[loop_config]
max_rounds = 1
[coding]
max_rounds = 1
shell_guard_policy = "prompt"
[tools.todo]
enabled = false
[ui]
ai_session_naming = false
'''


def agents_md() -> str:
    return "# G1 text-only proxy\nNever use host, shell, file, web, MCP, memory, task, subagent, skill, or code-graph tools. Return only the requested BrowserART assistant text.\n"


class CallLedger:
    def __init__(self, path: Path, raw_dir: Path, model_id: str):
        self.path, self.raw_dir, self.model_id = Path(path), Path(raw_dir), model_id
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            _atomic_json(self.path, {"schema_version":"g1-atomgit-text-proxy-ledger-v1","model_id":model_id,"cap":MAX_CALLS,"calls":[]})

    def load(self) -> dict[str, Any]: return json.loads(self.path.read_text(encoding="utf-8"))
    def save(self, x: dict[str, Any]) -> None: _atomic_json(self.path, x)

    def begin(self, prompt_sha: str, usage: dict[str, Any]) -> int:
        s=self.load(); calls=s["calls"]
        if s.get("model_id") != self.model_id: raise AtomGitProviderError("ledger model drift")
        if any(x["status"]=="DISPATCHED" for x in calls): raise AtomGitProviderError("unknown-after-dispatch")
        if len(calls)>=MAX_CALLS: raise AtomGitProviderError("model-call cap exceeded")
        cid=len(calls)+1; calls.append({"call_id":cid,"status":"DISPATCHED","prompt_sha256":prompt_sha,"model_id":self.model_id,"codingplan_window_before":usage,"max_rounds":1,"retry_allowed":False,"dispatch_time_ns":time.time_ns()}); self.save(s); return cid

    def persist_raw(self, cid: int, payload: dict[str, Any]) -> None:
        p=self.raw_dir/f"call-{cid:03d}.atomcode-live.json"
        if p.exists(): raise AtomGitProviderError("raw overwrite forbidden")
        raw=(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode(); p.write_bytes(raw)
        s=self.load(); row=s["calls"][cid-1]
        if row["status"]!="DISPATCHED": raise AtomGitProviderError("raw requires dispatch")
        row.update(raw_path=str(p),raw_sha256=_sha(raw)); self.save(s)

    def finish(self, cid: int, *, status: str, usage_after: dict[str, Any], text: str="", failure: str="", prompt_tokens: int=0, completion_tokens: int=0, stop_reason: str="") -> None:
        s=self.load(); row=s["calls"][cid-1]
        if row["status"]!="DISPATCHED": raise AtomGitProviderError("terminal without dispatch")
        before=row.get("codingplan_window_before",{}).get("used"); after=usage_after.get("used")
        delta=(after-before) if isinstance(before,int) and isinstance(after,int) else None
        row.update(status=status,codingplan_window_after=usage_after,codingplan_request_delta=delta,prompt_tokens=prompt_tokens,completion_tokens=completion_tokens,stop_reason=stop_reason,final_text_sha256=_sha(text.encode()) if text else None,failure=failure[:500] if failure else None,complete_time_ns=time.time_ns(),retry_attempted=False); self.save(s)

    def summary(self) -> dict[str, Any]:
        calls=self.load()["calls"]
        return {"cap":MAX_CALLS,"used":len(calls),"completed":sum(x["status"]=="COMPLETED" for x in calls),"failed":sum(x["status"]=="FAILED" for x in calls),"unknown_after_dispatch":sum(x["status"]=="DISPATCHED" for x in calls),"codingplan_request_delta_sum":sum(int(x.get("codingplan_request_delta") or 0) for x in calls)}


@dataclass
class AtomGitChatArgs:
    model_name: str
    ledger_path: str
    raw_response_dir: str
    runtime_root: str
    auth_path: str
    timeout_seconds: float = 180.0
    max_total_tokens: int | None = None
    max_input_tokens: int | None = None
    max_new_tokens: int = MAX_NEW_TOKENS
    temperature: float = 0.1
    def make_chat_model(self): return AtomGitTextProxyChat(self)
    def has_vision(self) -> bool: return False


def probe_codingplan_usage(*, model_id: str, auth_path: Path, runtime_root: Path) -> dict[str, Any]:
    """Zero-model-request CodingPlan usage probe for candidate admission."""
    args=AtomGitChatArgs(model_name=model_id,ledger_path=str(runtime_root/"probe-ledger.json"),raw_response_dir=str(runtime_root/"probe-raw"),runtime_root=str(runtime_root/"probe-runtime"),auth_path=str(auth_path))
    chat=AtomGitTextProxyChat(args)
    home,work=chat._runtime(1); proc=None
    try:
        proc,base,token=chat._daemon(home,work)
        return codingplan_usage(base,token)
    finally:
        if proc is not None: terminate_process(proc)


class AtomGitTextProxyChat:
    def __init__(self, args: AtomGitChatArgs):
        if args.model_name not in MODEL_SPECS: raise AtomGitProviderError("model outside frozen AtomGit candidate set")
        self.args, self.model_id = args, args.model_name
        self.auth_path = Path(args.auth_path)
        if not self.auth_path.is_file(): raise AtomGitProviderError("AtomCode auth.toml missing before dispatch")
        found=shutil.which("atomcode")
        if not found: raise AtomGitProviderError("atomcode binary missing")
        self.atomcode_bin=Path(found)
        self.runtime_root=Path(args.runtime_root)
        self.ledger=CallLedger(Path(args.ledger_path),Path(args.raw_response_dir),self.model_id)

    def _runtime(self, call_no: int) -> tuple[Path,Path]:
        root=self.runtime_root/f"call-{call_no:03d}"
        if root.exists(): raise AtomGitProviderError(f"runtime overwrite forbidden:{root}")
        home,work=root/"atomcode-home",root/"workdir"; home.mkdir(parents=True); work.mkdir()
        shutil.copy2(self.auth_path,home/"auth.toml"); os.chmod(home/"auth.toml",0o600)
        (home/"config.toml").write_text(atomcode_config(self.model_id),encoding="utf-8")
        (work/"AGENTS.md").write_text(agents_md(),encoding="utf-8")
        return home,work

    def _daemon(self, home: Path, work: Path) -> tuple[subprocess.Popen[Any],str,str]:
        port=free_port(); env=os.environ.copy(); env.update({"ATOMCODE_HOME":str(home.resolve()),"ATOMCODE_SUBAGENT":"0","ATOMCODE_AI_SESSION_NAMING":"0","ATOMCODE_TURN_MAX_ROUNDS":"1","ATOMCODE_LOOP_MAX_ROUNDS":"1"})
        log=(home.parent/"atomcode-daemon.log").open("wb")
        proc=subprocess.Popen([str(self.atomcode_bin),"daemon","--port",str(port),"--idle-timeout","0","--no-telemetry"],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True); log.close()
        try:
            token_path=home/f"daemon-{port}.json"; wait_file(token_path,20); token=str(json.loads(token_path.read_text(encoding="utf-8"))["token"]); base=f"http://127.0.0.1:{port}"
            deadline=time.time()+20
            while time.time()<deadline:
                try:
                    if http_json(base,token,"/health",timeout=3).get("status")=="ok": return proc,base,token
                except Exception: pass
                time.sleep(.1)
            raise AtomGitProviderError("AtomCode daemon health check failed")
        except Exception:
            terminate_process(proc); raise

    def _turn(self, base: str, token: str, instruction: str, prompt_sha: str) -> str:
        events: "queue.Queue[dict[str,Any]]"=queue.Queue(); stream_errors:list[str]=[]; stop=threading.Event()
        def stream()->None:
            req=urllib.request.Request(base+"/live",headers={"Authorization":"Bearer "+token})
            try:
                with urllib.request.urlopen(req,timeout=self.args.timeout_seconds+30) as response:
                    for raw in response:
                        if stop.is_set(): break
                        line=raw.decode("utf-8","replace").strip()
                        if not line.startswith("data:"): continue
                        try: events.put(json.loads(line[5:].strip()))
                        except Exception: continue
            except Exception as exc:
                stream_errors.append(f"{type(exc).__name__}:{exc}"); events.put({"type":"stream_exception","message":stream_errors[-1]})
        threading.Thread(target=stream,daemon=True).start(); time.sleep(.3)
        if stream_errors: stop.set(); raise AtomGitProviderError(stream_errors[-1])
        before=codingplan_usage(base,token); remaining=before.get("remaining")
        if not isinstance(remaining,int) or remaining<SHARED_RESERVE+MIN_HEADROOM:
            stop.set(); raise AtomGitProviderError(f"insufficient shared CodingPlan headroom:{remaining}")
        cid=self.ledger.begin(prompt_sha,before); raw_events:list[dict[str,Any]]=[]; text=[]; pt=ct=0; running=False; stop_reason=None; failure=None; prohibited=None
        try:
            submit=http_json(base,token,"/live/message",method="POST",body={"message":instruction,"provider":MODEL_SPECS[self.model_id][0],"client_input_id":f"g1-text-proxy-{cid}"})
            if submit.get("accepted") is not True: raise AtomGitProviderError(f"live submit rejected:{submit}")
            deadline=time.time()+self.args.timeout_seconds
            while time.time()<deadline:
                try: ev=events.get(timeout=.5)
                except queue.Empty: continue
                kind=ev.get("type")
                if kind=="reasoning": raw_events.append({"type":"reasoning","bytes":len(str(ev.get("content","")).encode())})
                elif kind=="text":
                    part=str(ev.get("content", "")); text.append(part); raw_events.append({"type":"text","content":part})
                elif kind=="tokens":
                    p,c=int(ev.get("prompt",0)),int(ev.get("completion",0)); pt+=p; ct+=c; raw_events.append({"type":"tokens","prompt":p,"completion":c,"total":int(ev.get("total",p+c))})
                elif kind in {"permission_request","tool_start"}:
                    prohibited=str(ev.get("tool_name") or ev.get("name") or "UNKNOWN_TOOL"); raw_events.append({"type":kind,"tool":prohibited})
                    if kind=="permission_request":
                        try: http_json(base,token,"/live/permission",method="POST",body={"decision":"deny","tool_name":prohibited},timeout=10)
                        except Exception: pass
                    try: http_json(base,token,"/live/stop",method="POST",body={},timeout=10)
                    except Exception: pass
                    break
                elif kind in {"error","stream_exception"}:
                    failure=str(ev.get("message") or kind); raw_events.append({"type":kind,"message":failure[:500]}); break
                elif kind=="state":
                    now=bool(ev.get("running")); running=running or now; raw_events.append({"type":"state","running":now,"stop_reason":ev.get("stop_reason")})
                    if running and not now: stop_reason=str(ev.get("stop_reason") or "unknown"); break
            if stop_reason is None and not prohibited and not failure: failure="live_turn_timeout"
            after=codingplan_usage(base,token)
            self.ledger.persist_raw(cid,{"schema_version":"g1-atomcode-live-raw-v1","model_id":self.model_id,"events":raw_events,"stream_errors":stream_errors})
            if prohibited:
                self.ledger.finish(cid,status="FAILED",usage_after=after,failure="HARNESS_CONTAMINATION_TOOL_ATTEMPT:"+prohibited); raise AtomGitProviderError("prohibited AtomCode tool attempt:"+prohibited)
            if failure:
                self.ledger.finish(cid,status="FAILED",usage_after=after,failure=failure); raise AtomGitProviderError(failure)
            final="".join(text)
            if not final.strip():
                self.ledger.finish(cid,status="FAILED",usage_after=after,failure="EMPTY_CONTENT"); raise AtomGitProviderError("empty AtomCode text")
            self.ledger.finish(cid,status="COMPLETED",usage_after=after,text=final,prompt_tokens=pt,completion_tokens=ct,stop_reason=stop_reason or "unknown"); return final
        except Exception as exc:
            try:
                state=self.ledger.load(); row=state["calls"][cid-1]
                if row["status"]=="DISPATCHED": self.ledger.finish(cid,status="FAILED",usage_after=codingplan_usage(base,token),failure=f"{type(exc).__name__}:{exc}")
            except Exception: pass
            raise
        finally: stop.set()

    def invoke(self, messages: Iterable[Any]) -> Any:
        from langchain.schema import AIMessage
        instruction,prompt_sha=serialize_messages(messages); state=self.ledger.load(); call_no=len(state["calls"])+1
        if any(x["status"]=="DISPATCHED" for x in state["calls"]): raise AtomGitProviderError("unknown-after-dispatch")
        if call_no>MAX_CALLS: raise AtomGitProviderError("model-call cap exceeded")
        home,work=self._runtime(call_no); proc=None
        try:
            proc,base,token=self._daemon(home,work); return AIMessage(content=self._turn(base,token,instruction,prompt_sha))
        finally:
            if proc is not None: terminate_process(proc)
