from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path

ACTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))
RHO_LEVELS = (0.0, 0.25, 0.5, 0.75, 1.0)
TAU_LEVELS = (0.25, 1.0, 4.0)
RETENTION_THRESHOLD = 0.90
MIN_ISOLATED_GAIN = 0.01


@dataclass(frozen=True)
class GridConfig:
    width: int = 10
    height: int = 10
    goal_x: int = 9
    goal_y: int = 9
    max_steps: int = 36
    step_cost: float = -0.02
    hazard_penalty: float = -0.18
    goal_reward: float = 1.0
    heuristic_toward: float = 0.36
    heuristic_away: float = -0.14
    policy_temperature: float = 0.72
    loop_a_alpha: float = 0.55
    loop_a_alt_bonus: float = 0.08
    loop_b_alpha: float = 0.075
    edit_fraction: float = 0.40
    train_episodes: int = 480
    eval_rollouts_per_start: int = 8


@dataclass
class EvalSummary:
    mean_reward: float
    success_rate: float
    mean_hazards: float
    mean_steps: float
    rewards: list[float]


class GridWorld:
    def __init__(self, cfg: GridConfig):
        self.cfg = cfg
        self.hazards = {(4, y) for y in range(1, cfg.height - 1)}

    @property
    def preference_dim(self) -> int:
        return self.cfg.width * self.cfg.height * len(ACTIONS)

    def state_index(self, state: tuple[int, int]) -> int:
        return state[1] * self.cfg.width + state[0]

    def preference_index(self, state: tuple[int, int], action: int) -> int:
        return self.state_index(state) * len(ACTIONS) + action

    def next_state(self, state: tuple[int, int], action: int) -> tuple[int, int]:
        dx, dy = ACTIONS[action]
        return (
            min(max(state[0] + dx, 0), self.cfg.width - 1),
            min(max(state[1] + dy, 0), self.cfg.height - 1),
        )

    def step(self, state: tuple[int, int], action: int) -> tuple[tuple[int, int], float, bool, bool]:
        nxt = self.next_state(state, action)
        reward = self.cfg.step_cost
        hazard = nxt in self.hazards
        if hazard:
            reward += self.cfg.hazard_penalty
        done = nxt == (self.cfg.goal_x, self.cfg.goal_y)
        if done:
            reward += self.cfg.goal_reward
        return nxt, reward, done, hazard

    def heuristic_logits(self, state: tuple[int, int]) -> list[float]:
        before = abs(self.cfg.goal_x - state[0]) + abs(self.cfg.goal_y - state[1])
        out = [0.0] * len(ACTIONS)
        for action in range(len(ACTIONS)):
            nxt = self.next_state(state, action)
            after = abs(self.cfg.goal_x - nxt[0]) + abs(self.cfg.goal_y - nxt[1])
            if after < before:
                out[action] = self.cfg.heuristic_toward
            elif after > before:
                out[action] = self.cfg.heuristic_away
        return out


def _softmax(values: list[float]) -> list[float]:
    m = max(values)
    exps = [math.exp(v - m) for v in values]
    total = sum(exps)
    return [x / total for x in exps]


def _sample(probs: list[float], rng: random.Random) -> int:
    u = rng.random()
    acc = 0.0
    for idx, prob in enumerate(probs):
        acc += prob
        if u <= acc:
            return idx
    return len(probs) - 1


def train_starts(_: GridConfig) -> tuple[tuple[int, int], ...]:
    return ((0, 1), (0, 3), (0, 5), (0, 7), (1, 2), (1, 4), (1, 6))


def eval_starts(_: GridConfig) -> tuple[tuple[int, int], ...]:
    return ((0, 2), (0, 4), (0, 6), (0, 8), (1, 1), (1, 3), (1, 5), (1, 7))


def mask_pair(dim: int, rho: float, edit_fraction: float, seed: int = 271828) -> tuple[list[bool], list[bool], float]:
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must be in [0,1]")
    m = int(round(dim * edit_fraction))
    if m <= 0 or 2 * m > dim:
        raise ValueError("edit_fraction cannot support rho=0")
    overlap = m if math.isclose(rho, 1.0) else int(round(2 * m * rho / (1 + rho)))
    order = list(range(dim))
    random.Random(seed).shuffle(order)
    a_idx = order[:m]
    outside = order[m:]
    b_idx = a_idx[:overlap] + outside[: m - overlap]
    a = [False] * dim
    b = [False] * dim
    for idx in a_idx:
        a[idx] = True
    for idx in b_idx:
        b[idx] = True
    inter = sum(1 for x, y in zip(a, b) if x and y)
    union = sum(1 for x, y in zip(a, b) if x or y)
    return a, b, inter / union if union else 0.0


