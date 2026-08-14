from __future__ import annotations

import hashlib
import re
from typing import Any

from .paper_first_primary_evidence import PRIMARY_EVIDENCE_OBJECT_LANES, _ArxivFullTextParser

CARRIER_CLASSIFIER_VERSION = "existing-object-carrier-v1"
LIVE_RESCUE_ELIGIBLE_LANES = frozenset({"parametric_model_state", "memory_continual", "world_model"})

_ALLOWED_SECTION_TERMS = (
    "method", "framework", "approach", "architecture", "system", "self-evolution",
    "self evolution", "implementation", "policy optimization", "training", "experiment setup", "algorithm",
    "experiment-guided", "strategy self-evolution", "rule generation", "rule elimination",
)
_EXCLUDED_SECTION_TERMS = ("related work", "background", "reference", "literature review")

_CARRIER_RULES: dict[str, tuple[re.Pattern[str], ...]] = {
    "parametric_model_state": tuple(re.compile(pattern, re.I) for pattern in (
        r"\bfor self[- ]evolution.{0,100}\b(?:lora[- ]based )?fine[- ]tuning\b",
        r"\bupdate(?:d|s|ing)?\s+(?:the\s+)?lora parameters\b",
        r"\binternaliz(?:e|es|ed|ing).{0,100}\bmodel weights\b",
        r"\bpolicy weight updates?\b",
        r"\bco[- ]evolving model weights\b",
        r"\bon[- ]policy (?:self[- ])?distillation\b",
        r"\bparameter[- ]based approaches?.{0,120}\bmodel parameters\b",
        r"\bcontinuously evolves? via fine[- ]tuning\b",
        r"\b(?:actor|policy|agent) model is trained\b",
        r"\btrain(?:ed|ing)? the (?:actor|policy|agent) model\b",
    )),
    "memory_continual": tuple(re.compile(pattern, re.I) for pattern in (
        r"\bpersistent (?:agent )?memory\b",
        r"\bepisodic memory bank\b",
        r"\b(?:hierarchical )?(?:strategy )?experience tree\b",
        r"\bpersistent evidence memory\b",
        r"\bmemory (?:state|store|bank).{0,100}\b(?:update|evolv|grow|refin)",
    )),
    "skill_harness": tuple(re.compile(pattern, re.I) for pattern in (
        r"\bpersistent runtime state\b",
        r"\bskill librar(?:y|ies)\b",
        r"\b(?:query[- ]rewriting )?rule set\b.{0,120}\b(?:refin|optim|evolv|update)",
        r"\b(?:refin|optim|evolv|update).{0,120}\b(?:query[- ]rewriting )?rule set\b",
        r"\brefin(?:e|es|ed|ing) query[- ]rewriting rules\b",
        r"\bexecutable (?:runtime )?harness\b",
        r"\bplaybook memory\b",
    )),
    "world_model": tuple(re.compile(pattern, re.I) for pattern in (
        r"\bself[- ]evolving world models?\b",
        r"\bworld model framework that revises\b",
        r"\bworld model mixture and evolution\b",
        r"\bcontinual (?:framework for .{0,80})?world model optimization\b",
        r"\bclosed[- ]loop refinement of the world model\b",
    )),
}
_PARAMETRIC_NEGATIVE = tuple(re.compile(pattern, re.I) for pattern in (
    r"\bwithout (?:any )?(?:parameter|weight) updates?\b",
    r"\bdoes not update model weights\b",
    r"\bmodel weights remain fixed\b",
    r"\bwithout changing a single model weight\b",
))
PRIMARY_SCOPE_EXCLUSION_RULE_VERSION = "genetic-network-programming-non-llm-v1"
_LLM_SCOPE_TERMS = ("llm", "large language model", "language model", "foundation model")


def primary_scope_exclusion(*, title: str, abstract: str) -> dict[str, Any] | None:
    """Return a narrow zero-authority carrier-probe scope exclusion.

    This does not alter global relevance or make a scientific negative claim. It
    only prevents a paper that explicitly studies Genetic Network Programming,
    without any language-model scope, from permanently blocking the LLM-agent
    existing-object carrier probe when arXiv HTML is unavailable.
    """
    text = f"{title} {abstract}".lower()
    if "genetic network programming" not in text:
        return None
    if any(term in text for term in _LLM_SCOPE_TERMS):
        return None
    return {
        "probe_outcome": "SCOPE_EXCLUDED_BY_PRIMARY",
        "scope_exclusion_rule": PRIMARY_SCOPE_EXCLUSION_RULE_VERSION,
        "reason": "Primary title/abstract explicitly studies Genetic Network Programming without language-model scope; this paper is outside the existing LLM-agent carrier-rescue probe only.",
        "scientific_authority": False,
        "global_relevance_changed": False,
        "can_create_new_object": False,
    }


