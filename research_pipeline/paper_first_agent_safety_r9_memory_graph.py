from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SCHEMA_VERSION = "1.0"
SUPPORTED_CLAIM_ID = "AGENT-SAFETY-R9-STATIC-PASS-NO-FUTURE-GUARANTEE"
CAUSAL_HOLD_CLAIM_ID = "AGENT-SAFETY-R9-PERSISTENT-UPDATE-CAUSAL-ATTRIBUTION"
REOPEN_CONDITION = (
    "Separate persistent update effect from held-out schedule effect with a "
    "pre-registered same-held-out-schedule no-update control under the frozen runtime."
)
DEFAULT_RECEIPT = (
    PROJECT_ROOT / "generated" / "agent-safety-r9-future-evidence-adjudication-20260820.json"
)
DEFAULT_CLAIM_TABLE_JSON = (
    PROJECT_ROOT / "generated" / "agent-safety-r9-paper-claim-table-20260820.json"
)
DEFAULT_CLAIM_TABLE_TEX = (
    PROJECT_ROOT / "paper_drafts" / "agent-safety-r9-paper-claim-table-20260820.tex"
)
DEFAULT_MEMORY_BUNDLE = (
    PROJECT_ROOT / "generated" / "agent-safety-r9-memory-graph21-inputs-20260820.json"
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_receipt(path: Path = DEFAULT_RECEIPT) -> dict[str, Any]:
    receipt = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(receipt, dict), "agent-safety receipt must be a JSON object")
    require(
        receipt.get("status")
        == "SUPPORTED_R9_STATIC_PASS_DOES_NOT_GUARANTEE_FUTURE_NO_VIOLATION",
        "agent-safety receipt is not adjudicated",
    )
    require(receipt.get("scientific_authority") is False, "receipt authority leak")
    require(receipt.get("paper_evidence_ready") is True, "paper evidence is not ready")
    require(
        receipt.get("additional_behavior_execution_authorized") is False,
        "receipt unexpectedly authorizes additional behavior execution",
    )
    static = receipt.get("static_current_safety") or {}
    future = receipt.get("future_first_violation") or {}
    integrity = receipt.get("execution_integrity") or {}
    require(
        static.get("qualification_episodes") == 12
        and static.get("qualification_violations") == 0,
        "static qualification evidence drift",
    )
    require(
        future.get("future_episodes") == 36
        and future.get("future_violation_episodes") == 11
        and future.get("branches") == 12
        and future.get("branches_with_first_violation") == 8
        and future.get("states_with_first_violation") == 3,
        "future hazard evidence drift",
    )
    require(
        integrity.get("completed_future_episodes") == 36
        and integrity.get("protocol_inconclusive_episodes") == 0
        and integrity.get("heldout_outcomes_used_for_support_selection") is False,
        "future execution integrity drift",
    )
    return receipt


def _receipt_ref(path: Path, receipt: dict[str, Any]) -> str:
    return f"repo://generated/{path.name}#sha256={file_sha256(path)}"


def build_paper_claim_table(
    receipt: dict[str, Any], *, receipt_ref: str
) -> dict[str, Any]:
    supported = (receipt.get("claim_scope") or {}).get("supported") or ""
    not_supported = list((receipt.get("claim_scope") or {}).get("not_supported") or [])
    require(supported and len(not_supported) == 4, "claim scope cardinality drift")
    rows = [
        {
            "row_id": "R9-CLAIM-01",
            "supported_claim": supported,
            "not_supported_claim": not_supported[0],
            "limitation": (
                "Persistent update and held-out task schedule change together in the "
                "frozen design; causal attribution to the update alone remains on HOLD."
            ),
        },
        {
            "row_id": "R9-CLAIM-02",
            "supported_claim": "",
            "not_supported_claim": not_supported[1],
            "limitation": (
                "Evidence is limited to four selected states, Qwen3-8B, BrowserART, "
                "HarmBench, three branches, and a three-update horizon."
            ),
        },
        {
            "row_id": "R9-CLAIM-03",
            "supported_claim": "",
            "not_supported_claim": not_supported[2],
            "limitation": (
                "The 8/12 branch event fraction is descriptive; common-random-number "
                "branches and the small frozen support set are not treated as IID population draws."
            ),
        },
        {
            "row_id": "R9-CLAIM-04",
            "supported_claim": "",
            "not_supported_claim": not_supported[3],
            "limitation": (
                "HarmBench is the frozen benchmark evaluator, not a noiseless safety oracle."
            ),
        },
    ]
    table = {
        "schema_version": SCHEMA_VERSION,
        "status": "READY_AGENT_SAFETY_R9_PAPER_CLAIM_TABLE",
        "candidate_id": (receipt.get("identity") or {}).get("candidate_id"),
        "receipt_ref": receipt_ref,
        "columns": ["supported_claim", "not_supported_claim", "limitation"],
        "rows": rows,
        "evidence_summary": {
            "static_qualification": "12/12 completed predictions were non-violations",
            "future_episode_violations": "11/36",
            "future_branch_first_violation_events": "8/12",
            "states_with_first_violation": "3/4",
        },
        "claim_is_narrow_not_causal": True,
        "scientific_authority": False,
    }
    table["table_sha256"] = canonical_sha256(
        {key: table[key] for key in ("schema_version", "candidate_id", "receipt_ref", "rows")}
    )
    return table


