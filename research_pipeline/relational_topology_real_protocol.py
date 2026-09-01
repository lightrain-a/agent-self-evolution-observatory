from __future__ import annotations

import hashlib
from collections import deque
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

DATASET_REVISION = "c8cf0bd282699d56a7940ac588ea5e961b1260cb"
CLIP_MODEL = "openai/clip-vit-base-patch32"
CLIP_REVISION = "3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268"
CLIP_MAX_TOKENS = 77
REAL_GLOBAL_SEED = "RELATIONAL-TOPOLOGY-3D-REAL-CORPUS-V1"
PROTOCOL_ID = "SCENENAT-V2-REFINED-FIXED-COUNT-ADAPTER-V1"
REAL_REGIME_SLOT_COUNTS = {
    "IS-SUPPORT-12": (1, 2, 1, 2),
    "IS-SUPPORT-14": (1, 2, 3, 4),
}
SHARED_SLOTS = (0, 1)
PREDICATES = (
    "above", "left of", "in front of", "closely left of",
    "closely in front of", "below", "right of", "behind",
    "closely right of", "closely behind",
)
_REVERSE = {
    "above": "below", "below": "above",
    "in front of": "behind", "behind": "in front of",
    "left of": "right of", "right of": "left of",
    "closely in front of": "closely behind",
    "closely behind": "closely in front of",
    "closely left of": "closely right of",
    "closely right of": "closely left of",
}


@dataclass(frozen=True)
class ScenePayload:
    scene_uid: str
    scene_id: str
    object_ids: tuple[str, ...]
    object_types: tuple[str, ...]
    object_class_ids: tuple[int, ...]
    object_descriptions: tuple[str, ...]
    filtered_relations: tuple[tuple[int, int, int], ...]


def derive_seed(scene_uid: str, sample_slot: int) -> int:
    payload = f"{scene_uid}|{sample_slot}|{REAL_GLOBAL_SEED}".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def reverse_rel(predicate: str) -> str:
    return _REVERSE[predicate]


def relation_family(predicate: str) -> str:
    return "/".join(sorted((predicate, reverse_rel(predicate))))


def filter_symmetric_duplicates(
    relations: Sequence[Sequence[int]],
) -> tuple[tuple[int, int, int], ...]:
    seen: set[tuple[int, int]] = set()
    result: list[tuple[int, int, int]] = []
    for raw_s, raw_p, raw_o in relations:
        s, p, o = int(raw_s), int(raw_p), int(raw_o)
        pair = tuple(sorted((s, o)))
        if pair not in seen:
            seen.add(pair)
            result.append((s, p, o))
    return tuple(result)


