from __future__ import annotations

import hashlib
import math
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, gammaln

CHANNELS = ("ObjAttr", "OORel", "OARel")
LAMBDA_GRID = (0.1, 1.0, 10.0, 100.0)


def specs(value: str) -> list[list[str]]:
    return [[p.strip() for p in s.strip().split(",")] for s in str(value or "").split(";") if s.strip()]


def fold_id(row: dict[str, str], prefix: str, count: int) -> int:
    raw = f"{prefix}\n{row['ID']}\n{row['Description']}".encode()
    return int(hashlib.sha256(raw).hexdigest()[:8], 16) % count


def composition(row: dict[str, str]) -> dict[str, Any]:
    attrs: dict[str, int] = {}; rel = {"OORel": {}, "OARel": {}}; cats: dict[str, int] = {}
    def add(d: dict[str, int], k: str) -> None:
        if k: d[k] = d.get(k, 0) + 1
    for p in specs(row["ObjAttr"]):
        if len(p) >= 4:
            add(cats, p[2])
            for t in p[3:]: add(attrs, t)
    for p in specs(row["OORel"]):
        if len(p) >= 5:
            add(rel["OORel"], p[2])
            for ref in p[4:]: add(cats, ref.split(":", 1)[0].strip())
    for p in specs(row["OARel"]):
        if len(p) >= 4:
            add(rel["OARel"], p[2]); add(cats, p[3].split(":", 1)[0].strip())
    return {"attrs": attrs, "rel": rel, "cats": cats}


def build_design(rows: list[dict[str, str]], channel: str, coverage: np.ndarray, notmatched: np.ndarray, vocab: dict[str, Any]):
    attrs = [x["token"] for x in vocab["ObjAttr_attribute_tokens"]]
    rels = [x["token"] for x in vocab.get(f"{channel}_relationship_tokens", [])]
    cats = [x["token"] for x in vocab["downstream_object_categories"]]
    names = ["intercept", "difficulty_medium", "difficulty_hard", "instruction_words", "total_explicit_specs", "ObjAttr_spec_count", "OORel_spec_count", "OARel_spec_count", "matching_coverage_fraction", "not_matched_object_count"]
    names += ([f"attr:{x}" for x in attrs] if channel == "ObjAttr" else [f"relation:{x}" for x in rels])
    names += [f"category:{x}" for x in cats]
    X = np.zeros((len(rows), len(names))); X[:, 0] = 1.0
    comps = [composition(r) for r in rows]
    for i, r in enumerate(rows):
        counts = {c: len(specs(r[c])) for c in CHANNELS}
        vals = [1.0 if r["Difficulty"] == "medium" else 0.0, 1.0 if r["Difficulty"] == "hard" else 0.0, len(r["Description"].split()), len(specs(r["ObjCount"])) + sum(counts.values()), counts["ObjAttr"], counts["OORel"], counts["OARel"], coverage[i], notmatched[i]]
        c = comps[i]
        vals += ([c["attrs"].get(x, 0) for x in attrs] if channel == "ObjAttr" else [c["rel"][channel].get(x, 0) for x in rels])
        vals += [c["cats"].get(x, 0) for x in cats]
        X[i, 1:] = vals
    scale_mask = np.ones(X.shape[1], dtype=bool); scale_mask[:3] = False
    X[:, 3:] = np.log1p(np.maximum(X[:, 3:], 0.0))
    return names, X, scale_mask


def fit_scaler(raw: np.ndarray, idx: np.ndarray, mask: np.ndarray):
    mean = np.zeros(raw.shape[1]); scale = np.ones(raw.shape[1])
    mean[mask] = raw[idx][:, mask].mean(0); sd = raw[idx][:, mask].std(0)
    scale[mask] = np.where(sd > 1e-8, sd, 1.0)
    return mean, scale


def transform(raw: np.ndarray, scaler):
    mean, scale = scaler; return (raw - mean[None, :]) / scale[None, :]


