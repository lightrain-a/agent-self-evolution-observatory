from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any

from .live_pipeline import load_live_corpus
from .models import FunnelStage, IdeaCandidate, PaperEvidence, PilotGate, PipelineSnapshot, now_iso, text
from .operators import operator_specs
from .review import build_reviews, build_scorecard, classify, reviewer_specs

ROOT = Path(__file__).resolve().parents[1]
EXPORTER = Path(__file__).resolve().with_name("export_legacy_portfolio.mjs")


def load_legacy_portfolio() -> dict[str, Any]:
    completed = subprocess.run(
        ["node", str(EXPORTER)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def _bi(value: Any, fallback_en: str = "", fallback_zh: str = "") -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "en": str(value.get("en", fallback_en)).strip(),
            "zh": str(value.get("zh", fallback_zh)).strip(),
        }
    if value is None:
        return text(fallback_en, fallback_zh)
    return text(str(value), str(value))


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for", "from", "how", "in", "is", "it",
    "of", "on", "or", "that", "the", "their", "this", "to", "using", "via", "what", "when", "where",
    "which", "with", "without", "agent", "agents", "model", "models", "method", "methods", "paper", "work",
}


def _tokens(value: str) -> set[str]:
    return {token for token in _TOKEN_RE.findall(value.lower().replace("-", " ")) if len(token) > 2 and token not in _STOPWORDS}


def _paper_evidence(direction_literature: list[dict[str, Any]], advantage: dict[str, str]) -> list[PaperEvidence]:
    results: list[PaperEvidence] = []
    for record in direction_literature[:4]:
        method = _bi(record.get("method"))
        fit = _bi(record.get("fit"))
        results.append(
            PaperEvidence(
                title=str(record.get("title", "")),
                year=record.get("year"),
                venue=str(record.get("venue", "")),
                role="direction-anchor",
                overlap=text(
                    f"This work anchors the same research neighborhood: {method.get('en', '')}",
                    f"该工作锚定了相同研究邻域：{method.get('zh', '')}",
                ),
                difference=text(
                    f"The candidate must still prove its narrower advantage: {advantage.get('en', '')}",
                    f"候选方案仍需证明更窄的差异：{advantage.get('zh', '')}",
                ),
            )
        )
    return results


def _live_paper_evidence(
    live_corpus: dict[str, Any] | None,
    *,
    purpose: dict[str, str],
    core: dict[str, str],
    rationale: dict[str, str],
    direction_title: dict[str, str],
    limit: int = 4,
) -> list[PaperEvidence]:
    if not live_corpus:
        return []
    query_text = " ".join((purpose.get("en", ""), core.get("en", ""), rationale.get("en", ""), direction_title.get("en", "")))
    query_tokens = _tokens(query_text)
    if not query_tokens:
        return []
    scored: list[tuple[float, dict[str, Any], list[str]]] = []
    for raw in live_corpus.get("papers") or []:
        title = str(raw.get("title") or "").strip()
        if not title:
            continue
        abstract = str(raw.get("abstract") or "")
        venue = str(raw.get("venue") or "")
        document_tokens = _tokens(f"{title} {abstract} {venue}")
        overlap = sorted(query_tokens & document_tokens)
        if len(overlap) < 2:
            continue
        title_overlap = query_tokens & _tokens(title)
        cosine_like = len(overlap) / math.sqrt(max(len(query_tokens), 1) * max(len(document_tokens), 1))
        score = cosine_like + 0.12 * len(title_overlap)
        metadata = raw.get("metadata") or {}
        score += min(float(metadata.get("citationCount") or 0), 5000.0) / 500000.0
        scored.append((score, raw, overlap))
    scored.sort(key=lambda item: (-item[0], -int((item[1].get("metadata") or {}).get("citationCount") or 0), item[1].get("title", "")))
    results: list[PaperEvidence] = []
    for score, raw, overlap in scored[:limit]:
        metadata = raw.get("metadata") or {}
        citation_count = metadata.get("citationCount")
        overlap_terms = ", ".join(overlap[:8])
        citation_note = f"; {citation_count} citations in the retrieved metadata" if citation_count is not None else ""
        results.append(
            PaperEvidence(
                title=str(raw.get("title") or ""),
                year=raw.get("year"),
                venue=str(raw.get("venue") or ""),
                role="semantic-scholar-nearest",
                overlap=text(
                    f"Semantic Scholar discovery match (local lexical score {score:.3f}); shared terms: {overlap_terms}{citation_note}.",
                    f"Semantic Scholar 发现候选（本地词项匹配分数 {score:.3f}）；共享关键词：{overlap_terms}{'；检索元数据引用量 ' + str(citation_count) if citation_count is not None else ''}。",
                ),
                difference=text(
                    "This is a nearest-work candidate, not a novelty verdict. Compare the exact problem, mechanism, supervision, and experiment before advancing the idea.",
                    "这只是最近工作候选，不代表新颖性结论；立项前必须逐项比较问题、机制、监督信号与实验设置。",
                ),
                url=str(raw.get("url") or ""),
            )
        )
    return results