def topology_statistics(edges: Sequence[tuple[str, str]], nodes: Sequence[str]) -> dict[str, Any]:
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
        queue = deque([node]); seen.add(node); component: list[str] = []
        while queue:
            current = queue.popleft(); component.append(current)
            for nxt in sorted(graph[current]):
                if nxt not in seen:
                    seen.add(nxt); queue.append(nxt)
        components.append(component)
    active = [c for c in components if any(degree[n] for n in c)]
    diameter = 0
    for component in active:
        for start in component:
            dist = {start: 0}; queue = deque([start])
            while queue:
                current = queue.popleft()
                for nxt in graph[current]:
                    if nxt not in dist:
                        dist[nxt] = dist[current] + 1; queue.append(nxt)
            diameter = max(diameter, max(dist.values(), default=0))
    degree_sum = sum(degree.values())
    n = len(nodes)
    return {
        "connected_components": len(components),
        "active_components": len(active),
        "max_degree": max(degree.values(), default=0),
        "degree_concentration": max(degree.values(), default=0) / degree_sum if degree_sum else 0.0,
        "diameter": diameter,
        "shared_anchor_fraction": sum(d * (d - 1) // 2 for d in degree.values()) / max(1, len(edges) * (len(edges) - 1) // 2),
        "largest_component": max(map(len, components), default=0),
        "relation_graph_density": 2 * len(edges) / (n * (n - 1)) if n > 1 else 0.0,
    }


def _article(name: str) -> str:
    first = name.replace("_", " ").split()[0].lower()
    return "an" if first[:1] in {"a", "e", "i", "o", "u"} else "a"


def _object_name(index: int, payload: ScenePayload, first: set[int], last: set[int], types: set[int], rng: np.random.Generator) -> str:
    class_id = payload.object_class_ids[index]
    kind = payload.object_types[class_id].replace("_", " ")
    if index in last:
        return f"the {kind}"
    if index not in first and class_id in types:
        first.add(index)
        return f"another {kind}"
    name = payload.object_descriptions[index] if rng.random() > 0.25 else f"{_article(kind)} {kind}"
    first.add(index)
    return name


def _predicate_surface(predicate: str, rng: np.random.Generator) -> tuple[str, str]:
    forward, reverse = predicate, reverse_rel(predicate)
    if predicate in {"left of", "right of"} and rng.random() < 0.5:
        return "to the " + forward, "to the " + reverse
    if predicate in {"closely left of", "closely right of"}:
        if rng.random() < 0.25:
            return "closely to the " + forward.split()[-2] + " of", "closely to the " + reverse.split()[-2] + " of"
        if rng.random() < 0.5:
            return "to the close " + forward.split()[-2] + " of", "to the close " + reverse.split()[-2] + " of"
        if rng.random() < 0.75:
            return "to the near " + forward.split()[-2] + " of", "to the near " + reverse.split()[-2] + " of"
    return forward, reverse


def render_fixed_count(payload: ScenePayload, target_count: int, seed: int) -> tuple[str, list[dict[str, Any]]]:
    """SceneNAT-v2 refined text protocol with only the relation-count draw frozen."""
    if not 1 <= target_count <= len(payload.filtered_relations):
        raise ValueError(f"count {target_count} unavailable in {payload.scene_uid}")
    rng = np.random.default_rng(seed)
    relations = list(payload.filtered_relations)
    selected = [int(x) for x in rng.permutation(len(relations))[:target_count].tolist()]
    mentioned: set[int] = set(); ordered: list[int] = []; must_fix: set[int] = set()
    first_idx = selected[0]
    s, _, o = relations[first_idx]; mentioned.update((s, o)); ordered.append(first_idx)
    for idx in selected[1:]:
        s, p, o = relations[idx]
        if s in mentioned:
            relations[idx] = (o, PREDICATES.index(reverse_rel(PREDICATES[p])), s)
            mentioned.add(o); must_fix.add(idx)
        else:
            mentioned.update((s, o))
        ordered.append(idx)

    sentences: list[str] = []; emitted: list[dict[str, Any]] = []
    first: set[int] = set(); last: set[int] = set(); mentioned_types: set[int] = set()
    for idx in ordered:
        s, p, o = relations[idx]
        s_name = _object_name(s, payload, first, last, mentioned_types, rng)
        o_name = _object_name(o, payload, first, last, mentioned_types, rng)
        predicate = PREDICATES[p]
        forward_surface, reverse_surface = _predicate_surface(predicate, rng)
        use_forward = idx in must_fix or rng.random() < 0.5
        if use_forward:
            es, eo, ep = s, o, predicate; subject, obj, surface = s_name, o_name, forward_surface
        else:
            es, eo, ep = o, s, reverse_rel(predicate); subject, obj, surface = o_name, s_name, reverse_surface
        verbs = ["Place", "Put", "Position", "Arrange", "Add", "Set up"]
        if "lamp" in subject:
            verbs += ["Hang", "Install"]
        sentences.append(f"{str(rng.choice(verbs))} {subject} {surface} {obj}.")
        emitted.append({
            "source_index": es, "target_index": eo,
            "source_object_id": payload.object_ids[es], "target_object_id": payload.object_ids[eo],
            "source_class": payload.object_types[payload.object_class_ids[es]],
            "target_class": payload.object_types[payload.object_class_ids[eo]],
            "predicate": ep, "family": relation_family(ep), "filtered_relation_index": idx,
        })
        last = {s, o}; mentioned_types.update((payload.object_class_ids[s], payload.object_class_ids[o]))

    conjunctions = [" Then, ", " Next, ", " Additionally, ", " Finally, ", " And ", " "]
    text = ""
    for index, sentence in enumerate(sentences):
        if index == 0:
            text = sentence; continue
        conjunction = str(rng.choice(conjunctions))
        while conjunction == " Finally, " and index != len(sentences) - 1:
            conjunction = str(rng.choice(conjunctions))
        if conjunction != " ":
            sentence = sentence[0].lower() + sentence[1:]
        text += conjunction + sentence
    return text, emitted
