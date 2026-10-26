"""Compatibility layer that lets the existing DB-API code use SQLite or PostgreSQL.

SQLite remains the default for local development and tests. Set DATABASE_URL to a
PostgreSQL connection string to enable the PostgreSQL backend.
"""
from __future__ import annotations

import os
import re
import sqlite3 as _sqlite3
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Iterable, Iterator

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # SQLite-only installs remain usable without psycopg.
    psycopg = None
    dict_row = None

Connection = _sqlite3.Connection
Row = _sqlite3.Row
Warning = _sqlite3.Warning
InterfaceError = _sqlite3.InterfaceError
DataError = _sqlite3.DataError
ProgrammingError = _sqlite3.ProgrammingError
NotSupportedError = _sqlite3.NotSupportedError

Error = _sqlite3.Error
DatabaseError = _sqlite3.DatabaseError
OperationalError = _sqlite3.OperationalError
IntegrityError = _sqlite3.IntegrityError

ERROR_CLASSES = (_sqlite3.Error, psycopg.Error) if psycopg is not None else (_sqlite3.Error,)
DATABASE_ERROR_CLASSES = (_sqlite3.DatabaseError, psycopg.DatabaseError) if psycopg is not None else (_sqlite3.DatabaseError,)
OPERATIONAL_ERROR_CLASSES = (_sqlite3.OperationalError, psycopg.OperationalError) if psycopg is not None else (_sqlite3.OperationalError,)
INTEGRITY_ERROR_CLASSES = (_sqlite3.IntegrityError, psycopg.IntegrityError) if psycopg is not None else (_sqlite3.IntegrityError,)


class HybridRow(Mapping[str, Any]):
    """Mapping that supports both row['column'] and row[0]."""

    def __init__(self, row: Mapping[str, Any]):
        self._data = dict(row)
        self._values = list(self._data.values())

    def __getitem__(self, key: str | int) -> Any:
        return self._values[key] if isinstance(key, int) else self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


def _replace_qmarks(sql: str) -> str:
    """Replace positional SQLite placeholders without touching quoted strings/comments."""
    result: list[str] = []
    i, quote = 0, None
    line_comment = block_comment = False
    while i < len(sql):
        char = sql[i]
        next_char = sql[i + 1] if i + 1 < len(sql) else ""
        if line_comment:
            result.append(char)
            if char == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            result.append(char)
            if char == "*" and next_char == "/":
                result.append(next_char)
                i += 2
                block_comment = False
            else:
                i += 1
            continue
        if quote:
            result.append(char)
            if char == quote:
                if next_char == quote and quote == "'":
                    result.append(next_char)
                    i += 2
                    continue
                quote = None
            elif char == "\\" and quote == "'" and next_char:
                result.append(next_char)
                i += 2
                continue
            i += 1
            continue
        if char == "-" and next_char == "-":
            result.extend((char, next_char))
            i += 2
            line_comment = True
            continue
        if char == "/" and next_char == "*":
            result.extend((char, next_char))
            i += 2
            block_comment = True
            continue
        if char in ("'", '"'):
            quote = "'" if char == "'" else '"'
            result.append(quote)
            i += 1
            continue
        result.append("%s" if char == "?" else char)
        i += 1
    return "".join(result)


def _split_sql_script(script: str) -> list[str]:
    """Split a simple DDL/data script at semicolons outside quoted strings/comments."""
    statements: list[str] = []
    current: list[str] = []
    quote = None
    line_comment = block_comment = False
    i = 0
    while i < len(script):
        char = script[i]
        next_char = script[i + 1] if i + 1 < len(script) else ""
        if line_comment:
            current.append(char)
            if char == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            current.append(char)
            if char == "*" and next_char == "/":
                current.append(next_char)
                i += 2
                block_comment = False
            else:
                i += 1
            continue
        if quote:
            current.append(char)
            if char == quote:
                if next_char == quote and quote == "'":
                    current.append(next_char)
                    i += 2
                    continue
                quote = None
            i += 1
            continue
        if char == "-" and next_char == "-":
            current.extend((char, next_char))
            i += 2
            line_comment = True
            continue
        if char == "/" and next_char == "*":
            current.extend((char, next_char))
            i += 2
            block_comment = True
            continue
        if char in ("'", '"'):
            quote = char
            current.append(char)
            i += 1
            continue
        if char == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current.clear()
        else:
            current.append(char)
        i += 1
    tail = "".join(current).strip()
    if tail:
        statements.append(tail)
    return statements


