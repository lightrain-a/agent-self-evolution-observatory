from __future__ import annotations

import json
import os
import re
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
SUPERVISOR_SPECS_EXEMPLAR_TASK_ID = "5238afc_1"
SUPERVISOR_MAIN_USER_ID = 99
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


def _is_file_gmail_target(constraint: dict[str, Any]) -> bool:
    return (
        constraint.get("role") == "TARGET"
        and constraint.get("evaluator_binding", {}).get("app") == "gmail"
        and constraint.get("semantic_description")
        == "Send exactly one email to the designated recipient with the two designated source files attached, preserving their bytes."
    )


def _evaluate_file_gmail_target(
    *,
    arm: dict[str, Any],
    constraint: dict[str, Any],
    connections: dict[str, sqlite3.Connection],
) -> bool:
    """Evaluate the complete semantic email obligation, not only its subject row.

    The protected family spec historically used one SQLite binding for the target,
    which was sufficient to locate the sent email but did not prove recipient or
    attachment correctness.  The scientific constraint is semantic, so the runtime
    evaluator closes that gap with deterministic checks over AppWorld state.
    """
    match = re.search(
        r"^Email (?P<recipient>\S+) with subject (?P<subject>\S+) and attach "
        r"(?P<first>\S+) and (?P<second>\S+) from (?P<directory>~/[^.]+)\.",
        arm["task_instruction"],
    )
    if match is None:
        raise MeasurementInterfaceError(
            f"{MEASUREMENT_FAILURE_CLASS}: cannot parse File/Gmail target instruction"
        )
    gmail = connections["gmail"]
    file_system = connections["file_system"]
    binding = constraint["evaluator_binding"]
    if not evaluate_binding(gmail, binding):
        return False
    where = binding["where"]
    clauses = " AND ".join(f'"{column}" = ?' for column in where)
    email_rows = gmail.execute(
        f'SELECT id, recipient_ids, subject FROM emails WHERE {clauses}',
        list(where.values()),
    ).fetchall()
    if len(email_rows) != 1:
        return False
    email_id, recipient_ids_raw, subject = email_rows[0]
    if str(subject) != match.group("subject"):
        return False
    recipient_row = gmail.execute(
        "SELECT id FROM users WHERE email = ?", (match.group("recipient"),)
    ).fetchone()
    if recipient_row is None:
        return False
    try:
        recipient_ids = json.loads(recipient_ids_raw)
    except (TypeError, json.JSONDecodeError):
        return False
    if recipient_ids != [int(recipient_row[0])]:
        return False

    expected_attachments: dict[str, str] = {}
    for file_name in (match.group("first"), match.group("second")):
        tilde_path = match.group("directory").rstrip("/") + "/" + file_name
        source_row = file_system.execute(
            "SELECT content FROM files WHERE tilde_path = ?", (tilde_path,)
        ).fetchone()
        if source_row is None:
            return False
        expected_attachments[file_name] = str(source_row[0])
    attachment_rows = gmail.execute(
        "SELECT file_name, file_content FROM attachments WHERE email_id = ? ORDER BY file_name",
        (email_id,),
    ).fetchall()
    observed_attachments = {str(name): str(content) for name, content in attachment_rows}
    return (
        len(attachment_rows) == len(expected_attachments)
        and observed_attachments == expected_attachments
    )


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
        if _is_file_gmail_target(constraint):
            required_tables_by_app.setdefault("gmail", set()).update(
                {"emails", "attachments", "users"}
            )
            required_tables_by_app.setdefault("file_system", set()).add("files")
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
            if _is_file_gmail_target(constraint):
                for required_app in ("gmail", "file_system"):
                    if required_app not in connections:
                        connections[required_app], _ = _sqlite_inventory(
                            measurement_db_root / f"{required_app}.db",
                            required_tables=required_tables_by_app[required_app],
                        )
                passed = _evaluate_file_gmail_target(
                    arm=arm, constraint=constraint, connections=connections
                )
            else:
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

    # AppWorld base_dbs intentionally contain no active supervisor task context.
    # ACE fixtures are owned by base main user 99 (Aaron Burton), so the custom
    # supervisor must be derived from that same main user rather than borrowed
    # from an unrelated official task.  This keeps ~ paths, app ownership, Gmail
    # sender_id, and note/todo ownership aligned with one identity.
    exemplar_specs_path = (
        appworld_root / "data" / "tasks" / SUPERVISOR_SPECS_EXEMPLAR_TASK_ID / "specs.json"
    )
    if not exemplar_specs_path.is_file():
        raise RunnerError("Frozen AppWorld specs exemplar is unavailable.")
    specs = json.loads(exemplar_specs_path.read_text(encoding="utf-8"))
    specs["instruction"] = arm["task_instruction"]

    admin_connection = sqlite3.connect(db_root / "admin.db")
    try:
        main_user_row = admin_connection.execute(
            "SELECT sex, record_hash, id, first_name, last_name, email, phone_number, birthday "
            "FROM main_users WHERE id = ?",
            (SUPERVISOR_MAIN_USER_ID,),
        ).fetchone()
        if main_user_row is None:
            raise RunnerError("Frozen supervisor main user 99 is missing from admin DB.")
        (
            supervisor_sex,
            supervisor_record_hash,
            supervisor_id,
            supervisor_first_name,
            supervisor_last_name,
            supervisor_email,
            supervisor_phone,
            supervisor_birthday,
        ) = main_user_row
        password_rows = admin_connection.execute(
            "SELECT account_name, password FROM account_passwords WHERE main_user_id = ?",
            (SUPERVISOR_MAIN_USER_ID,),
        ).fetchall()
        account_passwords = {str(name): str(password) for name, password in password_rows}
        address_rows = admin_connection.execute(
            "SELECT ua.name, ga.street_address, ga.city, ga.state, ga.country, ga.zip_code "
            "FROM user_addresses ua JOIN global_addresses ga ON ga.id = ua.global_address_id "
            "WHERE ua.main_user_id = ? ORDER BY ua.id",
            (SUPERVISOR_MAIN_USER_ID,),
        ).fetchall()
        card_rows = admin_connection.execute(
            "SELECT card_name, owner_name, card_number, expiry_year, expiry_month, cvv_number "
            "FROM payment_cards WHERE main_user_id = ? ORDER BY id",
            (SUPERVISOR_MAIN_USER_ID,),
        ).fetchall()
    finally:
        admin_connection.close()

    specs["supervisor"] = {
        "first_name": str(supervisor_first_name),
        "last_name": str(supervisor_last_name),
        "email": str(supervisor_email),
        "phone_number": str(supervisor_phone),
    }
    supervisor_db = db_root / "supervisor.db"
    supervisor_connection = sqlite3.connect(supervisor_db)
    try:
        supervisor_connection.execute(
            "INSERT INTO supervisors (sex, record_hash, id, first_name, last_name, email, phone_number, birthday) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                supervisor_sex,
                supervisor_record_hash,
                supervisor_id,
                supervisor_first_name,
                supervisor_last_name,
                supervisor_email,
                supervisor_phone,
                supervisor_birthday,
            ),
        )
        supervisor_connection.execute(
            "INSERT INTO tasks (status, record_hash, id, supervisor_id, instruction, answer) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (None, None, 1, supervisor_id, arm["task_instruction"], json.dumps("<<NOT_GIVEN>>")),
        )
        for index, (account_name, password) in enumerate(sorted(account_passwords.items()), start=1):
            supervisor_connection.execute(
                "INSERT INTO account_passwords (record_hash, id, supervisor_id, account_name, password) "
                "VALUES (?, ?, ?, ?, ?)",
                (None, index, supervisor_id, account_name, password),
            )
        for index, row in enumerate(address_rows, start=1):
            supervisor_connection.execute(
                "INSERT INTO addresses (name, record_hash, id, supervisor_id, street_address, city, state, country, zip_code) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (row[0], None, index, supervisor_id, row[1], row[2], row[3], row[4], row[5]),
            )
        for index, row in enumerate(card_rows, start=1):
            supervisor_connection.execute(
                "INSERT INTO payment_cards (card_name, record_hash, id, supervisor_id, owner_name, card_number, expiry_year, expiry_month, cvv_number) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (row[0], None, index, supervisor_id, row[1], row[2], row[3], row[4], row[5]),
            )
        supervisor_connection.commit()
        active_tasks = supervisor_connection.execute(
            "SELECT instruction FROM tasks WHERE supervisor_id = ?", (supervisor_id,)
        ).fetchall()
        if len(active_tasks) != 1 or active_tasks[0][0] != arm["task_instruction"]:
            raise RunnerError("Materialized AppWorld active-task binding is invalid.")
    finally:
        supervisor_connection.close()

    for app in family["fixture"]["apps"]:
        if app not in account_passwords:
            raise RunnerError(f"Supervisor lacks an account password for required app {app}.")
        app_connection = sqlite3.connect(db_root / f"{app}.db")
        try:
            account_row = app_connection.execute(
                "SELECT id, password FROM users WHERE email = ?", (supervisor_email,)
            ).fetchone()
        finally:
            app_connection.close()
        if (
            account_row is None
            or int(account_row[0]) != SUPERVISOR_MAIN_USER_ID
            or str(account_row[1]) != account_passwords[app]
        ):
            raise RunnerError(
                f"Supervisor credential/ownership does not match required app user 99 for {app}."
            )

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
        max_interactions: int = 12,
    ) -> None:
        os.environ["APPWORLD_ROOT"] = str(runtime_root)
        from appworld import AppWorld

        self._world = AppWorld(
            task_id=task_id,
            experiment_name=experiment_name,
            load_ground_truth=False,
            include_direct_functions=True,
            direct_function_separator=DIRECT_SEPARATOR,
            max_interactions=max_interactions,
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

    def save_state(self) -> None:
        """Persist AppWorld's current task changes without opening scientific outcomes."""
        self._world.save()

    def save_and_evaluate(self, arm: dict[str, Any]) -> dict[str, Any]:
        self.save_state()
        return evaluate_arm_from_materialized_state(
            arm=arm,
            source_db_root=self.source_db_root,
            changes_db_root=self.output_db_root,
            measurement_db_root=self.measurement_db_root,
        )

    def close(self) -> None:
        self._world.close()
