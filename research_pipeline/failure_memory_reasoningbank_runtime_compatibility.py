"""Audit ReasoningBank's declared WebArena runtime without scientific execution.

This audit is deliberately support-side. It inspects the pinned first-party
pyproject/uv.lock, a failed Python-3.13 greenlet installation receipt, and an
isolated Python-3.12 BrowserGym-0.14.1 component environment. It does not start
a browser task, call a model, or open a scientific outcome.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
AUDIT_ID = "D2-C45-REASONINGBANK-RUNTIME-COMPATIBILITY-R10"
EXPECTED_REASONINGBANK_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
EXPECTED_PYPROJECT_SHA256 = "8d2b9f61b5cae47ed7a83e61e4893f9c0a2c1035fe37ef64006748ab4934cfbe"
EXPECTED_UV_LOCK_SHA256 = "6835cc5149faf4ddd573cae98851bbd5db6844a1bed567fe8a85525d862d77fa"
EXPECTED_PY313_FAILURE_LOG_SHA256 = "19d81f2ca7c419e3a2e420f4608f8fc1281a021352aa2acbf097ad6852dd9d98"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def package_block(lock_text: str, name: str) -> str:
    # Dependency arrays also contain `name = ...`; only accept a name that is
    # the top-level name inside its own [[package]] block.
    for match in re.finditer(r'(?ms)^\[\[package\]\]\n.*?(?=^\[\[package\]\]|\Z)', lock_text):
        block = match.group(0)
        top = re.search(r'^name = "([^"]+)"$', block, re.MULTILINE)
        if top and top.group(1) == name:
            return block
    raise ValueError(f"missing package in uv.lock: {name}")


def extract_version(block: str) -> str:
    m = re.search(r'^version = "([^"]+)"', block, re.MULTILINE)
    if not m:
        raise ValueError("version missing")
    return m.group(1)


def inspect_first_party(root: Path) -> dict[str, Any]:
    head = git_head(root)
    if head != EXPECTED_REASONINGBANK_COMMIT:
        raise ValueError(f"ReasoningBank commit drift: {head}")
    pyproject = root / "pyproject.toml"
    lock = root / "uv.lock"
    if sha256(pyproject) != EXPECTED_PYPROJECT_SHA256:
        raise ValueError("pyproject digest drift")
    if sha256(lock) != EXPECTED_UV_LOCK_SHA256:
        raise ValueError("uv.lock digest drift")

    py = pyproject.read_text(encoding="utf-8")
    uv = lock.read_text(encoding="utf-8")
    requires_python = re.search(r'^requires-python = "([^"]+)"', py, re.MULTILINE)
    lock_requires_python = re.search(r'^requires-python = "([^"]+)"', uv, re.MULTILINE)
    if not requires_python or not lock_requires_python:
        raise ValueError("requires-python missing")

    bg = package_block(uv, "browsergym-core")
    pw = package_block(uv, "playwright")
    gr = package_block(uv, "greenlet")
    facts = {
        "requires_python": requires_python.group(1),
        "uv_lock_requires_python": lock_requires_python.group(1),
        "browsergym_core": extract_version(bg),
        "playwright": extract_version(pw),
        "greenlet": extract_version(gr),
        "greenlet_wheel_urls_in_lock": re.findall(r'url = "([^"]+greenlet[^\"]+\.whl)"', gr),
        "greenlet_sdist_sha256": None,
    }
    sm = re.search(r'sdist = \{[^\n]*hash = "sha256:([0-9a-f]+)"', gr)
    if sm:
        facts["greenlet_sdist_sha256"] = sm.group(1)
    facts["greenlet_cp313_wheels_in_lock"] = sum("cp313" in x for x in facts["greenlet_wheel_urls_in_lock"])

    # The top-level project says playwright>=1.44, but BrowserGym Core's wheel
    # metadata pins playwright==1.44. The uv.lock is authoritative evidence of
    # the resulting resolved 1.44.0 -> greenlet 3.0.3 chain.
    expected = {
        "requires_python": ">=3.13",
        "uv_lock_requires_python": ">=3.13",
        "browsergym_core": "0.14.1",
        "playwright": "1.44.0",
        "greenlet": "3.0.3",
        "greenlet_cp313_wheels_in_lock": 0,
    }
    for key, val in expected.items():
        if facts[key] != val:
            raise ValueError(f"first-party runtime fact drift: {key}={facts[key]!r} expected {val!r}")

    return {
        "repository": "https://github.com/google-research/reasoning-bank.git",
        "commit": head,
        "pyproject_sha256": sha256(pyproject),
        "uv_lock_sha256": sha256(lock),
        "resolved_dependency_facts": facts,
        "static_incompatibility_signal": (
            "The first-party project and lock require Python>=3.13 while the locked WebArena path resolves "
            "BrowserGym Core 0.14.1 -> Playwright 1.44.0 -> greenlet 3.0.3, with no cp313 greenlet wheel in the lock."
        ),
    }


def inspect_failure_log(path: Path) -> dict[str, Any]:
    digest = sha256(path)
    if digest != EXPECTED_PY313_FAILURE_LOG_SHA256:
        raise ValueError(f"Python-3.13 failure-log digest drift: {digest}")
    text = path.read_text(encoding="utf-8", errors="replace")
    markers = {
        "failed_building_greenlet_wheel": "Failed building wheel for greenlet" in text,
        "failed_wheel_build": "failed-wheel-build-for-install" in text,
        "py_build_core_error": "Py_BUILD_CORE" in text,
        "py_cframe_error": "_PyCFrame" in text,
    }
    if not all(markers.values()):
        raise ValueError(f"expected Python-3.13 build-failure markers absent: {markers}")
    return {
        "path_role": "support-side isolated Python-3.13 install attempt log",
        "sha256": digest,
        "exit_code": 1,
        "target": "greenlet==3.0.3",
        "markers": markers,
        "scientific_outcome": False,
    }


def inspect_compat_env(env: Path, nltk_data: Path) -> dict[str, Any]:
    py = env / "bin/python"
    if not py.exists():
        raise ValueError(f"compatibility Python missing: {py}")
    if not (nltk_data / "tokenizers/punkt_tab").exists():
        raise ValueError(f"private punkt_tab resource missing: {nltk_data}")
    code = r'''
import importlib.metadata as md, importlib.util, json, sys
versions = {}
for p in ["browsergym", "browsergym-core", "browsergym-experiments", "browsergym-webarena", "playwright", "greenlet", "libwebarena"]:
    try: versions[p] = md.version(p)
    except Exception: versions[p] = None
core_imports = True
error = None
webarena_import = False
webarena_error = None
webarena_task_count = None
try:
    import browsergym.core, browsergym.experiments, playwright
except Exception as e:
    core_imports = False
    error = type(e).__name__ + ":" + str(e)
try:
    import nltk
    nltk.data.find("tokenizers/punkt_tab")
    import browsergym.webarena as wa
    webarena_import = True
    webarena_task_count = len(wa.ALL_WEBARENA_TASK_IDS)
except Exception as e:
    webarena_error = type(e).__name__ + ":" + str(e)
print(json.dumps({
    "python": sys.version.split()[0],
    "versions": versions,
    "core_experiments_playwright_imports": core_imports,
    "core_import_error": error,
    "webarena_spec": (importlib.util.find_spec("browsergym.webarena").origin if importlib.util.find_spec("browsergym.webarena") else None),
    "webarena_import_completed": webarena_import,
    "webarena_import_error": webarena_error,
    "webarena_registered_task_ids": webarena_task_count,
}))
'''
    env_vars = dict(os.environ)
    env_vars["NLTK_DATA"] = str(nltk_data)
    result = subprocess.run([str(py), "-c", code], text=True, capture_output=True, check=True, env=env_vars)
    payload = json.loads(result.stdout.strip())
    expected_versions = {
        "browsergym": "0.14.1",
        "browsergym-core": "0.14.1",
        "browsergym-experiments": "0.14.1",
        "browsergym-webarena": "0.14.1",
        "playwright": "1.44.0",
        "greenlet": "3.0.3",
        "libwebarena": "0.0.4",
    }
    if payload["python"] != "3.12.13":
        raise ValueError(f"compatibility Python drift: {payload['python']}")
    if payload["versions"] != expected_versions:
        raise ValueError(f"compatibility package drift: {payload['versions']}")
    if payload["core_experiments_playwright_imports"] is not True:
        raise ValueError(f"compatibility core import failed: {payload['core_import_error']}")
    if not payload["webarena_spec"]:
        raise ValueError("browsergym.webarena module spec missing")
    if payload["webarena_import_completed"] is not True or payload["webarena_registered_task_ids"] != 812:
        raise ValueError(f"compatibility WebArena import drift: {payload}")
    site_packages = env / "lib/python3.12/site-packages"
    browsers_json = site_packages / "playwright/driver/package/browsers.json"
    browsers = json.loads(browsers_json.read_text(encoding="utf-8"))
    chromium = next(x for x in browsers["browsers"] if x["name"] == "chromium")
    expected_chromium_revision = str(chromium["revision"])
    default_browser_cache = Path.home() / ".cache/ms-playwright"
    matching_chromium_cache = default_browser_cache / f"chromium-{expected_chromium_revision}"
    required_site_envs = ["REDDIT", "SHOPPING", "SHOPPING_ADMIN", "GITLAB", "WIKIPEDIA", "MAP", "HOMEPAGE"]
    site_env = {name: os.environ.get(name, "") for name in required_site_envs}
    docker = subprocess.run(["docker", "ps", "--format", "{{.Names}} {{.Image}}"], text=True, capture_output=True)
    docker_lines = [line for line in docker.stdout.splitlines() if any(token in line.lower() for token in ("webarena", "shopping", "reddit", "gitlab", "map"))]
    return {
        "environment_role": "minimal WebArena-component compatibility environment; not the first-party declared Python>=3.13 environment",
        "environment_path": str(env),
        **payload,
        "private_nltk_data": str(nltk_data),
        "punkt_tab_files": sum(1 for x in (nltk_data / "tokenizers/punkt_tab").rglob("*") if x.is_file()),
        "playwright_chromium_revision": expected_chromium_revision,
        "playwright_chromium_version": chromium.get("browserVersion"),
        "matching_default_chromium_cache_found": matching_chromium_cache.is_dir(),
        "available_default_chromium_caches": sorted(x.name for x in default_browser_cache.glob("chromium-*") if x.is_dir()),
        "webarena_site_env_configured": site_env,
        "webarena_all_required_site_envs_present": all(bool(x) for x in site_env.values()),
        "webarena_like_docker_containers": docker_lines,
        "live_webarena_deployment_detected": bool(docker_lines) and all(bool(x) for x in site_env.values()),
        "full_browsergym_meta_dependency_closure": False,
        "missing_meta_extras_are_outside_planned_webarena_path": [
            "browsergym-assistantbench",
            "browsergym-miniwob",
            "browsergym-visualwebarena",
            "browsergym-workarena",
            "weblinx-browsergym",
        ],
        "browser_task_started": False,
    }


def build_audit(root: Path, py313_log: Path, compat_env: Path, nltk_data: Path) -> dict[str, Any]:
    first_party = inspect_first_party(root)
    failed = inspect_failure_log(py313_log)
    compat = inspect_compat_env(compat_env, nltk_data)
    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "audit_id": AUDIT_ID,
        "recorded_date": "2026-08-24",
        "status": "DECLARED_PY313_RUNTIME_NOT_DIRECTLY_MATERIALIZABLE_PY312_WEBARENA_COMPATIBILITY_PATH_VERIFIED",
        "role": "ZERO_MODEL_ZERO_BROWSER_TASK_RUNTIME_SUPPORT_AUDIT",
        "first_party_runtime": first_party,
        "python313_materialization_attempt": failed,
        "python312_compatibility_runtime": compat,
        "adjudication": {
            "exact_declared_python313_runtime_materialized": False,
            "exact_declared_runtime_support_failure": True,
            "support_failure_is_scientific_failure": False,
            "python312_browsergym0141_component_path_materialized": True,
            "python312_webarena_import_verified": True,
            "python312_live_browser_revision_ready": bool(compat["matching_default_chromium_cache_found"]),
            "python312_live_webarena_site_deployment_ready": bool(compat["live_webarena_deployment_detected"]),
            "python312_path_is_source_faithful_as_declared": False,
            "python312_path_may_be_silently_promoted_to_exact_runtime": False,
            "browsergym_or_playwright_may_be_silently_upgraded": False,
            "preferred_compatibility_deviation_if_l2_reopens": "Keep BrowserGym Core/Experiments/WebArena 0.14.1 and Playwright 1.44.0 fixed, use Python 3.12 only under an explicit compatibility-deviation label plus a pre-outcome live-runtime/evaluator fidelity gate. The interpreter deviation is shared across treatment arms, so it changes transport/runtime fidelity rather than the L2 within-runtime treatment definition.",
            "alternative_exact_reopen": "Obtain a first-party corrected lock/runtime receipt that is actually installable under Python>=3.13.",
            "l3_financial_transport_unblocked": False,
            "scientific_verdict": "NO_VERDICT_RUNTIME_SUPPORT_FAILURE",
        },
        "remaining_pre_execution_gates": [
            "choose and freeze exact-declared versus explicit Python-3.12 compatibility runtime policy",
            "if compatibility runtime is used, acquire the exact Playwright Chromium revision 1117 and configure/deploy all seven WebArena site URLs before a source-native evaluator/reset smoke; private punkt_tab and WebArena import are already verified",
            "bind source-memory generation/fixed selection",
            "bind executor/model/version/paired rollout count and maximum request budget",
            "bind L2-specific variance/noise source and final paired randomization implementation",
            "obtain scientific and experiment/model-call authority",
        ],
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_calls": False,
            "browser_tasks": False,
            "gpu": False,
            "submission": False,
        },
        "strongest_allowed_current_statement": (
            "The pinned first-party ReasoningBank dependency declaration is not directly materializable on Linux/Python 3.13 as resolved: "
            "its locked BrowserGym 0.14.1 path fixes Playwright 1.44.0 and greenlet 3.0.3, whose source build fails against Python 3.13. "
            "A Python 3.12.13 environment with the same BrowserGym WebArena components, Playwright, and greenlet versions installs and imports WebArena, registering 812 tasks, "
            "establishing a compatibility path but not an exact-as-declared runtime. No browser task or model call was executed."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--reasoningbank-root", type=Path, required=True)
    p.add_argument("--py313-failure-log", type=Path, required=True)
    p.add_argument("--compat-env", type=Path, required=True)
    p.add_argument("--nltk-data", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-reasoningbank-runtime-compatibility-r10.json"))
    args = p.parse_args()
    payload = build_audit(args.reasoningbank_root, args.py313_failure_log, args.compat_env, args.nltk_data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "exact_py313": payload["adjudication"]["exact_declared_python313_runtime_materialized"],
        "py312_compat": payload["adjudication"]["python312_browsergym0141_component_path_materialized"],
        "scientific_verdict": payload["adjudication"]["scientific_verdict"],
        "model_calls": payload["authority"]["model_calls"],
        "browser_tasks": payload["authority"]["browser_tasks"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
