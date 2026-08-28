from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SCHEMA_VERSION = "behavior-formal-goal-coupling-v1.1"

BOOLEAN_OPERATORS = frozenset({"and", "or", "not", "imply"})
QUANTIFIER_OPERATORS = frozenset({"forall", "exists", "forn", "forpairs", "fornpairs"})
OPERATORS = BOOLEAN_OPERATORS | QUANTIFIER_OPERATORS
BRANCH_OPERATORS = frozenset({"or", "imply"})


@dataclass(frozen=True, slots=True)
class AtomicLeaf:
    predicate: str
    arguments: tuple[str, ...]
    negated: bool

    @property
    def structural_key(self) -> tuple[Any, ...]:
        return (self.negated, self.predicate, self.arguments)


@dataclass(slots=True)
class _WalkResult:
    leaves: list[AtomicLeaf]
    logical_depth: int
    quantifier_count: int
    branch_operator_count: int
    unbound_variable_count: int


def _token(value: Any) -> str:
    return str(value).strip().lower()


def _binder_variable(binder: Any) -> str:
    if not isinstance(binder, list) or len(binder) < 3:
        raise ValueError(f"malformed BDDL binder:{binder!r}")
    variable = _token(binder[0])
    if not variable.startswith("?"):
        raise ValueError(f"BDDL binder variable must start with ?: {binder!r}")
    if _token(binder[1]) != "-":
        raise ValueError(f"BDDL binder must contain '-' separator:{binder!r}")
    return variable


def _alpha_bind(scope: dict[str, str], binder: Any, scope_id: int) -> dict[str, str]:
    variable = _binder_variable(binder)
    child = dict(scope)
    child[variable] = f"v:q{scope_id}:{variable}"
    return child


def _normalize_argument(argument: Any, scope: dict[str, str], ground_instances: set[str]) -> tuple[str, int]:
    value = _token(argument)
    if value.startswith("?"):
        # BEHAVIOR BDDL prefixes both quantified variables and concrete goal
        # object instances with '?'. Match the official Predicate resolution:
        # current quantifier binding wins; otherwise a declared :objects
        # instance is concrete; only then is the token genuinely unresolved.
        if value in scope:
            return scope[value], 0
        bare = value[1:]
        if bare in ground_instances:
            return f"g:{bare}", 0
        return f"unbound:{value}", 1
    return f"g:{value}", 0


def _walk(
    expr: Any,
    scope: dict[str, str],
    next_scope_id: list[int],
    ground_instances: set[str],
    negated: bool = False,
) -> _WalkResult:
    if not isinstance(expr, list) or not expr:
        raise ValueError(f"BDDL goal expression must be a non-empty list:{expr!r}")
    head = _token(expr[0])

    if head not in OPERATORS:
        args: list[str] = []
        unbound = 0
        for raw in expr[1:]:
            if isinstance(raw, list):
                raise ValueError(f"atomic predicate contains nested argument:{expr!r}")
            normalized, missing = _normalize_argument(raw, scope, ground_instances)
            args.append(normalized)
            unbound += missing
        return _WalkResult(
            leaves=[AtomicLeaf(predicate=head, arguments=tuple(args), negated=negated)],
            logical_depth=1,
            quantifier_count=0,
            branch_operator_count=0,
            unbound_variable_count=unbound,
        )

    if head == "not":
        if len(expr) != 2:
            raise ValueError(f"not must have exactly one child:{expr!r}")
        child = _walk(expr[1], scope, next_scope_id, ground_instances, not negated)
        child.logical_depth += 1
        return child

    if head in {"and", "or", "imply"}:
        children = expr[1:]
        if head == "imply" and len(children) != 2:
            raise ValueError(f"imply must have exactly two children:{expr!r}")
        if not children:
            raise ValueError(f"{head} must have at least one child")
        walked = [_walk(child, scope, next_scope_id, ground_instances, negated) for child in children]
        return _WalkResult(
            leaves=[leaf for result in walked for leaf in result.leaves],
            logical_depth=1 + max(result.logical_depth for result in walked),
            quantifier_count=sum(result.quantifier_count for result in walked),
            branch_operator_count=(1 if head in BRANCH_OPERATORS else 0)
            + sum(result.branch_operator_count for result in walked),
            unbound_variable_count=sum(result.unbound_variable_count for result in walked),
        )

    # Quantifiers are retained syntactically and never grounded into the object
    # domain.  This keeps the metric independent of sampler/domain cardinality.
    next_scope_id[0] += 1
    first_scope = next_scope_id[0]
    if head in {"forall", "exists"}:
        if len(expr) != 3:
            raise ValueError(f"{head} must have binder and body:{expr!r}")
        child_scope = _alpha_bind(scope, expr[1], first_scope)
        body = expr[2]
    elif head == "forn":
        if len(expr) != 4:
            raise ValueError(f"forn must have count,binder,body:{expr!r}")
        child_scope = _alpha_bind(scope, expr[2], first_scope)
        body = expr[3]
    elif head == "forpairs":
        if len(expr) != 4:
            raise ValueError(f"forpairs must have two binders and body:{expr!r}")
        child_scope = _alpha_bind(scope, expr[1], first_scope)
        next_scope_id[0] += 1
        child_scope = _alpha_bind(child_scope, expr[2], next_scope_id[0])
        body = expr[3]
    elif head == "fornpairs":
        if len(expr) != 5:
            raise ValueError(f"fornpairs must have count,two binders,body:{expr!r}")
        child_scope = _alpha_bind(scope, expr[2], first_scope)
        next_scope_id[0] += 1
        child_scope = _alpha_bind(child_scope, expr[3], next_scope_id[0])
        body = expr[4]
    else:  # pragma: no cover - OPERATORS exhausts this branch.
        raise ValueError(f"unsupported quantifier:{head}")

    child = _walk(body, child_scope, next_scope_id, ground_instances, negated)
    child.logical_depth += 1
    child.quantifier_count += 1
    return child