def build_primary_scope_exclusion_receipt(*, ref: str, title: str, abstract: str, primary_sha256: str) -> dict[str, Any] | None:
    exclusion = primary_scope_exclusion(title=title, abstract=abstract)
    if not exclusion:
        return None
    return {
        "schema_version": "1.0",
        "ref": str(ref),
        "title": str(title)[:300],
        "primary_sha256": str(primary_sha256),
        "fulltext_sha256": "",
        "classifier_version": CARRIER_CLASSIFIER_VERSION,
        "probe_outcome": exclusion["probe_outcome"],
        "scope_exclusion_rule": exclusion["scope_exclusion_rule"],
        "matched_existing_object_lanes": [],
        "live_rescue_eligible_lanes": [],
        "carrier_evidence": [],
        "policy": {
            "scientific_authority": False,
            "existing_object_lanes_only": True,
            "new_object_creation_forbidden": True,
            "global_relevance_changed": False,
            "fulltext_not_required_for_narrow_primary_scope_exclusion": True,
        },
        "scientific_authority": False,
    }


def _eligible_section(section: str) -> bool:
    low = str(section or "").lower()
    if any(term in low for term in _EXCLUDED_SECTION_TERMS):
        return False
    return any(term in low for term in _ALLOWED_SECTION_TERMS)


def _matching_excerpt(text: str, patterns: tuple[re.Pattern[str], ...]) -> str:
    for pattern in patterns:
        match = pattern.search(text)
        if not match:
            continue
        start = max(0, match.start() - 180)
        end = min(len(text), match.end() + 260)
        return " ".join(text[start:end].split())
    return ""


def classify_existing_object_carriers(*, title: str, abstract: str, fulltext_html: str) -> list[dict[str, Any]]:
    """Return zero-authority full-text receipts for already active object lanes.

    This classifier cannot create a new scientific object and does not change
    discovery membership by itself. It is deliberately high precision: only
    own-method/system/self-evolution sections are considered, while Related
    Work/Background text is excluded.
    """
    active_objects = {str(row["key"]) for row in PRIMARY_EVIDENCE_OBJECT_LANES}
    parser = _ArxivFullTextParser()
    try:
        parser.feed(fulltext_html)
    except Exception:
        return []
    receipts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for section, paragraph in parser.paragraphs:
        if not _eligible_section(section):
            continue
        text = " ".join(str(paragraph or "").split())
        if len(text) < 50:
            continue
        for lane, patterns in _CARRIER_RULES.items():
            if lane not in active_objects or lane in seen:
                continue
            if lane == "parametric_model_state" and any(pattern.search(text) for pattern in _PARAMETRIC_NEGATIVE):
                continue
            excerpt = _matching_excerpt(text, patterns)
            if not excerpt:
                continue
            seen.add(lane)
            receipts.append({
                "object_lane": lane,
                "section": str(section or "unnamed")[:240],
                "evidence_excerpt": excerpt[:700],
                "evidence_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "classifier_version": CARRIER_CLASSIFIER_VERSION,
                "live_rescue_eligible": lane in LIVE_RESCUE_ELIGIBLE_LANES,
                "scientific_authority": False,
                "can_create_new_object": False,
                "can_change_discovery_membership": False,
            })
    return receipts


def build_carrier_probe_receipt(*, ref: str, title: str, primary_sha256: str, fulltext_sha256: str, fulltext_html: str) -> dict[str, Any]:
    receipts = classify_existing_object_carriers(title=title, abstract="", fulltext_html=fulltext_html)
    return {
        "schema_version": "1.0",
        "ref": str(ref),
        "title": str(title)[:300],
        "primary_sha256": str(primary_sha256),
        "fulltext_sha256": str(fulltext_sha256),
        "classifier_version": CARRIER_CLASSIFIER_VERSION,
        "matched_existing_object_lanes": sorted(row["object_lane"] for row in receipts),
        "live_rescue_eligible_lanes": sorted(row["object_lane"] for row in receipts if row.get("live_rescue_eligible") is True),
        "carrier_evidence": receipts,
        "policy": {
            "scientific_authority": False,
            "existing_object_lanes_only": True,
            "new_object_creation_forbidden": True,
            "discovery_membership_change_forbidden_in_shadow_probe": True,
            "related_work_cannot_supply_carrier_evidence": True,
            "skill_harness_rescue_is_shadow_only_until_precision_gate_passes": True,
        },
        "scientific_authority": False,
    }
