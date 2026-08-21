from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponsesClient, ArkSettings, ArkResponseStateError
from research_pipeline.config import load_env_file

PAPER_ID = "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK"
PAPER_DIR = ROOT / "paper_drafts/d2-temporal-skill-bottleneck-iclr2027"
OUT = ROOT / "generated/d2-temporal-skill-bottleneck-post-repair-mock-pc-20260822"
CANON_ENV = Path("/home/wyt/code/agent-self-evolution-observatory/.env")
MODELS = ("deepseek-v4-pro", "kimi-k3")


def _load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _client(model: str) -> ArkResponsesClient:
    load_env_file(CANON_ENV)
    key = os.environ.get("ARK_API_KEY", "").strip()
    if not key:
        raise RuntimeError("ARK_API_KEY missing")
    base = ArkSettings.from_env()
    return ArkResponsesClient(ArkSettings(api_key=key, base_url=base.base_url, default_model=model, timeout_seconds=300.0, max_retries=0))


def _schema() -> list[dict[str, Any]]:
    props = {
        "recommendation": {"type": "string", "enum": ["strong_reject", "reject", "weak_reject", "borderline", "weak_accept", "accept", "strong_accept"]},
        "score_1_to_10": {"type": "integer", "minimum": 1, "maximum": 10},
        "submission_ready_as_manuscript": {"type": "boolean"},
        "evidence_debt_blocks_claim_truth": {"type": "boolean"},
        "evidence_debt_likely_blocks_acceptance": {"type": "boolean"},
        "control_operationalization_resolved": {"type": "boolean"},
        "unsupported_positive_c3_c4_result_claim_present": {"type": "boolean"},
        "decision_critical_objections": {"type": "array", "items": {"type": "object", "properties": {
            "id": {"type": "string"}, "text": {"type": "string"}, "resolved_in_manuscript": {"type": "boolean"}, "remaining_reason": {"type": "string"}
        }, "required": ["id", "text", "resolved_in_manuscript", "remaining_reason"], "additionalProperties": False}},
        "strongest_reject_reason": {"type": "string"},
        "highest_value_next_action": {"type": "string"},
        "submission_advice": {"type": "string", "enum": ["submit_with_evidence_debt", "hold_for_evidence", "manuscript_repair_required"]},
    }
    return [{"type": "function", "name": "submit_post_repair_review", "description": "Return the structured post-repair Mock PC review.", "parameters": {"type": "object", "properties": {"review": {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}}, "required": ["review"], "additionalProperties": False}}]


def _prompt() -> str:
    text = subprocess.run(["pdftotext", str(PAPER_DIR / "main.pdf"), "-"], check=True, text=True, capture_output=True).stdout
    packet = {
        "claim_ledger": _load("generated/d2-temporal-skill-bottleneck-claim-ledger.json"),
        "support_recheck": _load("generated/d2-temporal-skill-bottleneck-support-recheck-20260822.json"),
        "operationalization": _load("generated/d2-temporal-skill-bottleneck-operationalization-20260822.json"),
        "scoped_authorization": _load("generated/d2-temporal-skill-bottleneck-scoped-authorization-20260822.json"),
        "statement_evidence_binding": _load("generated/d2-temporal-skill-bottleneck-statement-evidence-binding-20260822.json"),
        "paper_qa": _load("generated/d2-temporal-skill-bottleneck-paper-qa.json"),
    }
    return f"""Act as a strict independent ICLR program-committee reviewer after targeted manuscript repair.
Judge scientific competitiveness and manuscript readiness separately. Missing first-party TimeSage-EV evaluated assets are an external support blocker with zero scientific authority. C3/C4 remain registered active unrefuted hypotheses and must not be credited as positive empirical results. Do not require the authors to substitute another benchmark. Check whether the repaired generic-skill control is now operationalized tightly enough to interpret a future targeted-minus-generic effect. Check whether the manuscript falsely claims that C3/C4 have already succeeded. A paper can be technically submission-ready while still likely to be rejected for empirical insufficiency; report both dimensions explicitly. Return exactly one submit_post_repair_review tool call.

PAPER ID: {PAPER_ID}

MANUSCRIPT:
{text}

AUDIT PACKET:
{json.dumps(packet, ensure_ascii=False)}
"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    prompt = _prompt()
    prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    ok = 0
    for model in MODELS:
        target = OUT / f"{model}.json"
        try:
            response = _client(model).respond(prompt, model=model, max_output_tokens=5000, tools=_schema(), thinking="disabled", store=True, allow_thinking_compatibility_fallback=True)
            calls = [x for x in response.get("function_calls") or [] if x.get("name") == "submit_post_repair_review"]
            if len(calls) != 1:
                raise RuntimeError(f"expected one review call, got {len(calls)}")
            review = json.loads(calls[0].get("arguments") or "{}").get("review") or {}
            rid = str(response.get("response_id") or "")
            row = {"schema_version": "1.0", "paper_id": PAPER_ID, "requested_model": model, "resolved_model": response.get("resolved_model"), "status": response.get("status"), "prompt_sha256": prompt_sha, "provider_response_id_archived_privately": bool(rid), "provider_response_id_sha256": hashlib.sha256(rid.encode()).hexdigest() if rid else "", "usage": response.get("usage") or {}, "review": review, "scientific_authority": False, "experiment_authority": False, "gpu_authority": False}
            ok += 1
        except ArkResponseStateError as exc:
            row = {"schema_version": "1.0", "paper_id": PAPER_ID, "requested_model": model, "status": "NONVOTING_PROVIDER_STATE_FAILURE", "prompt_sha256": prompt_sha, "provider_receipt": exc.receipt(), "scientific_authority": False, "experiment_authority": False, "gpu_authority": False}
        target.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"model": model, "status": row.get("status"), "review": row.get("review")}, ensure_ascii=False, indent=2))
    return 0 if ok == len(MODELS) else 2


if __name__ == "__main__":
    raise SystemExit(main())
