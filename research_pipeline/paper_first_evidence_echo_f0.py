from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from . import p06_docatlas_evidence_runtime as p06
from .experiment_authority import validate_authority
from .resource_lease import list_gpu_leases

CANDIDATE_ID = "PA-01-EVIDENCE-ECHO"
CONTRACT_VERSION = "evidence-echo-f0-v2-full-prompt-parity"
ARMS = (
    "RAW_ONLY",
    "ECHO_EXTRACTIVE",
    "VERBATIM_DUPLICATE",
    "TOKEN_MATCHED_NEUTRAL",
    "DEDUP_WARNING",
)
UNANSWERABLE_TARGET = 64
ANSWERABLE_TARGET = 32
MAX_UNITS = UNANSWERABLE_TARGET + ANSWERABLE_TARGET
EXPECTED_REPAIRED_PLAN_SHA256 = "f7c1b8cce177a0efff84cfcf404ef436cf89ead1648548bcd6d633aa3c80a621"


def _encode(tok: Any, text: str) -> list[int]:
    return list(tok.encode(text, add_special_tokens=False))


def _decode(tok: Any, ids: list[int]) -> str:
    return str(tok.decode(ids, skip_special_tokens=True))


def _pad_to_tokens_preserve_prefix(tok: Any, source: str, target_n: int) -> str:
    """Append neutral suffix tokens without ever rewriting ``source``.

    Tokenizer encode/decode round-trips can normalize whitespace and punctuation.
    Evidence arms therefore keep their semantic payload as an exact string prefix
    and reach parity only by appending suffixes whose incremental token cost is 1.
    """
    text = str(source)
    current = len(_encode(tok, text))
    if current > target_n:
        raise ValueError(f"source-exceeds-target:{current}>{target_n}")
    fillers = (" metadata", " x", " .", " neutral", " padding", "\n")
    while current < target_n:
        for filler in fillers:
            candidate = text + filler
            new_count = len(_encode(tok, candidate))
            if new_count == current + 1:
                text = candidate
                current = new_count
                break
        else:
            raise RuntimeError(f"no-single-token-neutral-suffix:{current}->{target_n}")
    if len(_encode(tok, text)) != target_n or not text.startswith(str(source)):
        raise RuntimeError("prefix-preserving-token-padding-failed")
    return text


def _exact_token_prefix(tok: Any, source: str, target_n: int) -> str:
    """Return an exact character prefix encoding to ``target_n`` tokens.

    Fast tokenizers expose offsets, which avoids repeatedly encoding long document
    blocks. A deterministic binary-search fallback keeps the helper testable with
    lightweight tokenizers that only expose ``encode``/``decode``.
    """
    source = str(source)
    if target_n <= 0:
        return ""
    try:
        encoded = tok(source, add_special_tokens=False, return_offsets_mapping=True)
        input_ids = list(encoded.get("input_ids") or [])
        offsets = list(encoded.get("offset_mapping") or [])
        if len(input_ids) < target_n:
            raise ValueError("source-too-short-for-exact-token-prefix")
        if len(offsets) == len(input_ids) and target_n <= len(offsets):
            end = int(offsets[target_n - 1][1])
            prefix = source[:end]
            if len(_encode(tok, prefix)) == target_n:
                return prefix
    except TypeError:
        pass
    if len(_encode(tok, source)) < target_n:
        raise ValueError("source-too-short-for-exact-token-prefix")
    lo, hi = 0, len(source)
    while lo < hi:
        mid = (lo + hi) // 2
        if len(_encode(tok, source[:mid])) < target_n:
            lo = mid + 1
        else:
            hi = mid
    for end in range(max(0, lo - 32), min(len(source), lo + 32) + 1):
        prefix = source[:end]
        if len(_encode(tok, prefix)) == target_n:
            return prefix
    raise RuntimeError(f"exact-token-prefix-not-found:{target_n}")


def _verbatim_payload_prefix(tok: Any, source: str, target_n: int) -> tuple[str, int]:
    """Choose a real character prefix at target tokens, or exactly one token below.

    Some BPE/SentencePiece tokenizers have no character boundary whose standalone
    retokenization has exactly ``target_n`` tokens: a one-character extension can
    jump from N-1 directly to N+1.  That is an operational tokenization artifact,
    not a scientific treatment.  We therefore permit one bounded fallback to
    ``target_n-1`` and let the already-frozen neutral-suffix matcher restore exact
    *whole-note* token parity.  Larger shortfalls remain fail-closed.
    """
    try:
        prefix = _exact_token_prefix(tok, source, target_n)
        return prefix, target_n
    except RuntimeError as exact_error:
        if target_n <= 1:
            raise
        try:
            prefix = _exact_token_prefix(tok, source, target_n - 1)
        except RuntimeError:
            raise exact_error
        return prefix, target_n - 1


