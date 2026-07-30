from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

BilingualText = dict[str, str]
Decision = Literal["advance", "investigate", "hold", "stop"]
Stage = Literal["raw", "deduplicated", "collision-check", "review", "pilot-ready", "selected", "archived"]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def text(en: str, zh: str) -> BilingualText:
    return {"en": en.strip(), "zh": zh.strip()}


@dataclass(slots=True)
class PaperEvidence:
    title: str
    year: int | None = None
    venue: str = ""
    role: str = "nearest-work"
    overlap: BilingualText = field(default_factory=dict)
    difference: BilingualText = field(default_factory=dict)
    url: str = ""


@dataclass(slots=True)
class ScoreDimension:
    key: str
    label: BilingualText
    level: Literal["strong", "medium", "weak", "unknown"]
    reason: BilingualText


@dataclass(slots=True)
class ReviewRecord:
    reviewer: str
    verdict: Literal["pass", "revise", "block", "unknown"]
    question: BilingualText
    finding: BilingualText
    required_action: BilingualText


@dataclass(slots=True)
class PilotGate:
    setup: BilingualText
    decisive_metric: BilingualText
    strongest_baseline: BilingualText
    go: BilingualText
    stop: BilingualText
    estimated_cost: BilingualText = field(default_factory=dict)


@dataclass(slots=True)
class IdeaCandidate:
    id: str
    name: str
    direction_id: str
    direction_code: str
    direction_title: BilingualText
    track: BilingualText
    stage: Stage
    decision: Decision
    confidence: Literal["H", "M", "L"]
    purpose: BilingualText
    core_idea: BilingualText
    rationale: BilingualText
    method_logic: BilingualText
    importance: BilingualText
    comparative_advantage: BilingualText
    thesis: BilingualText
    observation: BilingualText = field(default_factory=dict)
    existing_failure: BilingualText = field(default_factory=dict)
    visual_necessity: BilingualText = field(default_factory=dict)
    unresolved_risk: BilingualText = field(default_factory=dict)
    evidence: list[PaperEvidence] = field(default_factory=list)
    scorecard: list[ScoreDimension] = field(default_factory=list)
    reviews: list[ReviewRecord] = field(default_factory=list)
    pilot: PilotGate | None = None
    legacy_rank: int | None = None
    legacy_score: float | None = None
    generation_operator: str = "legacy-curated"
    updated_at: str = field(default_factory=now_iso)

    def validate(self) -> list[str]:
        errors: list[str] = []
        required = {
            "purpose": self.purpose,
            "core_idea": self.core_idea,
            "rationale": self.rationale,
            "method_logic": self.method_logic,
            "importance": self.importance,
            "comparative_advantage": self.comparative_advantage,
            "thesis": self.thesis,
        }
        for key, value in required.items():
            if not value.get("en") or not value.get("zh"):
                errors.append(f"{self.id}: missing bilingual field {key}")
        if self.decision == "advance" and self.pilot is None:
            errors.append(f"{self.id}: advance decision requires a pilot gate")
        if self.stage in {"pilot-ready", "selected"} and self.pilot is None:
            errors.append(f"{self.id}: {self.stage} requires a pilot gate")
        return errors

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema_version"] = "2.0"
        return payload


@dataclass(slots=True)
class FunnelStage:
    key: str
    label: BilingualText
    count: int
    description: BilingualText


@dataclass(slots=True)
class PipelineSnapshot:
    project: str
    generated_at: str
    architecture_version: str
    funnel: list[FunnelStage]
    ideas: list[IdeaCandidate]
    generation_operators: list[dict[str, Any]]
    reviewer_roles: list[dict[str, Any]]
    warnings: list[BilingualText] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        seen: set[str] = set()
        for idea in self.ideas:
            if idea.id in seen:
                errors.append(f"duplicate idea id: {idea.id}")
            seen.add(idea.id)
            errors.extend(idea.validate())
        if not any(idea.stage in {"pilot-ready", "selected"} for idea in self.ideas):
            errors.append("snapshot has no pilot-ready or selected idea")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "2.0",
            "project": self.project,
            "generated_at": self.generated_at,
            "architecture_version": self.architecture_version,
            "funnel": [asdict(stage) for stage in self.funnel],
            "ideas": [idea.to_dict() for idea in self.ideas],
            "generation_operators": self.generation_operators,
            "reviewer_roles": self.reviewer_roles,
            "warnings": self.warnings,
        }
