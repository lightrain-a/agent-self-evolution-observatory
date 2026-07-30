from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "iclr-experiment-audit.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "iclr-experiment-audit.js"


def bi(zh: str, en: str) -> dict[str, str]:
    return {"zh": zh.strip(), "en": en.strip()}


def P(
    id: str,
    title: str,
    venue: str,
    substrate: str,
    actor_zh: str,
    actor_en: str,
    api_zh: str,
    api_en: str,
    update_zh: str,
    update_en: str,
    data_zh: str,
    data_en: str,
    hardware_zh: str,
    hardware_en: str,
    implication_zh: str,
    implication_en: str,
    source: str,
    verification: str,
) -> dict[str, Any]:
    return {
        "id":id,
        "title":title,
        "venue":venue,
        "substrate":substrate,
        "actor":bi(actor_zh, actor_en),
        "api_role":bi(api_zh, api_en),
        "parameter_updates":bi(update_zh, update_en),
        "data":bi(data_zh, data_en),
        "hardware":bi(hardware_zh, hardware_en),
        "implication":bi(implication_zh, implication_en),
        "source":source,
        "verification":verification,
    }


PAPERS: tuple[dict[str, Any], ...] = (
    P(
        "retroformer-2024", "Retroformer: Retrospective Large Language Agents with Policy Gradient Optimization", "ICLR 2024", "hybrid-retrospective-training",
        "语言 Agent 与一个可训练 retrospective model 配对；精确基础模型组合需从官方配置读取。",
        "A language agent is paired with a trainable retrospective model; exact backbone combinations should be read from the official configuration.",
        "方法可连接商业或开源 Agent；API 不是 retrospective policy-gradient 机制的必要条件。",
        "The method can wrap proprietary or open agents; API access is not structurally required by retrospective policy-gradient learning.",
        "训练 retrospective 模型，使其从环境奖励总结根因并改写 Agent Prompt。",
        "Trains a retrospective model to summarize root causes from environment rewards and revise the agent prompt.",
        "跨多个交互环境与任务，以环境奖励训练。",
        "Uses multiple interactive environments and tasks with environment rewards.",
        "精确硬件在当前官方摘要中未报告，复现前需核对附录。",
        "Exact hardware is not stated in the official abstract and must be checked in the appendix.",
        "低资源 ICLR 工作可以冻结 Actor，只训练小型 retrospective/门控器；但必须报告圈外任务和多轮回退。",
        "A low-resource ICLR study can freeze the actor and train a small retrospective/gating model, but must report out-of-loop tasks and multi-round regression.",
        "https://proceedings.iclr.cc/paper_files/paper/2024/hash/29f421fbdcc82aeb349d784d3aaccdb3-Abstract-Conference.html", "official-abstract-method-verified",
    ),
    P(
        "opro-2024", "Large Language Models as Optimizers", "ICLR 2024", "in-context-optimizer",
        "LLM 根据历史候选解与分数生成新解；主应用是 Prompt 优化。",
        "An LLM generates new solutions from previously evaluated candidates; the main application is prompt optimization.",
        "可使用托管或本地模型；不同模型的调用成本必须单独报告。",
        "Hosted or local models can be used; call costs must be reported separately by model.",
        "不更新优化器模型参数；被更新对象是自然语言 Prompt/候选解。",
        "Does not update optimizer weights; the evolving object is the prompt or candidate solution.",
        "线性回归、旅行商、GSM8K 与 BIG-Bench Hard。",
        "Linear regression, traveling salesman, GSM8K, and BIG-Bench Hard.",
        "属于推理时搜索；硬件取决于所选模型，商业 API 不适用本地 GPU 报告。",
        "This is inference-time search; hardware depends on the model, while hosted APIs require call/cost accounting instead.",
        "可作为工作流/Prompt 进化基线，但必须匹配候选评估次数，不能把更多搜索当成学习收益。",
        "It is a strong prompt/workflow evolution baseline, but candidate evaluations must be budget-matched so extra search is not mistaken for learning.",
        "https://proceedings.iclr.cc/paper_files/paper/2024/hash/3339f19c5fcee3ad74502947a32be9e6-Abstract-Conference.html", "official-abstract-verified",
    ),
    P(
        "evo-prompt-2024", "Connecting Large Language Models with Evolutionary Algorithms Yields Powerful Prompt Optimizers", "ICLR 2024", "hybrid-evolutionary-search",
        "连接 GPT-3.5 与 Alpaca 等闭源/开源 LLM，通过进化算子优化 Prompt。",
        "Combines proprietary/open LLMs such as GPT-3.5 and Alpaca with evolutionary operators for prompt optimization.",
        "GPT-3.5 需要 API，Alpaca 可本地运行；主结果应区分两类成本。",
        "GPT-3.5 requires an API while Alpaca can run locally; costs must be separated.",
        "不使用梯度更新 LLM；进化的是 Prompt 群体。",
        "Does not update LLM weights; the prompt population evolves.",
        "31 个语言理解、生成与 BIG-Bench Hard 数据集。",
        "Thirty-one language understanding, generation, and BIG-Bench Hard datasets.",
        "本地开源模型硬件与托管 API 成本需要分别报告。",
        "Local open-model hardware and hosted API costs must be reported separately.",
        "适合作为无梯度更新基线，但 ICLR 主张必须证明持久结构或规则能圈外迁移。",
        "It is a strong gradient-free baseline, but an ICLR claim must show persistent structure/rules that transfer out of loop.",
        "https://proceedings.iclr.cc/paper_files/paper/2024/hash/9156b0f6dfa9bbd18c79cc459ef5d61c-Abstract-Conference.html", "official-abstract-verified",
    ),
    P(
        "online-continual-agent-2024", "Online Continual Learning for Interactive Instruction Following Agents", "ICLR 2024", "trained-embodied-continual-policy",
        "具身 instruction-following Agent 在 Behavior-IL 与 Environment-IL 流中持续学习。",
        "An embodied instruction-following agent learns continually under Behavior-IL and Environment-IL streams.",
        "核心方法为本地训练，不依赖商业 API。",
        "The core method is local training and does not depend on commercial APIs.",
        "CAMA 以 confidence-aware moving average 更新历史信息，无需任务边界。",
        "CAMA updates historical information with a confidence-aware moving average without task boundaries.",
        "具身日常任务的行为增量与环境增量设置。",
        "Behavior-incremental and environment-incremental embodied daily-task settings.",
        "精确硬件需从官方附录读取。",
        "Exact hardware should be copied from the official appendix.",
        "为 ICLR 提供稳定—可塑性基线；我们的具身实验应优先冻结大模型，只更新小门控并报告最坏任务回退。",
        "This provides a stability-plasticity baseline; our embodied study should freeze large models, update small gates, and report worst-task regression.",
        "https://proceedings.iclr.cc/paper_files/paper/2024/hash/557127988fc822e55f16aca5976cf0b7-Abstract-Conference.html", "official-abstract-verified",
    ),
    P(
        "aflow-2025", "AFlow: Automating Agentic Workflow Generation", "ICLR 2025", "workflow-search-hybrid",
        "把 LLM 调用节点组成的代码工作流视为搜索空间，用 MCTS 和执行反馈迭代修改。",
        "Treats code-represented workflows of LLM-invoking nodes as a search space refined by MCTS and execution feedback.",
        "可调用不同托管或本地 LLM；论文报告小模型在部分任务以 GPT-4o 约 4.55% 美元成本获得更高性能。",
        "Can invoke hosted or local LLMs; the paper reports smaller models outperforming GPT-4o on some tasks at about 4.55% of its dollar inference cost.",
        "基础模型可冻结；更新对象是工作流代码、拓扑和经验树。",
        "Foundation models may remain frozen; workflow code, topology, and the experience tree evolve.",
        "六个 benchmark 数据集。",
        "Six benchmark datasets.",
        "主要成本是大量工作流评估调用；必须报告调用数、token、美元和墙钟。",
        "The main cost is workflow evaluation calls; calls, tokens, dollars, and wall-clock time must be reported.",
        "是 ICLR 工作流进化的最强直接基线；新方法必须提供结构信用、稳定性或圈外泛化，而非仅更高开发分数。",
        "This is a primary ICLR workflow-evolution baseline; a new method needs structural credit, stability, or out-of-loop generalization rather than only better development scores.",
        "https://proceedings.iclr.cc/paper_files/paper/2025/hash/5492ecbce4439401798dcd2c90be94cd-Abstract-Conference.html", "official-abstract-verified",
    ),
    P(
        "web-rl-2025", "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning", "ICLR 2025", "open-weight-online-rl",
        "使用 Llama-3.1-8B 与 70B 训练开放 Web Agent。",
        "Trains open web agents based on Llama-3.1-8B and 70B.",
        "核心训练不依赖商业模型；GPT-4-Turbo 作为比较。",
        "Core training uses open models; GPT-4-Turbo is a comparison.",
        "从失败生成自进化课程，训练 outcome-supervised reward model 并进行自适应在线 RL。",
        "Generates a self-evolving curriculum from failures, trains an outcome-supervised reward model, and performs adaptive online RL.",
        "WebArena-Lite，覆盖五类网站。",
        "WebArena-Lite across five website categories.",
        "70B 复现资源高；低资源版本应以 8B、子集和小轮次为主。",
        "The 70B run is high-resource; a low-resource reproduction should use 8B models, subsets, and few rounds.",
        "是课程进化与策略漂移控制的核心基线；必须用未见任务和固定锚点验证真实泛化。",
        "This is a core curriculum/drift baseline; real generalization requires unseen tasks and frozen anchors.",
        "https://proceedings.iclr.cc/paper_files/paper/2025/hash/c66e1fcc9691aae706250638f36f681b-Abstract-Conference.html", "official-abstract-verified",
    ),
    P(
        "score-2025", "Training Language Models to Self-Correct via Reinforcement Learning", "ICLR 2025", "proprietary-online-rl",
        "在 Gemini 1.0 Pro 与 Gemini 1.5 Flash 上训练自纠正策略。",
        "Trains self-correction policies on Gemini 1.0 Pro and Gemini 1.5 Flash.",
        "核心实验使用不可下载的 Gemini 模型，因此完整复现依赖内部/托管训练条件。",
        "Core experiments use non-downloadable Gemini models, so full reproduction depends on internal or hosted training access.",
        "两阶段在线 RL 在模型自身分布的纠正轨迹上训练，并用正则化避免坍塌。",
        "A two-phase online RL procedure trains on the model's own correction distribution with regularization against collapse.",
        "MATH 与 HumanEval。",
        "MATH and HumanEval.",
        "属于高成本训练基线；低资源工作应使用开放 7B/8B 模型或只研究纠正准入/审计。",
        "This is a high-cost training baseline; low-resource work should use open 7B/8B models or study correction admission/auditing.",
        "关键 ICLR 证据是 on-policy 分布、正确答案保持和坍塌分析，而不是第二次回答更好。",
        "The key ICLR evidence is on-policy learning, correct-answer preservation, and collapse analysis—not merely better second answers.",
        "https://proceedings.iclr.cc/paper_files/paper/2025/hash/871ac99fdc5282d0301934d23945ebaa-Abstract-Conference.html", "official-abstract-verified",
    ),
    P(
        "self-evolved-reward-2025", "SELF-EVOLVED REWARD LEARNING FOR LLMS", "ICLR 2025", "open-weight-reward-training",
        "在 Mistral 与 Llama 3 等开放模型上训练 Reward Model。",
        "Trains reward models using open model families including Mistral and Llama 3.",
        "核心方法可本地运行；商业或更强 AI 仅是传统标签来源对照。",
        "The core method can run locally; proprietary or stronger AI systems are conventional label-source comparisons.",
        "Reward Model 自生成额外标签，经筛选后再训练 Reward Model。",
        "The reward model generates additional labels, filters them, and retrains itself.",
        "HH-RLHF、UltraFeedback 等偏好数据。",
        "Preference datasets including HH-RLHF and UltraFeedback.",
        "7B 级 Reward 可低资源复现，但多代自标注必须记录 GPU、标签谱系和噪声。",
        "A 7B reward model is feasible, but multi-generation self-labeling must report GPU use, label lineage, and noise.",
        "是评价器进化基线；新方法应解决跨版本共适应、置信传播或停止条件。",
        "This is a primary evaluator-evolution baseline; new work should address co-adaptation, confidence propagation, or stopping.",
        "https://proceedings.iclr.cc/paper_files/paper/2025/hash/26f5a4e26c13d1e0a47f46790c999361-Abstract-Conference.html", "official-abstract-verified",
    ),
    P(
        "worfbench-2025", "Benchmarking Agentic Workflow Generation", "ICLR 2025", "benchmark-plus-open-training",
        "WorfBench/WorfEval 评测序列与图工作流生成，并训练两个开放模型。",
        "WorfBench/WorfEval evaluates sequence and graph workflow generation and trains two open models.",
        "可本地运行；GPT-4 用于能力比较而非唯一评测器。",
        "Can run locally; GPT-4 is an evaluated comparison rather than the sole evaluator.",
        "训练开放工作流生成模型，评测使用 subsequence 与 subgraph matching。",
        "Trains open workflow-generation models and evaluates with subsequence and subgraph matching.",
        "多场景复杂工作流结构与 held-out 任务。",
        "Multi-scenario complex workflow structures with held-out tasks.",
        "精确训练硬件需查附录；评测本身可低资源运行。",
        "Exact training hardware requires appendix verification; evaluation itself is low-resource.",
        "为工作流一般化提供结构化主指标；新的搜索方法不能只报告最终任务成功率。",
        "It provides structured generalization metrics; new workflow search should not report only final task success.",
        "https://proceedings.iclr.cc/paper_files/paper/2025/hash/adbe936993aa7cf41e45054d8b72f183-Abstract-Conference.html", "official-abstract-verified",
    ),
    P(
        "wma-2025", "Web Agents with World Models: Learning and Leveraging Environment Dynamics in Web Navigation", "ICLR 2025", "world-model-augmented-inference",
        "Web Agent 使用 transition-focused observation abstraction 的世界模型预测动作后果。",
        "A web agent uses a world model with transition-focused observation abstraction to predict action outcomes.",
        "论文分析 GPT-4o、Claude-3.5-Sonnet 等模型；方法可作为推理时增强，精确开放/托管组合需按官方配置报告。",
        "The paper analyzes GPT-4o and Claude-3.5-Sonnet; the method is an inference-time augmentation, with exact hosted/open combinations reported from official configs.",
        "主要结果强调无需训练 Agent 策略即可改善 policy selection；世界模型具体训练/提示配置需查附录。",
        "The main result improves policy selection without policy training; exact world-model training/prompt details require the appendix.",
        "WebArena 与 Mind2Web。",
        "WebArena and Mind2Web.",
        "主要成本为额外后果预测调用，必须与树搜索等方法匹配时间和美元成本。",
        "The main cost is extra consequence-prediction calls, which must be matched against tree-search time and dollar costs.",
        "为世界模型方向提供直接基线；新工作需证明哪些模型误差值得学习且更准预测确实改变决策。",
        "This is a direct world-model baseline; new work must show which errors deserve learning and that better prediction changes decisions.",
        "https://proceedings.iclr.cc/paper_files/paper/2025/hash/a00548031e4647b13042c97c922fadf1-Abstract-Conference.html", "official-abstract-verified",
    ),
    P(
        "agent-refine-2025", "AgentRefine: Enhancing Agent Generalization through Refinement Tuning", "ICLR 2025", "hybrid-synthetic-instruction-tuning",
        "开放 Agent 模型通过多环境合成与纠错轨迹做 refinement tuning。",
        "Open agent models are refinement-tuned using synthesized multi-environment correction trajectories.",
        "强 LLM 用于合成和改写错误动作，核心部署模型为开放模型；精确 API 版本需查配置。",
        "A strong LLM synthesizes and refines error actions while the deployed model is open; exact API versions require config verification.",
        "执行 instruction/refinement tuning，使模型从环境观察中改正错误。",
        "Performs instruction/refinement tuning so the model learns to correct mistakes from environment observations.",
        "多种 Agent 环境、held-in 与 held-out 泛化任务。",
        "Multiple agent environments with held-in and held-out generalization tasks.",
        "数据合成可调用 API，训练开放模型需要 GPU；应分别报告。",
        "Data synthesis may use APIs while open-model training uses GPUs; both costs should be separated.",
        "是经验纠正内化的关键基线；新方法需区分合成数据规模与真正的归因/适用边界机制。",
        "This is a key refinement-internalization baseline; new work must separate data scale from attribution/applicability mechanisms.",
        "https://proceedings.iclr.cc/paper_files/paper/2025/hash/a3cc50126338b175e56bb3cad134db0b-Abstract-Conference.html", "official-abstract-verified",
    ),
    P(
        "flow-2025", "Flow: Modularized Agentic Workflow Automation", "ICLR 2025", "dynamic-workflow-inference",
        "用 AOV 图表示多 Agent 工作流，根据历史表现动态调整子任务分配。",
        "Represents multi-agent workflows as activity-on-vertex graphs and adapts subtask allocation from historical performance.",
        "具体 Agent 模型可为托管或本地 LLM；需按实现报告。",
        "The underlying agents may be hosted or local LLMs and must be reported from the implementation.",
        "主要更新工作流结构与分工，不要求全量训练基础模型。",
        "Primarily updates workflow structure and allocation rather than full foundation-model weights.",
        "多类实际复杂任务。",
        "Multiple practical complex tasks.",
        "成本主要来自多 Agent 并行调用；必须报告总调用和关键路径墙钟。",
        "Cost is dominated by multi-agent calls; total calls and critical-path wall-clock must be reported.",
        "为模块化与动态工作流提供基线；新工作需加入结构信用、非回退和组合兼容性。",
        "This is a modular dynamic-workflow baseline; new work needs structural credit, non-regression, or composition compatibility.",
        "https://proceedings.iclr.cc/paper_files/paper/2025/hash/ba84da6921f3040b74ee163aa7451f53-Abstract-Conference.html", "official-abstract-verified",
    ),
)


