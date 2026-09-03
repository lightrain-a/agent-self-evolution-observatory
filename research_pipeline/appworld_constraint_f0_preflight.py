from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_qwen_model_prereg import (
    ALLOWED_ALIAS,
    MANIFEST as MODEL_ADDENDUM_MANIFEST,
    OUTPUT as MODEL_ADDENDUM,
    PROVIDER_ID,
    REQUESTED_MODEL,
    safe_provider_summary,
)

OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"
GENERATED_AT = "2026-09-01T15:35:00+08:00"
ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
FAMILY_MANIFEST = (
    GENERATED / "agent-constraint-externality-matched-family-manifest-20260831.json"
)
COMPILER_QUALIFICATION = (
    GENERATED / "agent-constraint-externality-appworld-compiler-qualification-20260831.json"
)
COMPILER_MANIFEST = (
    GENERATED / "agent-constraint-externality-appworld-compiler-manifest-20260831.json"
)
M1_QUALIFICATION = (
    GENERATED / "agent-constraint-externality-m1-runner-qualification-v1-20260901.json"
)
M1_MANIFEST = (
    GENERATED / "agent-constraint-externality-m1-runner-qualification-v1-manifest-20260901.json"
)
CAPABILITY_RESULT = (
    GENERATED / "agent-constraint-externality-qwen-capability-result-20260901.json"
)
CAPABILITY_RESULT_MANIFEST = (
    GENERATED / "agent-constraint-externality-qwen-capability-manifest-20260901.json"
)
CAPABILITY_MODEL_SNAPSHOT = (
    GENERATED / "agent-constraint-externality-qwen-provider-model-snapshot-20260901.json"
)
CAPABILITY_CONTINUATION_RESULT = (
    GENERATED / "agent-constraint-externality-qwen-capability-continuation-r1-result-20260901.json"
)
CAPABILITY_A1_RESULT = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-result-a1-20260901.json"
)
CAPABILITY_A1_ADDENDUM = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-addendum-a1-20260901.json"
)
CAPABILITY_A1_SNAPSHOT = (
    GENERATED / "agent-constraint-externality-qwen37plus-provider-snapshot-a1-20260901.json"
)
CAPABILITY_A1_MANIFEST = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-a1-manifest-20260901.json"
)
CAPABILITY_SUBSTRATE_VOID = (
    GENERATED / "agent-constraint-externality-capability-substrate-invalid-void-r1-20260901.json"
)
CAPABILITY_SUBSTRATE_QUALIFICATION = (
    GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r1-20260901.json"
)
CAPABILITY_R2_CONTRACT = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-r2-contract-20260901.json"
)
CAPABILITY_R2_RESULT = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-result-r2-20260901.json"
)
CAPABILITY_SUBSTRATE_VOID_R2 = (
    GENERATED / "agent-constraint-externality-capability-substrate-invalid-void-r2-20260902.json"
)
CAPABILITY_SUBSTRATE_QUALIFICATION_R2 = (
    GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r2-20260902.json"
)
CAPABILITY_R3_CONTRACT = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-r3-contract-20260902.json"
)
CAPABILITY_R3_RESULT = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-result-r3-20260902.json"
)
CAPABILITY_R3_PARTIAL_CONTRACT = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-r3-partial-contract-20260902.json"
)
CAPABILITY_R3_PARTIAL_RESULT = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-result-r3-partial-20260902.json"
)
CAPABILITY_R2_FG_V2_REVALIDATION = (
    GENERATED / "agent-constraint-externality-qwen37plus-r2-fg-v2-revalidation-20260902.json"
)
CAPABILITY_SUBSTRATE_V2_CONTRACT = (
    GENERATED / "agent-constraint-externality-capability-substrate-v2-contract-20260902.json"
)
CAPABILITY_SUBSTRATE_V2_BUNDLE = (
    GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v2-20260902.bundle"
)
CAPABILITY_R2_ROOT_CAUSE_AUDIT = (
    GENERATED / "agent-constraint-externality-capability-r2-root-cause-audit-20260902.json"
)
CAPABILITY_R3_PARTIAL_VOID = (
    GENERATED / "agent-constraint-externality-capability-r3-partial-void-r1-20260902.json"
)
CAPABILITY_SUBSTRATE_V3_CONTRACT = (
    GENERATED / "agent-constraint-externality-capability-substrate-v3-contract-20260902.json"
)
CAPABILITY_SUBSTRATE_QUALIFICATION_R3 = (
    GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r3-20260902.json"
)
CAPABILITY_SUBSTRATE_V3_BUNDLE = (
    GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v3-20260902.bundle"
)
CAPABILITY_SUBSTRATE_V4_CONTRACT = (
    GENERATED / "agent-constraint-externality-capability-substrate-v4-contract-20260902.json"
)
CAPABILITY_SUBSTRATE_QUALIFICATION_R4 = (
    GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r4-20260902.json"
)
CAPABILITY_SUBSTRATE_V4_BUNDLE = (
    GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
)
CAPABILITY_R5_PARTIAL_CONTRACT = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-r5-partial-contract-20260902.json"
)
CAPABILITY_R5_PARTIAL_RESULT = (
    GENERATED / "agent-constraint-externality-qwen37plus-capability-result-r5-partial-20260902.json"
)
CODINGPLAN_QWEN38_Q0 = (
    GENERATED / "agent-constraint-externality-codingplan-mcp-q0-qualification-20260902.json"
)
CODINGPLAN_QWEN38_Q1 = (
    GENERATED / "agent-constraint-externality-codingplan-appworld-mcp-q1-predispatch-20260902.json"
)
CODINGPLAN_QWEN38_CONTRACT = (
    GENERATED / "agent-constraint-externality-codingplan-qwen38-capability-a0-contract-20260902.json"
)
CODINGPLAN_QWEN38_MANIFEST = (
    GENERATED / "agent-constraint-externality-codingplan-qwen38-capability-a0-manifest-20260902.json"
)
CODINGPLAN_QWEN38_RESULT = (
    GENERATED / "agent-constraint-externality-codingplan-qwen38-capability-a0-result-20260902.json"
)
CODINGPLAN_QWEN38_CLOSEOUT = (
    GENERATED / "agent-constraint-externality-codingplan-qwen38-capability-a0-closeout-20260902.json"
)
CODINGPLAN_DEEPSEEK_RESULT = (
    GENERATED / "agent-constraint-externality-codingplan-deepseek-live-capability-b0-result-20260903.json"
)
CODINGPLAN_DEEPSEEK_CLOSEOUT = (
    GENERATED / "agent-constraint-externality-codingplan-deepseek-live-capability-b0-closeout-20260903.json"
)
CODINGPLAN_CATALOG_B1 = (
    GENERATED / "agent-constraint-externality-codingplan-catalog-b1-20260903.json"
)
BACKBONE_SEARCH_STATE_B1 = (
    GENERATED / "agent-constraint-externality-capability-backbone-search-state-b1-20260903.json"
)
CODINGPLAN_GLM52_RESULT = (
    GENERATED / "agent-constraint-externality-codingplan-glm52-capability-b1-result-20260903.json"
)
CODINGPLAN_GLM52_CLOSEOUT = (
    GENERATED / "agent-constraint-externality-codingplan-glm52-capability-b1-closeout-20260903.json"
)
BACKBONE_SEARCH_STATE_B2 = (
    GENERATED / "agent-constraint-externality-capability-backbone-search-state-b2-20260903.json"
)
CODINGPLAN_MIMO25_RESULT = (
    GENERATED / "agent-constraint-externality-codingplan-mimo25-capability-b2-result-20260903.json"
)
CODINGPLAN_MIMO25_CLOSEOUT = (
    GENERATED / "agent-constraint-externality-codingplan-mimo25-capability-b2-closeout-20260903.json"
)
BACKBONE_SEARCH_STATE_B3 = (
    GENERATED / "agent-constraint-externality-capability-backbone-search-state-b3-20260903.json"
)
CODINGPLAN_MIMO25PRO_RESULT = (
    GENERATED / "agent-constraint-externality-codingplan-mimo25pro-capability-b3-result-20260903.json"
)
CODINGPLAN_MIMO25PRO_CLOSEOUT = (
    GENERATED / "agent-constraint-externality-codingplan-mimo25pro-capability-b3-closeout-20260903.json"
)
FINAL_BACKBONE_SELECTION = (
    GENERATED / "agent-constraint-externality-capability-backbone-selection-final-20260903.json"
)
F0_HUMAN_AUTHORIZATION = (
    GENERATED / "agent-constraint-externality-f0-human-authorization-20260903.json"
)
F0_TRANSPORT_ADDENDUM = (
    GENERATED / "agent-constraint-externality-f0-mimo25pro-transport-addendum-20260903.json"
)
F0_MIMO25PRO_Q1 = (
    GENERATED / "agent-constraint-externality-f0-mimo25pro-mcp-q1-predispatch-20260903.json"
)
F0_MIMO25PRO_SOURCE_CONTRACT = (
    GENERATED / "agent-constraint-externality-f0-mimo25pro-source-contract-20260903.json"
)
F0_REPAIRS_MANIFEST = (
    GENERATED / "agent-constraint-externality-f0-repairs-manifest-mimo25pro-20260903.json"
)
F0_ADJUDICATION = (
    GENERATED / "agent-constraint-externality-f0-adjudication-mimo25pro-20260903.json"
)
F0_SOURCE_CLOSEOUT = (
    GENERATED / "agent-constraint-externality-f0-source-closeout-mimo25pro-20260903.json"
)
F0_UPTAKE_ROOT_CAUSE = (
    GENERATED / "agent-constraint-externality-f0-uptake-root-cause-20260903.json"
)
F0_R1_PROPOSAL = (
    GENERATED / "agent-constraint-externality-f0-r1-source-failure-qualification-proposal-20260903.json"
)
SQ0_STATIC_CONTRACT = GENERATED / "agent-constraint-externality-sq0-target-challenge-v1-contract-20260903.json"
SQ0_STATIC_QUALIFICATION = GENERATED / "agent-constraint-externality-sq0-target-challenge-v1-static-qualification-20260903.json"
SQ0_HUMAN_AUTHORIZATION = GENERATED / "agent-constraint-externality-sq0-human-authorization-20260903.json"
SQ0_MIMO25PRO_Q1 = GENERATED / "agent-constraint-externality-sq0-mimo25pro-mcp-q1-predispatch-20260903.json"
SQ0_EXECUTION_CONTRACT = GENERATED / "agent-constraint-externality-sq0-mimo25pro-execution-contract-v1-20260903.json"
SQ0_V1_RESULT = GENERATED / "agent-constraint-externality-sq0-mimo25pro-result-v1-20260903.json"
SQ0_V1_CLOSEOUT = GENERATED / "agent-constraint-externality-sq0-v1-closeout-20260903.json"
SQ0_V2_STATIC_CONTRACT = GENERATED / "agent-constraint-externality-sq0-target-challenge-v2-contract-20260903.json"
SQ0_V2_STATIC_QUALIFICATION = GENERATED / "agent-constraint-externality-sq0-target-challenge-v2-static-qualification-20260903.json"
SQ0_V2_HUMAN_AUTHORIZATION = GENERATED / "agent-constraint-externality-sq0-v2-human-authorization-20260903.json"
SQ0_V2_MIMO25PRO_Q1 = GENERATED / "agent-constraint-externality-sq0-v2-mimo25pro-mcp-q1-predispatch-20260903.json"
SQ0_V2_EXECUTION_CONTRACT = GENERATED / "agent-constraint-externality-sq0-v2-mimo25pro-execution-contract-20260903.json"
SQ0_V2_VOID = GENERATED / "agent-constraint-externality-sq0-v2-harness-contamination-void-20260903.json"
SQ0_V2R1_STATIC_CONTRACT = GENERATED / "agent-constraint-externality-sq0-v2r1-target-challenge-contract-20260903.json"
SQ0_V2R1_STATIC_QUALIFICATION = GENERATED / "agent-constraint-externality-sq0-v2r1-static-qualification-20260903.json"
SQ0_V2R1_TRANSPORT_CONTRACT = GENERATED / "agent-constraint-externality-sq0-v2r1-transport-contract-20260903.json"
SQ0_V2R1_TRANSPORT_RESULT = GENERATED / "agent-constraint-externality-sq0-v2r1-transport-result-20260903.json"
SQ0_V2R1_HUMAN_AUTHORIZATION = GENERATED / "agent-constraint-externality-sq0-v2r1-human-authorization-20260903.json"
SQ0_V2R1_MIMO25PRO_Q1 = GENERATED / "agent-constraint-externality-sq0-v2r1-mimo25pro-mcp-q1-predispatch-20260903.json"
SQ0_V2R1_EXECUTION_CONTRACT = GENERATED / "agent-constraint-externality-sq0-v2r1-mimo25pro-execution-contract-20260903.json"
SQ0_V2R1_RESULT = GENERATED / "agent-constraint-externality-sq0-v2r1-mimo25pro-result-20260903.json"
SQ0_V2R1_CLOSEOUT = GENERATED / "agent-constraint-externality-sq0-v2r1-closeout-20260903.json"
SQ0_V2R1_ROOT_CAUSE = GENERATED / "agent-constraint-externality-sq0-v2r1-root-cause-20260903.json"
SQ0_V3_STATIC_CONTRACT = GENERATED / "agent-constraint-externality-sq0-v3-target-challenge-contract-20260903.json"
SQ0_V3_STATIC_QUALIFICATION = GENERATED / "agent-constraint-externality-sq0-v3-static-qualification-20260903.json"
SQ0_V3_HUMAN_AUTHORIZATION = GENERATED / "agent-constraint-externality-sq0-v3-human-authorization-20260903.json"
SQ0_V3_MIMO25PRO_Q1 = GENERATED / "agent-constraint-externality-sq0-v3-mimo25pro-mcp-q1-predispatch-20260903.json"
SQ0_V3_EXECUTION_CONTRACT = GENERATED / "agent-constraint-externality-sq0-v3-mimo25pro-execution-contract-20260903.json"
SQ0_V3_RESULT = GENERATED / "agent-constraint-externality-sq0-v3-mimo25pro-result-20260903.json"
CAPABILITY_FAMILIES = (
    "ACE-FG-05", "ACE-FG-06", "ACE-TNF-05", "ACE-TNF-06"
)
F0_FAMILIES = (
    "ACE-FG-01", "ACE-FG-02", "ACE-FG-03", "ACE-FG-04",
    "ACE-TNF-01", "ACE-TNF-02", "ACE-TNF-03", "ACE-TNF-04",
)
MODEL_SELECTION_ORDER = (REQUESTED_MODEL,)
SEEDS = (1201, 1202, 1203)
ARMS = ("INDEPENDENT", "LOW", "HIGH")
BRANCHES = ("NO_UPDATE", "UPDATE")
CAPABILITY_STATUSES = {
    "CAPABILITY_CALIBRATION_PASS",
    "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP",
    "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP",
    "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP",
}


