#!/usr/bin/env python3
"""Loopback-only chat server for the B1 R87 Qwen2.5-32B strong-scale check.

No benchmark logic or retrieval is implemented here.  The server intentionally
reuses the frozen LocalQwenProvider generation path (float16, apply_chat_template,
greedy at temperature=0) and exposes only the chat route required by the frozen
R87 actor.  Model root and ID are frozen constants after R80/R86.
"""
from __future__ import annotations
import argparse,hashlib,json,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from typing import Any
from failure_memory_memrl_local_runtime_r43 import LocalQwenProvider

LLM_MODEL_ID="B1-Qwen2.5-32B-Instruct-r87"
LLM_ROOT=Path("/data/wyt/models/Qwen2.5-32B-Instruct-c53f76495664")

def _flatten_content(content:Any)->str:
 if isinstance(content,str):return content
 if isinstance(content,list):
  parts=[]
  for item in content:
   if isinstance(item,dict) and item.get("type")=="text":parts.append(str(item.get("text") or ""))
   elif isinstance(item,str):parts.append(item)
  return "\n".join(parts)
 return str(content or "")

class Runtime:
 def __init__(self)->None:self.llm=LocalQwenProvider(model_root=LLM_ROOT,device="cuda:0",max_new_tokens=512)
 def chat(self,payload:dict[str,Any])->dict[str,Any]:
  model=str(payload.get("model") or LLM_MODEL_ID)
  if model!=LLM_MODEL_ID:raise ValueError(f"unsupported chat model:{model}")
  messages=[{"role":str(row.get("role") or "user"),"content":_flatten_content(row.get("content"))} for row in (payload.get("messages") or []) if isinstance(row,dict)]
  if not messages:raise ValueError("messages required")
  before=self.llm.get_token_usage();text=self.llm.generate(messages,temperature=float(payload.get("temperature") or 0.0),max_tokens=int(payload.get("max_tokens") or payload.get("max_completion_tokens") or 512));after=self.llm.get_token_usage()
  pt=int(after["prompt_tokens"]-before["prompt_tokens"]);ct=int(after["completion_tokens"]-before["completion_tokens"]);request_hash=hashlib.sha256(json.dumps(payload,sort_keys=True,default=str).encode()).hexdigest()[:20]
  return {"id":f"chatcmpl-b1-r87-{request_hash}","object":"chat.completion","created":int(time.time()),"model":LLM_MODEL_ID,"choices":[{"index":0,"message":{"role":"assistant","content":text},"finish_reason":"stop"}],"usage":{"prompt_tokens":pt,"completion_tokens":ct,"total_tokens":pt+ct}}

class Handler(BaseHTTPRequestHandler):
 runtime:Runtime;server_version="B1R87StrongScale/1.0"
 def log_message(self,fmt:str,*args:Any)->None:return
 def _json(self,code:int,payload:dict[str,Any])->None:
  body=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode();self.send_response(code);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
 def do_GET(self)->None:
  path=self.path.rstrip("/")
  if path in {"/v1/models","/models"}:self._json(200,{"object":"list","data":[{"id":LLM_MODEL_ID,"object":"model","owned_by":"local-b1-r87"}]});return
  if path in {"/health","/v1/health"}:self._json(200,{"status":"ok","llm":LLM_MODEL_ID});return
  self._json(404,{"error":{"message":"not found","type":"not_found"}})
 def do_POST(self)->None:
  try:
   length=int(self.headers.get("Content-Length") or 0);payload=json.loads(self.rfile.read(length).decode("utf-8"))
   if not isinstance(payload,dict):raise ValueError("JSON object required")
   path=self.path.rstrip("/")
   if path in {"/v1/chat/completions","/chat/completions"}:self._json(200,self.runtime.chat(payload));return
   self._json(404,{"error":{"message":"not found","type":"not_found"}})
  except Exception as exc:self._json(400,{"error":{"message":str(exc),"type":type(exc).__name__}})

def main()->None:
 p=argparse.ArgumentParser();p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=18145);a=p.parse_args()
 if a.host not in {"127.0.0.1","localhost"}:raise SystemExit("R87 server is loopback-only")
 Handler.runtime=Runtime();server=ThreadingHTTPServer((a.host,a.port),Handler);print(json.dumps({"status":"READY","host":a.host,"port":a.port,"llm":LLM_MODEL_ID},sort_keys=True),flush=True);server.serve_forever()
if __name__=="__main__":main()
