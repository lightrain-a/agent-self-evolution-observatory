from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Iterable

OBJECT_ID = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
LICENSE_RECEIPT = "USER_CONFIRMED_RESEARCH_LICENSE_ACCEPTED"
GLOBAL_SEED = "RELATIONAL-TOPOLOGY-3D-CORPUS-V1"
REGIME_SUPPORT = {"IS-SUPPORT-12": (1, 2), "IS-SUPPORT-14": (1, 2, 3, 4)}
RELATION_FAMILIES = (
    ("left", "right"),
    ("front", "behind"),
    ("above", "below"),
    ("near", "far"),
    ("facing", "not_facing"),
    ("supporting", "on"),
)
CORPUS_FIELDS = (
    "example_id", "source_scene_id", "room_type", "object_ids", "object_count",
    "relation_set", "relation_count", "relation_family_multiset",
    "direction_multiset", "exact_instruction", "clip_tokenizer",
    "clip_tokenizer_revision", "exact_clip_token_count", "tokenizer_truncated",
    "topology_statistics", "corpus_regime", "rng_seed", "generator_code_sha",
    "dataset_revision", "example_sha256",
)
CHECKPOINT_REQUIRED = (
    "run_id", "component_id", "step", "model_state_sha256",
    "optimizer_state_sha256", "scheduler_state_sha256", "rng_state_sha256",
    "sampler_state_sha256", "sampler_position", "corpus_cursor",
    "corpus_sha256", "config_sha256", "code_sha", "checkpoint_sha256",
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ) + "\n").encode()


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def derive_example_seed(
    scene_id: str,
    regime: str,
    sample_slot: int,
    frozen_global_seed: str = GLOBAL_SEED,
) -> int:
    if regime not in REGIME_SUPPORT:
        raise ValueError(f"unknown regime: {regime}")
    payload = f"{scene_id}|{regime}|{sample_slot}|{frozen_global_seed}".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def require_license(receipt: str | None) -> None:
    if receipt != LICENSE_RECEIPT:
        raise PermissionError("HOLD_USER_LICENSE_CONFIRMATION")


