# Published visual-agent substrate audit: 2024–2025

Use web research and consult only official paper PDFs, CVF/OpenReview/ACL/NeurIPS pages, official project pages, and author-maintained GitHub repositories.

Audit these published papers:

1. CLOVA: A Closed-Loop Visual Assistant with Tool Usage and Update (CVPR 2024)
2. Self-Training Large Language Models for Improved Visual Program Synthesis with Visual Reinforcement (CVPR 2024)
3. Self-Evolving Visual Concept Library using Vision-Language Critics (CVPR 2025)
4. VISCO: Benchmarking Fine-Grained Critique and Correction towards Self-Improvement in Visual Reasoning (CVPR 2025)
5. Critic-V: VLM Critics Help Catch VLM Errors in Multimodal Reasoning (CVPR 2025)
6. Can Large Vision-Language Models Correct Semantic Grounding Errors By Themselves? (CVPR 2025)
7. Phoenix: A Motion-based Self-Reflection Framework for Fine-grained Robotic Action Correction (CVPR 2025)
8. Visual Agentic AI for Spatial Reasoning with a Dynamic API (CVPR 2025)

For every paper report:

- exact title, venue, and year;
- exact backbone or foundation model names used in the main experiments;
- whether each model is accessed through a commercial API, uses open weights locally, or both;
- whether the method updates backbone weights, trains adapters/critics/tools, or is inference-only;
- datasets, simulators, or environments;
- hardware and compute only when explicitly reported;
- official code/project availability;
- direct source URLs;
- facts that remain unknown after checking the official materials.

Do not infer API use merely from a model family name. Distinguish the model that acts as the agent from models used only for data generation, evaluation, captioning, or judging.

Conclude with concrete implications for designing a low-resource CVPR experiment on agent self-evolution: which open models are credible, when a commercial API is unavoidable, what should be frozen, and what minimum cross-model validation is needed.

Return a compact but detailed Markdown table followed by recommendations.