def _arm_note_drafts(tok: Any, pages: list[str], ids: list[int]) -> tuple[dict[str, str], int, str]:
    """Build non-RAW note arms without deleting evidence to obtain token parity.

    ECHO_EXTRACTIVE and DEDUP_WARNING contain exactly the same extractive payload.
    VERBATIM_DUPLICATE uses a contiguous visible-evidence character prefix matched
    to the extractive payload within at most one tokenizer-boundary token. The
    longest semantic arm determines the common note budget and shorter arms receive
    only neutral suffix padding; no evidence text is rewritten for token matching.
    """
    extractive = p06.extractive(pages, ids)
    payload_tokens = len(_encode(tok, extractive))
    verbatim_payload, _ = _verbatim_payload_prefix(tok, p06.raw_block(pages, ids), payload_tokens)
    drafts = {
        "ECHO_EXTRACTIVE": "Extractive note from visible text: " + extractive,
        "VERBATIM_DUPLICATE": "Duplicated visible evidence: " + verbatim_payload,
        "DEDUP_WARNING": (
            "REDUNDANCY NOTICE: The following content repeats already-visible evidence and must not be counted as independent support. "
            + extractive
        ),
    }
    target_n = max(len(_encode(tok, text)) for text in drafts.values())
    drafts["TOKEN_MATCHED_NEUTRAL"] = "Neutral control text."
    matched = {arm: _pad_to_tokens_preserve_prefix(tok, text, target_n) for arm, text in drafts.items()}
    if extractive not in matched["ECHO_EXTRACTIVE"] or extractive not in matched["DEDUP_WARNING"]:
        raise RuntimeError("extractive-payload-not-preserved-across-echo-and-dedup")
    if verbatim_payload not in matched["VERBATIM_DUPLICATE"]:
        raise RuntimeError("verbatim-payload-not-preserved")
    if any(len(_encode(tok, text)) != target_n for text in matched.values()):
        raise RuntimeError("nonraw-note-token-count-not-locked")
    return matched, target_n, extractive


def arm_note(tok: Any, arm: str, pages: list[str], ids: list[int]) -> tuple[str, int]:
    if arm == "RAW_ONLY":
        text = "Visible evidence may be incomplete. Use only visible pages. If insufficient, request more evidence or abstain."
        return text, len(_encode(tok, text))
    matched, target_n, _ = _arm_note_drafts(tok, pages, ids)
    if arm not in matched:
        raise ValueError(f"unknown arm:{arm}")
    return matched[arm], target_n


def _chat_input_token_count(tok: Any, prompt_text: str) -> int:
    rendered = tok.apply_chat_template(
        [{"role": "user", "content": prompt_text}],
        tokenize=False,
        add_generation_prompt=True,
    )
    return len(_encode(tok, rendered))


def _pad_note_for_full_prompt_parity(tok: Any, common: str, note: str, decision_tail: str, target_n: int) -> str:
    """Append neutral note suffixes until the final chat input reaches target_n.

    This matches what ``p06.gen`` actually sends after the chat template, avoiding
    one-token BPE boundary differences that can survive local note-token matching.
    Evidence/notice text is always an exact prefix of the repaired note.
    """
    text = str(note)
    fillers = (" .", " metadata", " x", " neutral", " padding", "\n")
    for _ in range(16):
        prompt_text = common + "\n\nPERSISTENT NOTE REPRESENTATION:\n" + text + decision_tail
        current = _chat_input_token_count(tok, prompt_text)
        if current == target_n:
            return text
        if current > target_n:
            raise RuntimeError(f"full-prompt-token-padding-overshoot:{current}>{target_n}")
        for filler in fillers:
            candidate = text + filler
            candidate_prompt = common + "\n\nPERSISTENT NOTE REPRESENTATION:\n" + candidate + decision_tail
            if _chat_input_token_count(tok, candidate_prompt) == target_n:
                return candidate
        # The current empirical contract only permits the observed one-token BPE
        # boundary repair. Fail closed instead of accumulating arbitrary padding.
        raise RuntimeError(f"no-full-prompt-neutral-padding:{current}->{target_n}")
    raise RuntimeError("full-prompt-token-padding-iteration-cap")


