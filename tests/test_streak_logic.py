"""Regression tests for the current learning streak returned by the API."""

from datetime import date, timedelta
import sqlite3
from types import SimpleNamespace
import unittest

from app.api import _streak_payload


class StreakPayloadTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(
            """
            CREATE TABLE daily_streak (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_jour TEXT NOT NULL UNIQUE,
                minutes_etudiees INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE shop_inventory (
                item_id TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        self.tree = SimpleNamespace(conn=self.connection)

    def tearDown(self):
        self.connection.close()

    def add_study_day(self, day: date, minutes: int = 10):
        self.connection.execute(
            "INSERT INTO daily_streak (date_jour, minutes_etudiees) VALUES (?, ?)",
            (day.isoformat(), minutes),
        )
        self.connection.commit()

    def test_streak_expires_after_more_than_one_inactive_day(self):
        self.add_study_day(date.today() - timedelta(days=3))

        payload = _streak_payload(self.tree)

        self.assertEqual(payload["days"], 0)
        self.assertFalse(payload["active_today"])

    def test_activity_today_starts_or_continues_a_streak(self):
        self.add_study_day(date.today(), minutes=25)

        payload = _streak_payload(self.tree)

        self.assertEqual(payload["days"], 1)
        self.assertTrue(payload["active_today"])
        self.assertEqual(payload["minutes_today"], 25)

    def test_activity_yesterday_still_counts_until_today_ends(self):
        self.add_study_day(date.today() - timedelta(days=1))

        payload = _streak_payload(self.tree)

        self.assertEqual(payload["days"], 1)
        self.assertFalse(payload["active_today"])

    def test_streak_counts_consecutive_days_through_today(self):
        today = date.today()
        self.add_study_day(today - timedelta(days=2))
        self.add_study_day(today - timedelta(days=1))
        self.add_study_day(today)

        payload = _streak_payload(self.tree)

        self.assertEqual(payload["days"], 3)
        self.assertTrue(payload["active_today"])


if __name__ == "__main__":
    unittest.main()
