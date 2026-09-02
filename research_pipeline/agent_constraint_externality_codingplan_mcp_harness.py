from __future__ import annotations

import json, os, shutil, stat, subprocess, sys
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import ProviderReceipt, RunnerError

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "AtomGit-qwen3.8-27b"
MODEL = "qwen3.8-27b"
PROVIDER = "ATOMGIT_CODINGPLAN_ATOMCODE_QWEN38_MCP_NATIVE_V1"
PROVIDER_URI = "atomcode://atomgit-codingplan/qwen3.8-27b/mcp-native"
CONTEXT_WINDOW = 262144
MAX_OUTPUT_TOKENS = 65536
RETRY_MAX_ATTEMPTS = 1
MAX_ROUNDS = 20
TOOL_CALL_CAP = 16


def rows(text: str) -> list[dict[str, Any]]:
    out=[]
    for line in text.splitlines():
        try: value=json.loads(line)
        except json.JSONDecodeError: continue
        if isinstance(value,dict): out.append(value)
    return out


def write_config(path: Path) -> None:
    path.write_text("\n".join([
        f'default_provider="{PROFILE}"',f'default_model="{PROFILE}"','auto_update=false',
        'lsp.enabled=false','subagent.enabled=false','tools.todo.enabled=false',
        '[provider_accounts.AtomGit]','provider="openai"','base_url="https://llm-api.atomgit.com/v1"',
        f'[models."{PROFILE}"]','account="AtomGit"',f'model="{MODEL}"',
        f'context_window={CONTEXT_WINDOW}',f'max_tokens={MAX_OUTPUT_TOKENS}',
        f'retry_max_attempts={RETRY_MAX_ATTEMPTS}','[coding]',f'max_rounds={MAX_ROUNDS}',''
    ]),encoding='utf-8')


def setup_episode(*, episode_root: Path, prepared_runtime: Path, task_id: str,
                  experiment: str, family_id: str, seed: int, apps: list[str],
                  snapshot_sha: str, instruction_sha: str, auth_source: Path) -> tuple[Path,Path,Path,Path]:
    home=episode_root/'atomhome'; work=episode_root/'atomcode-work'; home.mkdir(parents=True); work.mkdir(parents=True)
    os.chmod(home,0o700); shutil.copy2(auth_source,home/'auth.toml'); os.chmod(home/'auth.toml',stat.S_IRUSR|stat.S_IWUSR)
    state=episode_root/'mcp-state.json'; audit=episode_root/'tool-gate-audit.jsonl'; gate=episode_root/'tool-gate.py'
    gate.write_text("import json,sys\ntry:p=json.load(sys.stdin)\nexcept Exception:p={}\nn=str(p.get('tool_name',''));a=n.startswith('mcp__ace__')\nopen(%r,'a').write(json.dumps({'tool_name':n,'allowed':a})+'\\n')\nprint(json.dumps({'action':'allow'} if a else {'action':'block','reason':'ACE harness permits only mcp__ace__*'}))\n" % str(audit),encoding='utf-8')
    args=['-m','research_pipeline.agent_constraint_externality_codingplan_appworld_mcp_server','--runtime-root',str(prepared_runtime),'--task-id',task_id,'--experiment-name',experiment,'--seed',str(seed),'--tool-call-cap',str(TOOL_CALL_CAP),'--state-manifest',str(state),'--initial-snapshot-sha256',snapshot_sha,'--instruction-sha256',instruction_sha,'--family-id',family_id]
    for app in apps: args += ['--allowed-app',app]
    (home/'mcp.json').write_text(json.dumps({'mcpServers':{'ace':{'command':sys.executable,'args':args,'env':{'PYTHONPATH':str(ROOT)},'timeout_ms':30000,'trust':True}}},sort_keys=True),encoding='utf-8')
    (work/'.hooks.json').write_text(json.dumps({'hooks':{'ace-scientific-tool-gate':{'event':'pre_tool_use','matcher':'*','command':f'{sys.executable} {gate}','timeout_ms':3000}}},sort_keys=True),encoding='utf-8')
    cfg=episode_root/'atomcode-config.toml'; write_config(cfg)
    return home,work,state,audit


def run_atomcode(*, config: Path, home: Path, work: Path, prompt: str, timeout: int=900) -> subprocess.CompletedProcess[str]:
    env=dict(os.environ); env.update({'ATOMCODE_HOME':str(home),'ATOMCODE_TODO':'0','ATOMCODE_REQUEST_USER_INPUT':'0','ATOMCODE_MEMORY_TOOL':'0'})
    return subprocess.run(['atomcode','--config',str(config),'--provider',PROFILE,'--ephemeral','--no-telemetry','--output-format','jsonl','-C',str(work),'-p',prompt],text=True,capture_output=True,timeout=timeout,check=False,env=env)


def receipts(unit_key: str, event_rows: list[dict[str, Any]]) -> list[ProviderReceipt]:
    start=next((r for r in event_rows if r.get('type')=='run.started'),{})
    if str(start.get('model')) != MODEL: raise RunnerError(f'CodingPlan model drift: {start.get("model")}')
    out=[]
    for i,r in enumerate((x for x in event_rows if x.get('type')=='usage'),1):
        p=int(r.get('prompt_tokens',0)); c=int(r.get('completion_tokens',0))
        out.append(ProviderReceipt(response_id=f'atomcode-mcp-{unit_key}-{i}',requested_model=MODEL,resolved_model=MODEL,provider=PROVIDER,base_url=PROVIDER_URI,output=[],usage={'input_tokens':p,'output_tokens':c,'total_tokens':p+c,'cached_tokens':int(r.get('cached_tokens',0)),'codingplan_requests':1,'round':r.get('round'),'request_id':r.get('request_id')},capability_snapshot={'surface':'MCP_NATIVE','context_window':CONTEXT_WINDOW,'max_output_tokens':MAX_OUTPUT_TOKENS,'retry_max_attempts':RETRY_MAX_ATTEMPTS,'max_rounds':MAX_ROUNDS,'tool_call_cap':TOOL_CALL_CAP,'allowed_tool_prefix':'mcp__ace__'}))
    if not out: raise RunnerError('CodingPlan invocation produced no usage receipt.')
    return out
