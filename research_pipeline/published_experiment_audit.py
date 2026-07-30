from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

DEFAULT_JSON = PROJECT_ROOT / "generated" / "published-experiment-audit.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "published-experiment-audit.js"


def bi(zh: str, en: str | None = None) -> dict[str, str]:
    return {"zh": zh.strip(), "en": (en or zh).strip()}


# Only facts traceable to official papers, CVF/arXiv pages, project pages, or
# author-maintained repositories are stated as verified. Missing hardware or
# exact variants remain explicitly unknown rather than being inferred.
PAPERS: tuple[dict[str, Any], ...] = (
    {
        "id": "clova-2024",
        "title": "CLOVA: A Closed-Loop Visual Assistant with Tool Usage and Update",
        "venue": "CVPR 2024",
        "substrate": "hybrid",
        "actor": "GPT-3.5 in the main tool-use comparison; the paper also evaluates Llama2-7B and GPT-4.",
        "critic_or_judge": "The same LLM loop provides reflection; task-specific visual tools provide executable feedback.",
        "api_role": "GPT-3.5-turbo and GPT-4 are commercial API models; text-davinci-002 is used by the LIST tool. Llama2-7B is the open-weight alternative.",
        "parameter_updates": "No full LLM fine-tuning. Correct/incorrect demonstrations are stored for in-context updates; visual-tool backbones stay frozen while soft prompts are tuned.",
        "data": "GQA, NLVRv2, plus manually collected image-editing and factual-knowledge tasks.",
        "hardware": "Unknown in the official main paper text inspected.",
        "code": "Official project page and code are public.",
        "source": "https://clova-tool.github.io/",
        "verification": "verified-official",
        "implication": bi(
            "商业 API 不是闭环更新的唯一实现；低资源复现可使用本地开源规划器与冻结视觉工具，但必须单独报告 API 与开源规划器的差异。",
            "Commercial APIs are not the only implementation of closed-loop updating. A low-resource reproduction can use an open local planner and frozen visual tools, but API and open-planner results must be separated.",
        ),
    },
    {
        "id": "virep-2024",
        "title": "Self-Training Large Language Models for Improved Visual Program Synthesis with Visual Reinforcement",
        "venue": "CVPR 2024",
        "substrate": "open-weight",
        "actor": "An open code LLM is self-trained for visual program synthesis; the exact checkpoint variant must be taken from the released configuration before reproduction.",
        "critic_or_judge": "Sparse binary execution reward and filtered behavioral cloning; fewer than 50 manually written corrections extend training.",
        "api_role": "The core method is designed to avoid dependence on strong commercial program generators such as GPT-4.",
        "parameter_updates": "The code model is updated through reinforced self-training / filtered behavioral cloning.",
        "data": "Object detection, compositional VQA, and image-text retrieval tasks.",
        "hardware": "Unknown until the official PDF/configuration is checked for the exact run.",
        "code": "Official project page is public.",
        "source": "https://zaidkhan.me/ViReP/",
        "verification": "verified-with-open-variant-pending",
        "implication": bi(
            "若论文贡献依赖模型参数自进化，可以用 7B 级开源代码/VLM 做 LoRA 或小规模自训练；但当前低资源 Idea 更适合冻结主干，只更新小模块。",
            "When the contribution truly requires parameter self-evolution, a 7B open model can be adapted with LoRA or small-scale self-training. Most current low-resource ideas should still freeze the backbone and update only small components.",
        ),
    },
    {
        "id": "se-vcl-2025",
        "title": "Self-Evolving Visual Concept Library using Vision-Language Critics",
        "venue": "CVPR 2025",
        "substrate": "open-or-hybrid-unknown-exact",
        "actor": "A visual concept library and downstream visual reasoning system; exact foundation-model checkpoints must be read from the official configuration.",
        "critic_or_judge": "Vision-language critics evaluate and refine concepts.",
        "api_role": "The official abstract establishes VLM critics but does not by itself prove whether every reported critic is API-hosted or local.",
        "parameter_updates": "The evolving object is the concept library rather than unrestricted full-backbone training.",
        "data": "Visual concept learning and downstream recognition/reasoning benchmarks reported in the paper.",
        "hardware": "Unknown from the official abstract/project metadata inspected.",
        "code": "Use the official author repository when reproducing; exact availability is recorded as pending if the repository is not linked from the paper page.",
        "source": "https://openaccess.thecvf.com/content/CVPR2025/html/Sehgal_Self-Evolving_Visual_Concept_Library_using_Vision-Language_Critics_CVPR_2025_paper.html",
        "verification": "partial-official",
        "implication": bi(
            "把可进化对象限制为概念库、记忆或工具，比全量训练 VLM 更符合低资源设置；但 Critic 必须有本地可复现版本。",
            "Restricting evolution to a concept library, memory, or tools is more compatible with low-resource work than full VLM training, but a locally reproducible critic is required.",
        ),
    },
    {
        "id": "visco-2025",
        "title": "VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning",
        "venue": "CVPR 2025",
        "substrate": "hybrid",
        "actor": "The released evaluation supports proprietary GPT-4o, Claude-3.5-Sonnet, Gemini-1.5-Pro and many local open LVLMs including Qwen2-VL, Molmo, InternVL2, LLaVA, NVLM, and Llama-3.2-Vision families.",
        "critic_or_judge": "LookBack is an inference-time prompting strategy; the released explanation-F1 evaluator uses an OpenAI API model unless replaced.",
        "api_role": "Commercial APIs are one evaluated model group and are used by the provided assisted evaluator, but open models can be run locally through vLLM/lmdeploy/sglang.",
        "parameter_updates": "Benchmarking and LookBack do not require backbone training.",
        "data": "1,645 question-answer pairs with 5,604 fine-grained step annotations.",
        "hardware": "Local serving requirements depend on the selected LVLM; no single universal hardware setting applies.",
        "code": "Official GitHub repository is public.",
        "source": "https://github.com/PlusLabNLP/VISCO",
        "verification": "verified-official-code",
        "implication": bi(
            "主实验可以完全基于本地开源 Actor/Critic；商业 API 只作为上界或辅助评测，并必须同时报告调用次数、模型版本和替代的本地评测。",
            "The main experiment can use local open actors and critics. Commercial APIs should be optional ceilings or assisted evaluators, with call counts, fixed versions, and a local alternative reported.",
        ),
    },
    {
        "id": "critic-v-2025",
        "title": "Critic-V: VLM Critics Help Catch VLM Errors in Multimodal Reasoning",
        "venue": "CVPR 2025",
        "substrate": "trained-open-critic-exact-backbone-pending",
        "actor": "A reasoner VLM is paired with an independent critic; exact released reasoner/critic checkpoints should be taken from the official code/configuration.",
        "critic_or_judge": "The critic is trained with DPO on preference critiques ranked by a rule-based reward.",
        "api_role": "GPT-4V is an evaluated comparison; the method contribution is an independently trained critic rather than an API-only prompt loop.",
        "parameter_updates": "Critic parameters are trained with DPO; this is not inference-only.",
        "data": "Multimodal reasoning and critique data described in the paper.",
        "hardware": "Unknown until the official appendix/configuration is checked.",
        "code": "Official paper/project materials should be used; exact repository availability is marked pending here.",
        "source": "https://arxiv.org/abs/2411.18203",
        "verification": "verified-method-exact-checkpoint-pending",
        "implication": bi(
            "独立 Critic 能减少共享盲点，但训练 Critic 会增加成本。低资源方案应先比较冻结的异构开源 Critic，再决定是否需要小型 DPO/LoRA。",
            "An independent critic can reduce shared blind spots, but critic training adds cost. A low-resource study should first compare a frozen heterogeneous open critic before adding small DPO/LoRA training.",
        ),
    },
    {
        "id": "grounding-correction-2025",
        "title": "Can Large Vision-Language Models Correct Semantic Grounding Errors By Themselves?",
        "venue": "CVPR 2025",
        "substrate": "api-and-model-agnostic-inference",
        "actor": "The official study evaluates GPT-4V/GPT-4o and additional LVLMs; the correction procedure is prompt-based and model-agnostic.",
        "critic_or_judge": "The model performs iterative binary verification and correction.",
        "api_role": "GPT models require commercial APIs, but the method itself does not structurally require API access.",
        "parameter_updates": "No fine-tuning, architecture change, or external training data.",
        "data": "Semantic grounding evaluation sets reported in the paper.",
        "hardware": "Not applicable to hosted GPT runs; local-model hardware depends on the selected open checkpoint.",
        "code": "Official CVF/arXiv materials are public.",
        "source": "https://arxiv.org/abs/2404.06510",
        "verification": "verified-official",
        "implication": bi(
            "推理时自纠正非常省训练资源，但必须控制迭代调用预算，并证明收益来自视觉复核而非更多 token 或更多采样。",
            "Inference-time self-correction is training-efficient, but iteration budgets must be controlled and gains must be separated from simply using more tokens or samples.",
        ),
    },
    {
        "id": "phoenix-2025",
        "title": "Phoenix: A Motion-based Self-Reflection Framework for Fine-grained Robotic Action Correction",
        "venue": "CVPR 2025",
        "substrate": "trained-policy-plus-mllm",
        "actor": "A motion-conditioned diffusion policy is paired with an MLLM-driven motion-adjustment component; exact MLLM checkpoint should be verified from the official configuration.",
        "critic_or_judge": "Motion-based self-reflection supplies corrective signals.",
        "api_role": "Unknown for the exact MLLM until the official config is checked; the policy itself is trained and locally executable.",
        "parameter_updates": "The diffusion policy/lifelong component is trained; this is not a training-free method.",
        "data": "RoboMimic simulation and real-world robotic experiments.",
        "hardware": "Exact training hardware remains pending official appendix/configuration verification.",
        "code": "Official author GitHub repository is public.",
        "source": "https://github.com/GeWu-Lab/Motion-based-Self-Reflection-Framework",
        "verification": "partial-official",
        "implication": bi(
            "完整复现成本较高。我们的具身方向应先在公开轨迹与仿真重放上冻结 OpenVLA，只训练审计器或记忆门控。",
            "Full reproduction is costly. Our embodied work should first freeze OpenVLA and train only an auditor or memory gate on public trajectories and simulator replay.",
        ),
    },
    {
        "id": "vadar-2025",
        "title": "Visual Agentic AI for Spatial Reasoning with a Dynamic API",
        "venue": "CVPR 2025",
        "substrate": "llm-program-synthesis-exact-model-pending",
        "actor": "Collaborating LLM agents generate and use a dynamic Python visual API; exact LLM versions should be read from the official paper/configuration.",
        "critic_or_judge": "Execution results and specialist agents provide feedback for API creation and use.",
        "api_role": "The official abstract establishes LLM-based program synthesis but does not alone identify whether every main run is hosted API or local open weights.",
        "parameter_updates": "The evolving artifact is the dynamic API/program library; full foundation-model training is not the central mechanism.",
        "data": "Omni3D-Bench, CLEVR, GQA, and VSI-Bench.",
        "hardware": "Unknown until official appendix/configuration verification.",
        "code": "Official project page is public.",
        "source": "https://glab-caltech.github.io/vadar/",
        "verification": "partial-official",
        "implication": bi(
            "工具/API 进化可以冻结基础模型完成，但必须把程序生成器的 API 依赖作为变量，并提供本地开源规划器对照。",
            "Tool/API evolution can freeze the foundation model, but the program generator's API dependency must be treated as an experimental variable with a local open-planner control.",
        ),
    },
    {
        "id": "visplay-2026",
        "title": "VisPlay: Self-Evolving Vision-Language Models",
        "venue": "CVPR 2026",
        "substrate": "open-weight-high-resource-training",
        "actor": "Qwen2.5-VL and MiMo-VL model families are used as trainable questioner/reasoner substrates.",
        "critic_or_judge": "Self-play difficulty/diversity rewards and verifiable task signals guide GRPO.",
        "api_role": "Commercial model APIs are not required for the core training loop.",
        "parameter_updates": "Questioner and reasoner are jointly optimized with GRPO on large unlabeled-image collections.",
        "data": "Large-scale unlabeled images plus multimodal reasoning evaluations.",
        "hardware": "High-resource distributed training; exact configuration should be copied from the official appendix before reproduction.",
        "code": "Official GitHub repository is public.",
        "source": "https://github.com/bruno686/VisPlay",
        "verification": "verified-official",
        "implication": bi(
            "它证明全参数/强化学习式视觉自进化可以用开源权重完成，但不适合作为当前低资源复现目标；应作为高资源上界。",
            "It demonstrates open-weight RL-style visual self-evolution, but is unsuitable as the current low-resource reproduction target and should be treated as a high-resource ceiling.",
        ),
    },
    {
        "id": "jarvisevo-2026",
        "title": "JarvisEvo: Towards a Self-Evolving Photo Editing Agent with Synergistic Editor-Evaluator Optimization",
        "venue": "CVPR 2026",
        "substrate": "open-weight-model-plus-proprietary-tool",
        "actor": "The released JarvisEvo-8B editor/evaluator stack integrates Qwen-Image-Edit and an Adobe Lightroom tool space.",
        "critic_or_judge": "A dual editor-evaluator loop is optimized with SFT/SEPO/RFT-style stages reported by the project.",
        "api_role": "A commercial LLM API is not required for the released 8B model, but Adobe Lightroom is a proprietary software dependency.",
        "parameter_updates": "The editor/evaluator system is trained; this is not inference-only.",
        "data": "ArtEdit-Bench and editing data released/described by the project.",
        "hardware": "Exact training hardware should be taken from the official appendix; inference weights are roughly 17 GB according to the release.",
        "code": "Official GitHub repository and model weights are public under their stated license.",
        "source": "https://github.com/LYL1015/JarvisEvo",
        "verification": "verified-official-code",
        "implication": bi(
            "开源 8B 编辑 Agent 可本地验证，但闭源工具依赖仍需显式报告。低资源研究可用 SDXL/FLUX 与开源编辑工具替代。",
            "The open 8B editing agent can be evaluated locally, but proprietary tool dependencies must be disclosed. Low-resource work can substitute SDXL/FLUX and open editing tools.",
        ),
    },
    {
        "id": "octot2i-2026",
        "title": "OctoT2I: A Self-Evolving Agentic Text-to-Image Router",
        "venue": "CVPR 2026",
        "substrate": "multi-tool-router-exact-substrates-pending",
        "actor": "An agentic router selects among multiple text-to-image tools and maintains an evolving capability knowledge base.",
        "critic_or_judge": "The propose-solve-evaluate-learn loop evaluates tool capability and routing outcomes.",
        "api_role": "Exact API/open-weight composition of every tool is pending verification from the official full paper and release.",
        "parameter_updates": "The capability knowledge base/router evolves; unrestricted full generator training is not the central contribution.",
        "data": "Text-to-image prompts and quality/efficiency evaluations described in the paper.",
        "hardware": "Unknown until official supplementary/configuration verification.",
        "code": "The official paper indicates release status; use the author release when available.",
        "source": "https://arxiv.org/abs/2606.01803",
        "verification": "partial-official",
        "implication": bi(
            "路由和能力记忆可做低资源研究，但必须分别报告本地生成器与外部 API 工具的调用成本和可复现性。",
            "Routing and capability memory are low-resource research targets, but local generators and external API tools must have separate cost and reproducibility reporting.",
        ),
    },
    {
        "id": "evograph-r1-2026",
        "title": "EvoGraph-R1: Self-Evolving Multimodal Knowledge Hypergraphs for Agentic Retrieval",
        "venue": "CVPR 2026",
        "substrate": "graph-and-web-tool-agent-exact-backbone-pending",
        "actor": "A multimodal agent selects GraphRetrieve, WebSearch, GraphEdit, and Answer actions over a dynamic hypergraph.",
        "critic_or_judge": "Retrieval and graph-edit outcomes provide the evolution signal.",
        "api_role": "Web search is an external service/tool; exact foundation-model and API choices remain pending official supplementary verification.",
        "parameter_updates": "The main evolving state is the multimodal graph rather than necessarily the foundation-model weights.",
        "data": "Agentic multimodal retrieval benchmarks reported in the paper.",
        "hardware": "Unknown until official appendix/configuration verification.",
        "code": "Use the official CVF/project release when available.",
        "source": "https://openaccess.thecvf.com/content/CVPR2026/html/Lin_EvoGraph-R1_Self-Evolving_Multimodal_Knowledge_Hypergraphs_for_Agentic_Retrieval_CVPR_2026_paper.html",
        "verification": "partial-official",
        "implication": bi(
            "图或记忆状态进化比模型权重训练更省资源，但外部搜索服务、缓存与图版本必须进入实验成本和复现协议。",
            "Graph or memory-state evolution is cheaper than weight training, but external search services, caching, and graph versions must be included in cost and reproducibility protocols.",
        ),
    },
)


