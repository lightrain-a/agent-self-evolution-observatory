from __future__ import annotations

from typing import Mapping


def validate_distribution(values: Mapping[str, float], *, tol: float = 1e-12) -> None:
    if not values or any(float(v) < -tol for v in values.values()):
        raise ValueError("distribution must be nonnegative and nonempty")
    if abs(sum(float(v) for v in values.values()) - 1.0) > tol:
        raise ValueError("distribution must sum to one")


def joint_cell_primitive_mass(
    cell_prior: Mapping[str, float],
    responsibility: Mapping[str, Mapping[str, float]],
) -> dict[tuple[str, str], float]:
    validate_distribution(cell_prior)
    joint: dict[tuple[str, str], float] = {}
    for cell, mu in cell_prior.items():
        alpha = responsibility.get(cell) or {}
        validate_distribution(alpha)
        for primitive, weight in alpha.items():
            joint[(cell, primitive)] = float(mu) * float(weight)
    return joint


def primitive_mass(joint: Mapping[tuple[str, str], float]) -> dict[str, float]:
    result: dict[str, float] = {}
    for (_, primitive), value in joint.items():
        result[primitive] = result.get(primitive, 0.0) + float(value)
    return result


def package_mass(
    primitive: Mapping[str, float],
    wrapper: Mapping[str, str],
) -> dict[str, float]:
    """Project invariant primitive mass onto a taxonomy-specific package wrapper."""
    if set(wrapper) != set(primitive):
        raise ValueError("wrapper must map every primitive exactly once")
    out: dict[str, float] = {}
    for primitive_id, value in primitive.items():
        package = str(wrapper[primitive_id])
        out[package] = out.get(package, 0.0) + float(value)
    return out


def distribute_credit(
    semantic_credit: Mapping[str, float],
    responsibility: Mapping[str, Mapping[str, float]],
) -> dict[str, float]:
    """Credit one semantic event once; primitive responsibilities conserve total credit."""
    out: dict[str, float] = {}
    for cell, credit in semantic_credit.items():
        alpha = responsibility.get(cell) or {}
        validate_distribution(alpha)
        for primitive, weight in alpha.items():
            out[primitive] = out.get(primitive, 0.0) + float(credit) * float(weight)
    return out
