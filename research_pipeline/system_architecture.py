from __future__ import annotations

from typing import Any


TEMPORAL_FLOW: tuple[dict[str, Any], ...] = (
    {"key":"scope","index":1,"label":{"en":"Paper scope","zh":"论文目标与边界"},"output":"research-scope"},
    {"key":"evidence","index":2,"label":{"en":"Evidence and closest work","zh":"证据与最近邻工作"},"output":"closest-work-and-evidence"},
    {"key":"novelty","index":3,"label":{"en":"Paper Novelty Contract","zh":"论文 Novelty 合同"},"output":"paper-novelty-contract"},
    {"key":"method","index":4,"label":{"en":"Principle and method design","zh":"原理与方法设计"},"output":"principle-and-method-contract"},
    {"key":"experiment-blueprint","index":5,"label":{"en":"Experiment Blueprint","zh":"实验蓝图"},"output":"claim-experiment-matrix"},
    {"key":"economy-compile","index":6,"label":{"en":"Economy and experiment compile","zh":"资源经济与实验编译"},"output":"launch-contract"},
    {"key":"local-validation","index":7,"label":{"en":"Local validation","zh":"局部实验验证"},"output":"f0-p0-evidence"},
    {"key":"method-freeze","index":8,"label":{"en":"Method freeze","zh":"方法冻结"},"output":"method-and-blueprint-hash"},
    {"key":"full-experiment","index":9,"label":{"en":"Full experiment","zh":"全量实验"},"output":"full-evidence-package"},
    {"key":"paper-evidence","index":10,"label":{"en":"Paper evidence closure","zh":"论文证据闭环"},"output":"chain-of-evidence"},
    {"key":"paper-design","index":11,"label":{"en":"Paper contract and story search","zh":"论文合同与故事线搜索"},"output":"paper-contract-and-story-candidates"},
    {"key":"manuscript","index":12,"label":{"en":"Manuscript construction","zh":"论文成稿"},"output":"evidence-bound-manuscript"},
    {"key":"mock-pc","index":13,"label":{"en":"Blind + artifact-aware Mock PC","zh":"盲审 + 工件审查 Mock PC"},"output":"decision-critical-review"},
    {"key":"targeted-repair","index":14,"label":{"en":"Review-to-action targeted repair","zh":"审稿意见到定向修复"},"output":"decision-critical-repair-plan"},
    {"key":"claim-audit","index":15,"label":{"en":"Manuscript claim audit","zh":"成稿主张审计"},"output":"sentence-to-evidence-audit"},
    {"key":"pdf-qa","index":16,"label":{"en":"Rendered PDF and Manuscript CI","zh":"渲染 PDF 与 Manuscript CI"},"output":"manuscript-ci-receipt"},
    {"key":"prebuttal","index":17,"label":{"en":"Decision-critical prebuttal","zh":"决策关键预答辩"},"output":"top-reject-reasons-and-responses"},
    {"key":"submission-ready","index":18,"label":{"en":"Submission readiness gate","zh":"投稿就绪门"},"output":"submission-readiness-receipt"},
    {"key":"submitted","index":19,"label":{"en":"Submitted artifact freeze","zh":"已投稿工件冻结"},"output":"submitted-artifact-receipt"},
    {"key":"rebuttal","index":20,"label":{"en":"Rebuttal and decision closure","zh":"答辩与审稿决策闭环"},"output":"review-and-decision-evidence"},
    {"key":"learn","index":21,"label":{"en":"System learning","zh":"系统学习"},"output":"rules-tests-failure-assets-review-calibration"},
)


