from __future__ import annotations

import json
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import (
    MalformedToolCallError,
    RunnerError,
    sha256_file,
    sha256_value,
)
from research_pipeline.appworld_constraint_compiler import (
    evaluate_binding,
    insert_fixture_row,
)

DIRECT_SEPARATOR = "__"


def _copy_or_link(source: Path, target: Path) -> None:
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(source.resolve(), target_is_directory=source.is_dir())


def prepare_appworld_runtime_root(
    appworld_root: Path,
    runtime_root: Path,
    *,
    family: dict[str, Any],
    arm: dict[str, Any],
    task_id: str,
) -> dict[str, Any]:
    """Materialize a private resettable AppWorld task; never commit runtime_root."""
    runtime_root.mkdir(parents=True, exist_ok=True)
    _copy_or_link(appworld_root / "data" / "base_dbs", runtime_root / "data" / "base_dbs")
    _copy_or_link(appworld_root / "data" / "api_docs", runtime_root / "data" / "api_docs")
    if (appworld_root / "data" / "datasets").exists():
        _copy_or_link(appworld_root / "data" / "datasets", runtime_root / "data" / "datasets")
    shutil.copy2(appworld_root / "data" / "version.txt", runtime_root / "data" / "version.txt")
    task_root = runtime_root / "data" / "tasks" / task_id
    if task_root.exists():
        raise RunnerError(f"Refusing to overwrite runtime task {task_id}.")
    db_root = task_root / "dbs"
    db_root.mkdir(parents=True)
    for source in sorted((appworld_root / "data" / "base_dbs").glob("*.db")):
        shutil.copy2(source, db_root / source.name)
    connections: dict[str, sqlite3.Connection] = {}
    try:
        for app in family["fixture"]["apps"]:
            connections[app] = sqlite3.connect(db_root / f"{app}.db")
        for row in family["fixture"]["rows"]:
            insert_fixture_row(connections[row["app"]], row)
        for connection in connections.values():
            connection.commit()
        for check in family["fixture"]["initial_checks"]:
            if not evaluate_binding(connections[check["app"]], check):
                raise RunnerError("Materialized AppWorld fixture failed its initial binding.")
    finally:
        for connection in connections.values():
            connection.close()
    exemplar = next((appworld_root / "data" / "tasks").glob("*/specs.json"))
    specs = json.loads(exemplar.read_text(encoding="utf-8"))
    specs["instruction"] = arm["task_instruction"]
    (task_root / "specs.json").write_text(
        json.dumps(specs, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    initial_hash = sha256_value({
        path.name: sha256_file(path) for path in sorted(db_root.glob("*.db"))
    })
    return {
        "task_id": task_id,
        "runtime_root": str(runtime_root),
        "initial_snapshot_sha256": initial_hash,
        "instruction_sha256": sha256_value(arm["task_instruction"]),
    }


class AppWorldToolWorld:
    def __init__(
        self,
        *,
        runtime_root: Path,
        task_id: str,
        experiment_name: str,
        seed: int,
        allowed_apps: set[str] | None = None,
    ) -> None:
        os.environ["APPWORLD_ROOT"] = str(runtime_root)
        from appworld import AppWorld

        self._world = AppWorld(
            task_id=task_id,
            experiment_name=experiment_name,
            load_ground_truth=False,
            include_direct_functions=True,
            direct_function_separator=DIRECT_SEPARATOR,
            max_interactions=12,
            max_api_calls_per_interaction=12,
            random_seed=seed,
        )
        self.output_db_root = Path(self._world.output_db_home_path_on_disk)
        self._tools = []
        allowed_prefixes = (
            None
            if allowed_apps is None
            else tuple(f"{app}{DIRECT_SEPARATOR}" for app in sorted(
                {*allowed_apps, "api_docs", "supervisor"}
            ))
        )
        for document in self._world.task.api_docs.function_calling():
            function = document["function"]
            if allowed_prefixes is not None and not function["name"].startswith(
                allowed_prefixes
            ):
                continue
            self._tools.append({
                "type": "function",
                "name": function["name"],
                "description": function.get("description", ""),
                "parameters": function["parameters"],
            })

    @property
    def tools(self) -> list[dict[str, Any]]:
        return self._tools

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        if name.count(DIRECT_SEPARATOR) != 1:
            raise MalformedToolCallError(f"Invalid AppWorld function name: {name}")
        encoded = repr(arguments)
        return self._world.execute(f"print({name}(**{encoded}))")

    def save_and_evaluate(self, arm: dict[str, Any]) -> dict[str, Any]:
        self._world.save()
        target: dict[str, bool] = {}
        non_target: dict[str, bool] = {}
        connections: dict[str, sqlite3.Connection] = {}
        try:
            for constraint in arm["constraints"]:
                binding = constraint["evaluator_binding"]
                app = binding["app"]
                if app not in connections:
                    connections[app] = sqlite3.connect(self.output_db_root / f"{app}.db")
                passed = evaluate_binding(connections[app], binding)
                destination = target if constraint["role"] == "TARGET" else non_target
                destination[constraint["constraint_id"]] = passed
        finally:
            for connection in connections.values():
                connection.close()
        return {
            "target": target,
            "non_target": non_target,
            "target_success": all(target.values()),
            "non_target_preservation": (
                sum(non_target.values()) / len(non_target) if non_target else 1.0
            ),
        }

    def close(self) -> None:
        self._world.close()
