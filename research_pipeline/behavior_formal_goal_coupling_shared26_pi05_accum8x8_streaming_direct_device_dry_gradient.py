from __future__ import annotations
import argparse, dataclasses, fcntl, functools, hashlib, json, os, shutil, subprocess, sys, tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

OBJECT_ID='SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL'
CHILD_ID='SUCC-C-BEHAVIOR2026-SHARED26-PI05-SINGLE-GPU-ACCUMULATION'
CONFIG_NAME='pi05_b1k_shared26_frozen'; EXP_NAME='shared26-seed42-run1'
CHILD_COMMIT='0d05f46ef40a6a0ff0a9b61f078835a71fececde'
PREREG_SHA='0d0a88b20f15d3a0fa2e8721da865bd5488cc39c43523a518608063c8a51a8d7'
HOST_EXIT_ADJ_SHA='7fce8b714c2b46c1561930c34f0c2e5b67987ddaa63e4868f42f752e076afad8'
DATA_ORDER_SHA='a218a76893b8e97dc849eb2d7dd63cf3a7516acbc0d0ded3822e20a0a211446d'
SYNTH_REPAIR2_AUTH_SHA='524f5e875c64b5d63f6700304a131c28c05d64056e6015bf3669340dfa58d588'
RESOURCE_SHA='b7c010d45c21a83db57567a2fe599d59bf2933c327423d1bc4cd2e265e376275'
MODEL_LOAD_SHA='fda2c02b5d8ec3e9acd491c9d197ba251e78cfc5e7d5486112c9a13bf655da0c'
LOADER_SHA='91e6e138bbe353fbf8774ea894c43cb9f6e7169b1f2dd0356456f62400babbd2'
TOKEN_RESULT_SHA='18ca3f4a11f23d58a0e14eb2ebc13838b5717f959ba788557de19439b74ce0dc'
BASE_RECEIPT_SHA='8e0f977e0641960ee3e082a19a57f52f994a817bbf981cbb2f7007ea3104a4ed'
TOKEN_SHA='8986bb4f423f07f8c7f70d0dbe3526fb2316056c17bae71b1ea975e77a168fc6'
BASE_OBJECTS=20; BASE_BYTES=12_441_721_931; EPISODES=5200
SOURCE_BATCH=64; MICRO=8; K=8; EFFECTIVE=64; ACTION_HORIZON=32; FSDP=1; SEED=42
SOURCE_WORKERS=8; WORKERS=0; TRAINABLE_ELEMENTS=3_353_433_872; GRAD_BYTES=13_413_735_488
MAX_GPU_USED=8192; MAX_GPU_UTIL=25; MAX_HOST_MEM=72*1024**3
ENV={'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1','TOKENIZERS_PARALLELISM':'false','JAX_PLATFORMS':'cuda','XLA_PYTHON_CLIENT_MEM_FRACTION':'0.9'}


def sha(path: Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda:f.read(8*1024*1024),b''): h.update(c)
    return h.hexdigest()

def require(path: Path, expected: str, label: str):
    if not path.is_file(): raise RuntimeError(f'{label} missing: {path}')
    got=sha(path)
    if got!=expected: raise RuntimeError(f'{label} SHA drift: {got}/{expected}')

def write_receipt(path: Path, obj: dict):
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8'); os.replace(tmp,path)

def copy_asset(src: Path,dst: Path,expected: str):
    require(src,expected,'tokenizer source'); dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists(): require(dst,expected,'cached tokenizer'); return
    fd,n=tempfile.mkstemp(prefix=dst.name+'.',suffix='.tmp',dir=dst.parent); os.close(fd); t=Path(n)
    try: shutil.copyfile(src,t); require(t,expected,'copied tokenizer'); os.replace(t,dst)
    finally:
        if t.exists(): t.unlink()

@contextmanager
def lock(path: Path):
    path.parent.mkdir(parents=True,exist_ok=True); f=path.open('a+')
    try:
        fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB); f.seek(0); f.truncate(); f.write(f'pid={os.getpid()}\n'); f.flush(); os.fsync(f.fileno()); yield
    finally: fcntl.flock(f.fileno(),fcntl.LOCK_UN); f.close()

def gpu():
    lines=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().splitlines(); out=[]
    for line in lines:
        i,n,t,u,z=[x.strip() for x in line.split(',',4)]; out.append({'index':int(i),'name':n,'memory_total_mib':int(t),'memory_used_mib':int(u),'utilization_gpu_percent':int(z)})
    return {'gpus':out}

