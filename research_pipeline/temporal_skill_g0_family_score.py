from __future__ import annotations

import re
from typing import Any


def normalize_reporting_period(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    s = re.sub(r"\s+", " ", value.strip().lower())
    # Frozen family-audit normalization accepts canonical hyphen notation and
    # human-readable space/quarter forms. Colon/underscore variants are not
    # canonicalized; the row-level historical receipts explicitly mark them null.
    if ":" in s or "_" in s:
        return None
    # YYYY-Qn / YYYY Qn / Qn YYYY, with optional explanatory suffix.
    m = re.search(r"\b(20\d{2})\s*[- ]?\s*q([1-4])\b", s)
    if m:
        return f"{m.group(1)}-Q{m.group(2)}"
    m = re.search(r"\bq([1-4])\s*[- ]?\s*(20\d{2})\b", s)
    if m:
        return f"{m.group(2)}-Q{m.group(1)}"
    words = {"first": "1", "1st": "1", "second": "2", "2nd": "2", "third": "3", "3rd": "3", "fourth": "4", "4th": "4"}
    m = re.search(r"\b(first|1st|second|2nd|third|3rd|fourth|4th)\s+quarter\s+(20\d{2})\b", s)
    if m:
        return f"{m.group(2)}-Q{words[m.group(1)]}"
    m = re.search(r"\b(20\d{2})\s+(first|1st|second|2nd|third|3rd|fourth|4th)\s+quarter\b", s)
    if m:
        return f"{m.group(1)}-Q{words[m.group(2)]}"
    return None


def family_score(endpoint: dict[str, Any], pred: dict[str, Any]) -> dict[str, Any]:
    family = str(endpoint["failure_family"])
    gold = endpoint["gold"]
    if family == "exogenous_grounding":
        xs = pred.get("selected_span_ids")
        ok = isinstance(xs, list) and len(xs) == int(endpoint.get("scorer", {}).get("exact_length", 2))
        details: dict[str, Any] = {"criterion": "frozen ordered-slot first-party grounding scorer"}
        if ok:
            for i, allowed in enumerate(gold["slot_acceptable_span_ids"]):
                hit = xs[i] in allowed
                details[gold["slot_names"][i]] = bool(hit)
                ok = ok and bool(hit)
        return {"success": bool(ok), "details": details}
    if family == "release_alignment":
        raw_period = pred.get("reporting_period")
        normalized = normalize_reporting_period(raw_period)
        gold_period = normalize_reporting_period(gold["reporting_period"])
        value = pred.get("headline_value")
        value_ok = isinstance(value, (int, float)) and abs(float(value) - float(gold["headline_value"])) <= 1e-9
        period_ok = normalized == gold_period and normalized is not None
        return {
            "success": bool(period_ok and value_ok),
            "details": {
                "criterion": "semantic reporting-period identity plus aligned headline value",
                "period_raw": raw_period,
                "period_normalized": normalized,
                "gold_period": gold_period,
                "period_match": bool(period_ok),
                "headline_value_match": bool(value_ok),
                "release_stage_ignored_by_family_contract": True,
            },
        }
    if family == "temporal_cutoff":
        refs = pred.get("evidence_refs_used")
        latest = pred.get("latest_evidence_ref")
        valid = set(gold["evidence_refs_used"])
        # The R3 endpoint gold stores only the latest admissible ref, but the
        # package exposes all release metadata. Reconstruct all cutoff-valid refs.
        cutoff = str(endpoint["cutoff_date"])
        for meta in endpoint["package"].get("evidence_metadata", []):
            if str(meta.get("release_date") or "") <= cutoff:
                valid.add(str(meta["evidence_ref"]))
        target = str(gold["latest_evidence_ref"])
        ok = isinstance(refs, list) and bool(refs) and latest == target and latest in refs and all(str(x) in valid for x in refs)
        return {
            "success": bool(ok),
            "details": {
                "criterion": "nonempty cited refs and latest ref are all cutoff-valid",
                "evidence_refs_used": refs,
                "latest_evidence_ref": latest,
                "valid_refs": sorted(valid),
            },
        }
    raise ValueError(f"unknown failure family: {family}")
