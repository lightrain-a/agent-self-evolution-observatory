from __future__ import annotations

import argparse
import base64
import contextlib
import csv
import hashlib
import io
import json
import math
import os
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
CANDIDATE_ID = "SHADOW-P22-C01"
CONTRACT_SHA256 = "88f6a753098a62df54cc7879ce3f43df8a6ac6b7565d75bfb12e6c2cd9c7fad2"
HARNESS_PLAN_SHA256 = "805fb80863b2bcd0d68448c0b727b7d74e0419e596afd3cb509587bf3fa5956f"
MEMEVOLVE_COMMIT = "6035d5659d7a092dbfa6a87b1a32a3cee652ba54"
XBENCH_COMMIT = "17c562192cc7e62215bfb98b65e9f8806fb95504"
DATASET_RELATIVE_PATH = Path("data/DeepSearch-2505.csv")
DATASET_SHA256 = "10bdb81321e3d919c052c2c9a7095868d8bc9036f719fb25d9223043aa28c118"
MEMORY_IDS = ("64","61","99","2","45","94","80","6","79","95","70","65","32","24","15","9","77","54","20","63","47","44","41","75","76","51","22","35","85","42")
CAL_IDS = ("87", "84")
EVAL_IDS = ("40", "25")
K_VALUES: tuple[int | str, ...] = (1, 3, 5, 10, 20, "all")
POOL_SIZE = 30
EMBEDDING_WEIGHT_SHA256 = "53aa51172d142c89d9012cce15ae4d6cc0ca6895895114379cacb4fab128d9db"
FEATURES = ("k","similarity_mean","similarity_min","similarity_max","similarity_q25","similarity_q50","similarity_q75","similarity_slope","task_embedding_projection_0","task_embedding_projection_1")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _decrypt(value: str, key: str) -> str:
    raw = base64.b64decode(value)
    kb = key.encode()
    return bytes(b ^ kb[i % len(kb)] for i, b in enumerate(raw)).decode()


def load_rows(path: Path) -> dict[str, dict[str, str]]:
    out = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            task_id, key = str(row["id"]), str(row["canary"])
            out[task_id] = {
                "id": task_id,
                "prompt": _decrypt(row["prompt"], key),
                "answer": _decrypt(row["answer"], key),
                "reference_steps": _decrypt(row["reference_steps"], key),
            }
    return out


