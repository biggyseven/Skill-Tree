"""Tests unitaires du TP serverless intermédiaire de Skill-Tree."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "serverless_intermediaire"
sys.path.insert(0, str(EXAMPLE_DIR))
import serverless_pipeline as pipeline  # noqa: E402


class ServerlessPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = Path(self.temp_dir.name) / "test.db"
        pipeline.init_db(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def submit_and_publish(self, attempt_id="attempt-1", user_id="user-1", lab_id="lab-1", passed=True, xp=100):
        result = pipeline.submit_lab_attempt(attempt_id, user_id, lab_id, passed, xp, self.db)
        self.assertEqual(result["status"], "accepted")
        pipeline.publish_outbox(self.db)
        with pipeline.open_db(self.db) as conn:
            row = conn.execute("SELECT message_id FROM queue_messages WHERE event_id = ?", (result["event_id"],)).fetchone()
        result["message_id"] = int(row["message_id"])
        return result

    def test_attempt_and_outbox_are_atomic(self):
        result = pipeline.submit_lab_attempt("attempt-1", "user-1", "lab-1", True, 100, self.db)
        with pipeline.open_db(self.db) as conn:
            self.assertIsNotNone(conn.execute("SELECT 1 FROM lab_attempts WHERE attempt_id='attempt-1'").fetchone())
            event = conn.execute("SELECT status FROM outbox_events WHERE event_id=?", (result["event_id"],)).fetchone()
            self.assertEqual(event["status"], "pending")
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM queue_messages").fetchone()[0], 0)

    def test_outbox_failure_rolls_back_attempt(self):
        with pipeline.open_db(self.db) as conn:
            conn.execute("CREATE TRIGGER fail_outbox BEFORE INSERT ON outbox_events BEGIN SELECT RAISE(ABORT, 'simulated'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            pipeline.submit_lab_attempt("attempt-1", "user-1", "lab-1", True, 100, self.db)
        with pipeline.open_db(self.db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM lab_attempts").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM outbox_events").fetchone()[0], 0)

    def test_outbox_publish_is_idempotent(self):
        pipeline.submit_lab_attempt("attempt-1", "user-1", "lab-1", True, 100, self.db)
        self.assertEqual(pipeline.publish_outbox(self.db)["published"], 1)
        self.assertEqual(pipeline.publish_outbox(self.db)["published"], 0)

    def test_success_awards_xp_once(self):
        item = self.submit_and_publish()
        result = pipeline.consume_message(item["message_id"], self.db, force=True)
        self.assertEqual(result["status"], "rewarded")
        self.assertEqual(result["xp_gained"], 100)
        self.assertEqual(pipeline.get_user_xp("user-1", self.db), 100)

    def test_same_message_cannot_award_twice(self):
        item = self.submit_and_publish()
        pipeline.consume_message(item["message_id"], self.db, force=True)
        result = pipeline.consume_message(item["message_id"], self.db, force=True)
        self.assertEqual(result["status"], "already_processed")
        self.assertEqual(pipeline.get_user_xp("user-1", self.db), 100)

    def test_redelivery_is_ignored(self):
        item = self.submit_and_publish()
        pipeline.consume_message(item["message_id"], self.db, force=True)
        duplicate = pipeline.simulate_redelivery(item["event_id"], self.db)
        result = pipeline.consume_message(duplicate["message_id"], self.db, force=True)
        self.assertEqual(result["status"], "duplicate_ignored")
        self.assertEqual(pipeline.get_user_xp("user-1", self.db), 100)

    def test_same_lab_is_rewarded_once_per_user(self):
        first = self.submit_and_publish("attempt-1", "user-1", "lab-1", True, 100)
        pipeline.consume_message(first["message_id"], self.db, force=True)
        second = self.submit_and_publish("attempt-2", "user-1", "lab-1", True, 100)
        result = pipeline.consume_message(second["message_id"], self.db, force=True)
        self.assertEqual(result["status"], "already_rewarded")
        self.assertEqual(result["xp_gained"], 0)
        self.assertEqual(pipeline.get_user_xp("user-1", self.db), 100)

    def test_failed_lab_has_no_reward(self):
        item = self.submit_and_publish(passed=False, xp=100)
        result = pipeline.consume_message(item["message_id"], self.db, force=True)
        self.assertEqual(result["status"], "processed_no_reward")
        self.assertEqual(pipeline.get_user_xp("user-1", self.db), 0)

    def test_transient_error_can_be_retried(self):
        item = self.submit_and_publish()
        first = pipeline.consume_message(item["message_id"], self.db, simulate_failure=True)
        self.assertEqual(first["status"], "retry")
        second = pipeline.consume_message(item["message_id"], self.db, force=True)
        self.assertEqual(second["status"], "rewarded")
        self.assertEqual(pipeline.get_user_xp("user-1", self.db), 100)

    def test_retry_limit_moves_message_to_dlq(self):
        item = self.submit_and_publish()
        first = pipeline.consume_message(item["message_id"], self.db, max_attempts=2, simulate_failure=True)
        self.assertEqual(first["status"], "retry")
        result = pipeline.consume_message(item["message_id"], self.db, max_attempts=2, simulate_failure=True, force=True)
        self.assertEqual(result["status"], "dead_letter")

    def test_reused_attempt_id_with_different_data_is_rejected(self):
        self.submit_and_publish(attempt_id="attempt-1")
        result = pipeline.submit_lab_attempt("attempt-1", "other-user", "lab-1", True, 100, self.db)
        self.assertEqual(result["status"], "id_conflict")

    def test_invalid_submission_does_not_write_data(self):
        with self.assertRaises(ValueError):
            pipeline.submit_lab_attempt("attempt-1", "user-1", "lab-1", "yes", 100, self.db)
        with self.assertRaises(ValueError):
            pipeline.submit_lab_attempt("attempt-2", "user-1", "lab-1", True, -1, self.db)
        with pipeline.open_db(self.db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM lab_attempts").fetchone()[0], 0)

    def test_invalid_payload_goes_to_dlq(self):
        item = self.submit_and_publish()
        with pipeline.open_db(self.db) as conn:
            conn.execute("UPDATE queue_messages SET payload_json='{invalid' WHERE message_id=?", (item["message_id"],))
            conn.commit()
        result = pipeline.consume_message(item["message_id"], self.db)
        self.assertEqual(result["status"], "dead_letter")


if __name__ == "__main__":
    unittest.main(verbosity=2)
