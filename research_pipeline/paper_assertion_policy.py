from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PAPER_ASSERTION_POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "draft_before_evidence_completion": True,
    "unrefuted_hypothesis_stays_active": True,
    "missing_evidence_creates_experiment_debt": True,
    "missing_evidence_does_not_trigger_claim_narrowing": True,
    "maximally_assertive_evidence_compatible_wording": True,
    "scientific_evidence_state_is_separate_from_manuscript_stance": True,
    "refutation_requires_scientific_counterevidence": True,
    "refutation_authorities": [
        "direct_counterevidence",
        "same_information_reduction",
        "scope_matched_principle_counter_explanation",
    ],
    "single_limitations_section_required": True,
    "distributed_limitation_language_forbidden": True,
    "not_but_contrast_forbidden": True,
    "rather_than_contrast_forbidden": True,
    "serial_enumeration_sentence_forbidden": True,
}

SUPPORTED_STATES = {
    "SUPPORTED",
    "SUPPORTED_NARROWLY",
    "SUPPORTED_ACTIVE",
    "PASS",
}
REFUTED_STATES = {
    "REFUTED",
    "REFUTED_BY_RESIDUAL",
    "PRINCIPLE_STOP",
    "PRINCIPLE_DEAD_END",
}


def resolve_manuscript_stance(evidence_state: str) -> str:
    """Map evidence state to manuscript stance without treating missing evidence as refutation."""
    state = str(evidence_state or "").strip().upper()
    if state in REFUTED_STATES:
        return "REMOVE_OR_REFORMULATE_REFUTED_CLAIM"
    if state in SUPPORTED_STATES:
        return "ASSERTIVE_SUPPORTED_CLAIM"
    return "ACTIVE_UNREFUTED_HYPOTHESIS"


def experiment_debt_for_claim(claim_id: str, evidence_state: str, missing_evidence: list[str] | None = None) -> dict[str, Any]:
    stance = resolve_manuscript_stance(evidence_state)
    debt = [str(item) for item in (missing_evidence or []) if str(item).strip()]
    return {
        "claim_id": str(claim_id),
        "evidence_state": str(evidence_state),
        "manuscript_stance": stance,
        "experiment_debt": debt,
        "retain_in_manuscript": stance != "REMOVE_OR_REFORMULATE_REFUTED_CLAIM",
        "claim_narrowing_required": False if stance == "ACTIVE_UNREFUTED_HYPOTHESIS" else None,
    }


def _plain_latex(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\cite[tp]?\{[^}]*\}", "", text)
    text = re.sub(r"\\(?:ref|eqref|label)\{[^}]*\}", "", text)
    text = re.sub(r"\\(?:emph|textbf|textit|texttt)\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    return re.sub(r"[ \t]+", " ", text)


def audit_manuscript_sources(
    sources: dict[str, str],
    *,
    limitations_source: str,
) -> dict[str, Any]:
    """Lint manuscript stance and style rules requested by the paper-writing policy."""
    violations: list[dict[str, Any]] = []
    limitation_sections = 0
    limitation_markers = (
        "we do not claim",
        "we cannot claim",
        "does not prove",
        "not a causal",
        "not causal",
        "inconclusive",
        "missing causal control",
        "missing experiment",
        "remains missing",
        "future evidence",
        "future validation",
        "limited to this",
        "is limited to",
    )

    not_but = re.compile(r"\bnot\b[^.!?\n]{0,120}\bbut\b", re.IGNORECASE)
    rather_than = re.compile(r"\brather\s+than\b", re.IGNORECASE)
    chinese_not_but = re.compile(r"不是[^。！？\n]{0,80}而是")
    serial_enum = re.compile(
        r"[^.!?\n,]{1,80},\s+[^.!?\n,]{1,80},\s+(?:and|or)\s+[^.!?\n]{1,100}",
        re.IGNORECASE,
    )

    for path, raw in sources.items():
        plain = _plain_latex(raw)
        limitation_sections += len(re.findall(r"\\section\{Limitations(?:\s+and\s+Scope)?\}", raw, re.IGNORECASE))
        for rule, pattern in (
            ("not_but_contrast", not_but),
            ("rather_than_contrast", rather_than),
            ("serial_enumeration_sentence", serial_enum),
        ):
            for match in pattern.finditer(plain):
                violations.append({"source": path, "rule": rule, "excerpt": match.group(0).strip()[:240]})
        for match in chinese_not_but.finditer(plain):
            violations.append({"source": path, "rule": "not_but_contrast", "excerpt": match.group(0).strip()[:240]})

        if path != limitations_source:
            low = plain.lower()
            for marker in limitation_markers:
                if marker in low:
                    violations.append({"source": path, "rule": "distributed_limitation_language", "excerpt": marker})

    if limitation_sections != 1:
        violations.append(
            {
                "source": limitations_source,
                "rule": "single_limitations_section",
                "excerpt": f"found {limitation_sections} Limitations sections",
            }
        )

    return {
        "schema_version": "1.0",
        "policy": PAPER_ASSERTION_POLICY,
        "limitations_source": limitations_source,
        "sources_audited": len(sources),
        "passed": not violations,
        "violations": violations,
    }


def audit_manuscript_directory(paper_dir: Path, *, limitations_source: str = "sections/06_limitations_conclusion.tex") -> dict[str, Any]:
    sources: dict[str, str] = {}
    for path in sorted(paper_dir.rglob("*.tex")):
        sources[str(path.relative_to(paper_dir))] = path.read_text(encoding="utf-8")
    return audit_manuscript_sources(sources, limitations_source=limitations_source)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Audit manuscript assertion and prose policy.")
    parser.add_argument("paper_dir", type=Path)
    parser.add_argument("--limitations-source", default="sections/06_limitations_conclusion.tex")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit_manuscript_directory(args.paper_dir, limitations_source=args.limitations_source)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if result["passed"] else "FAIL")
        for row in result["violations"]:
            print(f"{row['source']}: {row['rule']}: {row['excerpt']}")
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
