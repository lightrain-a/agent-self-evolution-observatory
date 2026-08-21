import json

from research_pipeline.discovery_engine_paper_yield_benchmark import ENGINE_SPECS, GATES, run_benchmark
from research_pipeline.discovery_engine_paper_yield_adjudication import compile_adjudication
from research_pipeline.discovery_engine_adaptive_policy import compile_policy


def _pool():
    return {
        "records": [
            {
                "ref": "arXiv:TEST1",
                "title": "Persistent Agent Boundary",
                "publication_date": "2026-08-20",
                "empirical_facts": [{"text": "Long-horizon performance differs despite matched current success."}],
                "typed_evidence": {
                    "operational_assumptions": [],
                    "measured_failures": [{"text": "Static evaluation misses a later regression."}],
                    "boundary_observations": [{"text": "The divergence appears only after repeated updates."}],
                },
            }
        ]
    }


def _memory():
    return {
        "wiki_sha256": "abc",
        "entries": [
            {
                "memory_id": "MEM-OPEN-1",
                "kind": "OPEN_QUESTION",
                "title": "Persistent drift",
                "summary": "Does matched present state imply matched future hazard?",
                "affected_layer": "core_principle",
                "prompt_eligible": True,
                "reopen_condition": "New identifiable longitudinal evidence.",
                "source_refs": [],
            }
        ],
    }


def _candidate():
    return {
        "title": "Matched state, different future",
        "birth_evidence_refs": ["arXiv:TEST1"],
        "memory_refs": ["MEM-OPEN-1"],
        "scientific_question": "Can matched present state hide different future hazard after different update histories?",
        "observed_trigger": "Long-horizon divergence after matched current success.",
        "structural_variable": "update history",
        "strongest_same_information_baseline": "A history-aware nonstationary baseline receiving the full update trace.",
        "baseline_counterexample": "Matched trace summary but different causal ordering predicts different next-step hazard.",
        "cheapest_falsifier": {"setup": "existing logs", "intervention_or_comparison": "matched histories", "metric": "future violation hazard", "stop_if": "history-aware baseline explains the difference", "estimated_effort": "CPU"},
        "closest_known_explanation": "nonstationary state dynamics",
        "residual_after_reduction": "ordering effect after equal observable history summary",
        "paper_level_claim": "A narrow update-order effect predicts future hazard beyond the strongest matched-information baseline.",
        "paperability_axis": "E",
        "executable_now": True,
    }


def test_mocked_benchmark_compares_all_engines():
    calls = {"generation": 0, "review": 0}

    def call(**kwargs):
        prompt = kwargs["prompt"]
        if "Return STRICT JSON only in this shape" in prompt:
            calls["generation"] += 1
            return {"text": json.dumps({"candidates": [_candidate()]}), "resolved_model": "gen"}
        calls["review"] += 1
        ids = []
        for eid, _, _ in ENGINE_SPECS:
            if f'"candidate_id": "{eid}-C01"' in prompt:
                ids.append(f"{eid}-C01")
        reviews = []
        for cid in ids:
            reviews.append({
                "candidate_id": cid,
                "gate_verdicts": {g: "PASS" for g in GATES},
                "hard_blocker": "",
                "strongest_reduction": "history-aware dynamics",
                "minimum_next_evidence": "run the frozen falsifier",
                "evidence_readiness": 5,
                "falsifier_executability": 5,
                "claim_specificity": 5,
                "estimated_experiments_to_paper": 2,
                "estimated_effort_level": 1,
                "advisory_summary": "near paper-ready",
            })
        return {"text": json.dumps({"reviews": reviews}), "resolved_model": "review"}

    report = run_benchmark(_pool(), _memory(), 1, call, call, "gen", "review")
    assert report["summary"]["engines"] == 7
    assert report["summary"]["generated_candidates"] == 7
    assert report["summary"]["paper_design_ready"] == 7
    assert calls["generation"] == 7
    assert calls["review"] == 1
    assert {row["engine_id"] for row in report["engine_ranking"]} == {spec[0] for spec in ENGINE_SPECS}


def test_invalid_reference_forces_provenance_failure():
    bad = _candidate(); bad["birth_evidence_refs"] = ["arXiv:INVENTED"]

    def call(**kwargs):
        prompt = kwargs["prompt"]
        if "Return STRICT JSON only in this shape" in prompt:
            return {"text": json.dumps({"candidates": [bad]}), "resolved_model": "gen"}
        ids = [f"{eid}-C01" for eid, _, _ in ENGINE_SPECS if f'"candidate_id": "{eid}-C01"' in prompt]
        return {"text": json.dumps({"reviews": [{"candidate_id": cid, "gate_verdicts": {g: "PASS" for g in GATES}, "evidence_readiness": 5, "falsifier_executability": 5, "claim_specificity": 5, "estimated_experiments_to_paper": 1, "estimated_effort_level": 1} for cid in ids]}), "resolved_model": "review"}

    report = run_benchmark(_pool(), _memory(), 1, call, call, "gen", "review")
    assert report["summary"]["paper_design_ready"] == 0
    assert all(row["review"]["gate_verdicts"]["G0"] == "FAIL" for row in report["candidates"])
    assert all(row["benchmark_outcome"]["pre_f0_ready"] is False for row in report["candidates"])


def test_hard_gate_and_adaptive_policy_stay_zero_authority():
    # Use the real frozen benchmark artifact when present: this test protects the
    # calibrated ranking and prevents a shadow benchmark from leaking authority.
    from pathlib import Path
    path = Path("generated/discovery-engine-paper-yield-benchmark.json")
    if not path.exists():
        return
    base = json.loads(path.read_text(encoding="utf-8"))
    adj = compile_adjudication(base)
    assert adj["summary"] == {"candidates": 21, "survive": 0, "hold_near_paper": 9, "reduce": 12, "semantic_basins": 9}
    assert [row["engine_id"] for row in adj["engine_ranking"][:2]] == ["D5", "D2"]
    assert adj["engine_ranking"][-1]["engine_id"] == "D7"
    assert all(value is False for value in adj["authority"].values())
    policy = compile_policy(adj)
    assert abs(sum(row["budget_share"] for row in policy["birth_engines"]) - 1.0) < 1e-9
    assert [row["engine_id"] for row in policy["mandatory_transformers"]] == ["D4", "D3", "D6"]
    assert policy["next_replication"]["compare_only_top_birth_engines"] == ["D5", "D2"]
    assert all(value is False for value in policy["authority"].values())
