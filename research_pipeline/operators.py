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
)


def operator_specs() -> list[dict[str, Any]]:
    return [operator.to_dict() for operator in OPERATORS]