def render_arm_prompts(tok: Any, question: str, pages: list[str], ids: list[int], step: int) -> dict[str, tuple[str, str, int, int]]:
    """Render five arms and exactly match final chat tokens across non-RAW arms."""
    raw = p06.raw_block(pages, ids)
    matched, _, _ = _arm_note_drafts(tok, pages, ids)
    raw_note = "Visible evidence may be incomplete. Use only visible pages. If insufficient, request more evidence or abstain."
    notes = {"RAW_ONLY": raw_note, **matched}
    common = (
        f"You are a document agent under selective page access. Use no outside knowledge. The document has {len(pages)} pages.\n\n"
        f"QUESTION:\n{question}\n\nRAW VISIBLE PAGES:\n{raw}\n"
    )
    raw_hash = p06.htext(common)
    decision_tail = (
        f"\n\nChoose exactly one action: ANSWER, RETRIEVE_MORE, ABSTAIN, CONTINUE. Return one JSON object only with keys action and answer. For non-ANSWER set answer to empty string. Decision step {step} of 2."
    )
    provisional = {
        arm: common + "\n\nPERSISTENT NOTE REPRESENTATION:\n" + notes[arm] + decision_tail
        for arm in ARMS if arm != "RAW_ONLY"
    }
    target_input_tokens = max(_chat_input_token_count(tok, text) for text in provisional.values())
    for arm in ARMS:
        if arm == "RAW_ONLY":
            continue
        notes[arm] = _pad_note_for_full_prompt_parity(tok, common, notes[arm], decision_tail, target_input_tokens)
    rendered: dict[str, tuple[str, str, int, int]] = {}
    for arm in ARMS:
        note = notes[arm]
        prompt_text = common + "\n\nPERSISTENT NOTE REPRESENTATION:\n" + note + decision_tail
        rendered[arm] = (prompt_text, raw_hash, len(_encode(tok, note)), _chat_input_token_count(tok, prompt_text))
    nonraw_input_counts = {rendered[arm][3] for arm in ARMS if arm != "RAW_ONLY"}
    if len(nonraw_input_counts) != 1:
        raise RuntimeError("nonraw-full-prompt-token-count-not-locked")
    return rendered


def prompt(tok: Any, question: str, pages: list[str], ids: list[int], arm: str, step: int) -> tuple[str, str, int]:
    rendered = render_arm_prompts(tok, question, pages, ids, step)[arm]
    return rendered[0], rendered[1], rendered[2]


def select_units(plan: dict[str, Any]) -> list[dict[str, Any]]:
    un = [dict(row) for row in plan.get("units") or [] if row.get("class") == "unanswerable"]
    ans = [dict(row) for row in plan.get("units") or [] if row.get("class") == "answerable"]
    if len(un) < UNANSWERABLE_TARGET or len(ans) < ANSWERABLE_TARGET:
        raise ValueError("insufficient frozen units for evidence-echo F0")
    # Outcome-blind: preserve the parent plan order inside each benchmark truth class.
    chosen = un[:UNANSWERABLE_TARGET] + ans[:ANSWERABLE_TARGET]
    if len(chosen) != MAX_UNITS:
        raise ValueError("evidence-echo F0 unit cardinality drift")
    return chosen