def _postgres_schema_sql(sql: str) -> str:
    """Convert the SQLite DDL idioms used by the current schema to PostgreSQL."""
    sql = re.sub(r"\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b", "BIGSERIAL PRIMARY KEY", sql, flags=re.IGNORECASE)
    # SQLite INTEGER PRIMARY KEY also generates an id when no value is supplied.
    sql = re.sub(r"\b(id)\s+INTEGER\s+PRIMARY\s+KEY(?=\s*[,)\n])", r"\1 BIGSERIAL PRIMARY KEY", sql, flags=re.IGNORECASE)
    ignore_conflicts = bool(re.match(r"\s*INSERT\s+OR\s+IGNORE\s+INTO\b", sql, flags=re.IGNORECASE))
    if ignore_conflicts:
        sql = re.sub(r"^\s*INSERT\s+OR\s+IGNORE\s+INTO\b", "INSERT INTO", sql, flags=re.IGNORECASE)
        if not re.search(r"\bON\s+CONFLICT\b", sql, flags=re.IGNORECASE):
            sql = sql.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"
    return sql


class PostgresCursor:
    def __init__(self, cursor: Any, *, inserted_id: bool = False):
        self._cursor = cursor
        self._pending_row: HybridRow | None = None
        self._lastrowid: int | None = None
        if inserted_id:
            raw = cursor.fetchone()
            if raw is not None:
                self._pending_row = HybridRow(raw)
                value = self._pending_row.get("id")
                self._lastrowid = int(value) if value is not None else None

    @property
    def lastrowid(self) -> int | None:
        return self._lastrowid

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    def fetchone(self) -> HybridRow | None:
        if self._pending_row is not None:
            row, self._pending_row = self._pending_row, None
            return row
        raw = self._cursor.fetchone()
        return HybridRow(raw) if raw is not None else None

    def fetchall(self) -> list[HybridRow]:
        rows: list[HybridRow] = []
        if self._pending_row is not None:
            rows.append(self._pending_row)
            self._pending_row = None
        rows.extend(HybridRow(row) for row in self._cursor.fetchall())
        return rows

    def fetchmany(self, size: int | None = None) -> list[HybridRow]:
        rows: list[HybridRow] = []
        if self._pending_row is not None and (size is None or size > 0):
            rows.append(self._pending_row)
            self._pending_row = None
        remaining = None if size is None else max(0, size - len(rows))
        if remaining == 0:
            return rows
        raw_rows = self._cursor.fetchmany() if remaining is None else self._cursor.fetchmany(remaining)
        rows.extend(HybridRow(row) for row in raw_rows)
        return rows

    def close(self) -> None:
        self._cursor.close()

    def __iter__(self):
        while True:
            row = self.fetchone()
            if row is None:
                break
            yield row


