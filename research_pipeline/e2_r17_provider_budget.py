from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any


SCHEMA_VERSION = "1.0"


class ProviderBudgetExceeded(RuntimeError):
    """Raised before provider I/O when a frozen call ceiling would be exceeded."""


class ProviderBudgetBindingError(RuntimeError):
    """Raised when a persisted ledger does not match the frozen execution binding."""


@dataclass(frozen=True)
class ProviderBudgetClaim:
    claim_id: int
    unit_id: str
    unit_call_index: int
    total_claimed_after: int
    per_unit_limit: int
    total_limit: int
    claimed_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderBudgetSnapshot:
    ledger_path: str
    contract_sha256: str
    authorization_sha256: str
    total_limit: int
    per_unit_limit: int
    total_claimed: int
    unit_claimed: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProviderBudgetLedger:
    """SQLite-backed fail-closed provider-call budget ledger.

    A claim is committed transactionally *before* provider I/O. Claims are never
    released, even when the subsequent provider request errors or the process
    crashes. This deliberately over-counts ambiguous calls so a resume cannot
    reset or reuse budget that may already have reached the provider.

    SQLite ``BEGIN IMMEDIATE`` serializes concurrent claims from the per-stream
    actor workers. The ledger is bound to one exact contract/authorization pair
    and fixed global/per-unit limits; any drift fails closed.
    """

    def __init__(
        self,
        *,
        path: Path,
        contract_sha256: str,
        authorization_sha256: str,
        total_limit: int,
        per_unit_limit: int,
        allow_create: bool,
    ) -> None:
        if total_limit <= 0 or per_unit_limit <= 0:
            raise ValueError("provider budget limits must be positive")
        self.path = Path(path)
        self.contract_sha256 = str(contract_sha256)
        self.authorization_sha256 = str(authorization_sha256)
        self.total_limit = int(total_limit)
        self.per_unit_limit = int(per_unit_limit)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        existed = self.path.exists()
        if not existed and not allow_create:
            raise ProviderBudgetBindingError(f"provider budget ledger does not exist: {self.path}")
        self._initialize_or_validate(allow_create=allow_create)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.path), timeout=30.0, isolation_level=None)
        connection.execute("PRAGMA busy_timeout=30000")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize_or_validate(self, *, allow_create: bool) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS claims (
                    claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id TEXT NOT NULL,
                    unit_call_index INTEGER NOT NULL,
                    claimed_at_utc TEXT NOT NULL,
                    UNIQUE(unit_id, unit_call_index)
                )
                """
            )
            current = dict(connection.execute("SELECT key, value FROM metadata").fetchall())
            expected = {
                "schema_version": SCHEMA_VERSION,
                "contract_sha256": self.contract_sha256,
                "authorization_sha256": self.authorization_sha256,
                "total_limit": str(self.total_limit),
                "per_unit_limit": str(self.per_unit_limit),
            }
            if not current:
                if not allow_create:
                    connection.execute("ROLLBACK")
                    raise ProviderBudgetBindingError("refusing to initialize missing provider budget metadata on resume")
                connection.executemany(
                    "INSERT INTO metadata(key, value) VALUES (?, ?)", expected.items()
                )
            elif current != expected:
                connection.execute("ROLLBACK")
                raise ProviderBudgetBindingError(
                    f"provider budget binding drift: observed={current!r}; expected={expected!r}"
                )
            connection.execute("COMMIT")

    def claim(self, unit_id: str) -> ProviderBudgetClaim:
        unit_id = str(unit_id)
        if not unit_id:
            raise ValueError("provider budget unit_id is required")
        claimed_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            metadata = dict(connection.execute("SELECT key, value FROM metadata").fetchall())
            expected = {
                "schema_version": SCHEMA_VERSION,
                "contract_sha256": self.contract_sha256,
                "authorization_sha256": self.authorization_sha256,
                "total_limit": str(self.total_limit),
                "per_unit_limit": str(self.per_unit_limit),
            }
            if metadata != expected:
                connection.execute("ROLLBACK")
                raise ProviderBudgetBindingError("provider budget metadata drift before claim")
            total_claimed = int(connection.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
            unit_claimed = int(
                connection.execute("SELECT COUNT(*) FROM claims WHERE unit_id=?", (unit_id,)).fetchone()[0]
            )
            if total_claimed >= self.total_limit:
                connection.execute("ROLLBACK")
                raise ProviderBudgetExceeded(
                    f"provider total call budget exhausted before I/O: {total_claimed}/{self.total_limit}"
                )
            if unit_claimed >= self.per_unit_limit:
                connection.execute("ROLLBACK")
                raise ProviderBudgetExceeded(
                    f"provider per-unit call budget exhausted before I/O: unit={unit_id}; "
                    f"{unit_claimed}/{self.per_unit_limit}"
                )
            unit_call_index = unit_claimed + 1
            cursor = connection.execute(
                "INSERT INTO claims(unit_id, unit_call_index, claimed_at_utc) VALUES (?, ?, ?)",
                (unit_id, unit_call_index, claimed_at),
            )
            claim_id = int(cursor.lastrowid)
            connection.execute("COMMIT")
        return ProviderBudgetClaim(
            claim_id=claim_id,
            unit_id=unit_id,
            unit_call_index=unit_call_index,
            total_claimed_after=total_claimed + 1,
            per_unit_limit=self.per_unit_limit,
            total_limit=self.total_limit,
            claimed_at_utc=claimed_at,
        )

    def snapshot(self) -> ProviderBudgetSnapshot:
        with self._connect() as connection:
            metadata = dict(connection.execute("SELECT key, value FROM metadata").fetchall())
            expected = {
                "schema_version": SCHEMA_VERSION,
                "contract_sha256": self.contract_sha256,
                "authorization_sha256": self.authorization_sha256,
                "total_limit": str(self.total_limit),
                "per_unit_limit": str(self.per_unit_limit),
            }
            if metadata != expected:
                raise ProviderBudgetBindingError("provider budget metadata drift while reading snapshot")
            total_claimed = int(connection.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
            unit_rows = connection.execute(
                "SELECT unit_id, COUNT(*) FROM claims GROUP BY unit_id ORDER BY unit_id"
            ).fetchall()
        return ProviderBudgetSnapshot(
            ledger_path=str(self.path),
            contract_sha256=self.contract_sha256,
            authorization_sha256=self.authorization_sha256,
            total_limit=self.total_limit,
            per_unit_limit=self.per_unit_limit,
            total_claimed=total_claimed,
            unit_claimed={str(unit_id): int(count) for unit_id, count in unit_rows},
        )

    def assert_completed_receipts_covered(self, completed_receipt_counts: dict[str, int]) -> None:
        snapshot = self.snapshot()
        for unit_id, observed_receipts in completed_receipt_counts.items():
            claimed = int(snapshot.unit_claimed.get(str(unit_id), 0))
            if claimed < int(observed_receipts):
                raise ProviderBudgetBindingError(
                    f"persisted provider receipts exceed budget claims: unit={unit_id}; "
                    f"receipts={observed_receipts}; claims={claimed}"
                )


__all__ = [
    "ProviderBudgetBindingError",
    "ProviderBudgetClaim",
    "ProviderBudgetExceeded",
    "ProviderBudgetLedger",
    "ProviderBudgetSnapshot",
    "SCHEMA_VERSION",
]
