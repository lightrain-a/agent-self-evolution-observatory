from __future__ import annotations

import jax
import jax.numpy as jnp
import optax


def loss_fn(params, x, y):
    pred = x @ params["w"] + params["b"]
    return jnp.mean(jnp.square(pred - y))


def main() -> None:
    key = jax.random.key(7)
    kx, ky, kw = jax.random.split(key, 3)
    x = jax.random.normal(kx, (64, 5))
    y = jax.random.normal(ky, (64, 3))
    params = {
        "w": jax.random.normal(kw, (5, 3)) * 0.1,
        "b": jnp.zeros((3,)),
    }
    tx = optax.chain(
        optax.clip_by_global_norm(1.0),
        optax.adamw(2.5e-5, b1=0.9, b2=0.95, eps=1e-8, weight_decay=1e-10),
    )
    opt_state_full = tx.init(params)
    opt_state_acc = tx.init(params)

    full_grad = jax.grad(loss_fn)(params, x, y)
    micro_grads = []
    for i in range(8):
        sl = slice(i * 8, (i + 1) * 8)
        micro_grads.append(jax.grad(loss_fn)(params, x[sl], y[sl]))
    accum_grad = jax.tree.map(lambda *xs: sum(xs) / 8.0, *micro_grads)

    grad_max_abs = max(
        float(jnp.max(jnp.abs(a - b)))
        for a, b in zip(jax.tree.leaves(full_grad), jax.tree.leaves(accum_grad), strict=True)
    )
    assert grad_max_abs < 2e-7, grad_max_abs

    updates_full, next_opt_full = tx.update(full_grad, opt_state_full, params)
    updates_acc, next_opt_acc = tx.update(accum_grad, opt_state_acc, params)
    params_full = optax.apply_updates(params, updates_full)
    params_acc = optax.apply_updates(params, updates_acc)
    param_max_abs = max(
        float(jnp.max(jnp.abs(a - b)))
        for a, b in zip(jax.tree.leaves(params_full), jax.tree.leaves(params_acc), strict=True)
    )
    assert param_max_abs < 2e-7, param_max_abs

    # The production child updates EMA exactly once after the one effective optimizer update.
    ema_decay = 0.99
    ema_full = jax.tree.map(lambda old, new: ema_decay * old + (1 - ema_decay) * new, params, params_full)
    ema_acc = jax.tree.map(lambda old, new: ema_decay * old + (1 - ema_decay) * new, params, params_acc)
    ema_max_abs = max(
        float(jnp.max(jnp.abs(a - b)))
        for a, b in zip(jax.tree.leaves(ema_full), jax.tree.leaves(ema_acc), strict=True)
    )
    assert ema_max_abs < 2e-7, ema_max_abs

    # Optax state is advanced once in both paths, not eight times.
    count_full = int(jax.device_get(next_opt_full[1][0].count))
    count_acc = int(jax.device_get(next_opt_acc[1][0].count))
    assert count_full == 1 and count_acc == 1, (count_full, count_acc)

    print(
        {
            "status": "ACCUM8X8_DETERMINISTIC_MATH_PASS",
            "gradient_max_abs_error": grad_max_abs,
            "parameter_max_abs_error": param_max_abs,
            "ema_max_abs_error": ema_max_abs,
            "optimizer_count_full": count_full,
            "optimizer_count_accum": count_acc,
            "note": "This validates deterministic accumulation arithmetic only; pi0.5 stochastic RNG expansion remains the separately preregistered child semantics.",
        }
    )


if __name__ == "__main__":
    main()
