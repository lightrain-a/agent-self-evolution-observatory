from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable

_MOVE_RE = re.compile(
    r"^(?P<who>\w+) (?:journeyed|went|travelled|traveled|moved|went back|travelled back|traveled back) to the (?P<loc>\w+)\.$",
    re.IGNORECASE,
)
_SIMPLE_LOCATION_RE = re.compile(r"^Where is (?P<who>\w+)\?$", re.IGNORECASE)


def _movement_events(contexts: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index, context in enumerate(contexts):
        text = str((context or {}).get("content") or "").strip()
        match = _MOVE_RE.match(text)
        if not match:
            continue
        out.append(
            {
                "index": index,
                "who": match.group("who"),
                "location": match.group("loc"),
                "text": text,
            }
        )
    return out


def _latest_distinct(events: list[dict[str, Any]], who: str, count: int = 3) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for event in reversed(events):
        if str(event.get("who") or "").lower() != who.lower():
            continue
        location = str(event.get("location") or "").lower()
        if not location or location in seen:
            continue
        selected.append(event)
        seen.add(location)
        if len(selected) >= count:
            break
    return selected


def _pick_length_matched_neutral(
    events: list[dict[str, Any]], *, target_who: str, target_text: str, used_indices: set[int]
) -> dict[str, Any] | None:
    candidates = [
        event
        for event in events
        if str(event.get("who") or "").lower() != target_who.lower()
        and int(event.get("index", -1)) not in used_indices
    ]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda event: (
            abs(len(str(event.get("text") or "")) - len(target_text)),
            int(event.get("index", -1)),
            str(event.get("text") or ""),
        ),
    )


def _candidate_id(row_id: str, question_index: int, target: str) -> str:
    raw = f"MINTEval/state_tracking/{row_id}/{question_index}/{target}".encode("utf-8")
    return "b3-mint-" + hashlib.sha256(raw).hexdigest()[:16]


