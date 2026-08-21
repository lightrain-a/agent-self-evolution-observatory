from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from .alfworld_react_scaffold import react_scaffold
from .p0_alfworld_adapter import parse_admissible_choice


@dataclass(slots=True)
class _RemoteTokenizerFacade:
    policy: "VLLMAdmissiblePolicy"

    def encode(self, text: str, *, add_special_tokens: bool = False) -> list[int]:
        if add_special_tokens:
            raise ValueError("remote tokenizer facade supports add_special_tokens=False only")
        payload = self.policy._post("/tokenize", {"model": self.policy.model, "prompt": text})
        return [int(value) for value in payload.get("tokens") or []]

    def decode(self, ids: list[int], *, skip_special_tokens: bool = True) -> str:
        if not skip_special_tokens:
            raise ValueError("remote tokenizer facade supports skip_special_tokens=True only")
        payload = self.policy._post("/detokenize", {"model": self.policy.model, "tokens": [int(v) for v in ids]})
        return str(payload.get("prompt") or "")


class VLLMAdmissiblePolicy:
    """ALFWorld admissible-action policy backed by an existing OpenAI-compatible vLLM server.

    This is a transport adapter only. It mirrors HFAdmissiblePolicy's react-family prompt,
    recent-history truncation, deterministic decoding request, admissible-command parser,
    and token accounting while avoiding a second model load on an already occupied GPU.
    """

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        max_history: int = 6,
        policy_mode: str = "react-family",
        timeout_seconds: float = 60.0,
        seed: int | None = None,
    ) -> None:
        if policy_mode not in {"direct", "react-lite", "react-family"}:
            raise ValueError(f"unsupported policy_mode: {policy_mode}")
        self.base_url = str(base_url).rstrip("/")
        self.model = str(model)
        self.max_history = int(max_history)
        self.policy_mode = policy_mode
        self.timeout_seconds = float(timeout_seconds)
        self.seed = int(seed) if seed is not None else None
        self.session = requests.Session()
        self.tokenizer = _RemoteTokenizerFacade(self)
        self._input_tokens = 0
        self._output_tokens = 0
        self._generation_calls = 0
        models = self.session.get(self.base_url + "/v1/models", timeout=self.timeout_seconds)
        models.raise_for_status()
        ids = {str(row.get("id") or "") for row in (models.json().get("data") or []) if isinstance(row, dict)}
        if self.model not in ids:
            raise RuntimeError(f"served model {self.model!r} not present in vLLM model registry: {sorted(ids)}")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.session.post(self.base_url + path, json=payload, timeout=self.timeout_seconds)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError(f"vLLM {path} returned non-object JSON")
        return data

    def usage_snapshot(self) -> dict[str, int]:
        return {
            "input_tokens": self._input_tokens,
            "output_tokens": self._output_tokens,
            "tokens": self._input_tokens + self._output_tokens,
            "generation_calls": self._generation_calls,
        }

    def token_count(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def choose(
        self,
        observation: str,
        commands: list[str],
        history: list[tuple[str, str]],
        patch: str,
        *,
        goal_context: str = "",
        task_family: str = "unknown",
    ) -> tuple[str, bool, str]:
        if not commands:
            raise ValueError("commands cannot be empty")
        numbered = "\n".join(f"{i+1}. {command}" for i, command in enumerate(commands))
        history_text = "\n".join(f"Action: {a}\nObservation: {o}" for a, o in history[-self.max_history:])
        if self.policy_mode == "react-family":
            system = react_scaffold(task_family)
        elif self.policy_mode == "react-lite":
            system = (
                "You are a text-based household task agent. Track the goal, what you are holding, and which subgoal is next. "
                "Think briefly from the current observation and recent history, then finish with exactly one line "
                "`Action: <one exact admissible command>`. Do not invent commands. "
                "If the target object has not been found, search plausible receptacles systematically. "
                "If the task requires cleaning, cooling, or heating, complete that transformation before final placement."
            )
        else:
            system = (
                "You are an ALFWorld text agent. Choose exactly one admissible command. "
                "Return only the command text or its number. Do not explain."
            )
        if patch.strip():
            if patch.startswith("MEMORY::"):
                system += "\nRetrieved experience memory:\n" + patch.removeprefix("MEMORY::").strip()
            else:
                system += "\nPersistent prompt update:\n" + patch.strip()
        user = (
            f"Task goal (do not forget):\n{goal_context or 'complete the household task'}\n\n"
            f"Recent history:\n{history_text or '(none)'}\n\nCurrent observation:\n{observation}\n\n"
            f"Admissible commands:\n{numbered}\n\nChoose the next action."
        )
        request = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0,
            "max_tokens": 72 if self.policy_mode in {"react-lite", "react-family"} else 24,
        }
        if self.seed is not None:
            request["seed"] = self.seed
        payload = self._post("/v1/chat/completions", request)
        choices = payload.get("choices") or []
        if not choices or not isinstance(choices[0], dict):
            raise RuntimeError("vLLM returned no completion choice")
        message = choices[0].get("message") or {}
        raw = str(message.get("content") or "").strip()
        if not raw:
            raise RuntimeError("vLLM returned empty assistant content")
        usage = payload.get("usage") or {}
        self._input_tokens += int(usage.get("prompt_tokens") or 0)
        self._output_tokens += int(usage.get("completion_tokens") or 0)
        self._generation_calls += 1
        action, invalid = parse_admissible_choice(raw, commands)
        return action, invalid, raw