def _commit(path: Path) -> str:
    return subprocess.run(["git","-C",str(path),"rev-parse","HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def verify_substrates(memevolve_root: Path, xbench_root: Path) -> dict[str, Any]:
    dataset = xbench_root / DATASET_RELATIVE_PATH
    observed = {
        "memevolve_commit": _commit(memevolve_root),
        "xbench_commit": _commit(xbench_root),
        "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "dataset_rows": len(load_rows(dataset)),
    }
    checks = {
        "memevolve_commit": observed["memevolve_commit"] == MEMEVOLVE_COMMIT,
        "xbench_commit": observed["xbench_commit"] == XBENCH_COMMIT,
        "dataset_sha256": observed["dataset_sha256"] == DATASET_SHA256,
        "dataset_rows": observed["dataset_rows"] == 100,
    }
    return {"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"observed":observed,"scientific_authority":False}


_ASCII = re.compile(r"[A-Za-z0-9_]+")
_CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]+")


def tokens(text: str) -> list[str]:
    out = [x.lower() for x in _ASCII.findall(text or "")]
    for seq in _CJK.findall(text or ""):
        chars = list(seq)
        out.extend(chars)
        out.extend(chars[i] + chars[i+1] for i in range(len(chars)-1))
    return out


def build_pool(rows: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    pool = []
    for task_id in MEMORY_IDS:
        content = rows[task_id]["reference_steps"].strip()
        if not content:
            raise ValueError(f"empty memory artifact: {task_id}")
        pool.append({"memory_id":f"P22-MEM-{task_id}","source_task_id":task_id,"content":content,"content_sha256":hashlib.sha256(content.encode()).hexdigest()})
    return pool


def bm25_rank(query: str, pool: list[dict[str, str]]) -> list[dict[str, Any]]:
    docs = [tokens(x["content"]) for x in pool]
    tfs = [Counter(x) for x in docs]
    lengths = [len(x) for x in docs]
    avgdl = sum(lengths) / max(len(lengths), 1)
    df: Counter[str] = Counter()
    for doc in docs: df.update(set(doc))
    q = Counter(tokens(query))
    ranking = []
    for i, item in enumerate(pool):
        score = 0.0
        for term, qf in q.items():
            freq = tfs[i].get(term, 0)
            if not freq: continue
            idf = math.log(1.0 + (len(pool)-df[term]+0.5)/(df[term]+0.5))
            denom = freq + 1.5*(0.25 + 0.75*lengths[i]/max(avgdl,1.0))
            score += qf * idf * freq*2.5/denom
        ranking.append({"memory_id":item["memory_id"],"source_task_id":item["source_task_id"],"content_sha256":item["content_sha256"],"score":float(score)})
    return sorted(ranking, key=lambda x:(-x["score"],x["memory_id"]))


def _k(value: int | str) -> int:
    return POOL_SIZE if value == "all" else int(value)


def _quantile(values: list[float], q: float) -> float:
    values = sorted(values)
    pos = q*(len(values)-1)
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi: return values[lo]
    return values[lo]*(hi-pos) + values[hi]*(pos-lo)


def task_embedding_projections(rows: dict[str, dict[str, str]], model_path: Path) -> dict[str, tuple[float, float]]:
    weight = model_path / "model.safetensors"
    if not weight.is_file() or hashlib.sha256(weight.read_bytes()).hexdigest() != EMBEDDING_WEIGHT_SHA256:
        raise ValueError("frozen task-embedding model weight mismatch")
    task_ids = (*CAL_IDS, *EVAL_IDS)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(str(model_path), local_files_only=True)
        vectors = model.encode([rows[task_id]["prompt"] for task_id in task_ids], normalize_embeddings=True)
    return {task_id: (float(vector[0]), float(vector[1])) for task_id, vector in zip(task_ids, vectors)}


def feature_row(task_id: str, kval: int | str, ranking: list[dict[str, Any]], projection: tuple[float, float]) -> dict[str, Any]:
    k = _k(kval)
    scores = [float(x["score"]) for x in ranking[:k]]
    slope = 0.0 if len(scores)==1 else (scores[0]-scores[-1])/(len(scores)-1)
    return {"task_id":task_id,"k":kval,"k_int":k,"selected_memory_ids":[x["memory_id"] for x in ranking[:k]],"features":{
        "k":k/POOL_SIZE,"similarity_mean":sum(scores)/len(scores),"similarity_min":min(scores),"similarity_max":max(scores),
        "similarity_q25":_quantile(scores,.25),"similarity_q50":_quantile(scores,.5),"similarity_q75":_quantile(scores,.75),
        "similarity_slope":slope,"task_embedding_projection_0":projection[0],"task_embedding_projection_1":projection[1]}}


def build_offline_probe(memevolve_root: Path, xbench_root: Path, embedding_model_path: Path) -> dict[str, Any]:
    substrate = verify_substrates(memevolve_root, xbench_root)
    rows = load_rows(xbench_root / DATASET_RELATIVE_PATH)
    split = set(MEMORY_IDS)|set(CAL_IDS)|set(EVAL_IDS)
    split_checks = {"pool_30":len(MEMORY_IDS)==30,"cal_2":len(CAL_IDS)==2,"eval_2":len(EVAL_IDS)==2,"disjoint":len(split)==34,"ids_exist":all(x in rows for x in split)}
    pool = build_pool(rows)
    projections = task_embedding_projections(rows, embedding_model_path)
    feature_rows, rankings = [], {}
    for task_id in (*CAL_IDS,*EVAL_IDS):
        ranking = bm25_rank(rows[task_id]["prompt"], pool)
        rankings[task_id] = ranking
        feature_rows.extend(feature_row(task_id,k,ranking,projections[task_id]) for k in K_VALUES)
    upper = 24*(8+1)+4
    core = {"schema_version":SCHEMA_VERSION,"candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"harness_plan_sha256":HARNESS_PLAN_SHA256,
        "substrate":substrate,"split":{"memory_source_task_ids":list(MEMORY_IDS),"calibration_task_ids":list(CAL_IDS),"evaluation_task_ids":list(EVAL_IDS),"checks":split_checks},
        "memory_pool":[{k:v for k,v in x.items() if k!="content"} for x in pool],"retrieval":{"scorer":"deterministic-bm25-v1","k_values":list(K_VALUES),"rankings":rankings},
        "task_embedding":{"model":"sentence-transformers/all-MiniLM-L6-v2","model_weight_sha256":EMBEDDING_WEIGHT_SHA256,"projection":"first-two-normalized-embedding-coordinates-v1","values":{k:list(v) for k,v in projections.items()}},
        "baseline_features":feature_rows,"budget":{"qualified_units":24,"hard_upper_bound_model_calls":upper,"contract_max_model_calls":256,"headroom":256-upper},
        "outcome_fields_present":False,"scientific_authority":False}
    core["offline_probe_sha256"] = sha_json(core)
    core["status"] = "P22_OFFLINE_HARNESS_PROBE_PASS" if substrate["status"]=="PASS" and all(split_checks.values()) and upper<=256 else "P22_OFFLINE_HARNESS_PROBE_FAIL"
    return core


def runtime_probe(python_bin: Path, memevolve_root: Path, xbench_root: Path, env: dict[str,str] | None = None) -> dict[str, Any]:
    env = dict(os.environ if env is None else env)
    flash = memevolve_root / "Flash-Searcher-main"
    link = flash / "xbench-evals-main"
    missing = [k for k in ("OPENAI_API_KEY","SERPER_API_KEY") if not env.get(k)]
    provider = (env.get("WEB_ACCESS_PROVIDER") or "jina").lower()
    if provider == "jina" and not env.get("JINA_API_KEY"): missing.append("JINA_API_KEY")
    cmd = f"import sys;sys.path.insert(0,{str(flash)!r});import base_agent,run_flash_searcher_mm_xbench;print('OK')"
    proc = subprocess.run([str(python_bin),"-c",cmd], cwd=str(flash), capture_output=True, text=True)
    checks = {"python_exists":python_bin.is_file(),"xbench_link":link.exists() and link.resolve()==xbench_root.resolve(),"runner_import":proc.returncode==0,"credentials":not missing}
    return {"status":"PASS" if all(checks.values()) else "BLOCKED_RUNTIME_SUPPORT","checks":checks,"missing_credential_keys":sorted(set(missing)),"web_access_provider":provider,"import_stderr_tail":proc.stderr[-800:],"scientific_authority":False,"belief_authority":False}


def _vector(row: dict[str, Any]) -> list[float]:
    f = row["features"]
    return [1.0] + [float(f[name]) for name in FEATURES]


def _solve(a: list[list[float]], b: list[float]) -> list[float]:
    n=len(b); m=[a[i][:]+[b[i]] for i in range(n)]
    for c in range(n):
        p=max(range(c,n),key=lambda r:abs(m[r][c])); m[c],m[p]=m[p],m[c]
        if abs(m[c][c])<1e-12: raise ValueError("singular ridge system")
        s=m[c][c]; m[c]=[x/s for x in m[c]]
        for r in range(n):
            if r==c: continue
            f=m[r][c]; m[r]=[m[r][j]-f*m[c][j] for j in range(n+1)]
    return [m[i][-1] for i in range(n)]


def prediction_manifest(probe: dict[str, Any], calibration: list[dict[str, Any]], ridge: float=1.0) -> dict[str, Any]:
    if probe.get("status")!="P22_OFFLINE_HARNESS_PROBE_PASS": raise ValueError("offline probe not PASS")
    outcomes={}
    for row in calibration:
        task_id=str(row.get("task_id") or "")
        if task_id not in CAL_IDS: raise ValueError("evaluation outcome cannot enter baseline fit")
        key=(task_id,_k(row.get("k")))
        if key in outcomes: raise ValueError("duplicate calibration outcome")
        if row.get("success") not in {0,1,False,True}: raise ValueError("success must be binary")
        outcomes[key]=float(bool(row["success"]))
    if len(outcomes)!=12: raise ValueError("all 12 calibration units required")
    train=[r for r in probe["baseline_features"] if r["task_id"] in CAL_IDS]
    d=len(_vector(train[0])); xtx=[[0.0]*d for _ in range(d)]; xty=[0.0]*d
    for row in train:
        x=_vector(row); y=outcomes[(row["task_id"],row["k_int"])]
        for i in range(d):
            xty[i]+=x[i]*y
            for j in range(d): xtx[i][j]+=x[i]*x[j]
    for i in range(1,d): xtx[i][i]+=ridge
    weights=_solve(xtx,xty)
    predictions=[]
    for task_id in EVAL_IDS:
        items=[]
        for row in [r for r in probe["baseline_features"] if r["task_id"]==task_id]:
            pred=max(0.0,min(1.0,sum(w*v for w,v in zip(weights,_vector(row)))))
            items.append({"k":row["k"],"k_int":row["k_int"],"predicted_success":pred})
        best=min(items,key=lambda x:(-x["predicted_success"],x["k_int"]))
        predictions.append({"task_id":task_id,"predicted_optimal_k":best["k"],"predicted_optimal_k_int":best["k_int"],"ordering":[x["k"] for x in sorted(items,key=lambda x:(-x["predicted_success"],x["k_int"]))],"scores":items})
    core={"schema_version":SCHEMA_VERSION,"status":"P22_EVALUATION_PREDICTIONS_COMMITTED","candidate_id":CANDIDATE_ID,"contract_sha256":CONTRACT_SHA256,"harness_plan_sha256":HARNESS_PLAN_SHA256,"offline_probe_sha256":probe["offline_probe_sha256"],"baseline":{"family":"ridge-value-of-information-v1","ridge":ridge,"features":list(FEATURES),"weights":weights,"fit_task_ids":list(CAL_IDS),"evaluation_outcomes_visible_during_fit":False},"evaluation_predictions":predictions,"scientific_authority":False}
    core["prediction_manifest_sha256"]=sha_json(core)
    return core


def main() -> None:
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("offline-probe"); p.add_argument("--memevolve-root",type=Path,required=True); p.add_argument("--xbench-root",type=Path,required=True); p.add_argument("--embedding-model-path",type=Path,required=True); p.add_argument("--output",type=Path)
    r=sub.add_parser("runtime-probe"); r.add_argument("--python-bin",type=Path,required=True); r.add_argument("--memevolve-root",type=Path,required=True); r.add_argument("--xbench-root",type=Path,required=True); r.add_argument("--output",type=Path)
    q=sub.add_parser("prediction-manifest"); q.add_argument("--offline-probe",type=Path,required=True); q.add_argument("--calibration-outcomes",type=Path,required=True); q.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if a.cmd=="offline-probe": out=build_offline_probe(a.memevolve_root,a.xbench_root,a.embedding_model_path)
    elif a.cmd=="runtime-probe": out=runtime_probe(a.python_bin,a.memevolve_root,a.xbench_root)
    else: out=prediction_manifest(json.loads(a.offline_probe.read_text()),json.loads(a.calibration_outcomes.read_text()))
    text=json.dumps(out,ensure_ascii=False,indent=2)+"\n"
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text,encoding="utf-8")
    print(text,end="")

if __name__=="__main__": main()
