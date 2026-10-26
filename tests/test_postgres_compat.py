from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app import db_compat


class PostgresCompatibilityTests(unittest.TestCase):
    def test_sqlite_remains_default_when_database_url_is_not_set(self) -> None:
        with patch.dict(os.environ, {"DATABASE_URL": "", "SKILLTREE_DATABASE_URL": ""}):
            connection = db_compat.connect(":memory:")
            try:
                self.assertFalse(getattr(connection, "is_postgres", False))
                self.assertEqual(connection.execute("SELECT 42").fetchone()[0], 42)
            finally:
                connection.close()

    def test_only_insert_or_ignore_gains_do_nothing_clause(self) -> None:
        ignored = db_compat._postgres_schema_sql(
            "INSERT OR IGNORE INTO badges (id, nom) VALUES ('x', 'test')"
        )
        ordinary = db_compat._postgres_schema_sql(
            "INSERT INTO badges (id, nom) VALUES ('x', 'test')"
        )
        upsert = db_compat._postgres_schema_sql(
            "INSERT INTO badges (id, nom) VALUES ('x', 'test') "
            "ON CONFLICT(id) DO UPDATE SET nom = excluded.nom"
        )
        self.assertTrue(ignored.endswith("ON CONFLICT DO NOTHING"))
        self.assertNotIn("ON CONFLICT", ordinary)
        self.assertEqual(upsert.count("ON CONFLICT"), 1)

    def test_postgres_schema_converts_sqlite_generated_ids(self) -> None:
        auto = db_compat._postgres_schema_sql(
            "CREATE TABLE attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT)"
        )
        rowid = db_compat._postgres_schema_sql(
            "CREATE TABLE topologies (id INTEGER PRIMARY KEY, name TEXT)"
        )
        singleton = db_compat._postgres_schema_sql(
            "CREATE TABLE user_stats (id INTEGER PRIMARY KEY CHECK (id = 1))"
        )
        self.assertIn("BIGSERIAL PRIMARY KEY", auto)
        self.assertIn("BIGSERIAL PRIMARY KEY", rowid)
        self.assertIn("id INTEGER PRIMARY KEY CHECK (id = 1)", singleton)

    def test_qmark_translation_does_not_replace_question_marks_in_literals(self) -> None:
        sql = "SELECT '?' AS question, ? AS value, 'a?b' AS example"
        self.assertEqual(
            db_compat._replace_qmarks(sql),
            "SELECT '?' AS question, %s AS value, 'a?b' AS example",
        )

    def test_schema_script_splitter_keeps_semicolons_inside_strings(self) -> None:
        statements = db_compat._split_sql_script(
            "CREATE TABLE a (name TEXT); "
            "INSERT INTO a (name) VALUES ('one; two'); "
            "-- comment; still comment\nSELECT 1;"
        )
        self.assertEqual(len(statements), 3)
        self.assertIn("'one; two'", statements[1])

    def test_sqlite_master_translation_uses_information_schema(self) -> None:
        connection = object.__new__(db_compat.PostgresConnection)
        sql, params, inserted_id = connection._translate(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
            ("nodes",),
        )
        self.assertIn("information_schema.tables", sql)
        self.assertEqual(params, ("nodes",))
        self.assertFalse(inserted_id)

    def test_table_info_translation_and_read_only_health_check(self) -> None:
        connection = object.__new__(db_compat.PostgresConnection)
        sql, params, inserted_id = connection._translate('PRAGMA table_info("nodes")', None)
        self.assertIn("information_schema.columns", sql)
        self.assertEqual(params, ("nodes",))
        self.assertFalse(inserted_id)
        health_sql, _, _ = connection._translate("PRAGMA quick_check", None)
        self.assertEqual(health_sql, "SELECT 'ok' AS integrity_check")

    def test_attempt_insert_requests_generated_id(self) -> None:
        connection = object.__new__(db_compat.PostgresConnection)
        sql, params, inserted_id = connection._translate(
            "INSERT INTO attempts (node_id, kind, score, passed, evidence, detail, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("node-1", "quiz", 90, 1, "", "", "2026-10-26 12:00:00"),
        )
        self.assertTrue(sql.endswith("RETURNING id"))
        self.assertEqual(params[0], "node-1")
        self.assertTrue(inserted_id)


    @unittest.skipUnless(os.environ.get("TEST_POSTGRES_URL"), "Dedicated PostgreSQL test database not configured")
    def test_postgres_backend_bootstraps_catalogue_and_records_progress(self) -> None:
        from app.db import ensure_ready
        from app.domain import ProofKind
        from app.engine import SkillTree

        database_url = os.environ["TEST_POSTGRES_URL"]
        with patch.dict(
            os.environ,
            {"DATABASE_URL": database_url, "SKILLTREE_DATABASE_URL": ""},
        ):
            connection = db_compat.connect()
            try:
                ensure_ready(connection)
                tree = SkillTree(connection)
                self.assertIn("intro-reseau-debutant", {node.id for node in tree.nodes()})
                cursor = connection.execute("SELECT COUNT(*) FROM requirements")
                self.assertGreater(cursor.fetchone()[0], 300)

                attempt, validated = tree.record(
                    "intro-reseau-debutant",
                    ProofKind.QUIZ,
                    85,
                    True,
                    evidence="postgres-integration-test",
                    detail="Neon backend smoke test",
                )
                self.assertGreater(attempt.id, 0)
                self.assertTrue(validated)
                self.assertIn("intro-reseau-debutant", tree.validated_ids())
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
