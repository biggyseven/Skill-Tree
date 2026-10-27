from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api


TARGET_LESSON_IDS = (
    "maint-communication-debutant",
    "maint-securite-base-debutant",
    "maint-procedures-intermediaire",
    "maint-reporting-incident-intermediaire",
    "maint-predictive-expert",
    "maint-audits-expert",
    "maint-fournisseurs-expert",
    "maint-retex-expert",
)


class LessonContentApiTests(unittest.TestCase):
    def test_all_repaired_maintenance_lessons_are_served_with_content(self) -> None:
        nodes_path = Path(api.CONTENT_DIR) / "nodes.json"
        nodes = json.loads(nodes_path.read_text(encoding="utf-8-sig"))
        titles = {node["id"]: node["title"] for node in nodes if isinstance(node, dict) and "id" in node and "title" in node}

        with tempfile.TemporaryDirectory() as temporary:
            database_path = Path(temporary) / "skilltree.db"
            with patch.object(api, "DB_PATH", database_path):
                with TestClient(api.app) as client:
                    for lesson_id in TARGET_LESSON_IDS:
                        with self.subTest(lesson_id=lesson_id):
                            self.assertIn(lesson_id, titles)
                            response = client.get(f"/api/node/{lesson_id}/lesson")
                            self.assertEqual(response.status_code, 200, response.text)
                            body = response.text.strip()
                            self.assertGreater(len(body), 8_000, f"{lesson_id}: contenu vide ou trop court")
                            self.assertTrue(
                                body.startswith(f"# {titles[lesson_id]}"),
                                f"{lesson_id}: le titre servi ne correspond pas au catalogue",
                            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
