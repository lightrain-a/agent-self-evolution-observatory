from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import BilingualText, text


@dataclass(frozen=True, slots=True)
class IdeaOperator:
    key: str
    name: BilingualText
    purpose: BilingualText
    required_evidence: tuple[str, ...]
    prompt: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "purpose": self.purpose,
            "required_evidence": list(self.required_evidence),
        }


OPERATORS: tuple[IdeaOperator, ...] = (
    IdeaOperator(
        "limitation-inversion",
        text("Limitation inversion", "限制反转"),
        text("Turn a repeatedly observed limitation into the primary scientific target.", "把反复出现的限制反转为论文的核心研究目标。"),
        ("direct limitations", "affected tasks", "strongest existing workaround"),
        "Given the evidence, invert one recurring limitation into a falsifiable paper problem. Do not merely add a module.",
    ),
    IdeaOperator(
        "assumption-removal",
        text("Assumption removal", "假设移除"),
        text("Remove one unrealistic data, supervision, observability, or deployment assumption.", "移除一个不现实的数据、监督、可观测性或部署假设。"),
        ("assumption", "why it fails in deployment", "replacement signal"),
        "Identify one indispensable but unrealistic assumption and propose the smallest mechanism that removes it.",
    ),
    IdeaOperator(
        "objective-evaluation-mismatch",
        text("Objective–evaluation mismatch", "目标—评测错位"),
        text("Find cases where the optimized surrogate does not establish the claimed behavior.", "寻找优化代理目标无法证明真实行为主张的场景。"),
        ("optimized objective", "claimed outcome", "counterexample"),
        "State the surrogate-to-behavior gap, then derive a mechanism and decisive metric that directly target the claimed behavior.",
    ),
    IdeaOperator(
        "pme-recombination",
        text("Purpose–mechanism–evaluation recombination", "问题—机制—评测重组"),
        text("Transfer a mechanism across structurally similar problems while preserving a direct validation path.", "在结构相似问题间迁移机制，并保留直接验证路径。"),
        ("target purpose", "source mechanism", "compatible evaluation"),
        "Recombine purpose, mechanism, and evaluation only when the shared structural variable is explicit.",
    ),
    IdeaOperator(
        "contradiction-resolution",
        text("Contradiction resolution", "矛盾消解"),
        text("Explain conflicting findings through a hidden boundary condition or causal variable.", "通过隐藏边界条件或因果变量解释冲突结论。"),
        ("paper A claim", "paper B claim", "setting difference"),
        "Propose the smallest latent variable that reconciles conflicting results and an experiment that can disprove it.",
    ),
    IdeaOperator(
        "missing-cell",
        text("Missing-cell completion", "空白单元补全"),
        text("Fill an important, feasible cell in the task × mechanism × evidence matrix.", "补全任务×机制×证据矩阵中重要且可执行的空白。"),
        ("landscape matrix", "missing cell", "reason it matters"),
        "Generate only missing cells with a clear reason for absence and a feasible measurement protocol.",
    ),
    IdeaOperator(
        "cross-domain-analogy",
        text("Cross-domain structural analogy", "跨领域结构类比"),
        text("Transfer a verified mechanism from another field based on shared structure rather than terminology.", "基于共同结构而非名词相似，从其他领域迁移已验证机制。"),
        ("source field", "shared structure", "target-specific adaptation"),
        "Name the shared state, intervention, and failure structure before proposing the transferred method.",
    ),
    IdeaOperator(
        "metric-replacement",
        text("Metric replacement", "指标替换"),
        text("Replace a convenient aggregate metric with one that directly measures the scientific claim.", "用直接测量科学主张的指标替代方便但失真的聚合指标。"),
        ("current metric", "hidden failure", "new observable"),
        "Show a concrete failure hidden by the current metric and define a measurement that changes the main conclusion.",
    ),
    IdeaOperator(
        "mechanism-inspiration-retrieval",
        text("Mechanism inspiration retrieval", "机制灵感独立检索"),
        text("Retrieve solution mechanisms separately from papers that merely describe the target problem.", "把解决机制的检索与目标问题文献分开，避免只在同题论文中做局部增量。"),
        ("target causal variable", "source mechanism corpus", "transport condition"),
        "Retrieve at least three mechanisms from structurally related but not title-neighbor papers; state why each mechanism can or cannot transport.",
    ),
    IdeaOperator(
        "concept-path-bridging",
        text("Concept-path bridging", "概念图桥接路径"),
        text("Generate a method from a non-trivial path connecting distant scientific concepts through explicit intermediate variables.", "沿科学概念图中的非显然路径，用显式中间变量连接远距离概念并生成方法。"),
        ("source concept", "bridge concepts", "target variable", "path evidence"),
        "Sample a short concept path, identify the bridge variable that changes the target mechanism, and reject purely metaphorical connections.",
    ),
    IdeaOperator(
        "reviewer-vector-repair",
        text("Reviewer-vector repair", "Reviewer 维度反推修复"),
        text("Turn low-scoring reviewer dimensions into changed assumptions, mechanisms, and decisive experiments rather than wording edits.", "把 Reviewer 的低分维度转化为假设、机制和决定性实验的实质变化，而不是改写措辞。"),
        ("review dimension", "blocking evidence", "changed assumption", "new mechanism"),
        "Produce materially distinct children for the two strongest blockers; each child must change one assumption and one executable mechanism.",
    ),
    IdeaOperator(
        "method-tree-search",
        text("Branch-and-bound method search", "分支限界方法树搜索"),
        text("Maintain multiple solution branches and expand only Pareto-promising methods under novelty, identifiability, and feasibility constraints.", "保留多个解决方案分支，在新颖性、可识别性和可行性约束下只扩展 Pareto 有潜力的方法。"),
        ("parent problem", "diverse child mechanisms", "branch score", "pruning evidence"),
        "Generate at least three mechanism-distinct children, score them on a Pareto frontier, and preserve pruned branches with explicit reasons.",
    ),
    IdeaOperator(
        "experiment-feedback-induction",
        text("Experiment-feedback induction", "实验反馈归纳"),
        text("Use controlled experimental failures to infer the missing mechanism or boundary for the next idea round.", "利用受控实验失败归纳缺失机制或边界，作为下一轮 Idea 的输入。"),
        ("frozen experiment", "failure signature", "alternative explanation", "mechanism revision"),
        "Convert a failed or ambiguous pilot into a falsifiable mechanism update without changing the frozen budget or regenerating the evidence split.",
    ),
    IdeaOperator(
        "resource-grounded-design",
        text("Resource-grounded method design", "公开资源约束的方法设计"),
        text("Concretize ideas around available code, datasets, verifiers, and intervention surfaces before ranking novelty.", "在排序新颖性前，先围绕可用代码、数据集、验证器和干预表面把方法具体化。"),
        ("public code", "dataset", "independent verifier", "exact update surface"),
        "Reject methods without an executable public-asset path; specify the smallest code change and independent ground truth before proposing scale-up.",
    ),
)


def operator_specs() -> list[dict[str, Any]]:
    return [operator.to_dict() for operator in OPERATORS]