# Chinese translations for all explanatory audit fields. Formal paper titles,
# model names, benchmark names, and venues remain in their original form.
ZH_FIELDS: dict[str, dict[str, str]] = {
    "clova-2024": {
        "actor": "主工具使用对比以 GPT-3.5 为规划模型；论文还评测了 Llama2-7B 和 GPT-4。",
        "critic_or_judge": "同一 LLM 闭环负责反思，任务专用视觉工具提供可执行反馈。",
        "api_role": "GPT-3.5-turbo 和 GPT-4 属于商业 API；LIST 工具使用 text-davinci-002；Llama2-7B 是开源权重替代方案。",
        "parameter_updates": "不对 LLM 做全量微调。系统保存正确/错误 demonstrations 进行上下文更新；视觉工具骨干保持冻结，只优化 soft prompts。",
        "data": "GQA、NLVRv2，以及人工收集的图像编辑和事实知识任务。",
        "hardware": "已检查的官方正文没有明确报告硬件。",
        "code": "官方项目页和代码均已公开。",
    },
    "virep-2024": {
        "actor": "使用开源代码 LLM 进行视觉程序合成自训练；复现前需从官方配置确认精确 checkpoint 版本。",
        "critic_or_judge": "使用稀疏二元执行奖励和过滤式行为克隆；少于 50 条人工修正用于扩展训练。",
        "api_role": "核心方法旨在避免依赖 GPT-4 这类强商业程序生成器。",
        "parameter_updates": "通过强化式自训练／过滤式行为克隆更新代码模型。",
        "data": "目标检测、组合式 VQA 和图文检索任务。",
        "hardware": "精确运行硬件需进一步核对官方 PDF 或配置。",
        "code": "官方项目页已公开。",
    },
    "se-vcl-2025": {
        "actor": "由视觉概念库和下游视觉推理系统组成；精确基础模型 checkpoint 需从官方配置中确认。",
        "critic_or_judge": "使用视觉语言 Critic 评估并修订概念。",
        "api_role": "官方摘要确认使用 VLM Critic，但不能据此判断所有 Critic 都是 API 托管还是本地模型。",
        "parameter_updates": "主要进化对象是概念库，而不是不受限制地训练完整骨干。",
        "data": "论文报告的视觉概念学习与下游识别／推理基准。",
        "hardware": "已检查的官方摘要和项目元数据没有明确报告硬件。",
        "code": "复现时应使用作者官方仓库；若论文页未链接仓库，则精确可用性仍标记为待确认。",
    },
    "visco-2025": {
        "actor": "发布的评测支持 GPT-4o、Claude-3.5-Sonnet、Gemini-1.5-Pro 等闭源模型，也支持 Qwen2-VL、Molmo、InternVL2、LLaVA、NVLM 和 Llama-3.2-Vision 等本地开源 LVLM。",
        "critic_or_judge": "LookBack 是推理时提示策略；发布的 explanation-F1 评测器默认使用 OpenAI API 模型，除非替换为本地评测器。",
        "api_role": "商业 API 是被评测的一类模型，也被辅助评测器使用；开源模型可通过 vLLM、lmdeploy 或 sglang 本地运行。",
        "parameter_updates": "Benchmark 和 LookBack 都不要求训练骨干参数。",
        "data": "1,645 个问答对和 5,604 条细粒度步骤标注。",
        "hardware": "本地部署需求取决于所选 LVLM，不存在统一硬件配置。",
        "code": "官方 GitHub 仓库已公开。",
    },
    "critic-v-2025": {
        "actor": "将推理 VLM 与独立 Critic 配对；精确的 reasoner／critic checkpoint 应以官方代码和配置为准。",
        "critic_or_judge": "Critic 使用规则奖励排序后的偏好 critique 数据进行 DPO 训练。",
        "api_role": "GPT-4V 作为对比模型；方法核心是独立训练 Critic，而不是仅依赖 API 的提示闭环。",
        "parameter_updates": "Critic 参数通过 DPO 更新，不属于纯推理时方法。",
        "data": "论文描述的多模态推理与 critique 数据。",
        "hardware": "精确硬件需进一步核对官方附录或配置。",
        "code": "应使用官方论文／项目材料；当前精确仓库可用性仍标记为待确认。",
    },
    "grounding-correction-2025": {
        "actor": "官方研究评测 GPT-4V／GPT-4o 及其他 LVLM；纠正流程基于 Prompt，且与具体模型无关。",
        "critic_or_judge": "模型执行迭代式二元验证与纠正。",
        "api_role": "GPT 模型需要商业 API，但方法结构本身不强制依赖 API。",
        "parameter_updates": "不进行微调、架构修改或外部训练数据注入。",
        "data": "论文报告的语义 grounding 评测集。",
        "hardware": "托管 GPT 运行不涉及本地硬件；本地模型硬件取决于所选开源 checkpoint。",
        "code": "官方 CVF／arXiv 材料已公开。",
    },
    "phoenix-2025": {
        "actor": "将运动条件扩散策略与 MLLM 驱动的动作调整模块结合；精确 MLLM checkpoint 需从官方配置确认。",
        "critic_or_judge": "基于运动的自反思提供纠正信号。",
        "api_role": "精确 MLLM 是否调用 API 仍需核对官方配置；策略本身经过训练并可本地执行。",
        "parameter_updates": "扩散策略／持续学习组件需要训练，不是免训练方法。",
        "data": "RoboMimic 仿真和真实机器人实验。",
        "hardware": "精确训练硬件仍待官方附录或配置核验。",
        "code": "作者官方 GitHub 仓库已公开。",
    },
    "vadar-2025": {
        "actor": "多个协作 LLM Agent 生成并调用动态 Python 视觉 API；精确 LLM 版本需从官方论文或配置确认。",
        "critic_or_judge": "执行结果和专职 Agent 为 API 创建与调用提供反馈。",
        "api_role": "官方摘要确认使用 LLM 程序合成，但无法单独判断所有主实验使用托管 API 还是本地开源权重。",
        "parameter_updates": "主要进化对象是动态 API／程序库，而不是训练完整基础模型。",
        "data": "Omni3D-Bench、CLEVR、GQA 和 VSI-Bench。",
        "hardware": "硬件需进一步核对官方附录或配置。",
        "code": "官方项目页已公开。",
    },
    "visplay-2026": {
        "actor": "以 Qwen2.5-VL 和 MiMo-VL 系列作为可训练 Questioner／Reasoner 基座。",
        "critic_or_judge": "自博弈难度／多样性奖励和可验证任务信号用于指导 GRPO。",
        "api_role": "核心训练闭环不需要商业模型 API。",
        "parameter_updates": "在大规模无标注图像上用 GRPO 联合优化 Questioner 和 Reasoner。",
        "data": "大规模无标注图像和多模态推理评测集。",
        "hardware": "属于高资源分布式训练；复现前应从官方附录复制精确配置。",
        "code": "官方 GitHub 仓库已公开。",
    },
    "jarvisevo-2026": {
        "actor": "发布的 JarvisEvo-8B Editor／Evaluator 系统结合 Qwen-Image-Edit 和 Adobe Lightroom 工具空间。",
        "critic_or_judge": "项目报告通过 SFT／SEPO／RFT 等阶段优化 Editor–Evaluator 双闭环。",
        "api_role": "发布的 8B 模型不要求商业 LLM API，但 Adobe Lightroom 是闭源软件依赖。",
        "parameter_updates": "Editor／Evaluator 系统需要训练，不属于纯推理时方法。",
        "data": "项目发布或描述的 ArtEdit-Bench 与图像编辑数据。",
        "hardware": "精确训练硬件应以官方附录为准；发布说明中推理权重约为 17 GB。",
        "code": "官方 GitHub 仓库和模型权重按其许可证公开。",
    },
    "octot2i-2026": {
        "actor": "Agent 路由器在多个文生图工具间选择，并维护持续进化的能力知识库。",
        "critic_or_judge": "propose–solve–evaluate–learn 闭环评估工具能力和路由结果。",
        "api_role": "每个工具的精确 API／开源权重组成仍待官方全文和发布材料确认。",
        "parameter_updates": "能力知识库／路由器持续进化，完整生成器训练不是核心贡献。",
        "data": "论文描述的文生图 Prompt、质量与效率评测。",
        "hardware": "硬件需进一步核对官方补充材料或配置。",
        "code": "论文声明了发布计划；复现时应使用作者官方版本。",
    },
    "evograph-r1-2026": {
        "actor": "多模态 Agent 在动态超图上选择 GraphRetrieve、WebSearch、GraphEdit 和 Answer 动作。",
        "critic_or_judge": "检索与图编辑结果构成进化信号。",
        "api_role": "Web 搜索是外部服务／工具；精确基础模型和 API 选择仍待官方补充材料核验。",
        "parameter_updates": "主要进化状态是多模态图，而不一定更新基础模型权重。",
        "data": "论文报告的 Agentic 多模态检索基准。",
        "hardware": "硬件需进一步核对官方附录或配置。",
        "code": "复现时应使用官方 CVF／项目发布版本。",
    },
}

