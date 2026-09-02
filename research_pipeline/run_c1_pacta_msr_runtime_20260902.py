#!/usr/bin/env python3
"""Rootful exact-digest import and exact-base qualification for all 20 PACTA-MSR images."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json,sha256_file
from research_pipeline.run_c1_pacta_rb_qwen397_t05_images_20260901 import CACHE,image_repo

ROOT=Path(__file__).resolve().parents[1]
IMAGE_ROOT=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-images-20260902-v1')
DEFAULT=Path('/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-runtime-20260902-v1')
LAYOUT_ROOT=Path('/data/wyt/e1-stri-reasoningbank-runtime/c1-pacta-msr-oci-layouts')
SKOPEO=Path('/data/wyt/e1-stri-reasoningbank-runtime/skopeo-root/usr/bin/skopeo')
POLICY=Path('/data/wyt/e1-stri-reasoningbank-runtime/skopeo-root/etc/containers/policy.json')
ROOTFUL_HOST='unix:///var/run/docker.sock'
MANIFEST_SHA='5c788e477a342b159d3928f4a66e1cb74f44445c5bee2cbb09a57933e1dec3be'
BLOB_RECEIPT_SHA='faeb699dd6b35e51871f6a7ab7122282feaf4d70a394cfe292ba8426b10f30eb'
OFFICIAL=Path('/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026')
OFFICIAL_COMMIT='ed80611788292ea739f1effd31f16c53823b8a0d'
EXPECTED_CARRIER={
 'config':('third_party/src/minisweagent/config/extra/swebench.yaml','d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41'),
 'agent':('third_party/src/minisweagent/agents/default.py','428a78335cbfb365ba8e6622effc8959104f08e8f32068727625bcb296da756c'),
 'writer':('third_party/src/minisweagent/memory/instruction.py','08e11fbeac1ba9e20d1dafb20728be24194b56bdfea33f05f6a1220ae2cc9bae'),
 'retrieval':('third_party/src/minisweagent/memory/memory_management.py','fe71285a878920d501013ab86b58ef12c9c08071ee0e690061774d5ff5588955'),
 'runner':('third_party/src/minisweagent/run/extra/swebench.py','8365112cd2dd2f3dbd74eff611b5d166530c6ddac4b09b674ae384da96531951')}

def now()->str:return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def append(path:Path,row:dict[str,Any])->None:
 path.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(row,sort_keys=True,ensure_ascii=False)+'\n').encode()
 with path.open('ab') as h:h.write(raw);h.flush();os.fsync(h.fileno())
def run(command:list[str],timeout:int=1800)->dict[str,Any]:
 env=os.environ.copy();env['DOCKER_HOST']=ROOTFUL_HOST
 try:
  p=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout,env=env,check=False);return {'command':command,'returncode':p.returncode,'output':p.stdout}
 except subprocess.TimeoutExpired as e:
  out=e.stdout or '';out=out.decode(errors='replace') if isinstance(out,bytes) else out;return {'command':command,'returncode':124,'output':out,'timeout_seconds':timeout}
def docker_metadata()->dict[str,Any]:
 v=run(['docker','version','--format','{{json .}}'],60);i=run(['docker','info','--format','{{json .}}'],60)
 if v['returncode'] or i['returncode']:raise RuntimeError('STOP_ROOTFUL_DOCKER_UNAVAILABLE')
 p=json.loads(i['output']);o={'docker_host':ROOTFUL_HOST,'version':json.loads(v['output']),'architecture':p.get('Architecture'),'docker_root_dir':p.get('DockerRootDir'),'driver':p.get('Driver'),'security_options':p.get('SecurityOptions') or []}
 if o['docker_root_dir']!='/var/lib/docker' or any('rootless' in str(x).lower() for x in o['security_options']) or str(o['architecture']).lower() not in {'x86_64','amd64'}:raise RuntimeError('STOP_ROOTFUL_DOCKER_UNAVAILABLE')
 return o
def carrier_audit()->dict[str,Any]:
 head=subprocess.run(['git','-C',str(OFFICIAL),'rev-parse','HEAD'],text=True,capture_output=True,check=True).stdout.strip();files={}
 for k,(rel,expected) in EXPECTED_CARRIER.items():
  p=OFFICIAL/rel;actual=sha256_file(p);files[k]={'path':str(p),'sha256':actual,'expected_sha256':expected,'pass':actual==expected}
 return {'official_commit':head,'expected_commit':OFFICIAL_COMMIT,'files':files,'pass':head==OFFICIAL_COMMIT and all(x['pass'] for x in files.values())}
def frozen_rows()->list[dict[str,Any]]:
 f=load(IMAGE_ROOT/'manifest-freeze.json')
 if sha256_file(IMAGE_ROOT/'manifest-freeze.json')!=MANIFEST_SHA or f.get('status')!='MSR_20_IMAGE_MANIFESTS_FROZEN' or f.get('image_count')!=20:raise RuntimeError('STOP_MSR_MANIFEST_FREEZE_DRIFT')
 rows=f['rows']
 if len(rows)!=20 or len({x['instance_id'] for x in rows})!=20:raise RuntimeError('STOP_MSR_IMAGE_GEOMETRY_DRIFT')
 return rows

def preflight(root:Path)->dict[str,Any]:
 if root.exists():raise RuntimeError('runtime root exists; no overwrite')
 root.mkdir(parents=True);receipt=load(IMAGE_ROOT/'blob-receipt.json')
 if sha256_file(IMAGE_ROOT/'blob-receipt.json')!=BLOB_RECEIPT_SHA or not receipt.get('all_blobs_verified') or receipt.get('unique_blob_count')!=86:raise RuntimeError('STOP_MSR_BLOB_RECEIPT_DRIFT')
 carrier=carrier_audit()
 if not carrier['pass']:raise RuntimeError('STOP_CARRIER_DRIFT')
 blobs=[]
 for item in load(IMAGE_ROOT/'blob-plan.json')['rows']:
  p=CACHE/item['digest'][7:];ok=p.is_file() and p.stat().st_size==int(item['size']) and sha256_file(p)==item['digest'][7:];blobs.append({'digest':item['digest'],'size':item['size'],'path':str(p),'pass':ok})
 if not all(x['pass'] for x in blobs):raise RuntimeError('STOP_MSR_BLOB_CACHE_CORRUPTION')
 out={'schema_version':1,'created_at_utc':now(),'status':'MSR_RUNTIME_PREFLIGHT_PASS','docker':docker_metadata(),'carrier':carrier,'images':20,'blobs':86,'blob_bytes':sum(x['size'] for x in blobs),'provider_calls':0,'scientific_calls':0}
 atomic_json(root/'preflight.json',out);return out

def assemble(row:dict[str,Any])->tuple[Path,str]:
 instance=row['instance_id'];amd64=row['amd64_digest'][7:];mp=Path(row['manifest_path']);raw=mp.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=amd64:raise RuntimeError(f'manifest digest mismatch {instance}')
 m=json.loads(raw);layout=LAYOUT_ROOT/instance;bd=layout/'blobs/sha256';bd.mkdir(parents=True,exist_ok=True)
 for d in [m['config'],*m['layers']]:
  value=d['digest'][7:];source=CACHE/value;target=bd/value
  if not source.is_file() or source.stat().st_size!=int(d['size']) or sha256_file(source)!=value:raise RuntimeError(f'unverified blob {instance}:{value}')
  if not target.exists():os.link(source,target)
  elif sha256_file(target)!=value:raise RuntimeError(f'layout blob corruption {instance}:{value}')
 mt=bd/amd64
 if not mt.exists():os.link(mp,mt)
 elif sha256_file(mt)!=amd64:raise RuntimeError(f'layout manifest corruption {instance}')
 (layout/'oci-layout').write_text('{"imageLayoutVersion":"1.0.0"}\n');tag=f'msr-{amd64[:12]}';desc={'mediaType':m.get('mediaType','application/vnd.docker.distribution.manifest.v2+json'),'digest':'sha256:'+amd64,'size':len(raw),'annotations':{'org.opencontainers.image.ref.name':tag},'platform':{'architecture':'amd64','os':'linux'}};(layout/'index.json').write_text(json.dumps({'schemaVersion':2,'manifests':[desc]},indent=2)+'\n');return layout,tag

def import_one(row:dict[str,Any])->dict[str,Any]:
 instance=row['instance_id'];amd64=row['amd64_digest'][7:];repo='docker.1ms.run/'+row['repository'];digest_ref=f'{repo}@sha256:{amd64}'
 inspect=run(['docker','image','inspect',digest_ref,'--format','{{json .RepoDigests}}|{{.Architecture}}|{{.Id}}'],60)
 if inspect['returncode'] or 'sha256:'+amd64 not in inspect['output']:
  layout,tag=assemble(row);archive=LAYOUT_ROOT/f'{instance}.msr.docker-archive.tar';archive.unlink(missing_ok=True);tagged=f'{repo}:{tag}'
  a=run([str(SKOPEO),'--policy',str(POLICY),'copy','--override-arch','amd64',f'oci:{layout}:{tag}',f'docker-archive:{archive}:{tagged}'],3600)
  if a['returncode']:raise RuntimeError(f'archive failed {instance}: {a["output"][-1000:]}')
  l=run(['docker','load','-i',str(archive)],3600);archive.unlink(missing_ok=True)
  if l['returncode']:raise RuntimeError(f'load failed {instance}: {l["output"][-1000:]}')
  p=run(['docker','pull',digest_ref],1800)
  if p['returncode']:raise RuntimeError(f'digest attach failed {instance}: {p["output"][-1000:]}')
  inspect=run(['docker','image','inspect',digest_ref,'--format','{{json .RepoDigests}}|{{.Architecture}}|{{.Id}}'],60)
 passed=inspect['returncode']==0 and 'sha256:'+amd64 in inspect['output'] and 'amd64' in inspect['output']
 if not passed:raise RuntimeError(f'exact digest inspect failed {instance}: {inspect["output"][-800:]}')
 return {**{k:row[k] for k in ('role','unit_id','instance_id','base_commit','index_digest','amd64_digest')},'digest_ref':digest_ref,'image_id':inspect['output'].strip().split('|')[-1],'import_pass':True,'digest_inspect_pass':True}

def import_all(root:Path)->dict[str,Any]:
 if not (root/'preflight.json').is_file():raise RuntimeError('preflight missing')
 if (root/'import-receipt.json').exists():raise RuntimeError('import receipt exists; no overwrite')
 journal=root/'import-journal.jsonl';done={}
 if journal.exists():
  for line in journal.read_text().splitlines():
   if line.strip():o=json.loads(line);done[o['instance_id']]=o
 out=[]
 for row in frozen_rows():
  if row['instance_id'] in done:o=done[row['instance_id']]
  else:
   try:o=import_one(row)
   except Exception as e:o={**{k:row[k] for k in ('role','unit_id','instance_id','base_commit','index_digest','amd64_digest')},'import_pass':False,'digest_inspect_pass':False,'invalid_reason':f'{type(e).__name__}: {e}'}
   append(journal,o);done[row['instance_id']]=o
  out.append(o);print(json.dumps({'role':o['role'],'instance_id':o['instance_id'],'import_pass':o['import_pass']}),flush=True)
 n=sum(x['import_pass'] and x['digest_inspect_pass'] for x in out);receipt={'schema_version':1,'created_at_utc':now(),'status':'MSR_20_IMPORT_PASS' if n==20 else 'MSR_IMPORT_INCOMPLETE','docker':docker_metadata(),'rows':out,'imported':n,'total':20,'provider_calls':0,'scientific_calls':0};atomic_json(root/'import-receipt.json',receipt);return receipt

def exec_in(cid:str,cmd:str,timeout:int=120)->dict[str,Any]:return run(['docker','exec','-w','/testbed',cid,'bash','-lc',cmd],timeout)
def qualify_one(row:dict[str,Any],imp:dict[str,Any])->dict[str,Any]:
 o={**{k:row[k] for k in ('role','unit_id','instance_id','base_commit','index_digest','amd64_digest')},'digest_ref':imp.get('digest_ref',''),'image_id':imp.get('image_id',''),'import_pass':bool(imp.get('import_pass')),'digest_inspect_pass':bool(imp.get('digest_inspect_pass'))}
 if not o['import_pass']:o.update({'container_start_pass':False,'exact_base_normalization_pass':False,'invalid_reason':imp.get('invalid_reason','import failed')});return o
 name='c1-msr-'+os.urandom(6).hex();s=run(['docker','run','-d','--pull=never','--name',name,'-w','/testbed','--rm',o['digest_ref'],'sleep','30m'],180);o['container_start_pass']=s['returncode']==0
 if not o['container_start_pass']:o.update({'exact_base_normalization_pass':False,'invalid_reason':s['output'][-800:]});return o
 cid=s['output'].strip();base=row['base_commit']
 try:
  h=exec_in(cid,'git rev-parse HEAD');clean=exec_in(cid,'test -z "$(git status --porcelain)"');exists=exec_in(cid,f'git cat-file -e {base}^{{commit}}');ancestor=exec_in(cid,f'git merge-base --is-ancestor {base} HEAD');tools=exec_in(cid,'test -d /testbed && command -v bash && command -v git && command -v python');reset=exec_in(cid,f'git reset --hard {base}');post=exec_in(cid,'git rev-parse HEAD');postclean=exec_in(cid,'test -z "$(git status --porcelain)"')
  o.update({'observed_initial_head':h['output'].strip(),'initial_working_tree_clean':clean['returncode']==0,'base_commit_exists':exists['returncode']==0,'base_is_ancestor':ancestor['returncode']==0,'runtime_tools_pass':tools['returncode']==0,'reset_pass':reset['returncode']==0,'post_reset_head':post['output'].strip(),'post_reset_head_exact':post['output'].strip()==base,'post_reset_working_tree_clean':postclean['returncode']==0})
  o['exact_base_normalization_pass']=all(o[k] for k in ('import_pass','digest_inspect_pass','container_start_pass','initial_working_tree_clean','base_commit_exists','base_is_ancestor','runtime_tools_pass','reset_pass','post_reset_head_exact','post_reset_working_tree_clean'))
  if not o['exact_base_normalization_pass']:o['invalid_reason']='exact-base pre/postcondition failed'
 finally:run(['docker','rm','-f',cid],120)
 return o

def qualify(root:Path)->dict[str,Any]:
 if (root/'normalization-qualification.json').exists():raise RuntimeError('qualification exists; no overwrite')
 imports={x['instance_id']:x for x in load(root/'import-receipt.json')['rows']};journal=root/'normalization-journal.jsonl';done={}
 if journal.exists():
  for line in journal.read_text().splitlines():
   if line.strip():x=json.loads(line);done[x['instance_id']]=x
 out=[]
 for row in frozen_rows():
  x=done.get(row['instance_id'])
  if x is None:x=qualify_one(row,imports[row['instance_id']]);append(journal,x);done[row['instance_id']]=x
  out.append(x);print(json.dumps({'role':x['role'],'instance_id':x['instance_id'],'exact_base':x['exact_base_normalization_pass']}),flush=True)
 n=sum(x['exact_base_normalization_pass'] for x in out);receipt={'schema_version':1,'created_at_utc':now(),'status':'MSR_20_RUNTIME_READY' if n==20 else 'HOLD_MSR_RUNTIME_SUPPORT_INCOMPLETE','rows':out,'qualified':n,'total':20,'source_qualified':sum(x['role']=='source' and x['exact_base_normalization_pass'] for x in out),'future_qualified':sum(x['role']=='future' and x['exact_base_normalization_pass'] for x in out),'provider_calls':0,'scientific_calls':0}
 atomic_json(root/'normalization-qualification.json',receipt);return receipt

def main()->None:
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=DEFAULT);a.add_argument('--phase',choices=('preflight','import','qualify'),required=True);x=a.parse_args();result={'preflight':preflight,'import':import_all,'qualify':qualify}[x.phase](x.root);print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