def loglik(y: np.ndarray, n: np.ndarray, eta: np.ndarray) -> float:
    coeff = gammaln(n + 1) - gammaln(y + 1) - gammaln(n - y + 1)
    return float((coeff + y * (-np.logaddexp(0.0, -eta)) + (n - y) * (-np.logaddexp(0.0, eta))).sum())


def fit_ridge(X: np.ndarray, y: np.ndarray, n: np.ndarray, lam: float):
    pen = np.ones(X.shape[1]); pen[0] = 0.0
    rate = min(1 - 1e-5, max(1e-5, float(y.sum() / n.sum()))); init = np.zeros(X.shape[1]); init[0] = math.log(rate / (1-rate))
    def fg(b):
        eta = X @ b; p = expit(eta)
        val = -loglik(y, n, eta) + 0.5 * lam * float(np.sum(pen * b * b))
        grad = X.T @ (n * p - y) + lam * pen * b
        return val, grad
    res = minimize(lambda b: fg(b)[0], init, jac=lambda b: fg(b)[1], method="L-BFGS-B", options={"maxiter": 900, "ftol": 1e-8, "gtol": 1e-5, "maxls": 40})
    return res


def choose_lambda(rows, raw, mask, outer_train, y, n):
    scores = {lam: 0.0 for lam in LAMBDA_GRID}
    for f in range(3):
        va = np.array([i for i in outer_train if fold_id(rows[i], "sceneeval-marginal-inner-v1", 3) == f], dtype=int)
        tr = np.array([i for i in outer_train if fold_id(rows[i], "sceneeval-marginal-inner-v1", 3) != f], dtype=int)
        X = transform(raw, fit_scaler(raw, tr, mask))
        for lam in LAMBDA_GRID:
            res = fit_ridge(X[tr], y[tr], n[tr], lam)
            if not res.success: raise RuntimeError(str(res.message))
            scores[lam] += loglik(y[va], n[va], X[va] @ res.x)
    best = max(LAMBDA_GRID, key=lambda l: (scores[l], l))
    return best, scores


def outer_crossfit(rows, raw, mask, y, n, outer_fold: int):
    eligible = [i for i in range(len(rows)) if n[i] > 0]
    va = np.array([i for i in eligible if fold_id(rows[i], "sceneeval-primary-v1", 5) == outer_fold], dtype=int)
    tr = np.array([i for i in eligible if fold_id(rows[i], "sceneeval-primary-v1", 5) != outer_fold], dtype=int)
    lam, scores = choose_lambda(rows, raw, mask, tr, y, n)
    train_eta = np.full(len(rows), np.nan)
    for f in range(3):
        iv = np.array([i for i in tr if fold_id(rows[i], "sceneeval-marginal-inner-v1", 3) == f], dtype=int)
        it = np.array([i for i in tr if fold_id(rows[i], "sceneeval-marginal-inner-v1", 3) != f], dtype=int)
        X = transform(raw, fit_scaler(raw, it, mask)); res = fit_ridge(X[it], y[it], n[it], lam)
        if not res.success: raise RuntimeError(str(res.message))
        train_eta[iv] = X[iv] @ res.x
    if np.any(np.isnan(train_eta[tr])): raise RuntimeError("incomplete crossfit eta")
    X = transform(raw, fit_scaler(raw, tr, mask)); res = fit_ridge(X[tr], y[tr], n[tr], lam)
    if not res.success: raise RuntimeError(str(res.message))
    held_eta = X[va] @ res.x
    rate = min(1-1e-8, max(1e-8, float(y[tr].sum()/n[tr].sum()))); intercept = np.full(len(va), math.log(rate/(1-rate)))
    return {"fold": outer_fold, "train_n": len(tr), "heldout_n": len(va), "lambda": float(lam), "lambda_scores": {str(k): round(v,6) for k,v in scores.items()}, "train_crossfit_ll": loglik(y[tr], n[tr], train_eta[tr]), "heldout_ll": loglik(y[va], n[va], held_eta), "intercept_ll": loglik(y[va], n[va], intercept), "iterations": int(res.nit)}