# Reader groups are a presentation index over the canonical temporal flow, not new gates.
# They make the public system overview readable without changing scientific authority or
# duplicating the underlying 21-stage state machine.
READING_GROUPS: tuple[dict[str, Any], ...] = (
    {
        "key":"overview","index":1,"stage_keys":[],"orientation_only":True,
        "label":{"en":"Start here: one flow, three views","zh":"从这里开始：一条主流程，三个视角"},
        "question":{"en":"How should the lifecycle, responsibility layers, and authority boundaries be read together?","zh":"21 步科研到投稿生命周期、六个职责层和权限边界应该如何一起理解？"},
        "output":"shared mental model",
    },
    {
        "key":"problem-discovery","index":2,"stage_keys":["scope","evidence"],
        "label":{"en":"Discover a real problem","zh":"发现真实科学问题"},
        "question":{"en":"What measured boundary survives closest-work and mature-reduction checks?","zh":"什么真实测量边界能够在最近邻工作和成熟 reduction 之后仍然成立？"},
        "output":"problem-gate candidate or typed stop/hold",
    },
    {
        "key":"scientific-design","index":3,"stage_keys":["novelty","method","experiment-blueprint"],
        "label":{"en":"Design the contribution before implementation","zh":"实现前先把科学贡献设计完整"},
        "question":{"en":"What is novel, what mechanism carries it, and what evidence package would make the paper convincing?","zh":"Novelty 是什么、由什么机制承载、最终需要什么证据包才能把论文讲完整？"},
        "output":"novelty + principle + method + claim/evidence blueprint",
    },
    {
        "key":"experiment-compile","index":4,"stage_keys":["economy-compile"],
        "label":{"en":"Compile the cheapest decisive experiment","zh":"编译最便宜的决定性实验"},
        "question":{"en":"Is there an identifiable, economical, protocol-valid run worth launching?","zh":"是否存在一个可辨识、值得花资源且协议有效的实验值得启动？"},
        "output":"launch contract or typed pre-GPU stop",
    },
    {
        "key":"validation-scale","index":5,"stage_keys":["local-validation","method-freeze","full-experiment"],
        "label":{"en":"Execute, diagnose, freeze, then scale","zh":"执行、诊断、冻结，再扩量"},
        "question":{"en":"What did the evidence actually test, does the method survive, and is the design frozen enough to scale?","zh":"证据究竟打到了哪一层、方法是否存活、是否已经冻结到可以扩量？"},
        "output":"typed scientific decision + frozen full evidence package",
    },
    {
        "key":"paper-evidence","index":6,"stage_keys":["paper-evidence"],
        "label":{"en":"Close paper evidence","zh":"论文证据闭环"},
        "question":{"en":"Do claims, baselines, ablations, analyses, figures, code, and reproducibility artifacts resolve to the exact frozen evidence?","zh":"主张、Baseline、消融、分析、图表、代码和复现工件是否都绑定到同一份冻结证据？"},
        "output":"content-addressed paper-ready evidence package",
    },
    {
        "key":"paper-construction","index":7,"stage_keys":["paper-design","manuscript"],
        "label":{"en":"Search the story, then construct the manuscript","zh":"先竞争故事线，再形成论文成稿"},
        "question":{"en":"Which claim-preserving story best exposes the contribution, and is the manuscript bound to that winning contract?","zh":"哪条不扩张主张的故事线最能呈现贡献，成稿是否严格绑定这一获胜合同？"},
        "output":"Story Search winner + evidence-bound manuscript",
    },
    {
        "key":"review-repair","index":8,"stage_keys":["mock-pc","targeted-repair","claim-audit","pdf-qa"],
        "label":{"en":"Review, repair, audit, and render","zh":"模拟审稿、定向修复、主张审计与 PDF 质检"},
        "question":{"en":"What would cause rejection, which objections can be repaired without new science, and does every surviving claim remain evidence-bound in the rendered artifact?","zh":"哪些问题最可能导致拒稿、哪些可以在不新增科学主张的前提下修复，以及最终 PDF 中每条主张是否仍有证据绑定？"},
        "output":"dual-mode Mock PC + targeted repair + Claim Audit + PDF QA",
    },
    {
        "key":"submission-closure","index":9,"stage_keys":["prebuttal","submission-ready","submitted","rebuttal"],
        "label":{"en":"Close submission and reviewer decisions","zh":"完成预答辩、投稿与审稿决策闭环"},
        "question":{"en":"Are decision-critical objections pre-answered, all submission gates satisfied, and external human submission authority explicit?","zh":"决策关键质疑是否已预先回答、投稿门是否全部通过，以及人工投稿权限是否明确？"},
        "output":"Prebuttal + submission readiness + submission/rebuttal receipts",
    },
    {
        "key":"system-learning","index":10,"stage_keys":["learn"],
        "label":{"en":"Turn outcomes into system memory","zh":"把结果沉淀成系统记忆"},
        "question":{"en":"Which lessons become reusable rules, dead-end memory, replay cases, and future search constraints?","zh":"哪些经验应该变成可复用规则、dead-end 记忆、回放 case 和下一轮搜索约束？"},
        "output":"meta-trace + failure assets + replay-tested rules",
    },
)


