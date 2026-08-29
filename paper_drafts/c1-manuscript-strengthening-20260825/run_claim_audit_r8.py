#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "source-r8"
RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-tgrp-p0-postexposure-uptake-20260829-pilot-v1")
REGISTRY = HERE / "claim-audit-r8-registry-20260829.json"
OUT = HERE / "claim-audit-r8-provenance-seal-20260829.json"

R6_PDF = HERE / "C1-stage-resolved-r6-final.pdf"
R7_PDF = HERE / "C1-stage-resolved-r7-review-repair.pdf"
R7_ZIP = HERE / "C1-stage-resolved-r7-review-repair-source.zip"
THEORY = HERE / "c1-prerequisite-diagnostic-completeness-20260828.json"
CLOSURE = HERE / "c1-tgrp-pilot-closure-20260829.json"

EXPECTED_R6 = "c71fec522756ebceed75dff8fd168f178bd7d843e5d33f992fc1f5d6b96f4d70"
EXPECTED_R7_PDF = "a5ce511a11a7781ca5374e0f54f7830454927874ca8dc6112c87e6106ab20167"
EXPECTED_R7_ZIP = "91af2cd961a0633b31e2ba38fb1e3f2abcf6db4013dd44977d7b1d2cf8fcc76e"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def all_tex() -> str:
    files = [SRC / "main.tex", *sorted((SRC / "sections").glob("*.tex"))]
    return "\n".join(p.read_text(encoding="utf-8") for p in files)


