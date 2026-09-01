# E2-R17 API / Backbone / Verifier Design Correction

Date: 2026-08-30
Status: DESIGN CORRECTION ONLY / ZERO NEW SCIENTIFIC AUTHORITY

## 1. Ark Agent Plan protocol

The R17 OpenAI-compatible route is `https://ark.cn-beijing.volces.com/api/plan/v3`; native Responses requests are sent to `<base>/responses`. The current `ArkResponsesClient.endpoint` implements exactly this. A client that appends `/v1/responses` to this already-versioned base is incompatible with Ark Agent Plan.

The user-provided Anthropic-compatible route should be treated as a separate protocol/tool route and must not be mixed with OpenAI/Responses request schemas or credentials. Before any future Anthropic-client use, bind the exact console/documented Anthropic base URL and Messages path in a separate transport qualification.

## 2. Kimi-K3 qualification reinterpretation

The development qualification froze `max_output_tokens=4096`. Its only provider-incomplete response exhausted exactly 4096 output tokens. A zero-scientific technical smoke on 2026-08-30 accepted `max_output_tokens=8192` on the same Ark Agent Plan Responses route and returned `PLAN_OK` for `kimi-k3`.

Therefore the single 4096-token incomplete is classified as REQUEST_OUTPUT_BUDGET / API-CONFIGURATION evidence, not model-capability evidence.

The observed 18/18 development success means only that the selected six-task panel is ceiling-saturated for Kimi-K3. It does not disqualify Kimi-K3 as an agent backbone. It only means that panel is unsuitable for estimating capability headroom/noise under the frozen qualification rule.

## 3. Qwen3-8B qualification reinterpretation

The Qwen3-8B local run passed model provenance, vLLM startup, function-tool semantics after transport-ID canonicalization, and 6/6 technical rollout completion, but scored 0/6 on the six development tasks.

However the frozen generation configuration was `enable_thinking=false`, `temperature=0.0`, `top_p=1.0`. Qwen's official Qwen3 guidance recommends thinking mode by default and specifically warns against greedy decoding for thinking mode; recommended thinking settings are approximately temperature 0.6 / top_p 0.95, while recommended non-thinking settings are approximately temperature 0.7 / top_p 0.8. Thus the 0/6 result establishes a floor only for the tested non-thinking deterministic configuration, not an intrinsic Qwen3-8B capability floor.

A future Qwen3-8B capability check is scientifically permissible only as a new configuration-repair qualification using official model-card decoding settings on development-only tasks. If it remains at floor under supported settings, then capability-floor classification becomes defensible. Qwen3-8B should still not be promoted to a headline R17 backbone merely because it is locally available.

## 4. Verifier terminology correction

The controlled SpreadsheetBench endpoint is not an LLM evaluator. `SpreadsheetBenchEnv.score()` calls a deterministic `openpyxl` workbook comparator against the golden workbook/answer cells. Therefore the original WIN-A/WIN-B held-out variability is principally hosted actor-policy plus updater variability, not verifier-model stochasticity.

Replacing DeepSeek with Kimi/Qwen changes the task-solving actor/backbone, not merely the verifier. Such replacement cannot be interpreted as a single-variable evaluator repair.

## 5. Published-baseline design pattern

The top-venue baselines use strong task-capable backbones and benchmark-level evaluation rather than requiring a weak deterministic local evaluator:

- ReasoningBank/MaTTS (ICLR 2026): Gemini-2.5-Flash, Gemini-2.5-Pro, Claude-3.7-Sonnet; WebArena table uses 684 tasks and MaTTS parallel scaling K=5. The paper uses stochastic decoding (temperature 0.7) and reports success rate/steps across the benchmark.
- PolySkill (ICLR 2026): GPT-4.1, Claude-3.7-Sonnet, Qwen3-Coder-480B-A35B, GLM-4.5. The open-source Qwen baseline is an agentic 480B MoE model, not Qwen3-8B. It evaluates WebArena and Mind2Web; Mind2Web uses GPT-4.1 WebJudge at temperature 0.
- Agent Workflow Memory (ICML 2025): GPT-4o-2024-05-13 at temperature 0.0 for WebArena and describes the setting as mostly stable, not mathematically deterministic.
- ACE (ICLR 2026): DeepSeek-V3.1 is the default backbone; the same model is used for Generator/Reflector/Curator in the main fair comparison, with cross-model robustness later.
- SAGE (ACL 2026): Qwen2.5-32B-Instruct on AppWorld; this is a substantially stronger task backbone than an 8B local model.

## 6. R17 design consequence

Do not continue the "replacement evaluator" branch as currently formulated. Keep the deterministic workbook verifier fixed. Treat stochasticity as part of the actor/updater execution process and control it statistically/procedurally.

A new protocol version should:

1. use a strong agentic backbone as the primary executor (current qualified DeepSeek family is reasonable); 
2. use Kimi-K3 as a second-backbone robustness axis only after fixing request output budget, not as an evaluator replacement;
3. optionally requalify Qwen3-8B with official decoding settings as a low-capability sensitivity axis, but never make it the sole measurement backbone;
4. keep the workbook verifier identical across all methods;
5. compare WIN and MRW contemporaneously/interleaved under the same backbone and exact pools;
6. use replicated/randomized or paired stream-level analysis to absorb hosted stochasticity instead of requiring exact deterministic replay;
7. preserve the historical negative-control HOLD as evidence about nuisance magnitude, but do not reinterpret it as verifier failure or central-mechanism failure.

Any reopening of MRW requires a new versioned contract and independent review because the historical gate explicitly forbade MRW under the old protocol.
