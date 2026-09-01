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
MEASUREMENT_FAILURE_CLASS = "MEASUREMENT_INTERFACE_FAIL_CLOSED"


class MeasurementInterfaceError(RunnerError):
    """Fail-closed measurement error; never reinterpret as an agent capability result."""


def _sqlite_inventory(
    path: Path, *, required_tables: set[str] | None = None
) -> tuple[sqlite3.Connection, dict[str, Any]]:
    """Open an existing SQLite DB read-only and validate its schema/integrity."""
    if not path.is_file():
        raise MeasurementInterfaceError(f"{MEASUREMENT_FAILURE_CLASS}: missing DB {path}")
    size = path.stat().st_size
    if size <= 0:
        raise MeasurementInterfaceError(f"{MEASUREMENT_FAILURE_CLASS}: empty DB {path}")
    uri = f"file:{path.resolve().as_posix()}?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        if not integrity or integrity[0] != "ok":
            connection.close()
            raise MeasurementInterfaceError(
                f"{MEASUREMENT_FAILURE_CLASS}: integrity check failed for {path}"
            )
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        missing = set(required_tables or set()) - tables
        if missing:
            connection.close()
            raise MeasurementInterfaceError(
                f"{MEASUREMENT_FAILURE_CLASS}: missing tables {sorted(missing)} in {path}"
            )
        return connection, {
            "path": str(path),
            "bytes": size,
            "sha256": sha256_file(path),
            "integrity_check": "ok",
            "table_count": len(tables),
            "tables": sorted(tables),
        }
    except sqlite3.DatabaseError as exc:
        raise MeasurementInterfaceError(
            f"{MEASUREMENT_FAILURE_CLASS}: invalid SQLite DB {path}: {type(exc).__name__}"
        ) from exc


def materialize_appworld_measurement_state(
    *,
    source_db_root: Path,
    changes_db_root: Path,
    measurement_db_root: Path,
    required_tables_by_app: dict[str, set[str]],
) -> dict[str, Any]:
    """Apply AppWorld's official changes format to frozen task-input full DBs.

    AppWorld saves task outputs as ``*.jsonl`` changes.  The scientific task input
    in this project contains fixture rows beyond the public base DB, so recovery
    must apply those official changes to the frozen task-input DB, not to a fresh
    public base DB.  The official ``apply_db_changes`` function defines the change
    semantics; this adapter only provides the correct starting snapshot and then
    validates the materialized full DB fail-closed.
    """
    if measurement_db_root.exists() and any(measurement_db_root.iterdir()):
        raise MeasurementInterfaceError(
            f"{MEASUREMENT_FAILURE_CLASS}: refusing to overwrite measurement state "
            f"{measurement_db_root}"
        )
    measurement_db_root.mkdir(parents=True, exist_ok=True)
    from appworld.apps.lib.models.db import apply_db_changes

    manifest: dict[str, Any] = {
        "failure_class": MEASUREMENT_FAILURE_CLASS,
        "source_db_root": str(source_db_root),
        "changes_db_root": str(changes_db_root),
        "measurement_db_root": str(measurement_db_root),
        "apps": {},
    }
    for app in sorted(required_tables_by_app):
        required_tables = required_tables_by_app[app]
        source = source_db_root / f"{app}.db"
        source_connection, source_info = _sqlite_inventory(
            source, required_tables=required_tables
        )
        source_connection.close()
        changes = changes_db_root / f"{app}.jsonl"
        if not changes.is_file():
            raise MeasurementInterfaceError(
                f"{MEASUREMENT_FAILURE_CLASS}: missing AppWorld changes file {changes}"
            )
        target = measurement_db_root / f"{app}.db"
        shutil.copy2(source, target)
        try:
            connection = sqlite3.connect(target)
            try:
                apply_db_changes(connection, str(changes))
            finally:
                connection.close()
        except Exception as exc:
            raise MeasurementInterfaceError(
                f"{MEASUREMENT_FAILURE_CLASS}: failed to apply AppWorld changes for {app}: "
                f"{type(exc).__name__}"
            ) from exc
        target_connection, target_info = _sqlite_inventory(
            target, required_tables=required_tables
        )
        target_connection.close()
        manifest["apps"][app] = {
            "required_tables": sorted(required_tables),
            "source": source_info,
            "changes_path": str(changes),
            "changes_bytes": changes.stat().st_size,
            "changes_sha256": sha256_file(changes),
            "measurement": target_info,
        }
    manifest["content_sha256"] = sha256_value(manifest)
    return manifest


def evaluate_arm_from_materialized_state(
    *,
    arm: dict[str, Any],
    source_db_root: Path,
    changes_db_root: Path,
    measurement_db_root: Path,
) -> dict[str, Any]:
    required_tables_by_app: dict[str, set[str]] = {}
    for constraint in arm["constraints"]:
        binding = constraint["evaluator_binding"]
        required_tables_by_app.setdefault(binding["app"], set()).add(binding["table"])
    measurement = materialize_appworld_measurement_state(
        source_db_root=source_db_root,
        changes_db_root=changes_db_root,
        measurement_db_root=measurement_db_root,
        required_tables_by_app=required_tables_by_app,
    )
    target: dict[str, bool] = {}
    non_target: dict[str, bool] = {}
    connections: dict[str, sqlite3.Connection] = {}
    try:
        for constraint in arm["constraints"]:
            binding = constraint["evaluator_binding"]
            app = binding["app"]
            if app not in connections:
                connections[app], _ = _sqlite_inventory(
                    measurement_db_root / f"{app}.db",
                    required_tables=required_tables_by_app[app],
                )
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
        "measurement": measurement,
    }


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
        self.source_db_root = runtime_root / "data" / "tasks" / task_id / "dbs"
        self.measurement_db_root = self.output_db_root.parent / "measurement-full-dbs"
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
        return evaluate_arm_from_materialized_state(
            arm=arm,
            source_db_root=self.source_db_root,
            changes_db_root=self.output_db_root,
            measurement_db_root=self.measurement_db_root,
        )

    def close(self) -> None:
        self._world.close()
