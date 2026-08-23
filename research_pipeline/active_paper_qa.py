from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from .paper_assertion_policy import audit_manuscript_directory


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _get(payload: Any, dotted: str) -> Any:
    cur = payload
    for part in dotted.split("."):
        if isinstance(cur, dict):
            cur = cur[part]
        else:
            raise KeyError(dotted)
    return cur


def _normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9.]+", " ", text.lower()).strip()


def _compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _run(args: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True)
    return proc.stdout


def _check(name: str, condition: bool, detail: Any = None) -> dict[str, Any]:
    return {"name": name, "pass": bool(condition), "detail": detail}


def audit_paper(spec: dict[str, Any]) -> dict[str, Any]:
    paper_dir = Path(spec["paper_dir"])
    pdf = paper_dir / "main.pdf"
    log = paper_dir / "main.log"
    ledger_path = Path(spec["claim_ledger"])
    if not pdf.exists() or not log.exists() or not ledger_path.exists():
        raise FileNotFoundError("paper PDF, log, or claim ledger missing")

    pdfinfo = _run(["pdfinfo", str(pdf)])
    page_match = re.search(r"^Pages:\s+(\d+)", pdfinfo, re.MULTILINE)
    pages = int(page_match.group(1)) if page_match else -1
    pdftext = _run(["pdftotext", str(pdf), "-"])
    norm = _normalized(pdftext)
    compact_pdf = _compact(pdftext)
    logtext = log.read_text(encoding="utf-8", errors="ignore")
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    style = audit_manuscript_directory(paper_dir)
    manuscript_sources = sorted(paper_dir.rglob("*.tex")) + [paper_dir / "references.bib"]
    figure_sources = sorted((paper_dir / "figures").rglob("*.pdf")) if (paper_dir / "figures").exists() else []
    freshness_sources = manuscript_sources + figure_sources
    existing_sources = [path for path in freshness_sources if path.exists()]

    checks: list[dict[str, Any]] = []
    newest_source = max(existing_sources, key=lambda path: path.stat().st_mtime_ns) if existing_sources else None
    checks.append(_check(
        "pdf_not_older_than_sources",
        newest_source is None or pdf.stat().st_mtime_ns >= newest_source.stat().st_mtime_ns,
        {
            "pdf_mtime_ns": pdf.stat().st_mtime_ns,
            "newest_source": str(newest_source) if newest_source else None,
            "newest_source_mtime_ns": newest_source.stat().st_mtime_ns if newest_source else None,
        },
    ))
    max_main_pages = spec.get("max_main_pages")
    if max_main_pages is not None:
        aux = paper_dir / "main.aux"
        appendix_start_page = None
        if aux.exists():
            auxtext = aux.read_text(encoding="utf-8", errors="ignore")
            matches = [int(x) for x in re.findall(r"\\newlabel\{app:[^}]+\}\{\{[^}]*\}\{(\d+)\}", auxtext)]
            if matches:
                appendix_start_page = min(matches)
        main_pages = (appendix_start_page - 1) if appendix_start_page else pages
        checks.append(_check(
            "page_limit",
            0 < main_pages <= int(max_main_pages),
            {"main_pages": main_pages, "max_main_pages": int(max_main_pages), "appendix_start_page": appendix_start_page, "total_pages": pages},
        ))
        if spec.get("max_total_pages") is not None:
            checks.append(_check("total_page_limit", 0 < pages <= int(spec["max_total_pages"]), pages))
    else:
        checks.append(_check("page_limit", 0 < pages <= int(spec.get("max_pages") or 9), pages))
    checks.append(_check("anonymous_placeholder", "anonymous authors" in pdftext.lower()))
    checks.append(_check("no_author_email", re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", pdftext) is None))
    checks.append(_check("no_internal_identity", all(token not in pdftext.lower() for token in ("/home/wyt", "222.20.126.69", "lightrain"))))
    checks.append(_check("no_undefined_citations", "undefined citation" not in logtext.lower() and "citation(s) may have changed" not in logtext.lower()))
    checks.append(_check("no_undefined_references", "undefined references" not in logtext.lower() and "there were undefined references" not in logtext.lower()))
    checks.append(_check("no_overfull", "overfull \\hbox" not in logtext.lower() and "overfull \\vbox" not in logtext.lower()))
    checks.append(_check("manuscript_policy", style["passed"], style.get("violations")))

    for fragment in spec.get("title_fragments") or []:
        target = _compact(fragment)
        checks.append(_check(f"title:{fragment}", target in compact_pdf))
    for fragment in spec.get("required_pdf_fragments") or []:
        target = _normalized(fragment)
        checks.append(_check(f"pdf_fragment:{fragment}", target in norm))

    active_claims = []
    for row in ledger.get("claims") or []:
        verdict = str(row.get("verdict") or "")
        if verdict.startswith("ACTIVE_UNREFUTED"):
            active_claims.append(str(row.get("claim_id") or ""))
            checks.append(_check(f"active_retain:{row.get('claim_id')}", row.get("retain_in_manuscript") is True))
            checks.append(_check(f"active_no_auto_narrow:{row.get('claim_id')}", row.get("claim_narrowing_required") is False))
            checks.append(_check(f"active_no_closure:{row.get('claim_id')}", not str(row.get("closure_authority") or "")))
    checks.append(_check("claim_ledger_has_claims", bool(ledger.get("claims")), len(ledger.get("claims") or [])))

    artifact_results = []
    for rule in spec.get("artifact_checks") or []:
        payload = json.loads(Path(rule["path"]).read_text(encoding="utf-8"))
        actual = _get(payload, rule["key"])
        expected = rule.get("equals")
        passed = actual == expected
        artifact_results.append({"path": rule["path"], "key": rule["key"], "actual": actual, "expected": expected, "pass": passed})
        checks.append(_check(f"artifact:{rule['key']}", passed, {"actual": actual, "expected": expected}))

    sources = manuscript_sources + figure_sources
    passed = all(row["pass"] for row in checks)
    return {
        "schema_version": "1.0",
        "paper_id": spec["paper_id"],
        "status": "PASS" if passed else "FAIL",
        "paper_dir": str(paper_dir),
        "summary": {
            "checks": len(checks),
            "passed": sum(row["pass"] for row in checks),
            "pages": pages,
            "pdf_sha256": _sha(pdf),
            "pdf_bytes": pdf.stat().st_size,
            "active_unrefuted_claims": active_claims,
        },
        "checks": checks,
        "style_audit": style,
        "artifact_checks": artifact_results,
        "manuscript_files": [{"path": str(p), "sha256": _sha(p)} for p in sources if p.exists()],
        "claim_ledger": {"path": str(ledger_path), "sha256": _sha(ledger_path)},
        "scientific_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contracts", type=Path, required=True)
    parser.add_argument("--paper-id")
    args = parser.parse_args()
    contracts = json.loads(args.contracts.read_text(encoding="utf-8"))
    specs = [row for row in contracts.get("papers") or [] if not args.paper_id or row.get("paper_id") == args.paper_id]
    if not specs:
        raise ValueError("paper spec not found")
    exit_code = 0
    for spec in specs:
        report = audit_paper(spec)
        output = Path(spec["output"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"paper_id": report["paper_id"], "status": report["status"], "summary": report["summary"]}, ensure_ascii=False, indent=2))
        if report["status"] != "PASS":
            exit_code = 1
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