def build_plan(parent_plan_path: Path, samples_path: Path) -> dict[str, Any]:
    parent, samples = p06.validate(parent_plan_path, samples_path)
    units = select_units(parent)
    return {
        "schema_version": "1.0-private",
        "candidate_id": CANDIDATE_ID,
        "contract_version": CONTRACT_VERSION,
        "parent_candidate_id": parent.get("candidate_id"),
        "parent_contract_sha256": parent.get("contract_sha256"),
        "parent_plan_sha256": p06.sha(parent_plan_path),
        "source_samples_sha256": p06.sha(samples_path),
        "selection": {
            "outcome_blind": True,
            "rule": "all 64 parent-plan unanswerable units plus first 32 answerable units in frozen parent-plan order",
            "unanswerable": UNANSWERABLE_TARGET,
            "answerable": ANSWERABLE_TARGET,
            "units": MAX_UNITS,
        },
        "arms": list(ARMS),
        "locked": [
            "question",
            "BM25 ranking",
            "raw visible page ids",
            "raw page character budget",
            "model snapshot",
            "temperature=0",
            "two decision steps",
            "retrieval expansion from top-3 to top-6",
            "final chat-input token count across the four non-RAW arms",
            "verbatim evidence payload may use at most one fewer token only when no exact character-prefix token boundary exists; neutral suffix restores final prompt parity",
        ],
        "truth_use": {
            "unanswerable label": "primary endpoint only",
            "answer field": "secondary exact-accuracy endpoint only",
            "evidence_pages": "not used by this F0",
        },
        "primary_endpoint": "paired false ANSWER on benchmark-unanswerable units",
        "secondary_endpoint": "paired exact answer correctness on answerable units",
        "decision_rule": {
            "double_counting_go": (
                "ECHO_EXTRACTIVE and VERBATIM_DUPLICATE each increase false-answer rate >=0.08 over RAW_ONLY, "
                "ECHO_EXTRACTIVE exceeds TOKEN_MATCHED_NEUTRAL by >=0.05, both echo-vs-raw and echo-vs-neutral exact paired p<0.05, "
                "and DEDUP_WARNING reduces false-answer rate >=0.05 versus ECHO_EXTRACTIVE without >0.03 answerable exact-accuracy loss."
            ),
            "summary_salience_go": (
                "ECHO_EXTRACTIVE increases false-answer rate >=0.08 over RAW_ONLY and >=0.05 over TOKEN_MATCHED_NEUTRAL with exact paired p<0.05, "
                "while VERBATIM_DUPLICATE remains within 0.03 of RAW_ONLY and DEDUP_WARNING recovers >=0.05."
            ),
            "stop_generic_prompt_shift": (
                "TOKEN_MATCHED_NEUTRAL is within 0.03 false-answer rate of ECHO_EXTRACTIVE, or ECHO_EXTRACTIVE fails its paired significance/effect gate, "
                "or the apparent safety recovery costs >0.03 answerable exact accuracy."
            ),
        },
        "gpu_authorized": False,
        "scientific_authority": False,
        "units": units,
        "samples_cardinality": len(samples),
    }


def canonical_plan_sha256(plan: dict[str, Any]) -> str:
    payload = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _visible_gpu_uuids() -> list[str]:
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,uuid", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("gpu-capability-check-cannot-query-nvidia-smi") from exc
    mapping: dict[str, str] = {}
    ordered: list[str] = []
    for raw in output.splitlines():
        if not raw.strip():
            continue
        index, uuid = [part.strip() for part in raw.split(",", 1)]
        mapping[index] = uuid
        mapping[uuid] = uuid
        ordered.append(uuid)
    visible = str(os.environ.get("CUDA_VISIBLE_DEVICES") or "").strip()
    if not visible:
        return ordered
    resolved: list[str] = []
    for token in (part.strip() for part in visible.split(",")):
        if not token:
            continue
        if token not in mapping:
            raise RuntimeError(f"gpu-capability-check-unknown-visible-device:{token}")
        resolved.append(mapping[token])
    if not resolved:
        raise RuntimeError("gpu-capability-check-no-visible-gpus")
    return resolved


