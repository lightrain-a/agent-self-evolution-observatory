from __future__ import annotations

import os
from typing import Final

# High-value Ark models explicitly smoke-tested against the configured Responses API.
# This module is routing policy only: it never grants scientific or execution authority.
PREMIUM_MODELS: Final[tuple[str, ...]] = (
    "glm-5.3",
    "kimi-k3",
    "minimax-m3",
    "deepseek-v4-pro",
)

PREMIUM_AUTO = "premium-auto"
MAX_PROVIDER_CONCURRENCY: Final[int] = 2

# Different roles intentionally start from different model families so a designer does
# not silently self-review.  Callers must still compare resolved_model receipts.
_STAGE_PRIORITIES: Final[dict[str, tuple[str, ...]]] = {
    "problem_generation": ("kimi-k3", "deepseek-v4-pro", "glm-5.3", "minimax-m3"),
    "portfolio_expand": ("kimi-k3", "glm-5.3", "minimax-m3", "deepseek-v4-pro"),
    "portfolio_evolve": ("kimi-k3", "deepseek-v4-pro", "glm-5.3", "minimax-m3"),
    "portfolio_formulate": ("kimi-k3", "deepseek-v4-pro", "glm-5.3", "minimax-m3"),
    "semantic_review": ("deepseek-v4-pro", "minimax-m3", "kimi-k3", "glm-5.3"),
    "evidence_design": ("kimi-k3", "deepseek-v4-pro", "glm-5.3", "minimax-m3"),
    "evidence_recompile": ("kimi-k3", "glm-5.3", "minimax-m3", "deepseek-v4-pro"),
    "evidence_review": ("deepseek-v4-pro", "minimax-m3", "kimi-k3", "glm-5.3"),
    "relation_mining": ("kimi-k3", "glm-5.3", "minimax-m3", "deepseek-v4-pro"),
    "relation_lane_review": ("glm-5.3", "minimax-m3", "deepseek-v4-pro", "kimi-k3"),
    "relation_reduction_review": ("deepseek-v4-pro", "minimax-m3", "kimi-k3", "glm-5.3"),
    "paper_design": ("kimi-k3", "deepseek-v4-pro", "glm-5.3", "minimax-m3"),
    "method_synthesis": ("kimi-k3", "deepseek-v4-pro", "glm-5.3", "minimax-m3"),
    "final_scientific_review": ("deepseek-v4-pro", "minimax-m3", "kimi-k3", "glm-5.3"),
}


def stage_model_priority(stage: str) -> tuple[str, ...]:
    key = str(stage or "").strip().lower()
    if key not in _STAGE_PRIORITIES:
        raise KeyError(f"unknown premium-model stage: {stage}")
    return _STAGE_PRIORITIES[key]


def preferred_model(stage: str, requested_model: str | None = None) -> str:
    """Resolve only the *requested* model for a high-value stage.

    Explicit concrete model requests always win.  PREMIUM_AUTO/empty requests use a
    stage-specific premium default.  Resolved provider identities are still recorded by
    ArkResponsesClient and remain the source of truth for independence checks.
    """
    requested = str(requested_model or "").strip()
    if requested and requested != PREMIUM_AUTO:
        return requested
    env_key = "PAPER_FIRST_MODEL_" + str(stage or "").strip().upper().replace("-", "_")
    override = os.getenv(env_key, "").strip()
    if override:
        return override
    return stage_model_priority(stage)[0]


def independent_priority(stage: str, *, exclude_resolved: str = "") -> tuple[str, ...]:
    """Return reviewer candidates with an optional resolved identity excluded.

    This is orchestration metadata; callers must still reject equal resolved_model values
    because provider aliases can resolve to the same backend.
    """
    excluded = str(exclude_resolved or "").strip()
    return tuple(model for model in stage_model_priority(stage) if not excluded or model != excluded)


def policy_summary() -> dict[str, object]:
    return {
        "premium_models": list(PREMIUM_MODELS),
        "max_provider_concurrency": MAX_PROVIDER_CONCURRENCY,
        "stages": {key: list(value) for key, value in sorted(_STAGE_PRIORITIES.items())},
        "explicit_model_override_allowed": True,
        "resolved_model_receipt_is_source_of_truth": True,
        "designer_reviewer_resolved_model_independence_required": True,
        "scientific_authority": False,
    }