class PostgresConnection:
    """Small SQLite-compatible wrapper around a psycopg connection."""

    is_postgres = True

    def __init__(self, raw: Any):
        self._raw = raw

    @property
    def row_factory(self):
        return None

    @row_factory.setter
    def row_factory(self, _factory) -> None:
        return None

    def _translate(self, sql: str, params: Sequence[Any] | Mapping[str, Any] | None):
        statement = sql.strip().rstrip(";")
        upper = statement.upper()

        if upper.startswith("PRAGMA TABLE_INFO"):
            match = re.search(r"PRAGMA\s+table_info\s*\(\s*(?:'|\x22|\x60)?([A-Za-z0-9_]+)", statement, re.IGNORECASE)
            if not match:
                raise ValueError("Table name invalide dans PRAGMA table_info.")
            return (
                "SELECT ordinal_position AS cid, column_name AS name, data_type AS type, "
                "CASE WHEN is_nullable = 'NO' THEN 1 ELSE 0 END AS notnull, "
                "column_default AS dflt_value, 0 AS pk "
                "FROM information_schema.columns WHERE table_schema = current_schema() "
                "AND table_name = %s ORDER BY ordinal_position",
                (match.group(1),),
                False,
            )
        if upper.startswith("PRAGMA QUICK_CHECK"):
            return "SELECT 'ok' AS integrity_check", None, False
        if upper.startswith("PRAGMA"):
            return "SELECT 1 AS pragma_ignored", None, False

        if re.match(r"SELECT\s+name\s+FROM\s+sqlite_master\b", statement, re.IGNORECASE):
            table_filter = re.search(r"\bname\s*=\s*(\?|%s|'([^']*)'|\x22([^\x22]*)\x22)", statement, re.IGNORECASE)
            if table_filter:
                if table_filter.group(1) in ("?", "%s"):
                    values = tuple(params) if params is not None and not isinstance(params, Mapping) else params
                    return (
                        "SELECT table_name AS name FROM information_schema.tables "
                        "WHERE table_schema = current_schema() AND table_type = 'BASE TABLE' "
                        "AND table_name = %s",
                        values,
                        False,
                    )
                name = table_filter.group(2) if table_filter.group(2) is not None else table_filter.group(3)
                return (
                    "SELECT table_name AS name FROM information_schema.tables "
                    "WHERE table_schema = current_schema() AND table_type = 'BASE TABLE' "
                    "AND table_name = %s",
                    (name,),
                    False,
                )
            return (
                "SELECT table_name AS name FROM information_schema.tables "
                "WHERE table_schema = current_schema() AND table_type = 'BASE TABLE'",
                None,
                False,
            )
        if upper.startswith("BEGIN IMMEDIATE"):
            return "SELECT 1 AS transaction_started", None, False

        translated = _replace_qmarks(_postgres_schema_sql(statement))
        inserted_id = False
        match = re.match(r"INSERT\s+INTO\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)", translated, re.IGNORECASE | re.DOTALL)
        if match and match.group(1).lower() == "attempts":
            columns = {item.strip().strip('"').lower() for item in match.group(2).split(",")}
            if "id" not in columns and not re.search(r"\bRETURNING\b", translated, re.IGNORECASE):
                translated += " RETURNING id"
                inserted_id = True
        return translated, params, inserted_id

    def execute(self, sql: str, params: Sequence[Any] | Mapping[str, Any] | None = None) -> PostgresCursor:
        translated, translated_params, inserted_id = self._translate(sql, params)
        cursor = self._raw.cursor()
        cursor.execute(translated) if translated_params is None else cursor.execute(translated, translated_params)
        return PostgresCursor(cursor, inserted_id=inserted_id)

    def executemany(self, sql: str, seq_of_params: Iterable[Sequence[Any]]) -> PostgresCursor:
        statement = _replace_qmarks(_postgres_schema_sql(sql.strip().rstrip(";")))
        cursor = self._raw.cursor()
        cursor.executemany(statement, seq_of_params)
        return PostgresCursor(cursor)

    def executescript(self, script: str) -> None:
        for statement in _split_sql_script(script):
            self.execute(statement)

    def cursor(self):
        return PostgresCursor(self._raw.cursor())

    def commit(self) -> None:
        self._raw.commit()

    def rollback(self) -> None:
        self._raw.rollback()

    def close(self) -> None:
        self._raw.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.commit() if exc_type is None else self.rollback()
        self.close()


def is_postgres_url(value: object) -> bool:
    return isinstance(value, str) and value.lower().startswith(("postgres://", "postgresql://"))


def connect(
    database: str | Path = "skilltree.db",
    timeout: float = 5.0,
    detect_types: int = 0,
    isolation_level: str | None = "",
    check_same_thread: bool = True,
    factory=None,
    cached_statements: int = 128,
    uri: bool = False,
    *,
    readonly: bool = False,
    **kwargs: Any,
):
    """Open PostgreSQL when DATABASE_URL is configured; otherwise use stdlib SQLite."""
    configured_url = os.environ.get("DATABASE_URL") or os.environ.get("SKILLTREE_DATABASE_URL")
    explicit_url = str(database)
    target_url = explicit_url if is_postgres_url(explicit_url) else configured_url
    if target_url:
        if psycopg is None:
            raise RuntimeError("DATABASE_URL est défini mais psycopg n'est pas installé.")
        connect_kwargs: dict[str, Any] = {"row_factory": dict_row, "connect_timeout": max(1, int(timeout)), "prepare_threshold": None}
        if readonly:
            connect_kwargs["options"] = "-c default_transaction_read_only=on"
        return PostgresConnection(psycopg.connect(target_url, **connect_kwargs))

    local_database: str | Path = database
    if readonly and not uri:
        local_database = Path(local_database).expanduser().resolve().as_uri() + "?mode=ro"
        uri = True
    sqlite_kwargs: dict[str, Any] = {
        "timeout": timeout,
        "detect_types": detect_types,
        "isolation_level": isolation_level,
        "check_same_thread": check_same_thread,
        "cached_statements": cached_statements,
        "uri": uri,
        **kwargs,
    }
    if factory is not None:
        sqlite_kwargs["factory"] = factory
    return _sqlite3.connect(local_database, **sqlite_kwargs)