def _deduplicate_evidence(records: list[PaperEvidence]) -> list[PaperEvidence]:
    seen: set[str] = set()
    results: list[PaperEvidence] = []
    for record in records:
        key = " ".join(record.title.lower().split())
        if not key or key in seen:
            continue
        seen.add(key)
        results.append(record)
    return results


def _pilot_cost(confidence: str) -> dict[str, str]:
    if confidence == "H":
        return text("Bounded pilot: one environment, two strong baselines, three seeds, and no full-scale training.", "有界 Pilot：一个环境、两个强基线、三个随机种子，不先进行全规模训练。")
    if confidence == "M":
        return text("Asset audit required before pilot; target one environment and one decisive mechanism test.", "Pilot 前需完成资产核查；先限定为一个环境和一个决定性机制测试。")
    return text("Do not allocate training compute until the phenomenon and data source are demonstrated.", "在证明现象和数据来源前，不投入训练算力。")


def _build_candidate(
    raw: dict[str, Any],
    payload: dict[str, Any],
    direction_map: dict[str, dict[str, Any]],
    live_corpus: dict[str, Any] | None,
) -> IdeaCandidate:
    name = str(raw["name"])
    direction_id = str(raw["directionId"])
    direction = direction_map[direction_id]
    explanation = payload.get("explanations", {}).get(name, {})
    comparison = payload.get("comparisons", {}).get(name, {})
    purpose = _bi(explanation.get("purpose"), raw.get("thesis", {}).get("en", ""), raw.get("thesis", {}).get("zh", ""))
    core = _bi(explanation.get("core"), raw.get("thesis", {}).get("en", ""), raw.get("thesis", {}).get("zh", ""))
    rationale = _bi(explanation.get("rationale"), "The mechanism is plausible but needs a direct phenomenon test.", "该机制具有合理性，但仍需直接现象验证。")
    logic = _bi(explanation.get("logic"), raw.get("experiment", {}).get("en", ""), raw.get("experiment", {}).get("zh", ""))
    importance = _bi(comparison.get("importance"), purpose.get("en", ""), purpose.get("zh", ""))
    advantage = _bi(comparison.get("advantage"), raw.get("baseline", {}).get("en", ""), raw.get("baseline", {}).get("zh", ""))
    track = _bi(raw.get("track"))
    confidence = str(raw.get("confidence", "L"))
    rank = int(raw.get("rank", 999))
    stage, decision = classify(
        name=name,
        confidence=confidence,
        legacy_rank=rank,
        track=track,
        direction_id=direction_id,
    )
    direction_literature = payload.get("literature", {}).get(direction_id, [])
    direction_title = _bi(direction.get("title"))
    evidence = _deduplicate_evidence(
        _paper_evidence(direction_literature, advantage)
        + _live_paper_evidence(
            live_corpus,
            purpose=purpose,
            core=core,
            rationale=rationale,
            direction_title=direction_title,
        )
    )
    selected = stage == "selected"
    pilot = PilotGate(
        setup=_bi(raw.get("experiment")),
        decisive_metric=_bi(raw.get("go")),
        strongest_baseline=_bi(raw.get("baseline")),
        go=_bi(raw.get("go")),
        stop=_bi(raw.get("stop")),
        estimated_cost=_pilot_cost(confidence),
    )
    direction_boundary = _bi(direction.get("boundary"))
    visual_track = any(token in f"{track.get('en', '')} {direction_id}".lower() for token in ("visual", "cvpr", "multimodal", "embodied"))
    visual_necessity = direction_boundary if visual_track else text(
        "Visual necessity is not yet established; this candidate may fit systems, security, or general agent venues better than CVPR.",
        "视觉不可替代性尚未建立；该候选可能更适合系统、安全或通用 Agent 会议，而非 CVPR。",
    )
    return IdeaCandidate(
        id=name.lower().replace("_", "-").replace(" ", "-"),
        name=name,
        direction_id=direction_id,
        direction_code=str(direction.get("code", "")),
        direction_title=direction_title,
        track=track,
        stage=stage,  # type: ignore[arg-type]
        decision=decision,  # type: ignore[arg-type]
        confidence=confidence,  # type: ignore[arg-type]
        purpose=purpose,
        core_idea=core,
        rationale=rationale,
        method_logic=logic,
        importance=importance,
        comparative_advantage=advantage,
        thesis=_bi(raw.get("thesis")),
        observation=rationale,
        existing_failure=purpose,
        visual_necessity=visual_necessity,
        unresolved_risk=_bi(raw.get("stop")),
        evidence=evidence,
        scorecard=build_scorecard(
            confidence=confidence,
            legacy_rank=rank,
            track=track,
            direction_id=direction_id,
            evidence_count=len(evidence),
        ),
        reviews=build_reviews(
            confidence=confidence,
            legacy_rank=rank,
            track=track,
            direction_id=direction_id,
            evidence_count=len(evidence),
            selected=selected,
        ),
        pilot=pilot,
        legacy_rank=rank,
        legacy_score=float(raw.get("score", 0.0)),
        generation_operator="legacy-curated",
    )


