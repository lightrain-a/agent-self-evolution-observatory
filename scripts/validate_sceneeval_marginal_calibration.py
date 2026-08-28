from __future__ import annotations

import argparse, csv, hashlib, json, platform
from pathlib import Path
import numpy as np
import scipy
from scipy.special import expit
from sceneeval_marginal_calibration_core import CHANNELS, LAMBDA_GRID, build_design, fit_scaler, outer_crossfit, specs, transform

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "generated" / "sceneeval500-prerequisite-coupling-preregistration-draft-20260828.json"
TOPOLOGY = ROOT / "generated" / "sceneeval500-logistic-normal-topology-implementation-preflight-20260828.json"
PREREG_SHA = "269412b2b0ac270de00d1cca60f4e429ca3b48aae5d62359be073a6095abc365"
TOPOLOGY_SHA = "4021b01498c5d6f18219fb1b3f34c4a77d2ed217f6dfeaba1a49cd7a83bb9f5a"
ANNOT_SHA = "d770886e249e7be04cc3e183ddd1b9e23c2aa6a7666226b5fe5da17236286ae3"
VOCAB_SHA = "9e5edf20f7d2c5d8152485ea4ef6c5d89cab4fe6eccffea4fad90594f241b39a"
SEED = 2026082811


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def synthetic_matching(rows, channel, rng):
    words=np.array([len(r["Description"].split()) for r in rows],float); load=np.array([len(specs(r[channel])) for r in rows],float)
    base=.92-.0025*np.maximum(words-35,0)-.012*np.maximum(load-4,0)
    coverage=np.clip(base+rng.normal(0,.035,len(rows)),.45,1.0)
    notmatched=rng.poisson(np.clip((1-coverage)*5,.05,3)).astype(float)
    return coverage,notmatched


def synthetic_outcomes(rows, channel, names, raw, mask, coverage, seed):
    rng=np.random.default_rng(seed); base=np.array([len(specs(r[channel])) for r in rows],int); n=np.zeros(len(rows))
    for i,c in enumerate(base):
        if c: n[i]=max(1,int(rng.binomial(c,float(coverage[i]))))
    X=transform(raw,fit_scaler(raw,np.arange(len(rows)),mask)); beta=np.zeros(X.shape[1]); beta[0]=-1; beta[1]=.25; beta[2]=.55
    for name,val in [("instruction_words",.22),("total_explicit_specs",.18),("matching_coverage_fraction",-.65),("not_matched_object_count",.45)]: beta[names.index(name)]=val
    comp=[i for i,nm in enumerate(names) if nm.startswith(("attr:","relation:","category:"))][:6]
    for i,val in zip(comp,(.24,-.20,.17,-.14,.11,-.09)): beta[i]=val
    p=expit(X@beta); y=np.array([rng.binomial(int(nn),float(pp)) if nn else 0 for nn,pp in zip(n,p)],float)
    return y,n


def validate_channel(rows, channel, vocab, seed):
    rng=np.random.default_rng(seed); coverage,notmatched=synthetic_matching(rows,channel,rng)
    names,raw,mask=build_design(rows,channel,coverage,notmatched,vocab); y,n=synthetic_outcomes(rows,channel,names,raw,mask,coverage,seed+100)
    folds=[outer_crossfit(rows,raw,mask,y,n,f) for f in range(5)]
    held=sum(x["heldout_ll"] for x in folds); base=sum(x["intercept_ll"] for x in folds); imp=held-base
    if imp<=10: raise SystemExit(f"{channel} synthetic marginal calibration too weak: {imp}")
    return {"channel":channel,"feature_count_including_intercept":len(names),"synthetic_eligible_scene_count":int((n>0).sum()),"heldout_loglik_improvement_over_intercept":round(imp,6),"selected_lambda_counts":{str(l):sum(x["lambda"]==l for x in folds) for l in LAMBDA_GRID},"outer_folds":[{**x,"train_crossfit_ll":round(x["train_crossfit_ll"],6),"heldout_ll":round(x["heldout_ll"],6),"intercept_ll":round(x["intercept_ll"],6)} for x in folds]}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--annotations",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    if sha(PREREG)!=PREREG_SHA or sha(TOPOLOGY)!=TOPOLOGY_SHA or sha(a.annotations)!=ANNOT_SHA: raise SystemExit("input digest drift")
    prereg=json.loads(PREREG.read_text()); vocab=prereg["same_information_metadata_block"]["composition_vocabulary"]
    if vocab["vocabulary_sha256"]!=VOCAB_SHA: raise SystemExit("vocabulary drift")
    rows=list(csv.DictReader(a.annotations.open(newline="",encoding="utf-8-sig"))); assert len(rows)==500
    channels=[validate_channel(rows,c,vocab,SEED+i*1000) for i,c in enumerate(CHANNELS)]
    artifact={"schema_version":"sceneeval-marginal-calibration-implementation-preflight-v1","status":"MARGINAL_METADATA_CALIBRATION_SYNTHETIC_PASS","preregistration_sha256":PREREG_SHA,"topology_implementation_sha256":TOPOLOGY_SHA,"annotations_sha256":ANNOT_SHA,"composition_vocabulary_sha256":VOCAB_SHA,"scientific_authority":False,"execution_authority":False,"outcome_exposure":{"sceneeval_generator_outputs_read":False,"sceneeval_matching_outputs_read":False,"sceneeval_metric_outputs_read":False,"synthetic_matching_and_outcomes_only":True},"runtime":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,"required_runtime_on_69":"/home/wyt/anaconda3/bin/python","new_packages_installed":False},"real_run_contract":{"outer_folds":"five frozen instruction-hash folds","inner_lambda_folds":"three deterministic instruction-hash folds inside each outer training set","ridge_lambda_grid":list(LAMBDA_GRID),"lambda_selection":"maximize summed inner-validation binomial log likelihood using outer-training data only; deterministic tie favors stronger regularization","training_offset_crossfit":"after lambda selection every outer-training eta is predicted by an inner model that did not fit that scene","heldout_offset":"fit one marginal model on all outer-training scenes with selected lambda and predict outer-heldout only","feature_scaling":"training-split-only; count/load/matching/composition features log1p then standardize; intercept/difficulty dummies unscaled","metadata_features":"difficulty, words, total/per-channel loads, official matching coverage/not-matched counts, frozen attribute/relation/object-category vocabulary","candidate_N2_fairness":"N2 and candidate receive identical cross-fitted eta offsets; covariance model cannot alter marginal calibration","zero_count_policy":"zero prerequisite-eligible cells stay in prerequisite summaries only"},"synthetic_validation":{"seed":SEED,"channels":channels,"acceptance_rule":"each downstream channel improves five-fold heldout binomial log likelihood over outer-training intercept by >10; every optimizer fit succeeds"},"remaining_implementation_blockers":["freeze and synthetic-test scene-level uncertainty/bootstrap plus practical-equivalence rule","run real measurement-format smoke only after legitimate HSM gated access"],"does_not_authorize":["HSM gated access","SceneEval semantic provider calls","P0","GPU","generator admission","Problem Gate","scientific PASS"],"authority":{"canonical_generator":False,"problem_gate":False,"paper_design":False,"method":False,"experiment":False,"local_validation":False,"p0":False,"provider":False,"gpu":False,"scientific":False}}
    a.output.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":artifact["status"],"channels":[{"channel":x["channel"],"features":x["feature_count_including_intercept"],"heldout_improvement":x["heldout_loglik_improvement_over_intercept"],"lambdas":x["selected_lambda_counts"]} for x in channels],"scientific_authority":False},indent=2))
if __name__=="__main__": main()