class PreflightError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_capability_result(payload: dict[str, Any]) -> str | None:
    if not payload:
        return None
    if payload.get("object_id") != OBJECT_ID:
        raise PreflightError("Capability result object identity mismatch.")
    status = payload.get("status")
    if status not in CAPABILITY_STATUSES:
        raise PreflightError("Capability result status is not frozen.")
    content_sha256 = payload.get("content_sha256")
    unhashed = {key: value for key, value in payload.items() if key != "content_sha256"}
    if content_sha256 != digest(unhashed):
        raise PreflightError("Capability result content hash mismatch.")
    f0_authorized = bool(payload.get("authority", {}).get("f0"))
    if status != "CAPABILITY_CALIBRATION_PASS" and f0_authorized:
        raise PreflightError("A stopped capability result cannot authorize F0.")
    if status != "CAPABILITY_CALIBRATION_PASS" and payload.get(
        "scientific_outcomes_observed"
    ) != 0:
        raise PreflightError("Stopped capability result exposed scientific outcomes.")
    return str(status)


def validate_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    families = read_json(FAMILY_MANIFEST)
    qualification = read_json(COMPILER_QUALIFICATION)
    if families["object_id"] != OBJECT_ID or qualification["object_id"] != OBJECT_ID:
        raise PreflightError("Scientific object identity mismatch.")
    if qualification["verdict"] != "PRE_F0_5_PASS":
        raise PreflightError("F0 preflight requires PRE_F0_5_PASS.")
    if not all(qualification["pass_conditions"].values()):
        raise PreflightError("A compiler pass condition is false.")
    available = {row["family_id"]: row for row in families["families"]}
    selected = set(CAPABILITY_FAMILIES) | set(F0_FAMILIES)
    if set(CAPABILITY_FAMILIES) & set(F0_FAMILIES):
        raise PreflightError("Capability and decisive splits overlap.")
    if selected != set(available):
        raise PreflightError("Outcome-blind split must partition all compiled families.")
    if MODEL_SELECTION_ORDER != (REQUESTED_MODEL,):
        raise PreflightError("Exactly one Qwen candidate must remain preregistered.")
    addendum = read_json(MODEL_ADDENDUM)
    if addendum["status"] != "QWEN_MODEL_PREREG_ADDENDUM_A0_PASS":
        raise PreflightError("Qwen model prereg addendum is not qualified.")
    return families, qualification


