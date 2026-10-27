"""Connexion SQLite, schéma et amorçage du contenu."""
from __future__ import annotations

from . import db_compat as sqlite3
from datetime import date, timedelta
from pathlib import Path

DEFAULT_DB = "skilltree.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category    TEXT NOT NULL DEFAULT 'Général',
    module TEXT NOT NULL DEFAULT 'Administration Réseaux',
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

-- Schéma persistant du Lab Workspace v2. Ces tables doivent exister sur tout
-- environnement démarré depuis le dépôt, sans dépendre d'une base locale ignorée.
CREATE TABLE IF NOT EXISTS labs (
    id              TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    level           TEXT NOT NULL DEFAULT 'débutant',
    module          TEXT NOT NULL DEFAULT 'Général',
    prompt          TEXT NOT NULL DEFAULT '',
    objectives      TEXT NOT NULL DEFAULT '[]',
    hints           TEXT NOT NULL DEFAULT '[]',
    duration_min    INTEGER NOT NULL DEFAULT 15,
    difficulty      TEXT NOT NULL DEFAULT 'débutant',
    xp_reward       INTEGER NOT NULL DEFAULT 0 CHECK (xp_reward >= 0),
    badges          TEXT NOT NULL DEFAULT '[]',
    schema_version  INTEGER NOT NULL DEFAULT 2,
    definition_json TEXT NOT NULL DEFAULT '{}',
    migration_note  TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS lab_attempts (
    id                TEXT PRIMARY KEY,
    lab_id            TEXT NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    user_id           TEXT,
    started_at        TEXT NOT NULL,
    finished_at       TEXT NOT NULL,
    passed            INTEGER NOT NULL DEFAULT 0 CHECK (passed IN (0, 1)),
    config_snapshot   TEXT NOT NULL DEFAULT '{}',
    check_result_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_lab_attempts_lab_finished
    ON lab_attempts(lab_id, finished_at);

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

CREATE TABLE IF NOT EXISTS exam_sessions (
    session_id   TEXT PRIMARY KEY,
    category     TEXT NOT NULL,
    question_ids TEXT NOT NULL,
    started_at   INTEGER NOT NULL,
    expires_at   INTEGER NOT NULL,
    submitted    INTEGER NOT NULL DEFAULT 0,
    score        INTEGER,
    passed       INTEGER,
    correct      INTEGER,
    total        INTEGER,
    submitted_at INTEGER,
    time_expired INTEGER NOT NULL DEFAULT 0,
    answers_json TEXT NOT NULL DEFAULT '[]',
    details_json TEXT NOT NULL DEFAULT '[]',
    paused_at    INTEGER,
    paused_seconds INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_exam_sessions_expires ON exam_sessions(expires_at);

CREATE TABLE IF NOT EXISTS terminal_specs (
    node_id TEXT PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    prompt  TEXT NOT NULL,
    answer  TEXT NOT NULL,
    pattern TEXT NOT NULL,
    explanation TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS daily_streak (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date_jour        TEXT NOT NULL UNIQUE,
    minutes_etudiees INTEGER NOT NULL DEFAULT 0 CHECK (minutes_etudiees >= 0)
);

CREATE INDEX IF NOT EXISTS idx_daily_streak_date ON daily_streak(date_jour);

CREATE TABLE IF NOT EXISTS user_stats (
    id            INTEGER PRIMARY KEY CHECK (id = 1),
    total_xp      INTEGER NOT NULL DEFAULT 0 CHECK (total_xp >= 0),
    current_level INTEGER NOT NULL DEFAULT 1 CHECK (current_level BETWEEN 1 AND 4),
    coins         INTEGER NOT NULL DEFAULT 0 CHECK (coins >= 0)
);

CREATE TABLE IF NOT EXISTS badges (
    id                      TEXT PRIMARY KEY,
    nom                     TEXT NOT NULL,
    description             TEXT NOT NULL,
    icone                   TEXT NOT NULL,
    condition_debloquee_le  TEXT
);

CREATE TABLE IF NOT EXISTS shop_items (
    id          TEXT PRIMARY KEY,
    nom         TEXT NOT NULL,
    description TEXT NOT NULL,
    prix        INTEGER NOT NULL CHECK (prix >= 0),
    type        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shop_inventory (
    item_id  TEXT PRIMARY KEY REFERENCES shop_items(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0)
);

CREATE TABLE IF NOT EXISTS certificates (
    number    TEXT PRIMARY KEY,
    name      TEXT NOT NULL,
    level     INTEGER NOT NULL,
    issued_at TEXT NOT NULL
);

INSERT OR IGNORE INTO shop_items (id, nom, description, prix, type)
VALUES
    ('hint', 'Indice', 'Débloque un indice pour t''aider à résoudre un exercice.', 50, 'hint'),
    ('streak_freeze', 'Gel de streak', 'Protège ta série pendant une journée manquée.', 100, 'streak_freeze');
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
    if not getattr(conn, "is_postgres", False):
        _migrate(conn)
    else:
        # CREATE TABLE IF NOT EXISTS ne modifie pas une table PostgreSQL existante.
        conn.execute("ALTER TABLE exam_sessions ADD COLUMN IF NOT EXISTS answers_json TEXT NOT NULL DEFAULT '[]'")
        conn.execute("ALTER TABLE exam_sessions ADD COLUMN IF NOT EXISTS details_json TEXT NOT NULL DEFAULT '[]'")
        conn.execute("ALTER TABLE exam_sessions ADD COLUMN IF NOT EXISTS paused_at INTEGER")
        conn.execute("ALTER TABLE exam_sessions ADD COLUMN IF NOT EXISTS paused_seconds INTEGER NOT NULL DEFAULT 0")
    _ensure_user_stats(conn)
    conn.commit()


def _migrate(conn: sqlite3.Connection) -> None:
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(lab_specs)")]
    if "kind" not in columns:
        conn.execute(
            "ALTER TABLE lab_specs ADD COLUMN kind TEXT NOT NULL DEFAULT 'text'"
            " CHECK (kind IN ('text', 'docker'))"
        )

    stats_columns = {row["name"] for row in conn.execute("PRAGMA table_info(user_stats)")}
    if "coins" not in stats_columns:
        conn.execute(
            "ALTER TABLE user_stats ADD COLUMN coins INTEGER NOT NULL DEFAULT 0"
        )

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

    # La session garde les réponses et le corrigé après envoi pour rendre la note immuable.
    exam_columns = {row["name"] for row in conn.execute("PRAGMA table_info(exam_sessions)")}
    if "answers_json" not in exam_columns:
        conn.execute("ALTER TABLE exam_sessions ADD COLUMN answers_json TEXT NOT NULL DEFAULT '[]'")
    if "details_json" not in exam_columns:
        conn.execute("ALTER TABLE exam_sessions ADD COLUMN details_json TEXT NOT NULL DEFAULT '[]'")
    if "paused_at" not in exam_columns:
        conn.execute("ALTER TABLE exam_sessions ADD COLUMN paused_at INTEGER")
    if "paused_seconds" not in exam_columns:
        conn.execute("ALTER TABLE exam_sessions ADD COLUMN paused_seconds INTEGER NOT NULL DEFAULT 0")

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_attempts_node ON attempts(node_id, created_at)"
    )

    _migrate_proof_kind(conn, "requirements")
    _migrate_proof_kind(conn, "attempts")


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


STREAK_MINUTES_PER_VALIDATION = 5


def touch_daily_streak(
    conn: sqlite3.Connection,
    day: str | None = None,
    minutes: int = STREAK_MINUTES_PER_VALIDATION,
    *,
    commit: bool = True,
) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS daily_streak ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "date_jour TEXT NOT NULL UNIQUE, "
        "minutes_etudiees INTEGER NOT NULL DEFAULT 0 CHECK (minutes_etudiees >= 0))"
    )
    day = day or date.today().isoformat()
    minutes = max(0, int(minutes))
    try:
        current_day = date.fromisoformat(day)
    except (TypeError, ValueError):
        current_day = date.today()
        day = current_day.isoformat()

    prior = conn.execute(
        "SELECT MAX(date_jour) AS day FROM daily_streak WHERE date_jour < ?",
        (day,),
    ).fetchone()
    if prior and prior["day"]:
        try:
            last_day = date.fromisoformat(prior["day"])
            _consume_streak_freezes(conn, last_day, current_day)
        except (TypeError, ValueError):
            pass

    conn.execute(
        "INSERT INTO daily_streak (date_jour, minutes_etudiees) VALUES (?, ?)"
        " ON CONFLICT(date_jour) DO UPDATE SET"
        " minutes_etudiees = daily_streak.minutes_etudiees + excluded.minutes_etudiees",
        (day, minutes),
    )
    if commit:
        conn.commit()


XP_LEVELS = (
    (1, 0, "Débutant"),
    (2, 500, "Technicien"),
    (3, 1500, "Admin"),
    (4, 3000, "Senior"),
)

XP_REWARDS = {
    "quiz": 10,
    "terminal": 10,
    "lab": 50,
    "manual": 30,
    "exam": 100,
    "diagnostic": 20,
}

COIN_REWARDS = {
    "quiz": 5,
    "terminal": 5,
    "lab": 20,
    "manual": 10,
    "exam": 50,
}

STREAK_FREEZE_ITEM = "streak_freeze"


def streak_days(conn: sqlite3.Connection, today: date | None = None) -> int:
    today = today or date.today()
    rows = conn.execute(
        "SELECT date_jour FROM daily_streak WHERE date_jour <= ? ORDER BY date_jour DESC",
        (today.isoformat(),),
    ).fetchall()
    days: set[date] = set()
    for row in rows:
        try:
            day = date.fromisoformat(row["date_jour"])
        except (TypeError, ValueError):
            continue
        if day <= today:
            days.add(day)
    if not days:
        return 0
    latest = max(days)
    if latest < today - timedelta(days=1):
        return 0
    streak = 0
    cursor = latest
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def streak_multiplier(days: int) -> float:
    if days >= 7:
        return 2.0
    if days >= 3:
        return 1.5
    return 1.0


def _consume_streak_freezes(conn: sqlite3.Connection, last_day: date, today: date) -> None:
    missing = (today - last_day).days - 1
    if missing <= 0:
        return
    try:
        row = conn.execute(
            "SELECT quantity FROM shop_inventory WHERE item_id = ?",
            (STREAK_FREEZE_ITEM,),
        ).fetchone()
    except sqlite3.OPERATIONAL_ERROR_CLASSES:
        return
    available = max(0, int(row["quantity"] or 0)) if row else 0
    used = min(missing, available)
    if used <= 0:
        return
    for offset in range(1, used + 1):
        covered = (last_day + timedelta(days=offset)).isoformat()
        conn.execute(
            "INSERT OR IGNORE INTO daily_streak (date_jour, minutes_etudiees)"
            " VALUES (?, 0)",
            (covered,),
        )
    conn.execute(
        "UPDATE shop_inventory SET quantity = quantity - ? WHERE item_id = ?",
        (used, STREAK_FREEZE_ITEM),
    )


def _ensure_user_stats(conn: sqlite3.Connection, *, commit: bool = True) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO user_stats (id, total_xp, current_level, coins)"
        " VALUES (1, 0, 1, 0)"
    )
    if commit:
        conn.commit()


def level_for_xp(total_xp: int) -> dict:
    total_xp = max(0, int(total_xp))
    current = XP_LEVELS[0]
    for candidate in XP_LEVELS:
        if total_xp >= candidate[1]:
            current = candidate

    next_level = next(
        (candidate for candidate in XP_LEVELS if candidate[1] > total_xp),
        None,
    )
    xp_in_level = total_xp - current[1]
    if next_level is None:
        progress = 100
        xp_to_next = 0
    else:
        span = next_level[1] - current[1]
        progress = int(100 * xp_in_level / span) if span else 100
        xp_to_next = next_level[1] - total_xp

    return {
        "current_level": current[0],
        "level_name": current[2],
        "level_xp": current[1],
        "next_level": next_level[0] if next_level else None,
        "next_level_xp": next_level[1] if next_level else None,
        "xp_in_level": xp_in_level,
        "xp_to_next": xp_to_next,
        "progress_percent": progress,
        "max_level": next_level is None,
    }


def get_user_stats(conn: sqlite3.Connection) -> dict:
    _ensure_user_stats(conn)
    row = conn.execute(
        "SELECT total_xp, current_level, coins FROM user_stats WHERE id = 1"
    ).fetchone()
    total_xp = max(0, int(row["total_xp"] or 0)) if row else 0
    coins = max(0, int(row["coins"] or 0)) if row else 0
    info = level_for_xp(total_xp)
    if row is None or int(row["current_level"]) != info["current_level"]:
        conn.execute(
            "UPDATE user_stats SET total_xp = ?, current_level = ?, coins = ? WHERE id = 1",
            (total_xp, info["current_level"], coins),
        )
        conn.commit()
    return {"total_xp": total_xp, "coins": coins, **info}


def add_xp(conn: sqlite3.Connection, amount: int, coins: int = 0) -> dict:
    amount = max(0, int(amount))
    coins = max(0, int(coins))
    # Ne pas interrompre une transaction englobante (ex. soumission d'un lab).
    _ensure_user_stats(conn, commit=False)
    row = conn.execute("SELECT total_xp, coins FROM user_stats WHERE id = 1").fetchone()
    total_xp = (int(row["total_xp"] or 0) if row else 0) + amount
    total_coins = (int(row["coins"] or 0) if row else 0) + coins
    info = level_for_xp(total_xp)
    conn.execute(
        "UPDATE user_stats SET total_xp = ?, current_level = ?, coins = ? WHERE id = 1",
        (total_xp, info["current_level"], total_coins),
    )
    conn.commit()
    return get_user_stats(conn)


def award_attempt_xp(conn: sqlite3.Connection, kind: object, passed: bool = True) -> dict | None:
    if not passed:
        return None
    kind_value = str(getattr(kind, "value", kind))
    base_xp = XP_REWARDS.get(kind_value, 0)
    base_coins = COIN_REWARDS.get(kind_value, 0)
    if base_xp <= 0 and base_coins <= 0:
        return None

    # Calcul du multiplicateur de streak
    days = streak_days(conn)
    multiplier = streak_multiplier(days)
    xp = int(round(base_xp * multiplier))
    coins = int(round(base_coins * multiplier))
    
    before = get_user_stats(conn)
    stats = add_xp(conn, xp, coins)
    
    return {
        "xp": xp,
        "coins": coins,
        "base_xp": base_xp,
        "base_coins": base_coins,
        "multiplier": multiplier,
        "streak_days": days,
        "level_up": stats["current_level"] > before["current_level"],
        "stats": stats,
    }


def ensure_ready(conn: sqlite3.Connection) -> None:
    initialize(conn)
    if is_empty(conn):
        from .loader import load_content

        load_content(conn)