def _largest_component_size(node_count: int, edges: list[tuple[int, int]]) -> int:
    if node_count == 0:
        return 0
    adjacency = [set() for _ in range(node_count)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen: set[int] = set()
    largest = 0
    for start in range(node_count):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        largest = max(largest, size)
    return largest


def analyze_goal_state(goal_state: list[Any], object_map: dict[str, list[str]] | None = None) -> dict[str, Any]:
    """Compute frozen syntax-only formal-goal metrics from a BDDL goal_state.

    ``goal_state`` follows the pinned BEHAVIOR parser contract: it is a list of
    top-level clauses with the original top-level ``and`` packaging removed.
    The implicit top-level conjunction therefore contributes no logical depth.
    """
    if not isinstance(goal_state, list):
        raise ValueError("goal_state must be a list")
    if not goal_state:
        return {
            "schema_version": SCHEMA_VERSION,
            "atomic_occurrence_count": 0,
            "atomic_goal_count": 0,
            "duplicate_atomic_occurrences": 0,
            "shared_argument_edge_count": 0,
            "largest_connected_component_size": 0,
            "mean_degree": 0.0,
            "coupling_density": 0.0,
            "goal_logic_depth": 0,
            "quantifier_count": 0,
            "branch_operator_count": 0,
            "unbound_variable_count": 0,
        }

    ground_instances = {
        _token(instance)
        for instances in (object_map or {}).values()
        for instance in instances
    }
    scope_counter = [0]
    results = [_walk(clause, {}, scope_counter, ground_instances, False) for clause in goal_state]
    occurrences = [leaf for result in results for leaf in result.leaves]

    unique_by_key: dict[tuple[Any, ...], AtomicLeaf] = {}
    for leaf in occurrences:
        unique_by_key.setdefault(leaf.structural_key, leaf)
    nodes = list(unique_by_key.values())

    edges: list[tuple[int, int]] = []
    for i in range(len(nodes)):
        left_args = set(nodes[i].arguments)
        for j in range(i + 1, len(nodes)):
            if left_args.intersection(nodes[j].arguments):
                edges.append((i, j))

    possible_edges = len(nodes) * (len(nodes) - 1) / 2
    lcc = _largest_component_size(len(nodes), edges)
    return {
        "schema_version": SCHEMA_VERSION,
        "atomic_occurrence_count": len(occurrences),
        "atomic_goal_count": len(nodes),
        "duplicate_atomic_occurrences": len(occurrences) - len(nodes),
        "shared_argument_edge_count": len(edges),
        "largest_connected_component_size": lcc,
        "mean_degree": (2.0 * len(edges) / len(nodes)) if nodes else 0.0,
        "coupling_density": (len(edges) / possible_edges) if possible_edges else 0.0,
        "goal_logic_depth": max(result.logical_depth for result in results),
        "quantifier_count": sum(result.quantifier_count for result in results),
        "branch_operator_count": sum(result.branch_operator_count for result in results),
        "unbound_variable_count": sum(result.unbound_variable_count for result in results),
    }
