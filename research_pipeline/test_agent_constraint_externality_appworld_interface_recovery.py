from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
import warnings
from pathlib import Path

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    AppWorldToolWorld,
    MeasurementInterfaceError,
    _sqlite_inventory,
    materialize_appworld_measurement_state,
    prepare_appworld_runtime_root,
)
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
APPWORLD_ROOT = ROOT / "cache/substrates/appworld-official-20260831"
BUNDLE = ROOT / "generated/agent-constraint-externality-appworld-pre-f0_5-protected-20260831.bundle"


class AppWorldInterfaceRecoveryTests(unittest.TestCase):
    def _source(self, root: Path, *, include_table: bool = True) -> Path:
        source = root / "source"
        source.mkdir()
        path = source / "gmail.db"
        connection = sqlite3.connect(path)
        try:
            if include_table:
                connection.execute(
                    "CREATE TABLE emails (id INTEGER PRIMARY KEY, subject TEXT, status TEXT)"
                )
                connection.execute(
                    "INSERT INTO emails (id, subject, status) VALUES (1, 'alpha', 'old')"
                )
                connection.commit()
            else:
                connection.execute("CREATE TABLE other (id INTEGER PRIMARY KEY)")
                connection.commit()
        finally:
            connection.close()
        return source

    def _changes(self, root: Path, rows: list[object]) -> Path:
        changes = root / "changes"
        changes.mkdir()
        with (changes / "gmail.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row) + "\n")
        return changes

    def _rows(self, path: Path) -> list[tuple[object, ...]]:
        connection, _ = _sqlite_inventory(path, required_tables={"emails"})
        try:
            return connection.execute(
                "SELECT id, subject, status FROM emails ORDER BY id"
            ).fetchall()
        finally:
            connection.close()

    def test_identity_reconstruction_uses_frozen_task_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self._source(root)
            changes = self._changes(root, [])
            measurement = root / "measurement"
            result = materialize_appworld_measurement_state(
                source_db_root=source,
                changes_db_root=changes,
                measurement_db_root=measurement,
                required_tables_by_app={"gmail": {"emails"}},
            )
            self.assertEqual(
                self._rows(measurement / "gmail.db"), [(1, "alpha", "old")]
            )
            self.assertEqual(result["apps"]["gmail"]["changes_bytes"], 0)
            self.assertEqual(result["apps"]["gmail"]["measurement"]["integrity_check"], "ok")

    def test_insert_update_delete_follow_official_changes_semantics(self) -> None:
        changes_rows = [
            [
                "INSERT INTO emails (id, subject, status) VALUES (?, ?, ?)",
                [2, "beta", "new"],
                False,
            ],
            ["UPDATE emails SET status = ? WHERE id = ?", ["updated", 2], False],
            ["DELETE FROM emails WHERE id = ?", [1], False],
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self._source(root)
            changes = self._changes(root, changes_rows)
            measurement = root / "measurement"
            materialize_appworld_measurement_state(
                source_db_root=source,
                changes_db_root=changes,
                measurement_db_root=measurement,
                required_tables_by_app={"gmail": {"emails"}},
            )
            self.assertEqual(
                self._rows(measurement / "gmail.db"), [(2, "beta", "updated")]
            )

    def test_missing_source_fails_without_creating_database(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            changes = self._changes(root, [])
            measurement = root / "measurement"
            with self.assertRaises(MeasurementInterfaceError):
                materialize_appworld_measurement_state(
                    source_db_root=source,
                    changes_db_root=changes,
                    measurement_db_root=measurement,
                    required_tables_by_app={"gmail": {"emails"}},
                )
            self.assertFalse((source / "gmail.db").exists())
            self.assertFalse((measurement / "gmail.db").exists())

    def test_readonly_inventory_does_not_create_missing_database(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "never-create.db"
            with self.assertRaises(MeasurementInterfaceError):
                _sqlite_inventory(path, required_tables={"emails"})
            self.assertFalse(path.exists())

    def test_zero_byte_database_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            path = source / "gmail.db"
            path.touch()
            changes = self._changes(root, [])
            with self.assertRaises(MeasurementInterfaceError):
                materialize_appworld_measurement_state(
                    source_db_root=source,
                    changes_db_root=changes,
                    measurement_db_root=root / "measurement",
                    required_tables_by_app={"gmail": {"emails"}},
                )
            self.assertEqual(path.stat().st_size, 0)

    def test_corrupt_database_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "gmail.db").write_bytes(b"not sqlite")
            changes = self._changes(root, [])
            with self.assertRaises(MeasurementInterfaceError):
                materialize_appworld_measurement_state(
                    source_db_root=source,
                    changes_db_root=changes,
                    measurement_db_root=root / "measurement",
                    required_tables_by_app={"gmail": {"emails"}},
                )

    def test_missing_required_table_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self._source(root, include_table=False)
            changes = self._changes(root, [])
            with self.assertRaises(MeasurementInterfaceError):
                materialize_appworld_measurement_state(
                    source_db_root=source,
                    changes_db_root=changes,
                    measurement_db_root=root / "measurement",
                    required_tables_by_app={"gmail": {"emails"}},
                )

    def test_malformed_changes_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self._source(root)
            changes = root / "changes"
            changes.mkdir()
            (changes / "gmail.jsonl").write_text("not-json\n", encoding="utf-8")
            with self.assertRaises(MeasurementInterfaceError):
                materialize_appworld_measurement_state(
                    source_db_root=source,
                    changes_db_root=changes,
                    measurement_db_root=root / "measurement",
                    required_tables_by_app={"gmail": {"emails"}},
                )

    def test_missing_changes_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self._source(root)
            changes = root / "changes"
            changes.mkdir()
            with self.assertRaises(MeasurementInterfaceError):
                materialize_appworld_measurement_state(
                    source_db_root=source,
                    changes_db_root=changes,
                    measurement_db_root=root / "measurement",
                    required_tables_by_app={"gmail": {"emails"}},
                )

    def test_reconstruction_is_logically_repeatable(self) -> None:
        rows = [
            ["UPDATE emails SET status = ? WHERE id = ?", ["updated", 1], False]
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self._source(root)
            changes = self._changes(root, rows)
            observed = []
            for name in ("measurement-a", "measurement-b"):
                target = root / name
                materialize_appworld_measurement_state(
                    source_db_root=source,
                    changes_db_root=changes,
                    measurement_db_root=target,
                    required_tables_by_app={"gmail": {"emails"}},
                )
                observed.append(self._rows(target / "gmail.db"))
            self.assertEqual(observed[0], observed[1])
            self.assertEqual(observed[0], [(1, "alpha", "updated")])

    def test_actual_appworld_changes_output_is_materialized_without_empty_db(self) -> None:
        spec = load_protected_spec(BUNDLE)
        family = next(item for item in spec["families"] if item["family_id"] == "ACE-FG-05")
        arm = next(item for item in family["arms"] if item["coupling_level"] == "LOW")
        with tempfile.TemporaryDirectory() as directory, warnings.catch_warnings():
            warnings.simplefilter("ignore")
            runtime = Path(directory)
            prepare_appworld_runtime_root(
                APPWORLD_ROOT,
                runtime,
                family=family,
                arm=arm,
                task_id="aceinterfacetest_1",
            )
            world = AppWorldToolWorld(
                runtime_root=runtime,
                task_id="aceinterfacetest_1",
                experiment_name="ace-interface-test",
                seed=1,
                allowed_apps=set(family["fixture"]["apps"]),
            )
            try:
                result = world.save_and_evaluate(arm)
                self.assertIn("measurement", result)
                self.assertTrue((world.output_db_root / "gmail.jsonl").is_file())
                self.assertFalse((world.output_db_root / "gmail.db").exists())
                measurement_db = world.measurement_db_root / "gmail.db"
                self.assertGreater(measurement_db.stat().st_size, 0)
                connection, inventory = _sqlite_inventory(
                    measurement_db, required_tables={"emails"}
                )
                connection.close()
                self.assertEqual(inventory["integrity_check"], "ok")
            finally:
                world.close()


if __name__ == "__main__":
    unittest.main()