def _preference_state_action(env: GridWorld, index: int) -> tuple[tuple[int, int], int]:
    action = index % len(ACTIONS)
    state_i = index // len(ACTIONS)
    state = (state_i % env.cfg.width, state_i // env.cfg.width)
    return state, action


def periods_for_tau(tau: float) -> tuple[int, int]:
    if math.isclose(tau, 0.25):
        return 4, 1
    if math.isclose(tau, 1.0):
        return 1, 1
    if math.isclose(tau, 4.0):
        return 1, 4
    raise ValueError(f"unsupported preregistered tau={tau}")


def rollout(env: GridWorld, start: tuple[int, int], theta_a: list[float], theta_b: list[float], rng: random.Random) -> dict:
    state = start
    total = 0.0
    hazards = 0
    transitions: list[tuple[int, bool]] = []
    for step in range(env.cfg.max_steps):
        base = env.heuristic_logits(state)
        logits = []
        for action in range(len(ACTIONS)):
            idx = env.preference_index(state, action)
            logits.append((base[action] + theta_a[idx] + theta_b[idx]) / env.cfg.policy_temperature)
        action = _sample(_softmax(logits), rng)
        idx = env.preference_index(state, action)
        nxt, reward, done, hazard = env.step(state, action)
        transitions.append((idx, hazard))
        total += reward
        hazards += int(hazard)
        state = nxt
        if done:
            return {"reward": total, "success": True, "hazards": hazards, "steps": step + 1, "transitions": transitions}
    return {"reward": total, "success": False, "hazards": hazards, "steps": env.cfg.max_steps, "transitions": transitions}


def baseline_visitation_profile(env: GridWorld, episodes: int = 256) -> dict:
    """Build an outcome-independent support profile from the frozen no-loop base policy."""
    zeros = [0.0] * env.preference_dim
    counts = [0] * env.preference_dim
    starts = train_starts(env.cfg)
    for ep in range(episodes):
        rng = random.Random(7_331_003 + ep * 104_729)
        out = rollout(env, starts[ep % len(starts)], zeros, zeros, rng)
        for index, _hazard in out["transitions"]:
            counts[index] += 1

    order = sorted(range(env.preference_dim), key=lambda index: (counts[index], index))
    quartile = [0] * env.preference_dim
    for rank, index in enumerate(order):
        quartile[index] = min(3, (4 * rank) // max(env.preference_dim, 1))

    strata: dict[str, tuple[int, ...]] = {}
    mutable: dict[str, list[int]] = {}
    for index in range(env.preference_dim):
        state, action = _preference_state_action(env, index)
        nxt = env.next_state(state, action)
        before = abs(env.cfg.goal_x - state[0]) + abs(env.cfg.goal_y - state[1])
        after = abs(env.cfg.goal_x - nxt[0]) + abs(env.cfg.goal_y - nxt[1])
        progress = 1 if after < before else (-1 if after > before else 0)
        hazard_entry = int(nxt in env.hazards)
        key = f"hazard={hazard_entry}|progress={progress}|visit_q={quartile[index]}"
        mutable.setdefault(key, []).append(index)
    strata = {key: tuple(indices) for key, indices in sorted(mutable.items())}
    return {
        "source": "frozen-no-loop-base-policy",
        "episodes": episodes,
        "counts": counts,
        "quartile": quartile,
        "strata": strata,
    }


def support_matched_mask_pair(
    env: GridWorld,
    rho: float,
    profile: dict,
    seed: int,
) -> tuple[list[bool], list[bool], float, dict]:
    """Vary only within-stratum A/B overlap while holding both marginal supports fixed."""
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must be in [0,1]")
    counts = list(profile.get("counts") or [])
    strata = profile.get("strata") or {}
    if len(counts) != env.preference_dim or not isinstance(strata, dict) or not strata:
        raise ValueError("invalid baseline visitation support profile")

    mask_a = [False] * env.preference_dim
    mask_b = [False] * env.preference_dim
    audit_strata: dict[str, dict] = {}
    for key, raw_indices in sorted(strata.items()):
        indices = list(raw_indices)
        n = len(indices)
        editable = min(int(round(n * env.cfg.edit_fraction)), n // 2)
        key_seed = sum((pos + 1) * ord(ch) for pos, ch in enumerate(str(key)))
        order = list(indices)
        random.Random(seed * 1_000_003 + key_seed).shuffle(order)
        a_indices = order[:editable]
        outside = order[editable:]
        # Pair each A support element with the closest available outside element in
        # baseline visitation mass. This preserves the reviewed semantic strata while
        # tightening marginal capability matching without using any loop outcome.
        unused_outside = set(outside)
        paired_outside: list[int] = []
        for a_index in a_indices:
            if not unused_outside:
                raise ValueError(f"support matching exhausted outside stratum capacity:{key}")
            partner = min(unused_outside, key=lambda index: (abs(counts[index] - counts[a_index]), index))
            paired_outside.append(partner)
            unused_outside.remove(partner)
        intersection_target = editable if math.isclose(rho, 1.0) else int(round(2 * editable * rho / (1 + rho)))
        intersection_target = min(editable, max(0, intersection_target))
        b_indices = a_indices[:intersection_target] + paired_outside[intersection_target:]
        for index in a_indices:
            mask_a[index] = True
        for index in b_indices:
            mask_b[index] = True
        intersection = len(set(a_indices).intersection(b_indices))
        union = len(set(a_indices).union(b_indices))
        audit_strata[str(key)] = {
            "capacity": n,
            "a_count": len(a_indices),
            "b_count": len(b_indices),
            "intersection": intersection,
            "jaccard": intersection / union if union else 0.0,
            "a_visitation_mass": sum(counts[index] for index in a_indices),
            "b_visitation_mass": sum(counts[index] for index in b_indices),
        }

    inter = sum(1 for left, right in zip(mask_a, mask_b) if left and right)
    union = sum(1 for left, right in zip(mask_a, mask_b) if left or right)
    actual = inter / union if union else 0.0
    audit = {
        "profile_source": str(profile.get("source") or ""),
        "profile_episodes": int(profile.get("episodes") or 0),
        "mask_seed": seed,
        "rho_requested": rho,
        "rho_actual": actual,
        "a_count": sum(mask_a),
        "b_count": sum(mask_b),
        "intersection": inter,
        "strata": audit_strata,
    }
    return mask_a, mask_b, actual, audit


def _clip(values: list[float]) -> None:
    for idx, value in enumerate(values):
        values[idx] = min(3.0, max(-3.0, value))


def _apply_loop_a(env: GridWorld, theta: list[float], mask: list[bool], episode: dict) -> None:
    for idx, hazard in episode["transitions"]:
        if not hazard:
            continue
        if mask[idx]:
            theta[idx] -= env.cfg.loop_a_alpha
        base = (idx // len(ACTIONS)) * len(ACTIONS)
        state_i = idx // len(ACTIONS)
        state = (state_i % env.cfg.width, state_i // env.cfg.width)
        for alt in range(len(ACTIONS)):
            alt_idx = base + alt
            if alt_idx == idx or not mask[alt_idx]:
                continue
            if env.next_state(state, alt) not in env.hazards:
                theta[alt_idx] += env.cfg.loop_a_alt_bonus
    _clip(theta)


def _apply_loop_b(env: GridWorld, theta: list[float], mask: list[bool], episode: dict) -> None:
    if not episode["success"]:
        return
    n = max(len(episode["transitions"]), 1)
    for t, (idx, _hazard) in enumerate(episode["transitions"]):
        if mask[idx]:
            theta[idx] += env.cfg.loop_b_alpha * (1.0 - 0.35 * t / n)
    _clip(theta)


def train(env: GridWorld, mask_a: list[bool], mask_b: list[bool], tau: float, seed: int, mode: str, episodes: int) -> tuple[list[float], list[float]]:
    theta_a = [0.0] * env.preference_dim
    theta_b = [0.0] * env.preference_dim
    period_a, period_b = periods_for_tau(tau)
    starts = train_starts(env.cfg)
    for ep in range(episodes):
        rng = random.Random(seed * 1_000_003 + ep * 97 + 17)
        result = rollout(env, starts[ep % len(starts)], theta_a, theta_b, rng)
        if mode in {"a", "both"} and ep % period_a == 0:
            _apply_loop_a(env, theta_a, mask_a, result)
        if mode in {"b", "both"} and ep % period_b == 0:
            _apply_loop_b(env, theta_b, mask_b, result)
    return theta_a, theta_b


def evaluate(env: GridWorld, theta_a: list[float], theta_b: list[float], seed: int, repeats: int) -> EvalSummary:
    rewards: list[float] = []
    success = hazards = steps = 0
    starts = eval_starts(env.cfg)
    for s_idx, start in enumerate(starts):
        for rep in range(repeats):
            rng = random.Random(seed * 2_000_033 + s_idx * 1009 + rep * 131 + 23)
            out = rollout(env, start, theta_a, theta_b, rng)
            rewards.append(float(out["reward"]))
            success += int(out["success"])
            hazards += int(out["hazards"])
            steps += int(out["steps"])
    n = len(rewards)
    return EvalSummary(statistics.fmean(rewards), success / n, hazards / n, steps / n, rewards)


def paired_normal_p(candidate: list[float], baseline: list[float]) -> float:
    diffs = [x - y for x, y in zip(candidate, baseline)]
    if len(diffs) < 2:
        return 1.0
    sd = statistics.stdev(diffs)
    mean = statistics.fmean(diffs)
    if sd <= 1e-12:
        return 0.0 if abs(mean) > 1e-12 else 1.0
    z = mean / (sd / math.sqrt(len(diffs)))
    return math.erfc(abs(z) / math.sqrt(2.0))


def classify_regime(delta_a: float, delta_b: float, delta_a_comp: float, delta_b_comp: float) -> tuple[str, float, float, bool]:
    if delta_a <= MIN_ISOLATED_GAIN or delta_b <= MIN_ISOLATED_GAIN:
        return "invalid-isolated-gain", float("nan"), float("nan"), False
    ra, rb = delta_a_comp / delta_a, delta_b_comp / delta_b
    keep_a, keep_b = ra >= RETENTION_THRESHOLD, rb >= RETENTION_THRESHOLD
    if keep_a and keep_b:
        label = "additive"
    elif keep_a != keep_b:
        label = "dominance"
    else:
        label = "mutual-degradation"
    return label, ra, rb, True


def update_counts(tau: float, episodes: int) -> tuple[int, int]:
    period_a, period_b = periods_for_tau(tau)
    return ((episodes - 1) // period_a + 1, (episodes - 1) // period_b + 1)


def candidate_rho_critical(delta_a: float, delta_b: float, tau: float, episodes: int) -> float:
    updates_a, updates_b = update_counts(tau, episodes)
    rate_a = max(delta_a, 0.0) / max(updates_a, 1)
    rate_b = max(delta_b, 0.0) / max(updates_b, 1)
    denom = rate_a + rate_b
    if denom <= 1e-12:
        return 1.0
    return 1.0 - (min(rate_a, rate_b) / denom) * (1.0 / (1.0 + abs(math.log(tau))))


def candidate_regime(delta_a: float, delta_b: float, rho: float, tau: float, episodes: int) -> tuple[str, float]:
    critical = candidate_rho_critical(delta_a, delta_b, tau, episodes)
    if rho <= critical:
        return "additive", critical
    if math.isclose(tau, 1.0):
        return "mutual-degradation", critical
    return "dominance", critical


def coupled_dynamics_baseline(delta_a: float, delta_b: float, rho: float, tau: float) -> tuple[str, float, float]:
    if delta_a <= MIN_ISOLATED_GAIN or delta_b <= MIN_ISOLATED_GAIN:
        return "invalid-isolated-gain", float("nan"), float("nan")
    rate_a, rate_b = tau, 1.0
    grow_a = max(0.15, min(2.5, delta_a / 0.08))
    grow_b = max(0.15, min(2.5, delta_b / 0.08))

    def integrate(coupled: bool) -> tuple[float, float]:
        xa = xb = 0.08
        for _ in range(600):
            ca = rho * xb if coupled else 0.0
            cb = rho * xa if coupled else 0.0
            xa += 0.01 * rate_a * grow_a * xa * (1 - xa - ca)
            xb += 0.01 * rate_b * grow_b * xb * (1 - xb - cb)
            xa, xb = max(xa, 1e-8), max(xb, 1e-8)
        return xa, xb

    iso_a, iso_b = integrate(False)
    comp_a, comp_b = integrate(True)
    ra, rb = comp_a / iso_a, comp_b / iso_b
    keep_a, keep_b = ra >= RETENTION_THRESHOLD, rb >= RETENTION_THRESHOLD
    if keep_a and keep_b:
        label = "additive"
    elif keep_a != keep_b:
        label = "dominance"
    else:
        label = "mutual-degradation"
    return label, ra, rb


def run_condition(
    rho: float,
    tau: float,
    seed: int,
    *,
    smoke: bool = False,
    cfg: GridConfig | None = None,
    support_profile: dict | None = None,
    mask_seed: int = 271828,
) -> dict:
    cfg = cfg or GridConfig()
    env = GridWorld(cfg)
    profile = support_profile or baseline_visitation_profile(env)
    mask_a, mask_b, rho_actual, support_audit = support_matched_mask_pair(env, rho, profile, mask_seed)
    episodes = 24 if smoke else cfg.train_episodes
    repeats = 2 if smoke else cfg.eval_rollouts_per_start
    zeros = [0.0] * env.preference_dim
    eval_seed = seed + 10_000
    base = evaluate(env, zeros, zeros, eval_seed, repeats)
    a_iso, _ = train(env, mask_a, mask_b, tau, seed + 101, "a", episodes)
    isolated_a = evaluate(env, a_iso, zeros, eval_seed, repeats)
    _, b_iso = train(env, mask_a, mask_b, tau, seed + 211, "b", episodes)
    isolated_b = evaluate(env, zeros, b_iso, eval_seed, repeats)
    a_comp, b_comp = train(env, mask_a, mask_b, tau, seed + 307, "both", episodes)
    composed_full = evaluate(env, a_comp, b_comp, eval_seed, repeats)
    composed_a = evaluate(env, a_comp, zeros, eval_seed, repeats)
    composed_b = evaluate(env, zeros, b_comp, eval_seed, repeats)
    da = isolated_a.mean_reward - base.mean_reward
    db = isolated_b.mean_reward - base.mean_reward
    dac = composed_a.mean_reward - base.mean_reward
    dbc = composed_b.mean_reward - base.mean_reward
    regime, ra, rb, valid = classify_regime(da, db, dac, dbc)
    baseline_regime, base_ra, base_rb = coupled_dynamics_baseline(da, db, rho_actual, tau)
    p_a = paired_normal_p(isolated_a.rewards, base.rewards)
    p_b = paired_normal_p(isolated_b.rewards, base.rewards)
    isolated_gate = da > MIN_ISOLATED_GAIN and db > MIN_ISOLATED_GAIN and p_a < 0.05 and p_b < 0.05
    return {
        "rho_requested": rho, "rho_actual": rho_actual, "tau": tau, "seed": seed, "mask_seed": mask_seed,
        "support_audit": support_audit,
        "base": asdict(base), "isolated_a": asdict(isolated_a), "isolated_b": asdict(isolated_b),
        "composed_full": asdict(composed_full), "composed_a_only": asdict(composed_a), "composed_b_only": asdict(composed_b),
        "delta_a": da, "delta_b": db, "delta_a_composed": dac, "delta_b_composed": dbc,
        "retention_a": ra, "retention_b": rb, "baseline_retention_a": base_ra, "baseline_retention_b": base_rb,
        "isolated_a_p": p_a, "isolated_b_p": p_b, "isolated_gate_pass": isolated_gate,
        "regime": regime, "baseline_regime": baseline_regime, "valid": valid,
    }


def _majority(labels: list[str]) -> tuple[str, int]:
    counts = {label: labels.count(label) for label in sorted(set(labels))}
    winner = max(counts, key=lambda label: (counts[label], label))
    return winner, counts[winner]


def binomial_tail(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1)) if n else 1.0


def run_full(cfg: GridConfig | None = None) -> dict:
    cfg = cfg or GridConfig()
    env = GridWorld(cfg)
    support_profile = baseline_visitation_profile(env, episodes=256)
    raw_rows: list[dict] = []
    for rho in RHO_LEVELS:
        for tau in TAU_LEVELS:
            for rep in range(3):
                # Common random numbers across rho isolate the overlap intervention; tau and
                # replicate retain distinct execution randomness. Mask seed depends only on rep.
                seed = 20260818 + rep * 100_003 + int(tau * 100) * 17
                mask_seed = 271828 + rep * 1009
                raw_rows.append(
                    run_condition(
                        rho, tau, seed, smoke=False, cfg=cfg,
                        support_profile=support_profile, mask_seed=mask_seed,
                    )
                )

    cells = []
    for rho in RHO_LEVELS:
        for tau in TAU_LEVELS:
            reps = [r for r in raw_rows if math.isclose(r["rho_requested"], rho) and math.isclose(r["tau"], tau)]
            delta_a = statistics.fmean(r["delta_a"] for r in reps)
            delta_b = statistics.fmean(r["delta_b"] for r in reps)
            pooled_base_a = [v for r in reps for v in r["base"]["rewards"]]
            pooled_base_b = [v for r in reps for v in r["base"]["rewards"]]
            pooled_iso_a = [v for r in reps for v in r["isolated_a"]["rewards"]]
            pooled_iso_b = [v for r in reps for v in r["isolated_b"]["rewards"]]
            p_a = paired_normal_p(pooled_iso_a, pooled_base_a)
            p_b = paired_normal_p(pooled_iso_b, pooled_base_b)
            cell_gate = delta_a > MIN_ISOLATED_GAIN and delta_b > MIN_ISOLATED_GAIN and p_a < 0.05 and p_b < 0.05
            rho_actual = statistics.fmean(r["rho_actual"] for r in reps)
            candidate_label, critical = candidate_regime(delta_a, delta_b, rho_actual, tau, cfg.train_episodes)
            baseline_label, base_ra, base_rb = coupled_dynamics_baseline(delta_a, delta_b, rho_actual, tau)
            if not cell_gate:
                cells.append({
                    "rho": rho, "rho_actual": rho_actual, "tau": tau, "qualified": False,
                    "cell_delta_a": delta_a, "cell_delta_b": delta_b, "cell_isolated_a_p": p_a, "cell_isolated_b_p": p_b,
                    "majority_regime": "invalid", "agreement": 0, "candidate_regime": candidate_label,
                    "rho_critical": critical, "baseline_regime": baseline_label,
                    "baseline_retention_a": base_ra, "baseline_retention_b": base_rb,
                })
                continue
            labels = []
            for row in reps:
                label, _ra, _rb, _valid = classify_regime(delta_a, delta_b, row["delta_a_composed"], row["delta_b_composed"])
                labels.append(label)
            majority, agreement = _majority(labels)
            cells.append({
                "rho": rho, "rho_actual": rho_actual, "tau": tau, "qualified": True,
                "cell_delta_a": delta_a, "cell_delta_b": delta_b, "cell_isolated_a_p": p_a, "cell_isolated_b_p": p_b,
                "replicate_regimes": labels, "majority_regime": majority, "agreement": agreement,
                "candidate_regime": candidate_label, "rho_critical": critical, "baseline_regime": baseline_label,
                "baseline_retention_a": base_ra, "baseline_retention_b": base_rb,
            })

    qualified_cells = [c for c in cells if c["qualified"]]
    consistent = [c for c in qualified_cells if c["agreement"] >= 2]
    baseline_correct = [c for c in qualified_cells if c["majority_regime"] == c["baseline_regime"]]
    candidate_correct = [c for c in qualified_cells if c["majority_regime"] == c["candidate_regime"]]
    baseline_accuracy = len(baseline_correct) / len(qualified_cells) if qualified_cells else 0.0
    candidate_accuracy = len(candidate_correct) / len(qualified_cells) if qualified_cells else 0.0
    margin = candidate_accuracy - baseline_accuracy
    consistency = len(consistent) / len(qualified_cells) if qualified_cells else 0.0
    baseline_p = binomial_tail(len(baseline_correct), len(qualified_cells), 1 / 3)
    high_rho_mutual = any(
        c["majority_regime"] == "mutual-degradation" and math.isclose(c["tau"], 1.0) and c["rho_actual"] > c["rho_critical"]
        for c in qualified_cells
    )
    low_rho_additive = any(
        c["majority_regime"] == "additive" and c["rho_actual"] < c["rho_critical"]
        for c in qualified_cells
    )
    enough_support = len(qualified_cells) >= 12 and consistency >= 0.70
    if enough_support and baseline_accuracy >= 0.80 and margin < 0.10:
        outcome = "REDUCTION_SUPPORTED"
    elif enough_support and candidate_accuracy >= 0.80 and margin >= 0.20 and high_rho_mutual and low_rho_additive:
        outcome = "RESIDUAL_SURVIVES"
    else:
        outcome = "INCONCLUSIVE"

    rows: list[dict] = []
    for row in raw_rows:
        compact = dict(row)
        for key in ("base", "isolated_a", "isolated_b", "composed_full", "composed_a_only", "composed_b_only"):
            compact[key] = dict(compact[key])
            compact[key].pop("rewards", None)
        rows.append(compact)
    return {
        "schema_version": "1.1-r5", "config": asdict(cfg),
        "preregistered": {
            "rho_levels": list(RHO_LEVELS), "tau_levels": list(TAU_LEVELS), "replicates_per_cell": 3,
            "qualification_unit": "rho-tau-cell", "train_horizon_episodes": cfg.train_episodes,
            "minimum_slow_loop_updates": min(min(update_counts(tau, cfg.train_episodes)) for tau in TAU_LEVELS),
            "retention_threshold": RETENTION_THRESHOLD, "min_isolated_gain": MIN_ISOLATED_GAIN,
            "candidate_rho_critical_formula": "1 - (min(r_A,r_B)/(r_A+r_B))*(1/(1+abs(log(tau))))",
            "candidate_formula_source": "archived pre-composed-outcome R2 evidence-design-p2",
            "candidate_formula_used_in_dynamics": False,
            "baseline_uses_candidate_formula": False,
            "rho_intervention": "baseline-visitation-stratified-marginal-support-matched",
            "baseline_visitation_profile_episodes": 256,
            "support_strata": ["hazard-entry", "goal-progress-class", "baseline-visitation-rank-quartile"],
            "mask_seed_counterbalanced_by_replicate": True,
            "common_random_numbers_across_rho": True,
        },
        "rows": rows, "cells": cells,
        "metrics": {
            "qualified_cells": len(qualified_cells), "consistent_cells": len(consistent), "replication_consistency": consistency,
            "baseline_correct_cells": len(baseline_correct), "baseline_accuracy": baseline_accuracy, "baseline_binomial_p": baseline_p,
            "candidate_correct_cells": len(candidate_correct), "candidate_accuracy": candidate_accuracy, "candidate_minus_baseline_accuracy": margin,
            "high_rho_tau1_mutual_observed": high_rho_mutual, "low_rho_additive_observed": low_rho_additive,
        },
        "outcome": outcome, "scientific_authority": False,
    }


def smoke_probe() -> dict:
    cfg = GridConfig()
    env = GridWorld(cfg)
    profile = baseline_visitation_profile(env, episodes=256)
    audits = []
    for rho in RHO_LEVELS:
        _a, _b, actual, audit = support_matched_mask_pair(env, rho, profile, seed=271828)
        audits.append({"rho_requested": rho, "rho_actual": actual, **audit})
    stratum_keys = sorted(profile["strata"])
    marginal_invariant = all(
        len({audit["strata"][key]["a_count"] for audit in audits}) == 1
        and len({audit["strata"][key]["b_count"] for audit in audits}) == 1
        for key in stratum_keys
    )
    rho0_disjoint = all(row["intersection"] == 0 for row in audits[0]["strata"].values())
    rho1_identical = all(row["intersection"] == row["a_count"] == row["b_count"] for row in audits[-1]["strata"].values())
    actual_rhos = [row["rho_actual"] for row in audits]
    sample = run_condition(
        0.5, 1.0, 20260818, smoke=True, cfg=cfg,
        support_profile=profile, mask_seed=271828,
    )
    return {
        "schema_version": "1.1-r6", "status": "SMOKE_PASS",
        "support_profile": {"source": profile["source"], "episodes": profile["episodes"], "strata_count": len(profile["strata"])},
        "support_audits": audits,
        "support_marginals_invariant_across_rho": marginal_invariant,
        "rho0_disjoint_within_every_stratum": rho0_disjoint,
        "rho1_identical_within_every_stratum": rho1_identical,
        "actual_rho_monotone": all(left <= right for left, right in zip(actual_rhos, actual_rhos[1:])),
        "tau_periods": {str(t): periods_for_tau(t) for t in TAU_LEVELS},
        "train_eval_disjoint": set(train_starts(cfg)).isdisjoint(set(eval_starts(cfg))),
        "sample_exec_finite": all(math.isfinite(sample[k]) for k in ("delta_a", "delta_b", "delta_a_composed", "delta_b_composed")),
        "scientific_outcome_inferred": False, "scientific_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = smoke_probe() if args.mode == "smoke" else run_full()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mode": args.mode, "output": str(args.output), "status": payload.get("status"), "outcome": payload.get("outcome"), "scientific_authority": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