def build_artifacts() -> dict[str, dict[str, Any]]:
    families, qualification = validate_inputs()
    safe_provider = safe_provider_summary()
    provider_ready = bool(safe_provider["configured"])
    m1 = read_json(M1_QUALIFICATION) if M1_QUALIFICATION.is_file() else {}
    m1_pass = m1.get("status") == "M1_RUNNER_QUALIFICATION_PASS"
    substrate_void = (
        read_json(CAPABILITY_SUBSTRATE_VOID)
        if CAPABILITY_SUBSTRATE_VOID.is_file()
        else {}
    )
    substrate_qualification = (
        read_json(CAPABILITY_SUBSTRATE_QUALIFICATION)
        if CAPABILITY_SUBSTRATE_QUALIFICATION.is_file()
        else {}
    )
    r2_contract = (
        read_json(CAPABILITY_R2_CONTRACT)
        if CAPABILITY_R2_CONTRACT.is_file()
        else {}
    )
    substrate_void_active = (
        substrate_void.get("status") == "CAPABILITY_RESULTS_VOID_SUBSTRATE_INVALID"
    )
    substrate_recovery_pass = (
        substrate_qualification.get("status")
        == "CAPABILITY_SUBSTRATE_RECOVERY_QUALIFICATION_PASS"
    )
    r2_authorized = (
        r2_contract.get("status")
        == "QWEN37PLUS_CAPABILITY_R2_AUTHORIZED_AFTER_SUBSTRATE_VOID"
    )
    substrate_void_r2 = (
        read_json(CAPABILITY_SUBSTRATE_VOID_R2)
        if CAPABILITY_SUBSTRATE_VOID_R2.is_file()
        else {}
    )
    substrate_qualification_r2 = (
        read_json(CAPABILITY_SUBSTRATE_QUALIFICATION_R2)
        if CAPABILITY_SUBSTRATE_QUALIFICATION_R2.is_file()
        else {}
    )
    r3_contract = (
        read_json(CAPABILITY_R3_CONTRACT)
        if CAPABILITY_R3_CONTRACT.is_file()
        else {}
    )
    substrate_v2_contract = (
        read_json(CAPABILITY_SUBSTRATE_V2_CONTRACT)
        if CAPABILITY_SUBSTRATE_V2_CONTRACT.is_file()
        else {}
    )
    r2_void_active = (
        substrate_void_r2.get("status")
        == "QWEN37PLUS_R2_VOID_SUBSTRATE_DISCOVERABILITY_INVALID"
    )
    substrate_v2_recovery_pass = (
        substrate_qualification_r2.get("status")
        == "CAPABILITY_SUBSTRATE_V2_PUBLIC_REACHABILITY_PASS"
        and substrate_v2_contract.get("status")
        == "CAPABILITY_SUBSTRATE_V2_STATIC_REPAIR_READY"
    )
    r3_authorized = (
        r3_contract.get("status")
        == "QWEN37PLUS_CAPABILITY_R3_AUTHORIZED_AFTER_SUBSTRATE_V2"
    )
    r3_partial_contract = (
        read_json(CAPABILITY_R3_PARTIAL_CONTRACT)
        if CAPABILITY_R3_PARTIAL_CONTRACT.is_file()
        else {}
    )
    r3_partial_authorized = (
        r3_partial_contract.get("status")
        == "QWEN37PLUS_CAPABILITY_R3_PARTIAL_AUTHORIZED"
        and r3_partial_contract.get("rerun_unit_count") == 4
        and r3_partial_contract.get("preserved_unit_count") == 4
    )
    r3_partial_void = (
        read_json(CAPABILITY_R3_PARTIAL_VOID)
        if CAPABILITY_R3_PARTIAL_VOID.is_file()
        else {}
    )
    r3_partial_void_active = (
        r3_partial_void.get("status")
        == "QWEN37PLUS_R3_PARTIAL_VOID_SUBSTRATE_FILESYSTEM_FILENAME_INVALID"
    )
    substrate_v4_contract = (
        read_json(CAPABILITY_SUBSTRATE_V4_CONTRACT)
        if CAPABILITY_SUBSTRATE_V4_CONTRACT.is_file()
        else {}
    )
    substrate_qualification_r4 = (
        read_json(CAPABILITY_SUBSTRATE_QUALIFICATION_R4)
        if CAPABILITY_SUBSTRATE_QUALIFICATION_R4.is_file()
        else {}
    )
    substrate_v4_recovery_pass = (
        substrate_v4_contract.get("status") == "CAPABILITY_SUBSTRATE_V4_TOOL_BUDGET_QUALIFIED"
        and substrate_v4_contract.get("tool_budget_rule", {}).get("resolved_tool_call_cap") == 16
        and substrate_qualification_r4.get("status")
        == "CAPABILITY_SUBSTRATE_V4_PUBLIC_REACHABILITY_WITH_HEADROOM_PASS"
        and substrate_qualification_r4.get("tool_call_cap") == 16
    )
    r5_partial_contract = (
        read_json(CAPABILITY_R5_PARTIAL_CONTRACT)
        if CAPABILITY_R5_PARTIAL_CONTRACT.is_file()
        else {}
    )
    r5_partial_authorized = (
        r5_partial_contract.get("status")
        == "QWEN37PLUS_CAPABILITY_R5_PARTIAL_TNF_ONLY_AUTHORIZED"
        and r5_partial_contract.get("rerun_tnf_measurements") == 4
        and r5_partial_contract.get("preserve_fg_measurements") == 4
        and r5_partial_contract.get("tool_call_cap") == 16
        and r5_partial_contract.get("model_switch") is False
        and r5_partial_contract.get("replacement") is False
    )
    codingplan_result = (
        read_json(CODINGPLAN_QWEN38_RESULT) if CODINGPLAN_QWEN38_RESULT.is_file() else {}
    )
    codingplan_status = validate_capability_result(codingplan_result)
    codingplan_closeout = (
        read_json(CODINGPLAN_QWEN38_CLOSEOUT) if CODINGPLAN_QWEN38_CLOSEOUT.is_file() else {}
    )
    codingplan_closeout_valid = False
    if codingplan_closeout:
        if codingplan_closeout.get("object_id") != OBJECT_ID:
            raise PreflightError("CodingPlan closeout object identity mismatch.")
        claimed = codingplan_closeout.get("content_sha256")
        unsigned = dict(codingplan_closeout)
        unsigned.pop("content_sha256", None)
        if claimed != digest(unsigned):
            raise PreflightError("CodingPlan closeout content hash mismatch.")
        if codingplan_closeout.get("status") != "CODINGPLAN_QWEN38_CAPABILITY_A0_CLOSEOUT_CEILING_STOP":
            raise PreflightError("CodingPlan closeout is not at its frozen ceiling stop.")
        if codingplan_closeout.get("scientific_verdict") != codingplan_status:
            raise PreflightError("CodingPlan closeout/result verdict mismatch.")
        if codingplan_closeout.get("authority", {}).get("f0") is not False:
            raise PreflightError("CodingPlan closeout cannot authorize F0.")
        codingplan_closeout_valid = True

    deepseek_result = (
        read_json(CODINGPLAN_DEEPSEEK_RESULT)
        if CODINGPLAN_DEEPSEEK_RESULT.is_file()
        else {}
    )
    deepseek_status = validate_capability_result(deepseek_result)
    deepseek_closeout = (
        read_json(CODINGPLAN_DEEPSEEK_CLOSEOUT)
        if CODINGPLAN_DEEPSEEK_CLOSEOUT.is_file()
        else {}
    )
    backbone_search_state = (
        read_json(BACKBONE_SEARCH_STATE_B1)
        if BACKBONE_SEARCH_STATE_B1.is_file()
        else {}
    )
    codingplan_catalog_b1 = (
        read_json(CODINGPLAN_CATALOG_B1)
        if CODINGPLAN_CATALOG_B1.is_file()
        else {}
    )
    backbone_search_active = False
    if backbone_search_state:
        for label, payload in (
            ("DeepSeek closeout", deepseek_closeout),
            ("CodingPlan catalog B1", codingplan_catalog_b1),
            ("backbone search state B1", backbone_search_state),
        ):
            if payload.get("object_id") != OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            claimed = payload.get("content_sha256")
            unsigned = dict(payload)
            unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError(f"{label} content hash mismatch.")
        if deepseek_status != "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP":
            raise PreflightError("DeepSeek B0 result is not at its frozen floor stop.")
        if deepseek_closeout.get("status") != "CODINGPLAN_DEEPSEEK_LIVE_B0_FLOOR_CLOSEOUT":
            raise PreflightError("DeepSeek B0 closeout status mismatch.")
        if deepseek_closeout.get("verdict") != deepseek_status:
            raise PreflightError("DeepSeek B0 result/closeout verdict mismatch.")
        if codingplan_catalog_b1.get("status") != "CODINGPLAN_ACCOUNT_CATALOG_REFRESH_PASS_ZERO_MODEL_REQUESTS":
            raise PreflightError("CodingPlan catalog B1 is not a zero-request refresh pass.")
        if codingplan_catalog_b1.get("codingplan_model_request_delta") != 0:
            raise PreflightError("CodingPlan catalog B1 consumed model requests.")
        if backbone_search_state.get("status") != "CAPABILITY_BACKBONE_SEARCH_CONTINUE_GLM52_NEXT":
            raise PreflightError("Backbone search B1 state is not frozen to GLM-5.2 next.")
        if backbone_search_state.get("remaining_frozen_order") != [
            "GLM-5.2", "mimo-v2.5", "mimo-v2.5-pro"
        ]:
            raise PreflightError("Backbone search candidate order drifted.")
        if backbone_search_state.get("authority", {}).get("f0") is not False:
            raise PreflightError("Backbone search state cannot authorize F0.")
        backbone_search_active = True

    glm52_result = (
        read_json(CODINGPLAN_GLM52_RESULT)
        if CODINGPLAN_GLM52_RESULT.is_file()
        else {}
    )
    glm52_status = validate_capability_result(glm52_result)
    glm52_closeout = (
        read_json(CODINGPLAN_GLM52_CLOSEOUT)
        if CODINGPLAN_GLM52_CLOSEOUT.is_file()
        else {}
    )
    backbone_search_state_b2 = (
        read_json(BACKBONE_SEARCH_STATE_B2)
        if BACKBONE_SEARCH_STATE_B2.is_file()
        else {}
    )
    backbone_search_b2_active = False
    if backbone_search_state_b2:
        for label, payload in (
            ("GLM-5.2 closeout", glm52_closeout),
            ("backbone search state B2", backbone_search_state_b2),
        ):
            if payload.get("object_id") != OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            claimed = payload.get("content_sha256")
            unsigned = dict(payload)
            unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError(f"{label} content hash mismatch.")
        if glm52_status != "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP":
            raise PreflightError("GLM-5.2 B1 result is not at its frozen ceiling stop.")
        if glm52_closeout.get("status") != "CODINGPLAN_GLM52_B1_CEILING_CLOSEOUT":
            raise PreflightError("GLM-5.2 B1 closeout status mismatch.")
        if glm52_closeout.get("verdict") != glm52_status:
            raise PreflightError("GLM-5.2 result/closeout verdict mismatch.")
        if backbone_search_state_b2.get("status") != "CAPABILITY_BACKBONE_SEARCH_CONTINUE_MIMO25_NEXT":
            raise PreflightError("Backbone search B2 state is not frozen to mimo-v2.5 next.")
        if backbone_search_state_b2.get("remaining_frozen_order") != [
            "mimo-v2.5", "mimo-v2.5-pro"
        ]:
            raise PreflightError("Backbone search B2 candidate order drifted.")
        if backbone_search_state_b2.get("authority", {}).get("f0") is not False:
            raise PreflightError("Backbone search B2 state cannot authorize F0.")
        backbone_search_b2_active = True

    mimo25_result = (
        read_json(CODINGPLAN_MIMO25_RESULT)
        if CODINGPLAN_MIMO25_RESULT.is_file()
        else {}
    )
    mimo25_status = validate_capability_result(mimo25_result)
    mimo25_closeout = (
        read_json(CODINGPLAN_MIMO25_CLOSEOUT)
        if CODINGPLAN_MIMO25_CLOSEOUT.is_file()
        else {}
    )
    backbone_search_state_b3 = (
        read_json(BACKBONE_SEARCH_STATE_B3)
        if BACKBONE_SEARCH_STATE_B3.is_file()
        else {}
    )
    backbone_search_b3_active = False
    if backbone_search_state_b3:
        for label, payload in (
            ("mimo-v2.5 closeout", mimo25_closeout),
            ("backbone search state B3", backbone_search_state_b3),
        ):
            if payload.get("object_id") != OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            claimed = payload.get("content_sha256")
            unsigned = dict(payload)
            unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError(f"{label} content hash mismatch.")
        if mimo25_status != "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP":
            raise PreflightError("mimo-v2.5 B2 result is not at its frozen ceiling stop.")
        if mimo25_closeout.get("status") != "CODINGPLAN_MIMO25_B2_CEILING_CLOSEOUT":
            raise PreflightError("mimo-v2.5 B2 closeout status mismatch.")
        if mimo25_closeout.get("verdict") != mimo25_status:
            raise PreflightError("mimo-v2.5 result/closeout verdict mismatch.")
        if backbone_search_state_b3.get("status") != "CAPABILITY_BACKBONE_SEARCH_CONTINUE_MIMO25PRO_NEXT":
            raise PreflightError("Backbone search B3 state is not frozen to mimo-v2.5-pro next.")
        if backbone_search_state_b3.get("remaining_frozen_order") != ["mimo-v2.5-pro"]:
            raise PreflightError("Backbone search B3 candidate order drifted.")
        if backbone_search_state_b3.get("authority", {}).get("f0") is not False:
            raise PreflightError("Backbone search B3 state cannot authorize F0.")
        backbone_search_b3_active = True

    mimo25pro_result = (
        read_json(CODINGPLAN_MIMO25PRO_RESULT)
        if CODINGPLAN_MIMO25PRO_RESULT.is_file()
        else {}
    )
    mimo25pro_status = validate_capability_result(mimo25pro_result)
    mimo25pro_closeout = (
        read_json(CODINGPLAN_MIMO25PRO_CLOSEOUT)
        if CODINGPLAN_MIMO25PRO_CLOSEOUT.is_file()
        else {}
    )
    final_backbone_selection = (
        read_json(FINAL_BACKBONE_SELECTION)
        if FINAL_BACKBONE_SELECTION.is_file()
        else {}
    )
    final_backbone_selected = False
    if final_backbone_selection:
        for label, payload in (
            ("mimo-v2.5-pro closeout", mimo25pro_closeout),
            ("final backbone selection", final_backbone_selection),
        ):
            if payload.get("object_id") != OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            claimed = payload.get("content_sha256")
            unsigned = dict(payload)
            unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError(f"{label} content hash mismatch.")
        if mimo25pro_status != "CAPABILITY_CALIBRATION_PASS":
            raise PreflightError("mimo-v2.5-pro B3 result is not a capability PASS.")
        if mimo25pro_closeout.get("status") != "CODINGPLAN_MIMO25PRO_B3_PASS_CLOSEOUT":
            raise PreflightError("mimo-v2.5-pro B3 closeout status mismatch.")
        if mimo25pro_closeout.get("verdict") != mimo25pro_status:
            raise PreflightError("mimo-v2.5-pro result/closeout verdict mismatch.")
        if final_backbone_selection.get("status") != "CAPABILITY_BACKBONE_SELECTED_MIMO25PRO_PASS":
            raise PreflightError("Final backbone selection status mismatch.")
        selected = final_backbone_selection.get("selected_backbone", {})
        if selected != {
            "model_id": "mimo-v2.5-pro",
            "model_profile": "AtomGit-mimo-v2.5-pro",
            "provider": "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY",
            "harness": "ATOMCODE_CODINGPLAN_MCP_V1",
        }:
            raise PreflightError("Final selected backbone identity drifted.")
        if final_backbone_selection.get("capability_closeout_content_sha256") != mimo25pro_closeout.get("content_sha256"):
            raise PreflightError("Final selection/closeout lineage drifted.")
        if final_backbone_selection.get("authority", {}).get("f0") is not False:
            raise PreflightError("Backbone selection cannot self-authorize F0.")
        final_backbone_selected = True

    f0_source_authorized = False
    f0_human_authorization = (
        read_json(F0_HUMAN_AUTHORIZATION) if F0_HUMAN_AUTHORIZATION.is_file() else {}
    )
    f0_transport_addendum = (
        read_json(F0_TRANSPORT_ADDENDUM) if F0_TRANSPORT_ADDENDUM.is_file() else {}
    )
    f0_q1 = read_json(F0_MIMO25PRO_Q1) if F0_MIMO25PRO_Q1.is_file() else {}
    f0_source_contract = (
        read_json(F0_MIMO25PRO_SOURCE_CONTRACT)
        if F0_MIMO25PRO_SOURCE_CONTRACT.is_file()
        else {}
    )
    if any((f0_human_authorization, f0_transport_addendum, f0_q1, f0_source_contract)):
        if not all((f0_human_authorization, f0_transport_addendum, f0_q1, f0_source_contract)):
            raise PreflightError("F0 authorization artifact set is incomplete.")
        if not final_backbone_selected:
            raise PreflightError("F0 authorization requires a frozen selected backbone.")
        for label, payload in (
            ("F0 human authorization", f0_human_authorization),
            ("F0 transport addendum", f0_transport_addendum),
            ("F0 MCP Q1", f0_q1),
            ("F0 source contract", f0_source_contract),
        ):
            if payload.get("object_id") != OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            claimed = payload.get("content_sha256")
            unsigned = dict(payload)
            unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError(f"{label} content hash mismatch.")
        if f0_human_authorization.get("status") != "USER_AUTHORIZED_F0_AFTER_MIMO25PRO_CAPABILITY_PASS":
            raise PreflightError("F0 human authorization status mismatch.")
        if f0_human_authorization.get("authority", {}).get("f0") is not True:
            raise PreflightError("F0 human authorization did not open F0.")
        if f0_human_authorization.get("authority", {}).get("p1") is not False:
            raise PreflightError("F0 authorization cannot open P1.")
        if f0_transport_addendum.get("status") != "F0_SELECTED_BACKBONE_TRANSPORT_COMPATIBILITY_ADDENDUM_PASS":
            raise PreflightError("F0 selected-backbone transport addendum mismatch.")
        if f0_transport_addendum.get("scientific_variables_changed") != []:
            raise PreflightError("F0 transport addendum changed scientific variables.")
        if f0_q1.get("status") != "F0_CODINGPLAN_MIMO25PRO_MCP_PREDISPATCH_PASS":
            raise PreflightError("F0 MCP Q1 status mismatch.")
        if f0_q1.get("codingplan_model_requests") != 0 or f0_q1.get("scientific_dispatch_sent") is not False:
            raise PreflightError("F0 MCP Q1 crossed the zero-request predispatch boundary.")
        if f0_source_contract.get("status") != "F0_CODINGPLAN_MIMO25PRO_SOURCE_AUTHORIZED":
            raise PreflightError("F0 source contract status mismatch.")
        if f0_source_contract.get("authority", {}).get("source") is not True:
            raise PreflightError("F0 source contract did not authorize source execution.")
        if f0_source_contract.get("authority", {}).get("probe") is not False:
            raise PreflightError("F0 source contract prematurely authorized probes.")
        if f0_source_contract.get("authority", {}).get("p1") is not False:
            raise PreflightError("F0 source contract cannot authorize P1.")
        if f0_source_contract.get("selected_backbone_content_sha256") != final_backbone_selection.get("content_sha256"):
            raise PreflightError("F0 source contract/backbone lineage drifted.")
        f0_source_authorized = True

    f0_uptake_failed = False
    f0_repairs_manifest = read_json(F0_REPAIRS_MANIFEST) if F0_REPAIRS_MANIFEST.is_file() else {}
    f0_adjudication = read_json(F0_ADJUDICATION) if F0_ADJUDICATION.is_file() else {}
    f0_source_closeout = read_json(F0_SOURCE_CLOSEOUT) if F0_SOURCE_CLOSEOUT.is_file() else {}
    f0_uptake_root_cause = read_json(F0_UPTAKE_ROOT_CAUSE) if F0_UPTAKE_ROOT_CAUSE.is_file() else {}
    f0_r1_proposal = read_json(F0_R1_PROPOSAL) if F0_R1_PROPOSAL.is_file() else {}
    if any((f0_repairs_manifest, f0_adjudication, f0_source_closeout)):
        if not all((f0_repairs_manifest, f0_adjudication, f0_source_closeout)):
            raise PreflightError("F0 source closeout artifact set is incomplete.")
        if f0_repairs_manifest.get("status") != "F0_UPDATE_UPTAKE_INSUFFICIENT_STOP":
            raise PreflightError("F0 repairs manifest disposition mismatch.")
        if f0_repairs_manifest.get("eligible_families") != []:
            raise PreflightError("F0 uptake-fail manifest unexpectedly has eligible repairs.")
        for label, payload in (("F0 adjudication", f0_adjudication), ("F0 source closeout", f0_source_closeout)):
            if payload.get("object_id") != OBJECT_ID:
                raise PreflightError(f"{label} object mismatch.")
            claimed = payload.get("content_sha256")
            unsigned = dict(payload); unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError(f"{label} content hash mismatch.")
        if f0_adjudication.get("verdict") != "F0_UPDATE_UPTAKE_FAIL" or f0_adjudication.get("further_execution_authority") is not False:
            raise PreflightError("F0 adjudication did not freeze mandatory uptake stop.")
        if f0_source_closeout.get("status") != "F0_UPDATE_UPTAKE_FAIL_SOURCE_CLOSEOUT":
            raise PreflightError("F0 source closeout status mismatch.")
        if f0_source_closeout.get("source_target_success_count") != 8 or f0_source_closeout.get("eligible_repair_family_count") != 0:
            raise PreflightError("F0 source closeout aggregate drifted.")
        if f0_source_closeout.get("authority", {}).get("f0") is not False:
            raise PreflightError("Stopped F0 source closeout cannot retain F0 authority.")
        if f0_uptake_root_cause:
            if f0_uptake_root_cause.get("object_id") != OBJECT_ID:
                raise PreflightError("F0 uptake root-cause object mismatch.")
            claimed = f0_uptake_root_cause.get("content_sha256")
            unsigned = dict(f0_uptake_root_cause); unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError("F0 uptake root-cause content hash mismatch.")
            if f0_uptake_root_cause.get("status") != "CAPABILITY_GATE_DOES_NOT_IDENTIFY_SOURCE_FAILURE_AVAILABILITY":
                raise PreflightError("F0 uptake root-cause status mismatch.")
            if f0_uptake_root_cause.get("classification") != "SOURCE_FAILURE_OPPORTUNITY_DESIGN_MISMATCH":
                raise PreflightError("F0 uptake root-cause classification mismatch.")
            if f0_uptake_root_cause.get("authority", {}).get("prospective_redesign_only") is not True:
                raise PreflightError("F0 uptake root-cause did not preserve prospective-redesign-only boundary.")
        if f0_r1_proposal:
            if f0_r1_proposal.get("object_id") != OBJECT_ID:
                raise PreflightError("F0-R1 proposal object mismatch.")
            claimed = f0_r1_proposal.get("content_sha256")
            unsigned = dict(f0_r1_proposal); unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError("F0-R1 proposal content hash mismatch.")
            if f0_r1_proposal.get("status") != "PROSPECTIVE_F0_R1_SOURCE_FAILURE_QUALIFICATION_PROPOSAL_ONLY":
                raise PreflightError("F0-R1 proposal status mismatch.")
            authority = f0_r1_proposal.get("authority", {})
            if authority.get("design_only") is not True or authority.get("sq0_execution") is not False or authority.get("f0_r1_execution") is not False:
                raise PreflightError("F0-R1 proposal crossed proposal-only authority boundary.")
        f0_uptake_failed = True

    sq0_execution_authorized = False
    sq0_static_contract = read_json(SQ0_STATIC_CONTRACT) if SQ0_STATIC_CONTRACT.is_file() else {}
    sq0_static_qualification = read_json(SQ0_STATIC_QUALIFICATION) if SQ0_STATIC_QUALIFICATION.is_file() else {}
    sq0_human_authorization = read_json(SQ0_HUMAN_AUTHORIZATION) if SQ0_HUMAN_AUTHORIZATION.is_file() else {}
    sq0_q1 = read_json(SQ0_MIMO25PRO_Q1) if SQ0_MIMO25PRO_Q1.is_file() else {}
    sq0_execution_contract = read_json(SQ0_EXECUTION_CONTRACT) if SQ0_EXECUTION_CONTRACT.is_file() else {}
    if any((sq0_static_contract, sq0_static_qualification, sq0_human_authorization, sq0_q1, sq0_execution_contract)):
        if not all((sq0_static_contract, sq0_static_qualification, sq0_human_authorization, sq0_q1, sq0_execution_contract)):
            raise PreflightError("SQ0 authorization artifact set is incomplete.")
        if not f0_uptake_failed:
            raise PreflightError("SQ0 execution requires frozen current-F0 uptake failure.")
        for label, payload in (
            ("SQ0 static contract", sq0_static_contract),
            ("SQ0 static qualification", sq0_static_qualification),
            ("SQ0 human authorization", sq0_human_authorization),
            ("SQ0 MCP Q1", sq0_q1),
            ("SQ0 execution contract", sq0_execution_contract),
        ):
            if payload.get("object_id") != OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            claimed = payload.get("content_sha256")
            unsigned = dict(payload); unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError(f"{label} content hash mismatch.")
        if sq0_static_contract.get("status") != "SQ0_TARGET_CHALLENGE_V1_STATIC_DESIGN_READY":
            raise PreflightError("SQ0 static design status mismatch.")
        if sq0_static_contract.get("case_count") != 12 or sq0_static_contract.get("confirmatory_reuse") is not False:
            raise PreflightError("SQ0 static design cardinality/reuse boundary drifted.")
        if sq0_static_qualification.get("status") != "SQ0_TARGET_CHALLENGE_V1_PUBLIC_REACHABILITY_PASS":
            raise PreflightError("SQ0 public reachability status mismatch.")
        if sq0_static_qualification.get("provider_requests") != 0 or sq0_static_qualification.get("minimum_headroom", 0) < 6:
            raise PreflightError("SQ0 static qualification is not zero-request/headroom qualified.")
        if sq0_human_authorization.get("status") != "USER_AUTHORIZED_SQ0_TARGET_FAILURE_QUALIFICATION_AFTER_F0_UPTAKE_FAIL":
            raise PreflightError("SQ0 human authorization status mismatch.")
        if sq0_human_authorization.get("authority", {}).get("sq0_execution") is not True:
            raise PreflightError("SQ0 authorization did not open SQ0 execution.")
        if any(sq0_human_authorization.get("authority", {}).get(key) for key in ("f0_r1", "probe", "p1", "toolsandbox", "appworld_ul", "paper_claim")):
            raise PreflightError("SQ0 human authorization opened forbidden downstream authority.")
        if sq0_q1.get("status") != "SQ0_MIMO25PRO_MCP_PREDISPATCH_PASS" or sq0_q1.get("codingplan_model_requests") != 0 or sq0_q1.get("scientific_dispatch_sent") is not False:
            raise PreflightError("SQ0 Q1 crossed zero-request predispatch boundary.")
        if sq0_execution_contract.get("status") != "SQ0_MIMO25PRO_V1_EXECUTION_AUTHORIZED":
            raise PreflightError("SQ0 execution contract status mismatch.")
        if sq0_execution_contract.get("panel", {}).get("case_count") != 12 or sq0_execution_contract.get("panel", {}).get("confirmatory_reuse") is not False:
            raise PreflightError("SQ0 execution panel/reuse boundary drifted.")
        if sq0_execution_contract.get("authority", {}).get("sq0_execution") is not True or any(sq0_execution_contract.get("authority", {}).get(key) for key in ("f0_r1", "probe", "p1", "toolsandbox", "appworld_ul", "paper_claim")):
            raise PreflightError("SQ0 execution contract authority boundary drifted.")
        sq0_execution_authorized = True

    sq0_v1_closed = False
    sq0_v1_result = read_json(SQ0_V1_RESULT) if SQ0_V1_RESULT.is_file() else {}
    sq0_v1_closeout = read_json(SQ0_V1_CLOSEOUT) if SQ0_V1_CLOSEOUT.is_file() else {}
    if any((sq0_v1_result, sq0_v1_closeout)):
        if not all((sq0_v1_result, sq0_v1_closeout)):
            raise PreflightError("SQ0-V1 result/closeout artifact set is incomplete.")
        for label, payload in (("SQ0-V1 result", sq0_v1_result), ("SQ0-V1 closeout", sq0_v1_closeout)):
            if payload.get("object_id") != OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            claimed = payload.get("content_sha256"); unsigned = dict(payload); unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError(f"{label} content hash mismatch.")
        if sq0_v1_result.get("status") != "SQ0_TARGET_CHALLENGE_TOO_EASY_STOP":
            raise PreflightError("SQ0-V1 result is not at frozen too-easy stop.")
        if sq0_v1_result.get("case_count") != 12 or sq0_v1_result.get("usable_target_failure_count") != 0 or sq0_v1_result.get("non_semantic_failure_units") != []:
            raise PreflightError("SQ0-V1 aggregate drifted.")
        if sq0_v1_closeout.get("status") != "SQ0_V1_TOO_EASY_CLOSEOUT" or sq0_v1_closeout.get("verdict") != sq0_v1_result.get("status"):
            raise PreflightError("SQ0-V1 closeout/result mismatch.")
        if sq0_v1_closeout.get("authority", {}).get("sq0_v2_design") is not True or sq0_v1_closeout.get("authority", {}).get("sq0_v2_execution") is not False:
            raise PreflightError("SQ0-V1 closeout crossed development-only redesign boundary.")
        sq0_v1_closed = True

    sq0_v2_execution_authorized = False
    sq0_v2_static_contract = read_json(SQ0_V2_STATIC_CONTRACT) if SQ0_V2_STATIC_CONTRACT.is_file() else {}
    sq0_v2_static_qualification = read_json(SQ0_V2_STATIC_QUALIFICATION) if SQ0_V2_STATIC_QUALIFICATION.is_file() else {}
    sq0_v2_human_authorization = read_json(SQ0_V2_HUMAN_AUTHORIZATION) if SQ0_V2_HUMAN_AUTHORIZATION.is_file() else {}
    sq0_v2_q1 = read_json(SQ0_V2_MIMO25PRO_Q1) if SQ0_V2_MIMO25PRO_Q1.is_file() else {}
    sq0_v2_execution_contract = read_json(SQ0_V2_EXECUTION_CONTRACT) if SQ0_V2_EXECUTION_CONTRACT.is_file() else {}
    if any((sq0_v2_static_contract, sq0_v2_static_qualification, sq0_v2_human_authorization, sq0_v2_q1, sq0_v2_execution_contract)):
        if not all((sq0_v2_static_contract, sq0_v2_static_qualification, sq0_v2_human_authorization, sq0_v2_q1, sq0_v2_execution_contract)):
            raise PreflightError("SQ0-V2 authorization artifact set is incomplete.")
        if not sq0_v1_closed:
            raise PreflightError("SQ0-V2 requires a frozen SQ0-V1 too-easy closeout.")
        for label, payload in (
            ("SQ0-V2 static contract", sq0_v2_static_contract),
            ("SQ0-V2 static qualification", sq0_v2_static_qualification),
            ("SQ0-V2 human authorization", sq0_v2_human_authorization),
            ("SQ0-V2 MCP Q1", sq0_v2_q1),
            ("SQ0-V2 execution contract", sq0_v2_execution_contract),
        ):
            if payload.get("object_id") != OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            claimed = payload.get("content_sha256"); unsigned = dict(payload); unsigned.pop("content_sha256", None)
            if claimed != digest(unsigned):
                raise PreflightError(f"{label} content hash mismatch.")
        if sq0_v2_static_contract.get("status") != "SQ0_V2_TARGET_CHALLENGE_STATIC_DESIGN_READY" or sq0_v2_static_contract.get("case_count") != 12 or sq0_v2_static_contract.get("v1_case_reuse") is not False:
            raise PreflightError("SQ0-V2 static design/reuse boundary drifted.")
        if sq0_v2_static_qualification.get("status") != "SQ0_V2_PUBLIC_REACHABILITY_PASS" or sq0_v2_static_qualification.get("provider_requests") != 0 or sq0_v2_static_qualification.get("minimum_headroom", 0) < 10:
            raise PreflightError("SQ0-V2 public qualification drifted.")
        if sq0_v2_human_authorization.get("status") != "USER_AUTHORIZED_SQ0_V2_DEVELOPMENT_ITERATION_AFTER_V1_TOO_EASY" or sq0_v2_human_authorization.get("authority", {}).get("sq0_v2_execution") is not True:
            raise PreflightError("SQ0-V2 human authorization mismatch.")
        if any(sq0_v2_human_authorization.get("authority", {}).get(k) for k in ("f0_r1", "probe", "p1", "toolsandbox", "appworld_ul", "paper_claim")):
            raise PreflightError("SQ0-V2 human authorization opened downstream authority.")
        if sq0_v2_q1.get("status") != "SQ0_V2_MIMO25PRO_MCP_PREDISPATCH_PASS" or sq0_v2_q1.get("codingplan_model_requests") != 0 or sq0_v2_q1.get("scientific_dispatch_sent") is not False:
            raise PreflightError("SQ0-V2 Q1 crossed zero-request predispatch boundary.")
        if sq0_v2_execution_contract.get("status") != "SQ0_V2_MIMO25PRO_EXECUTION_AUTHORIZED" or sq0_v2_execution_contract.get("panel", {}).get("case_count") != 12 or sq0_v2_execution_contract.get("panel", {}).get("confirmatory_reuse") is not False:
            raise PreflightError("SQ0-V2 execution contract drifted.")
        if sq0_v2_execution_contract.get("authority", {}).get("sq0_v2_execution") is not True or any(sq0_v2_execution_contract.get("authority", {}).get(k) for k in ("f0_r1", "probe", "p1", "toolsandbox", "appworld_ul", "paper_claim")):
            raise PreflightError("SQ0-V2 execution authority boundary drifted.")
        sq0_v2_execution_authorized = True

    sq0_v2_void = read_json(SQ0_V2_VOID) if SQ0_V2_VOID.is_file() else {}
    sq0_v2_void_active = False
    if sq0_v2_void:
        claimed=sq0_v2_void.get("content_sha256"); unsigned=dict(sq0_v2_void); unsigned.pop("content_sha256",None)
        if sq0_v2_void.get("object_id")!=OBJECT_ID or claimed!=digest(unsigned):
            raise PreflightError("SQ0-V2 void identity/hash mismatch.")
        if sq0_v2_void.get("status")!="SQ0_V2_VOID_NATIVE_READ_FILE_SCHEMA_CONTAMINATION" or sq0_v2_void.get("valid_sq0_v2_measurements")!=0 or sq0_v2_void.get("appworld_tool_calls_executed")!=0:
            raise PreflightError("SQ0-V2 contamination void classification drifted.")
        sq0_v2_void_active=True
        sq0_v2_execution_authorized=False

    sq0_v2r1_transport_ready=False
    sq0_v2r1_transport_pass=False
    sq0_v2r1_static_contract=read_json(SQ0_V2R1_STATIC_CONTRACT) if SQ0_V2R1_STATIC_CONTRACT.is_file() else {}
    sq0_v2r1_static_qualification=read_json(SQ0_V2R1_STATIC_QUALIFICATION) if SQ0_V2R1_STATIC_QUALIFICATION.is_file() else {}
    sq0_v2r1_transport_contract=read_json(SQ0_V2R1_TRANSPORT_CONTRACT) if SQ0_V2R1_TRANSPORT_CONTRACT.is_file() else {}
    sq0_v2r1_transport_result=read_json(SQ0_V2R1_TRANSPORT_RESULT) if SQ0_V2R1_TRANSPORT_RESULT.is_file() else {}
    if any((sq0_v2r1_static_contract,sq0_v2r1_static_qualification,sq0_v2r1_transport_contract,sq0_v2r1_transport_result)):
        if not all((sq0_v2r1_static_contract,sq0_v2r1_static_qualification,sq0_v2r1_transport_contract)):
            raise PreflightError("SQ0-V2R1 pre-transport artifact set is incomplete.")
        if not sq0_v2_void_active:
            raise PreflightError("SQ0-V2R1 requires frozen V2 harness-contamination void.")
        for label,payload in (("SQ0-V2R1 static contract",sq0_v2r1_static_contract),("SQ0-V2R1 static qualification",sq0_v2r1_static_qualification),("SQ0-V2R1 transport contract",sq0_v2r1_transport_contract)):
            if payload.get("object_id")!=OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            c=payload.get("content_sha256"); u=dict(payload); u.pop("content_sha256",None)
            if c!=digest(u): raise PreflightError(f"{label} content hash mismatch.")
        if sq0_v2r1_static_contract.get("status")!="SQ0_V2R1_STATIC_DESIGN_READY" or sq0_v2r1_static_contract.get("v2_case_reuse") is not False:
            raise PreflightError("SQ0-V2R1 static design/reuse boundary drifted.")
        if sq0_v2r1_static_qualification.get("status")!="SQ0_V2R1_PUBLIC_REACHABILITY_PASS" or sq0_v2r1_static_qualification.get("provider_requests")!=0 or sq0_v2r1_static_qualification.get("minimum_headroom",0)<15:
            raise PreflightError("SQ0-V2R1 static qualification drifted.")
        if sq0_v2r1_transport_contract.get("status")!="SQ0_V2R1_TRANSPORT_QUALIFICATION_AUTHORIZED" or sq0_v2r1_transport_contract.get("authority",{}).get("transport_qualification") is not True or sq0_v2r1_transport_contract.get("authority",{}).get("sq0_v2r1_execution") is not False:
            raise PreflightError("SQ0-V2R1 transport authority boundary drifted.")
        if sq0_v2r1_transport_result:
            c=sq0_v2r1_transport_result.get("content_sha256"); u=dict(sq0_v2r1_transport_result); u.pop("content_sha256",None)
            if sq0_v2r1_transport_result.get("object_id")!=OBJECT_ID or c!=digest(u): raise PreflightError("SQ0-V2R1 transport result identity/hash mismatch.")
            if sq0_v2r1_transport_result.get("status")!="SQ0_V2R1_TRANSPORT_QUALIFICATION_PASS" or sq0_v2r1_transport_result.get("native_tool_attempts")!=[] or sq0_v2r1_transport_result.get("prohibited_tool") is not None:
                raise PreflightError("SQ0-V2R1 transport result is not a clean PASS.")
            sq0_v2r1_transport_pass=True
        else:
            sq0_v2r1_transport_ready=True

    sq0_v2r1_execution_authorized=False
    sq0_v2r1_human_authorization=read_json(SQ0_V2R1_HUMAN_AUTHORIZATION) if SQ0_V2R1_HUMAN_AUTHORIZATION.is_file() else {}
    sq0_v2r1_q1=read_json(SQ0_V2R1_MIMO25PRO_Q1) if SQ0_V2R1_MIMO25PRO_Q1.is_file() else {}
    sq0_v2r1_execution_contract=read_json(SQ0_V2R1_EXECUTION_CONTRACT) if SQ0_V2R1_EXECUTION_CONTRACT.is_file() else {}
    if any((sq0_v2r1_human_authorization,sq0_v2r1_q1,sq0_v2r1_execution_contract)):
        if not all((sq0_v2r1_human_authorization,sq0_v2r1_q1,sq0_v2r1_execution_contract)):
            raise PreflightError("SQ0-V2R1 execution authorization artifact set is incomplete.")
        if not sq0_v2r1_transport_pass:
            raise PreflightError("SQ0-V2R1 execution requires clean transport qualification PASS.")
        for label,payload in (("SQ0-V2R1 human authorization",sq0_v2r1_human_authorization),("SQ0-V2R1 MCP Q1",sq0_v2r1_q1),("SQ0-V2R1 execution contract",sq0_v2r1_execution_contract)):
            if payload.get("object_id")!=OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            c=payload.get("content_sha256");u=dict(payload);u.pop("content_sha256",None)
            if c!=digest(u):raise PreflightError(f"{label} content hash mismatch.")
        if sq0_v2r1_human_authorization.get("status")!="USER_AUTHORIZED_SQ0_V2R1_AFTER_TRANSPORT_QUALIFICATION_PASS" or sq0_v2r1_human_authorization.get("authority",{}).get("sq0_v2r1_execution") is not True:
            raise PreflightError("SQ0-V2R1 human authorization mismatch.")
        if any(sq0_v2r1_human_authorization.get("authority",{}).get(k) for k in ("f0_r1","probe","p1","toolsandbox","appworld_ul","paper_claim")):
            raise PreflightError("SQ0-V2R1 human authorization opened downstream authority.")
        if sq0_v2r1_q1.get("status")!="SQ0_V2R1_MIMO25PRO_MCP_PREDISPATCH_PASS" or sq0_v2r1_q1.get("codingplan_model_requests")!=0 or sq0_v2r1_q1.get("scientific_dispatch_sent") is not False:
            raise PreflightError("SQ0-V2R1 Q1 crossed zero-request predispatch boundary.")
        if sq0_v2r1_execution_contract.get("status")!="SQ0_V2R1_MIMO25PRO_EXECUTION_AUTHORIZED" or sq0_v2r1_execution_contract.get("panel",{}).get("case_count")!=12 or sq0_v2r1_execution_contract.get("panel",{}).get("confirmatory_reuse") is not False:
            raise PreflightError("SQ0-V2R1 execution contract drifted.")
        if sq0_v2r1_execution_contract.get("authority",{}).get("sq0_v2r1_execution") is not True or any(sq0_v2r1_execution_contract.get("authority",{}).get(k) for k in ("f0_r1","probe","p1","toolsandbox","appworld_ul","paper_claim")):
            raise PreflightError("SQ0-V2R1 execution authority boundary drifted.")
        sq0_v2r1_execution_authorized=True

    sq0_v2r1_closed=False
    sq0_v2r1_result=read_json(SQ0_V2R1_RESULT) if SQ0_V2R1_RESULT.is_file() else {}
    sq0_v2r1_closeout=read_json(SQ0_V2R1_CLOSEOUT) if SQ0_V2R1_CLOSEOUT.is_file() else {}
    sq0_v2r1_root_cause=read_json(SQ0_V2R1_ROOT_CAUSE) if SQ0_V2R1_ROOT_CAUSE.is_file() else {}
    if any((sq0_v2r1_result,sq0_v2r1_closeout,sq0_v2r1_root_cause)):
        if not all((sq0_v2r1_result,sq0_v2r1_closeout,sq0_v2r1_root_cause)):
            raise PreflightError("SQ0-V2R1 closeout artifact set is incomplete.")
        for label,payload in (("SQ0-V2R1 result",sq0_v2r1_result),("SQ0-V2R1 closeout",sq0_v2r1_closeout),("SQ0-V2R1 root cause",sq0_v2r1_root_cause)):
            if payload.get("object_id")!=OBJECT_ID:
                raise PreflightError(f"{label} object identity mismatch.")
            c=payload.get("content_sha256");u=dict(payload);u.pop("content_sha256",None)
            if c!=digest(u): raise PreflightError(f"{label} content hash mismatch.")
        if sq0_v2r1_result.get("status")!="SQ0_V2R1_TARGET_CHALLENGE_TOO_EASY_STOP" or sq0_v2r1_result.get("usable_target_failure_count")!=4 or sq0_v2r1_result.get("non_semantic_failure_units")!=[]:
            raise PreflightError("SQ0-V2R1 result aggregate drifted.")
        if sq0_v2r1_closeout.get("status")!="SQ0_V2R1_TOO_EASY_CLOSEOUT" or sq0_v2r1_closeout.get("verdict")!=sq0_v2r1_result.get("status"):
            raise PreflightError("SQ0-V2R1 closeout/result mismatch.")
        if sq0_v2r1_root_cause.get("status")!="SQ0_V2R1_RAW_FAILURES_ARE_FORMATTING_PSEUDO_FAILURES" or sq0_v2r1_root_cause.get("semantic_failure_count_after_terminal_newline_normalization")!=0:
            raise PreflightError("SQ0-V2R1 semantic failure diagnosis drifted.")
        if sq0_v2r1_closeout.get("authority",{}).get("sq0_v3_execution") is not False or sq0_v2r1_root_cause.get("authority",{}).get("sq0_v3_execution") is not False:
            raise PreflightError("SQ0-V2R1 closeout prematurely authorizes V3 execution.")
        sq0_v2r1_closed=True
        sq0_v2r1_execution_authorized=False

    sq0_v3_execution_authorized=False
    sq0_v3_static_contract=read_json(SQ0_V3_STATIC_CONTRACT) if SQ0_V3_STATIC_CONTRACT.is_file() else {}
    sq0_v3_static_qualification=read_json(SQ0_V3_STATIC_QUALIFICATION) if SQ0_V3_STATIC_QUALIFICATION.is_file() else {}
    sq0_v3_human_authorization=read_json(SQ0_V3_HUMAN_AUTHORIZATION) if SQ0_V3_HUMAN_AUTHORIZATION.is_file() else {}
    sq0_v3_q1=read_json(SQ0_V3_MIMO25PRO_Q1) if SQ0_V3_MIMO25PRO_Q1.is_file() else {}
    sq0_v3_execution_contract=read_json(SQ0_V3_EXECUTION_CONTRACT) if SQ0_V3_EXECUTION_CONTRACT.is_file() else {}
    if any((sq0_v3_static_contract,sq0_v3_static_qualification,sq0_v3_human_authorization,sq0_v3_q1,sq0_v3_execution_contract)):
        if not all((sq0_v3_static_contract,sq0_v3_static_qualification,sq0_v3_human_authorization,sq0_v3_q1,sq0_v3_execution_contract)):
            raise PreflightError("SQ0-V3 execution artifact set is incomplete.")
        if not sq0_v2r1_closed:
            raise PreflightError("SQ0-V3 requires frozen V2R1 closeout.")
        for label,payload in (("SQ0-V3 static contract",sq0_v3_static_contract),("SQ0-V3 static qualification",sq0_v3_static_qualification),("SQ0-V3 human authorization",sq0_v3_human_authorization),("SQ0-V3 Q1",sq0_v3_q1),("SQ0-V3 execution contract",sq0_v3_execution_contract)):
            if payload.get("object_id")!=OBJECT_ID: raise PreflightError(f"{label} object mismatch.")
            c=payload.get("content_sha256");u=dict(payload);u.pop("content_sha256",None)
            if c!=digest(u): raise PreflightError(f"{label} hash mismatch.")
        if sq0_v3_static_contract.get("status")!="SQ0_V3_STATIC_DESIGN_READY" or sq0_v3_static_contract.get("case_count")!=12 or sq0_v3_static_contract.get("confirmatory_reuse") is not False:
            raise PreflightError("SQ0-V3 static contract drifted.")
        if sq0_v3_static_qualification.get("status")!="SQ0_V3_PUBLIC_REACHABILITY_PASS" or sq0_v3_static_qualification.get("minimum_headroom",0)<18 or sq0_v3_static_qualification.get("provider_requests")!=0:
            raise PreflightError("SQ0-V3 static qualification drifted.")
        if sq0_v3_human_authorization.get("status")!="USER_AUTHORIZED_SQ0_V3_AFTER_TRANSPORT_QUALIFICATION_PASS" or sq0_v3_human_authorization.get("authority",{}).get("sq0_v3_execution") is not True:
            raise PreflightError("SQ0-V3 human authorization mismatch.")
        if any(sq0_v3_human_authorization.get("authority",{}).get(k) for k in ("f0_r1","probe","p1","toolsandbox","appworld_ul","paper_claim")):
            raise PreflightError("SQ0-V3 human authorization opened downstream authority.")
        if sq0_v3_q1.get("status")!="SQ0_V3_MIMO25PRO_MCP_PREDISPATCH_PASS" or sq0_v3_q1.get("codingplan_model_requests")!=0 or sq0_v3_q1.get("scientific_dispatch_sent") is not False:
            raise PreflightError("SQ0-V3 Q1 crossed zero-request boundary.")
        if sq0_v3_execution_contract.get("status")!="SQ0_V3_MIMO25PRO_EXECUTION_AUTHORIZED" or sq0_v3_execution_contract.get("panel",{}).get("case_count")!=12:
            raise PreflightError("SQ0-V3 execution contract drifted.")
        futility=sq0_v3_execution_contract.get("execution_policy",{}).get("futility_early_stop",{})
        if futility.get("acceptable_final_failure_counts")!=[9,10] or futility.get("stop_too_easy_if_target_success_count_exceeds")!=3 or futility.get("stop_too_hard_if_usable_failure_count_exceeds")!=10:
            raise PreflightError("SQ0-V3 futility rule drifted.")
        if sq0_v3_execution_contract.get("authority",{}).get("sq0_v3_execution") is not True or any(sq0_v3_execution_contract.get("authority",{}).get(k) for k in ("f0_r1","probe","p1","toolsandbox","appworld_ul","paper_claim")):
            raise PreflightError("SQ0-V3 execution authority boundary drifted.")
        sq0_v3_execution_authorized=True

    if CAPABILITY_R5_PARTIAL_RESULT.is_file():
        capability_result_path = CAPABILITY_R5_PARTIAL_RESULT
        capability_result = read_json(CAPABILITY_R5_PARTIAL_RESULT)
    elif r3_partial_void_active:
        capability_result_path = Path()
        capability_result = {}
    elif CAPABILITY_R3_PARTIAL_RESULT.is_file():
        capability_result_path = CAPABILITY_R3_PARTIAL_RESULT
        capability_result = read_json(CAPABILITY_R3_PARTIAL_RESULT)
    elif CAPABILITY_R3_RESULT.is_file():
        capability_result_path = CAPABILITY_R3_RESULT
        capability_result = read_json(CAPABILITY_R3_RESULT)
    elif r2_void_active:
        capability_result_path = Path()
        capability_result = {}
    else:
        capability_result_path = CAPABILITY_R2_RESULT if CAPABILITY_R2_RESULT.is_file() else Path()
        capability_result = (
            read_json(CAPABILITY_R2_RESULT) if CAPABILITY_R2_RESULT.is_file() else {}
        )
    capability_status = validate_capability_result(capability_result)

    flash_final = (
        read_json(CAPABILITY_CONTINUATION_RESULT)
        if CAPABILITY_CONTINUATION_RESULT.is_file()
        else {}
    )
    plus_a1 = read_json(CAPABILITY_A1_RESULT) if CAPABILITY_A1_RESULT.is_file() else {}
    flash_provider_requests = int(flash_final.get("provider_request_total", 0))
    plus_a1_provider_requests = int(plus_a1.get("provider_request_total", 0))
    r2_result = read_json(CAPABILITY_R2_RESULT) if CAPABILITY_R2_RESULT.is_file() else {}
    r2_provider_requests = int(r2_result.get("provider_request_total", 0))
    r3_provider_requests = (
        int(capability_result.get("provider_request_total", 0))
        if capability_result_path == CAPABILITY_R3_RESULT
        else int(capability_result.get("provider_request_total_new", 0))
        if capability_result_path == CAPABILITY_R3_PARTIAL_RESULT
        else 0
    )
    r3_partial_void_provider_requests = int(
        r3_partial_void.get("provider_requests_spent_in_void_tnf_attempt", 0)
    )
    r5_provider_requests = (
        int(capability_result.get("provider_request_total_new", 0))
        if capability_result_path == CAPABILITY_R5_PARTIAL_RESULT
        else 0
    )
    flash_agent_requests = int(
        flash_final.get(
            "agent_model_request_count",
            flash_final.get("gate", {}).get("agent_model_request_count", 0),
        )
    )
    plus_a1_agent_requests = int(plus_a1.get("agent_model_request_count", 0))
    r2_agent_requests = int(r2_result.get("agent_model_request_count", 0))
    r2_agent_episodes = int(r2_result.get("agent_episode_count", 0))
    historical_void_provider_requests = flash_provider_requests + plus_a1_provider_requests
    historical_void_agent_requests = flash_agent_requests + plus_a1_agent_requests
    historical_void_agent_episodes = int(flash_final.get("agent_episode_count", 0)) + int(
        plus_a1.get("agent_episode_count", 0)
    )
    if r2_void_active:
        historical_void_provider_requests += r2_provider_requests
        historical_void_agent_requests += r2_agent_requests
        historical_void_agent_episodes += r2_agent_episodes
    if r3_partial_void_active:
        historical_void_provider_requests += r3_partial_void_provider_requests
        historical_void_agent_requests += r3_partial_void_provider_requests
        historical_void_agent_episodes += len(r3_partial_void.get("affected_units", []))
    if capability_result_path == CAPABILITY_R5_PARTIAL_RESULT:
        latest_provider_requests = r5_provider_requests
        latest_agent_requests = int(capability_result.get("new_agent_model_request_count", 0))
        latest_agent_episodes = int(capability_result.get("rerun_tnf_measurements", 0))
    elif capability_result_path == CAPABILITY_R3_PARTIAL_RESULT:
        latest_provider_requests = r3_provider_requests
        latest_agent_requests = int(capability_result.get("new_agent_model_request_count", 0))
        latest_agent_episodes = int(capability_result.get("rerun_tnf_measurements", 0))
    elif capability_result_path == CAPABILITY_R3_RESULT:
        latest_provider_requests = r3_provider_requests
        latest_agent_requests = int(capability_result.get("agent_model_request_count", 0))
        latest_agent_episodes = int(capability_result.get("agent_episode_count", 0))
    elif r2_void_active:
        latest_provider_requests = 0
        latest_agent_requests = 0
        latest_agent_episodes = 0
    else:
        latest_provider_requests = r2_provider_requests
        latest_agent_requests = r2_agent_requests
        latest_agent_episodes = r2_agent_episodes
    lineage_provider_requests = historical_void_provider_requests + latest_provider_requests
    lineage_agent_requests = historical_void_agent_requests + latest_agent_requests
    lineage_agent_episodes = historical_void_agent_episodes + latest_agent_episodes
    codingplan_accounting = codingplan_closeout.get("execution_accounting", {})
    both_valid_candidates_ceiling = (
        capability_status == "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP"
        and codingplan_status == "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP"
        and codingplan_closeout_valid
    )
    eligible_backbone_selected = (
        capability_status == "CAPABILITY_CALIBRATION_PASS"
        or codingplan_status == "CAPABILITY_CALIBRATION_PASS"
        or final_backbone_selected
    )

    capability = {
        "schema_version": "agent-constraint-externality-capability-calibration-v1",
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "stage": "DISJOINT_CAPABILITY_CALIBRATION",
        "outcome_status": "NOT_EXECUTED",
        "family_split_rule": "FIXED_BEFORE_ANY_PROVIDER_CALL",
        "family_ids": list(CAPABILITY_FAMILIES),
        "family_count": len(CAPABILITY_FAMILIES),
        "repeats_per_family": 2,
        "episodes_per_candidate": len(CAPABILITY_FAMILIES) * 2,
        "maximum_candidate_count": len(MODEL_SELECTION_ORDER),
        "maximum_episode_envelope": (
            len(CAPABILITY_FAMILIES) * 2 * len(MODEL_SELECTION_ORDER)
        ),
        "model_selection_order": list(MODEL_SELECTION_ORDER),
        "selection_rule": "ONLY_QWEN_CANDIDATE_MUST_QUALIFY_OR_STOP",
        "requested_model": REQUESTED_MODEL,
        "allowed_alias": ALLOWED_ALIAS,
        "candidate_isolation": (
            "The single candidate uses only this disjoint split; no F0 family "
            "outcome is readable before backbone freeze."
        ),
        "qualification_rules": {
            "tool_loop_completion_rate_min": 0.75,
            "target_success_rate_min": 0.50,
            "target_success_rate_max": 0.875,
            "baseline_non_target_preservation_rate_min": 0.85,
            "zero_malformed_function_calls_required": True,
        },
        "floor_disposition": "CAPABILITY_CALIBRATION_FAIL_FLOOR_STOP",
        "ceiling_disposition": "CAPABILITY_CALIBRATION_FAIL_CEILING_STOP",
        "interface_disposition": "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP",
        "automatic_fallback": False,
        "execution": {
            "provider": PROVIDER_ID,
            "provider_max_retries": 0,
            "application_retry": False,
            "capability_episode_cap": 8,
            "tool_interaction_cap": 16 if substrate_v4_recovery_pass else 12,
            "temperature": 0,
            "append_only_ledger": True,
            "no_episode_replacement": True,
        },
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
        "gpu_runs": 0,
    }

    f0 = {
        "schema_version": "agent-constraint-externality-f0-protocol-v1",
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "stage": "F0_FROZEN_NOT_EXECUTED",
        "family_ids": list(F0_FAMILIES),
        "family_count": len(F0_FAMILIES),
        "split_is_disjoint_from_capability": True,
        "backbone": "FROZEN_FROM_CAPABILITY_CALIBRATION_BEFORE_F0",
        "harness": "APPWORLD_FUNCTION_CALLING_V1",
        "update_surface": "PERSISTENT_PROCEDURAL_REPAIR_NOTE",
        "budgets": {
            "capability_agent_episodes": 8,
            "f0_source_agent_episodes": 8,
            "f0_probe_agent_episode_min": 108,
            "f0_probe_agent_episode_max": 144,
            "agent_episode_total_max": 160,
            "repair_generation_provider_request_cap": 8,
            "count_separately": [
                "agent_episode_count", "agent_model_request_count",
                "updater_model_request_count", "provider_request_total",
            ],
        },
        "source_phase": {
            "episodes": len(F0_FAMILIES),
            "one_target_isolated_episode_per_family": True,
            "updater_input": [
                "TARGET_CONSTRAINT_SPEC",
                "TARGET_TASK_INSTRUCTION",
                "TARGET_FAILURE_SLICE",
                "TARGET_TOOL_TRAJECTORY",
            ],
            "forbidden_updater_input": [
                "NON_TARGET_OUTCOMES",
                "TOPOLOGY_LABEL",
                "COUPLING_LEVEL",
                "ARM_ASSIGNMENT",
                "F0_EFFECT",
            ],
            "candidate_generation": (
                "Same frozen backbone generates one procedural repair note "
                "automatically from target failure only."
            ),
            "human_edit_after_generation": False,
            "freeze_fields": [
                "sha256", "raw_bytes", "normalized_bytes", "byte_length",
                "word_count", "fixed_tokenizer_token_count",
                "procedural_clause_count", "injection_position", "exposure_rule",
                "generation_model_id", "generation_request_sha256",
                "source_trajectory_sha256",
            ],
            "minimum_eligible_repair_families": 6,
            "maximum_eligible_repair_families": 8,
            "failure_or_success_retention": (
                "Retain every source result; never replace a family. Only a "
                "preregistered target failure can yield a repair artifact."
            ),
        },
        "probe_phase": {
            "arms": list(ARMS),
            "branches": list(BRANCHES),
            "seeds": list(SEEDS),
            "repeats": len(SEEDS),
            "planned_episode_envelope": (
                len(F0_FAMILIES) * len(ARMS) * len(BRANCHES) * len(SEEDS)
            ),
            "actual_episode_formula": (
                "eligible_repair_family_count * 3 arms * 2 branches * 3 seeds"
            ),
            "same_update_bytes_across_all_arms_and_update_replays": True,
            "reset_snapshot_before_every_replay": True,
            "partial_effects_readable_during_execution": False,
            "branch_order": {
                "method": "SHA256_PARITY",
                "salt": "ACE-F0-BRANCH-ORDER-20260831-V1",
                "key_fields": ["family_id", "arm", "seed"],
                "balanced_pair_rule": (
                    "Parity zero runs NO_UPDATE first; parity one runs UPDATE first."
                ),
            },
        },
        "exactly_once": {
            "provider_max_retries": 0,
            "application_retry": False,
            "append_only_ledger": True,
            "unique_episode_key_fields": ["family_id", "arm", "branch", "seed"],
            "dispatch_recorded_before_provider_call": True,
            "completion_appended_after_provider_call": True,
            "duplicate_key_is_fatal": True,
            "failed_or_partial_episode_retained": True,
            "retry_or_replacement_forbidden": True,
        },
        "metrics": {
            "target_repair_gain": "TARGET_UPDATE_MINUS_NO_UPDATE",
            "collateral_regression_rate": (
                "NEWLY_FAILED_BASELINE_SATISFIED_NON_TARGETS_DIVIDED_BY_ELIGIBLE_NON_TARGETS"
            ),
            "update_attributable_externality": "CRR_UPDATE_MINUS_CRR_NO_UPDATE",
            "primary_contrast": "UE_HIGH_MINUS_UE_INDEPENDENT_WITHIN_REPAIR_FAMILY",
            "secondary_ordered_contrast": "UE_INDEPENDENT_LE_UE_LOW_LE_UE_HIGH",
            "negative_values_retained": True,
            "per_constraint_rows_required": True,
        },
        "adjudication": {
            "uptake_fail": (
                "Fewer than 6 eligible repair families or mean target repair gain "
                "is not positive."
            ),
            "mechanism_support": (
                "At least 6 eligible families, positive mean target repair gain, "
                "mean within-family UE_HIGH-UE_INDEPENDENT >= 0.05, and the "
                "ordered exposure direction holds in at least two thirds of "
                "eligible families."
            ),
            "mechanism_fail": (
                "Uptake passes but mean UE_HIGH-UE_INDEPENDENT <= 0 and no ordered "
                "exposure direction remains."
            ),
            "otherwise": "F0_INCONCLUSIVE_STOP_OR_REVISE_WITHOUT_P1",
            "no_significance_claim_from_f0": True,
        },
        "post_f0_authority": {
            "toolsandbox_only_after": "F0_MECHANISM_SUPPORT",
            "appworld_ul_only_after": "F0_AND_TOOLSANDBOX_MECHANISM_SUPPORT",
            "full_p1": False,
            "workarena": False,
            "multi_backbone": False,
            "method_claim": False,
            "paper_claim": False,
        },
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
        "gpu_runs": 0,
    }

    if not m1_pass:
        readiness_status = "M1_RUNNER_QUALIFICATION_REQUIRED"
        blocker = "M1 scientific runner qualification has not passed."
        next_action = "RUN_M1_MOCK_QUALIFICATION"
    elif capability_status == "CAPABILITY_CALIBRATION_PASS":
        readiness_status = "CAPABILITY_CALIBRATION_PASS_F0_AUTHORIZATION_REQUIRED"
        blocker = "Capability passed, but this capability execution does not itself authorize F0."
        next_action = "STOP_AWAIT_HUMAN_F0_AUTHORIZATION"
    elif codingplan_status == "CAPABILITY_CALIBRATION_PASS" and codingplan_closeout_valid:
        readiness_status = "CODINGPLAN_CAPABILITY_PASS_F0_AUTHORIZATION_REQUIRED"
        blocker = "CodingPlan capability passed, but the distinct AtomCode MCP harness still requires separate human F0 authorization."
        next_action = "STOP_AWAIT_HUMAN_F0_AUTHORIZATION"
    elif sq0_v3_execution_authorized:
        readiness_status = "SQ0_V3_TARGET_FAILURE_QUALIFICATION_AUTHORIZED_READY"
        blocker = None
        next_action = "RUN_SQ0_V3_MIMO25PRO"
    elif sq0_v2r1_closed:
        readiness_status = "SQ0_V2R1_TOO_EASY_CLOSED_V3_DESIGN_REQUIRED"
        blocker = (
            "SQ0-V2R1 completed 12/12 with no interface failures, but raw target-failure rate was only 4/12; "
            "post-aggregate audit showed all four raw failures were terminal-newline-only formatting pseudo-failures."
        )
        next_action = "BUILD_FRESH_SQ0_V3_SEMANTIC_CHALLENGE"
    elif sq0_v2r1_execution_authorized:
        readiness_status = "SQ0_V2R1_TARGET_FAILURE_QUALIFICATION_AUTHORIZED_READY"
        blocker = None
        next_action = "RUN_SQ0_V2R1_MIMO25PRO"
    elif sq0_v2r1_transport_ready:
        readiness_status = "SQ0_V2R1_TRANSPORT_QUALIFICATION_AUTHORIZED_READY"
        blocker = "SQ0-V2 was voided before any AppWorld action because the official AtomCode coding-agent schema exposed native read_file; V2-R1 uses fresh cases and must first pass a non-scientific AppWorld-MCP tool-routing qualification."
        next_action = "RUN_SQ0_V2R1_TRANSPORT_QUALIFICATION"
    elif sq0_v2_execution_authorized:
        readiness_status = "SQ0_V2_TARGET_FAILURE_QUALIFICATION_AUTHORIZED_READY"
        blocker = None
        next_action = "RUN_SQ0_V2_MIMO25PRO"
    elif sq0_v1_closed:
        readiness_status = "SQ0_TARGET_CHALLENGE_TOO_EASY_STOP"
        blocker = "SQ0-V1 completed without interface/cap contamination but MiMo 2.5 Pro succeeded on all 12 development target challenges, yielding zero usable target failures."
        next_action = "DESIGN_FRESH_SQ0_V2_TARGET_CHALLENGE"
    elif sq0_execution_authorized:
        readiness_status = "SQ0_TARGET_FAILURE_QUALIFICATION_AUTHORIZED_READY"
        blocker = None
        next_action = "RUN_SQ0_MIMO25PRO_V1"
    elif f0_uptake_failed:
        readiness_status = "F0_UPDATE_UPTAKE_FAIL"
        blocker = "All eight frozen target-isolated F0 source episodes succeeded, so no repair note could be generated and the preregistered minimum of six eligible repair families was not met."
        next_action = (
            "STOP_CURRENT_F0_REVIEW_PROSPECTIVE_SOURCE_FAILURE_QUALIFICATION_PROPOSAL"
            if f0_r1_proposal
            else "STOP_F0_NO_PROBE_NO_P1_REDESIGN_SOURCE_FAILURE_SUBSTRATE"
        )
    elif f0_source_authorized:
        readiness_status = "F0_SOURCE_AUTHORIZED_READY"
        blocker = None
        next_action = "RUN_F0_SOURCE_MIMO25PRO"
    elif final_backbone_selected:
        readiness_status = "CAPABILITY_CALIBRATION_PASS_F0_AUTHORIZATION_REQUIRED"
        blocker = (
            "The predeclared backbone search selected AtomGit mimo-v2.5-pro after a valid 8-unit capability PASS. "
            "Backbone selection is frozen, but capability selection never self-authorizes F0."
        )
        next_action = "STOP_AWAIT_HUMAN_F0_AUTHORIZATION"
    elif backbone_search_b3_active:
        readiness_status = backbone_search_state_b3["status"]
        blocker = (
            "No eligible backbone has been selected yet: Qwen3.7-Plus, CodingPlan Qwen3.8-27B, GLM-5.2, and mimo-v2.5 are ceiling candidates, "
            "while CodingPlan DeepSeek-v4-flash is a floor candidate. The final predeclared candidate mimo-v2.5-pro remains."
        )
        next_action = "FREEZE_AND_RUN_CODINGPLAN_MIMO25PRO_CAPABILITY_B3"
    elif backbone_search_b2_active:
        readiness_status = backbone_search_state_b2["status"]
        blocker = (
            "No eligible backbone has been selected yet: Qwen3.7-Plus, CodingPlan Qwen3.8-27B, and GLM-5.2 are ceiling candidates, "
            "while CodingPlan DeepSeek-v4-flash is a floor candidate. The remaining order was frozen before any mimo-v2.5 scientific dispatch."
        )
        next_action = "FREEZE_AND_RUN_CODINGPLAN_MIMO25_CAPABILITY_B2"
    elif backbone_search_active:
        readiness_status = backbone_search_state["status"]
        blocker = (
            "No eligible backbone has been selected yet: Qwen3.7-Plus and CodingPlan Qwen3.8-27B are ceiling candidates, "
            "while CodingPlan DeepSeek-v4-flash is a floor candidate because frozen tool-loop completion is below threshold. "
            "The remaining candidate order was frozen before any GLM-5.2 scientific dispatch."
        )
        next_action = "FREEZE_AND_RUN_CODINGPLAN_GLM52_CAPABILITY_B1"
    elif both_valid_candidates_ceiling:
        readiness_status = "CAPABILITY_MODEL_SELECTION_NO_ELIGIBLE_BACKBONE_ALL_CEILING_STOP"
        blocker = (
            "Both valid post-repair candidates are above the frozen target-success ceiling: "
            "Qwen3.7-Plus under the direct AppWorld harness and CodingPlan Qwen3.8-27B under AtomCode MCP. "
            "No F0 backbone is selected."
        )
        next_action = "STOP_AWAIT_HUMAN_BACKBONE_SELECTION"
    elif capability_status:
        readiness_status = capability_status
        blocker = (
            "Capability calibration terminated at its frozen stop rule; "
            "F0 remains unauthorized."
        )
        next_action = "STOP_AWAIT_HUMAN_ADJUDICATION"
    elif r3_partial_void_active and substrate_v4_recovery_pass and r5_partial_authorized:
        readiness_status = "CAPABILITY_SUBSTRATE_V4_PARTIAL_REQUALIFICATION_READY"
        blocker = None
        next_action = "RUN_QWEN37PLUS_CAPABILITY_R5_PARTIAL_TNF_ONLY"
    elif r3_partial_void_active:
        readiness_status = "CAPABILITY_SUBSTRATE_V4_RECOVERY_REQUIRED"
        blocker = (
            "R3 partial TNF measurements are void because FileSystem path/filename semantics "
            "and the zero-headroom 12-call budget were not a valid capability substrate."
        )
        next_action = "QUALIFY_CAPABILITY_SUBSTRATE_V4"
    elif r2_void_active and substrate_v2_recovery_pass and r3_partial_authorized:
        readiness_status = "CAPABILITY_SUBSTRATE_V2_PARTIAL_REQUALIFICATION_READY"
        blocker = None
        next_action = "RUN_QWEN37PLUS_CAPABILITY_R3_PARTIAL_TNF_ONLY"
    elif r2_void_active and substrate_v2_recovery_pass and r3_authorized:
        readiness_status = "CAPABILITY_SUBSTRATE_V2_REQUALIFICATION_READY"
        blocker = "Full eight-unit R3 contract is superseded when a narrower partial contract is present."
        next_action = "FREEZE_PARTIAL_R3_OR_STOP"
    elif r2_void_active:
        readiness_status = "CAPABILITY_SUBSTRATE_V2_RECOVERY_REQUIRED"
        blocker = (
            "Plus R2 is void because target-note discoverability and File/Gmail evaluator fidelity were invalid."
        )
        next_action = "QUALIFY_CAPABILITY_SUBSTRATE_V2"
    elif substrate_void_active and substrate_recovery_pass and r2_authorized:
        readiness_status = "CAPABILITY_SUBSTRATE_REQUALIFICATION_READY"
        blocker = None
        next_action = "RUN_QWEN37PLUS_CAPABILITY_R2"
    elif substrate_void_active:
        readiness_status = "CAPABILITY_SUBSTRATE_RECOVERY_REQUIRED"
        blocker = "Prior capability results are void because the AppWorld task substrate was invalid."
        next_action = "QUALIFY_CAPABILITY_SUBSTRATE_RECOVERY"
    elif not provider_ready:
        readiness_status = "QWEN_PROVIDER_CONFIGURATION_REQUIRED"
        blocker = "AA_API_KEY is not configured in the approved environment."
        next_action = "CONFIGURE_QWEN_PROVIDER_CREDENTIAL"
    else:
        readiness_status = "CAPABILITY_CALIBRATION_READY"
        blocker = None
        next_action = "RUN_QWEN_CAPABILITY_CALIBRATION"
    readiness = {
        "schema_version": "agent-constraint-externality-f0-readiness-v1",
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "status": readiness_status,
        "compiler_verdict": qualification["verdict"],
        "compiler_pass_conditions_all_true": all(
            qualification["pass_conditions"].values()
        ),
        "model_prereg_addendum_a0_pass": True,
        "m1_runner_qualification_pass": m1_pass,
        "capability_contract_frozen": True,
        "capability_prior_results_void_substrate_invalid": substrate_void_active or r2_void_active,
        "capability_substrate_recovery_qualification_pass": substrate_recovery_pass,
        "capability_r2_authorized": r2_authorized,
        "capability_r2_void_substrate_discoverability_invalid": r2_void_active,
        "capability_substrate_v2_recovery_qualification_pass": substrate_v2_recovery_pass,
        "capability_r3_authorized": r3_authorized,
        "capability_r3_partial_authorized": r3_partial_authorized,
        "capability_r3_full_contract_superseded": r3_partial_authorized,
        "capability_r3_preserved_fg_measurements": int(capability_result.get("preserved_fg_measurements", 0)),
        "capability_r3_rerun_tnf_measurements": int(capability_result.get("rerun_tnf_measurements", 0)),
        "capability_r3_partial_void_substrate_filesystem_filename_invalid": r3_partial_void_active,
        "capability_substrate_v4_recovery_qualification_pass": substrate_v4_recovery_pass,
        "capability_r5_partial_authorized": r5_partial_authorized,
        "capability_preserved_fg_measurements": 4 if r3_partial_void_active else int(
            capability_result.get("preserved_fg_measurements", 0)
        ),
        "capability_rerun_tnf_measurements": int(
            capability_result.get("rerun_tnf_measurements", 0)
        ),
        "capability_result_status": capability_status,
        "capability_result_artifact": (
            str(capability_result_path.relative_to(ROOT))
            if capability_result_path.is_file()
            else None
        ),
        "direct_api_capability_result_status": capability_status,
        "direct_api_capability_result_artifact": (
            str(capability_result_path.relative_to(ROOT))
            if capability_result_path.is_file()
            else None
        ),
        "codingplan_capability_result_status": codingplan_status,
        "codingplan_capability_result_artifact": (
            str(CODINGPLAN_QWEN38_RESULT.relative_to(ROOT))
            if CODINGPLAN_QWEN38_RESULT.is_file()
            else None
        ),
        "codingplan_capability_closeout_status": codingplan_closeout.get("status"),
        "codingplan_capability_closeout_artifact": (
            str(CODINGPLAN_QWEN38_CLOSEOUT.relative_to(ROOT))
            if CODINGPLAN_QWEN38_CLOSEOUT.is_file()
            else None
        ),
        "codingplan_capability_valid_measurements": int(
            codingplan_result.get("valid_capability_measurements", 0)
        ),
        "codingplan_model_profile": codingplan_result.get("model_profile"),
        "codingplan_model_id": codingplan_result.get("model_id"),
        "codingplan_harness": codingplan_result.get("harness"),
        "codingplan_scientific_model_round_count": int(
            codingplan_accounting.get("scientific_model_round_count", 0)
        ),
        "codingplan_account_window_request_delta": int(
            codingplan_accounting.get("codingplan_account_window_request_delta", 0)
        ),
        "codingplan_account_level_unattributed_request_count": int(
            codingplan_accounting.get("account_level_unattributed_request_count", 0)
        ),
        "codingplan_appworld_tool_call_total": int(
            codingplan_accounting.get("appworld_tool_call_total", 0)
        ),
        "codingplan_prompt_tokens_total": int(
            codingplan_accounting.get("prompt_tokens_total", 0)
        ),
        "codingplan_completion_tokens_total": int(
            codingplan_accounting.get("completion_tokens_total", 0)
        ),
        "codingplan_request_accounting_domain": "CODINGPLAN_ACCOUNT_WINDOW_DO_NOT_SUM_WITH_DIRECT_API_PROVIDER_CALLS",
        "deepseek_capability_result_status": deepseek_status,
        "deepseek_capability_result_artifact": (
            str(CODINGPLAN_DEEPSEEK_RESULT.relative_to(ROOT))
            if CODINGPLAN_DEEPSEEK_RESULT.is_file()
            else None
        ),
        "deepseek_capability_closeout_status": deepseek_closeout.get("status"),
        "deepseek_capability_closeout_artifact": (
            str(CODINGPLAN_DEEPSEEK_CLOSEOUT.relative_to(ROOT))
            if CODINGPLAN_DEEPSEEK_CLOSEOUT.is_file()
            else None
        ),
        "deepseek_scientific_model_round_count": int(
            deepseek_closeout.get("accounting", {}).get("scientific_model_round_count", 0)
        ),
        "deepseek_account_window_request_delta": int(
            deepseek_closeout.get("accounting", {}).get("codingplan_account_window_request_delta", 0)
        ),
        "deepseek_tool_loop_completion_rate": (
            deepseek_result.get("gate", {}).get("tool_loop_completion_rate")
        ),
        "deepseek_target_success_rate": deepseek_result.get("gate", {}).get("target_success_rate"),
        "backbone_search_state_status": backbone_search_state.get("status"),
        "backbone_search_state_artifact": (
            str(BACKBONE_SEARCH_STATE_B1.relative_to(ROOT))
            if BACKBONE_SEARCH_STATE_B1.is_file()
            else None
        ),
        "backbone_search_remaining_frozen_order": backbone_search_state.get(
            "remaining_frozen_order", []
        ),
        "backbone_search_next_candidate": backbone_search_state.get("next_candidate"),
        "codingplan_catalog_b1_artifact": (
            str(CODINGPLAN_CATALOG_B1.relative_to(ROOT))
            if CODINGPLAN_CATALOG_B1.is_file()
            else None
        ),
        "glm52_capability_result_status": glm52_status,
        "glm52_capability_result_artifact": (
            str(CODINGPLAN_GLM52_RESULT.relative_to(ROOT))
            if CODINGPLAN_GLM52_RESULT.is_file()
            else None
        ),
        "glm52_capability_closeout_status": glm52_closeout.get("status"),
        "glm52_capability_closeout_artifact": (
            str(CODINGPLAN_GLM52_CLOSEOUT.relative_to(ROOT))
            if CODINGPLAN_GLM52_CLOSEOUT.is_file()
            else None
        ),
        "glm52_scientific_model_round_count": int(
            glm52_closeout.get("accounting", {}).get("scientific_model_round_count", 0)
        ),
        "glm52_account_window_request_delta": int(
            glm52_closeout.get("accounting", {}).get("codingplan_account_window_request_delta", 0)
        ),
        "glm52_tool_loop_completion_rate": glm52_result.get("gate", {}).get("tool_loop_completion_rate"),
        "glm52_target_success_rate": glm52_result.get("gate", {}).get("target_success_rate"),
        "backbone_search_state_b2_status": backbone_search_state_b2.get("status"),
        "backbone_search_state_b2_artifact": (
            str(BACKBONE_SEARCH_STATE_B2.relative_to(ROOT))
            if BACKBONE_SEARCH_STATE_B2.is_file()
            else None
        ),
        "backbone_search_b2_remaining_frozen_order": backbone_search_state_b2.get(
            "remaining_frozen_order", []
        ),
        "backbone_search_b2_next_candidate": backbone_search_state_b2.get("next_candidate"),
        "mimo25_capability_result_status": mimo25_status,
        "mimo25_capability_result_artifact": (
            str(CODINGPLAN_MIMO25_RESULT.relative_to(ROOT))
            if CODINGPLAN_MIMO25_RESULT.is_file()
            else None
        ),
        "mimo25_capability_closeout_status": mimo25_closeout.get("status"),
        "mimo25_capability_closeout_artifact": (
            str(CODINGPLAN_MIMO25_CLOSEOUT.relative_to(ROOT))
            if CODINGPLAN_MIMO25_CLOSEOUT.is_file()
            else None
        ),
        "mimo25_scientific_model_round_count": int(
            mimo25_closeout.get("accounting", {}).get("scientific_model_round_count", 0)
        ),
        "mimo25_account_window_request_delta": int(
            mimo25_closeout.get("accounting", {}).get("codingplan_account_window_request_delta", 0)
        ),
        "mimo25_tool_loop_completion_rate": mimo25_result.get("gate", {}).get("tool_loop_completion_rate"),
        "mimo25_target_success_rate": mimo25_result.get("gate", {}).get("target_success_rate"),
        "backbone_search_state_b3_status": backbone_search_state_b3.get("status"),
        "backbone_search_state_b3_artifact": (
            str(BACKBONE_SEARCH_STATE_B3.relative_to(ROOT))
            if BACKBONE_SEARCH_STATE_B3.is_file()
            else None
        ),
        "backbone_search_b3_remaining_frozen_order": backbone_search_state_b3.get(
            "remaining_frozen_order", []
        ),
        "backbone_search_b3_next_candidate": backbone_search_state_b3.get("next_candidate"),
        "mimo25pro_capability_result_status": mimo25pro_status,
        "mimo25pro_capability_result_artifact": (
            str(CODINGPLAN_MIMO25PRO_RESULT.relative_to(ROOT))
            if CODINGPLAN_MIMO25PRO_RESULT.is_file()
            else None
        ),
        "mimo25pro_capability_closeout_status": mimo25pro_closeout.get("status"),
        "mimo25pro_capability_closeout_artifact": (
            str(CODINGPLAN_MIMO25PRO_CLOSEOUT.relative_to(ROOT))
            if CODINGPLAN_MIMO25PRO_CLOSEOUT.is_file()
            else None
        ),
        "mimo25pro_scientific_model_round_count": int(
            mimo25pro_closeout.get("accounting", {}).get("scientific_model_round_count", 0)
        ),
        "mimo25pro_account_window_request_delta": int(
            mimo25pro_closeout.get("accounting", {}).get("codingplan_account_window_request_delta", 0)
        ),
        "mimo25pro_account_level_unattributed_request_count": int(
            mimo25pro_closeout.get("accounting", {}).get("account_level_unattributed_request_count", 0)
        ),
        "mimo25pro_tool_loop_completion_rate": mimo25pro_result.get("gate", {}).get("tool_loop_completion_rate"),
        "mimo25pro_target_success_rate": mimo25pro_result.get("gate", {}).get("target_success_rate"),
        "final_backbone_selection_status": final_backbone_selection.get("status"),
        "final_backbone_selection_artifact": (
            str(FINAL_BACKBONE_SELECTION.relative_to(ROOT))
            if FINAL_BACKBONE_SELECTION.is_file()
            else None
        ),
        "selected_backbone": final_backbone_selection.get("selected_backbone"),
        "selected_backbone_capability_result_status": (
            mimo25pro_status if final_backbone_selected else None
        ),
        "f0_human_authorization_status": f0_human_authorization.get("status"),
        "f0_human_authorization_artifact": (
            str(F0_HUMAN_AUTHORIZATION.relative_to(ROOT))
            if F0_HUMAN_AUTHORIZATION.is_file()
            else None
        ),
        "f0_transport_addendum_status": f0_transport_addendum.get("status"),
        "f0_mcp_q1_status": f0_q1.get("status"),
        "f0_mcp_q1_model_requests": f0_q1.get("codingplan_model_requests"),
        "f0_source_contract_status": f0_source_contract.get("status"),
        "f0_source_closeout_status": f0_source_closeout.get("status"),
        "f0_adjudication_verdict": f0_adjudication.get("verdict"),
        "f0_uptake_root_cause_status": f0_uptake_root_cause.get("status"),
        "f0_uptake_root_cause_classification": f0_uptake_root_cause.get("classification"),
        "f0_uptake_root_cause_artifact": (
            str(F0_UPTAKE_ROOT_CAUSE.relative_to(ROOT))
            if F0_UPTAKE_ROOT_CAUSE.is_file()
            else None
        ),
        "f0_r1_proposal_status": f0_r1_proposal.get("status"),
        "f0_r1_proposal_artifact": (
            str(F0_R1_PROPOSAL.relative_to(ROOT))
            if F0_R1_PROPOSAL.is_file()
            else None
        ),
        "sq0_static_contract_status": sq0_static_contract.get("status"),
        "sq0_static_qualification_status": sq0_static_qualification.get("status"),
        "sq0_static_max_public_tool_calls": sq0_static_qualification.get("max_public_tool_calls"),
        "sq0_static_minimum_headroom": sq0_static_qualification.get("minimum_headroom"),
        "sq0_human_authorization_status": sq0_human_authorization.get("status"),
        "sq0_mcp_q1_status": sq0_q1.get("status"),
        "sq0_mcp_q1_model_requests": sq0_q1.get("codingplan_model_requests"),
        "sq0_execution_contract_status": sq0_execution_contract.get("status"),
        "sq0_v1_result_status": sq0_v1_result.get("status"),
        "sq0_v1_closeout_status": sq0_v1_closeout.get("status"),
        "sq0_v1_usable_target_failure_count": int(sq0_v1_result.get("usable_target_failure_count", 0)),
        "sq0_v1_usable_target_failure_rate": sq0_v1_result.get("usable_target_failure_rate"),
        "sq0_v1_scientific_model_round_count": int(sq0_v1_result.get("scientific_model_round_count", 0)),
        "sq0_v1_appworld_tool_call_total": int(sq0_v1_result.get("appworld_tool_call_total", 0)),
        "sq0_v2_static_contract_status": sq0_v2_static_contract.get("status"),
        "sq0_v2_static_qualification_status": sq0_v2_static_qualification.get("status"),
        "sq0_v2_static_max_public_tool_calls": sq0_v2_static_qualification.get("max_public_tool_calls"),
        "sq0_v2_static_minimum_headroom": sq0_v2_static_qualification.get("minimum_headroom"),
        "sq0_v2_human_authorization_status": sq0_v2_human_authorization.get("status"),
        "sq0_v2_mcp_q1_status": sq0_v2_q1.get("status"),
        "sq0_v2_mcp_q1_model_requests": sq0_v2_q1.get("codingplan_model_requests"),
        "sq0_v2_execution_contract_status": sq0_v2_execution_contract.get("status"),
        "sq0_v2_void_status": sq0_v2_void.get("status"),
        "sq0_v2_void_active": sq0_v2_void_active,
        "sq0_v2r1_static_contract_status": sq0_v2r1_static_contract.get("status"),
        "sq0_v2r1_static_qualification_status": sq0_v2r1_static_qualification.get("status"),
        "sq0_v2r1_static_max_public_tool_calls": sq0_v2r1_static_qualification.get("max_public_tool_calls"),
        "sq0_v2r1_static_minimum_headroom": sq0_v2r1_static_qualification.get("minimum_headroom"),
        "sq0_v2r1_transport_contract_status": sq0_v2r1_transport_contract.get("status"),
        "sq0_v2r1_transport_result_status": sq0_v2r1_transport_result.get("status"),
        "sq0_v2r1_transport_model_round_count": int(sq0_v2r1_transport_result.get("model_round_count", 0)),
        "sq0_v2r1_transport_native_tool_attempts": sq0_v2r1_transport_result.get("native_tool_attempts", []),
        "sq0_v2r1_transport_qualification_ready": sq0_v2r1_transport_ready,
        "sq0_v2r1_human_authorization_status": sq0_v2r1_human_authorization.get("status"),
        "sq0_v2r1_mcp_q1_status": sq0_v2r1_q1.get("status"),
        "sq0_v2r1_mcp_q1_model_requests": sq0_v2r1_q1.get("codingplan_model_requests"),
        "sq0_v2r1_execution_contract_status": sq0_v2r1_execution_contract.get("status"),
        "sq0_v2r1_execution_authorized": sq0_v2r1_execution_authorized,
        "sq0_v2r1_result_status": sq0_v2r1_result.get("status"),
        "sq0_v2r1_usable_target_failure_count": int(sq0_v2r1_result.get("usable_target_failure_count", 0)),
        "sq0_v2r1_usable_target_failure_rate": sq0_v2r1_result.get("usable_target_failure_rate"),
        "sq0_v2r1_non_semantic_failure_units": sq0_v2r1_result.get("non_semantic_failure_units", []),
        "sq0_v2r1_scientific_model_round_count": int(sq0_v2r1_result.get("scientific_model_round_count", 0)),
        "sq0_v2r1_closeout_status": sq0_v2r1_closeout.get("status"),
        "sq0_v2r1_root_cause_status": sq0_v2r1_root_cause.get("status"),
        "sq0_v2r1_semantic_failure_count": int(sq0_v2r1_root_cause.get("semantic_failure_count_after_terminal_newline_normalization", 0)),
        "sq0_v2r1_closed": sq0_v2r1_closed,
        "sq0_v3_static_contract_status": sq0_v3_static_contract.get("status"),
        "sq0_v3_static_qualification_status": sq0_v3_static_qualification.get("status"),
        "sq0_v3_static_max_public_tool_calls": sq0_v3_static_qualification.get("max_public_tool_calls"),
        "sq0_v3_static_minimum_headroom": sq0_v3_static_qualification.get("minimum_headroom"),
        "sq0_v3_human_authorization_status": sq0_v3_human_authorization.get("status"),
        "sq0_v3_mcp_q1_status": sq0_v3_q1.get("status"),
        "sq0_v3_mcp_q1_model_requests": sq0_v3_q1.get("codingplan_model_requests"),
        "sq0_v3_execution_contract_status": sq0_v3_execution_contract.get("status"),
        "sq0_v3_execution_authorized": sq0_v3_execution_authorized,
        "sq0_v2_execution_authorized": sq0_v2_execution_authorized,
        "sq0_execution_authorized": sq0_execution_authorized and not sq0_v1_closed,
        "f0_r1_sq0_execution_authorized": sq0_execution_authorized and not sq0_v1_closed,
        "f0_r1_execution_authorized": False,
        "f0_source_target_success_count": int(f0_source_closeout.get("source_target_success_count", 0)),
        "f0_source_target_failure_count": int(f0_source_closeout.get("source_target_failure_count", 0)),
        "f0_eligible_repair_family_count": int(f0_source_closeout.get("eligible_repair_family_count", 0)),
        "f0_source_scientific_model_round_count": int(f0_source_closeout.get("scientific_model_round_count", 0)),
        "f0_source_appworld_tool_call_total": int(f0_source_closeout.get("appworld_tool_call_total", 0)),
        "f0_probe_episode_count": int(f0_source_closeout.get("probe_episode_count", 0)),
        "capability_model_selection_state": (
            "SELECTED_MIMO25PRO_SQ0_V3_AUTHORIZED_AFTER_V2R1_CLOSEOUT"
            if sq0_v3_execution_authorized
            else "SELECTED_MIMO25PRO_SQ0_V2R1_TOO_EASY_CLOSED_V3_DESIGN_REQUIRED"
            if sq0_v2r1_closed
            else "SELECTED_MIMO25PRO_SQ0_V2R1_AUTHORIZED_AFTER_TRANSPORT_PASS"
            if sq0_v2r1_execution_authorized
            else "SELECTED_MIMO25PRO_SQ0_V2R1_TRANSPORT_READY_AFTER_V2_VOID"
            if sq0_v2r1_transport_ready
            else "SELECTED_MIMO25PRO_SQ0_V2_AUTHORIZED_AFTER_V1_TOO_EASY"
            if sq0_v2_execution_authorized
            else "SELECTED_MIMO25PRO_SQ0_V1_TOO_EASY_STOP"
            if sq0_v1_closed
            else "SELECTED_MIMO25PRO_SQ0_AUTHORIZED_AFTER_F0_UPTAKE_FAIL"
            if sq0_execution_authorized
            else "SELECTED_MIMO25PRO_F0_UPDATE_UPTAKE_FAIL"
            if f0_uptake_failed
            else "SELECTED_MIMO25PRO_F0_SOURCE_AUTHORIZED"
            if f0_source_authorized
            else "SELECTED_MIMO25PRO_PASS_F0_AUTHORIZATION_REQUIRED"
            if final_backbone_selected
            else "SEARCH_ACTIVE_QWEN_CEILING_DEEPSEEK_FLOOR_GLM52_CEILING_MIMO25_CEILING_MIMO25PRO_NEXT"
            if backbone_search_b3_active
            else "SEARCH_ACTIVE_QWEN_CEILING_DEEPSEEK_FLOOR_GLM52_CEILING_MIMO25_NEXT"
            if backbone_search_b2_active
            else "SEARCH_ACTIVE_QWEN_CEILING_DEEPSEEK_FLOOR_GLM52_NEXT"
            if backbone_search_active
            else "NO_ELIGIBLE_BACKBONE_BOTH_VALID_CANDIDATES_CEILING"
            if both_valid_candidates_ceiling
            else "ELIGIBLE_BACKBONE_SELECTED"
            if eligible_backbone_selected
            else "MODEL_SELECTION_INCOMPLETE"
        ),
        "eligible_backbone_selected": eligible_backbone_selected,
        "capability_valid_measurements": capability_result.get(
            "valid_capability_measurements", 0
        ),
        "capability_tool_cap_incomplete_measurements": capability_result.get(
            "tool_cap_incomplete_measurements", 0
        ),
        "capability_scheduled_agent_episode_count": capability_result.get(
            "scheduled_agent_episode_count", 0
        ),
        "capability_latest_attempt_agent_episode_count": latest_agent_episodes,
        "capability_historical_void_agent_episode_count": historical_void_agent_episodes,
        "capability_agent_episode_count": lineage_agent_episodes,
        "capability_terminal_agent_episode_count": capability_result.get(
            "terminal_agent_episode_count", 0
        ),
        "capability_latest_attempt_agent_model_request_count": latest_agent_requests,
        "capability_historical_void_agent_model_request_count": historical_void_agent_requests,
        "capability_agent_model_request_count": lineage_agent_requests,
        "capability_latest_attempt_provider_request_total": latest_provider_requests,
        "capability_historical_void_provider_request_total": historical_void_provider_requests,
        "capability_provider_request_total": lineage_provider_requests,
        "capability_scientific_outcomes_observed": capability_result.get(
            "scientific_outcomes_observed", 0
        ),
        "f0_contract_frozen": True,
        "provider": safe_provider,
        "execution_override": {
            "max_retries": 0,
            "note": "Frozen protocol overrides provider default for scientific calls.",
        },
        "provider_credential_present": provider_ready,
        "blocker": blocker,
        "next_authorized_action": next_action,
        "f0_executed": f0_uptake_failed,
        "f0_outcomes_observed": 8 if f0_uptake_failed else 0,
        "f0_source_outcomes_observed": 8 if f0_uptake_failed else 0,
        "f0_probe_effects_observed": 0,
        "tool_sandbox_authorized": False,
        "appworld_ul_authorized": False,
        "p1_authorized": False,
        "f0_authorized": f0_source_authorized and not f0_uptake_failed,
        "f0_authority_note": (
            "F0 source phase reached a mandatory uptake stop; probes, P1, ToolSandbox, and AppWorld-UL remain closed."
            if f0_uptake_failed
            else "User-authorized F0 source execution is open; probes remain closed until repair artifacts are frozen and separately sealed."
            if f0_source_authorized
            else "Capability PASS, if obtained, still requires separate human F0 authorization."
        ),
    }
    return {
        "agent-constraint-externality-capability-contract-20260831.json": capability,
        "agent-constraint-externality-f0-frozen-protocol-20260831.json": f0,
        "agent-constraint-externality-f0-readiness-20260831.json": readiness,
    }


