from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app import api


class _TreeStub:
    def nodes(self):
        return [SimpleNamespace(id="lesson-alias"), SimpleNamespace(id="canonical-lesson")]


class LessonSourceAliasTests(unittest.TestCase):
    def test_route_resolves_canonical_lesson_and_uses_requested_node_title(self) -> None:
        node = SimpleNamespace(id="lesson-alias", title="Titre du cours demandé")
        canonical = "# Titre canonique\n\nContenu pédagogique conservé.\n"
        with (
            patch.object(api, "_get_node", return_value=node),
            patch.object(api, "_configured_lesson_sources", return_value={"lesson-alias": "canonical-lesson"}),
            patch.object(api, "load_lessons", return_value={"canonical-lesson": canonical}),
        ):
            response = api.read_lesson("lesson-alias", tree=_TreeStub())

        self.assertEqual(response.status_code, 200)
        body = response.body.decode("utf-8")
        self.assertTrue(body.startswith("# Titre du cours demandé"))
        self.assertIn("Contenu pédagogique conservé.", body)

    def test_catalogue_aliases_target_non_empty_canonical_lessons(self) -> None:
        import json
        from pathlib import Path

        nodes_file = Path(api.CONTENT_DIR) / "nodes.json"
        lessons_dir = Path(api.CONTENT_DIR) / "lessons"
        catalog = json.loads(nodes_file.read_text(encoding="utf-8-sig"))
        aliases = {
            node["id"]: node["lesson_source_id"]
            for node in catalog
            if isinstance(node.get("lesson_source_id"), str)
        }
        expected = {
            "maint-securite-base-debutant": "maint-securite-bases-debutant",
            "maint-procedures-intermediaire": "maint-procedure-intermediaire",
            "maint-reporting-incident-intermediaire": "maint-reporting-technique-intermediaire",
        }
        self.assertEqual({k: aliases.get(k) for k in expected}, expected)
        for source_id in expected.values():
            source = lessons_dir / f"{source_id}.md"
            self.assertTrue(source.is_file(), f"Leçon canonique absente : {source_id}")
            self.assertGreater(len(source.read_text(encoding="utf-8").strip()), 1000, source_id)

    def test_communication_course_uses_its_own_canonical_markdown(self) -> None:
        import json
        from pathlib import Path

        nodes_file = Path(api.CONTENT_DIR) / "nodes.json"
        lessons_dir = Path(api.CONTENT_DIR) / "lessons"
        catalog = json.loads(nodes_file.read_text(encoding="utf-8-sig"))
        node = next(n for n in catalog if n.get("id") == "maint-communication-debutant")

        # The dedicated communication course must not be redirected to the old glossary.
        self.assertNotIn("lesson_source_id", node)
        canonical = lessons_dir / "maint-communication-debutant.md"
        self.assertTrue(canonical.is_file(), f"Leçon canonique absente : {canonical}")
        text = canonical.read_text(encoding="utf-8").strip()
        self.assertGreater(len(text), 1000)
        self.assertIn("Mise en contexte", text)
        self.assertNotIn("[Contenu à rédiger]", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
