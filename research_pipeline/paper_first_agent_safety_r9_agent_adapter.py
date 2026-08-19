from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class R9LocalQwenChatArgs:
    model_name: str = "Qwen3-8B"
    base_url: str = "http://127.0.0.1:18000/v1"
    api_key: str = "EMPTY"
    temperature: float = 0.1
    seed: int = 0
    max_total_tokens: int | None = None
    max_input_tokens: int | None = None
    max_new_tokens: int = 2000
    max_retries: int = 0

    def has_vision(self) -> bool:
        return False

    def make_chat_model(self):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=self.model_name,
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=self.temperature,
            max_tokens=self.max_new_tokens,
            max_retries=self.max_retries,
            model_kwargs={"seed": self.seed},
        )


def make_r9_awm_agent(*, awm_root: Path, workflow_path: Path, seed: int, qwen_base_url: str):
    awm_root = Path(awm_root).resolve()
    if str(awm_root) not in sys.path:
        sys.path.insert(0, str(awm_root))

    from webarena.agents.legacy.agent import GenericAgent
    from webarena.agents.legacy.dynamic_prompting import Flags

    flags = Flags(
        use_html=False,
        use_ax_tree=True,
        use_thinking=True,
        use_error_logs=True,
        use_past_error_logs=True,
        use_history=True,
        use_action_history=True,
        use_memory=False,
        use_diff=False,
        use_concrete_example=True,
        use_abstract_example=True,
        multi_actions=True,
        action_space="bid",
        is_strict=False,
        use_screenshot=False,
        enable_chat=True,
        max_prompt_tokens=None,
        demo_mode="off",
        workflow_path=str(Path(workflow_path).resolve()),
    )
    chat_args = R9LocalQwenChatArgs(base_url=qwen_base_url, seed=int(seed))
    agent = GenericAgent(chat_model_args=chat_args, flags=flags, max_retry=1)
    module_path = Path(sys.modules[GenericAgent.__module__].__file__).resolve()
    if awm_root not in module_path.parents:
        raise RuntimeError(f"GenericAgent was not loaded from frozen AWM root: {module_path}")
    return agent


def agent_runtime_contract(agent: Any) -> dict[str, Any]:
    args = agent.chat_model_args
    return {
        "model_name": args.model_name,
        "base_url": args.base_url,
        "temperature": args.temperature,
        "seed": args.seed,
        "max_total_tokens": args.max_total_tokens,
        "max_input_tokens": args.max_input_tokens,
        "max_new_tokens": args.max_new_tokens,
        "client_max_retries": args.max_retries,
        "generic_agent_max_retry": agent.max_retry,
        "use_html": agent.flags.use_html,
        "use_ax_tree": agent.flags.use_ax_tree,
        "use_thinking": agent.flags.use_thinking,
        "use_screenshot": agent.flags.use_screenshot,
        "multi_actions": agent.flags.multi_actions,
        "action_space": agent.flags.action_space,
        "enable_chat": agent.flags.enable_chat,
        "workflow_path": agent.flags.workflow_path,
    }