FUNCTIONAL_LAYERS: tuple[dict[str, Any], ...] = (
    {
        "key":"evidence-knowledge","index":1,
        "label":{"en":"Evidence, scope, and closest work","zh":"证据、边界与最近邻工作"},
        "mandate":{"en":"Build provenance-aware evidence, define the research boundary, and detect collisions before a contribution is claimed.","zh":"建立可追溯证据、冻结研究边界，并在声称贡献前完成最近邻与撞车审查。"},
        "primary_outputs":["research scope","literature/evidence graph","closest-work evidence","collision boundary"],
    },
    {
        "key":"paper-design","index":2,
        "label":{"en":"Novelty, principle, and method formation","zh":"Novelty、原理与方法形成"},
        "mandate":{"en":"Turn a real gap into a publishable contribution, explicit mechanism, and paper-motivated method before implementation.","zh":"在实现之前，把真实缺口转成可发表贡献、明确机制和由论文 Novelty 推导的方法。"},
        "primary_outputs":["Paper Novelty Contract","Principle Certificate","Method Contract","idea lineage/review state"],
    },
    {
        "key":"experiment-design","index":3,
        "label":{"en":"Experiment blueprint and launch admission","zh":"实验蓝图与启动准入"},
        "mandate":{"en":"Compile paper claims into decisive tests and prove the cheapest local experiment is identifiable, economical, and executable.","zh":"把论文主张编译成决定性实验，并证明最便宜的局部验证在可识别性、资源与执行条件上具备启动资格。"},
        "primary_outputs":["Claim→Experiment matrix","P0 Economy","Protocol Validity","Research Execution Plan","Pre-Experiment 8/8 card"],
    },
    {
        "key":"scientific-validation","index":4,
        "label":{"en":"Scientific validation, freeze, and scale","zh":"科学验证、冻结与扩展"},
        "mandate":{"en":"Separate phenomenon support from method evidence, adjudicate negative results by layer, freeze the method, then scale only the frozen design.","zh":"把现象支持与方法证据分开，按证据层解释负结果，冻结方法后才允许对冻结设计做全量扩展。"},
        "primary_outputs":["F0","P0-Support","P0-Method","typed decision","method freeze","P1/full experiment evidence"],
    },
    {
        "key":"runtime-authority","index":5,
        "label":{"en":"Runtime, resources, and authority","zh":"运行时、资源与权限"},
        "mandate":{"en":"Keep code execution, GPU leases, traces, budgets, AI triggers, and scientific authority explicit and recoverable.","zh":"把代码执行、GPU 租约、Trace、预算、AI 触发与科学权限分离管理，并保证可恢复。"},
        "primary_outputs":["resource lease","single-writer authority","raw trace","heartbeat/progress","automation state"],
    },
    {
        "key":"memory-publication","index":6,
        "label":{"en":"Scientific memory, system learning, and publication","zh":"科研记忆、系统学习与发布"},
        "mandate":{"en":"Preserve decisions and dead ends without rewriting history, evaluate the research system itself, close publishable claims against real artifacts, and carry evidence-closed work through reviewer-aware submission closure without weakening scientific authority.","zh":"在不改写科研历史的前提下沉淀决策与死路，评测科研系统本身，让论文主张逐条回到真实工件，并在不放宽科学权限的前提下把证据闭环工作推进到面向审稿决策的投稿闭环。"},
        "primary_outputs":["Decision Ledger","Scientific Meta-Trace","Failure Assets","replay benchmark","public snapshot","Chain-of-Evidence","Paper Contract","Mock PC","Manuscript CI","Prebuttal","submission/rebuttal receipts"],
    },
)