def build_matched_stale_pair_candidates(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build data-only B3 candidates without consulting model outputs.

    Every arm contains exactly three memory slots. S is the latest gold-consistent
    target-location fact and is present in every arm. A/B are the two latest older
    *distinct* target-location facts. N1/N2 are length-matched movement facts about
    other entities. This creates a matched 2x2 intervention over stale co-retrieval:

      none = S + N1 + N2
      A    = S + A  + N2
      B    = S + N1 + B
      AB   = S + A  + B

    A candidate is only a substrate unit. It becomes B3 mechanism support only if
    a frozen model run satisfies the preregistered interaction rule in
    score_factorial_outcome().
    """
    candidates: list[dict[str, Any]] = []
    for wrapped in rows:
        row = wrapped.get("row") if isinstance(wrapped, dict) and isinstance(wrapped.get("row"), dict) else wrapped
        if not isinstance(row, dict):
            continue
        row_id = str(row.get("id") or "").strip()
        events = _movement_events(row.get("contexts") or [])
        if not row_id or not events:
            continue
        for question_index, question in enumerate(row.get("questions") or []):
            if not isinstance(question, dict) or str(question.get("question_type") or "") != "simple":
                continue
            match = _SIMPLE_LOCATION_RE.match(str(question.get("question") or "").strip())
            if not match:
                continue
            target = match.group("who")
            distinct = _latest_distinct(events, target, 3)
            if len(distinct) < 3:
                continue
            support, stale_a, stale_b = distinct[:3]
            gold = str(question.get("answer") or "").strip()
            if str(support.get("location") or "").lower() != gold.lower():
                continue
            neutral_1 = _pick_length_matched_neutral(
                events, target_who=target, target_text=str(stale_a["text"]), used_indices=set()
            )
            if neutral_1 is None:
                continue
            neutral_2 = _pick_length_matched_neutral(
                events,
                target_who=target,
                target_text=str(stale_b["text"]),
                used_indices={int(neutral_1["index"])},
            )
            if neutral_2 is None:
                continue
            arm_memories = {
                "none": [dict(support), dict(neutral_1), dict(neutral_2)],
                "A": [dict(support), dict(stale_a), dict(neutral_2)],
                "B": [dict(support), dict(neutral_1), dict(stale_b)],
                "AB": [dict(support), dict(stale_a), dict(stale_b)],
            }
            arms = {
                name: [str(memory.get("text") or "") for memory in memories]
                for name, memories in arm_memories.items()
            }
            candidates.append(
                {
                    "candidate_id": _candidate_id(row_id, question_index, target),
                    "source": "dinobby/MINTEval",
                    "split": "state_tracking",
                    "history_id": row_id,
                    "question_index": question_index,
                    "question": str(question.get("question") or ""),
                    "gold_answer": gold,
                    "target": target,
                    "support_memory": support,
                    "stale_memory_A": stale_a,
                    "stale_memory_B": stale_b,
                    "neutral_memory_N1": neutral_1,
                    "neutral_memory_N2": neutral_2,
                    "arms": arms,
                    "arm_memories": arm_memories,
                    "candidate_qualified": True,
                    "mechanism_support": False,
                    "selection_used_model_outputs": False,
                    "scientific_authority": False,
                }
            )
    candidates.sort(key=lambda row: (str(row["history_id"]), int(row["question_index"]), str(row["candidate_id"])))
    return candidates


def select_source_disjoint_candidates(candidates: Iterable[dict[str, Any]], limit: int = 24) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_histories: set[str] = set()
    for candidate in candidates:
        history_id = str(candidate.get("history_id") or "")
        if not history_id or history_id in seen_histories:
            continue
        selected.append(dict(candidate))
        seen_histories.add(history_id)
        if len(selected) >= max(0, int(limit)):
            break
    return selected


def score_factorial_outcome(outcomes: dict[str, Any]) -> dict[str, Any]:
    """Score one frozen 2x2 stale-memory intervention.

    Inputs are binary correctness values for none/A/B/AB. The B3 support pattern is
    deliberately stronger than a generic nonzero difference-in-differences: the
    matched base and each stale memory alone must remain correct, while joint stale
    co-retrieval must fail. This excludes ordinary multi-hop complementarity and
    simple single-memory harm.
    """
    values = {name: int(bool(outcomes.get(name))) for name in ("none", "A", "B", "AB")}
    interaction = values["AB"] - values["A"] - values["B"] + values["none"]
    joint_only_harm = values == {"none": 1, "A": 1, "B": 1, "AB": 0}
    ordinary_complementarity = values == {"none": 0, "A": 0, "B": 0, "AB": 1}
    single_memory_harm = bool(values["none"] == 1 and (values["A"] == 0 or values["B"] == 0))
    return {
        "binary_correctness": values,
        "interaction_contrast": interaction,
        "joint_only_co_retrieval_harm": joint_only_harm,
        "ordinary_complementarity_excluded": ordinary_complementarity,
        "single_memory_harm_excluded": single_memory_harm,
        "mechanism_support": bool(joint_only_harm),
        "scientific_authority": False,
    }


def build_preflight_payload(rows: Iterable[dict[str, Any]], *, freeze_limit: int = 24, required_support: int = 6) -> dict[str, Any]:
    candidates = build_matched_stale_pair_candidates(rows)
    frozen = select_source_disjoint_candidates(candidates, freeze_limit)
    return {
        "schema_version": "1.0",
        "idea_id": "B3-CO-RETRIEVAL-INTERACTION",
        "mode": "DATA_ONLY_MATCHED_STALE_PAIR_PREFLIGHT",
        "candidate_definition": "S fixed latest gold fact; A/B are two older distinct target facts; N1/N2 are length-matched other-entity movement facts; 2x2 slots are matched before model execution.",
        "factorial_arms": {
            "none": "S+N1+N2",
            "A": "S+A+N2",
            "B": "S+N1+B",
            "AB": "S+A+B",
        },
        "support_rule": "Count only none=1,A=1,B=1,AB=0 as joint-only co-retrieval harm; ordinary two-fact complementarity and single-memory harm do not qualify.",
        "candidate_pool": len(candidates),
        "source_disjoint_frozen": len(frozen),
        "required_interaction_positive_support": int(required_support),
        "selection_used_model_outputs": False,
        "frozen_candidates": frozen,
        "scientific_authority": False,
        "authority": {"problem_gate": False, "method": False, "experiment": False, "p0": False, "gpu": False},
    }
