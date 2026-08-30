"""Qualify local Q3 parsers against the SHA-frozen SWE-bench 5.0.2 wheel."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import zipfile
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT,
    sha256_text,
    utcnow,
    write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_eval import (
    parse_django,
    parse_pytest_v2,
)

WHEEL = Path(
    "/data/wyt/e1-stri-reasoningbank-runtime/"
    "swebench-5.0.2-py3-none-any.whl"
)
WHEEL_SHA256 = "b7f0416a1e686eca22c2f749b5f816685a202835032f6683080e2b53545bbb62"
MEMBER = "swebench/harness/log_parsers/python.py"
SOURCE_SHA256 = {
    "parse_log_django": "3a4f69dccc4e44725c9e3580a323c131bafc434aed3b333126154469a41c5872",
    "parse_log_pytest_v2": "d3f4c2ef28b0005fd76df82beb06fb899aa77ae27a775273cc8579524fe8371d",
}
OUTPUT = (
    ROOT
    / "generated/asset-first-stri-reasoningbank-p1-q3-parser-qualification-20260830.json"
)


class TestStatus(Enum):
    FAILED = "FAILED"
    PASSED = "PASSED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"
    XFAIL = "XFAIL"


_SKIP_SUMMARY_COUNT = re.compile(r"^\[\d+\]$")


def _is_skip_summary(status: str, name: str) -> bool:
    return status == TestStatus.SKIPPED.value and bool(
        _SKIP_SUMMARY_COUNT.match(name)
    )


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_official() -> tuple[dict[str, Callable[..., dict[str, str]]], dict[str, str]]:
    if _file_sha256(WHEEL) != WHEEL_SHA256:
        raise RuntimeError("SWE-bench wheel SHA-256 drift")
    with zipfile.ZipFile(WHEEL) as archive:
        source = archive.read(MEMBER).decode("utf-8")
    tree = ast.parse(source)
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    extracted: dict[str, str] = {}
    for name, expected in SOURCE_SHA256.items():
        snippet = ast.get_source_segment(source, functions[name])
        if snippet is None or sha256_text(snippet) != expected:
            raise RuntimeError(f"official parser source drift: {name}")
        extracted[name] = snippet
    namespace: dict[str, Any] = {
        "re": re,
        "TestSpec": Any,
        "TestStatus": TestStatus,
        "_is_skip_summary": _is_skip_summary,
    }
    exec(extracted["parse_log_django"], namespace)
    exec(extracted["parse_log_pytest_v2"], namespace)
    return (
        {
            "parse_log_django": namespace["parse_log_django"],
            "parse_log_pytest_v2": namespace["parse_log_pytest_v2"],
        },
        {name: sha256_text(value) for name, value in extracted.items()},
    )


def corpora() -> dict[str, list[str]]:
    django = [
        "\n".join(
            [
                "--version is equivalent to version",
                "pkg.Test.test_ok ... ok",
                "pkg.Test.test_upper ... OK",
                "pkg.Test.test_spaced ...  OK",
                "pkg.Test.test_skip ... skipped 'reason'",
                "pkg.Test.test_fail ... FAIL",
                "FAIL: pkg.Test.test_fail_header (pkg.Test)",
                "pkg.Test.test_error ... ERROR",
                "ERROR: pkg.Test.test_error_header (pkg.Test)",
            ]
        ),
        "pkg.Test.test_multiline ... Internal Server Error: /example/\nok",
        (
            "pkg.Test.test_system ... System check identified no issues "
            "(0 silenced)\nok"
        ),
    ]
    sphinx = [
        "\n".join(
            [
                "\x1b[32mPASSED\x1b[0m docs/test_build.py::test_pass",
                "FAILED docs/test_build.py::test_fail - AssertionError: details",
                "SKIPPED [2] docs/test_build.py:12: optional",
                "docs/test_old.py::test_pass PASSED",
                "docs/test_old.py::test_skip SKIPPED",
            ]
        )
    ]
    for status in ("FAILED", "PASSED", "SKIPPED", "ERROR", "XFAIL"):
        sphinx.append(f"{status} path/test_mod.py::test_{status.lower()}")
        sphinx.append(f"path/test_mod.py::test_{status.lower()} {status}")
    return {
        "parse_log_django": django,
        "parse_log_pytest_v2": sphinx,
    }


def qualify() -> dict[str, Any]:
    official, source_hashes = load_official()
    local = {
        "parse_log_django": parse_django,
        "parse_log_pytest_v2": parse_pytest_v2,
    }
    rows = []
    for parser_name, samples in corpora().items():
        for index, log in enumerate(samples):
            expected = official[parser_name](log, None)
            observed = local[parser_name](log)
            rows.append(
                {
                    "parser": parser_name,
                    "case_index": index,
                    "log_sha256": sha256_text(log),
                    "expected_sha256": sha256_text(
                        json.dumps(expected, sort_keys=True, separators=(",", ":"))
                    ),
                    "observed_sha256": sha256_text(
                        json.dumps(observed, sort_keys=True, separators=(",", ":"))
                    ),
                    "pass": expected == observed,
                }
            )
    passed = bool(rows) and all(row["pass"] for row in rows)
    payload = {
        "schema_version": 1,
        "experiment_id": "E1-STRI-REASONINGBANK-P1-Q3-PARSER-QUALIFICATION-20260830",
        "created_at_utc": utcnow(),
        "source": {
            "package": "swebench==5.0.2",
            "wheel_sha256": WHEEL_SHA256,
            "member": MEMBER,
            "function_source_sha256": source_hashes,
        },
        "case_count": len(rows),
        "rows": rows,
        "all_cases_exact": passed,
        "decision": (
            "P1_Q3_PARSERS_QUALIFIED"
            if passed
            else "P1_Q3_PARSER_IMPLEMENTATION_HOLD"
        ),
        "credential_material_present": False,
        "scientific_boundary": {
            "q2_artifacts_modified": False,
            "q3_task_outcome_observed": False,
        },
    }
    file_sha = write_json(OUTPUT, payload)
    return {
        "decision": payload["decision"],
        "output": str(OUTPUT.relative_to(ROOT)),
        "file_sha256": file_sha,
        "case_count": len(rows),
    }


if __name__ == "__main__":
    print(json.dumps(qualify(), sort_keys=True))
