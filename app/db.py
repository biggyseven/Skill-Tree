"""Connexion SQLite, schéma et amorçage du contenu."""
from __future__ import annotations

import sqlite3
from pathlib import Path

DEFAULT_DB = "skilltree.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category    TEXT NOT NULL DEFAULT 'Général',
    sort_order  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS edges (
    node_id   TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    prereq_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    PRIMARY KEY (node_id, prereq_id)
);

CREATE TABLE IF NOT EXISTS requirements (
    node_id   TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    kind      TEXT NOT NULL CHECK (kind IN ('quiz', 'lab', 'exam', 'manual', 'terminal')),
    min_score INTEGER NOT NULL DEFAULT 80 CHECK (min_score BETWEEN 0 AND 100),
    PRIMARY KEY (node_id, kind)
);

CREATE TABLE IF NOT EXISTS attempts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id    TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    kind       TEXT NOT NULL CHECK (kind IN ('quiz', 'lab', 'exam', 'manual', 'terminal')),
    score      INTEGER NOT NULL DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
    passed     INTEGER NOT NULL DEFAULT 0 CHECK (passed IN (0, 1)),
    evidence   TEXT NOT NULL DEFAULT '',
    detail     TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_attempts_node ON attempts(node_id, created_at);

CREATE TABLE IF NOT EXISTS lab_specs (
    node_id TEXT PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    kind    TEXT NOT NULL DEFAULT 'text' CHECK (kind IN ('text', 'docker')),
    mode    TEXT NOT NULL CHECK (mode IN ('exact', 'contains', 'regex', 'all', 'any')),
    pattern TEXT NOT NULL,
    prompt  TEXT NOT NULL DEFAULT '',
    hint    TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS questions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id     TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    scope       TEXT NOT NULL CHECK (scope IN ('quiz', 'exam')),
    prompt      TEXT NOT NULL,
    choices     TEXT NOT NULL,
    answer      INTEGER NOT NULL,
    question_type TEXT NOT NULL DEFAULT 'qcm' CHECK (question_type IN ('qcm', 'input', 'terminal')),
    answer_text TEXT,
    answer_regex TEXT,
    explanation TEXT NOT NULL DEFAULT '',
    position    INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_questions_node ON questions(node_id, scope, position);

CREATE TABLE IF NOT EXISTS topologies (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    data       TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS challenges (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id            TEXT NOT NULL UNIQUE REFERENCES nodes(id) ON DELETE CASCADE,
    expected_topology  TEXT NOT NULL,
    time_limit         INTEGER NOT NULL CHECK (time_limit > 0)
);

CREATE TABLE IF NOT EXISTS challenge_sessions (
    session_id TEXT PRIMARY KEY,
    node_id    TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    expires_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS terminal_specs (
    node_id TEXT PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    prompt  TEXT NOT NULL,
    answer  TEXT NOT NULL,
    pattern TEXT NOT NULL,
    explanation TEXT NOT NULL DEFAULT ''
);
"""


def connect(path: str | Path = DEFAULT_DB, *, check_same_thread: bool = True) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), check_same_thread=check_same_thread)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    _migrate(conn)
    conn.commit()


def _migrate(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(lab_specs)")}
    if "kind" not in columns:
        conn.execute(
            "ALTER TABLE lab_specs ADD COLUMN kind TEXT NOT NULL DEFAULT 'text'"
            " CHECK (kind IN ('text', 'docker'))"
        )

    _migrate_proof_kind(conn, "requirements")
    _migrate_proof_kind(conn, "attempts")

    question_columns = {row["name"] for row in conn.execute("PRAGMA table_info(questions)")}
    if "question_type" not in question_columns:
        conn.execute(
            "ALTER TABLE questions ADD COLUMN question_type TEXT NOT NULL DEFAULT 'qcm'"
            " CHECK (question_type IN ('qcm', 'input', 'terminal'))"
        )
    if "answer_text" not in question_columns:
        conn.execute("ALTER TABLE questions ADD COLUMN answer_text TEXT")
    if "answer_regex" not in question_columns:
        conn.execute("ALTER TABLE questions ADD COLUMN answer_regex TEXT")

    question_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'questions'"
    ).fetchone()["sql"]
    if "'terminal'" not in question_sql:
        conn.execute(
            "CREATE TABLE questions_new ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE, "
            "scope TEXT NOT NULL CHECK (scope IN ('quiz', 'exam')), "
            "prompt TEXT NOT NULL, choices TEXT NOT NULL, answer INTEGER NOT NULL, "
            "question_type TEXT NOT NULL DEFAULT 'qcm' "
            "CHECK (question_type IN ('qcm', 'input', 'terminal')), "
            "answer_text TEXT, answer_regex TEXT, explanation TEXT NOT NULL DEFAULT '', "
            "position INTEGER NOT NULL DEFAULT 0)"
        )
        conn.execute(
            "INSERT INTO questions_new "
            "(id, node_id, scope, prompt, choices, answer, question_type, answer_text, "
            "answer_regex, explanation, position) "
            "SELECT id, node_id, scope, prompt, choices, answer, question_type, answer_text, "
            "answer_regex, explanation, position FROM questions"
        )
        conn.execute("DROP TABLE questions")
        conn.execute("ALTER TABLE questions_new RENAME TO questions")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_questions_node ON questions(node_id, scope, position)"
        )

    terminal_columns = {row["name"] for row in conn.execute("PRAGMA table_info(terminal_specs)")}
    if "explanation" not in terminal_columns:
        conn.execute(
            "ALTER TABLE terminal_specs ADD COLUMN explanation TEXT NOT NULL DEFAULT ''"
        )

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_attempts_node ON attempts(node_id, created_at)"
    )


def _migrate_proof_kind(conn: sqlite3.Connection, table: str) -> None:
    table_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()["sql"]
    if "'terminal'" in table_sql:
        return

    if table == "requirements":
        conn.execute("DROP TABLE IF EXISTS requirements_new")
        conn.execute(
            "CREATE TABLE requirements_new ("
            "node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE, "
            "kind TEXT NOT NULL CHECK (kind IN ('quiz', 'lab', 'exam', 'manual', 'terminal')), "
            "min_score INTEGER NOT NULL DEFAULT 80 CHECK (min_score BETWEEN 0 AND 100), "
            "PRIMARY KEY (node_id, kind))"
        )
        conn.execute("INSERT INTO requirements_new SELECT node_id, kind, min_score FROM requirements")
        conn.execute("DROP TABLE requirements")
        conn.execute("ALTER TABLE requirements_new RENAME TO requirements")
        return

    conn.execute("DROP TABLE IF EXISTS attempts_new")
    conn.execute(
        "CREATE TABLE attempts_new ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE, "
        "kind TEXT NOT NULL CHECK (kind IN ('quiz', 'lab', 'exam', 'manual', 'terminal')), "
        "score INTEGER NOT NULL DEFAULT 0 CHECK (score BETWEEN 0 AND 100), "
        "passed INTEGER NOT NULL DEFAULT 0 CHECK (passed IN (0, 1)), "
        "evidence TEXT NOT NULL DEFAULT '', "
        "detail TEXT NOT NULL DEFAULT '', "
        "created_at TEXT NOT NULL)"
    )
    conn.execute(
        "INSERT INTO attempts_new (id, node_id, kind, score, passed, evidence, detail, created_at) "
        "SELECT id, node_id, kind, score, passed, evidence, detail, created_at FROM attempts"
    )
    conn.execute("DROP TABLE attempts")
    conn.execute("ALTER TABLE attempts_new RENAME TO attempts")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_attempts_node ON attempts(node_id, created_at)"
    )


def is_empty(conn: sqlite3.Connection) -> bool:
    return conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] == 0


def ensure_ready(conn: sqlite3.Connection) -> None:
    """Crée le schéma et charge content/ au premier lancement."""
    initialize(conn)
    if is_empty(conn):
        from .loader import load_content

        load_content(conn)
