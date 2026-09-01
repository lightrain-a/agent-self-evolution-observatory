"""Pinned SWE-bench 5.0.2 Python log-parser compatibility for Qwen STRI."""

from __future__ import annotations

import re
from collections.abc import Callable

SWEBENCH_VERSION = "5.0.2"
SWEBENCH_WHEEL_SHA256 = "b7f0416a1e686eca22c2f749b5f816685a202835032f6683080e2b53545bbb62"
OFFICIAL_PYTHON_PARSER_SHA256 = "cd56156414f8327221e525665ace9b184f7d73e83b272d9eb3f545fb17c2d9bc"
STATUSES = ("FAILED", "PASSED", "SKIPPED", "ERROR", "XFAIL", "XPASS")
PASSING = {"PASSED", "XFAIL"}
MAINTAINED = {"PASSED", "XFAIL", "SKIPPED"}
_SKIP_SUMMARY_COUNT = re.compile(r"^\[\d+\]$")


def _is_skip_summary(status: str, name: str) -> bool:
    return status == "SKIPPED" and bool(_SKIP_SUMMARY_COUNT.match(name))


def parse_log_pytest(log: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in log.split("\n"):
        if any(line.startswith(status) for status in STATUSES):
            if line.startswith("FAILED"):
                line = line.replace(" - ", " ")
            parts = line.split()
            if len(parts) <= 1 or _is_skip_summary(parts[0], parts[1]):
                continue
            result[parts[1]] = parts[0]
    return result


def parse_log_pytest_options(log: str) -> dict[str, str]:
    option_pattern = re.compile(r"(.*?)\[(.*)\]")
    result: dict[str, str] = {}
    for line in log.split("\n"):
        if not any(line.startswith(status) for status in STATUSES):
            continue
        if line.startswith("FAILED"):
            line = line.replace(" - ", " ")
        parts = line.split()
        if len(parts) <= 1 or _is_skip_summary(parts[0], parts[1]):
            continue
        match = option_pattern.search(parts[1])
        if match:
            main, option = match.groups()
            if option.startswith("/") and not option.startswith("//") and "*" not in option:
                option = "/" + option.split("/")[-1]
            name = f"{main}[{option}]"
        else:
            name = parts[1]
        result[name] = parts[0]
    return result


def parse_log_django(log: str) -> dict[str, str]:
    result: dict[str, str] = {}
    previous = None
    for raw in log.split("\n"):
        line = raw.strip()
        if "--version is equivalent to version" in line:
            result["--version is equivalent to version"] = "PASSED"
        if " ... " in line:
            previous = line.split(" ... ")[0]
        for suffix in (" ... ok", " ... OK", " ...  OK"):
            if line.endswith(suffix):
                if line.startswith("Applying sites.0002_alter_domain_unique...test_no_migrations"):
                    line = line.split("...", 1)[-1].strip()
                result[line.rsplit(suffix, 1)[0]] = "PASSED"
                break
        if " ... skipped" in line:
            result[line.split(" ... skipped")[0]] = "SKIPPED"
        if line.endswith(" ... FAIL"):
            result[line.split(" ... FAIL")[0]] = "FAILED"
        if line.startswith("FAIL:"):
            result[line.split()[1].strip()] = "FAILED"
        if line.endswith(" ... ERROR"):
            result[line.split(" ... ERROR")[0]] = "ERROR"
        if line.startswith("ERROR:"):
            result[line.split()[1].strip()] = "ERROR"
        if line.lstrip().startswith("ok") and previous is not None:
            result[previous] = "PASSED"
    patterns = [
        r"^(.*?)\s\.\.\.\sTesting\ against\ Django\ installed\ in\ ((?s:.*?))\ silenced\)\.\nok$",
        r"^(.*?)\s\.\.\.\sInternal\ Server\ Error:\ \/(.*)\/\nok$",
        r"^(.*?)\s\.\.\.\sSystem check identified no issues \(0 silenced\)\nok$",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, log, re.MULTILINE):
            result[match.group(1)] = "PASSED"
    return result


def parse_log_pytest_v2(log: str) -> dict[str, str]:
    result: dict[str, str] = {}
    escapes = "".join(chr(char) for char in range(1, 32))
    translator = str.maketrans("", "", escapes)
    for line in log.split("\n"):
        line = re.sub(r"\[(\d+)m", "", line).translate(translator)
        if any(line.startswith(status) for status in STATUSES):
            if line.startswith("FAILED"):
                line = line.split(" - ", 1)[0]
            parts = line.split()
            if len(parts) >= 2 and not _is_skip_summary(parts[0], parts[1]):
                result[" ".join(parts[1:])] = parts[0]
        elif any(line.endswith(status) for status in STATUSES):
            parts = line.split()
            if len(parts) >= 2:
                result[" ".join(parts[:-1])] = parts[-1]
    return result


def parse_log_seaborn(log: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in log.split("\n"):
        parts = line.split()
        if len(parts) < 2:
            continue
        if line.startswith("FAILED"):
            result[parts[1]] = "FAILED"
        elif " PASSED " in line and parts[1] == "PASSED":
            result[parts[0]] = "PASSED"
        elif line.startswith("PASSED"):
            result[parts[1]] = "PASSED"
    return result


def parse_log_sympy(log: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.findall(r"(_*) (.*)\.py:(.*) (_*)", log):
        result[f"{match[1]}.py:{match[2]}"] = "FAILED"
    for raw in log.split("\n"):
        line = raw.strip()
        if not line.startswith("test_"):
            continue
        if line.endswith(" E"):
            result[line.split()[0]] = "ERROR"
        if line.endswith(" F"):
            result[line.split()[0]] = "FAILED"
        if line.endswith(" ok"):
            result[line.split()[0]] = "PASSED"
    return result


def parse_log_matplotlib(log: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in log.split("\n"):
        line = line.replace("MouseButton.LEFT", "1").replace("MouseButton.RIGHT", "3")
        if any(line.startswith(status) for status in STATUSES):
            if line.startswith("FAILED"):
                line = line.replace(" - ", " ")
            parts = line.split()
            if len(parts) <= 1 or _is_skip_summary(parts[0], parts[1]):
                continue
            result[parts[1]] = parts[0]
    return result


PARSERS: dict[str, Callable[[str], dict[str, str]]] = {
    "parse_log_astropy": parse_log_pytest_v2,
    "parse_log_django": parse_log_django,
    "parse_log_matplotlib": parse_log_matplotlib,
    "parse_log_seaborn": parse_log_seaborn,
    "parse_log_flask": parse_log_pytest,
    "parse_log_requests": parse_log_pytest_options,
    "parse_log_xarray": parse_log_pytest,
    "parse_log_pylint": parse_log_pytest_options,
    "parse_log_pytest": parse_log_pytest,
    "parse_log_scikit": parse_log_pytest_v2,
    "parse_log_sphinx": parse_log_pytest_v2,
    "parse_log_sympy": parse_log_sympy,
}


def parse_status_map(parser_family: str, raw_output: str) -> dict[str, str]:
    if parser_family not in PARSERS:
        raise RuntimeError(f"unsupported pinned SWE-bench parser: {parser_family}")
    start = ">>>>> Start Test Output"
    end = ">>>>> End Test Output"
    sliced = raw_output
    if start in raw_output and end in raw_output:
        sliced = raw_output.split(start, 1)[1].split(end, 1)[0]
    return PARSERS[parser_family](sliced)


def grade_status_map(
    status_map: dict[str, str],
    fail_to_pass: list[str],
    pass_to_pass: list[str],
) -> dict[str, object]:
    f2p = {case: status_map.get(case, "MISSING") for case in fail_to_pass}
    p2p = {case: status_map.get(case, "MISSING") for case in pass_to_pass}
    all_f2p = bool(f2p) and all(value in PASSING for value in f2p.values())
    all_p2p = all(value in MAINTAINED for value in p2p.values())
    return {
        "FAIL_TO_PASS": f2p,
        "PASS_TO_PASS": p2p,
        "all_fail_to_pass": all_f2p,
        "all_pass_to_pass": all_p2p,
        "resolved": bool(status_map) and all_f2p and all_p2p,
    }
