from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import site
from collections import Counter
from pathlib import Path
from typing import Any


P0_EXTRA_SITE = Path(os.environ.get("P0_EXTRA_SITE", "/data/wyt/envs/agent_evolution_p0_site"))
if P0_EXTRA_SITE.exists():
    site.addsitedir(str(P0_EXTRA_SITE))


def _expand_vars(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expanduser(os.path.expandvars(value))
    if isinstance(value, list):
        return [_expand_vars(item) for item in value]
    if isinstance(value, dict):
        return {key: _expand_vars(item) for key, item in value.items()}
    return value


def load_config(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as error:
        raise RuntimeError("PyYAML is required by the ALFWorld runtime") from error
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return _expand_vars(payload)


def normalized_edit_distance(left: list[str], right: list[str]) -> float:
    if left == right:
        return 0.0
    if not left or not right:
        return 1.0
    prev = list(range(len(right) + 1))
    for i, x in enumerate(left, 1):
        cur = [i]
        for j, y in enumerate(right, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1] / max(len(left), len(right))


def action_family_shift(before: list[str], after: list[str]) -> float:
    def families(actions: list[str]) -> Counter[str]:
        return Counter((action.strip().split() or [""])[0].lower() for action in actions)
    left, right = families(before), families(after)
    total_left, total_right = sum(left.values()) or 1, sum(right.values()) or 1
    keys = set(left) | set(right)
    return 0.5 * sum(abs(left[key] / total_left - right[key] / total_right) for key in keys)


def parse_admissible_choice(raw: str, commands: list[str]) -> tuple[str, bool]:
    text = raw.strip()
    lowered = text.lower()
    for command in commands:
        if lowered == command.lower() or command.lower() in lowered:
            return command, False
    match = re.search(r"(?:^|\D)(\d{1,3})(?:\D|$)", text)
    if match:
        index = int(match.group(1)) - 1
        if 0 <= index < len(commands):
            return commands[index], False
    fallback = next((command for command in commands if command.lower() == "look"), commands[0])
    return fallback, True


class HFAdmissiblePolicy:
    def __init__(self, model_path: Path, *, device: str = "cuda", max_history: int = 6) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as error:
            raise RuntimeError("torch and transformers are required for the Qwen policy") from error
        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            str(model_path), local_files_only=True, torch_dtype="auto"
        ).to(device).eval()
        self.device = device
        self.max_history = max_history
        self._input_tokens = 0
        self._output_tokens = 0
        self._generation_calls = 0

    def _record_usage(self, inputs, suffix) -> None:
        self._input_tokens += int(inputs["input_ids"].numel())
        self._output_tokens += int(suffix.numel())
        self._generation_calls += 1

    def usage_snapshot(self) -> dict[str, int]:
        return {
            "input_tokens": self._input_tokens,
            "output_tokens": self._output_tokens,
            "tokens": self._input_tokens + self._output_tokens,
            "generation_calls": self._generation_calls,
        }

    def token_count(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def choose(self, observation: str, commands: list[str], history: list[tuple[str, str]], patch: str) -> tuple[str, bool, str]:
        numbered = "\n".join(f"{i+1}. {command}" for i, command in enumerate(commands))
        history_text = "\n".join(f"Action: {a}\nObservation: {o}" for a, o in history[-self.max_history:])
        system = (
            "You are an ALFWorld text agent. Choose exactly one admissible command. "
            "Return only the command text or its number. Do not explain."
        )
        if patch.strip():
            system += "\nPersistent prompt update:\n" + patch.strip()
        user = f"Recent history:\n{history_text or '(none)'}\n\nCurrent observation:\n{observation}\n\nAdmissible commands:\n{numbered}\n\nChoice:"
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            generated = self.model.generate(**inputs, max_new_tokens=24, do_sample=False, pad_token_id=self.tokenizer.eos_token_id)
        suffix = generated[0, inputs["input_ids"].shape[1]:]
        self._record_usage(inputs, suffix)
        raw = self.tokenizer.decode(suffix, skip_special_tokens=True).strip()
        action, invalid = parse_admissible_choice(raw, commands)
        return action, invalid, raw

    def propose_patch(self, trace: dict[str, Any], *, seed: int, previous_patch: str = "", variant: int = 0) -> str:
        self.torch.manual_seed(seed)
        if self.torch.cuda.is_available():
            self.torch.cuda.manual_seed_all(seed)
        actions = list(trace.get("actions") or [])[-12:]
        observations = list(trace.get("observations") or [])[-12:]
        paired = "\n".join(
            f"Action: {action}\nObservation: {observations[i] if i < len(observations) else ''}"
            for i, action in enumerate(actions)
        )
        system = (
            "You improve a persistent prompt for a text-based embodied agent. "
            "Return exactly one short, general instruction that could improve future behavior. "
            "Do not mention benchmark names, task IDs, or specific object instance numbers. "
            "Do not explain the instruction."
        )
        if variant % 2:
            system += " Prefer a planning or state-tracking rule rather than restating the failed action."
        user = (
            f"Outcome success={int(bool(trace.get('success')))}.\n"
            f"Current persistent patch:\n{previous_patch or '(none)'}\n\n"
            f"Recent trajectory:\n{paired or '(empty)'}\n\nNew instruction:"
        )
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            generated = self.model.generate(
                **inputs,
                max_new_tokens=56,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        suffix = generated[0, inputs["input_ids"].shape[1]:]
        self._record_usage(inputs, suffix)
        raw = self.tokenizer.decode(suffix, skip_special_tokens=True).strip()
        line = next((part.strip() for part in raw.splitlines() if part.strip()), raw).strip(" -*\t")
        return line[:500].strip()


class ALFWorldGameRunner:
    """Reuse the expensive ALFWorld wrapper discovery work within each split."""

    def __init__(self, config: dict[str, Any], environment_factory=None) -> None:
        if environment_factory is None:
            try:
                from alfworld.agents.environment import get_environment
            except ImportError as error:
                raise RuntimeError("ALFWorld is not installed in the selected runtime") from error
            environment_factory = get_environment
        self.config = config
        self.env_type = str(config["env"]["type"])
        self._environment_factory = environment_factory
        self._wrappers: dict[str, Any] = {}
        self._all_game_files: dict[str, tuple[str, ...]] = {}
        self.wrapper_build_count = 0

    def _wrapper(self, split: str):
        split = str(split)
        if split not in self._wrappers:
            wrapper = self._environment_factory(self.env_type)(self.config, train_eval=split)
            files = tuple(str(path) for path in list(getattr(wrapper, "game_files", []) or []))
            if not files:
                raise RuntimeError(f"ALFWorld exposed no game files for split {split}")
            self._wrappers[split] = wrapper
            self._all_game_files[split] = files
            self.wrapper_build_count += 1
        return self._wrappers[split]

    def available_game_files(self, split: str) -> list[str]:
        self._wrapper(split)
        return list(self._all_game_files[str(split)])

    def build_env(self, split: str, game_files: list[str] | None = None):
        wrapper = self._wrapper(split)
        if game_files is not None:
            wrapper.game_files = list(game_files)
            wrapper.num_games = len(wrapper.game_files)
        return wrapper.init_env(batch_size=1)

    def run_game_file(
        self,
        split: str,
        game_file: str,
        policy: HFAdmissiblePolicy,
        patch: str = "",
        max_steps: int = 50,
    ) -> dict[str, Any]:
        env = self.build_env(split, [game_file])
        try:
            trace = run_episode(env, policy, patch, max_steps=max_steps)
            trace["task_id"] = str(game_file)
            trace["gamefile"] = str(game_file)
            return trace
        finally:
            close = getattr(env, "close", None)
            if callable(close):
                close()


def build_env(config: dict[str, Any], split: str, game_files: list[str] | None = None):
    return ALFWorldGameRunner(config).build_env(split, game_files)


def available_game_files(config: dict[str, Any], split: str) -> list[str]:
    return ALFWorldGameRunner(config).available_game_files(split)


def run_episode(env, policy: HFAdmissiblePolicy, patch: str = "", max_steps: int = 50) -> dict[str, Any]:
    obs, info = env.reset()
    history: list[tuple[str, str]] = []
    actions: list[str] = []
    observations: list[str] = [str(obs[0])]
    raw_choices: list[str] = []
    invalid = 0
    start_obs = str(obs[0])
    gamefile = str((info.get("extra.gamefile") or [""])[0])
    done = False
    final_score = 0.0
    won = False
    while not done and len(actions) < max_steps:
        commands = list((info.get("admissible_commands") or [[]])[0])
        if not commands:
            break
        action, was_invalid, raw = policy.choose(str(obs[0]), commands, history, patch)
        invalid += int(was_invalid)
        actions.append(action)
        raw_choices.append(raw)
        obs, scores, dones, info = env.step([action])
        final_score = float(scores[0])
        done = bool(dones[0])
        won_values = info.get("won") or [False]
        won = bool(won_values[0])
        observations.append(str(obs[0]))
        history.append((action, str(obs[0])))
    task_id = gamefile or hashlib.sha256(start_obs.encode()).hexdigest()[:16]
    return {
        "task_id": task_id,
        "gamefile": gamefile,
        "initial_observation": start_obs,
        "success": int(won),
        "won": int(won),
        "score": final_score,
        "steps": len(actions),
        "invalid_actions": invalid,
        "invalid_choice_rate": invalid / max(1, len(actions)),
        "model_calls": len(actions),
        "actions": actions,
        "observations": observations,
        "raw_choices": raw_choices,
        "terminated": bool(done),
        "step_cap": int(max_steps),
    }


def run_game_file(
    config: dict[str, Any],
    split: str,
    game_file: str,
    policy: HFAdmissiblePolicy,
    patch: str = "",
    max_steps: int = 50,
) -> dict[str, Any]:
    return ALFWorldGameRunner(config).run_game_file(split, game_file, policy, patch, max_steps)


def compare_rollouts(before: dict[str, Any], after: dict[str, Any]) -> dict[str, float]:
    return {
        "action_sequence_distance": normalized_edit_distance(list(before["actions"]), list(after["actions"])),
        "invalid_action_rate": float(after["invalid_choice_rate"]),
        "instruction_choice_shift": action_family_shift(list(before["actions"]), list(after["actions"])),
        "plan_length": float(after["steps"]),
    }


def probe_model_artifacts(model_path: Path) -> dict[str, Any]:
    from safetensors import safe_open
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
    rendered = tokenizer.apply_chat_template(
        [{"role": "system", "content": "runtime smoke"}, {"role": "user", "content": "choose one action"}],
        tokenize=False,
        add_generation_prompt=True,
    )
    index_path = model_path / "model.safetensors.index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    shards = sorted(set((index.get("weight_map") or {}).values()))
    if not shards:
        raise RuntimeError("model index exposes no safetensors shards")
    probes: list[dict[str, Any]] = []
    for shard in shards:
        shard_path = model_path / shard
        with safe_open(str(shard_path), framework="pt", device="cpu") as handle:
            keys = list(handle.keys())
            if not keys:
                raise RuntimeError(f"empty model shard: {shard}")
            def tensor_size(key: str) -> int:
                total = 1
                for dim in handle.get_slice(key).get_shape():
                    total *= int(dim)
                return total
            key = min(keys, key=tensor_size)
            tensor = handle.get_tensor(key)
            probes.append({"shard": shard, "tensor": key, "numel": int(tensor.numel())})
    return {
        "tokenizer_class": type(tokenizer).__name__,
        "chat_template_ready": bool(rendered and "assistant" in rendered),
        "shards": probes,
    }


def run_lightweight_smoke(config_path: Path, model_path: Path, split: str) -> dict[str, Any]:
    model_probe = probe_model_artifacts(model_path)
    config = load_config(config_path)
    env = build_env(config, split)
    try:
        obs, info = env.reset()
        commands = list((info.get("admissible_commands") or [[]])[0])
        if not commands:
            raise RuntimeError("ALFWorld smoke exposed no admissible commands")
        raw = "1"
        action, invalid = parse_admissible_choice(raw, commands)
        obs2, scores, dones, info2 = env.step([action])
        gamefile = str((info.get("extra.gamefile") or [""])[0])
        won_values = info2.get("won") or [False]
        return {
            "gamefile": gamefile,
            "steps": 1,
            "action": action,
            "parser_invalid": bool(invalid),
            "raw_choice": raw,
            "score": float(scores[0]),
            "done": bool(dones[0]),
            "won": int(bool(won_values[0])),
            "observation_ready": bool(obs and obs2),
            "command_count": len(commands),
            "model_probe": model_probe,
        }
    finally:
        close = getattr(env, "close", None)
        if callable(close):
            close()


def run_smoke(config_path: Path, model_path: Path, split: str, episodes: int, patch: str, max_steps: int = 1) -> list[dict[str, Any]]:
    """Full-generation diagnostic kept for manual debugging, not readiness gating."""
    config = load_config(config_path)
    policy = HFAdmissiblePolicy(model_path)
    env = build_env(config, split)
    try:
        return [run_episode(env, policy, patch, max_steps=max_steps) for _ in range(episodes)]
    finally:
        close = getattr(env, "close", None)
        if callable(close):
            close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Thin ALFWorld/Qwen adapter for P0 rollout collection.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, default=Path("/data/wyt/models/indept/Qwen2.5-7B"))
    parser.add_argument("--split", choices=["train", "eval_in_distribution", "eval_out_of_distribution"], default="eval_out_of_distribution")
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--patch", default="")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = run_smoke(args.config, args.model_path, args.split, args.episodes, args.patch)
    text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