def build_payload() -> dict:
    registry = load(REGISTRY)
    theory = load(THEORY)
    closure = load(CLOSURE)
    analysis = load(RUN / "pilot-analysis.json")
    text = all_tex()
    lower = text.lower()

    checks: list[dict] = []
    def add(cid: str, ok: bool, detail: object) -> None:
        desc = next(row["description"] for row in registry["checks"] if row["id"] == cid)
        checks.append({"id": cid, "description": desc, "pass": bool(ok), "detail": detail})

    add("R8-C01", sha(R6_PDF) == EXPECTED_R6, {"sha256": sha(R6_PDF), "expected": EXPECTED_R6})
    add("R8-C02", sha(R7_PDF) == EXPECTED_R7_PDF and sha(R7_ZIP) == EXPECTED_R7_ZIP,
        {"pdf_sha256": sha(R7_PDF), "source_zip_sha256": sha(R7_ZIP)})
    add("R8-C03", SRC.is_dir() and (HERE / "source-r7").is_dir() and (SRC / "main.tex").read_bytes() == (HERE / "source-r7" / "main.tex").read_bytes(),
        {"source_r8_exists": SRC.is_dir(), "source_r7_exists": (HERE / "source-r7").is_dir(), "main_tex_same_scaffold": True})
    add("R8-C04", "bundled writer-protocol intervention" in lower and "not a pure reward-bit" in lower,
        {"bundled_writer_boundary_present": "bundled writer-protocol intervention" in lower})
    add("R8-C05", all(s in text for s in ["20/20", "4/4", "0.105", "0.0078"]), {"required": ["20/20", "4/4", "0.105", "0.0078"]})
    add("R8-C06", "125/172" in text and "availability" in lower and "not treatment-residual exposure" in lower,
        {"source_item_exposure": "125/172"})
    add("R8-C07", all(s in text for s in ["0.06944", "0.5801", "0/36"]), {"required": ["0.06944", "0.5801", "0/36"]})
    add("R8-C08", all(s in text for s in ["0.02083", "0.4289", "34/36"]), {"required": ["0.02083", "0.4289", "34/36"]})
    add("R8-C09", all(s in text for s in ["0.125", "0.2253", "6/8", "opposite signs"]), {"required": ["0.125", "0.2253", "6/8", "opposite signs"]})
    add("R8-C10", "0.15625" in text and "0.00074" in text and "capacity" in lower and "not native transport" in lower,
        {"forced_abs_delta": 0.15625, "p": 0.00074})

    tmodel = theory.get("model") or {}
    tres = theory.get("result") or {}
    uniq = tres.get("injective_subsets") or []
    add("R8-C11", tmodel.get("diagnostic_states") == 10 and tmodel.get("observed_surface_subsets") == 32 and "10-state" in lower and "32" in text,
        {"states": tmodel.get("diagnostic_states"), "subsets": tmodel.get("observed_surface_subsets")})
    add("R8-C12", uniq == [["W", "E", "U", "O", "F"]] and "unique separating basis" in lower,
        {"injective_subsets": uniq})

    sel = load(HERE / "c1-transport-guided-repair-pilot-freeze-20260828.json")
    add("R8-C13", sel["selection"]["pilot_units"] == 13 and sel["selection"]["confirmatory_holdout_units"] == 23 and closure["execution"]["confirmatory_holdout_new_calls"] == 0,
        {"pilot": sel["selection"]["pilot_units"], "holdout": sel["selection"]["confirmatory_holdout_units"], "holdout_new_calls": closure["execution"]["confirmatory_holdout_new_calls"]})
    ex = analysis["execution"]
    add("R8-C14", ex["expected_cases"] == ex["complete_cases"] == 312 and ex["failed_cases"] == 0 and ex["missing_cases"] == 0,
        {k: ex[k] for k in ["expected_cases", "complete_cases", "failed_cases", "missing_cases"]})
    add("R8-C15", not ex["model_drift_cases"] and not ex["prompt_hash_mismatch_cases"] and closure["adjudication"]["packet_invariance"] == "PASS",
        {"model_drift_cases": ex["model_drift_cases"], "prompt_hash_mismatch_cases": ex["prompt_hash_mismatch_cases"], "packet_invariance": closure["adjudication"]["packet_invariance"]})
    eff = analysis["effect_summary"]
    target_u = 0.09615384615384616
    add("R8-C16", all(abs(eff[k] - target_u) < 1e-15 for k in ["mean_U_A0", "mean_U_A1", "mean_U_A2"]),
        {k: eff[k] for k in ["mean_U_A0", "mean_U_A1", "mean_U_A2"]})
    add("R8-C17", eff["mean_D_A2_minus_A1"] == 0.0 and eff["mean_N_A2_minus_A0"] == 0.0,
        {"D": eff["mean_D_A2_minus_A1"], "N": eff["mean_N_A2_minus_A0"]})
    dvals = [row["D_A2_minus_A1"] for row in analysis["heterogeneity"]["per_state"]]
    counts = {"positive": sum(x > 0 for x in dvals), "negative": sum(x < 0 for x in dvals), "zero": sum(x == 0 for x in dvals)}
    add("R8-C18", counts == {"positive": 3, "negative": 2, "zero": 8}, counts)
    ci = eff["D_bootstrap"]["percentile_95_ci"]
    add("R8-C19", ci == [-0.11538461538461539, 0.09615384615384616], {"ci": ci})
    add("R8-C20", analysis["gate"]["pass"] is False and analysis["gate"]["thresholds_unchanged"] is True and analysis["confirmatory_full_executed"] is False and closure["status"] == "PILOT_HOLD_OR_STOP_DO_NOT_RUN_CURRENT_CONFIRMATORY",
        {"gate_pass": analysis["gate"]["pass"], "thresholds_unchanged": analysis["gate"]["thresholds_unchanged"], "confirmatory_full_executed": analysis["confirmatory_full_executed"]})

    add("R8-C21", "negative diagnosis-guided repair pilot" in lower and "falsified repair realization" not in lower and "falsifies only" not in lower,
        {"negative_pilot_language": "negative diagnosis-guided repair pilot" in lower, "forbidden_confirmatory_falsification_absent": "falsified repair realization" not in lower and "falsifies only" not in lower})
    add("R8-C22", "diagnostic-completeness result remain intact" in lower and "localization" in lower and "does not identify what intervention will repair" in lower,
        {"separation_present": True})
    add("R8-C23", "not supported as an actionable repair" in lower and "repair efficacy" in lower,
        {"effective_repair_not_claimed": True})
    add("R8-C24", "retrieval is not use" in lower and "not our novelty" in lower and "new memory-utilization method" in lower,
        {"novelty_boundary_present": True})
    add("R8-C25", "treatment" in lower and "delivery" in lower and "not internal cognitive compliance" in lower,
        {"delivery_vs_compliance_boundary": "treatment/delivery + not internal cognitive compliance"})
    add("R8-C26", all(s in lower for s in ["state divergence is not behavioral authority", "availability is not use", "diagnosis is not repair"]),
        {"conclusion_boundary": True})

    by_id = {row["id"]: row for row in checks}
    expected_ids = [row["id"] for row in registry["checks"]]
    if list(by_id) != expected_ids:
        raise RuntimeError("R8 claim audit check order/identity drift")
    passed = sum(row["pass"] for row in checks)
    return {
        "schema_version": "1.0",
        "artifact_kind": "C1_R8_CLAIM_AUDIT",
        "paper_id": registry["paper_id"],
        "revision": "R8",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "summary": {"claims_total": len(checks), "claims_passed": passed, "claims_failed": len(checks) - passed},
        "checks": checks,
        "authority": {"scientific_claim_expansion": False, "confirmatory_full": False, "new_repair_experiment": False, "submission": False}
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    payload = build_payload()
    if args.check:
        if not OUT.is_file():
            print(json.dumps({"status": "REPLAY_FAIL", "reason": "missing saved audit"}, indent=2))
            return 2
        saved = load(OUT)
        ok = saved == payload and payload["status"] == "PASS"
        print(json.dumps({"status": "REPLAY_PASS" if ok else "REPLAY_FAIL", "summary": payload["summary"]}, indent=2))
        return 0 if ok else 1
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"]}, indent=2))
    return 0 if payload["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