def build_memory_graph_inputs(
    receipt: dict[str, Any], *, receipt_ref: str, claim_table_sha256: str
) -> dict[str, Any]:
    supported = str((receipt.get("claim_scope") or {}).get("supported") or "")
    supported_claim = {
        "claim_id": SUPPORTED_CLAIM_ID,
        "claim_text": supported,
        "claim_type": "predictive_sufficiency",
        "scientific_object": "persistent-state-agent-safety",
        "mechanism": "current-safety-panel-to-future-first-violation",
        "scope": {
            "runtime": "R9 SecureClaw / Qwen3-8B",
            "benchmark": "BrowserART",
            "evaluator": "HarmBench",
            "states": 4,
            "branches": 12,
            "horizon": 3,
        },
        "adjudication_status": "SUPPORTED_NARROWLY",
        "trace_complete": True,
        "evidence_ids": [receipt_ref],
        "paper_claim_table_sha256": claim_table_sha256,
        "scientific_authority": False,
    }
    causal_hold_claim = {
        "claim_id": CAUSAL_HOLD_CLAIM_ID,
        "claim_text": "Persistent update alone causally produced the observed future violations.",
        "claim_type": "causal_attribution",
        "scientific_object": "persistent-state-agent-safety",
        "mechanism": "persistent-update-effect",
        "scope": {
            "runtime": "R9 SecureClaw / Qwen3-8B",
            "heldout_schedule_varies_with_update": True,
        },
        "adjudication_status": "HOLD_METHOD_IDENTIFICATION",
        "trace_complete": True,
        "evidence_ids": [receipt_ref],
        "scientific_authority": False,
    }
    hold_memory = {
        "memory_id": "MEM-HOLD-AGENT-SAFETY-R9-UPDATE-VS-SCHEDULE",
        "kind": "HOLD",
        "title": "R9 persistent-update causal attribution remains unidentified",
        "summary": (
            "The completed R9 run supports failure of a deterministic static-pass "
            "guarantee, but does not isolate persistent update from held-out schedule change."
        ),
        "candidate_id": CAUSAL_HOLD_CLAIM_ID,
        "scope": {
            "scientific_object": "persistent-state-agent-safety",
            "mechanism": "persistent-update-effect",
            "claim_type": "causal_attribution",
        },
        "scientific_object": "persistent-state-agent-safety",
        "mechanism": "persistent-update-effect",
        "claim_type": "causal_attribution",
        "affected_layer": "method",
        "memory_class": "METHOD_IDENTIFICATION_HOLD",
        "durability_class": "scientific",
        "prompt_eligible": True,
        "search_closure_certified": False,
        "scientific_dead_end_certified": False,
        "principle_update_allowed": False,
        "reopen_condition": REOPEN_CONDITION,
        "opposite_search_seed": "",
        "reusable_precheck": (
            "Do not interpret future hazards as update-caused unless update and held-out "
            "schedule effects are separately identified under a pre-registered comparison."
        ),
        "source_refs": [receipt_ref],
        "source_artifact": "agent-safety-r9-future-evidence-adjudication",
        "reuse_effectiveness": {},
        "scientific_authority": False,
    }
    bundle = {
        "schema_version": SCHEMA_VERSION,
        "status": "READY_AGENT_SAFETY_R9_MEMORY_GRAPH_2_1_INPUTS",
        "receipt_ref": receipt_ref,
        "claim_table_sha256": claim_table_sha256,
        "claim_ledger": [supported_claim, causal_hold_claim],
        "supplemental_memory_entries": [hold_memory],
        "reopen_condition": {
            "condition_id": "REOPEN-AGENT-SAFETY-R9-SEPARATE-UPDATE-FROM-SCHEDULE",
            "claim_id": CAUSAL_HOLD_CLAIM_ID,
            "affected_layer": "method",
            "condition": REOPEN_CONDITION,
            "automatic_reopen": False,
            "new_behavior_execution_authorized": False,
            "scientific_authority": False,
        },
        "summary": {
            "claims": 2,
            "supported_narrowly": 1,
            "method_holds": 1,
            "reopen_conditions": 1,
            "scientific_closures": 0,
            "principle_updates": 0,
        },
        "scientific_authority": False,
    }
    bundle["bundle_sha256"] = canonical_sha256(
        {
            key: bundle[key]
            for key in (
                "schema_version",
                "receipt_ref",
                "claim_table_sha256",
                "claim_ledger",
                "supplemental_memory_entries",
                "reopen_condition",
            )
        }
    )
    return bundle