def build_payload() -> dict[str, Any]:
    counts: dict[str, int] = {}
    for paper in PAPERS:
        counts[paper["substrate"]] = counts.get(paper["substrate"], 0) + 1
    return {
        "schema_version":"1.0",
        "generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target_venue":"ICLR",
        "policy":{
            "source_rule":bi("仅使用 ICLR Proceedings、官方项目页或作者代码；未知字段不推断。", "Use only ICLR Proceedings, official project pages, or author code; unknown fields are not inferred."),
            "interpretation":bi("商业 API、开放权重、参数训练、搜索调用和外部工具分别报告。", "Report proprietary APIs, open weights, parameter training, search calls, and external tools separately."),
        },
        "summary":{
            "papers":len(PAPERS),
            "substrate_counts":counts,
            "primary_recommendation":bi("主结果使用开放 7B/8B 模型；商业 API 只作为可选上界/数据生成器；严格匹配交互、token、调用、训练和墙钟。", "Use open 7B/8B models for primary results; proprietary APIs only as optional ceilings/data generators; match interaction, token, call, training, and wall-clock budgets."),
        },
        "papers":list(PAPERS),
    }


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for paper in payload.get("papers", []):
        if paper["id"] in seen:
            errors.append(f"duplicate paper id: {paper['id']}")
        seen.add(paper["id"])
        for key in ("actor", "api_role", "parameter_updates", "data", "hardware", "implication"):
            value = paper.get(key)
            if not isinstance(value, dict) or not value.get("zh") or not value.get("en"):
                errors.append(f"missing bilingual {key}: {paper['id']}")
        if not paper.get("source", "").startswith("https://"):
            errors.append(f"invalid source: {paper['id']}")
    if len(payload.get("papers", [])) < 10:
        errors.append("fewer than ten ICLR papers")
    return errors


def write_audit(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_payload()
    errors = validate(payload)
    if errors:
        raise ValueError("Invalid ICLR experiment audit:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.ICLR_EXPERIMENT_AUDIT = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload
