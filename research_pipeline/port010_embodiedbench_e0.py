from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "port010-embodiedbench-e0-outcome-blind-v1.1"

DATASETS = {
    "EB-Habitat": {
        "repo": "EmbodiedBench/EB-Habitat_trajectory_dataset",
        "revision": "d391eba8684b0de0c4f37a223e69237c91444209",
        "filename": "eb-habitat_dataset_multi_step.json",
        "bytes": 64296884,
        "sha256": "2cb8965964868c58b3f29fddd91a7fc92919ca9af71ea12ea4e3de702f277c80",
        "role": "DISCOVERY_STAGE_TRACE",
    },
    "EB-Manipulation": {
        "repo": "EmbodiedBench/EB-Man_trajectory_dataset",
        "revision": "0d0ecef2891dc06dc4422734cd98e40057438ac7",
        "filename": "eb-man_dataset_multi_step.json",
        "bytes": 17808872,
        "sha256": "7af29d9e82fda46cf125bdae3a689a88de30ed5fb909823905786a78f48389cb",
        "role": "DISCOVERY_STAGE_TRACE",
    },
    "EB-Navigation": {
        "repo": "EmbodiedBench/EB-Nav_trajectory_dataset",
        "revision": "c8e0ed66aa62432267ba19f59d87fe9724c18f45",
        "filename": "eb-nav_dataset_multi_step.json",
        "bytes": 61267651,
        "sha256": "c620e62e13e709592c5c5b57d8d38aeea02e7b89d39080033540e4cc46d29014",
        "role": "HELDOUT_FINAL_OUTCOME",
    },
    "EB-ALFRED": {
        "repo": "EmbodiedBench/EB-Alfred_trajectory_dataset",
        "revision": "720b5f5683b9ecbb9418f8c5998d686cde3a1397",
        "filename": "eb-alfred_dataset_multi_step.json",
        "bytes": 77556504,
        "sha256": "5a618d9332a08f055ba79644bd464368744a657555394b3cb59471b6af32a44c",
        "role": "HELDOUT_FINAL_OUTCOME",
    },
}

ALLOWED_SOURCE_FIELDS = ("model_name", "eval_set", "episode_id", "instruction")
FORBIDDEN_OUTCOME_KEYS = {
    "success",
    "trajectory",
    "action_success",
    "env_feedback",
    "reasoning_and_reflection",
    "visual_description",
    "language_plan",
    "executable_plan",
    "input",
    "img_path",
    "input_image_path",
}

TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)?")

# The lexicons below are fixed before any EmbodiedBench outcome access.  They are
# deliberately small and interpretable; v1 is rejected rather than retuned from
# benchmark outcomes if it fails the outcome-blind construct-validity gates.
SPATIAL_TERMS = (
    "left", "right", "above", "below", "under", "over", "inside", "outside",
    "behind", "beside", "between", "near", "around", "across", "opposite",
    "next to", "in front of", "on top of", "to the left of", "to the right of",
)
ORDERING_TERMS = (
    "then", "after", "before", "while", "until", "first", "second", "third",
    "next", "finally", "subsequently", "followed by", "prior to",
)
QUANTIFIER_TERMS = (
    "all", "every", "each", "both", "different", "exactly",
    "at least", "at most", "once", "twice", "one", "two", "three", "four",
)
REFERENCE_TERMS = (
    "it", "them", "this", "that", "these", "those", "there", "former", "latter",
    "same", "another", "other one", "the other",
)
NEGATION_TERMS = (
    "not", "never", "without", "except", "avoid", "do not", "don't", "cannot",
    "must not", "other than",
)
ATTRIBUTE_TERMS = (
    "red", "blue", "green", "yellow", "purple", "black", "white",
    "brown", "gray", "grey", "pink", "small", "large", "big", "tall", "short",
)
COORDINATION_TERMS = ("and", "or", "but", "while", "then")


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _tokens(text: str) -> list[str]:
    return [m.group(0).lower().replace("’", "'") for m in TOKEN_RE.finditer(text or "")]


def _count_phrase(text: str, phrase: str) -> int:
    norm = " ".join(_tokens(text))
    p = " ".join(_tokens(phrase))
    if not p:
        return 0
    return len(re.findall(r"(?<![a-z0-9])" + re.escape(p) + r"(?![a-z0-9])", norm))


def _count_terms(text: str, terms: Iterable[str]) -> int:
    # Longest-first alternation counts one marker per text span. This prevents
    # nested phrases such as "to the left of" from also counting "left" and
    # prevents "do not" from also counting its embedded "not".
    norm = " ".join(_tokens(text))
    phrases = sorted({" ".join(_tokens(term)) for term in terms if _tokens(term)}, key=lambda p: (-len(p.split()), -len(p), p))
    if not phrases:
        return 0
    pattern = r"(?<![a-z0-9])(?:" + "|".join(re.escape(p) for p in phrases) + r")(?![a-z0-9])"
    return sum(1 for _ in re.finditer(pattern, norm))


ENTITY_STOPWORDS = frozenset(
    "a an the to of on in at from with into inside for and or but is are be been being this that these those it them its their "
    "your my our one two three four left right side bottom top front back there here".split()
)
ENTITY_ACTIONS = frozenset(
    "change replace add delete remove move put place make turn transform modify set insert attach detach swap convert alter find bring "
    "take pick open close navigate go transfer give get leave need want".split()
)
REFERENCE_PRONOUNS = frozenset("it them this that these those same another former latter".split())
SEQUENTIAL_SPLIT_RE = re.compile(
    r"[\r\n]+|(?<=[.!?;])\s+|\b(?:and\s+then|after\s+that|then|subsequently|finally)\b[,;:]?\s*",
    re.IGNORECASE,
)


def _entity_normalize(token: str) -> str:
    value = token.lower().replace("’", "'").strip("'_- ")
    if len(value) > 4 and value.endswith("ies"):
        return value[:-3] + "y"
    if len(value) > 3 and value.endswith("s") and not value.endswith("ss"):
        return value[:-1]
    return value


def _non_entity_lexicon() -> frozenset[str]:
    terms = set(ENTITY_STOPWORDS) | set(ENTITY_ACTIONS)
    for lexicon in (SPATIAL_TERMS, ORDERING_TERMS, QUANTIFIER_TERMS, NEGATION_TERMS, ATTRIBUTE_TERMS, COORDINATION_TERMS):
        for phrase in lexicon:
            terms.update(_entity_normalize(tok) for tok in _tokens(phrase))
    return frozenset(terms)


NON_ENTITY_LEXICON = _non_entity_lexicon()


def constraint_clauses(text: str) -> list[str]:
    return [part.strip(" ,") for part in SEQUENTIAL_SPLIT_RE.split(text or "") if part and part.strip(" ,")]


def _entity_tokens(text: str) -> set[str]:
    values = {_entity_normalize(tok) for tok in _tokens(text)}
    return {tok for tok in values if len(tok) > 2 and tok not in NON_ENTITY_LEXICON}


def constraint_graph_features(text: str) -> dict[str, int | float]:
    clauses = constraint_clauses(text)
    if not clauses:
        clauses = [text or ""]
    entities = [_entity_tokens(clause) for clause in clauses]
    token_sets = [set(_entity_normalize(tok) for tok in _tokens(clause)) for clause in clauses]
    all_edges: list[tuple[int, int]] = []
    adjacent_edges = 0
    adjacent_overlap_tokens = 0
    longest_run = 0
    current_run = 0
    for j in range(len(clauses)):
        for i in range(j):
            overlap = entities[i] & entities[j]
            has_reference = bool(token_sets[j] & REFERENCE_PRONOUNS)
            if overlap or (has_reference and i == j - 1):
                all_edges.append((i, j))
        if j == 0:
            continue
        overlap = entities[j - 1] & entities[j]
        has_reference = bool(token_sets[j] & REFERENCE_PRONOUNS)
        if overlap or has_reference:
            adjacent_edges += 1
            adjacent_overlap_tokens += len(overlap)
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 0
    depth = 1 + longest_run if clauses else 0
    return {
        "constraint_clause_count_v2": len(clauses),
        "cross_clause_dependency_edges_v2": len(all_edges),
        "adjacent_dependency_edges_v2": adjacent_edges,
        "adjacent_entity_overlap_tokens_v2": adjacent_overlap_tokens,
        "text_dependency_depth_v2": depth,
        "has_text_dependency_v2": int(adjacent_edges > 0),
    }


def binding_features(text: str) -> dict[str, float | int]:
    toks = _tokens(text)
    spatial = _count_terms(text, SPATIAL_TERMS)
    ordering = _count_terms(text, ORDERING_TERMS)
    quantifier = _count_terms(text, QUANTIFIER_TERMS)
    reference = _count_terms(text, REFERENCE_TERMS)
    negation = _count_terms(text, NEGATION_TERMS)
    attribute = _count_terms(text, ATTRIBUTE_TERMS)
    coordination = _count_terms(text, COORDINATION_TERMS)

    # v1 is retained only as an audited diagnostic because outcome-blind
    # ComplexBench calibration showed rho(v1, token_count)=0.819.  v1.1 uses
    # the six channel densities as the primary predictor vector and keeps raw
    # token_count as a separate nuisance covariate.  No channel weights are fit.
    binding_load_v1 = spatial + ordering + quantifier + reference + negation + attribute
    binding_load_core = spatial + ordering + quantifier + reference + negation
    denom = max(1, len(toks))
    per100 = lambda value: 100.0 * float(value) / denom
    graph = constraint_graph_features(text)
    return {
        "char_count": len(text or ""),
        "token_count": len(toks),
        "spatial_relation_count": spatial,
        "ordering_dependency_count": ordering,
        "quantifier_constraint_count": quantifier,
        "referential_dependency_count": reference,
        "negation_exclusion_count": negation,
        "attribute_binding_count": attribute,
        "coordination_count": coordination,
        "binding_load_v1": binding_load_v1,
        "binding_load_core": binding_load_core,
        "spatial_relation_density_per_100": per100(spatial),
        "ordering_dependency_density_per_100": per100(ordering),
        "quantifier_constraint_density_per_100": per100(quantifier),
        "referential_dependency_density_per_100": per100(reference),
        "negation_exclusion_density_per_100": per100(negation),
        "attribute_binding_density_per_100": per100(attribute),
        "binding_density_v1_1": per100(binding_load_v1),
        **graph,
    }


def project_record(environment: str, row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("trajectory row must be an object")
    missing = [key for key in ALLOWED_SOURCE_FIELDS if key not in row]
    if missing:
        raise ValueError(f"trajectory row missing outcome-blind fields:{','.join(missing)}")
    instruction = str(row.get("instruction") or "").strip()
    if not instruction:
        raise ValueError("trajectory row has empty instruction")
    projected = {
        "environment": environment,
        "model_name": str(row.get("model_name") or "").strip(),
        "eval_set": str(row.get("eval_set") or "").strip(),
        "episode_id": str(row.get("episode_id") or "").strip(),
        "instruction": instruction,
        "instruction_sha256": hashlib.sha256(instruction.encode("utf-8")).hexdigest(),
        "features": binding_features(instruction),
    }
    if not projected["model_name"] or not projected["eval_set"] or not projected["episode_id"]:
        raise ValueError("trajectory row has empty model_name/eval_set/episode_id")
    return projected


def project_raw_dataset(environment: str, raw_path: Path) -> dict[str, Any]:
    if environment not in DATASETS:
        raise ValueError(f"unknown environment:{environment}")
    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("trajectory dataset must be a JSON list")
    rows = [project_record(environment, row) for row in payload]
    out = {
        "schema_version": SCHEMA_VERSION,
        "environment": environment,
        "source": DATASETS[environment],
        "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "records": rows,
        "record_count": len(rows),
        "outcome_fields_projected": False,
        "scientific_authority": False,
        "execution_authority": False,
        "outcomes_read_by_researcher": False,
    }
    out["projection_sha256"] = _canonical_sha({k: v for k, v in out.items() if k != "projection_sha256"})
    validate_projection(out)
    return out


def validate_projection(payload: Any) -> None:
    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if str(key).lower() in FORBIDDEN_OUTCOME_KEYS:
                    raise ValueError(f"forbidden outcome-bearing key leaked into E0 projection:{key}")
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(payload)


def _rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = avg
        i = j
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    rx, ry = _rank(xs), _rank(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((x - mx) * (y - my) for x, y in zip(rx, ry))
    dx = math.sqrt(sum((x - mx) ** 2 for x in rx))
    dy = math.sqrt(sum((y - my) ** 2 for y in ry))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def partial_spearman(xs: list[float], ys: list[float], zs: list[float]) -> float | None:
    rxy, rxz, ryz = spearman(xs, ys), spearman(xs, zs), spearman(ys, zs)
    if rxy is None or rxz is None or ryz is None:
        return None
    denom = math.sqrt(max(0.0, (1.0 - rxz * rxz) * (1.0 - ryz * ryz)))
    if denom == 0:
        return None
    return (rxy - rxz * ryz) / denom


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def summarize_projection(projections: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [row for p in projections for row in p.get("records") or []]
    # Construct validation is task-level, not rollout-level.  A task evaluated by
    # more models must not receive more weight.  Keep one canonical metadata row
    # per environment/eval_set/episode/instruction; model overlap is audited
    # separately for future outcome models.
    unique: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    by_env_models: dict[str, set[str]] = defaultdict(set)
    by_model_env_sets: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    same_instruction_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    same_episode_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    normalized_instruction_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        env, ev = row["environment"], row["eval_set"]
        key = (env, ev, row["episode_id"], row["instruction_sha256"])
        unique.setdefault(key, row)
        by_env_models[env].add(row["model_name"])
        by_model_env_sets[(row["model_name"], env)][ev].add(row["episode_id"])
        same_instruction_sets[(env, row["instruction_sha256"])].add(ev)
        same_episode_sets[(env, row["episode_id"])].add(ev)
        normalized = " ".join(_tokens(row["instruction"]))
        normalized_sha = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        normalized_instruction_sets[(env, normalized_sha)].add(ev)

    tasks = list(unique.values())
    by_env_set: dict[str, Counter[str]] = defaultdict(Counter)
    per_env_feature: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    per_env_set_feature: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    feature_keys = (
        "binding_load_v1",
        "binding_density_v1_1",
        "token_count",
        "adjacent_dependency_edges_v2",
        "text_dependency_depth_v2",
        "has_text_dependency_v2",
    )
    for row in tasks:
        env, ev = row["environment"], row["eval_set"]
        by_env_set[env][ev] += 1
        for key in feature_keys:
            value = float(row["features"][key])
            per_env_feature[env][key].append(value)
            per_env_set_feature[env][ev][key].append(value)

    env_rows: list[dict[str, Any]] = []
    graph_edge_direction_envs = 0
    graph_depth_direction_envs = 0
    joint_graph_direction_envs = 0
    dependency_rate_direction_envs = 0
    graph_length_ok = True
    for env in sorted(by_env_set):
        sets = per_env_set_feature[env]
        graph_token_rho = spearman(per_env_feature[env]["adjacent_dependency_edges_v2"], per_env_feature[env]["token_count"])
        if graph_token_rho is not None and abs(graph_token_rho) >= 0.50:
            graph_length_ok = False
        c_edges = _median(sets.get("complex_instruction", {}).get("adjacent_dependency_edges_v2", []))
        b_edges = _median(sets.get("base", {}).get("adjacent_dependency_edges_v2", []))
        c_depth = _median(sets.get("complex_instruction", {}).get("text_dependency_depth_v2", []))
        b_depth = _median(sets.get("base", {}).get("text_dependency_depth_v2", []))
        c_dep_values = sets.get("complex_instruction", {}).get("has_text_dependency_v2", [])
        b_dep_values = sets.get("base", {}).get("has_text_dependency_v2", [])
        c_dep_rate = statistics.fmean(c_dep_values) if c_dep_values else None
        b_dep_rate = statistics.fmean(b_dep_values) if b_dep_values else None
        edge_up = c_edges is not None and b_edges is not None and c_edges > b_edges
        depth_up = c_depth is not None and b_depth is not None and c_depth > b_depth
        if edge_up:
            graph_edge_direction_envs += 1
        if depth_up:
            graph_depth_direction_envs += 1
        if edge_up and depth_up:
            joint_graph_direction_envs += 1
        if c_dep_rate is not None and b_dep_rate is not None and c_dep_rate > b_dep_rate:
            dependency_rate_direction_envs += 1
        env_rows.append({
            "environment": env,
            "unique_tasks": sum(by_env_set[env].values()),
            "models": len(by_env_models[env]),
            "eval_set_unique_task_counts": dict(sorted(by_env_set[env].items())),
            "graph_edge_token_spearman": graph_token_rho,
            "complex_adjacent_edge_median": c_edges,
            "base_adjacent_edge_median": b_edges,
            "complex_minus_base_edge_median": None if c_edges is None or b_edges is None else c_edges - b_edges,
            "complex_depth_median": c_depth,
            "base_depth_median": b_depth,
            "complex_minus_base_depth_median": None if c_depth is None or b_depth is None else c_depth - b_depth,
            "complex_dependency_rate": c_dep_rate,
            "base_dependency_rate": b_dep_rate,
            "complex_minus_base_dependency_rate": None if c_dep_rate is None or b_dep_rate is None else c_dep_rate - b_dep_rate,
            "raw_v1_token_spearman": spearman(per_env_feature[env]["binding_load_v1"], per_env_feature[env]["token_count"]),
            "binding_density_token_spearman": spearman(per_env_feature[env]["binding_density_v1_1"], per_env_feature[env]["token_count"]),
        })

    pooled_graph_token_rho = spearman(
        [float(row["features"]["adjacent_dependency_edges_v2"]) for row in tasks],
        [float(row["features"]["token_count"]) for row in tasks],
    )
    pooled_density_token_rho = spearman(
        [float(row["features"]["binding_density_v1_1"]) for row in tasks],
        [float(row["features"]["token_count"]) for row in tasks],
    )
    pooled_raw_v1_rho = spearman(
        [float(row["features"]["binding_load_v1"]) for row in tasks],
        [float(row["features"]["token_count"]) for row in tasks],
    )
    collision_count = sum(1 for sets in same_instruction_sets.values() if len(sets) > 1)
    normalized_collision_count = sum(1 for sets in normalized_instruction_sets.values() if len(sets) > 1)
    episode_cross_set_collision_count = sum(1 for sets in same_episode_sets.values() if len(sets) > 1)
    eligible_strata = []
    for (model, env), sets in sorted(by_model_env_sets.items()):
        base_n = len(sets.get("base", set()))
        complex_n = len(sets.get("complex_instruction", set()))
        if base_n >= 10 and complex_n >= 10:
            eligible_strata.append({"model_name": model, "environment": env, "base_episode_ids": base_n, "complex_episode_ids": complex_n})

    graph_direction_pass = joint_graph_direction_envs >= 3
    length_pass = (pooled_graph_token_rho is None or abs(pooled_graph_token_rho) < 0.50) and graph_length_ok
    metadata_independence_pass = collision_count == 0 and normalized_collision_count == 0 and episode_cross_set_collision_count == 0
    return {
        "rollout_records": len(rows),
        "unique_tasks": len(tasks),
        "environments": len(by_env_set),
        "environment_summary": env_rows,
        "cross_eval_set_instruction_collisions": collision_count,
        "cross_eval_set_normalized_instruction_collisions": normalized_collision_count,
        "cross_eval_set_episode_id_collisions": episode_cross_set_collision_count,
        "eligible_model_environment_strata": eligible_strata,
        "eligible_model_environment_strata_count": len(eligible_strata),
        "pooled_graph_edge_token_spearman": pooled_graph_token_rho,
        "pooled_binding_density_token_spearman": pooled_density_token_rho,
        "pooled_raw_v1_token_spearman": pooled_raw_v1_rho,
        "outcome_blind_construct_gate": {
            "complex_edge_median_gt_base_environments": graph_edge_direction_envs,
            "complex_depth_median_gt_base_environments": graph_depth_direction_envs,
            "complex_edge_and_depth_jointly_gt_base_environments": joint_graph_direction_envs,
            "complex_dependency_rate_gt_base_environments_supporting": dependency_rate_direction_envs,
            "required_joint_environments": 3,
            "directional_construct_support": graph_direction_pass,
            "pooled_abs_graph_edge_token_spearman_lt": 0.50,
            "per_environment_abs_graph_edge_token_spearman_lt": 0.50,
            "length_noncollapse": length_pass,
            "cross_eval_set_metadata_independence": metadata_independence_pass,
            "future_outcome_overlap_present": len(eligible_strata) >= 2,
            "pass": graph_direction_pass and length_pass and metadata_independence_pass and len(eligible_strata) >= 2,
        },
    }


def complexbench_calibration(records: list[dict[str, Any]]) -> dict[str, Any]:
    # ComplexBench is a DEVELOPMENT calibration set only. We already observed
    # its full non-outcome structure while diagnosing v1, so it is never called
    # an independent holdout. Independent construct confirmation is reserved for
    # ComplexBench-Edit two-chain vs three-chain instructions.
    raw_v1: list[float] = []
    density_v11: list[float] = []
    token: list[float] = []
    dependency_edges: list[float] = []
    dependent_points: list[float] = []
    atomic_points: list[float] = []
    initial_target: list[float] = []
    composition_types: list[float] = []
    channel_density: dict[str, list[float]] = defaultdict(list)
    channel_keys = (
        "spatial_relation_density_per_100",
        "ordering_dependency_density_per_100",
        "quantifier_constraint_density_per_100",
        "referential_dependency_density_per_100",
        "negation_exclusion_density_per_100",
        "attribute_binding_density_per_100",
    )
    for row in records:
        text = str(row.get("instruction_en") or "").strip()
        if not text:
            continue
        dims = row.get("constraint_dimensions") or []
        comps = row.get("composition_types") or []
        qs = [q for q in (row.get("scoring_questions") or []) if isinstance(q, dict)]
        feat = binding_features(text)
        raw_v1.append(float(feat["binding_load_v1"]))
        density_v11.append(float(feat["binding_density_v1_1"]))
        token.append(float(feat["token_count"]))
        dependency_edges.append(float(sum(len(q.get("dep") or []) for q in qs)))
        dependent_points.append(float(sum(1 for q in qs if q.get("dep") or [])))
        atomic_points.append(float(len(qs)))
        initial_target.append(float(len(set(map(str, dims))) + len(set(map(str, comps)))))
        composition_types.append(float(len(set(map(str, comps)))))
        for key in channel_keys:
            channel_density[key].append(float(feat[key]))

    initial_rho = spearman(raw_v1, initial_target)
    raw_v1_token_rho = spearman(raw_v1, token)
    density_token_rho = spearman(density_v11, token)
    density_dep_partial = partial_spearman(density_v11, dependency_edges, token)
    density_dpts_partial = partial_spearman(density_v11, dependent_points, token)
    per_channel = {
        key: {
            "rho_dependency_edges": spearman(values, dependency_edges),
            "partial_rho_dependency_edges_given_token": partial_spearman(values, dependency_edges, token),
            "rho_token_count": spearman(values, token),
        }
        for key, values in channel_density.items()
    }
    ordering_partial = (per_channel.get("ordering_dependency_density_per_100") or {}).get(
        "partial_rho_dependency_edges_given_token"
    )
    gate = {
        "raw_v1_retired_for_length_collapse": raw_v1_token_rho is not None and abs(raw_v1_token_rho) >= 0.80,
        "v1_1_density_abs_token_rho_lt_0_30": density_token_rho is None or abs(density_token_rho) < 0.30,
        "v1_1_partial_dependency_edges_ge_0_25": density_dep_partial is not None and density_dep_partial >= 0.25,
        "v1_1_partial_dependent_points_ge_0_25": density_dpts_partial is not None and density_dpts_partial >= 0.25,
        "ordering_channel_partial_dependency_ge_0_25": ordering_partial is not None and ordering_partial >= 0.25,
    }
    gate["development_calibration_pass"] = all(gate.values())
    return {
        "role": "DEVELOPMENT_CALIBRATION_NOT_HOLDOUT",
        "records": len(raw_v1),
        "audit_trail": {
            "initial_external_target": "unique constraint_dimensions + unique composition_types",
            "initial_raw_v1_spearman": initial_rho,
            "initial_gate_failed": initial_rho is None or initial_rho < 0.25,
            "construct_correction": (
                "binding/dependency was the preregistered latent object; dependency_edges/dependent_points are retained as development "
                "targets after the initial category-count proxy failed, before any EmbodiedBench outcome access"
            ),
        },
        "diagnostics": {
            "raw_v1_token_spearman": raw_v1_token_rho,
            "raw_v1_dependency_edges_spearman": spearman(raw_v1, dependency_edges),
            "raw_v1_atomic_points_spearman": spearman(raw_v1, atomic_points),
            "raw_v1_composition_types_spearman": spearman(raw_v1, composition_types),
            "v1_1_binding_density_token_spearman": density_token_rho,
            "v1_1_binding_density_dependency_edges_spearman": spearman(density_v11, dependency_edges),
            "v1_1_partial_dependency_edges_given_token": density_dep_partial,
            "v1_1_partial_dependent_points_given_token": density_dpts_partial,
            "v1_1_partial_composition_types_given_token": partial_spearman(density_v11, composition_types, token),
            "per_channel_density": per_channel,
        },
        "gate": gate,
    }


def complexbench_edit_chain_check(two_chain_texts: list[str], three_chain_texts: list[str]) -> dict[str, Any]:
    # Historical v1.1 scalar-density check. Keep it permanently in the audit
    # trail because it failed on the real ComplexBench-Edit release and
    # motivated the outcome-blind ConstraintGraph-v2 refinement.
    two = [float(binding_features(text)["binding_density_v1_1"]) for text in two_chain_texts if str(text).strip()]
    three = [float(binding_features(text)["binding_density_v1_1"]) for text in three_chain_texts if str(text).strip()]
    if not two or not three:
        raise ValueError("ComplexBench-Edit chain check requires both two-chain and three-chain instructions")
    two_med, three_med = statistics.median(two), statistics.median(three)
    return {
        "role": "HISTORICAL_V1_1_CHAIN_CHECK_NOT_HOLDOUT",
        "two_chain_records": len(two),
        "three_chain_records": len(three),
        "two_chain_binding_density_median": two_med,
        "three_chain_binding_density_median": three_med,
        "three_minus_two_median": three_med - two_med,
        "gate": {
            "three_chain_median_gt_two_chain": three_med > two_med,
        },
    }


def complexbench_edit_graph_calibration(two_chain_texts: list[str], three_chain_texts: list[str]) -> dict[str, Any]:
    # ComplexBench-Edit is DEVELOPMENT data for v2: it was inspected while v2
    # was designed, therefore none of the numbers below are an independent
    # validation.  The independent v2 check is EmbodiedBench metadata only.
    two = [constraint_graph_features(text) for text in two_chain_texts if str(text).strip()]
    three = [constraint_graph_features(text) for text in three_chain_texts if str(text).strip()]
    if not two or not three:
        raise ValueError("ConstraintGraph-v2 calibration requires two-chain and three-chain instructions")

    def med(rows: list[dict[str, int | float]], key: str) -> float:
        return float(statistics.median(float(row[key]) for row in rows))

    def rate(rows: list[dict[str, int | float]], predicate) -> float:
        return sum(1 for row in rows if predicate(row)) / len(rows)

    two_edge_med = med(two, "adjacent_dependency_edges_v2")
    three_edge_med = med(three, "adjacent_dependency_edges_v2")
    two_depth_med = med(two, "text_dependency_depth_v2")
    three_depth_med = med(three, "text_dependency_depth_v2")
    two_depth3 = rate(two, lambda row: int(row["text_dependency_depth_v2"]) >= 3)
    three_depth3 = rate(three, lambda row: int(row["text_dependency_depth_v2"]) >= 3)
    accuracy = (
        sum(1 for row in two if int(row["text_dependency_depth_v2"]) < 3)
        + sum(1 for row in three if int(row["text_dependency_depth_v2"]) >= 3)
    ) / (len(two) + len(three))
    return {
        "role": "DEVELOPMENT_CHAIN_RECOVERY_NOT_HOLDOUT",
        "two_chain_records": len(two),
        "three_chain_records": len(three),
        "two_chain_adjacent_edge_median": two_edge_med,
        "three_chain_adjacent_edge_median": three_edge_med,
        "two_chain_depth_median": two_depth_med,
        "three_chain_depth_median": three_depth_med,
        "two_chain_depth_ge_3_rate": two_depth3,
        "three_chain_depth_ge_3_rate": three_depth3,
        "depth_ge_3_classification_accuracy": accuracy,
        "development_gate": {
            "three_edge_median_gt_two": three_edge_med > two_edge_med,
            "three_depth_median_gt_two": three_depth_med > two_depth_med,
            "three_depth3_rate_gt_two": three_depth3 > two_depth3,
            "depth_ge_3_accuracy_ge_0_75": accuracy >= 0.75,
        },
    }


def _raw_material_path(raw_root: Path, environment: str) -> Path:
    source = DATASETS[environment]
    repo_name = str(source["repo"]).split("/")[-1]
    return raw_root / f"{repo_name}--{source['revision']}--{source['filename']}"


def compile_e0(
    *,
    raw_root: Path,
    complexbench_json: Path,
    complexbench_edit_root: Path,
    projection_root: Path,
) -> dict[str, Any]:
    raw_root = raw_root.resolve()
    projection_root = projection_root.resolve()
    projection_root.mkdir(parents=True, exist_ok=True)

    projections: list[dict[str, Any]] = []
    source_receipts: list[dict[str, Any]] = []
    for environment in DATASETS:
        raw_path = _raw_material_path(raw_root, environment)
        if not raw_path.is_file():
            raise ValueError(f"missing pinned EmbodiedBench raw material:{environment}:{raw_path}")
        if Path(str(raw_path) + ".aria2").exists():
            raise ValueError(f"incomplete aria2 material cannot enter E0:{environment}")
        expected_bytes = int(DATASETS[environment]["bytes"])
        actual_bytes = raw_path.stat().st_size
        if actual_bytes != expected_bytes:
            raise ValueError(f"pinned EmbodiedBench size mismatch:{environment}:{actual_bytes}!={expected_bytes}")
        actual_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        expected_sha = str(DATASETS[environment]["sha256"])
        if actual_sha != expected_sha:
            raise ValueError(f"pinned EmbodiedBench sha256 mismatch:{environment}:{actual_sha}!={expected_sha}")
        projected = project_raw_dataset(environment, raw_path)
        out_path = projection_root / f"{environment.lower()}-metadata-projection.json"
        out_path.write_text(json.dumps(projected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        projections.append(projected)
        source_receipts.append({
            "environment": environment,
            "repo": DATASETS[environment]["repo"],
            "revision": DATASETS[environment]["revision"],
            "filename": DATASETS[environment]["filename"],
            "raw_sha256": projected["raw_sha256"],
            "record_count": projected["record_count"],
            "projection_sha256": projected["projection_sha256"],
            "projection_path": str(out_path),
            "transport_is_authority": False,
        })

    complexbench_rows = json.loads(complexbench_json.read_text(encoding="utf-8"))
    if not isinstance(complexbench_rows, list):
        raise ValueError("ComplexBench calibration source must be a JSON list")
    cb = complexbench_calibration(complexbench_rows)

    cbe_texts: dict[str, list[str]] = {}
    cbe_sources: dict[str, dict[str, Any]] = {}
    for kind in ("two-chain", "three-chain"):
        path = complexbench_edit_root / kind / "final_update_v2.json"
        data = path.read_bytes()
        payload = json.loads(data)
        values = list(payload.values()) if isinstance(payload, dict) else payload
        texts = [
            str(row.get("new_ins") or "").strip()
            for row in values
            if isinstance(row, dict) and str(row.get("new_ins") or "").strip()
        ]
        if not texts:
            raise ValueError(f"ComplexBench-Edit has no usable {kind} instructions")
        cbe_texts[kind] = texts
        cbe_sources[kind] = {"path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "records": len(texts)}

    cbe_v11 = complexbench_edit_chain_check(cbe_texts["two-chain"], cbe_texts["three-chain"])
    cbe_v2 = complexbench_edit_graph_calibration(cbe_texts["two-chain"], cbe_texts["three-chain"])
    summary = summarize_projection(projections)
    contract = preregistration_contract()
    construct_pass = bool((cb.get("gate") or {}).get("development_calibration_pass")) and all(
        bool(value) for value in (cbe_v2.get("development_gate") or {}).values()
    ) and bool((summary.get("outcome_blind_construct_gate") or {}).get("pass"))
    compiler_path = Path(__file__).resolve()
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": "PORT-010",
        "compiler": {
            "path": str(compiler_path),
            "sha256": hashlib.sha256(compiler_path.read_bytes()).hexdigest(),
            "constraint_graph_v2_frozen_before_embodiedbench_projection": True,
        },
        "status": "E0_CONSTRUCT_GATE_PASS_AWAITING_INDEPENDENT_REVIEW" if construct_pass else "E0_CONSTRUCT_GATE_HOLD",
        "scientific_authority": False,
        "execution_authority": False,
        "outcome_access_authorized": False,
        "provider_calls_executed_by_compiler": 0,
        "outcomes_projected": False,
        "source_receipts": source_receipts,
        "complexbench_source": {
            "path": str(complexbench_json),
            "sha256": hashlib.sha256(complexbench_json.read_bytes()).hexdigest(),
            "role": "DEVELOPMENT_CALIBRATION_NOT_HOLDOUT",
        },
        "complexbench_calibration": cb,
        "complexbench_edit_sources": cbe_sources,
        "historical_v1_1_chain_failure": cbe_v11,
        "constraint_graph_v2_development": cbe_v2,
        "embodiedbench_metadata_summary": summary,
        "preregistration_contract": contract,
        "construct_gate_pass": construct_pass,
        "next_gate": (
            "independent Kimi/DeepSeek review of this exact content-addressed E0 receipt before any success/action_success access"
            if construct_pass
            else "HOLD/STOP binding-mechanism lane; do not inspect EmbodiedBench success/action_success"
        ),
    }
    receipt["receipt_sha256"] = _canonical_sha({key: value for key, value in receipt.items() if key != "receipt_sha256"})
    return receipt


def preregistration_contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": "PORT-010",
        "status": "E0_OUTCOME_BLIND_DESIGN_ONLY",
        "scientific_authority": False,
        "execution_authority": False,
        "provider_calls_authorized": False,
        "outcome_access_authorized": False,
        "primary_scientific_object": (
            "association between preregistered instruction constraint/binding load and stage-resolved embodied-agent failure, "
            "not a causal effect of the EmbodiedBench complex_instruction label"
        ),
        "primary_predictor": (
            "ConstraintGraph-v2 adjacent_dependency_edges_v2, a deterministic cross-clause entity/reference reuse count frozen after "
            "development on ComplexBench-Edit and before any EmbodiedBench instruction or outcome inspection"
        ),
        "confirmatory_structural_predictor": "ConstraintGraph-v2 text_dependency_depth_v2; no fitted weights or outcome-derived labels",
        "secondary_lexical_predictors": (
            "BindingLoad-v1.1 six channel densities per 100 tokens are secondary diagnostics only; raw binding_load_v1 is permanently "
            "retired from primary use because outcome-blind calibration found rho(raw_v1,token_count)>=0.80"
        ),
        "nuisance_covariate": "raw token_count entered separately in all primary models",
        "official_eval_set_role": "author-defined validation/falsifier strata, not causal treatment assignment",
        "discovery_environments": ["EB-Habitat", "EB-Manipulation"],
        "heldout_environments": ["EB-Navigation", "EB-ALFRED"],
        "model_environment_inclusion_rule": (
            "include a model×environment stratum only if released metadata contain at least 10 unique episode_ids in both "
            "base and complex_instruction; rule is evaluated without outcome access"
        ),
        "e1_primary_endpoint": "released binary episode success; inaccessible during E0",
        "e1_primary_model": (
            "logistic association model: released episode success ~ adjacent_dependency_edges_v2 + token_count + eval_set + model_name + "
            "environment fixed effects; task-cluster robust uncertainty using environment×eval_set×episode_id. Discovery is restricted "
            "to EB-Habitat and EB-Manipulation; held-out environments are not opened for the discovery fit."
        ),
        "e1_primary_test": (
            "two-sided alpha=0.05 for adjacent_dependency_edges_v2 with preregistered directional expectation beta<0; report odds ratio "
            "and 95% CI. text_dependency_depth_v2 is one confirmatory structural test. The six v1.1 lexical-density channels are one "
            "secondary 6-df block test; channel-level follow-ups use Benjamini-Hochberg FDR q=0.05."
        ),
        "e2_stage_signature": {
            "scope": ["EB-Habitat", "EB-Manipulation"],
            "action_outcome": "released action_success only; no relabeling from env_feedback/reasoning text",
            "normalized_position": "0 for one-action episodes; otherwise (action_ordinal-1)/(n_actions-1)",
            "primary_interaction": (
                "released action_success ~ adjacent_dependency_edges_v2 * normalized_position + token_count + eval_set + model_name + "
                "environment; preregistered expectation is a negative dependency×position interaction"
            ),
            "signature": (
                "dependency×position interaction is negative at alpha=0.05, while the first-quartile dependency association is no more "
                "than half the magnitude of the final episode-success association; otherwise do not label the pattern stage-specific binding"
            ),
        },
        "falsifier_strata": ["long_horizon", "visual_appearance", "common_sense", "spatial_relationship", "base"],
        "construct_gates_before_outcomes": {
            "audit_initial_failures": (
                "retain both failed metrics in the receipt: raw v1 failed the original ComplexBench category-count target and collapsed "
                "to token length; v1.1 scalar density failed the real ComplexBench-Edit three-chain>two-chain direction. Neither may be erased."
            ),
            "development_only": (
                "ComplexBench and ComplexBench-Edit are development calibration data, not holdouts. ConstraintGraph-v2 must recover the "
                "CBE chain structure with three-chain median adjacent edges > two-chain, median depth > two-chain, depth>=3 rate higher, "
                "and depth>=3 classification accuracy >=0.75. These development results never count as independent support."
            ),
            "embodiedbench_independent_directional": (
                "on unique task metadata only, before success/action_success access, complex_instruction must exceed base in BOTH median "
                "adjacent_dependency_edges_v2 AND median text_dependency_depth_v2 within the same environment in at least 3 of 4 environments; "
                "has_text_dependency_v2 rate is supporting only"
            ),
            "embodiedbench_metadata_independence": (
                "zero cross-eval-set collisions by exact instruction SHA, normalized instruction SHA, and episode_id within each environment"
            ),
            "embodiedbench_graph_length_noncollapse": (
                "abs Spearman(adjacent_dependency_edges_v2,token_count)<0.50 pooled and <0.50 in every environment"
            ),
            "future_outcome_overlap": (
                "at least two model×environment strata must each contain >=10 unique released episode_ids in both base and complex_instruction"
            ),
            "metric_revision_policy": (
                "ConstraintGraph-v2 is frozen before EmbodiedBench instruction projection. If the independent metadata gate fails, HOLD/STOP "
                "the binding mechanism claim; do not revise v2 from EmbodiedBench labels or outcomes in the same confirmatory lane."
            ),
        },
        "stop_rules": [
            "ConstraintGraph-v2 fails the independent EmbodiedBench metadata construct gate",
            "cross-eval-set instruction or episode identity collisions invalidate the independent metadata contrast",
            "adjacent_dependency_edges_v2 remains strongly coupled to instruction length",
            "released metadata do not provide adequate model×environment overlap",
            "E1 association disappears after preregistered token/eval-set/model/environment adjustment",
            "challenge strata all show indistinguishable deficits, indicating generic benchmark difficulty",
            "E2 shows equally strong early action degradation, contradicting a later-stage binding signature",
            "effect is isolated to one model family or one environment without held-out replication",
        ],
        "vwe_rule": (
            "VWE remains HOLD during E0/E1/E2 and can be used only as a separately labeled preregistered local 3D external validation "
            "after the EmbodiedBench released-evidence signature survives; VWE can never rescue a failed EmbodiedBench result"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile PORT-010 EmbodiedBench E0 outcome-blind metadata and construct gate")
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--complexbench-json", type=Path, required=True)
    parser.add_argument("--complexbench-edit-root", type=Path, required=True, help="directory containing two-chain/ and three-chain/")
    parser.add_argument("--projection-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = compile_e0(
        raw_root=args.raw_root,
        complexbench_json=args.complexbench_json,
        complexbench_edit_root=args.complexbench_edit_root,
        projection_root=args.projection_root,
    )
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "construct_gate_pass": receipt["construct_gate_pass"],
        "receipt_sha256": receipt["receipt_sha256"],
        "outcomes_projected": receipt["outcomes_projected"],
        "outcome_access_authorized": receipt["outcome_access_authorized"],
        "summary": receipt["embodiedbench_metadata_summary"]["outcome_blind_construct_gate"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