def jmem(device):
    try: d=device.memory_stats()
    except Exception: return None
    return None if d is None else {str(k):v for k,v in d.items() if isinstance(v,(int,float,str,bool)) or v is None}

def resource_scope():
    rows=Path('/proc/self/cgroup').read_text().splitlines(); ids=[r.split(':',2)[2] for r in rows if r.startswith('0::')]
    if len(ids)!=1: raise RuntimeError(f'bad cgroup: {ids}')
    cg=Path('/sys/fs/cgroup')/ids[0].lstrip('/'); mm=(cg/'memory.max').read_text().strip(); sm=(cg/'memory.swap.max').read_text().strip()
    if mm=='max' or int(mm)>MAX_HOST_MEM or sm!='0': raise RuntimeError(f'bad resource scope memory={mm} swap={sm}')
    aff=set(os.sched_getaffinity(0))
    if aff!=set(range(64)): raise RuntimeError(f'CPU affinity drift: {sorted(aff)}')
    return {'cgroup':str(cg),'memory_max_bytes':int(mm),'memory_swap_max_bytes':0,'cpu_affinity':'0-63'}

def validate_base(receipt: Path, root: Path):
    require(receipt,BASE_RECEIPT_SHA,'base receipt'); d=json.loads(receipt.read_text()); count=total=0
    if d.get('status')!='PI05_BASE_TRANSPORT_REPAIR1_COMPLETE': raise RuntimeError('base receipt not complete')
    for r in d['objects']:
        p=root/r['relative_path']
        if not p.is_file() or p.stat().st_size!=int(r['size']) or sha(p)!=r['local_sha256']: raise RuntimeError(f"base object drift: {r['relative_path']}")
        count+=1; total+=int(r['size'])
    if count!=BASE_OBJECTS or total!=BASE_BYTES: raise RuntimeError(f'base total drift {count}/{total}')
    return count,total