# The English component title is deliberately the binding key. If a component is renamed or
# added, architecture validation fails until its responsibility is explicitly re-adjudicated.
COMPONENT_BINDINGS: dict[str, tuple[str, str]] = {
    "Citation and evidence graph": ("evidence-graph", "evidence-knowledge"),
    "Declarative research capability registry": ("capability-registry", "runtime-authority"),
    "Literature retrieval + Evidence Integrity layer": ("literature-evidence-integrity", "evidence-knowledge"),
    "Hybrid semantic deduplication and collision filtering": ("collision-filter", "evidence-knowledge"),
    "Idea lineage and branch preservation": ("idea-lineage", "paper-design"),
    "Terminalized human-parent lifecycle controller": ("human-terminal-ledger", "paper-design"),
    "Role-separated review repair queue": ("review-repair-queue", "paper-design"),
    "Solution-first branch search": ("solution-branch-search", "paper-design"),
    "Constrained composition and conditional revival": ("composition-revival", "paper-design"),
    "Wide-search simplification-challenge ideation": ("wide-search-ideation", "paper-design"),
    "Adversarial fan-out + independent jury harness": ("research-harness-assurance", "paper-design"),
    "Persistent multi-candidate research portfolio": ("research-candidate-portfolio", "paper-design"),
    "Search funnel + bottleneck telemetry": ("search-funnel-telemetry", "memory-publication"),
    "Pre-P0 identifiability auditor": ("pre-p0-identifiability", "experiment-design"),
    "Paper novelty → method → experiment blueprint contract": ("paper-design-contract", "paper-design"),
    "Principle Certificate + epistemic adjudicator": ("principle-adjudicator", "paper-design"),
    "Scientific Meta-Trace + cross-branch world state": ("scientific-meta-trace", "memory-publication"),
    "Typed Scientific Research Graph": ("scientific-research-graph", "memory-publication"),
    "Failure Asset + dead-end memory": ("failure-assets", "memory-publication"),
    "Information-gain experiment portfolio scheduler": ("experiment-value-scheduler", "experiment-design"),
    "Protocol-validity auditor + research-system replay benchmark": ("protocol-and-replay", "experiment-design"),
    "Continuous external research-system learning": ("external-system-learning", "memory-publication"),
    "Paper acceptance closure and manuscript integrity": ("paper-acceptance-closure", "memory-publication"),
    "Five-gate P0 Economy layer": ("p0-economy", "experiment-design"),
    "Five-checkpoint AI consultation clinic": ("ai-consultation-clinic", "paper-design"),
    "Automatic consultation trigger queue": ("ai-consultation-automation", "runtime-authority"),
    "Current experiment-decision ledger": ("p0-decision-ledger", "memory-publication"),
    "Stage governance, repair budgets, trace contracts, and resource leases": ("p0-governance", "scientific-validation"),
    "Updater prerequisite + derived Research Execution Plan + eight-gate Pre-Experiment Compiler": ("pre-experiment-compiler", "experiment-design"),
    "Pilot registry and result feedback": ("pilot-registry", "scientific-validation"),
    "Experiment diagnosis and atomic repair tree": ("experiment-diagnosis", "scientific-validation"),
    "Unrestricted autonomous code execution tree": ("unrestricted-code-execution", "runtime-authority"),
}


AUTHORITY_BOUNDARIES: tuple[dict[str, Any], ...] = (
    {"key":"advisory","label":{"en":"Advisory only","zh":"仅建议"},"examples":["AI consultation","experiment value scheduler","review agents"]},
    {"key":"machine-gated","label":{"en":"Machine-gated continuation","zh":"机器门控继续"},"examples":["Economy","Protocol Validity","Pre-Experiment Compiler","typed runtime checks"]},
    {"key":"human-scientific","label":{"en":"Human scientific authority","zh":"人工科学权限"},"examples":["claim boundary","core-method change","budget escalation","principle interpretation","final paper claim"]},
)


def _component_title(item: dict[str, Any]) -> str:
    component = item.get("component") or item.get("name") or ""
    if isinstance(component, dict):
        return str(component.get("en") or component.get("zh") or "").strip()
    return str(component).strip()


