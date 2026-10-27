from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.db import connect, initialize
from app.loader import ContentError, load_content, load_lessons


class MissingPrerequisiteLoaderTests(unittest.TestCase):
    def test_missing_prerequisites_are_warned_and_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            content_dir = Path(temporary) / "content"
            content_dir.mkdir()
            (content_dir / "nodes.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "course-a",
                            "title": "Cours A",
                            "prereqs": ["course-b", "missing-course"],
                            "requirements": [{"kind": "manual", "min_score": 80}],
                        },
                        {
                            "id": "course-b",
                            "title": "Cours B",
                            "prereqs": [],
                            "requirements": [{"kind": "manual", "min_score": 80}],
                        },
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            conn = connect(":memory:")
            try:
                initialize(conn)
                with patch("builtins.print") as mocked_print:
                    report = load_content(conn, content_dir)

                nodes = {row["id"] for row in conn.execute("SELECT id FROM nodes")}
                edges = {
                    (row["node_id"], row["prereq_id"])
                    for row in conn.execute("SELECT node_id, prereq_id FROM edges")
                }

                self.assertEqual(nodes, {"course-a", "course-b"})
                self.assertEqual(edges, {("course-a", "course-b")})
                self.assertEqual(report.edges, 1)
                self.assertTrue(
                    any(
                        "missing-course" in str(call)
                        and "Pré-requis ignoré" in str(call)
                        for call in mocked_print.call_args_list
                    ),
                    "Un avertissement doit signaler le prérequis absent.",
                )
            finally:
                conn.close()


    def test_empty_unregistered_lesson_stubs_are_ignored_but_filled_orphans_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            content_dir = Path(temporary) / "content"
            lessons_dir = content_dir / "lessons"
            lessons_dir.mkdir(parents=True)
            (content_dir / "nodes.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "course-a",
                            "title": "Cours A",
                            "prereqs": [],
                            "requirements": [{"kind": "manual", "min_score": 80}],
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (lessons_dir / "course-a.md").write_text("# Cours A", encoding="utf-8")
            stub = lessons_dir / "draft-course.md"
            stub.write_text("", encoding="utf-8")

            self.assertEqual(load_lessons(content_dir), {"course-a": "# Cours A"})

            stub.write_text("# Une vraie leçon non enregistrée", encoding="utf-8")
            with self.assertRaisesRegex(ContentError, "draft-course.*absent de nodes.json"):
                load_lessons(content_dir)



if __name__ == "__main__":
    unittest.main(verbosity=2)