def _topology(edges: list[tuple[str, str]], nodes: list[str]) -> dict[str, Any]:
    graph = {node: set() for node in nodes}
    for source, target in edges:
        graph[source].add(target)
        graph[target].add(source)
    degree = {node: len(graph[node]) for node in nodes}
    seen: set[str] = set()
    components: list[list[str]] = []
    for node in nodes:
        if node in seen:
            continue
        queue = deque([node])
        seen.add(node)
        component = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for nxt in sorted(graph[current]):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        components.append(component)
    active_components = [c for c in components if any(degree[node] for node in c)]
    diameter = 0
    for component in active_components:
        for start in component:
            distances = {start: 0}
            queue = deque([start])
            while queue:
                current = queue.popleft()
                for nxt in graph[current]:
                    if nxt not in distances:
                        distances[nxt] = distances[current] + 1
                        queue.append(nxt)
            diameter = max(diameter, max(distances.values(), default=0))
    degree_sum = sum(degree.values())
    return {
        "connected_components": len(components),
        "active_components": len(active_components),
        "max_degree": max(degree.values(), default=0),
        "degree_concentration": max(degree.values(), default=0) / degree_sum if degree_sum else 0.0,
        "diameter": diameter,
        "shared_anchor_fraction": (
            sum(d * (d - 1) // 2 for d in degree.values())
            / max(1, len(edges) * (len(edges) - 1) // 2)
        ),
        "largest_component": max(map(len, components), default=0),
        "relation_graph_density": 2 * len(edges) / (len(nodes) * (len(nodes) - 1)),
    }


def _synthetic_edges(count: int, slot: int) -> list[tuple[str, str]]:
    nodes = list("ABCDEFGH")
    mode = ("DISJOINT", "CHAIN", "HUB")[slot % 3]
    if mode == "DISJOINT":
        return [(nodes[2 * i], nodes[2 * i + 1]) for i in range(count)]
    if mode == "CHAIN":
        return [(nodes[i], nodes[i + 1]) for i in range(count)]
    return [(nodes[0], nodes[i + 1]) for i in range(count)]


def build_synthetic_example(
    scene_id: str,
    regime: str,
    sample_slot: int,
    generator_code_sha: str,
) -> dict[str, Any]:
    seed = derive_example_seed(scene_id, regime, sample_slot)
    rng = random.Random(seed)
    support = REGIME_SUPPORT[regime]
    relation_count = support[sample_slot % len(support)]
    nodes = list("ABCDEFGH")
    edges = _synthetic_edges(relation_count, sample_slot)
    occurrence = sample_slot // len(support)
    offset = occurrence % len(RELATION_FAMILIES)
    relations = []
    families = []
    directions = []
    for index, (source, target) in enumerate(edges):
        forward, reverse = RELATION_FAMILIES[(offset + index) % len(RELATION_FAMILIES)]
        if rng.randint(0, 1):
            source, target, forward, reverse = target, source, reverse, forward
        family = "/".join(sorted((forward, reverse)))
        relations.append({
            "source": source, "target": target, "direction": forward,
            "reverse_direction": reverse, "family": family,
        })
        families.append(family)
        directions.extend((forward, reverse))
    body = {
        "example_id": f"SYN-{scene_id}-{regime}-{sample_slot:04d}",
        "source_scene_id": scene_id,
        "room_type": "BEDROOM",
        "object_ids": nodes,
        "object_count": len(nodes),
        "relation_set": relations,
        "relation_count": relation_count,
        "relation_family_multiset": dict(sorted(Counter(families).items())),
        "direction_multiset": dict(sorted(Counter(directions).items())),
        "exact_instruction": "SYNTHETIC_ONLY_NO_SCIENTIFIC_LANGUAGE",
        "clip_tokenizer": "openai/clip-vit-base-patch32",
        "clip_tokenizer_revision": "3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268",
        "exact_clip_token_count": None,
        "tokenizer_truncated": None,
        "topology_statistics": _topology(edges, nodes),
        "corpus_regime": regime,
        "rng_seed": seed,
        "generator_code_sha": generator_code_sha,
        "dataset_revision": "SYNTHETIC_PUBLIC_SAFE_V1",
    }
    body["example_sha256"] = sha256_value(body)
    return body


def compile_synthetic_corpus(
    scene_ids: Iterable[str],
    regime: str,
    sample_slots: int,
    generator_code_sha: str,
    traversal: str = "forward",
    workers: int = 1,
) -> tuple[list[dict[str, Any]], str]:
    scenes = list(scene_ids)
    if traversal == "reverse":
        scenes.reverse()
    elif traversal == "shuffled":
        random.Random(20260901).shuffle(scenes)
    elif traversal != "forward":
        raise ValueError(traversal)
    jobs = [(scene, slot) for scene in scenes for slot in range(sample_slots)]

    def build(job: tuple[str, int]) -> dict[str, Any]:
        return build_synthetic_example(job[0], regime, job[1], generator_code_sha)

    if workers == 1:
        rows = [build(job) for job in jobs]
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            rows = list(executor.map(build, jobs))
    rows.sort(key=lambda row: row["example_id"])
    return rows, sha256_value(rows)


def replay_matrix(
    scene_ids: Iterable[str], regime: str, sample_slots: int, generator_code_sha: str
) -> dict[str, Any]:
    variants = {
        "forward_w1": ("forward", 1),
        "reverse_w1": ("reverse", 1),
        "shuffled_w1": ("shuffled", 1),
        "forward_w4": ("forward", 4),
    }
    hashes = {
        name: compile_synthetic_corpus(
            scene_ids, regime, sample_slots, generator_code_sha, traversal, workers
        )[1]
        for name, (traversal, workers) in variants.items()
    }
    return {"hashes": hashes, "byte_identical": len(set(hashes.values())) == 1}


def validate_exact_pairing(predicted: dict[str, Any], oracle: dict[str, Any]) -> bool:
    fields = ("slot_ids", "object_ids", "object_classes", "objfeat_ids", "obj_masks")
    if not all(field in predicted and field in oracle for field in fields):
        return False
    return all(predicted[field] == oracle[field] for field in fields)


def exactly_once_key(
    component_id: str, corpus_sha256: str, config_sha256: str, seed: int
) -> str:
    return hashlib.sha256(
        f"{component_id}|{corpus_sha256}|{config_sha256}|{seed}".encode()
    ).hexdigest()


def validate_checkpoint_record(record: dict[str, Any]) -> list[str]:
    return [field for field in CHECKPOINT_REQUIRED if field not in record]


def empty_p1_schema() -> dict[str, Any]:
    return {
        "authorized": False,
        "room": "BEDROOM",
        "models": ["SGP-12+SHARED", "SGP-14+SHARED"],
        "relation_counts": [2, 3, 4],
        "topologies": ["DISJOINT", "CHAIN", "HUB", "COMPONENT_BRIDGE_OPTIONAL"],
        "observables": [
            "text_to_graph_relation_recall",
            "graph_to_scene_relation_retention",
            "end_to_end_relation_iRecall",
        ],
        "interventions": ["predicted_graph", "oracle_graph"],
        "scientific_cases": [],
        "scientific_outcomes": [],
    }


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_bytes(b"".join(canonical_bytes(row) for row in rows))