def annotate_components(components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    for original in components:
        item = dict(original)
        title = _component_title(item)
        binding = COMPONENT_BINDINGS.get(title)
        if binding:
            item["key"], item["primary_layer"] = binding
        else:
            item["key"], item["primary_layer"] = "unassigned", "unassigned"
        annotated.append(item)
    return annotated


def build_system_architecture(components: list[dict[str, Any]], methodology_controls: dict[str, Any] | None = None) -> dict[str, Any]:
    keys = [str(item.get("key") or "") for item in components]
    layer_keys = {str(row["key"]) for row in FUNCTIONAL_LAYERS}
    unassigned = [_component_title(item) for item in components if item.get("primary_layer") not in layer_keys]
    duplicates = sorted({key for key in keys if key and keys.count(key) > 1})
    component_keys = {key for key in keys if key}
    cross_controls = [dict(row) for row in ((methodology_controls or {}).get("controls") or [])]
    orphan_controls = [str(row.get("key") or "") for row in cross_controls if str(row.get("owner_component") or "") not in component_keys]
    temporal_keys = [str(row["key"]) for row in TEMPORAL_FLOW]
    grouped_stage_keys = [str(stage) for group in READING_GROUPS if not group.get("orientation_only") for stage in group.get("stage_keys") or []]
    reading_stage_duplicates = sorted({key for key in grouped_stage_keys if grouped_stage_keys.count(key) > 1})
    reading_stage_missing = [key for key in temporal_keys if key not in grouped_stage_keys]
    reading_stage_extra = sorted({key for key in grouped_stage_keys if key not in temporal_keys})
    stage_group_map = {
        str(stage): str(group["key"])
        for group in READING_GROUPS if not group.get("orientation_only")
        for stage in group.get("stage_keys") or []
    }
    layers: list[dict[str, Any]] = []
    for spec in FUNCTIONAL_LAYERS:
        key = str(spec["key"])
        members = [item for item in components if item.get("primary_layer") == key]
        layers.append({
            **spec,
            "component_keys": [str(item.get("key")) for item in members],
            "component_count": len(members),
            "running": sum(item.get("status") == "running" for item in members),
            "intentionally_disabled": sum(item.get("status") == "intentionally-disabled" for item in members),
        })
    return {
        "schema_version":"1.1",
        "model":"one temporal lifecycle + ten reader groups + six functional responsibility layers",
        "temporal_flow":[dict(row) for row in TEMPORAL_FLOW],
        "reading_groups":[dict(row) for row in READING_GROUPS],
        "stage_group_map":stage_group_map,
        "functional_layers":layers,
        "authority_boundaries":[dict(row) for row in AUTHORITY_BOUNDARIES],
        "summary":{
            "temporal_stages":len(TEMPORAL_FLOW),
            "reader_chapters":len(READING_GROUPS),
            "reader_stage_coverage":len(stage_group_map),
            "reader_stage_missing":len(reading_stage_missing),
            "reader_stage_duplicates":len(reading_stage_duplicates),
            "reader_stage_extra":len(reading_stage_extra),
            "functional_layers":len(FUNCTIONAL_LAYERS),
            "components":len(components),
            "assigned_components":len(components)-len(unassigned),
            "unassigned_components":len(unassigned),
            "duplicate_component_keys":len(duplicates),
            "cross_cutting_controls":len(cross_controls),
            "orphan_cross_cutting_controls":len(orphan_controls),
        },
        "cross_cutting_controls":cross_controls,
        "unassigned_components":unassigned,
        "duplicate_component_keys":duplicates,
        "orphan_cross_cutting_controls":orphan_controls,
        "reading_stage_missing":reading_stage_missing,
        "reading_stage_duplicates":reading_stage_duplicates,
        "reading_stage_extra":reading_stage_extra,
        "invariants":[
            "Temporal stages answer WHEN work may advance; reading groups only organize the public explanation and never create new gates.",
            "Functional layers answer WHO owns each responsibility.",
            "A component has one primary responsibility layer even when its evidence is consumed elsewhere.",
            "No advisory component can grant scientific or GPU authority.",
            "Fan-out may increase search breadth, but only an independent jury may adjudicate its outputs and jury CLEAR is still not scientific PASS.",
            "Execution loops may establish artifact completeness but cannot self-acquit scientific quality or status.",
            "Search effort and scientific assurance are orthogonal: more firepower never relaxes evidence or authority gates.",
            "The P0 seven-stage state machine is nested inside scientific validation; it is not a second paper lifecycle.",
            "Cross-cutting methodology controls attach to an existing owner component and never create an implicit seventh functional layer.",
            "Paper optimization begins only after Paper Evidence closure; it may change framing and presentation but cannot expand the frozen scientific claim.",
            "Submission readiness is a fail-closed paper gate and never implies scientific, experiment, GPU, or submission authority.",
        ],
    }
