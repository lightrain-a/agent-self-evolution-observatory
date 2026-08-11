from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "emerging-niche-policy.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "emerging-niche-policy.js"

COMPONENTS: dict[str, dict[str, Any]] = {
    "exact_problem_sparsity": {"weight": 0.30, "en": "Exact-problem sparsity", "zh": "精确问题稀疏度"},
    "emerging_signal": {"weight": 0.20, "en": "Emerging-neighborhood signal", "zh": "新兴邻域信号"},
    "collision_margin": {"weight": 0.20, "en": "Collision margin", "zh": "碰撞余量"},
    "decisive_p0": {"weight": 0.20, "en": "Cheap decisive P0", "zh": "低成本决定性 P0"},
    "importance_floor": {"weight": 0.10, "en": "Importance floor", "zh": "重要性地板"},
}
BANDS = (
    {"min": 80, "key": "priority", "en": "Emerging-niche priority", "zh": "新兴小众优先"},
    {"min": 65, "key": "promising", "en": "Promising / verify", "zh": "有潜力／继续核验"},
    {"min": 50, "key": "neutral", "en": "Maturing / neutral", "zh": "正在成熟／中性"},
    {"min": 0, "key": "low", "en": "Crowded, weak, or premature", "zh": "拥挤、偏弱或过早"},
)
AUTHORITATIVE_BLOCKS = (
    "direct_collision", "matched_simplification_reducible", "experiment_stop",
    "human_terminal_merge", "human_terminal_drop",
)

def _value(value: Any, key: str) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{key} must be numeric") from error
    if not 0 <= score <= 5:
        raise ValueError(f"{key} must be in [0, 5]")
    return score


def score_emerging_niche(components: Mapping[str, Any] | None, *, evidence_fresh: bool,
                         authoritative_blocks: Mapping[str, Any] | None = None) -> dict[str, Any]:
    supplied = dict(components or {})
    missing = [key for key in COMPONENTS if supplied.get(key) is None]
    blocks = [key for key in AUTHORITATIVE_BLOCKS if bool((authoritative_blocks or {}).get(key))]
    if not evidence_fresh or missing:
        return {"status": "pending", "score": None, "band": "pending", "priority_eligible": False,
                "reason": "fresh_primary_source_evidence_required" if not evidence_fresh else "missing_components",
                "missing_components": missing, "authoritative_blocks": blocks}
    values = {key: _value(supplied[key], key) for key in COMPONENTS}
    raw = 20 * sum(values[key] * float(meta["weight"]) for key, meta in COMPONENTS.items())
    final, caps = raw, []
    if values["emerging_signal"] < 2:
        final = min(final, 64); caps.append("insufficient_emerging_neighborhood")
    if values["importance_floor"] < 3:
        final = min(final, 64); caps.append("importance_floor_not_met")
    if values["decisive_p0"] < 3:
        final = min(final, 69); caps.append("decisive_p0_floor_not_met")
    final = round(final, 1)
    band = next(item for item in BANDS if final >= item["min"])
    return {"status": "scored", "score": final, "raw_score": round(raw, 1), "band": band["key"],
            "band_label": {"en": band["en"], "zh": band["zh"]}, "priority_eligible": not blocks,
            "components": values, "caps": caps, "authoritative_blocks": blocks,
            "reason": "eligible_for_priority_ordering" if not blocks else "blocked_by_authoritative_gate"}

def policy_payload() -> dict[str, Any]:
    return {
        "schema_version": "1.0", "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "name": "Emerging-Niche Score", "short_name": "ENS", "scale": "0-100",
        "role": "candidate exploration and audit priority only",
        "formula": "20 * sum(component_0_to_5 * weight)", "components": COMPONENTS, "bands": list(BANDS),
        "hard_policy": {
            "fresh_primary_source_evidence_required": True, "generator_self_score_forbidden": True,
            "unknown_is_pending_not_high": True, "importance_floor": 3, "decisive_p0_floor": 3,
            "never_overrides": list(AUTHORITATIVE_BLOCKS), "human_terminal_and_real_experiment_precedence": True,
            "discussion_pool_exclusion_forbidden": True,
        },
        "interpretation": {
            "en": "Reward a forming research neighborhood whose exact problem-mechanism pair remains sparse and has a cheap decisive pilot. Rarity alone earns nothing.",
            "zh": "奖励邻域正在形成、精确问题—机制仍稀疏、且存在便宜决定性 P0 的方向；单纯冷门本身不加分。",
        },
    }


def write_emerging_niche_policy(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = policy_payload(); json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.EMERGING_NICHE_POLICY = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--json", type=Path, default=DEFAULT_JSON); p.add_argument("--js", type=Path, default=DEFAULT_JS); a = p.parse_args()
    payload = write_emerging_niche_policy(a.json, a.js)
    print(json.dumps({"name": payload["name"], "components": len(payload["components"]), "scale": payload["scale"]}, ensure_ascii=False)); return 0


if __name__ == "__main__": raise SystemExit(main())