def compile_memory_graph_inputs(
    receipt_path: Path = DEFAULT_RECEIPT,
) -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = load_receipt(receipt_path)
    receipt_ref = _receipt_ref(receipt_path, receipt)
    table = build_paper_claim_table(receipt, receipt_ref=receipt_ref)
    bundle = build_memory_graph_inputs(
        receipt,
        receipt_ref=receipt_ref,
        claim_table_sha256=table["table_sha256"],
    )
    return table, bundle


def _tex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in value)


def render_claim_table_tex(table: dict[str, Any]) -> str:
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\begin{tabular}{p{0.29\textwidth}p{0.29\textwidth}p{0.34\textwidth}}",
        r"\toprule",
        r"Supported claim & Not supported claim & Limitation \\",
        r"\midrule",
    ]
    for row in table["rows"]:
        values = [
            _tex_escape(str(row.get("supported_claim") or "---")),
            _tex_escape(str(row.get("not_supported_claim") or "---")),
            _tex_escape(str(row.get("limitation") or "---")),
        ]
        lines.append(" & ".join(values) + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            (
                r"\caption{Claim boundary for the frozen R9 future-hazard evidence. "
                r"The table is descriptive and does not assert update-only causality.}"
            ),
            r"\label{tab:r9-future-hazard-claim-boundary}",
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    table: dict[str, Any],
    bundle: dict[str, Any],
    *,
    claim_table_json: Path = DEFAULT_CLAIM_TABLE_JSON,
    claim_table_tex: Path = DEFAULT_CLAIM_TABLE_TEX,
    memory_bundle_json: Path = DEFAULT_MEMORY_BUNDLE,
) -> None:
    for path in (claim_table_json, claim_table_tex, memory_bundle_json):
        path.parent.mkdir(parents=True, exist_ok=True)
    claim_table_json.write_text(
        json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    claim_table_tex.write_text(render_claim_table_tex(table), encoding="utf-8")
    memory_bundle_json.write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", default=str(DEFAULT_RECEIPT))
    parser.add_argument("--claim-table-json", default=str(DEFAULT_CLAIM_TABLE_JSON))
    parser.add_argument("--claim-table-tex", default=str(DEFAULT_CLAIM_TABLE_TEX))
    parser.add_argument("--memory-bundle-json", default=str(DEFAULT_MEMORY_BUNDLE))
    args = parser.parse_args()
    table, bundle = compile_memory_graph_inputs(Path(args.receipt))
    write_outputs(
        table,
        bundle,
        claim_table_json=Path(args.claim_table_json),
        claim_table_tex=Path(args.claim_table_tex),
        memory_bundle_json=Path(args.memory_bundle_json),
    )
    print(
        json.dumps(
            {
                "status": bundle["status"],
                "claim_table_sha256": table["table_sha256"],
                "bundle_sha256": bundle["bundle_sha256"],
                "reopen_condition": bundle["reopen_condition"]["condition"],
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
