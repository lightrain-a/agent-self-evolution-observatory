from __future__ import annotations

import math
import statistics
from collections import Counter
from typing import Any

SCHEMA_VERSION = "behavior-formal-goal-coupling-distribution-gate-v1"

# Frozen by generated/behavior-formal-goal-coupling-source-qualification-20260828.json
# before any BEHAVIOR activity-definition structure was scanned.
MIN_NONTRIVIAL_TASKS = 100
MAX_DOMINANT_VALUE_FRACTION = 0.90
MAX_ABS_COUPLING_SIZE_SPEARMAN = 0.90
MAX_BRANCH_BEARING_TASK_FRACTION = 0.30


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


def _dominant_fraction(values: list[int]) -> float | None:
    if not values:
        return None
    return max(Counter(values).values()) / len(values)


def summarize_distribution(task_rows: list[dict[str, Any]], *, parser_error_tasks: int = 0) -> dict[str, Any]:
    required = {
        "atomic_goal_count",
        "shared_argument_edge_count",
        "largest_connected_component_size",
        "goal_logic_depth",
        "branch_operator_count",
        "unbound_variable_count",
    }
    for index, row in enumerate(task_rows):
        missing = sorted(required - set(row))
        if missing:
            raise ValueError(f"task row {index} missing structural metrics:{','.join(missing)}")

    nontrivial = [row for row in task_rows if int(row["atomic_goal_count"]) >= 2]
    sizes = [int(row["atomic_goal_count"]) for row in nontrivial]
    edges = [int(row["shared_argument_edge_count"]) for row in nontrivial]
    branch_fraction = (
        sum(int(row["branch_operator_count"]) > 0 for row in task_rows) / len(task_rows)
        if task_rows
        else 0.0
    )
    unbound_tasks = sum(int(row["unbound_variable_count"]) > 0 for row in task_rows)
    size_dominant = _dominant_fraction(sizes)
    edge_dominant = _dominant_fraction(edges)
    coupling_size_rho = spearman([float(v) for v in edges], [float(v) for v in sizes])

    gates = {
        "parser_errors_zero": parser_error_tasks == 0,
        "unbound_variable_tasks_zero": unbound_tasks == 0,
        "enough_nontrivial_tasks": len(nontrivial) >= MIN_NONTRIVIAL_TASKS,
        "atomic_goal_count_has_variance": size_dominant is not None and size_dominant < MAX_DOMINANT_VALUE_FRACTION,
        "shared_argument_edge_count_has_variance": edge_dominant is not None and edge_dominant < MAX_DOMINANT_VALUE_FRACTION,
        "coupling_not_almost_redundant_with_size": coupling_size_rho is not None
        and abs(coupling_size_rho) < MAX_ABS_COUPLING_SIZE_SPEARMAN,
        "branch_overapproximation_not_dominant": branch_fraction <= MAX_BRANCH_BEARING_TASK_FRACTION,
    }
    gates["pass"] = all(gates.values())
    return {
        "schema_version": SCHEMA_VERSION,
        "scientific_authority": False,
        "result_access_authorized": False,
        "task_count": len(task_rows),
        "nontrivial_task_count": len(nontrivial),
        "parser_error_tasks": parser_error_tasks,
        "unbound_variable_tasks": unbound_tasks,
        "branch_bearing_task_fraction": branch_fraction,
        "atomic_goal_count_dominant_value_fraction": size_dominant,
        "shared_argument_edge_count_dominant_value_fraction": edge_dominant,
        "shared_argument_edge_vs_atomic_goal_spearman": coupling_size_rho,
        "descriptive_only": {
            "atomic_goal_count_median": statistics.median(sizes) if sizes else None,
            "shared_argument_edge_count_median": statistics.median(edges) if edges else None,
            "largest_connected_component_median": statistics.median(
                [int(row["largest_connected_component_size"]) for row in nontrivial]
            ) if nontrivial else None,
            "goal_logic_depth_median": statistics.median(
                [int(row["goal_logic_depth"]) for row in nontrivial]
            ) if nontrivial else None,
        },
        "frozen_thresholds": {
            "min_nontrivial_tasks": MIN_NONTRIVIAL_TASKS,
            "max_dominant_value_fraction": MAX_DOMINANT_VALUE_FRACTION,
            "max_abs_coupling_size_spearman": MAX_ABS_COUPLING_SIZE_SPEARMAN,
            "max_branch_bearing_task_fraction": MAX_BRANCH_BEARING_TASK_FRACTION,
        },
        "gates": gates,
    }
