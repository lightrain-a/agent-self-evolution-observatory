from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import importlib.metadata
import json
from typing import Any, Mapping, Sequence


TOKENIZER_PACKAGE = "tiktoken"
TOKENIZER_VERSION = "0.11.0"
TOKENIZER_ENCODING = "cl100k_base"
FINAL_BLOCK_CAP_TOKENS = 3072
HEAD_FRACTION = 1.0 / 3.0
MIN_SELECTED_SOURCE_TOKENS = 64
BLOCK_HEADER = "E2-R17 SELECTED EXPERIENCE\n<EVIDENCE_HEAD>\n"
BLOCK_BOUNDARY = "\n</EVIDENCE_HEAD>\n<EVIDENCE_TAIL>\n"
BLOCK_FOOTER = "\n</EVIDENCE_TAIL>"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_trajectory_text(payload: Mapping[str, Any]) -> str:
    """Canonical branch evidence shown to the updater.

    Arm/projection identity, rollout index, provider metadata, paths, receipts and
    the common system prompt are deliberately absent.  The verifier score/message
    remain because whether the selected experience succeeded or failed is part of
    the scientific evidence treatment itself.
    """
    messages: list[dict[str, Any]] = []
    for message in payload.get("messages") or []:
        if not isinstance(message, Mapping):
            continue
        if str(message.get("role") or "") == "system":
            continue
        messages.append(dict(message))
    return json.dumps(
        {
            "messages": messages,
            "score": payload.get("score"),
            "score_message": payload.get("score_message"),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _safe_decode(encoding: Any, tokens: Sequence[int]) -> str:
    """Decode a token slice without inserting Unicode replacement characters."""
    if hasattr(encoding, "decode_bytes"):
        return encoding.decode_bytes(list(tokens)).decode("utf-8", errors="ignore")
    return encoding.decode(list(tokens))


def _candidate_block(encoding: Any, raw_tokens: Sequence[int], selected_budget: int) -> tuple[str, int]:
    if selected_budget < 2:
        raise ValueError("selected_budget must be at least two tokens")
    tokens = list(raw_tokens)
    selected_budget = min(int(selected_budget), len(tokens))
    head = max(1, int(selected_budget * HEAD_FRACTION))
    tail = selected_budget - head
    if tail < 1:
        tail = 1
        head = selected_budget - 1

    if selected_budget >= len(tokens):
        # Preserve all source tokens in order; the explicit boundary marker is
        # inserted at the deterministic one-third point for both arms.
        head_tokens = tokens[:head]
        tail_tokens = tokens[head:]
    else:
        head_tokens = tokens[:head]
        tail_tokens = tokens[-tail:]

    text = (
        BLOCK_HEADER
        + _safe_decode(encoding, head_tokens)
        + BLOCK_BOUNDARY
        + _safe_decode(encoding, tail_tokens)
        + BLOCK_FOOTER
    )
    actual = len(encoding.encode(text))
    return text, actual


@dataclass(frozen=True)
class ExactMatchedBlockReceipt:
    tokenizer_package: str
    tokenizer_version: str
    tokenizer_encoding: str
    final_block_cap_tokens: int
    head_fraction: float
    min_selected_source_tokens: int
    left_raw_source_tokens: int
    right_raw_source_tokens: int
    left_selected_source_tokens: int
    right_selected_source_tokens: int
    matched_final_block_tokens: int
    left_block_sha256: str
    right_block_sha256: str
    search_lower_bound: int
    search_candidates_left: int
    search_candidates_right: int
    padding_used: bool
    arm_metadata_visible: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExactMatchedEvidenceBlockRenderer:
    """Render two evidence blocks to the same *actual re-tokenized* length.

    V3's nominal token slicing failed because decoding and concatenating head/tail
    slices can create a fresh BPE merge at the splice.  V3.1 therefore searches
    deterministic source-token budgets for each arm and accepts only a pair whose
    final rendered UTF-8 texts re-encode to exactly the same token count under the
    frozen tokenizer.  No padding is used.  The largest common reachable final
    token count not exceeding `final_block_cap_tokens` is selected.

    The updater-visible wrapper is identical and arm-blinded.  Projection name,
    role, rollout index and provenance remain in receipts rather than the text the
    updater reasons over.
    """

    def __init__(self, *, final_block_cap_tokens: int = FINAL_BLOCK_CAP_TOKENS) -> None:
        if final_block_cap_tokens < MIN_SELECTED_SOURCE_TOKENS:
            raise ValueError("final block cap is too small")
        try:
            observed = importlib.metadata.version(TOKENIZER_PACKAGE)
        except importlib.metadata.PackageNotFoundError as exc:
            raise RuntimeError(
                f"{TOKENIZER_PACKAGE}=={TOKENIZER_VERSION} is required for the frozen E2-R17 V3.1 renderer"
            ) from exc
        if observed != TOKENIZER_VERSION:
            raise RuntimeError(
                f"frozen E2-R17 V3.1 renderer requires {TOKENIZER_PACKAGE}=={TOKENIZER_VERSION}, observed {observed}"
            )
        import tiktoken  # type: ignore

        self.encoding = tiktoken.get_encoding(TOKENIZER_ENCODING)
        self.final_block_cap_tokens = int(final_block_cap_tokens)

    def _reachable(
        self,
        raw_tokens: Sequence[int],
        *,
        start_budget: int,
        lower_bound: int,
    ) -> dict[int, tuple[int, str]]:
        reachable: dict[int, tuple[int, str]] = {}
        for budget in range(start_budget, lower_bound - 1, -1):
            text, actual = _candidate_block(self.encoding, raw_tokens, budget)
            if actual > self.final_block_cap_tokens:
                continue
            # For a given actual provider-visible length, keep the largest source
            # budget so the deterministic rule retains maximal evidence.
            reachable.setdefault(actual, (budget, text))
        return reachable

    def render_pair(self, left_text: str, right_text: str) -> tuple[str, str, ExactMatchedBlockReceipt]:
        left_raw = self.encoding.encode(left_text)
        right_raw = self.encoding.encode(right_text)
        if len(left_raw) < MIN_SELECTED_SOURCE_TOKENS or len(right_raw) < MIN_SELECTED_SOURCE_TOKENS:
            raise ValueError("both source evidences must contain at least 64 tokens")

        start = min(len(left_raw), len(right_raw), self.final_block_cap_tokens)
        # Search progressively wider deterministic windows.  The result is the
        # maximum common actual re-tokenized length, never a first-hit dependent
        # on arm order.
        lower_bounds = []
        for width in (32, 128, 512, 1024, start):
            lower = max(MIN_SELECTED_SOURCE_TOKENS, start - int(width))
            if not lower_bounds or lower != lower_bounds[-1]:
                lower_bounds.append(lower)
        if lower_bounds[-1] != MIN_SELECTED_SOURCE_TOKENS:
            lower_bounds.append(MIN_SELECTED_SOURCE_TOKENS)

        chosen: tuple[int, int, str, str, int, int, int] | None = None
        for lower in lower_bounds:
            left_map = self._reachable(left_raw, start_budget=start, lower_bound=lower)
            right_map = self._reachable(right_raw, start_budget=start, lower_bound=lower)
            common = set(left_map).intersection(right_map)
            if common:
                matched = max(common)
                left_budget, left_block = left_map[matched]
                right_budget, right_block = right_map[matched]
                chosen = (
                    left_budget,
                    right_budget,
                    left_block,
                    right_block,
                    matched,
                    len(left_map),
                    len(right_map),
                )
                search_lower_bound = lower
                break
        if chosen is None:
            raise RuntimeError("no exact common re-tokenized evidence-block length is reachable without padding")

        left_budget, right_budget, left_block, right_block, matched, left_n, right_n = chosen
        left_actual = len(self.encoding.encode(left_block))
        right_actual = len(self.encoding.encode(right_block))
        if left_actual != right_actual or left_actual != matched:
            raise AssertionError("V3.1 exact re-tokenized parity invariant failed")
        if matched > self.final_block_cap_tokens:
            raise AssertionError("V3.1 final block exceeded frozen cap")

        receipt = ExactMatchedBlockReceipt(
            tokenizer_package=TOKENIZER_PACKAGE,
            tokenizer_version=TOKENIZER_VERSION,
            tokenizer_encoding=TOKENIZER_ENCODING,
            final_block_cap_tokens=self.final_block_cap_tokens,
            head_fraction=HEAD_FRACTION,
            min_selected_source_tokens=MIN_SELECTED_SOURCE_TOKENS,
            left_raw_source_tokens=len(left_raw),
            right_raw_source_tokens=len(right_raw),
            left_selected_source_tokens=left_budget,
            right_selected_source_tokens=right_budget,
            matched_final_block_tokens=matched,
            left_block_sha256=sha256_text(left_block),
            right_block_sha256=sha256_text(right_block),
            search_lower_bound=search_lower_bound,
            search_candidates_left=left_n,
            search_candidates_right=right_n,
            padding_used=False,
            arm_metadata_visible=False,
        )
        return left_block, right_block, receipt
