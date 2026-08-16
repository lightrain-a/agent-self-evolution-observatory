from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("agent3_stri_sqc_static_control.py")
spec = importlib.util.spec_from_file_location("agent3_stri_sqc_static_control", MODULE_PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_expected_unique_uniform_beats_concentrated_at_fixed_budget():
    uniform = [0.25, 0.25, 0.25, 0.25]
    concentrated = [0.4, 0.3, 0.2, 0.1]
    assert m.expected_unique(uniform, 4) > m.expected_unique(concentrated, 4)


def test_sqc_joint_is_context_uniform_despite_overlap():
    rows = [
        {"accepted_skill_ids": ["a"]},
        {"accepted_skill_ids": ["a", "b"]},
        {"accepted_skill_ids": ["b"]},
    ]
    r = m.sqc_joint(rows, {"a", "b"})
    assert r["context_distribution"] == [1 / 3, 1 / 3, 1 / 3]
    assert abs(sum(r["package_marginal"].values()) - 1.0) < 1e-12


def test_global_additive_exposure_overweights_overlap():
    rows = [
        {"accepted_skill_ids": ["a"]},
        {"accepted_skill_ids": ["a", "b"]},
        {"accepted_skill_ids": ["b"]},
    ]
    e = m.exposure_for_global(rows, {"a", "b"}, {"a": 1.0, "b": 1.0})
    assert e == [1.0, 2.0, 1.0]
    assert max(e) / min(e) == 2.0


def test_sqc_clone_pushforward_is_zero_tv():
    rows = [
        {"accepted_skill_ids": ["a"]},
        {"accepted_skill_ids": ["a", "b"]},
        {"accepted_skill_ids": ["b"]},
    ]
    assert m.clone_invariance_tv(rows, {"a", "b"}, "a") == 0.0