def main() -> None:
    artifacts = build_artifacts()
    for name, payload in artifacts.items():
        write_json(GENERATED / name, payload)
    manifest_files = {
        str((GENERATED / name).relative_to(ROOT)): {
            "sha256": file_sha256(GENERATED / name),
            "bytes": (GENERATED / name).stat().st_size,
        }
        for name in artifacts
    }
    for path in (
        FAMILY_MANIFEST, COMPILER_QUALIFICATION, COMPILER_MANIFEST,
        MODEL_ADDENDUM, MODEL_ADDENDUM_MANIFEST, M1_QUALIFICATION, M1_MANIFEST,
    ):
        manifest_files[str(path.relative_to(ROOT))] = {
            "sha256": file_sha256(path),
            "bytes": path.stat().st_size,
        }
    for path in (
        CAPABILITY_RESULT, CAPABILITY_RESULT_MANIFEST, CAPABILITY_MODEL_SNAPSHOT,
        CAPABILITY_CONTINUATION_RESULT, CAPABILITY_A1_RESULT, CAPABILITY_A1_ADDENDUM,
        CAPABILITY_A1_SNAPSHOT, CAPABILITY_A1_MANIFEST, CAPABILITY_SUBSTRATE_VOID,
        CAPABILITY_SUBSTRATE_QUALIFICATION, CAPABILITY_R2_CONTRACT, CAPABILITY_R2_RESULT,
        CAPABILITY_SUBSTRATE_VOID_R2, CAPABILITY_SUBSTRATE_QUALIFICATION_R2,
        CAPABILITY_R3_CONTRACT, CAPABILITY_R3_RESULT, CAPABILITY_R3_PARTIAL_CONTRACT,
        CAPABILITY_R3_PARTIAL_RESULT, CAPABILITY_R2_FG_V2_REVALIDATION,
        CAPABILITY_SUBSTRATE_V2_CONTRACT, CAPABILITY_SUBSTRATE_V2_BUNDLE,
        CAPABILITY_R2_ROOT_CAUSE_AUDIT, CAPABILITY_R3_PARTIAL_VOID,
        CAPABILITY_SUBSTRATE_V3_CONTRACT, CAPABILITY_SUBSTRATE_QUALIFICATION_R3,
        CAPABILITY_SUBSTRATE_V3_BUNDLE, CAPABILITY_SUBSTRATE_V4_CONTRACT,
        CAPABILITY_SUBSTRATE_QUALIFICATION_R4, CAPABILITY_SUBSTRATE_V4_BUNDLE,
        CAPABILITY_R5_PARTIAL_CONTRACT, CAPABILITY_R5_PARTIAL_RESULT,
        CODINGPLAN_QWEN38_Q0, CODINGPLAN_QWEN38_Q1, CODINGPLAN_QWEN38_CONTRACT,
        CODINGPLAN_QWEN38_MANIFEST, CODINGPLAN_QWEN38_RESULT, CODINGPLAN_QWEN38_CLOSEOUT,
        CODINGPLAN_DEEPSEEK_RESULT, CODINGPLAN_DEEPSEEK_CLOSEOUT,
        CODINGPLAN_CATALOG_B1, BACKBONE_SEARCH_STATE_B1,
        CODINGPLAN_GLM52_RESULT, CODINGPLAN_GLM52_CLOSEOUT,
        BACKBONE_SEARCH_STATE_B2,
        CODINGPLAN_MIMO25_RESULT, CODINGPLAN_MIMO25_CLOSEOUT,
        BACKBONE_SEARCH_STATE_B3, CODINGPLAN_MIMO25PRO_RESULT,
        CODINGPLAN_MIMO25PRO_CLOSEOUT, FINAL_BACKBONE_SELECTION,
        F0_HUMAN_AUTHORIZATION, F0_TRANSPORT_ADDENDUM,
        F0_MIMO25PRO_Q1, F0_MIMO25PRO_SOURCE_CONTRACT,
        F0_REPAIRS_MANIFEST, F0_ADJUDICATION, F0_SOURCE_CLOSEOUT,
        F0_UPTAKE_ROOT_CAUSE, F0_R1_PROPOSAL,
        SQ0_STATIC_CONTRACT, SQ0_STATIC_QUALIFICATION, SQ0_HUMAN_AUTHORIZATION,
        SQ0_MIMO25PRO_Q1, SQ0_EXECUTION_CONTRACT, SQ0_V1_RESULT, SQ0_V1_CLOSEOUT,
        SQ0_V2_STATIC_CONTRACT, SQ0_V2_STATIC_QUALIFICATION, SQ0_V2_HUMAN_AUTHORIZATION,
        SQ0_V2_MIMO25PRO_Q1, SQ0_V2_EXECUTION_CONTRACT, SQ0_V2_VOID,
        SQ0_V2R1_STATIC_CONTRACT, SQ0_V2R1_STATIC_QUALIFICATION, SQ0_V2R1_TRANSPORT_CONTRACT,
        SQ0_V2R1_TRANSPORT_RESULT, SQ0_V2R1_HUMAN_AUTHORIZATION,
        SQ0_V2R1_MIMO25PRO_Q1, SQ0_V2R1_EXECUTION_CONTRACT,
        SQ0_V2R1_RESULT, SQ0_V2R1_CLOSEOUT, SQ0_V2R1_ROOT_CAUSE,
    ):
        if not path.is_file():
            continue
        manifest_files[str(path.relative_to(ROOT))] = {
            "sha256": file_sha256(path),
            "bytes": path.stat().st_size,
        }
    readiness = artifacts[
        "agent-constraint-externality-f0-readiness-20260831.json"
    ]
    manifest = {
        "schema_version": "agent-constraint-externality-f0-preflight-manifest-v1",
        "generated_at": GENERATED_AT,
        "object_id": OBJECT_ID,
        "status": readiness["status"],
        "files": manifest_files,
        "scientific_outcomes_observed": readiness["f0_outcomes_observed"],
        "provider_calls": readiness["capability_provider_request_total"],
        "provider_calls_accounting_domain": "DIRECT_API_ONLY",
        "codingplan_account_window_requests": readiness[
            "codingplan_account_window_request_delta"
        ],
        "codingplan_request_accounting_domain": readiness[
            "codingplan_request_accounting_domain"
        ],
        "deepseek_codingplan_account_window_requests": readiness[
            "deepseek_account_window_request_delta"
        ],
        "deepseek_codingplan_request_accounting_domain": (
            "CODINGPLAN_ACCOUNT_WINDOW_DEEPSEEK_B0_DO_NOT_SUM_WITH_DIRECT_API_PROVIDER_CALLS"
        ),
        "glm52_codingplan_account_window_requests": readiness[
            "glm52_account_window_request_delta"
        ],
        "glm52_codingplan_request_accounting_domain": (
            "CODINGPLAN_ACCOUNT_WINDOW_GLM52_B1_DO_NOT_SUM_WITH_DIRECT_API_PROVIDER_CALLS"
        ),
        "mimo25_codingplan_account_window_requests": readiness[
            "mimo25_account_window_request_delta"
        ],
        "mimo25_codingplan_request_accounting_domain": (
            "CODINGPLAN_ACCOUNT_WINDOW_MIMO25_B2_DO_NOT_SUM_WITH_DIRECT_API_PROVIDER_CALLS"
        ),
        "mimo25pro_codingplan_account_window_requests": readiness[
            "mimo25pro_account_window_request_delta"
        ],
        "mimo25pro_codingplan_request_accounting_domain": (
            "CODINGPLAN_ACCOUNT_WINDOW_MIMO25PRO_B3_DO_NOT_SUM_WITH_DIRECT_API_PROVIDER_CALLS"
        ),
        "selected_backbone": readiness["selected_backbone"],
        "gpu_runs": 0,
        "authority": {
            "m1_mock_qualification": not readiness["m1_runner_qualification_pass"],
            "capability_calibration": (
                readiness["m1_runner_qualification_pass"]
                and readiness["capability_result_status"] is None
            ),
            "f0": readiness["f0_authorized"],
            "toolsandbox": False,
            "appworld_ul": False,
            "p1": False,
            "method": False,
            "paper_claim": False,
        },
    }
    write_json(
        GENERATED / "agent-constraint-externality-f0-preflight-manifest-20260831.json",
        manifest,
    )
    print(json.dumps({
        "status": readiness["status"],
        "capability_family_count": len(CAPABILITY_FAMILIES),
        "f0_family_count": len(F0_FAMILIES),
        "capability_episode_cap": 8,
        "f0_source_episode_cap": 8,
        "f0_probe_episode_envelope": (
            len(F0_FAMILIES) * len(ARMS) * len(BRANCHES) * len(SEEDS)
        ),
        "agent_episode_total_max": 160,
        "scientific_outcomes_observed": readiness["f0_outcomes_observed"],
        "provider_calls": readiness["capability_provider_request_total"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