def main():
    ap=argparse.ArgumentParser()
    for name in ['authority','preregistration','host_exit_adjudication','data_order_qualification','resource_admission','model_load_result','direct_device_model_load_result','dataloader_smoke','tokenizer_result','base_receipt','openpi_child_root','params_root','tokenizer_source','openpi_data_home','receipt']:
        ap.add_argument('--'+name.replace('_','-'),type=Path,required=True)
    a=ap.parse_args(); P={n:getattr(a,n).resolve() for n in vars(a)}; R=P['receipt']
    if R.exists(): raise RuntimeError(f'exactly-once streaming accum8x8 repair receipt exists: {R}')
    auth=json.loads(P['authority'].read_text())
    if auth.get('status')!='AUTHORIZED_PI05_STREAMING_ACCUM8X8_DIRECT_DEVICE_NO_UPDATE_DRY_GRADIENT_REPAIR1' or auth.get('object_id')!=OBJECT_ID or auth.get('child_id')!=CHILD_ID: raise RuntimeError('authority drift')
    if auth.get('runner_sha256')!=sha(Path(__file__).resolve()): raise RuntimeError('runner SHA binding drift')
    consumed=auth.get('consumed_attempt1') or {}; repo_root=P['authority'].parent.parent
    require((repo_root/consumed.get('result_path','')).resolve(),consumed.get('result_sha256',''),'consumed attempt1 result')
    require((repo_root/consumed.get('adjudication_path','')).resolve(),consumed.get('adjudication_sha256',''),'consumed attempt1 adjudication')
    require(P['preregistration'],PREREG_SHA,'prereg'); require(P['host_exit_adjudication'],HOST_EXIT_ADJ_SHA,'8x8 host-exit adjudication'); require(P['data_order_qualification'],DATA_ORDER_SHA,'data order')
    require(P['resource_admission'],RESOURCE_SHA,'resource admission'); require(P['model_load_result'],MODEL_LOAD_SHA,'original model load'); require(P['dataloader_smoke'],LOADER_SHA,'loader smoke'); require(P['tokenizer_result'],TOKEN_RESULT_SHA,'tokenizer result'); require(P['tokenizer_source'],TOKEN_SHA,'tokenizer')
    direct_binding=auth.get('direct_device_model_load_result') or {}; require(P['direct_device_model_load_result'],direct_binding.get('sha256',''),'portable direct-device model-load result')
    if json.loads(P['direct_device_model_load_result'].read_text()).get('status')!='PI05_PORTABLE_DIRECT_DEVICE_NO_UPDATE_MODEL_LOAD_PASS': raise RuntimeError('portable direct-device model-load result not PASS')
    synth_binding=auth.get('synthetic_fused_gate') or {}
    synth_path=(repo_root/synth_binding.get('path','')).resolve()
    require(synth_path,synth_binding.get('sha256',''),'synthetic fused 8x8 result')
    synth=json.loads(synth_path.read_text())
    if synth.get('status')!='PI05_SYNTHETIC_FUSED_ACCUM8X8_DIRECT_DEVICE_REPAIR2_PASS' or synth.get('micro_gradients_completed')!=8 or not synth.get('accumulated_gradient_complete'):
        raise RuntimeError('synthetic fused 8x8 repair2 gate not PASS')
    if synth.get('authority_sha256')!=SYNTH_REPAIR2_AUTH_SHA:
        raise RuntimeError('synthetic fused 8x8 repair2 authority drift')
    if any(synth.get(k) not in (False,None) for k in ['dataset_accessed','optimizer_update','parameter_update','checkpoint_written','scientific_training_started','formal_training_authorized']):
        raise RuntimeError('synthetic fused 8x8 crossed forbidden boundary')
    pre=json.loads(P['preregistration'].read_text()); first=pre['microbatch_resource_ladder'][1]
    if first!={'priority':2,'physical_micro_batch':8,'accumulation_steps':8,'effective_batch':64}: raise RuntimeError(f'ladder drift {first}')
    order=json.loads(P['data_order_qualification'].read_text())
    if order.get('status')!='PI05_ACCUM_8X8_DATA_ORDER_QUALIFICATION_PASS' or not order.get('sampler_groups_exactly_equal'): raise RuntimeError('data-order gate not PASS')
    for k,v in ENV.items():
        if os.environ.get(k)!=v: raise RuntimeError(f'env drift {k}={os.environ.get(k)!r}/{v!r}')
    if os.environ.get('HF_HUB_OFFLINE')!='1' or os.environ.get('TRANSFORMERS_OFFLINE')!='1': raise RuntimeError('offline flags missing')
    if Path(os.environ.get('OPENPI_DATA_HOME','')).resolve()!=P['openpi_data_home']: raise RuntimeError('OPENPI_DATA_HOME drift')
    scope=resource_scope(); child=subprocess.check_output(['git','-C',str(P['openpi_child_root']),'rev-parse','HEAD'],text=True).strip()
    if child!=CHILD_COMMIT: raise RuntimeError(f'child commit drift {child}')
    bc,bb=validate_base(P['base_receipt'],P['params_root']); g0=gpu()
    if len(g0['gpus'])!=1 or 'A100' not in g0['gpus'][0]['name'] or g0['gpus'][0]['memory_total_mib']<80000: raise RuntimeError(f'GPU topology drift {g0}')
    if g0['gpus'][0]['memory_used_mib']>MAX_GPU_USED or g0['gpus'][0]['utilization_gpu_percent']>MAX_GPU_UTIL: raise RuntimeError(f'GPU busy; attempt not consumed {g0}')
    copy_asset(P['tokenizer_source'],P['openpi_data_home']/ 'big_vision'/'paligemma_tokenizer.model',TOKEN_SHA)
    ck=P['openpi_child_root']/'outputs'/'checkpoints'/CONFIG_NAME/EXP_NAME
    if ck.exists(): raise RuntimeError(f'formal checkpoint already exists {ck}')
    initial={'schema_version':'behavior-formal-goal-coupling-shared26-pi05-streaming-accum8x8-direct-device-dry-gradient-result-v1','object_id':OBJECT_ID,'child_id':CHILD_ID,'generated_at':datetime.now(timezone.utc).isoformat(),'status':'PI05_STREAMING_ACCUM8X8_DIRECT_DEVICE_NO_UPDATE_DRY_GRADIENT_STARTED','candidate_priority':2,'physical_micro_batch':MICRO,'accumulation_steps':K,'effective_batch':EFFECTIVE,'attempt_count_under_candidate_authority':1,'attempt_is_exactly_once':True,'authority_sha256':sha(P['authority']),'preregistration_sha256':PREREG_SHA,'host_exit_adjudication_sha256':HOST_EXIT_ADJ_SHA,'data_order_qualification_sha256':DATA_ORDER_SHA,'openpi_child_commit':child,'base_object_count_rehashed':bc,'base_bytes_rehashed':bb,'resource_scope':scope,'gpu_before':g0,'micro_gradients_completed':0,'accumulated_gradient_complete':False,'loss_value_retained_or_reported':False,'gradient_numerical_values_read':False,'optimizer_update':False,'parameter_update':False,'checkpoint_written':False,'scientific_training_started':False,'policy_rollouts_started':False,'policy_outcomes_read':False,'formal_training_authorized':False}
    with lock(Path('/data/wyt/.formal-goal-pi05-streaming-accum8x8-direct-device-dry-gradient-repair1.lock')):
        write_receipt(R,initial); status='PI05_STREAMING_ACCUM8X8_DIRECT_DEVICE_NO_UPDATE_DRY_GRADIENT_HOLD'; err=None; batch_ready=False; state_ready=False; done=0; acc=None; leaf_count=None; elem_count=None; gpu_state=None; mem_state=None; gpu_micro=[]; mem_micro=[]
        try:
            os.chdir(P['openpi_child_root']); sys.path.insert(0,str(P['openpi_child_root'])); sys.path.insert(0,str(P['openpi_child_root']/ 'src'))
            import flax.nnx as nnx, jax, jax.numpy as jnp
            import openpi.models.model as model_lib
            import openpi.shared.array_typing as at
            import openpi.training.config as config_lib, openpi.training.data_loader as data_loader, openpi.training.sharding as sharding, openpi.training.weight_loaders as weight_loaders
            from scripts.b1k import train_b1k

            class DirectDeviceCheckpointWeightLoader:
                def __init__(self, params_path: str): self.params_path=params_path
                def load(self, params):
                    loaded=model_lib.restore_params(self.params_path,restore_type=jax.Array)
                    leaves=jax.tree.leaves(loaded)
                    if not leaves or not all(isinstance(x,jax.Array) for x in leaves): raise RuntimeError('direct-device restore returned non-jax.Array leaves')
                    return weight_loaders._merge_params(loaded,params,missing_regex='.*lora.*')
            devs=jax.devices()
            if len(devs)!=1 or devs[0].platform!='gpu': raise RuntimeError(f'expected one CUDA device, got {devs}')
            dev=devs[0]; src=config_lib.get_config(CONFIG_NAME)
            if src.batch_size!=SOURCE_BATCH or src.num_workers!=SOURCE_WORKERS: raise RuntimeError(f'source batch/workers drift {src.batch_size}/{src.num_workers}')
            cfg=dataclasses.replace(src,exp_name=EXP_NAME,weight_loader=DirectDeviceCheckpointWeightLoader(str(P['params_root'])),batch_size=MICRO,num_workers=WORKERS,wandb_enabled=False,resume=False,overwrite=True)
            eps=list(cfg.data.base_config.dataset_kwargs.get('episodes',[]))
            if cfg.seed!=SEED or cfg.model.action_horizon!=ACTION_HORIZON or cfg.fsdp_devices!=FSDP or cfg.num_train_steps!=50000 or len(eps)!=EPISODES or len(set(eps))!=EPISODES: raise RuntimeError('scientific config drift')
            mesh=sharding.make_mesh(cfg.fsdp_devices); ds=jax.sharding.NamedSharding(mesh,jax.sharding.PartitionSpec(sharding.DATA_AXIS)); rs=jax.sharding.NamedSharding(mesh,jax.sharding.PartitionSpec())
            # Resource-only lifetime repair: restore the direct-device step-0 state before
            # materializing the first decoded video/tokenizer microbatch.  The sampler uses
            # its own frozen torch.Generator(seed=42), so this reordering cannot change data
            # order or any scientific variable; it only avoids overlapping checkpoint-restore
            # host-memory peak with the 7+ GiB LeRobot first-batch path observed on host 69.
            rng=jax.random.key(cfg.seed); train_rng,init_rng=jax.random.split(rng); state,state_shard=train_b1k.init_train_state(cfg,init_rng,mesh,resume=False); jax.block_until_ready(state)
            if int(jax.device_get(state.step))!=0: raise RuntimeError('state step drift')
            state_ready=True; gpu_state=gpu(); mem_state=jmem(dev)
            loader=data_loader.create_b1k_data_loader(cfg,sharding=ds,shuffle=True,num_batches=K,skip_norm_stats=False); loader_iter=iter(loader); first_batch=next(loader_iter)
            if first_batch[1].shape[0]!=MICRO: raise RuntimeError('first microbatch shape drift')
            batch_ready=True
            @at.typecheck
            def grad_only(cfg_arg,rng_arg:at.KeyArrayLike,state_arg,batch_arg):
                model=nnx.merge(state_arg.model_def,state_arg.params); model.train()
                @at.typecheck
                def loss_fn(m,r,o,a):
                    loss=m.compute_loss(r,o,a,train=True)
                    return jnp.mean(loss)
                obs,acts=batch_arg; diff=nnx.DiffState(0,cfg_arg.trainable_filter)
                discarded,grads=nnx.value_and_grad(loss_fn,argnums=diff)(model,rng_arg,obs,acts); del discarded
                return jax.tree.map(lambda x:x/K,grads)
            @at.typecheck
            def grad_add(cfg_arg,rng_arg:at.KeyArrayLike,state_arg,batch_arg,accum):
                g=grad_only(cfg_arg,rng_arg,state_arg,batch_arg)
                return jax.tree.map(lambda a,b:a+b,accum,g)
            pfirst=jax.jit(functools.partial(grad_only,cfg),in_shardings=(rs,state_shard,ds),out_shardings=None)
            padd=jax.jit(functools.partial(grad_add,cfg),in_shardings=(rs,state_shard,ds,None),out_shardings=None,donate_argnums=(3,))
            for i in range(K):
                batch=first_batch if i==0 else next(loader_iter)
                if batch[1].shape[0]!=MICRO: raise RuntimeError(f'microbatch {i} shape drift: {batch[1].shape}')
                prog=dict(initial); prog.update({'status':'PI05_STREAMING_ACCUM8X8_DIRECT_DEVICE_MICRO_GRADIENT_STARTED','batch_ready':True,'train_state_ready':True,'micro_gradient_index_started':i,'micro_gradients_completed':done,'gpu_after_state':gpu_state,'jax_memory_after_state':mem_state,'gpu_after_each_completed_micro':gpu_micro,'jax_memory_after_each_completed_micro':mem_micro}); write_receipt(R,prog)
                mrng=jax.random.fold_in(train_rng,i)
                acc=pfirst(mrng,state,batch) if i==0 else padd(mrng,state,batch,acc)
                jax.tree.map(lambda x:x.block_until_ready(),acc); done+=1; gpu_micro.append(gpu()); mem_micro.append(jmem(dev))
            leaves=jax.tree.leaves(acc); leaf_count=len(leaves); elem_count=int(sum(np.prod(tuple(x.shape),dtype=np.int64) for x in leaves)); byte_count=int(sum(np.prod(tuple(x.shape),dtype=np.int64)*np.dtype(x.dtype).itemsize for x in leaves))
            if elem_count!=TRAINABLE_ELEMENTS or byte_count!=GRAD_BYTES: raise RuntimeError(f'accumulator structure drift elements={elem_count} bytes={byte_count}')
            status='PI05_STREAMING_ACCUM8X8_DIRECT_DEVICE_NO_UPDATE_DRY_GRADIENT_PASS'; del acc,batch,first_batch,loader_iter,loader,state
        except Exception as exc: err=f'{type(exc).__name__}: {exc}'
        finally:
            final=dict(initial); final.update({'generated_at':datetime.now(timezone.utc).isoformat(),'status':status,'batch_ready':batch_ready,'train_state_ready':state_ready,'micro_gradients_completed':done,'accumulated_gradient_complete':status.endswith('PASS'),'accumulator_leaf_count':leaf_count,'accumulator_element_count':elem_count,'gpu_after_state':gpu_state,'jax_memory_after_state':mem_state,'gpu_after_each_completed_micro':gpu_micro,'jax_memory_after_each_completed_micro':mem_micro,'error':err,'loss_value_retained_or_reported':False,'gradient_numerical_values_read':False,'optimizer_update':False,'parameter_update':False,'checkpoint_written':False,'scientific_training_started':False,'policy_rollouts_started':False,'policy_outcomes_read':False,'formal_training_authorized':False,'next_gate':'AUTHORIZE_SINGLE_GPU_STREAMING_ACCUM8X8_DIRECT_DEVICE_FORMAL_TRAINING_IMPLEMENTATION' if status.endswith('PASS') else 'STREAMING_ACCUM8X8_FAILURE_ADJUDICATION_BEFORE_ANY_4X16_ADVANCE'}); write_receipt(R,final)
        print(json.dumps({'status':status,'micro_gradients_completed':done,'accumulator_element_count':elem_count,'error':err},sort_keys=True)); return 0 if status.endswith('PASS') else 2

if __name__=='__main__': raise SystemExit(main())
