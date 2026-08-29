from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import importlib.metadata
import json
from typing import Any, Mapping, Sequence


TOKENIZER_PACKAGE = "tiktoken"
TOKENIZER_VERSION = "0.11.0"
TOKENIZER_ENCODING = "cl100k_base"
DEFAULT_CAP_TOKENS = 3072
HEAD_FRACTION = 1.0 / 3.0


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_trajectory_text(payload: Mapping[str, Any]) -> str:
    """Render updater evidence while excluding execution/provenance boilerplate.

    The system message is common across arms and consumes budget without carrying
    branch-specific evidence, so it is excluded. User/assistant/tool messages and
    verifier outcome are kept. Provider receipts, paths, timing, and identifiers
    remain in immutable raw artifacts but are not shown to the updater.
    """
    messages = []
    for message in payload.get("messages") or []:
        if not isinstance(message, Mapping):
            continue
        if str(message.get("role") or "") == "system":
            continue
        messages.append(dict(message))
    evidence = {
        "messages": messages,
        "score": payload.get("score"),
        "score_message": payload.get("score_message"),
    }
    return json.dumps(evidence, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def select_head_tail(tokens: Sequence[int], budget: int, *, head_fraction: float = HEAD_FRACTION) -> list[int]:
    if budget < 1:
        raise ValueError("budget must be positive")
    if not 0.0 < head_fraction < 1.0:
        raise ValueError("head_fraction must lie in (0,1)")
    values = list(tokens)
    if len(values) <= budget:
        return values
    head = max(1, int(budget * head_fraction))
    tail = budget - head
    if tail < 1:
        return values[:budget]
    return values[:head] + values[-tail:]


@dataclass(frozen=True)
class MatchedWindowReceipt:
    tokenizer_package: str
    tokenizer_version: str
    tokenizer_encoding: str
    cap_tokens: int
    head_fraction: float
    left_raw_tokens: int
    right_raw_tokens: int
    matched_tokens: int
    left_rendered_sha256: str
    right_rendered_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MatchedEvidenceWindowRenderer:
    """Pairwise-match evidence length before an updater sees either branch.

    For each WIN/MRW pair the budget is

        min(cap_tokens, len(WIN), len(MRW)).

    Both trajectories are then rendered to exactly that many cl100k_base tokens
    using the same one-third-head / two-thirds-tail rule. No padding or extra
    semantic content is introduced. The pairwise budget is a deterministic
    function of the already frozen search pool and therefore cannot depend on a
    downstream learning outcome.
    """

    def __init__(self, *, cap_tokens: int = DEFAULT_CAP_TOKENS) -> None:
        if cap_tokens < 1:
            raise ValueError("cap_tokens must be positive")
        try:
            observed_version = importlib.metadata.version(TOKENIZER_PACKAGE)
        except importlib.metadata.PackageNotFoundError as exc:
            raise RuntimeError(
                f"{TOKENIZER_PACKAGE}=={TOKENIZER_VERSION} is required for the frozen E2-R17 evidence renderer"
            ) from exc
        if observed_version != TOKENIZER_VERSION:
            raise RuntimeError(
                f"frozen E2-R17 renderer requires {TOKENIZER_PACKAGE}=={TOKENIZER_VERSION}, observed {observed_version}"
            )
        import tiktoken  # type: ignore

        self.encoding = tiktoken.get_encoding(TOKENIZER_ENCODING)
        self.cap_tokens = int(cap_tokens)

    def render_pair(self, left_text: str, right_text: str) -> tuple[str, str, MatchedWindowReceipt]:
        left_tokens = self.encoding.encode(left_text)
        right_tokens = self.encoding.encode(right_text)
        matched = min(self.cap_tokens, len(left_tokens), len(right_tokens))
        if matched < 1:
            raise ValueError("both evidence texts must contain at least one token")
        left_window = select_head_tail(left_tokens, matched)
        right_window = select_head_tail(right_tokens, matched)
        if len(left_window) != matched or len(right_window) != matched:
            raise AssertionError("pairwise evidence window is not token matched")
        left_rendered = self.encoding.decode(left_window)
        right_rendered = self.encoding.decode(right_window)
        receipt = MatchedWindowReceipt(
            tokenizer_package=TOKENIZER_PACKAGE,
            tokenizer_version=TOKENIZER_VERSION,
            tokenizer_encoding=TOKENIZER_ENCODING,
            cap_tokens=self.cap_tokens,
            head_fraction=HEAD_FRACTION,
            left_raw_tokens=len(left_tokens),
            right_raw_tokens=len(right_tokens),
            matched_tokens=matched,
            left_rendered_sha256=sha256_text(left_rendered),
            right_rendered_sha256=sha256_text(right_rendered),
        )
        return left_rendered, right_rendered, receipt