LOCALIZED_FIELDS = (
    "actor", "critic_or_judge", "api_role", "parameter_updates",
    "data", "hardware", "code",
)


def _localized_paper(paper: dict[str, Any]) -> dict[str, Any]:
    result = dict(paper)
    translations = ZH_FIELDS.get(str(paper["id"]), {})
    for key in LOCALIZED_FIELDS:
        result[key] = bi(translations.get(key, str(paper[key])), str(paper[key]))
    return result


def build_payload() -> dict[str, Any]:
    counts: dict[str, int] = {}
    for paper in PAPERS:
        counts[paper["substrate"]] = counts.get(paper["substrate"], 0) + 1
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "policy": {
            "source_rule": bi(
                "只使用正式论文、项目页或作者代码；未报告字段不做推断。",
                "Official paper/project/author code only; unknown fields are not inferred.",
            ),
            "interpretation": bi(
                "分别报告 API、开源权重、参数训练和外部软件／工具依赖。",
                "API access, open weights, parameter training, and external software/tools are reported separately.",
            ),
        },
        "summary": {
            "papers": len(PAPERS),
            "substrate_counts": counts,
            "primary_recommendation": bi(
                "主结果使用开源权重；第二个开源架构验证迁移；商业 API 仅作为可选上界或 Judge。",
                "Open-weight primary results, second open architecture for transfer, commercial API only as optional ceiling/judge.",
            ),
        },
        "papers": [_localized_paper(paper) for paper in PAPERS],
    }


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    required = (
        "id", "title", "venue", "substrate", "actor", "critic_or_judge",
        "api_role", "parameter_updates", "data", "hardware", "code",
        "source", "verification", "implication",
    )
    for paper in payload.get("papers", []):
        if paper.get("id") in seen:
            errors.append(f"duplicate paper id: {paper.get('id')}")
        seen.add(str(paper.get("id")))
        for key in required:
            value = paper.get(key)
            if not value:
                errors.append(f"missing {key}: {paper.get('id')}")
            if key in LOCALIZED_FIELDS or key == "implication":
                if not isinstance(value, dict) or not value.get("zh") or not value.get("en"):
                    errors.append(f"missing bilingual {key}: {paper.get('id')}")
    if len(payload.get("papers", [])) < 10:
        errors.append("fewer than ten audited papers")
    return errors


def write_audit(json_path: Path = DEFAULT_JSON, js_path: Path = DEFAULT_JS) -> dict[str, Any]:
    payload = build_payload()
    errors = validate(payload)
    if errors:
        raise ValueError("Invalid published experiment audit:\n- " + "\n- ".join(errors))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text(
        "window.PUBLISHED_EXPERIMENT_AUDIT = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    return payload
