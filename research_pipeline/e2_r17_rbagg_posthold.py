from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import re
from typing import Any, Mapping, Sequence


_MEMORY_ITEM_RE = re.compile(
    r"(?ms)^# Memory Item (?P<index>[1-5])\s*\n"
    r"## Title\s+(?P<title>[^\n]+)\s*\n"
    r"## Description\s+(?P<description>[^\n]+)\s*\n"
    r"## Content\s+(?P<content>.*?)(?=^# Memory Item [1-5]\s*$|\Z)"
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RBMemoryItem:
    index: int
    title: str
    description: str
    content: str

    def normalized(self) -> str:
        return (
            f"# Memory Item {self.index}\n"
            f"## Title {self.title.strip()}\n"
            f"## Description {self.description.strip()}\n"
            f"## Content {self.content.strip()}"
        )


@dataclass(frozen=True)
class RBAggregatedSessionEvidence:
    """One ReasoningBank-style summary of a frozen K=8 search session.

    The object is deliberately NOT called a trajectory.  It represents one
    task-level search session whose eight source trajectories are separately
    content-addressed by ``aggregation_receipt``. ``acting_score`` is the frozen
    user-facing best-of-K session outcome. It is the only score permitted when
    the precomputed aggregate is handed to MindMemOS's scored patch proposer.
    """

    task_id: str
    pool_id: str
    acting_score: float
    memory_items_markdown: str
    memory_items_sha256: str
    memory_item_count: int
    aggregation_receipt: Mapping[str, Any]

    def validate(self) -> None:
        if not self.task_id or not self.pool_id:
            raise ValueError("RB aggregate must bind task_id and pool_id")
        if self.acting_score not in (0.0, 1.0):
            raise ValueError("RB aggregate acting score must be binary")
        parsed = parse_rb_memory_items(self.memory_items_markdown)
        if len(parsed) != self.memory_item_count:
            raise ValueError("RB aggregate item count drift")
        normalized = normalize_rb_memory_items(parsed)
        if normalized != self.memory_items_markdown:
            raise ValueError("RB aggregate Markdown is not canonical")
        if sha256_text(self.memory_items_markdown) != self.memory_items_sha256:
            raise ValueError("RB aggregate Markdown SHA drift")
        sources = list(self.aggregation_receipt.get("sources") or [])
        if len(sources) != 8:
            raise ValueError("RB aggregate must bind exactly eight source trajectories")
        if len({int(row["rollout_index"]) for row in sources}) != 8:
            raise ValueError("RB aggregate rollout indices are not unique")
        if any(float(row["verifier_score"]) not in (0.0, 1.0) for row in sources):
            raise ValueError("RB aggregate source score is non-binary")
        observed = max(float(row["verifier_score"]) for row in sources)
        if observed != self.acting_score:
            raise ValueError("RB aggregate session score differs from frozen best-of-K outcome")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["aggregation_receipt"] = dict(self.aggregation_receipt)
        return payload


def parse_rb_memory_items(text: str) -> tuple[RBMemoryItem, ...]:
    """Strictly parse the official PARALLEL_SI Memory Item surface.

    We intentionally reject prose before/after the item blocks, skipped indices,
    duplicated indices, empty fields and more than five items. There is no parse
    correction or hidden retry in the scientific adapter.
    """

    raw = (text or "").strip()
    if not raw:
        raise ValueError("RB aggregation returned empty text")
    matches = list(_MEMORY_ITEM_RE.finditer(raw))
    if not matches:
        raise ValueError("RB aggregation did not emit official Memory Item blocks")
    prefix = raw[: matches[0].start()].strip()
    suffix = raw[matches[-1].end() :].strip()
    if prefix or suffix:
        raise ValueError("RB aggregation contains text outside Memory Item blocks")
    covered = "".join(match.group(0) for match in matches)
    # Normalizing whitespace by concatenation is not a reliable full-coverage
    # check, so verify every gap between matched blocks is whitespace only.
    previous = 0
    for match in matches:
        if raw[previous : match.start()].strip():
            raise ValueError("RB aggregation contains unparsed inter-item text")
        previous = match.end()
    if raw[previous:].strip():
        raise ValueError("RB aggregation contains unparsed trailing text")

    items: list[RBMemoryItem] = []
    for expected, match in enumerate(matches, start=1):
        index = int(match.group("index"))
        if index != expected:
            raise ValueError("RB Memory Item indices must be contiguous from one")
        title = match.group("title").strip()
        description = match.group("description").strip()
        content = match.group("content").strip()
        if not title or not description or not content:
            raise ValueError("RB Memory Item fields must be nonempty")
        items.append(RBMemoryItem(index=index, title=title, description=description, content=content))
    if not 1 <= len(items) <= 5:
        raise ValueError("RB aggregation must emit one to five Memory Items")
    return tuple(items)


def normalize_rb_memory_items(items: Sequence[RBMemoryItem]) -> str:
    if not items:
        raise ValueError("cannot normalize an empty RB Memory Item list")
    if len(items) > 5:
        raise ValueError("RB Memory Item list exceeds official cap")
    return "\n\n".join(item.normalized() for item in items)


def build_rb_aggregated_session_evidence(
    *,
    task_id: str,
    pool_id: str,
    acting_score: float,
    raw_memory_items: str,
    aggregation_receipt: Mapping[str, Any],
) -> RBAggregatedSessionEvidence:
    items = parse_rb_memory_items(raw_memory_items)
    normalized = normalize_rb_memory_items(items)
    unit = RBAggregatedSessionEvidence(
        task_id=task_id,
        pool_id=pool_id,
        acting_score=float(acting_score),
        memory_items_markdown=normalized,
        memory_items_sha256=sha256_text(normalized),
        memory_item_count=len(items),
        aggregation_receipt=dict(aggregation_receipt),
    )
    unit.validate()
    return unit


def build_rb_search_session_add_payload(
    *,
    unit: RBAggregatedSessionEvidence,
    project_id: str,
    task_completed_at: str,
    initial_skill_sha256: str,
    root_version_id: str,
    deterministic_add_record_id: str,
) -> dict[str, Any]:
    """Construct the 1:1 source record paired with a precomputed RB summary.

    The record explicitly says it represents a multi-trajectory search session.
    A runtime supervisor must assert that the matching precomputed summary exists
    before SkillEvolver is entered; direct trajectory summarization of this record
    is forbidden for the diagnostic child.
    """

    unit.validate()
    if not deterministic_add_record_id:
        raise ValueError("RB aggregate requires a deterministic add-record id")
    return {
        "add_record_id": deterministic_add_record_id,
        "project_id": project_id,
        "task_completed_at": task_completed_at,
        "messages": [
            {
                "role": "user",
                "content": (
                    "E2-R17 RB-AGG SEARCH-SESSION EVIDENCE\n"
                    "This is a precomputed ReasoningBank-style aggregation of one frozen K=8 task session, "
                    "not a single execution trajectory.\n\n"
                    + unit.memory_items_markdown
                ),
            }
        ],
        "score": float(unit.acting_score),
        "task_id": unit.task_id,
        "skill_bindings": [
            {
                "name": "xlsx",
                "content_hash": initial_skill_sha256,
                "version_id": root_version_id,
                "usage": "injected",
            }
        ],
        "r17_rbagg": True,
        "r17_rbagg_pool_id": unit.pool_id,
        "r17_rbagg_memory_items_sha256": unit.memory_items_sha256,
        "r17_rbagg_source_count": 8,
        "r17_rbagg_precomputed_summary_required": True,
        "r17_rbagg_direct_trajectory_summarization_forbidden": True,
    }


def build_rb_precomputed_summary_payload(
    *,
    unit: RBAggregatedSessionEvidence,
    project_id: str,
    cloud_skill_id: str,
    skill_name: str,
    deterministic_add_record_id: str,
    created_at: datetime,
) -> dict[str, Any]:
    """Build the payload corresponding to MindMemOS ``SkillTraceSummary``.

    The aggregate is inserted at the summary boundary, not misrepresented as a
    single rollout. Its score is the frozen best-of-K session outcome; therefore
    the standard scored patch proposer remains semantically truthful at the
    *session* level.
    """

    unit.validate()
    if not deterministic_add_record_id:
        raise ValueError("RB aggregate requires a deterministic add-record id")
    return {
        "summary_id": deterministic_add_record_id,
        "project_id": project_id,
        "cloud_skill_id": cloud_skill_id,
        "add_record_id": deterministic_add_record_id,
        "skill_name": skill_name,
        "summary": unit.memory_items_markdown,
        "created_at": created_at,
        "consumed_version_id": None,
        "score": float(unit.acting_score),
        "task_id": unit.task_id,
        "r17_semantic_role": "reasoningbank_style_precomputed_search_session_summary",
        "r17_pool_id": unit.pool_id,
        "r17_memory_items_sha256": unit.memory_items_sha256,
    }


def validate_rb_add_summary_pair(add_payload: Mapping[str, Any], summary_payload: Mapping[str, Any]) -> None:
    if add_payload.get("add_record_id") != summary_payload.get("summary_id"):
        raise ValueError("RB add/summary point id mismatch")
    if add_payload.get("add_record_id") != summary_payload.get("add_record_id"):
        raise ValueError("RB summary does not bind originating add record")
    if add_payload.get("task_id") != summary_payload.get("task_id"):
        raise ValueError("RB add/summary task mismatch")
    if float(add_payload.get("score")) != float(summary_payload.get("score")):
        raise ValueError("RB add/summary score mismatch")
    if add_payload.get("r17_rbagg_memory_items_sha256") != summary_payload.get("r17_memory_items_sha256"):
        raise ValueError("RB add/summary aggregate SHA mismatch")
    if add_payload.get("r17_rbagg_precomputed_summary_required") is not True:
        raise ValueError("RB add record does not require precomputed summary")
    if add_payload.get("r17_rbagg_direct_trajectory_summarization_forbidden") is not True:
        raise ValueError("RB add record does not forbid direct trajectory summarization")