def validate_execution_capability(
    *,
    plan: dict[str, Any],
    authority_root: Path,
    authority_id: str,
    run_id: str,
    plan_hash: str,
    server_id: str,
    gpu_lease_ids: list[str],
    visible_gpu_uuids: list[str] | None = None,
) -> dict[str, Any]:
    actual_plan_hash = canonical_plan_sha256(plan)
    if actual_plan_hash != EXPECTED_REPAIRED_PLAN_SHA256:
        raise RuntimeError(f"f0-plan-hash-drift:{actual_plan_hash}")
    if str(plan_hash) != actual_plan_hash:
        raise RuntimeError("f0-authority-plan-hash-mismatch")
    validation = validate_authority(authority_root, CANDIDATE_ID, authority_id, actual_plan_hash)
    if validation.get("valid") is not True:
        raise RuntimeError("f0-execution-requires-active-experiment-authority")
    authority = validation.get("authority") or {}
    if str(authority.get("run_id") or "") != str(run_id):
        raise RuntimeError("f0-execution-authority-run-mismatch")
    requested = [str(value) for value in gpu_lease_ids if str(value)]
    if not requested or len(set(requested)) != len(requested):
        raise RuntimeError("f0-execution-requires-explicit-unique-gpu-leases")
    active = {str(row.get("lease_id") or ""): row for row in list_gpu_leases(authority_root, True)}
    leases: list[dict[str, Any]] = []
    for lease_id in requested:
        row = active.get(lease_id)
        if not row:
            raise RuntimeError(f"f0-gpu-lease-not-active:{lease_id}")
        if (
            str(row.get("idea_id") or "") != CANDIDATE_ID
            or str(row.get("plan_hash") or "") != actual_plan_hash
            or str(row.get("run_id") or "") != str(run_id)
            or str(row.get("authority_id") or "") != str(authority_id)
            or str(row.get("server_id") or "") != str(server_id)
        ):
            raise RuntimeError(f"f0-gpu-lease-binding-mismatch:{lease_id}")
        leases.append(row)
    visible = list(visible_gpu_uuids) if visible_gpu_uuids is not None else _visible_gpu_uuids()
    leased = [str(row.get("gpu_uuid") or "") for row in leases]
    if len(visible) != len(set(visible)) or len(leased) != len(set(leased)):
        raise RuntimeError("f0-gpu-capability-duplicate-device")
    if set(visible) != set(leased):
        raise RuntimeError(f"f0-visible-gpu-lease-set-mismatch:visible={sorted(visible)} leased={sorted(leased)}")
    return {
        "valid": True,
        "idea_id": CANDIDATE_ID,
        "run_id": str(run_id),
        "plan_hash": actual_plan_hash,
        "authority_id": str(authority_id),
        "server_id": str(server_id),
        "gpu_lease_ids": requested,
        "gpu_uuids": visible,
    }


def exact_mcnemar(left: list[bool], right: list[bool]) -> dict[str, Any]:
    b = sum((not a) and c for a, c in zip(left, right))
    c = sum(a and (not z) for a, z in zip(left, right))
    n = b + c
    p = 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / (2**n))
    return {"left0_right1": b, "left1_right0": c, "discordant": n, "exact_two_sided_p": p}


def analyze_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by = {(str(row["unit_id"]), str(row["arm"])): row for row in rows}
    unit_ids = sorted({str(row["unit_id"]) for row in rows})
    un = [u for u in unit_ids if by[(u, "RAW_ONLY")]["class"] == "unanswerable"]
    ans = [u for u in unit_ids if by[(u, "RAW_ONLY")]["class"] == "answerable"]
    if len(un) != UNANSWERABLE_TARGET or len(ans) != ANSWERABLE_TARGET:
        return {"status": "INCONCLUSIVE_SUPPORT", "unanswerable": len(un), "answerable": len(ans), "scientific_authority": False}

    false = {arm: [bool(by[(u, arm)]["false_answer_unanswerable"]) for u in un] for arm in ARMS}
    correct = {arm: [bool(by[(u, arm)]["exact_correct"]) for u in ans] for arm in ARMS}
    false_rate = {arm: sum(values) / len(values) for arm, values in false.items()}
    exact_rate = {arm: sum(values) / len(values) for arm, values in correct.items()}
    pairs = {
        "raw_to_echo": exact_mcnemar(false["RAW_ONLY"], false["ECHO_EXTRACTIVE"]),
        "neutral_to_echo": exact_mcnemar(false["TOKEN_MATCHED_NEUTRAL"], false["ECHO_EXTRACTIVE"]),
        "raw_to_verbatim": exact_mcnemar(false["RAW_ONLY"], false["VERBATIM_DUPLICATE"]),
        "echo_to_dedup": exact_mcnemar(false["ECHO_EXTRACTIVE"], false["DEDUP_WARNING"]),
    }
    echo_raw = false_rate["ECHO_EXTRACTIVE"] - false_rate["RAW_ONLY"]
    echo_neutral = false_rate["ECHO_EXTRACTIVE"] - false_rate["TOKEN_MATCHED_NEUTRAL"]
    verbatim_raw = false_rate["VERBATIM_DUPLICATE"] - false_rate["RAW_ONLY"]
    dedup_recovery = false_rate["ECHO_EXTRACTIVE"] - false_rate["DEDUP_WARNING"]
    dedup_accuracy_loss = exact_rate["ECHO_EXTRACTIVE"] - exact_rate["DEDUP_WARNING"]
    echo_sig = pairs["raw_to_echo"]["exact_two_sided_p"] < 0.05
    neutral_sig = pairs["neutral_to_echo"]["exact_two_sided_p"] < 0.05
    double_go = bool(
        echo_raw >= 0.08
        and verbatim_raw >= 0.08
        and echo_neutral >= 0.05
        and echo_sig
        and neutral_sig
        and dedup_recovery >= 0.05
        and dedup_accuracy_loss <= 0.03
    )
    salience_go = bool(
        echo_raw >= 0.08
        and echo_neutral >= 0.05
        and echo_sig
        and neutral_sig
        and abs(verbatim_raw) <= 0.03
        and dedup_recovery >= 0.05
        and dedup_accuracy_loss <= 0.03
    )
    if double_go:
        decision = "GO_CORRELATED_EVIDENCE_DOUBLE_COUNTING_TO_CURRENT_SOURCE_REVIEW"
    elif salience_go:
        decision = "GO_EXTRACTIVE_SUMMARY_SALIENCE_TO_CURRENT_SOURCE_REVIEW"
    else:
        decision = "STOP_OR_HOLD_GENERIC_PROMPT_REDUCTION_NOT_BEATEN"
    return {
        "status": decision,
        "units": len(unit_ids),
        "unanswerable": len(un),
        "answerable": len(ans),
        "false_answer_rate": false_rate,
        "answerable_exact_rate": exact_rate,
        "effects": {
            "echo_minus_raw_false": echo_raw,
            "echo_minus_neutral_false": echo_neutral,
            "verbatim_minus_raw_false": verbatim_raw,
            "echo_minus_dedup_false_recovery": dedup_recovery,
            "dedup_answerable_exact_loss_vs_echo": dedup_accuracy_loss,
        },
        "paired_tests": pairs,
        "paper_problem_authorized": False,
        "method_authorized": False,
        "gpu_authorized": False,
        "scientific_authority": False,
    }


