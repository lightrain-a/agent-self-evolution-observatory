from __future__ import annotations

from typing import Any

from .method_details_common import bi


def final(recommendation: str, gate_zh: str, gate_en: str, baseline_zh: str, baseline_en: str, rationale_zh: str, rationale_en: str, sources: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "round": "2026-08-10",
        "recommendation": recommendation,
        "offline_pre_p0_gate": bi(gate_zh, gate_en),
        "strongest_simplification": bi(baseline_zh, baseline_en),
        "rationale": bi(rationale_zh, rationale_en),
        "sources": sources or [],
        "multi_model_inputs": ["deepseek-v4-pro", "kimi-k3", "doubao-seed-evolving"],
        "glm_5_2_status": "returned-but-failed-structured-quality-gate",
    }


def iteration(verdict: str, zh: str, en: str) -> dict[str, Any]:
    return {"round": "2026-08-10 · Final Refinement", "verdict": verdict, "summary": bi(zh, en)}