def build_snapshot(
    payload: dict[str, Any] | None = None,
    live_corpus: dict[str, Any] | None = None,
) -> PipelineSnapshot:
    payload = payload or load_legacy_portfolio()
    live_corpus = load_live_corpus() if live_corpus is None else live_corpus
    directions = payload.get("directions", [])
    direction_map = {str(direction["id"]): direction for direction in directions}
    ideas = [_build_candidate(raw, payload, direction_map, live_corpus) for raw in payload.get("ideas", [])]
    ideas.sort(key=lambda item: item.legacy_rank or 999)

    merged_count = 18
    rejected_count = 17
    retained_count = len(ideas)
    raw_count = retained_count + merged_count + rejected_count
    shortlist_count = sum(idea.decision in {"advance", "investigate"} and (idea.legacy_rank or 999) <= 12 for idea in ideas)
    pilot_count = sum(idea.stage in {"pilot-ready", "selected"} for idea in ideas)

    funnel = [
        FunnelStage("formulations", text("Candidate formulations", "候选表述"), raw_count, text("Generated or manually proposed formulations before collision, identifiability, and experiment checks.", "在文献碰撞、可识别性和实验检查前生成或人工提出的表述。")),
        FunnelStage("retained", text("Structurally complete ideas", "结构完整 Idea"), retained_count, text("Ideas with a problem, mechanism, rationale, method logic, importance, advantage, and Go/Stop experiment.", "具有问题、机制、依据、方法逻辑、重要性、优势和 Go／Stop 实验的 Idea。")),
        FunnelStage("advisor-shortlist", text("Advisor shortlist", "导师短名单"), shortlist_count, text("High-priority candidates shown first for expert judgment; not automatic acceptance.", "优先展示给师兄和老师判断的候选，不代表自动通过。")),
        FunnelStage("pilot", text("Selected / pilot stage", "已选／Pilot 阶段"), pilot_count, text("Candidates with a bounded falsification experiment and an explicit resource decision.", "具有有界证伪实验和明确资源决策的候选。")),
    ]

    snapshot = PipelineSnapshot(
        project="Agent Self-Evolution Observatory",
        generated_at=now_iso(),
        architecture_version="2.1-s2-connected",
        funnel=funnel,
        ideas=ideas,
        generation_operators=operator_specs(),
        reviewer_roles=reviewer_specs(),
        warnings=[
            text("Legacy decimal scores are preserved only for traceability; the advisor view uses evidence gates and decision stages.", "旧小数分数仅用于追溯；导师视图改用证据门槛和决策阶段。"),
            text("Direction-level literature anchors are not sufficient to claim novelty. Exact idea-level collision checks remain mandatory.", "方向级文献锚点不足以声称新颖性；仍必须执行 Idea 级精确碰撞检查。"),
            text(
                "Semantic Scholar nearest-work matches are retrieval aids, not automatic novelty judgments; every claimed difference still requires paper-level verification.",
                "Semantic Scholar 最近工作匹配只是检索辅助，不是自动新颖性判断；所有差异主张仍需逐篇核验。",
            ),
        ],
    )
    errors = snapshot.validate()
    if errors:
        raise ValueError("Invalid pipeline snapshot:\n- " + "\n- ".join(errors))
    return snapshot


def write_snapshot(snapshot: PipelineSnapshot, json_path: Path, js_path: Path | None = None) -> None:
    payload = snapshot.to_dict()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if js_path is not None:
        js_path.parent.mkdir(parents=True, exist_ok=True)
        js_path.write_text("window.IDEA_PIPELINE = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
