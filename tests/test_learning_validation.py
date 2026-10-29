from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api


NODE_ID = "intro-reseau-debutant"


class LearningValidationTests(unittest.TestCase):
    def test_reading_progress_persists_and_unlocks_a_real_quiz_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database_path = Path(temporary) / "skilltree.db"
            quiz_path = Path(api.CONTENT_DIR) / "quiz" / f"{NODE_ID}.json"
            quiz_data = json.loads(quiz_path.read_text(encoding="utf-8-sig"))
            correct_answers = [question["answer"] for question in quiz_data["questions"]]

            with patch.object(api, "DB_PATH", database_path):
                with TestClient(api.app) as client:
                    initial = client.get(f"/api/node/{NODE_ID}/learning-progress")
                    self.assertEqual(initial.status_code, 200, initial.text)
                    self.assertGreater(initial.json()["target_seconds"], 0)
                    self.assertFalse(initial.json()["started"])
                    self.assertFalse(initial.json()["ready_for_assessment"])

                    blocked = client.post(
                        f"/api/node/{NODE_ID}/quiz",
                        json={"answers": correct_answers},
                    )
                    self.assertEqual(blocked.status_code, 409)
                    self.assertIn("90 %", blocked.json()["detail"])

                    reading = client.post(
                        f"/api/node/{NODE_ID}/learning-progress",
                        json={"progress_percent": 100},
                    )
                    self.assertEqual(reading.status_code, 200, reading.text)
                    self.assertEqual(reading.json()["progress_percent"], 100)
                    self.assertFalse(reading.json()["read_completed"])

                    target = int(reading.json()["target_seconds"])
                    # A recent activity ping can earn the final ten seconds; stale sessions cannot.
                    old_ping = (datetime.now(timezone.utc) - timedelta(seconds=15)).isoformat()
                    with sqlite3.connect(database_path) as conn:
                        conn.execute(
                            "UPDATE lesson_progress SET active_seconds = ?, last_ping_at = ? WHERE node_id = ?",
                            (max(0, target - 10), old_ping, NODE_ID),
                        )
                        conn.commit()

                    completed_reading = client.post(
                        f"/api/node/{NODE_ID}/learning-progress",
                        json={"progress_percent": 100},
                    )
                    self.assertTrue(completed_reading.json()["read_completed"])
                    self.assertTrue(completed_reading.json()["ready_for_assessment"])

                    incomplete = client.post(
                        f"/api/node/{NODE_ID}/quiz",
                        json={"answers": []},
                    )
                    self.assertEqual(incomplete.status_code, 422)

                    passed = client.post(
                        f"/api/node/{NODE_ID}/quiz",
                        json={"answers": correct_answers},
                    )
                    self.assertEqual(passed.status_code, 200, passed.text)
                    self.assertTrue(passed.json()["passed"])
                    self.assertTrue(passed.json()["validated"])
                    self.assertEqual(passed.json()["status"], "validated")

                    review_state = client.get(f"/api/node/{NODE_ID}/learning-progress")
                    self.assertTrue(review_state.json()["already_validated"])
                    self.assertTrue(review_state.json()["ready_for_assessment"])
                    reassessment = client.post(
                        f"/api/node/{NODE_ID}/quiz",
                        json={"answers": correct_answers},
                    )
                    self.assertEqual(reassessment.status_code, 200, reassessment.text)
                    self.assertTrue(reassessment.json()["validated"])
                    self.assertTrue(reassessment.json()["reassessment"])
                    self.assertFalse(reassessment.json()["attempt_recorded"])
                    self.assertEqual(reassessment.json()["xp_gained"], 0)

                    tree = client.get("/api/tree").json()
                    self.assertGreaterEqual(tree["validated"], 1)
                    course = next(node for node in tree["nodes"] if node["id"] == NODE_ID)
                    self.assertEqual(course["status"], "validated")
                    self.assertEqual(course["reading_progress_percent"], 100)
                    self.assertTrue(course["reading_completed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