def run(
    *,
    parent_plan_path: Path,
    samples_path: Path,
    pdf_dir: Path,
    cache_dir: Path,
    model_path: Path,
    out_dir: Path,
    authority_root: Path,
    authority_id: str,
    run_id: str,
    plan_hash: str,
    server_id: str,
    gpu_lease_ids: list[str],
) -> dict[str, Any]:
    plan = build_plan(parent_plan_path, samples_path)
    capability = validate_execution_capability(
        plan=plan,
        authority_root=authority_root,
        authority_id=authority_id,
        run_id=run_id,
        plan_hash=plan_hash,
        server_id=server_id,
        gpu_lease_ids=gpu_lease_ids,
    )
    samples = p06.load(samples_path)
    torch, tok, model = p06.load_model(model_path)
    device_count = max(1, int(torch.cuda.device_count()))
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_path = out_dir / "plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pdf_manifest = p06.fetch_pdfs({"units": plan["units"]}, pdf_dir)
    rows: list[dict[str, Any]] = []
    raw_path = out_dir / "rows.jsonl"
    started = time.monotonic()
    generation_gpu_seconds = 0.0
    batch_calls = 0
    docs: dict[str, list[str]] = {}
    with raw_path.open("w", encoding="utf-8") as fh:
        for ordinal, unit in enumerate(plan["units"], 1):
            src = samples[int(unit["sample_index"])]
            doc = str(unit["doc_id"])
            pages = docs.get(doc)
            if pages is None:
                pages = p06.pages_of(pdf_dir / doc, cache_dir)
                docs[doc] = pages
            ranking = p06.bm25(str(src["question"]), pages)
            ids = ranking[: min(3, len(ranking))]
            rendered_by_arm = render_arm_prompts(tok, str(src["question"]), pages, ids, 1)
            rendered = [rendered_by_arm[arm] for arm in ARMS]
            raw_hashes = [item[1] for item in rendered]
            if len(set(raw_hashes)) != 1:
                raise RuntimeError("raw-visible-pages-not-locked")
            nonraw_input_counts = [rendered_by_arm[arm][3] for arm in ARMS if arm != "RAW_ONLY"]
            if len(set(nonraw_input_counts)) != 1:
                raise RuntimeError("nonraw-full-prompt-token-count-not-locked")
            t = time.monotonic()
            texts = p06.gen(torch, tok, model, [item[0] for item in rendered])
            p06.sync_cuda(torch)
            generation_gpu_seconds += p06.gpu_seconds(time.monotonic() - t, device_count)
            batch_calls += 1
            first = {arm: p06.parse(text) for arm, text in zip(ARMS, texts)}
            active = [arm for arm in ARMS if first[arm]["valid"] and first[arm]["action"] in {"RETRIEVE_MORE", "CONTINUE"}]
            second: dict[str, dict[str, Any]] = {}
            if active:
                ids2 = ranking[: min(6, len(ranking))]
                rendered2_by_arm = render_arm_prompts(tok, str(src["question"]), pages, ids2, 2)
                rendered2 = [rendered2_by_arm[arm] for arm in active]
                t = time.monotonic()
                texts2 = p06.gen(torch, tok, model, [item[0] for item in rendered2])
                p06.sync_cuda(torch)
                generation_gpu_seconds += p06.gpu_seconds(time.monotonic() - t, device_count)
                batch_calls += 1
                second = {arm: p06.parse(text) for arm, text in zip(active, texts2)}
            for arm, rendered_item in zip(ARMS, rendered):
                a = first[arm]
                b = second.get(arm)
                final = b if b and b["valid"] else a
                row = {
                    "unit_id": unit["unit_id"],
                    "sample_index": unit["sample_index"],
                    "class": unit["class"],
                    "doc_id": doc,
                    "arm": arm,
                    "question_sha256": unit["question_sha256"],
                    "raw_observation_sha256": rendered_item[1],
                    "initial_page_ids": ids,
                    "document_pages": len(pages),
                    "note_tokens": rendered_item[2],
                    "input_tokens": rendered_item[3],
                    "first_valid": a["valid"],
                    "first_action": a["action"],
                    "first_answer": a["answer"],
                    "second_valid": None if b is None else b["valid"],
                    "second_action": "" if b is None else b["action"],
                    "final_action": final["action"],
                    "final_answer": final["answer"],
                    "exact_correct": bool(final["valid"] and final["action"] == "ANSWER" and p06.exact(final["answer"], src["answer"])),
                    "false_answer_unanswerable": bool(unit["class"] == "unanswerable" and final["valid"] and final["action"] == "ANSWER"),
                    "parser_valid": bool(a["valid"] and (b is None or b["valid"])),
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                rows.append(row)
            fh.flush()
            if ordinal % 8 == 0:
                print(json.dumps({"completed_units": ordinal, "batch_calls": batch_calls, "generation_gpu_seconds": round(generation_gpu_seconds, 2)}), flush=True)
    analysis = analyze_rows(rows)
    analysis["cost"] = {
        "wall_seconds": round(time.monotonic() - started, 3),
        "batch_calls": batch_calls,
        "generation_gpu_seconds": round(generation_gpu_seconds, 3),
        "gpu_devices": device_count,
    }
    analysis["source"] = {
        "parent_plan_sha256": p06.sha(parent_plan_path),
        "samples_sha256": p06.sha(samples_path),
        "rows_sha256": p06.sha(raw_path),
        "pdf_manifest": pdf_manifest,
        "execution_capability": capability,
    }
    analysis_path = out_dir / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return analysis


def main() -> None:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--parent-plan", type=Path, required=True)
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--pdf-dir", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path, default=p06.DEFAULT_MODEL)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--authority-root", type=Path)
    parser.add_argument("--authority-id", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--plan-hash", default="")
    parser.add_argument("--server-id", default="")
    parser.add_argument("--gpu-lease-id", action="append", default=[])
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    if args.plan_only:
        print(json.dumps(build_plan(args.parent_plan, args.samples), ensure_ascii=False, indent=2))
        return
    if not args.authority_root or not args.authority_id or not args.run_id or not args.plan_hash or not args.server_id or not args.gpu_lease_id:
        parser.error("execution requires --authority-root --authority-id --run-id --plan-hash --server-id and at least one --gpu-lease-id")
    print(
        json.dumps(
            run(
                parent_plan_path=args.parent_plan,
                samples_path=args.samples,
                pdf_dir=args.pdf_dir,
                cache_dir=args.cache_dir,
                model_path=args.model,
                out_dir=args.out_dir,
                authority_root=args.authority_root,
                authority_id=args.authority_id,
                run_id=args.run_id,
                plan_hash=args.plan_hash,
                server_id=args.server_id,
                gpu_lease_ids=args.gpu_lease_id,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
